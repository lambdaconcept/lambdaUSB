from nmigen import *
from nmigen.hdl.rec import *

from ...lib import stream
from .rx import PHY as PHYRX
from .tx import PHY as PHYTX


__all__ = ["PHY"]


class PHY(Elaboratable):
    def __init__(self, pins, sync_freq):
        if sync_freq < 48e6:
            raise ValueError("sync_freq must be at least 48e6 Hz, not {!r}".format(sync_freq))

        self.rx = Record([
            ("stb",  1, DIR_FANOUT),
            ("lst",  1, DIR_FANOUT),
            ("data", 8, DIR_FANOUT),
            ("rdy",  1, DIR_FANIN),
        ])
        self.tx = Record([
            ("stb",  1, DIR_FANIN),
            ("lst",  1, DIR_FANIN),
            ("data", 8, DIR_FANIN),
            ("rdy",  1, DIR_FANOUT),
        ])

        self.sync_freq = sync_freq
        self._pins = pins


    def elaborate(self, platform):
        m = Module()

        rx = m.submodules.rx = PHYRX(self.sync_freq)
        tx = m.submodules.tx = PHYTX(self.sync_freq)

        m.d.comb += [
            rx.din[0].eq(self._pins.p.i),
            rx.din[1].eq(self._pins.n.i),
            self._pins.p.o.eq(tx.dout[0]),
            self._pins.n.o.eq(tx.dout[1])
        ]

        period = int(self.sync_freq//12e6)

        with m.FSM() as fsm:
            with m.State("IDLE"):
                with m.If(~rx.idle):
                    m.next = "RECEIVE"
                with m.Elif(self.tx.stb):
                    m.next = "TRANSMIT"

            with m.State("RECEIVE"):
                m.d.comb += [
                    self.rx.stb.eq(rx.source.valid),
                    self.rx.lst.eq(rx.source.last),
                    self.rx.data.eq(rx.source.data),
                    rx.source.ready.eq(self.rx.rdy),
                ]
                ctr_idle = Signal(range(2*period + 1), reset=2*period)
                with m.If(ctr_idle == 0):
                    m.d.sync += ctr_idle.eq(ctr_idle.reset)
                    m.next = "IDLE"
                with m.Elif(rx.idle):
                    m.d.sync += ctr_idle.eq(ctr_idle - 1)

            with m.State("TRANSMIT"):
                m.d.comb += [
                    tx.sink.valid.eq(self.tx.stb),
                    tx.sink.last.eq(self.tx.lst),
                    tx.sink.data.eq(self.tx.data),
                    self.tx.rdy.eq(tx.sink.ready),
                ]
                ctr_oen = Signal(range(2*period + 1), reset=2*period)
                with m.If(ctr_oen == 0):
                    m.d.sync += ctr_oen.eq(ctr_oen.reset)
                    m.next = "IDLE"
                with m.Elif(~tx.oe):
                    m.d.sync += ctr_oen.eq(ctr_oen - 1)

        m.d.comb += [
            rx.enable.eq(~fsm.ongoing("TRANSMIT")),
            self._pins.p.oe.eq(fsm.ongoing("TRANSMIT")),
            self._pins.n.oe.eq(fsm.ongoing("TRANSMIT"))
        ]

        return m
