from nmigen import *
from nmigen.hdl.rec import *
from nmigen.lib.cdc import AsyncFFSynchronizer

from ..lib import stream


__all__ = ["PHY", "Transceiver"]


class PHY(Elaboratable):
    def __init__(self, *, pins, rx_depth=32, tx_depth=32):
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

        self.dev_reset = Signal()

        self.rx_depth = rx_depth
        self.tx_depth = tx_depth
        self._pins = pins

    def elaborate(self, platform):
        m = Module()

        m.domains += ClockDomain("ulpi", local=True)

        m.submodules.xcvr = xcvr = Transceiver(domain="ulpi", pins=self._pins)
        m.submodules.timer = timer = _Timer()
        m.submodules.splitter = splitter = _Splitter()
        m.submodules.sender = sender = _Sender()

        usb_reset = Signal()
        m.submodules.usb_reset_sync = AsyncFFSynchronizer(usb_reset, self.dev_reset, domain="sync")

        rx_fifo = stream.AsyncFIFO([("data", 8)], self.rx_depth, w_domain="ulpi", r_domain="sync")
        tx_fifo = stream.AsyncFIFO([("data", 8)], self.tx_depth, w_domain="sync", r_domain="ulpi")
        m.submodules.rx_fifo = rx_fifo
        m.submodules.tx_fifo = tx_fifo

        m.d.comb += [
            self.rx.stb.eq(rx_fifo.source.valid),
            self.rx.lst.eq(rx_fifo.source.last),
            self.rx.data.eq(rx_fifo.source.data),
            rx_fifo.source.ready.eq(self.rx.rdy),

            tx_fifo.sink.valid.eq(self.tx.stb),
            tx_fifo.sink.last.eq(self.tx.lst),
            tx_fifo.sink.data.eq(self.tx.data),
            self.tx.rdy.eq(tx_fifo.sink.ready),

            splitter.source.connect(rx_fifo.sink),
            tx_fifo.source.connect(sender.sink),
        ]

        rx_cmd = Record([
            ("line_state", 2),
            ("vbus_state", 2),
            ("event",      2),
            ("id",         1),
            ("alt_int",    1),
        ])

        with m.If(xcvr.source.valid & xcvr.source.cmd):
            m.d.ulpi += rx_cmd.eq(xcvr.source.data)

        hs_mode = Signal()

        with m.FSM(domain="ulpi") as fsm:
            with m.State("RESET-0"):
                m.d.comb += xcvr.rst.eq(1)
                m.d.comb += timer.cnt25ns.eq(1)
                with m.If(timer.done):
                    m.next = "RESET-1"

            with m.State("RESET-1"):
                m.d.comb += timer.cnt25ns.eq(1)
                with m.If(timer.done):
                    m.next = "INIT-0"

            with m.State("INIT-0"):
                # Write Function Control register.
                m.d.comb += [
                    xcvr.sink.data.eq(0x80 | 0x4),
                    xcvr.sink.valid.eq(1)
                ]
                with m.If(xcvr.sink.ready):
                    m.next = "INIT-1"

            with m.State("INIT-1"):
                # XcvrSelect = 01 (Enable FS transceiver)
                # TermSelect =  1 (Peripheral FS)
                # OpMode     = 00 (Normal operation)
                # Reset      =  1
                # SuspendM   =  1 (Powered)
                # Reserved   =  0
                m.d.comb += [
                    xcvr.sink.data.eq(0b01100101),
                    xcvr.sink.last.eq(1),
                    xcvr.sink.valid.eq(1),
                ]
                m.d.comb += timer.cnt25ns.eq(1)
                with m.If(timer.done):
                    m.next = "INIT-0"
                with m.If(xcvr.sink.ready):
                    m.next = "INIT-2"

            with m.State("INIT-2"):
                with m.If(xcvr.source.valid & xcvr.source.cmd):
                    m.next = "INIT-3"

            with m.State("INIT-3"):
                m.d.comb += timer.cnt2ns.eq(1)
                with m.If(timer.done):
                    m.next = "INIT-4"

            with m.State("INIT-4"):
                # Write OTG Control register.
                m.d.comb += [
                    xcvr.sink.data.eq(0x80 | 0xa),
                    xcvr.sink.valid.eq(1)
                ]
                with m.If(xcvr.sink.ready):
                    m.next = "INIT-5"

            with m.State("INIT-5"):
                # DpPullDown = 0 (Disable D+ pull-down resistor)
                # DmPullDown = 0 (Disable D- pull-down resistor)
                m.d.comb += [
                    xcvr.sink.data.eq(0b00000000),
                    xcvr.sink.last.eq(1),
                    xcvr.sink.valid.eq(1)
                ]
                m.d.comb += timer.cnt25ns.eq(1)
                with m.If(timer.done):
                    m.next = "INIT-4"
                with m.If(xcvr.sink.ready):
                    m.next = "IDLE"

            with m.State("IDLE"):
                m.d.comb += [
                    xcvr.source.connect(splitter.sink),
                    sender.source.connect(xcvr.sink),
                ]
                with m.If(rx_cmd.line_state == 0b00):
                    m.d.comb += timer.cnt2ms.eq(1)
                with m.If(timer.done):
                    # A reset condition was detected.
                    m.d.comb += usb_reset.eq(1)
                    # If the link is Full Speed, we attempt a chirp handshake to advertise
                    # High Speed capability.
                    with m.If(hs_mode):
                        m.d.ulpi += hs_mode.eq(0)
                        m.next = "INIT-0"
                    with m.Else():
                        m.next = "CHIRP-0"

            with m.State("CHIRP-0"):
                # Write Function Control register.
                m.d.comb += [
                    xcvr.sink.data.eq(0x80 | 0x4),
                    xcvr.sink.valid.eq(1)
                ]
                with m.If(xcvr.sink.ready):
                    m.next = "CHIRP-1"

            with m.State("CHIRP-1"):
                # XcvrSelect = 00 (Enable HS transceiver)
                # TermSelect =  1 (Peripheral Chirp)
                # OpMode     = 10 (Disable bit-stuff and NRZI encoding)
                # Reset      =  0
                # SuspendM   =  1 (Powered)
                # Reserved   =  0
                m.d.comb += [
                    xcvr.sink.data.eq(0b01010100),
                    xcvr.sink.last.eq(1),
                    xcvr.sink.valid.eq(1)
                ]
                with m.If(xcvr.sink.ready):
                    m.next = "CHIRP-2"

            with m.State("CHIRP-2"):
                # Send a NOPID TXCMD.
                m.d.comb += [
                    xcvr.sink.valid.eq(1),
                    xcvr.sink.data.eq(0b01000000)
                ]
                with m.If(xcvr.sink.ready):
                    m.next = "CHIRP-3"

            with m.State("CHIRP-3"):
                # Send a K chirp for 2ms.
                m.d.comb += [
                    xcvr.sink.valid.eq(1),
                    xcvr.sink.data.eq(0x00),
                    timer.cnt2ms.eq(1)
                ]
                with m.If(timer.done):
                    m.next = "CHIRP-4"
                    m.d.comb += xcvr.sink.last.eq(1)

            with m.State("CHIRP-4"):
                # Host responds by alternating K and J chirps.
                # FIXME: Detect a K-J-K-J-K-J pattern before going further.
                m.d.comb += timer.cnt2ms.eq(1)
                with m.If(timer.done):
                    m.next = "CHIRP-5"

            with m.State("CHIRP-5"):
                # Write Function Control register.
                m.d.comb += [
                    xcvr.sink.data.eq(0x80 | 0x4),
                    xcvr.sink.valid.eq(1)
                ]
                with m.If(xcvr.sink.ready):
                    m.next = "CHIRP-6"

            with m.State("CHIRP-6"):
                # XcvrSelect = 00 (Enable HS transceiver)
                # TermSelect =  0 (Peripheral HS)
                # OpMode     = 00 (Normal mode)
                # Reset      =  0
                # SuspendM   =  1 (Powered)
                # Reserved   =  0
                m.d.comb += [
                    xcvr.sink.data.eq(0b01000000),
                    xcvr.sink.last.eq(1),
                    xcvr.sink.valid.eq(1)
                ]
                with m.If(xcvr.sink.ready):
                    m.d.ulpi += hs_mode.eq(1)
                    m.next = "IDLE"

        return m


