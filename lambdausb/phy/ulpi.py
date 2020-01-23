from nmigen import *

from ..lib import stream


__all__ = ["ULPIPhy"]


class ULPIPhy(Elaboratable):
    def __init__(self, pads):
        self.pads = pads

        self.sink = stream.Endpoint([("data", 8)])
        self.source = stream.Endpoint([("data", 8)])

    def elaborate(self, platform):
        m = Module()

        cd_ulpi = m.domains.cd_ulpi = ClockDomain("ulpi", local=False)
        m.submodules += Instance("BUFG",
            i_I=self.pads.clk.i,
            o_O=cd_ulpi.clk
        )

        ctl = m.submodules.ctl = DomainRenamer("ulpi")(ULPIDeviceController(self.pads))

        rx_fifo = stream.AsyncFIFO([("data", 8)], 128, w_domain="ulpi", r_domain="sync")
        m.submodules.rx_fifo = rx_fifo

        tx_fifo = stream.AsyncFIFO([("data", 8)], 128, w_domain="sync", r_domain="ulpi")
        m.submodules.tx_fifo = tx_fifo

        m.d.comb += [
            ctl.source.connect(rx_fifo.sink),
            rx_fifo.source.connect(self.source),
            self.sink.connect(tx_fifo.sink),
            tx_fifo.source.connect(ctl.sink)
        ]

        return m


class ULPIPhy2(Elaboratable): # TODO rename
    def __init__(self, pads):
        self.sink   = stream.Endpoint([('data', 8)])
        self.source = stream.Endpoint([('data', 8), ('cmd', 1)])
        self.reset  = Signal()
        self.pads   = pads

    def elaborate(self, platform):
        m = Module()

        dir_r = Signal()
        m.d.sync += dir_r.eq(self.pads.dir.i)

        m.d.comb += self.pads.rst.o.eq(self.reset)

        # Transmit
        with m.If(~dir_r & ~self.pads.dir.i):
            m.d.comb += self.pads.data.oe.eq(1)
            with m.If(~self.pads.stp.o):
                with m.If(self.sink.valid):
                    m.d.comb += self.pads.data.o.eq(self.sink.data)
                    with m.If(self.sink.last & self.pads.nxt.i):
                        m.d.sync += self.pads.stp.o.eq(1)
                m.d.comb += self.sink.ready.eq(self.pads.nxt.i)

        with m.If(self.pads.stp.o):
            m.d.sync += self.pads.stp.o.eq(0)

        # Receive
        with m.If(dir_r & self.pads.dir.i):
            m.d.sync += [
                self.source.valid.eq(1),
                self.source.data.eq(self.pads.data.i),
                self.source.cmd.eq(~self.pads.nxt.i)
            ]
        with m.Else():
            m.d.sync += self.source.valid.eq(0)

        m.d.comb += self.source.last.eq(dir_r & ~self.pads.dir.i)

        return m


class ULPIPhyS7(Elaboratable):
    def __init__(self, pads):
        self.sink   = stream.Endpoint([('data', 8)])
        self.source = stream.Endpoint([('data', 8), ('cmd', 1)])
        self.reset  = Signal()
        self.pads   = pads

    def elaborate(self, platform):
        m = Module()

        last = Signal()
        odir = Signal()

        data_i = Signal(8)
        for i in range(8):
            m.submodules += Instance("IDDR",
                p_DDR_CLK_EDGE="SAME_EDGE", p_INIT_Q1=0, p_INIT_Q2=0, p_SRTYPE="ASYNC",
                i_C=ClockSignal("sync"),
                i_CE=Const(1), i_S=Const(0), i_R=Const(0),
                i_D=self.pads.data.i[i], o_Q1=Signal(), o_Q2=data_i[i]
            )

        m.d.comb += [
            self.pads.rst.eq(self.reset),
            self.pads.data.oe.eq(~odir)
        ]

        with m.If(self.sink.valid & ~last):
            m.d.comb += self.pads.data.o.eq(self.sink.data)
        with m.Else():
            m.d.comb += self.pads.data.o.eq(0)
        m.d.comb += self.sink.ready.eq(~self.pads.dir & self.pads.nxt)
        with m.If(~self.pads.dir):
            m.d.comb += self.pads.stp.eq(last)
        m.d.comb += [
            self.source.last.eq(odir & ~self.pads.dir),
            self.source.data.eq(data_i)
        ]

        with m.If(self.pads.nxt):
            m.d.sync += last.eq(self.sink.last)
        with m.Else():
            m.d.sync += last.eq(0)

        m.d.sync += [
            odir.eq(self.pads.dir),
            self.source.cmd.eq(~self.pads.nxt),
            self.source.valid.eq(odir & self.pads.dir)
        ]

        return m


