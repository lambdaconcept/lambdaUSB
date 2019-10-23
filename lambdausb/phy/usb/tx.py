from nmigen import *

from ...lib import stream
from ...protocol import LineState


__all__ = ["NRZIEncoder", "USBPHYTX"]


class NRZIEncoder(Elaboratable):
    def __init__(self, sync_freq):
        self.sync_freq = sync_freq
        self.sink      = stream.Endpoint([("data", 8)])
        self.idle      = Signal()
        self.dout      = Signal(2)

    def elaborate(self, platform):
        m = Module()

        phase_accumulator = Signal(32)
        tuning_word       = Signal(32, reset=int((12e6/self.sync_freq)*2**32))
        tick              = Signal()

        m.d.sync += Cat(phase_accumulator, tick).eq(phase_accumulator + tuning_word)

        sink_last = Signal()
        shreg     = Signal(9)
        ctr_bit   = Signal(range(9), reset=8)
        ctr_one   = Signal(range(7), reset=6)
        hold_line = Signal()

        with m.FSM() as fsm:
            with m.State("IDLE"):
                m.d.comb += self.sink.ready.eq(1)
                with m.If(self.sink.valid):
                    m.d.sync += [
                        sink_last.eq(self.sink.last),
                        shreg.eq(self.sink.data),
                        ctr_bit.eq(ctr_bit.reset)
                    ]
                    m.next = "ENCODE"
                with m.If(~hold_line):
                    m.d.sync += self.dout.eq(LineState.J)
                    m.d.sync += hold_line.eq(1)

            with m.State("ENCODE"):
                with m.If(tick):
                    with m.If((ctr_bit == 1) & ~sink_last):
                        m.d.sync += hold_line.eq(1)
                        m.next = "IDLE"
                    with m.If(ctr_one == 0):
                        # We must insert a 0 for every six consecutive 1s.
                        m.d.sync += ctr_one.eq(ctr_one.reset)
                        m.d.sync += self.dout.eq(~self.dout)
                    with m.Elif(ctr_bit != 0):
                        with m.If(shreg[0] == 1):
                            m.d.sync += ctr_one.eq(ctr_one - 1)
                        with m.Else():
                            m.d.sync += ctr_one.eq(ctr_one.reset)
                            m.d.sync += self.dout.eq(~self.dout)
                        m.d.sync += [
                            shreg.eq(Cat(shreg[1:], 0)),
                            ctr_bit.eq(ctr_bit - 1),
                        ]
                    with m.Else():
                        m.d.sync += hold_line.eq(0)
                        m.d.sync += ctr_one.eq(ctr_one.reset)
                        m.next = "IDLE"

        m.d.comb += self.idle.eq(fsm.ongoing("IDLE"))

        return m


class USBPHYTX(Elaboratable):
    def __init__(self, sync_freq):
        self.sync_freq = sync_freq
        self.sink      = stream.Endpoint([("data", 8)])
        self.oe        = Signal()
        self.dout      = Signal(2)

    def elaborate(self, platform):
        m = Module()

        nrzi_enc = m.submodules.nrzi_enc = NRZIEncoder(self.sync_freq)

        with m.FSM() as fsm:
            with m.State("SYNC"):
                # Encode and transmit the SYNC pattern.
                m.d.comb += [
                    nrzi_enc.sink.data.eq(0b10000000),
                    nrzi_enc.sink.valid.eq(self.sink.valid),
                    self.oe.eq(self.sink.valid),
                    self.dout.eq(nrzi_enc.dout)
                ]
                with m.If(nrzi_enc.sink.valid & nrzi_enc.sink.ready):
                    m.next = "TRANSMIT"

            with m.State("TRANSMIT"):
                # Encode and transmit the packet data.
                m.d.comb += [
                    self.sink.connect(nrzi_enc.sink),
                    self.oe.eq(1),
                    self.dout.eq(nrzi_enc.dout)
                ]
                with m.If(~self.sink.valid & nrzi_enc.idle):
                    m.next = "EOP"

            with m.State("EOP"):
                period  = int(self.sync_freq//12e6)
                ctr_eop = Signal(range(4*period), reset=4*period-1)
                # Hold SE0 for 2 cycles, which signals the end of packet.
                with m.If(ctr_eop == 0):
                    m.d.sync += ctr_eop.eq(ctr_eop.reset)
                    m.next = "SYNC"
                with m.Else():
                    m.d.sync += ctr_eop.eq(ctr_eop - 1)
                    m.d.comb += [
                        self.oe.eq(1),
                        self.dout.eq(LineState.SE0)
                    ]

        return m