class Transceiver(Elaboratable):
    def __init__(self, domain="ulpi", pins=None):
        self.sink   = stream.Endpoint([('data', 8)])
        self.source = stream.Endpoint([('data', 8), ('cmd', 1)])

        self.rst  = Signal()
        self.dir  = Signal()
        self.nxt  = Signal()
        self.stp  = Signal()
        self.data = Record([("i", 8), ("o", 8), ("oe", 1)])

        self._domain = domain
        self._pins   = pins

    def elaborate(self, platform):
        m = Module()

        if self._pins is not None:
            m.d.comb += [
                ClockSignal(self._domain).eq(self._pins.clk.i),
                self.dir.eq(self._pins.dir.i),
                self.nxt.eq(self._pins.nxt.i),
                self.data.i.eq(self._pins.data.i),
                self._pins.data.o.eq(self.data.o),
                self._pins.data.oe.eq(self.data.oe),
                self._pins.rst.o.eq(self.rst),
                self._pins.stp.o.eq(self.stp),
            ]

        dir_r = Signal()
        m.d[self._domain] += dir_r.eq(self.dir)

        # Transmit
        with m.If(~dir_r & ~self.dir):
            m.d.comb += self.data.oe.eq(1)
            with m.If(~self.stp):
                with m.If(self.sink.valid):
                    m.d.comb += self.data.o.eq(self.sink.data)
                    with m.If(self.sink.last & self.nxt):
                        m.d[self._domain] += self.stp.eq(1)
                m.d.comb += self.sink.ready.eq(self.nxt)

        with m.If(self.stp):
            m.d[self._domain] += self.stp.eq(0)

        # Receive
        with m.If(dir_r & self.dir):
            m.d[self._domain] += [
                self.source.valid.eq(1),
                self.source.data.eq(self.data.i),
                self.source.cmd.eq(~self.nxt)
            ]
        with m.Else():
            m.d[self._domain] += self.source.valid.eq(0)

        m.d.comb += self.source.last.eq(dir_r & ~self.dir)

        return m


