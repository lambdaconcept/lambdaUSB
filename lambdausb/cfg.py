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

        rx_buf = Array(Signal(8) for _ in range(8))
        rx_count = Signal(range(8))

        ctl_type  = Signal(8)
        ctl_req   = Signal(8)
        ctl_val0  = Signal(8)
        ctl_val1  = Signal(8)
        ctl_index = Signal(16)
        ctl_size  = Signal(16)
        m.d.comb += [
            ctl_type.eq(rx_buf[0]),
            ctl_req.eq(rx_buf[1]),
            ctl_val0.eq(rx_buf[2]),
            ctl_val1.eq(rx_buf[3]),
            ctl_index.eq(Cat(rx_buf[4], rx_buf[5])),
            ctl_size.eq(Cat(rx_buf[6], rx_buf[7]))
        ]

        rom = Memory(width=8, depth=len(self.rom_init), init=self.rom_init)
        rom_rp = m.submodules.rom_rp = rom.read_port(transparent=False)
        rom_rp.en.reset = 0

        req_offset = Signal(range(len(self.rom_init)))
        req_size = Signal(16)

        with m.Switch(ctl_val1):
            for val1, sub_map in self.descriptor_map.items():
                with m.Case(val1):
                    with m.Switch(ctl_val0):
                        for val0, (offset, size) in sub_map.items():
                            with m.Case(val0):
                                m.d.comb += [
                                    req_offset.eq(offset),
                                    req_size.eq(size)
                                ]

        tx_sent = Signal(16)
        status_last = Signal()

        with m.FSM() as fsm:
            with m.State("RECEIVE"):
                m.d.comb += self.ep_out.rdy.eq(1)
                with m.If(self.ep_out.stb):
                    m.d.sync += rx_buf[rx_count].eq(self.ep_out.data)
                    with m.If(self.ep_out.lst):
                        m.d.sync += rx_count.eq(0)
                        with m.If(rx_count == 7):
                            with m.If(ctl_type == 0x80):
                                with m.If(ctl_req == USB_REQ_GETDESCRIPTOR):
                                    m.d.sync += tx_sent.eq(0)
                                    m.d.comb += [
                                        rom_rp.addr.eq(req_offset),
                                        rom_rp.en.eq(1)
                                    ]
                                    m.next = "SEND-DESCRIPTOR"
                                with m.Elif(ctl_req == USB_REQ_GETSTATUS):
                                    m.d.sync += status_last.eq(0)
                                    m.next = "SEND-STATUS"
                            with m.Else():
                                m.next = "SEND-NODATA"
                    with m.Else():
                        m.d.sync += rx_count.eq(rx_count + 1)
                        with m.If(rx_count == 7):
                            m.next = "WAIT-LAST"

            with m.State("SEND-DESCRIPTOR"):
                m.d.comb += [
                    self.ep_in.stb.eq(1),
                    self.ep_in.data.eq(rom_rp.data)
                ]
                with m.If(req_size < ctl_size):
                    m.d.comb += self.ep_in.lst.eq(tx_sent == (req_size - 1))
                with m.Else():
                    m.d.comb += self.ep_in.lst.eq(tx_sent == (ctl_size - 1))
                m.d.comb += rom_rp.addr.eq(req_offset + tx_sent + 1)
                with m.If(self.ep_in.rdy):
                    with m.If(self.ep_in.lst):
                        m.d.sync += rx_count.eq(0)
                        m.next = "RECEIVE"
                    with m.Else():
                        m.d.sync += tx_sent.eq(tx_sent + 1)
                        m.d.comb += rom_rp.en.eq(1)

            with m.State("SEND-STATUS"):
                m.d.comb += [
                    self.ep_in.stb.eq(1),
                    self.ep_in.data.eq(0x00),
                    self.ep_in.lst.eq(status_last)
                ]
                with m.If(self.ep_in.rdy):
                    m.d.sync += status_last.eq(1),
                    with m.If(status_last):
                        m.d.sync += rx_count.eq(0)
                        m.next = "RECEIVE"

            with m.State("SEND-NODATA"):
                m.d.comb += [
                    self.ep_in.stb.eq(1),
                    self.ep_in.data.eq(0x00),
                    self.ep_in.zlp.eq(1),
                    self.ep_in.lst.eq(1)
                ]
                with m.If(self.ep_in.rdy):
                    m.d.sync += rx_count.eq(0)
                    m.next = "RECEIVE"

            with m.State("WAIT-LAST"):
                m.d.comb += self.ep_out.rdy.eq(1)
                with m.If(self.ep_out.stb & self.ep_out.lst):
                    m.d.sync += rx_count.eq(0)
                    m.next = "RECEIVE"

        return m
