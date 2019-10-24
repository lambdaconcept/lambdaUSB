from nmigen import *

from .lib import stream
from .protocol import Transfer


__all__ = ["USBInputArbiter", "USBOutputArbiter"]


class RoundRobin(Elaboratable):
    def __init__(self, width):
        self.width = width
        self.request = Signal(width)
        self.ce = Signal()
        self.grant = Signal.range(width)

    def elaborate(self, platform):
        m = Module()

        with m.If(self.ce):
            with m.Switch(self.grant):
                for i in range(self.width):
                    with m.Case(i):
                        for j in reversed(range(i+1, i+self.width)):
                            t = j % self.width
                            with m.If(self.request[t]):
                                m.d.sync += self.grant.eq(t)

        return m


class USBInputArbiter(Elaboratable):
    def __init__(self, port_map):
        self.port_map     = port_map
        self.source_write = stream.Endpoint([("ep", 4)])
        self.source_data  = stream.Endpoint([("empty", 1), ("data", 8)])

    def elaborate(self, platform):
        m = Module()

        rr = m.submodules.rr = RoundRobin(len(self.port_map))
        for i, (port, max_size, xfer_type) in enumerate(self.port_map.values()):
            m.d.comb += rr.request[i].eq(port.valid)

        with m.If(~self.source_write.valid):
            with m.If(rr.request.bool()):
                m.d.comb += rr.ce.eq(1)
                m.d.sync += self.source_write.valid.eq(1)
        with m.Elif(~self.source_write.ready |
                    ~self.source_data.valid | self.source_data.last & self.source_data.ready):
            m.d.sync += self.source_write.valid.eq(0)

        ep_map = Array(self.port_map.keys())
        m.d.comb += self.source_write.ep.eq(ep_map[rr.grant])

        with m.Switch(rr.grant):
            for i, (port, max_size, xfer_type) in enumerate(self.port_map.values()):
                with m.Case(i):
                    if xfer_type is Transfer.CONTROL:
                        m.d.comb += self.source_data.empty.eq(port.empty)
                    else:
                        m.d.comb += self.source_data.empty.eq(Const(0))
                    m.d.comb += [
                        self.source_data.valid.eq(port.valid),
                        self.source_data.last.eq(port.last),
                        self.source_data.data.eq(port.data),
                        port.ready.eq(self.source_data.ready)
                    ]

        return m


class USBOutputArbiter(Elaboratable):
    def __init__(self, port_map):
        self.port_map  = port_map
        self.sink_read = stream.Endpoint([("ep", 4)])
        self.sink_data = stream.Endpoint([("setup", 1), ("data", 8)])

    def elaborate(self, platform):
        m = Module()

        rr = m.submodules.rr = RoundRobin(len(self.port_map))
        for i, (port, max_size, xfer_type) in enumerate(self.port_map.values()):
            m.d.comb += rr.request[i].eq(port.ready)

        with m.If(~self.sink_read.valid):
            with m.If(rr.request.bool()):
                m.d.comb += rr.ce.eq(1)
                m.d.sync += self.sink_read.valid.eq(1)
        with m.Elif(~self.sink_read.ready |
                    self.sink_data.valid & self.sink_data.last & self.sink_data.ready):
            m.d.sync += self.sink_read.valid.eq(0)

        ep_map = Array(self.port_map.keys())
        m.d.comb += self.sink_read.ep.eq(ep_map[rr.grant])

        with m.Switch(rr.grant):
            for i, (port, max_size, xfer_type) in enumerate(self.port_map.values()):
                with m.Case(i):
                    if xfer_type is Transfer.CONTROL:
                        m.d.comb += port.setup.eq(self.sink_data.setup)
                    m.d.comb += [
                        port.valid.eq(self.sink_data.valid),
                        port.last.eq(self.sink_data.last),
                        port.data.eq(self.sink_data.data),
                        self.sink_data.ready.eq(port.ready)
                    ]

        return m
