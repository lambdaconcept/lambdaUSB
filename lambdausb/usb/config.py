from nmigen import *

from .endpoint import *


__all__ = ["ConfigurationFSM"]


USB_REQ_GETDESCRIPTOR = 0x06
USB_REQ_GETSTATUS     = 0x00


class ConfigurationFSM(Elaboratable):
    def __init__(self, descriptor_map, rom_init):
        self.ep_in  = InputEndpoint(xfer=Transfer.CONTROL, max_size=64)
        self.ep_out = OutputEndpoint(xfer=Transfer.CONTROL, max_size=64)

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
            ("bmRequestType",  8),
            ("bRequest",       8),
            ("wValue",        16),
            ("wIndex",        16),
            ("wLength",       16),
        ])

        with m.FSM() as fsm:
            with m.State("RECEIVE"):
                rx_ctr = Signal(range(8))
                m.d.comb += self.ep_out.rdy.eq(1)
                with m.If(self.ep_out.stb):
                    m.d.sync += setup.eq(Cat(setup[8:], self.ep_out.data))
                    with m.If(rx_ctr == 7):
                        with m.If(self.ep_out.lst):
                            m.next = "DECODE-0"
                        with m.Else():
                            # Overflow. Flush remaining bytes.
                            m.next = "FLUSH"
                        m.d.sync += rx_ctr.eq(0)
                    with m.Else():
                        m.d.sync += rx_ctr.eq(Mux(self.ep_out.lst, 0, rx_ctr + 1))

            with m.State("DECODE-0"):
                with m.If(setup.bmRequestType == 0x80):
                    with m.Switch(setup.bRequest):
                        with m.Case(USB_REQ_GETDESCRIPTOR):
                            m.next = "DECODE-1"
                        with m.Case(USB_REQ_GETSTATUS):
                            m.next = "SEND-STATUS"
                        with m.Default():
                            # Unsupported request. Ignore.
                            m.next = "RECEIVE"
                with m.Else():
                    m.next = "SEND-ZLP"

            with m.State("DECODE-1"):
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
                        m.next = "RECEIVE"
                    with m.Else():
                        m.d.sync += tx_ctr.eq(tx_ctr + 1)
                        m.d.comb += rom_rp.en.eq(1)

            with m.State("SEND-STATUS"):
                tx_last = Signal()
                m.d.comb += [
                    self.ep_in.stb.eq(1),
                    self.ep_in.data.eq(0x00),
                    self.ep_in.lst.eq(tx_last),
                ]
                with m.If(self.ep_in.rdy):
                    with m.If(tx_last):
                        m.d.sync += tx_last.eq(0)
                        m.next = "RECEIVE"
                    with m.Else():
                        m.d.sync += tx_last.eq(1)

            with m.State("SEND-ZLP"):
                m.d.comb += [
                    self.ep_in.stb.eq(1),
                    self.ep_in.data.eq(0x00),
                    self.ep_in.zlp.eq(1),
                    self.ep_in.lst.eq(1),
                ]
                with m.If(self.ep_in.rdy):
                    m.next = "RECEIVE"

            with m.State("FLUSH"):
                m.d.comb += self.ep_out.rdy.eq(1)
                with m.If(self.ep_out.stb & self.ep_out.lst):
                    m.next = "RECEIVE"

        return m
