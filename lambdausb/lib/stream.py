from nmigen import *
from nmigen.hdl.rec import *
from nmigen.lib import fifo


__all__ = ["Endpoint", "SyncFIFO", "AsyncFIFO"]


def _make_fanout(layout):
    r = []
    for f in layout:
        if isinstance(f[1], (int, tuple)):
            r.append((f[0], f[1], DIR_FANOUT))
        else:
            r.append((f[0], _make_fanout(f[1])))
    return r


class EndpointDescription:
    def __init__(self, payload_layout):
        self.payload_layout = payload_layout

    def get_full_layout(self):
        reserved = {"valid", "ready", "first", "last", "payload"}
        attributed = set()
        for f in self.payload_layout:
            if f[0] in attributed:
                raise ValueError(f[0] + " already attributed in payload layout")
            if f[0] in reserved:
                raise ValueError(f[0] + " cannot be used in endpoint layout")
            attributed.add(f[0])

        full_layout = [
            ("valid", 1, DIR_FANOUT),
            ("ready", 1, DIR_FANIN),
            ("first", 1, DIR_FANOUT),
            ("last",  1, DIR_FANOUT),
            ("payload", _make_fanout(self.payload_layout))
        ]
        return full_layout


class Endpoint(Record):
    def __init__(self, layout_or_description, **kwargs):
        if isinstance(layout_or_description, EndpointDescription):
            self.description = layout_or_description
        else:
            self.description = EndpointDescription(layout_or_description)
        super().__init__(self.description.get_full_layout(), src_loc_at=1, **kwargs)

    def __getattr__(self, name):
        try:
            return super().__getattr__(name)
        except AttributeError:
            return self.fields["payload"][name]


class _FIFOWrapper:
    def __init__(self, payload_layout):
        self.sink   = Endpoint(payload_layout)
        self.source = Endpoint(payload_layout)

        self.layout = Layout([
            ("payload", self.sink.description.payload_layout),
            ("first",   1, DIR_FANOUT),
            ("last",    1, DIR_FANOUT)
        ])

    def elaborate(self, platform):
        m = Module()

        fifo = m.submodules.fifo = self.fifo
        fifo_din = Record(self.layout)
        fifo_dout = Record(self.layout)
        m.d.comb += [
            fifo.w_data.eq(fifo_din),
            fifo_dout.eq(fifo.r_data),

            self.sink.ready.eq(fifo.w_rdy),
            fifo.w_en.eq(self.sink.valid),
            fifo_din.first.eq(self.sink.first),
            fifo_din.last.eq(self.sink.last),
            fifo_din.payload.eq(self.sink.payload),

            self.source.valid.eq(fifo.r_rdy),
            self.source.first.eq(fifo_dout.first),
            self.source.last.eq(fifo_dout.last),
            self.source.payload.eq(fifo_dout.payload),
            fifo.r_en.eq(self.source.ready)
        ]

        return m


class SyncFIFO(Elaboratable, _FIFOWrapper):
    def __init__(self, layout, depth, fwft=True):
        super().__init__(layout)
        self.fifo = fifo.SyncFIFO(width=len(Record(self.layout)), depth=depth, fwft=fwft)
        self.depth = self.fifo.depth
        self.level = self.fifo.level


class AsyncFIFO(Elaboratable, _FIFOWrapper):
    def __init__(self, layout, depth, r_domain="read", w_domain="write"):
        super().__init__(layout)
        self.fifo = fifo.AsyncFIFO(width=len(Record(self.layout)), depth=depth,
                                   r_domain=r_domain, w_domain=w_domain)
        self.depth = self.fifo.depth
