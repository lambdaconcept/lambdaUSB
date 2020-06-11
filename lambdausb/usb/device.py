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
    addr : Signal, in
        Device address. Provided by the logic controlling endpoint 0.
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

        self.addr = Signal(7)

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

        m.submodules.token_sink  = token_sink  = _TokenSink()
        m.submodules.data_sink   = data_sink   = _DataSink()
        m.submodules.data_source = data_source = _DataSource()

        rx_pid   = Signal(4)
        rx_pid_r = Signal.like(rx_pid)
        m.d.comb += rx_pid.eq(self.rx.data[:4])

        # PIDs are followed by a 4-bit field equal to their one's complement.
        rx_pid_valid = Signal()
        m.d.comb += rx_pid_valid.eq((rx_pid ^ self.rx.data[4:]).all())

        # DATA0 and DATA1 PIDs are alternated between non-isochronous transactions to let the
        # recipient know if it missed a data packet.
        # The `rx_seq[ep]` bit tracks the expected PID for host->device transactions, and
        # the `tx_seq[ep]` bit tracks the expected PID for device->host transactions.
        # See section 8.6 of the USB 2.0 specification for details.
        rx_seq = Array(Signal(16, name="rx_seq"))
        tx_seq = Array(Signal(16, name="tx_seq"))

        token_dev   = Signal(7)
        token_ep    = Signal(4)
        token_setup = Signal()

        expect_handshake = Signal()

        with m.FSM() as fsm:
            with m.State("IDLE"):
                m.d.comb += self.rx.rdy.eq(1)
                with m.If(self.rx.stb):
                    with m.If(rx_pid_valid):
                        m.d.sync += rx_pid_r.eq(rx_pid)
                        with m.If(self.rx.lst):
                            with m.If(PacketID.is_handshake(rx_pid)
                                    # Ignore handshake packets if we are not expecting one.
                                    & expect_handshake):
                                m.next = "RECV-HANDSHAKE"
                        with m.Else():
                            with m.If(PacketID.is_token(rx_pid)
                                    # PING packets use the same encoding as token packets.
                                    | (rx_pid == PacketID.PING)):
                                m.next = "RECV-TOKEN-0"
                            with m.Else():
                                m.next = "FLUSH-PACKET"
                    with m.Elif(~self.rx.lst):
                        m.next = "FLUSH-PACKET"

            with m.State("RECV-HANDSHAKE"):
                with m.If(rx_pid_r == PacketID.ACK):
                    m.d.comb += [
                        mux_in.pkt.rdy.eq(1),
                        mux_in.pkt.ack.eq(1),
                    ]
                    # Toggle the transmitter-side sequence bit upon receipt of an ACK.
                    m.d.sync += tx_seq[token_ep].eq(~tx_seq[token_ep])
                m.d.sync += expect_handshake.eq(0)
                m.next = "IDLE"

            with m.State("RECV-TOKEN-0"):
                m.d.comb += [
                    token_sink.rx.stb .eq(self.rx.stb),
                    token_sink.rx.lst .eq(self.rx.lst),
                    token_sink.rx.data.eq(self.rx.data),
                    self.rx.rdy.eq(token_sink.rx.rdy),
                ]
                with m.If(token_sink.stb):
                    with m.If(self.rx.lst):
                        m.d.sync += [
                            token_dev.eq(token_sink.dev),
                            token_ep .eq(token_sink.ep),
                        ]
                        m.next = "RECV-TOKEN-1"
                    with m.Else():
                        m.next = "FLUSH-PACKET"
                with m.Elif(self.rx.stb & self.rx.lst):
                    m.next = "IDLE"

            with m.State("RECV-TOKEN-1"):
                with m.If(rx_pid_r == PacketID.SOF):
                    # When a new (micro)frame starts, assume any ongoing transaction has timed out.
                    m.d.sync += expect_handshake.eq(0)
                    m.d.comb += [
                        mux_out.sof.eq(1),
                        mux_in .sof.eq(1),
                    ]
                    m.next = "IDLE"
                with m.Elif(token_dev == self.addr):
                    with m.Switch(rx_pid_r):
                        with m.Case(PacketID.PING):
                            m.d.sync += mux_out.sel.addr.eq(token_ep)
                            m.next = "SEND-PONG"
                        with m.Case(PacketID.SETUP):
                            m.d.sync += token_setup.eq(1)
                            # Upon receipt of a SETUP token, we set the receiver-side sequence bit
                            # to 0, and the transmitter-side sequence bit to 1. This guarantees
                            # that at the end of the transaction (after receipt of a DATA0 packet),
                            # both sequence bits will be equal to 1.
                            m.d.sync += [
                                rx_seq[token_ep].eq(0),
                                tx_seq[token_ep].eq(1),
                            ]
                            m.d.sync += mux_out.sel.addr.eq(token_ep)
                            m.next = "RECV-DATA-0"
                        with m.Case(PacketID.OUT):
                            m.d.sync += mux_out.sel.addr.eq(token_ep)
                            m.next = "RECV-DATA-0"
                        with m.Case(PacketID.IN):
                            m.d.sync += mux_in .sel.addr.eq(token_ep)
                            m.next = "SEND-DATA-0"
                        with m.Default():
                            # Unknown/unsupported token.
                            m.next = "IDLE"
                with m.Else():
                    # We are not the recipient of this token.
                    m.next = "IDLE"

            with m.State("SEND-PONG"):
                with m.If(mux_out.sel.err):
                    # Invalid endpoint. Abort transaction.
                    m.next = "IDLE"
                with m.Elif(mux_out.pkt.rdy):
                    m.next = "SEND-ACK"
                with m.Else():
                    m.next = "SEND-NAK"

            with m.State("RECV-DATA-0"):
                expected_pid = Signal.like(rx_pid)
                m.d.comb += expected_pid.eq(Mux(rx_seq[token_ep], PacketID.DATA1, PacketID.DATA0))
                with m.If(mux_out.sel.err):
                    # Invalid endpoint. Abort transaction.
                    m.next = "FLUSH-PACKET"
                with m.Else():
                    m.d.comb += self.rx.rdy.eq(1)
                    with m.If(self.rx.stb):
                        with m.If(self.rx.lst):
                            m.next = "IDLE"
                        with m.Elif(rx_pid_valid):
                            with m.If(mux_out.sel.xfer != Transfer.ISOCHRONOUS):
                                with m.If(rx_pid == expected_pid):
                                    m.next = "RECV-DATA-1"
                                with m.Else():
                                    m.next = "FLUSH-PACKET"
                            with m.Else():
                                # FIXME: Data PID sequencing for isochronous transfers (section
                                # 5.9.2 of the USB 2.0 specification) isn't implemented.
                                # Be lenient and accept any data PID.
                                with m.If(PacketID.is_data(rx_pid)):
                                    m.next = "RECV-DATA-1"
                                with m.Else():
                                    m.next = "FLUSH-PACKET"
                        with m.Else():
                            m.next = "FLUSH-PACKET"

            with m.State("RECV-DATA-1"):
                ep_busy = Signal()
                m.d.comb += [
                    data_sink.rx.stb .eq(self.rx.stb),
                    data_sink.rx.lst .eq(self.rx.lst),
                    data_sink.rx.data.eq(self.rx.data),
                    self.rx.rdy.eq(data_sink.rx.rdy),

                    mux_out.pkt.stb  .eq(data_sink.stb),
                    mux_out.pkt.lst  .eq(data_sink.lst),
                    mux_out.pkt.data .eq(data_sink.data),
                    mux_out.pkt.zlp  .eq(data_sink.zlp),
                    mux_out.pkt.drop .eq(data_sink.drop),
                    mux_out.pkt.setup.eq(token_setup),
                ]
                with m.If(mux_out.pkt.stb):
                    with m.If(~mux_out.pkt.rdy):
                        m.d.sync += ep_busy.eq(1)
                    with m.If(mux_out.pkt.lst):
                        m.d.sync += ep_busy.eq(0)
                        m.d.sync += token_setup.eq(0)
                        with m.If(mux_out.pkt.drop):
                            # CRC check failed. Ignore packet.
                            m.next = "IDLE"
                        with m.Elif(mux_out.sel.xfer == Transfer.ISOCHRONOUS):
                            # Isochronous transactions do not include a handshake.
                            m.next = "IDLE"
                        with m.Elif(~mux_out.pkt.rdy | ep_busy):
                            # Endpoint wasn't able to receive the whole payload.
                            m.next = "SEND-NAK"
                        with m.Else():
                            # Toggle the receiver-side sequence bit upon receipt of a valid data
                            # packet.
                            m.d.sync += rx_seq[token_ep].eq(~rx_seq[token_ep])
                            m.next = "SEND-ACK"

            with m.State("SEND-DATA-0"):
                with m.If(mux_in.sel.err):
                    # Invalid endpoint. Abort transaction.
                    m.next = "IDLE"
                with m.Elif(mux_in.pkt.stb):
                    m.d.comb += [
                        self.tx.stb.eq(1),
                        self.tx.lst.eq(0),
                    ]
                    with m.If(tx_seq[token_ep]):
                        m.d.comb += [
                            self.tx.data[:4].eq( PacketID.DATA1),
                            self.tx.data[4:].eq(~PacketID.DATA1),
                        ]
                    with m.Else():
                        m.d.comb += [
                            self.tx.data[:4].eq( PacketID.DATA0),
                            self.tx.data[4:].eq(~PacketID.DATA0),
                        ]
                    with m.If(self.tx.rdy):
                        m.next = "SEND-DATA-1"
                with m.Else():
                    # Endpoint is not ready to send a payload.
                    with m.If(mux_in.sel.xfer == Transfer.ISOCHRONOUS):
                        m.next = "IDLE"
                    with m.Else():
                        m.next = "SEND-NAK"

            with m.State("SEND-DATA-1"):
                m.d.comb += [
                    data_source.tx.connect(self.tx),
                    data_source.stb .eq(mux_in.pkt.stb),
                    data_source.lst .eq(mux_in.pkt.lst),
                    data_source.data.eq(mux_in.pkt.data),
                    data_source.zlp .eq(mux_in.pkt.zlp),
                    mux_in.pkt.rdy.eq(data_source.rdy),
                ]
                with m.If(self.tx.stb & self.tx.lst & self.tx.rdy):
                    m.d.sync += expect_handshake.eq(1)
                    m.next = "IDLE"

            with m.State("SEND-ACK"):
                m.d.comb += [
                    self.tx.stb.eq(1),
                    self.tx.lst.eq(1),
                    self.tx.data[:4].eq( PacketID.ACK),
                    self.tx.data[4:].eq(~PacketID.ACK),
                ]
                with m.If(self.tx.rdy):
                    m.next = "IDLE"

            with m.State("SEND-NAK"):
                m.d.comb += [
                    self.tx.stb.eq(1),
                    self.tx.lst.eq(1),
                    self.tx.data[:4].eq( PacketID.NAK),
                    self.tx.data[4:].eq(~PacketID.NAK),
                ]
                with m.If(self.tx.rdy):
                    m.next = "IDLE"

            with m.State("FLUSH-PACKET"):
                m.d.comb += self.rx.rdy.eq(1)
                with m.If(self.rx.stb & self.rx.lst):
                    m.next = "IDLE"

        return m


