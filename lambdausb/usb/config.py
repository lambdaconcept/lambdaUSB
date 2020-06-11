import enum

from nmigen import *

from .endpoint import *


__all__ = ["ConfigurationFSM"]


class Request(enum.IntEnum):
    GET_DESCRIPTOR = 0x8006
    GET_DEV_STATUS = 0x8000
    SET_ADDRESS    = 0x0005
    SET_CONFIG     = 0x0009


class ConfigurationFSM(Elaboratable):
    def __init__(self, descriptor_map, rom_init):
        self.ep_in  = InputEndpoint(xfer=Transfer.CONTROL, max_size=64)
        self.ep_out = OutputEndpoint(xfer=Transfer.CONTROL, max_size=64)
        self.dev_addr  = Signal(7)

        self.descriptor_map = descriptor_map
        self.rom_init = rom_init

    def elaborate(self, platform):
        m = Module()

        rom = Memory(width=8, depth=len(self.rom_init), init=self.rom_init)
        m.submodules.rom_rp = rom_rp = rom.read_port(transparent=False)
        rom_rp.en.reset = 0

        rom_offset = Signal(range(len(self.rom_init)), reset_less=True)
        desc_size  = Signal(16, reset_less=True)

        setup = Record([
            ("bmRequestType", [("rcpt", 5), ("type", 2), ("dir", 1)]),
            ("bRequest",       8),
            ("wValue",        16),
            ("wIndex",        16),
            ("wLength",       16),
        ])

        dev_addr_next = Signal.like(self.dev_addr)

        with m.FSM() as fsm:
            with m.State("RECEIVE"):
                rx_ctr = Signal(range(8))
                m.d.comb += self.ep_out.rdy.eq(1)
                with m.If(self.ep_out.stb):
                    m.d.sync += setup.eq(Cat(setup[8:], self.ep_out.data))
                    with m.If(rx_ctr == 7):
                        with m.If(self.ep_out.lst):
                            with m.If(~self.ep_out.drop):
                                m.next = "DECODE-REQUEST"
                        with m.Else():
                            # Overflow. Flush remaining bytes.
                            m.next = "FLUSH"
                        m.d.sync += rx_ctr.eq(0)
                    with m.Else():
                        m.d.sync += rx_ctr.eq(Mux(self.ep_out.lst, 0, rx_ctr + 1))

            with m.State("DECODE-REQUEST"):
                with m.Switch(Cat(setup.bRequest, setup.bmRequestType)):
                    with m.Case(Request.GET_DESCRIPTOR):
                        m.next = "GET-DESCRIPTOR"
                    with m.Case(Request.GET_DEV_STATUS):
                        m.next = "SEND-DEV-STATUS-0"
                    with m.Case(Request.SET_ADDRESS):
                        m.d.sync += dev_addr_next.eq(setup.wValue[:7])
                        m.next = "SEND-ZLP"
                    with m.Case(Request.SET_CONFIG):
                        m.next = "SEND-ZLP"
                    with m.Default():
                        # Unsupported request. Ignore.
                        m.next = "RECEIVE"

            with m.State("GET-DESCRIPTOR"):
                with m.Switch(setup.wValue[8:]):
                    for desc_type, index_map in self.descriptor_map.items():
                        with m.Case(desc_type):
                            with m.Switch(setup.wValue[:8]):
                                for desc_index, (offset, size) in index_map.items():
                                    with m.Case(desc_index):
                                        m.d.sync += [
                                            rom_offset.eq(offset),
                                            desc_size.eq(size)
                                        ]
                                        m.next = "SEND-DESCRIPTOR-0"
                                with m.Default():
                                    m.next = "RECEIVE"
                    with m.Default():
                        m.next = "RECEIVE"

            with m.State("SEND-DESCRIPTOR-0"):
                m.d.comb += [
                    rom_rp.addr.eq(rom_offset),
                    rom_rp.en.eq(1),
                ]
                m.next = "SEND-DESCRIPTOR-1"

            with m.State("SEND-DESCRIPTOR-1"):
                tx_ctr = Signal(16)
                m.d.comb += [
                    self.ep_in.stb.eq(1),
                    self.ep_in.data.eq(rom_rp.data)
                ]
                with m.If(desc_size < setup.wLength):
                    m.d.comb += self.ep_in.lst.eq(tx_ctr == (desc_size - 1))
                with m.Else():
                    m.d.comb += self.ep_in.lst.eq(tx_ctr == (setup.wLength - 1))
                m.d.comb += rom_rp.addr.eq(rom_offset + tx_ctr + 1)
                with m.If(self.ep_in.rdy):
                    with m.If(self.ep_in.lst):
                        m.d.sync += tx_ctr.eq(0)
                        m.next = "SEND-DESCRIPTOR-2"
                    with m.Else():
                        m.d.sync += tx_ctr.eq(tx_ctr + 1)
                        m.d.comb += rom_rp.en.eq(1)

            with m.State("SEND-DESCRIPTOR-2"):
                with m.If(self.ep_in.rdy):
                    with m.If(self.ep_in.ack):
                        m.next = "RECEIVE"
                    with m.Else():
                        m.next = "SEND-DESCRIPTOR-0"

            with m.State("SEND-DEV-STATUS-0"):
                tx_last = Signal()
                m.d.comb += [
                    self.ep_in.stb.eq(1),
                    self.ep_in.data.eq(0x00),
                    self.ep_in.lst.eq(tx_last),
                ]
                with m.If(self.ep_in.rdy):
                    with m.If(tx_last):
                        m.d.sync += tx_last.eq(0)
                        m.next = "SEND-DEV-STATUS-1"
                    with m.Else():
                        m.d.sync += tx_last.eq(1)

            with m.State("SEND-DEV-STATUS-1"):
                with m.If(self.ep_in.rdy):
                    with m.If(self.ep_in.ack):
                        m.next = "RECEIVE"
                    with m.Else():
                        m.next = "SEND-DEV-STATUS-0"

            with m.State("SEND-ZLP"):
                m.d.comb += [
                    self.ep_in.stb.eq(1),
                    self.ep_in.zlp.eq(1),
                    self.ep_in.lst.eq(1),
                ]
                with m.If(self.ep_in.rdy & self.ep_in.ack):
                    m.d.sync += self.dev_addr.eq(dev_addr_next)
                    m.next = "RECEIVE"

            with m.State("FLUSH"):
                m.d.comb += self.ep_out.rdy.eq(1)
                with m.If(self.ep_out.stb & self.ep_out.lst):
                    m.next = "RECEIVE"

        return m