class _Timer(Elaboratable):
    def __init__(self):
        self.cnt2ns  = Signal()
        self.cnt25ns = Signal()
        self.cnt2ms  = Signal()
        self.done    = Signal()

    def elaborate(self, platform):
        m = Module()

        counter = Signal(30)

        with m.If(self.cnt2ns | self.cnt25ns | self.cnt2ms):
            with m.If(self.done):
                m.d.ulpi += counter.eq(0)
            with m.Else():
                m.d.ulpi += counter.eq(counter + 1)
        with m.Else():
            m.d.ulpi += counter.eq(0)

        with m.If(self.cnt2ns & (counter == 10)):
            m.d.comb += self.done.eq(1)
        with m.If(self.cnt25ns & (counter == 120)):
            m.d.comb += self.done.eq(1)
        with m.If(self.cnt2ms & (counter == 120000)):
            m.d.comb += self.done.eq(1)

        return m


class _Splitter(Elaboratable):
    def __init__(self):
        self.sink   = stream.Endpoint([('data', 8), ('cmd', 1)])
        self.source = stream.Endpoint([('data', 8)])

    def elaborate(self, platform):
        m = Module()

        buf_data  = Signal(8)
        buf_valid = Signal()

        m.d.ulpi += self.source.valid.eq(0)

        with m.If(self.sink.valid):
            with m.If(~self.sink.cmd):
                m.d.ulpi += [
                    buf_data.eq(self.sink.data),
                    buf_valid.eq(1),
                ]
                with m.If(buf_valid):
                    m.d.ulpi += [
                        self.source.valid.eq(1),
                        self.source.data.eq(buf_data),
                        self.source.last.eq(0),
                    ]
            with m.Elif(self.sink.data & 0x38 == 0x08):
                with m.If(buf_valid):
                    m.d.ulpi += [
                        self.source.valid.eq(1),
                        self.source.last.eq(1),
                        self.source.data.eq(buf_data),
                        buf_valid.eq(0),
                    ]

        return m


class _Sender(Elaboratable):
    def __init__(self):
        self.sink   = stream.Endpoint([("data", 8)])
        self.source = stream.Endpoint([("data", 8)])

    def elaborate(self, platform):
        m = Module()

        last_r = Signal(reset=1)

        # Detect first byte and replace it with 0100xxxx (with xxxx being the PID).
        with m.If(self.sink.valid & self.sink.ready):
            m.d.ulpi += last_r.eq(self.sink.last)

        with m.If(last_r):
            m.d.comb += [
                self.source.data.eq(Cat(self.sink.data[0:4], 0b0100)),
                self.source.valid.eq(self.sink.valid),
                self.source.last.eq(self.sink.last),
                self.sink.ready.eq(self.source.ready)
            ]
        with m.Else():
            m.d.comb += [
                self.sink.connect(self.source)
            ]

        return m