class _TokenSink(Elaboratable):
    def __init__(self):
        self.rx = Record([
            ("stb",  1, DIR_FANIN),
            ("lst",  1, DIR_FANIN),
            ("data", 8, DIR_FANIN),
            ("rdy",  1, DIR_FANOUT),
        ])
        self.stb = Signal()
        self.dev = Signal(7)
        self.ep  = Signal(4)
        self.crc = Signal(5)

    def elaborate(self, platform):
        m = Module()

        m.submodules.crc = crc = CRC(poly=0b00101, size=5, dw=11, init=0x1f)

        ep_lsb = Signal()
        ep_msb = Signal(3)
        m.d.comb += self.ep.eq(Cat(ep_lsb, ep_msb))

        m.d.comb += self.rx.rdy.eq(1)
        with m.If(self.rx.stb):
            token_msb = Signal()
            with m.If(~token_msb):
                m.d.sync += Cat(self.dev, ep_lsb).eq(self.rx.data)
                m.d.sync += token_msb.eq(1)
            with m.Else():
                m.d.comb += Cat(ep_msb, self.crc).eq(self.rx.data)
                m.d.comb += [
                    crc.val.eq(Cat(self.dev, self.ep)),
                    self.stb.eq(crc.res == self.crc),
                ]
                m.d.sync += token_msb.eq(0)

        return m