class ULPITimer(Elaboratable):
    def __init__(self):
        self.cnt50ns = Signal() # 50ns 256
        self.cnt2ms  = Signal() # 2ms  120000
        self.cnt3ms  = Signal() # 3ms  180000
        self.cnt10ms = Signal() # 10ms 600000
        self.cnt5s   = Signal()
        self.done    = Signal()

    def elaborate(self, platform):
        m = Module()

        counter = Signal(30)

        with m.If(self.cnt2ms | self.cnt3ms | self.cnt10ms | self.cnt50ns | self.cnt5s):
            with m.If(self.done):
                m.d.sync += counter.eq(0)
            with m.Else():
                m.d.sync += counter.eq(counter + 1)
        with m.Else():
            m.d.sync += counter.eq(0)

        with m.If(self.cnt50ns & (counter == 256)):
            m.d.comb += self.done.eq(1)
        with m.Elif(self.cnt2ms & (counter == 120000)):
            m.d.comb += self.done.eq(1)
        with m.Elif(self.cnt3ms & (counter == 180000)):
            m.d.comb += self.done.eq(1)
        with m.Elif(self.cnt10ms & (counter == 600000)):
            m.d.comb += self.done.eq(1)
        with m.Elif(self.cnt5s & (counter == 2**28)):
            m.d.comb += self.done.eq(1)

        return m


class ULPISplitter(Elaboratable):
    def __init__(self):
        self.sink = stream.Endpoint([('data', 8), ('cmd', 1)])
        self.source = stream.Endpoint([('data', 8)])

    def elaborate(self, platform):
        m = Module()

        prevdata = Signal(8)
        prevdataset = Signal()

        with m.If(self.sink.valid):
            with m.If(~self.sink.cmd):
                with m.If(prevdataset):
                    m.d.sync += [
                        self.source.valid.eq(1),
                        self.source.data.eq(prevdata),
                        self.source.last.eq(0)
                    ]
                with m.Else():
                    m.d.sync += self.source.valid.eq(0)
                m.d.sync += [
                    prevdata.eq(self.sink.data),
                    prevdataset.eq(1)
                ]
            with m.Else():
                with m.If(self.sink.data & 0x38 == 0x08):
                    with m.If(prevdataset):
                        m.d.sync += [
                            self.source.valid.eq(1),
                            self.source.last.eq(1),
                            self.source.data.eq(prevdata),
                            prevdataset.eq(0)
                        ]
                    with m.Else():
                        m.d.sync += self.source.valid.eq(0)
                with m.Else():
                    m.d.sync += self.source.valid.eq(0)
        with m.Else():
            m.d.sync += self.source.valid.eq(0)

        return m


class ULPISender(Elaboratable):
    def __init__(self):
        self.sink = stream.Endpoint([("data", 8)])
        self.source = stream.Endpoint([("data", 8)])

    def elaborate(self, platform):
        m = Module()

        lst_r = Signal(reset=1)

        #detect first byte in order to replace it with 0100xxxx with xxxx being the PID
        with m.If(self.sink.valid & self.sink.ready):
            m.d.sync += lst_r.eq(self.sink.last)

        with m.If(lst_r):
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


