from nmigen import *

from .lib import stream
from .crc import *
from .protocol import *
from .endpoint import Transfer


__all__ = ["USBController"]


class USBController(Elaboratable):
    def __init__(self, phy):
        self.phy          = phy

        self.source_write = stream.Endpoint([("ep", 4)])
        self.source_data  = stream.Endpoint([("setup", 1), ("data", 8), ("crc_ok", 1)])
        self.sink_read    = stream.Endpoint([("ep", 4)])
        self.sink_data    = stream.Endpoint([("empty", 1), ("data", 8)])

        self.host_ack     = Signal()
        self.host_zlp     = Signal()
        self.read_xfer    = Signal(2)
        self.write_xfer   = Signal(2)

    def elaborate(self, platform):
        m = Module()

        crc16 = m.submodules.crc16 = CRC(poly=0b11000000000000101, size=16, dw=8, init=0xffff)
        crc5  = m.submodules.crc5  = CRC(poly=0b101, size=5, dw=11, init=0x1f)

        rx_pid = Signal(8)
        rx_ep = Signal(4)
        rx_dev = Signal(8)
        rx_token_byte_0 = Signal(8)
        rx_crc5 = Signal(5)
        rx_frame_no = Signal(11)
        rx_setup = Signal()
        rx_isochronous = Signal()

        # Select between DATA0/DATA1 PIDs for outgoing transfers.
        send_data1 = Array(Signal(16))

        with m.FSM() as fsm:
            with m.State("IDLE"):
                m.d.comb += self.phy.source.ready.eq(1)
                with m.If(self.phy.source.valid):
                    m.d.sync += rx_pid.eq(self.phy.source.data)
                    with m.If(self.phy.source.last):
                        with m.If(self.phy.source.data[:2] == Packet.HANDSHAKE):
                            with m.Switch(self.phy.source.data[2:4]):
                                with m.Case(Handshake.ACK):
                                    m.d.comb += self.host_ack.eq(1)
                                    m.d.sync += send_data1[rx_ep].eq(~send_data1[rx_ep])
                    with m.Else():
                        with m.Switch(self.phy.source.data[:2]):
                            with m.Case(Packet.TOKEN):
                                m.next = "ACCEPT-TOKEN-0"
                            with m.Case(Packet.SPECIAL):
                                with m.If(self.phy.source.data[2:4] == Special.PING):
                                    # PINGs are actually token packets.
                                    m.next = "ACCEPT-TOKEN-0"
                                with m.Else():
                                    m.next = "FLUSH"
                            with m.Case():
                                m.next = "FLUSH"

            with m.State("ACCEPT-TOKEN-0"):
                m.d.comb += self.phy.source.ready.eq(1)
                with m.If(self.phy.source.valid):
                    with m.If(~self.phy.source.last):
                        m.d.sync += rx_token_byte_0.eq(self.phy.source.data)
                        m.d.comb += crc5.clr.eq(1)
                        m.next = "ACCEPT-TOKEN-1"
                    with m.Else():
                        m.next = "IDLE"

            with m.State("ACCEPT-TOKEN-1"):
                m.d.comb += [
                    self.phy.source.ready.eq(1),
                    crc5.en.eq(self.phy.source.valid),
                    crc5.val.eq(Cat(rx_token_byte_0, self.phy.source.data[:3]))
                ]
                with m.If(self.phy.source.valid):
                    with m.If(~self.phy.source.last):
                        # A token packet has 3 bytes. This one has more than 3, ignore it.
                        m.next = "FLUSH"
                    with m.Elif(crc5.crc == self.phy.source.data[3:8]):
                        m.d.sync += [
                            rx_dev.eq(rx_token_byte_0[:-2]),
                            rx_ep.eq(Cat(rx_token_byte_0[-1], self.phy.source.data[:3]))
                        ]
                        with m.If(rx_pid == pid_from(Packet.SPECIAL, Special.PING)):
                            m.next = "SEND-PONG"
                        with m.Else():
                            with m.Switch(rx_pid[2:4]):
                                with m.Case(Token.SOF):
                                    m.d.sync += rx_frame_no.eq(Cat(rx_token_byte_0, self.phy.source.data[:3]))
                                    m.next = "IDLE"
                                with m.Case(Token.OUT):
                                    m.d.sync += rx_setup.eq(0)
                                    m.next = "RECEIVE-DATA-0"
                                with m.Case(Token.IN):
                                    m.d.comb += crc16.clr.eq(1)
                                    m.next = "SEND-DATA-0"
                                with m.Case(Token.SETUP):
                                    m.d.sync += rx_setup.eq(1)
                                    m.next = "RECEIVE-DATA-0"
                    with m.Else():
                        # Bad CRC5, ignore packet.
                        m.next = "IDLE"

            with m.State("SEND-PONG"):
                m.d.comb += [
                    self.phy.sink.valid.eq(1),
                    self.source_write.ep.eq(rx_ep)
                ]
                with m.If(self.source_write.ready):
                    m.d.comb += self.phy.sink.data.eq(pid_from(Packet.HANDSHAKE, Handshake.ACK))
                with m.Else():
                    m.d.comb += self.phy.sink.data.eq(pid_from(Packet.HANDSHAKE, Handshake.NAK))
                m.d.comb += self.phy.sink.last.eq(1)
                with m.If(self.phy.sink.ready):
                    m.next = "IDLE"

            with m.State("RECEIVE-DATA-0"):
                m.d.comb += [
                    self.source_write.valid.eq(1),
                    self.source_write.ep.eq(rx_ep)
                ]
                with m.If(self.source_write.ready):
                    m.d.sync += rx_isochronous.eq(self.write_xfer == Transfer.ISOCHRONOUS)
                    m.next = "RECEIVE-DATA-1"
                with m.Else():
                    m.next = "SEND-NAK"

            with m.State("RECEIVE-DATA-1"):
                m.d.comb += self.phy.source.ready.eq(self.source_data.ready)
                with m.If(self.phy.source.ready & self.phy.source.valid):
                    with m.If(~self.phy.source.last):
                        with m.If(self.phy.source.data[:2] == Packet.DATA):
                            m.d.comb += crc16.clr.eq(1)
                            m.next = "RECEIVE-DATA-2"
                    with m.Else():
                        m.next = "IDLE"

            with m.State("RECEIVE-DATA-2"):
                rx_valid  = Signal(reset=1)
                rx_skip   = Signal(range(3), reset=2)
                rx_byte_0 = Signal(8)
                rx_byte_1 = Signal(8)
                m.d.comb += self.phy.source.ready.eq(1)
                with m.If(self.phy.source.valid):
                    with m.If(~self.source_data.ready):
                        m.d.sync += rx_valid.eq(0)
                    with m.If(rx_skip != 0):
                        m.d.sync += rx_skip.eq(rx_skip - 1)
                    m.d.sync += [
                        rx_byte_0.eq(self.phy.source.data),
                        rx_byte_1.eq(rx_byte_0)
                    ]
                    m.d.comb += [
                        crc16.en.eq(~rx_skip.bool()),
                        crc16.val.eq(rx_byte_1),
                        self.source_data.valid.eq(~rx_skip.bool()),
                        self.source_data.setup.eq(rx_setup),
                        self.source_data.data.eq(rx_byte_1),
                        self.source_data.crc_ok.eq(crc16.crc == Cat(rx_byte_0, self.phy.source.data)),
                        self.source_data.last.eq(self.phy.source.last)
                    ]
                    with m.If(self.phy.source.last):
                        m.d.sync += [
                            rx_valid.eq(rx_valid.reset),
                            rx_skip.eq(rx_skip.reset)
                        ]
                        with m.If(rx_isochronous):
                            m.next = "IDLE"
                        with m.Elif((rx_skip == 1) & (Cat(rx_byte_0, self.phy.source.data) == 0)):
                            # This was a zero-length packet.
                            m.d.comb += self.host_zlp.eq(1)
                            m.next = "SEND-ACK"
                        with m.Elif(self.source_data.valid & self.source_data.crc_ok):
                            with m.If(self.source_data.ready & rx_valid):
                                m.next = "SEND-ACK"
                            with m.Else():
                                # The source wasn't ready for the whole transaction.
                                m.next = "SEND-NAK"
                        with m.Else():
                            m.next = "IDLE"

            with m.State("SEND-DATA-0"):
                m.d.comb += [
                    self.sink_read.valid.eq(1),
                    self.sink_read.ep.eq(rx_ep)
                ]
                with m.If(~self.sink_read.ready):
                    with m.If(self.read_xfer == Transfer.ISOCHRONOUS):
                        m.next = "IDLE"
                    with m.Else():
                        m.next = "SEND-NAK"
                with m.Else():
                    m.next = "SEND-DATA-1"

            with m.State("SEND-DATA-1"):
                with m.If(send_data1[rx_ep]):
                    m.d.comb += self.phy.sink.data.eq(pid_from(Packet.DATA, Data.DATA1))
                with m.Else():
                    m.d.comb += self.phy.sink.data.eq(pid_from(Packet.DATA, Data.DATA0))
                m.d.comb += self.phy.sink.valid.eq(1)
                with m.If(self.phy.sink.ready):
                    m.next = "SEND-DATA-2"

            tx_crc16 = Signal(16)
            with m.State("SEND-DATA-2"):
                m.d.comb += [
                    self.phy.sink.valid.eq(self.sink_data.valid),
                    self.phy.sink.data.eq(Mux(self.sink_data.empty, Const(0), self.sink_data.data)),
                    self.sink_data.ready.eq(self.phy.sink.ready),
                    crc16.val.eq(self.phy.sink.data)
                ]
                with m.If(self.phy.sink.ready & self.phy.sink.valid):
                    m.d.comb += crc16.en.eq(1)
                    with m.If(self.sink_data.last):
                        with m.If(self.sink_data.empty):
                            m.next = "SEND-ZLP"
                        with m.Else():
                            m.d.sync += tx_crc16.eq(crc16.crc)
                            m.next = "SEND-DATA-3"

            with m.State("SEND-DATA-3"):
                tx_first = Signal(reset=1)
                m.d.comb += self.phy.sink.valid.eq(1)
                with m.If(self.phy.sink.ready):
                    with m.If(tx_first):
                        m.d.comb += self.phy.sink.data.eq(tx_crc16[:8])
                        m.d.sync += tx_first.eq(0)
                    with m.Else():
                        m.d.comb += [
                            self.phy.sink.data.eq(tx_crc16[8:]),
                            self.phy.sink.last.eq(1)
                        ]
                        m.d.sync += tx_first.eq(tx_first.reset)
                        m.next = "IDLE"

            with m.State("SEND-ZLP"):
                m.d.comb += [
                    self.phy.sink.valid.eq(1),
                    self.phy.sink.last.eq(1),
                    self.phy.sink.data.eq(0)
                ]
                with m.If(self.phy.sink.ready):
                    m.next = "IDLE"

            with m.State("SEND-ACK"):
                m.d.comb += [
                    self.phy.sink.valid.eq(1),
                    self.phy.sink.data.eq(pid_from(Packet.HANDSHAKE, Handshake.ACK)),
                    self.phy.sink.last.eq(1)
                ]
                with m.If(self.phy.sink.ready):
                    m.next = "IDLE"
                with m.If(rx_setup):
                    m.d.sync += send_data1[rx_ep].eq(1)

            with m.State("SEND-NAK"):
                m.d.comb += [
                    self.phy.sink.valid.eq(1),
                    self.phy.sink.data.eq(pid_from(Packet.HANDSHAKE, Handshake.NAK)),
                    self.phy.sink.last.eq(1)
                ]
                with m.If(self.phy.sink.ready):
                    m.next = "IDLE"

            with m.State("FLUSH"):
                m.d.comb += self.phy.source.ready.eq(1)
                with m.If(self.phy.source.valid & self.phy.source.last):
                    m.next = "IDLE"

        return m