class _DataSink(Elaboratable):
    def __init__(self):
        self.rx = Record([
            ("stb",  1, DIR_FANIN),
            ("lst",  1, DIR_FANIN),
            ("data", 8, DIR_FANIN),
            ("rdy",  1, DIR_FANOUT),
        ])
        self.stb  = Signal()
        self.lst  = Signal()
        self.data = Signal(8)
        self.zlp  = Signal()
        self.drop = Signal()

    def elaborate(self, platform):
        m = Module()

        buf_0 = Record([("stb", 1), ("lst", 1), ("data", 8)])
        buf_1 = Record.like(buf_0)

        m.submodules.crc = crc = CRC(poly=0b11000000000000101, size=16, dw=8, init=0xffff)

        with m.If(self.stb & self.lst):
            m.d.sync += [
                buf_0.stb.eq(0),
                buf_1.stb.eq(0),
            ]
        with m.Else():
            m.d.comb += self.rx.rdy.eq(1)
            with m.If(self.rx.stb):
                m.d.sync += [
                    buf_0.stb.eq(1),
                    buf_0.lst.eq(self.rx.lst),
                    buf_0.data.eq(self.rx.data),
                    buf_1.eq(buf_0),
                ]

        m.d.comb += [
            crc.en.eq(self.rx.stb & buf_1.stb),
            crc.val.eq(buf_1.data),
            crc.clr.eq(self.stb & self.lst),
        ]

        with m.If(buf_1.stb):
            with m.If(buf_0.lst):
                # We received a zero-length packet. (no data bytes, CRC field is 0)
                m.d.comb += [
                    self.stb.eq(1),
                    self.lst.eq(1),
                    self.zlp.eq(1),
                    self.drop.eq(Cat(buf_1.data, buf_0.data).any()),
                ]
            with m.Else():
                m.d.comb += [
                    self.stb.eq(self.rx.stb),
                    self.lst.eq(self.rx.lst),
                    self.data.eq(buf_1.data),
                    self.drop.eq(crc.res != Cat(buf_0.data, self.rx.data)),
                ]

        return m


