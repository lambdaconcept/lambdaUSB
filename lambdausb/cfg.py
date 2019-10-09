from nmigen import *

from .lib import stream


__all__ = ["ConfigurationEndpoint"]


USB_REQ_GETDESCRIPTOR = 0x06
USB_REQ_GETSTATUS     = 0x00


class ConfigurationEndpoint(Elaboratable):
    def __init__(self, descriptor_map, rom_init):
        self.descriptor_map = descriptor_map
        self.rom_init       = rom_init
        self.sink           = stream.Endpoint([("setup", 1), ("data", 8)])
        self.source         = stream.Endpoint([("empty", 1), ("data", 8)])

    def elaborate(self, platform):
        m = Module()

        rx_buf = Array(Signal(8) for _ in range(8))
        rx_count = Signal.range(8)

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

        req_offset = Signal.range(len(self.rom_init))
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
                m.d.comb += self.sink.ready.eq(1)
                with m.If(self.sink.valid):
                    m.d.sync += rx_buf[rx_count].eq(self.sink.data)
                    with m.If(self.sink.last):
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
                    self.source.valid.eq(1),
                    self.source.data.eq(rom_rp.data)
                ]
                with m.If(req_size < ctl_size):
                    m.d.comb += self.source.last.eq(tx_sent == (req_size - 1))
                with m.Else():
                    m.d.comb += self.source.last.eq(tx_sent == (ctl_size - 1))
                m.d.comb += rom_rp.addr.eq(req_offset + tx_sent + 1)
                with m.If(self.source.ready):
                    with m.If(self.source.last):
                        m.d.sync += rx_count.eq(0)
                        m.next = "RECEIVE"
                    with m.Else():
                        m.d.sync += tx_sent.eq(tx_sent + 1)
                        m.d.comb += rom_rp.en.eq(1)

            with m.State("SEND-STATUS"):
                m.d.comb += [
                    self.source.valid.eq(1),
                    self.source.data.eq(0x00),
                    self.source.last.eq(status_last)
                ]
                with m.If(self.source.ready):
                    m.d.sync += status_last.eq(1),
                    with m.If(status_last):
                        m.d.sync += rx_count.eq(0)
                        m.next = "RECEIVE"

            with m.State("SEND-NODATA"):
                m.d.comb += [
                    self.source.valid.eq(1),
                    self.source.data.eq(0x00),
                    self.source.empty.eq(1),
                    self.source.last.eq(1)
                ]
                with m.If(self.source.ready):
                    m.d.sync += rx_count.eq(0)
                    m.next = "RECEIVE"

            with m.State("WAIT-LAST"):
                m.d.comb += self.sink.ready.eq(1)
                with m.If(self.sink.valid & self.sink.last):
                    m.d.sync += rx_count.eq(0)
                    m.next = "RECEIVE"

        return m
