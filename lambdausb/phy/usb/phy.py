from nmigen import *

from ...lib import stream
from .rx import USBPHYRX
from .tx import USBPHYTX


__all__ = ["USBPHY"]


class USBPHY(Elaboratable):
    def __init__(self, pins, sync_freq):
        if sync_freq < 48e6:
            raise ValueError("sync_freq must be at least 48e6 Hz, not {!r}".format(sync_freq))

        self.pins      = pins
        self.sync_freq = sync_freq
        self.sink      = stream.Endpoint([("data", 8)])
        self.source    = stream.Endpoint([("data", 8)])

    def elaborate(self, platform):
        m = Module()

        rx = m.submodules.rx = USBPHYRX(self.sync_freq)
        tx = m.submodules.tx = USBPHYTX(self.sync_freq)

        m.d.comb += [
            rx.din[0].eq(self.pins.p.i),
            rx.din[1].eq(self.pins.n.i),
            self.pins.p.o.eq(tx.dout[0]),
            self.pins.n.o.eq(tx.dout[1])
        ]

        period = int(self.sync_freq//12e6)

        with m.FSM() as fsm:
            with m.State("IDLE"):
                with m.If(~rx.idle):
                    m.next = "RECEIVE"
                with m.Elif(self.sink.valid):
                    m.next = "TRANSMIT"

            with m.State("RECEIVE"):
                m.d.comb += rx.source.connect(self.source),
                ctr_idle = Signal(range(2*period + 1), reset=2*period)
                with m.If(ctr_idle == 0):
                    m.d.sync += ctr_idle.eq(ctr_idle.reset)
                    m.next = "IDLE"
                with m.Elif(rx.idle):
                    m.d.sync += ctr_idle.eq(ctr_idle - 1)

            with m.State("TRANSMIT"):
                m.d.comb += self.sink.connect(tx.sink)
                ctr_oen = Signal(range(2*period + 1), reset=2*period)
                with m.If(ctr_oen == 0):
                    m.d.sync += ctr_oen.eq(ctr_oen.reset)
                    m.next = "IDLE"
                with m.Elif(~tx.oe):
                    m.d.sync += ctr_oen.eq(ctr_oen - 1)

        m.d.comb += [
            rx.enable.eq(~fsm.ongoing("TRANSMIT")),
            self.pins.p.oe.eq(fsm.ongoing("TRANSMIT")),
            self.pins.n.oe.eq(fsm.ongoing("TRANSMIT"))
        ]

        return m