class ULPIDeviceController(Elaboratable):
    def __init__(self, pads):
        self.pads = pads

        self.sink = stream.Endpoint([("data", 8)])
        self.source = stream.Endpoint([("data", 8)])

    def elaborate(self, platform):
        m = Module()

        # phy      = m.submodules.phy      = ULPIPhyS7(self.pads)
        phy      = m.submodules.phy      = ULPIPhy2(self.pads)
        timer    = m.submodules.timer    = ULPITimer()
        splitter = m.submodules.splitter = ULPISplitter()
        sender   = m.submodules.sender   = ULPISender()

        m.d.comb += [
            self.sink.connect(sender.sink),
            splitter.source.connect(self.source)
        ]

        line_state = Signal(2)
        with m.If(phy.source.valid & phy.source.cmd):
            m.d.sync += line_state.eq(phy.source.data[:2])

        is_hs = Signal()

        with m.FSM() as fsm:
            with m.State("INIT0"):
                m.d.sync += is_hs.eq(0)
                m.d.comb += [
                    phy.reset.eq(1),
                    timer.cnt10ms.eq(1)
                ]
                with m.If(timer.done):
                    m.next = "INIT"

            with m.State("INIT"):
                m.d.comb += timer.cnt10ms.eq(1)
                with m.If(timer.done):
                    m.next = "RESET-PHY-1"

            with m.State("RESET-PHY-1"):
                m.d.comb += [
                    phy.sink.data.eq(0x80 | 0x4),
                    phy.sink.valid.eq(1)
                ]
                with m.If(phy.sink.ready):
                    m.next = "RESET-PHY-2"
                m.d.comb += timer.cnt5s.eq(1)
                with m.If(timer.done):
                    m.next = "INIT0"

            with m.State("RESET-PHY-2"):
                m.d.comb += [
                    phy.sink.data.eq(0b01100101),
                    phy.sink.last.eq(1),
                    phy.sink.valid.eq(1),
                ]
                with m.If(phy.source.valid):
                    m.next = "WRITE-OTGCTRL-1"
                with m.Elif(timer.done):
                    m.next = "INIT"

            with m.State("WRITE-OTGCTRL-1"):
                m.d.comb += [
                    phy.sink.data.eq(0x80 | 0xa),
                    phy.sink.valid.eq(1)
                ]
                with m.If(phy.sink.ready):
                    m.next = "WRITE-OTGCTRL-2"

            with m.State("WRITE-OTGCTRL-2"):
                m.d.comb += [
                    phy.sink.data.eq(0),
                    phy.sink.last.eq(1),
                    phy.sink.valid.eq(1)
                ]
                with m.If(phy.sink.ready):
                    m.next = "IDLE"
                m.d.comb += timer.cnt50ns.eq(1)
                with m.If(timer.done):
                    m.next = "WRITE-OTGCTRL-1"

            with m.State("IDLE"):
                with m.If(line_state == 0):
                    m.d.comb += timer.cnt2ms.eq(1)
                with m.If(timer.done):
                    with m.If(is_hs):
                        m.next = "INIT0"
                    with m.Else():
                        m.next = "CHIRP-0"
                m.d.comb += [
                    phy.source.connect(splitter.sink),
                    sender.source.connect(phy.sink)
                ]

            with m.State("CHIRP-0"):
                m.d.comb += [
                    phy.sink.data.eq(0x80 | 0x4),
                    phy.sink.valid.eq(1)
                ]
                with m.If(phy.sink.ready):
                    m.next = "CHIRP-1"

            with m.State("CHIRP-1"):
                m.d.comb += [
                    phy.sink.data.eq(0b01010000),
                    phy.sink.last.eq(1),
                    phy.sink.valid.eq(1)
                ]
                with m.If(phy.sink.ready):
                    m.next = "CHIRP-2"

            with m.State("CHIRP-2"):
                m.d.comb += [
                    phy.sink.valid.eq(1),
                    phy.sink.data.eq(0b01000000)
                ]
                with m.If(phy.sink.ready):
                    m.next = "CHIRP-3"

            with m.State("CHIRP-3"):
                m.d.comb += [
                    phy.sink.valid.eq(1),
                    phy.sink.data.eq(0x00),
                    timer.cnt2ms.eq(1)
                ]
                with m.If(timer.done):
                    m.next = "CHIRP-4"
                    m.d.comb += phy.sink.last.eq(1)

            with m.State("CHIRP-4"):
                m.d.comb += timer.cnt2ms.eq(1)
                with m.If(timer.done):
                    m.next = "CHIRP-5"

            with m.State("CHIRP-5"):
                m.d.comb += [
                    phy.sink.data.eq(0x80 | 0x4),
                    phy.sink.valid.eq(1)
                ]
                with m.If(phy.sink.ready):
                    m.next = "CHIRP-6"

            with m.State("CHIRP-6"):
                m.d.comb += [
                    phy.sink.data.eq(0b01000000),
                    phy.sink.last.eq(1),
                    phy.sink.valid.eq(1)
                ]
                with m.If(phy.sink.ready):
                    m.d.sync += is_hs.eq(1)
                    m.next = "IDLE"

        return m
