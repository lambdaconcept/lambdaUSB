from nmigen import *
from nmigen.hdl.rec import *

from .crc import CRC
from .defs import *
from .endpoint import *
from .mux import *


__all__ = ["Device"]


class Device(Elaboratable):
    """USB 2.0 device controller.

    An USB 2.0 device controller, managing transactions between its endpoints and the host.

    Attributes
    ----------
    rx.stb : Signal, in
        Receive strobe. Asserted by the underlying PHY when it has data to send.
    rx.lst : Signal, in
        Receive last. Asserted when `rx.data` holds the last byte of a packet.
    rx.data : Signal, in
        Receive data.
    rx.rdy : Signal, out
        Receive ready. Asserted when the device is able to receive data.
    tx.stb : Signal, out
        Transmit strobe. Asserted by the device when it has data to send.
    tx.lst : Signal, out
        Transmit last. Asserted when `tx.data` holds the last byte of a packet.
    tx.data : Signal, out
        Transmit data.
    tx.rdy : Signal, in
        Transmit ready. Asserted when the underlying PHY is able to receive data.
    """
    def __init__(self):
        self.rx = Record([
            ("stb",  1, DIR_FANIN),
            ("lst",  1, DIR_FANIN),
            ("data", 8, DIR_FANIN),
            ("rdy",  1, DIR_FANOUT),
        ])
        self.tx = Record([
            ("stb",  1, DIR_FANOUT),
            ("lst",  1, DIR_FANOUT),
            ("data", 8, DIR_FANOUT),
            ("rdy",  1, DIR_FANIN),
        ])

        self._mux_in  = InputMultiplexer()
        self._mux_out = OutputMultiplexer()

    def add_endpoint(self, ep, *, addr, buffered=False):
        """
        Add an endpoint to the USB device.

        Parameters
        ----------
        ep : :class:`endpoint.InputEndpoint` or :class:`endpoint.OutputEndpoint`
            Endpoint interface.
        addr : int
            Endpoint address.
        buffered : bool
            Endpoint buffering. Optional. If true, a double buffer is provided between the
            the endpoint and the device controller.
        """
        if isinstance(ep, InputEndpoint):
            self._mux_in .add_endpoint(ep, addr=addr, buffered=buffered)
        elif isinstance(ep, OutputEndpoint):
            self._mux_out.add_endpoint(ep, addr=addr, buffered=buffered)
        else:
            raise TypeError("Endpoint must be an InputEndpoint or an OutputEndpoint, not {!r}"
                            .format(ep))

    def elaborate(self, platform):
        m = Module()

        m.submodules.mux_in  = mux_in  = self._mux_in
        m.submodules.mux_out = mux_out = self._mux_out

        m.submodules.crc16 = crc16 = CRC(poly=0b11000000000000101, size=16, dw=8, init=0xffff)
        m.submodules.crc5  = crc5  = CRC(poly=0b00101, size=5, dw=11, init=0x1f)

        rx_pid = Signal(8)
        rx_ep = Signal(4)
        rx_dev = Signal(8)
        rx_token_lsb = Signal(8)
        rx_setup = Signal()
        rx_xfer = Signal.like(mux_out.cmd.xfer)

        rx_sof = Signal()
        rx_frame_no = Signal(11)
        m.d.comb += [
            mux_in.sof.eq(rx_sof),
            mux_out.sof.eq(rx_sof),
        ]

        # Select between DATA0/DATA1 PIDs for outgoing transfers.
        use_data1 = Array(Signal(16))

        with m.FSM() as fsm:
            with m.State("IDLE"):
                m.d.comb += self.rx.rdy.eq(1)
                with m.If(self.rx.stb):
                    m.d.sync += rx_pid.eq(self.rx.data)
                    with m.If(self.rx.lst):
                        with m.If((self.rx.data[0:2] == Packet.HANDSHAKE)
                                & (self.rx.data[2:4] == Handshake.ACK)):
                            m.d.comb += [
                                mux_in.pkt.rdy.eq(1),
                                mux_in.pkt.ack.eq(1),
                            ]
                            m.d.sync += use_data1[rx_ep].eq(~use_data1[rx_ep])
                    with m.Else():
                        with m.Switch(self.rx.data[0:2]):
                            with m.Case(Packet.TOKEN):
                                m.next = "ACCEPT-TOKEN-0"
                            with m.Case(Packet.SPECIAL):
                                with m.If(self.rx.data[2:4] == Special.PING):
                                    # PINGs are treated as token packets.
                                    m.next = "ACCEPT-TOKEN-0"
                                with m.Else():
                                    m.next = "FLUSH"
                            with m.Default():
                                m.next = "FLUSH"

            with m.State("ACCEPT-TOKEN-0"):
                m.d.comb += self.rx.rdy.eq(1)
                with m.If(self.rx.stb):
                    with m.If(~self.rx.lst):
                        m.d.sync += rx_token_lsb.eq(self.rx.data)
                        m.d.comb += crc5.clr.eq(1)
                        m.next = "ACCEPT-TOKEN-1"
                    with m.Else():
                        m.next = "IDLE"

            with m.State("ACCEPT-TOKEN-1"):
                m.d.comb += [
                    self.rx.rdy.eq(1),
                    crc5.en.eq(self.rx.stb),
                    crc5.val.eq(Cat(rx_token_lsb, self.rx.data[:3]))
                ]
                with m.If(self.rx.stb):
                    with m.If(~self.rx.lst):
                        # A token packet has 3 bytes. This one has more than 3, ignore it.
                        m.next = "FLUSH"
                    with m.Elif(crc5.crc == self.rx.data[3:8]):
                        m.d.sync += [
                            rx_dev.eq(rx_token_lsb[:-2]),
                            rx_ep.eq(Cat(rx_token_lsb[-1], self.rx.data[:3]))
                        ]
                        with m.If(rx_pid == pid_from(Packet.SPECIAL, Special.PING)):
                            m.next = "SEND-PONG"
                        with m.Else():
                            with m.Switch(rx_pid[2:4]):
                                with m.Case(Token.SOF):
                                    m.d.comb += rx_sof.eq(1)
                                    m.d.sync += rx_frame_no.eq(Cat(rx_token_lsb, self.rx.data[:3]))
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
                m.d.comb += mux_out.cmd.addr.eq(rx_ep)
                with m.If(mux_out.cmd.rdy):
                    m.d.comb += self.tx.data.eq(pid_from(Packet.HANDSHAKE, Handshake.ACK))
                with m.Else():
                    m.d.comb += self.tx.data.eq(pid_from(Packet.HANDSHAKE, Handshake.NAK))
                m.d.comb += [
                    self.tx.stb.eq(1),
                    self.tx.lst.eq(1),
                ]
                with m.If(self.tx.rdy):
                    m.next = "IDLE"

            with m.State("RECEIVE-DATA-0"):
                m.d.comb += [
                    mux_out.cmd.stb.eq(1),
                    mux_out.cmd.addr.eq(rx_ep),
                ]
                with m.If(~mux_out.cmd.rdy):
                    with m.If(mux_out.cmd.xfer == Transfer.ISOCHRONOUS):
                        m.next = "IDLE"
                    with m.Else():
                        m.next = "SEND-NAK"
                with m.Else():
                    m.d.sync += rx_xfer.eq(mux_out.cmd.xfer)
                    m.next = "RECEIVE-DATA-1"

            with m.State("RECEIVE-DATA-1"):
                m.d.comb += self.rx.rdy.eq(mux_out.pkt.rdy)
                with m.If(self.rx.rdy & self.rx.stb):
                    with m.If(~self.rx.lst):
                        with m.If(self.rx.data[0:2] == Packet.DATA):
                            m.d.comb += crc16.clr.eq(1)
                            m.next = "RECEIVE-DATA-2"
                    with m.Else():
                        m.next = "IDLE"

            with m.State("RECEIVE-DATA-2"):
                rx_skip_ctr = Signal(2, reset=2)
                rx_byte_0   = Signal(8)
                rx_byte_1   = Signal(8)
                ep_busy     = Signal()
                m.d.comb += self.rx.rdy.eq(1)
                with m.If(self.rx.stb):
                    with m.If(rx_skip_ctr != 0):
                        m.d.sync += rx_skip_ctr.eq(rx_skip_ctr - 1)
                    m.d.sync += [
                        rx_byte_0.eq(self.rx.data),
                        rx_byte_1.eq(rx_byte_0),
                    ]
                m.d.comb += [
                    mux_out.pkt.stb.eq(self.rx.stb & (rx_skip_ctr == 0)),
                    mux_out.pkt.data.eq(rx_byte_1),
                    mux_out.pkt.setup.eq(rx_setup),
                    mux_out.pkt.lst.eq(self.rx.lst),
                    mux_out.pkt.drop.eq(crc16.crc != Cat(rx_byte_0, self.rx.data)),
                    crc16.en.eq(mux_out.pkt.stb),
                    crc16.val.eq(mux_out.pkt.data),
                ]
                with m.If(mux_out.pkt.stb & ~mux_out.pkt.rdy):
                    m.d.sync += ep_busy.eq(1)
                with m.If(self.rx.stb):
                    with m.If(self.rx.lst):
                        with m.If(rx_xfer == Transfer.ISOCHRONOUS):
                            m.next = "IDLE"
                        with m.Elif((rx_skip_ctr == 1) & (Cat(rx_byte_0, self.rx.data) == 0)):
                            # This was a zero-length packet.
                            m.next = "SEND-ACK"
                        with m.Elif(mux_out.pkt.stb & ~mux_out.pkt.drop):
                            # CRC check passed.
                            with m.If(mux_out.pkt.rdy & ~ep_busy):
                                m.next = "SEND-ACK"
                            with m.Else():
                                m.next = "SEND-NAK"
                        with m.Else():
                            # CRC check failed. Ignore packet.
                            m.next = "IDLE"
                        m.d.sync += [
                            rx_skip_ctr.eq(rx_skip_ctr.reset),
                            ep_busy.eq(ep_busy.reset),
                        ]

            with m.State("SEND-DATA-0"):
                m.d.comb += [
                    mux_in.cmd.stb.eq(1),
                    mux_in.cmd.addr.eq(rx_ep),
                ]
                with m.If(~mux_in.cmd.rdy):
                    with m.If(mux_in.cmd.xfer == Transfer.ISOCHRONOUS):
                        m.next = "IDLE"
                    with m.Else():
                        m.next = "SEND-NAK"
                with m.Else():
                    m.next = "SEND-DATA-1"

            with m.State("SEND-DATA-1"):
                with m.If(use_data1[rx_ep]):
                    m.d.comb += self.tx.data.eq(pid_from(Packet.DATA, Data.DATA1))
                with m.Else():
                    m.d.comb += self.tx.data.eq(pid_from(Packet.DATA, Data.DATA0))
                m.d.comb += self.tx.stb.eq(1)
                with m.If(self.tx.rdy):
                    m.next = "SEND-DATA-2"

            tx_crc16 = Signal(16)
            with m.State("SEND-DATA-2"):
                m.d.comb += [
                    self.tx.stb.eq(mux_in.pkt.stb),
                    self.tx.data.eq(Mux(mux_in.pkt.zlp, Const(0), mux_in.pkt.data)),
                    mux_in.pkt.rdy.eq(self.tx.rdy),
                    crc16.val.eq(self.tx.data)
                ]
                with m.If(self.tx.rdy & self.tx.stb):
                    m.d.comb += crc16.en.eq(1)
                    with m.If(mux_in.pkt.lst):
                        with m.If(mux_in.pkt.zlp):
                            m.next = "SEND-ZLP"
                        with m.Else():
                            m.d.sync += tx_crc16.eq(crc16.crc)
                            m.next = "SEND-DATA-3"

            with m.State("SEND-DATA-3"):
                tx_msb = Signal()
                m.d.comb += self.tx.stb.eq(1)
                with m.If(self.tx.rdy):
                    with m.If(~tx_msb):
                        m.d.comb += self.tx.data.eq(tx_crc16[:8])
                        m.d.sync += tx_msb.eq(1)
                    with m.Else():
                        m.d.comb += [
                            self.tx.data.eq(tx_crc16[8:]),
                            self.tx.lst.eq(1),
                        ]
                        m.d.sync += tx_msb.eq(tx_msb.reset)
                        m.next = "IDLE"

            with m.State("SEND-ZLP"):
                m.d.comb += [
                    self.tx.stb.eq(1),
                    self.tx.lst.eq(1),
                    self.tx.data.eq(0),
                ]
                with m.If(self.tx.rdy):
                    m.next = "IDLE"

            with m.State("SEND-ACK"):
                m.d.comb += [
                    self.tx.stb.eq(1),
                    self.tx.data.eq(pid_from(Packet.HANDSHAKE, Handshake.ACK)),
                    self.tx.lst.eq(1)
                ]
                with m.If(self.tx.rdy):
                    m.next = "IDLE"
                with m.If(rx_setup):
                    # In a control transfer, the first data packet is a DATA1.
                    m.d.sync += use_data1[rx_ep].eq(1)

            with m.State("SEND-NAK"):
                m.d.comb += [
                    self.tx.stb.eq(1),
                    self.tx.data.eq(pid_from(Packet.HANDSHAKE, Handshake.NAK)),
                    self.tx.lst.eq(1)
                ]
                with m.If(self.tx.rdy):
                    m.next = "IDLE"

            with m.State("FLUSH"):
                m.d.comb += self.rx.rdy.eq(1)
                with m.If(self.rx.stb & self.rx.lst):
                    m.next = "IDLE"

        return m