class _DataSource(Elaboratable):
    def __init__(self):
        self.tx = Record([
            ("stb",  1, DIR_FANOUT),
            ("lst",  1, DIR_FANOUT),
            ("data", 8, DIR_FANOUT),
            ("rdy",  1, DIR_FANIN),
        ])
        self.stb  = Signal()
        self.lst  = Signal()
        self.data = Signal(8)
        self.zlp  = Signal()
        self.rdy  = Signal()

    def elaborate(self, platform):
        m = Module()

        m.submodules.crc = crc = CRC(poly=0b11000000000000101, size=16, dw=8, init=0xffff)
        crc_res_r = Signal.like(crc.res)

        with m.FSM():
            with m.State("DATA"):
                m.d.comb += [
                    self.rdy.eq(self.tx.rdy),
                    self.tx.stb.eq(self.stb),
                    self.tx.data.eq(Mux(self.zlp, 0, self.data)),
                    crc.en.eq(self.stb & self.rdy),
                    crc.val.eq(self.data),
                ]
                with m.If(self.stb & self.rdy & self.lst):
                    m.d.sync += crc_res_r.eq(crc.res)
                    m.d.comb += crc.clr.eq(1)
                    with m.If(self.zlp):
                        m.next = "ZLP"
                    with m.Else():
                        m.next = "CRC-0"

            with m.State("ZLP"):
                m.d.comb += [
                    self.tx.stb.eq(1),
                    self.tx.lst.eq(1),
                    self.tx.data.eq(0),
                ]
                with m.If(self.tx.rdy):
                    m.next = "DATA"

            with m.State("CRC-0"):
                m.d.comb += [
                    self.tx.stb.eq(1),
                    self.tx.data.eq(crc_res_r[:8]),
                ]
                with m.If(self.tx.rdy):
                    m.next = "CRC-1"

            with m.State("CRC-1"):
                m.d.comb += [
                    self.tx.stb.eq(1),
                    self.tx.lst.eq(1),
                    self.tx.data.eq(crc_res_r[8:]),
                ]
                with m.If(self.tx.rdy):
                    m.next = "DATA"

        return m
