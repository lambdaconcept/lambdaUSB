from collections import OrderedDict

from nmigen import *
from nmigen.hdl.rec import *

from .endpoint import *


__all__ = ["DoubleBuffer", "InputMultiplexer", "OutputMultiplexer"]


class DoubleBuffer(Elaboratable):
    def __init__(self, *, depth, width, read_ack=False):
        self.w_stb  = Signal()
        self.w_lst  = Signal()
        self.w_data = Signal(width)
        self.w_drop = Signal()
        self.w_rdy  = Signal()

        self.r_stb  = Signal()
        self.r_lst  = Signal()
        self.r_data = Signal(width)
        self.r_rdy  = Signal()
        self.r_ack  = Signal(1 if read_ack else 0)

        self.depth = depth
        self.width = width
        self.read_ack = read_ack

    def elaborate(self, platform):
        m = Module()

        banks = [Record([("w_addr", range(self.depth)), ("w_data", self.width), ("w_en", 1),
                         ("r_addr", range(self.depth)), ("r_data", self.width), ("r_en", 1),
                         ("valid",  1), ("level", range(self.depth + 1))],
                         name="bank_{}".format(i))
                      for i in range(2)]

        for i, bank in enumerate(banks):
            mem = Memory(depth=self.depth, width=self.width)
            m.submodules["mem{}_wp".format(i)] = mem_wp = mem.write_port()
            m.submodules["mem{}_rp".format(i)] = mem_rp = mem.read_port(transparent=False)
            m.d.comb += [
                mem_wp.addr.eq(bank.w_addr),
                mem_wp.data.eq(bank.w_data),
                mem_wp.en.eq(bank.w_en),
                mem_rp.addr.eq(bank.r_addr),
                mem_rp.en.eq(bank.r_en),
                bank.r_data.eq(mem_rp.data),
            ]

        bank_lru = Signal()

        with m.FSM() as write_fsm:
            for i, bank in enumerate(banks):
                with m.State("WRITE-{}".format(i)):
                    w_addr_inc = Signal.like(bank.w_addr, name_suffix="_inc")
                    m.d.comb += w_addr_inc.eq(bank.w_addr + 1)
                    m.d.comb += [
                        self.w_rdy.eq(1),
                        bank.w_en.eq(self.w_stb),
                        bank.w_data.eq(self.w_data),
                    ]
                    with m.If(self.w_stb):
                        with m.If(w_addr_inc == self.depth):
                            # Overflow. Flush remaining bytes.
                            m.d.sync += bank.w_addr.eq(0)
                            m.next = "FLUSH"
                        with m.Elif(self.w_lst):
                            m.d.sync += bank.w_addr.eq(0)
                            m.next = "WAIT"
                            with m.If(~self.w_drop):
                                m.d.sync += [
                                    bank.valid.eq(1),
                                    bank.level.eq(w_addr_inc),
                                    bank_lru.eq(1 - i),
                                ]
                        with m.Else():
                            m.d.sync += bank.w_addr.eq(w_addr_inc)

            with m.State("FLUSH"):
                m.d.comb += self.w_rdy.eq(1)
                with m.If(self.w_stb & self.w_lst):
                    m.next = "WAIT"

            with m.State("WAIT"):
                with m.If(~banks[0].valid):
                    m.next = "WRITE-0"
                with m.Elif(~banks[1].valid):
                    m.next = "WRITE-1"

        with m.FSM() as read_fsm:
            with m.State("WAIT"):
                with m.If(banks[0].valid & ~(banks[1].valid & bank_lru)):
                    m.d.comb += banks[0].r_en.eq(1)
                    m.d.sync += banks[0].r_addr.eq(1)
                    m.next = "READ-0"
                with m.Elif(banks[1].valid):
                    m.d.comb += banks[1].r_en.eq(1)
                    m.d.sync += banks[1].r_addr.eq(1)
                    m.next = "READ-1"

            for i, bank in enumerate(banks):
                with m.State("READ-{}".format(i)):
                    m.d.comb += [
                        self.r_stb.eq(1),
                        self.r_data.eq(bank.r_data),
                        self.r_lst.eq(bank.r_addr == bank.level),
                    ]
                    with m.If(self.r_rdy):
                        r_done = self.r_ack if self.read_ack else self.r_lst
                        with m.If(r_done):
                            m.d.sync += bank.valid.eq(0)
                            m.d.sync += bank.r_addr.eq(0)
                            m.next = "WAIT"
                        with m.Else():
                            m.d.comb += bank.r_en.eq(1)
                            m.d.sync += bank.r_addr.eq(Mux(self.r_lst, 0, bank.r_addr + 1))

        return m


class InputMultiplexer(Elaboratable):
    def __init__(self):
        self.cmd = Record([
            ("stb",  1, DIR_FANIN),
            ("addr", 4, DIR_FANIN),
            ("rdy",  1, DIR_FANOUT),
            ("xfer", 2, DIR_FANOUT),
        ])
        self.pkt = Record([
            ("stb",  1, DIR_FANOUT),
            ("lst",  1, DIR_FANOUT),
            ("data", 8, DIR_FANOUT),
            ("zlp",  1, DIR_FANOUT),
            ("rdy",  1, DIR_FANIN),
            ("ack",  1, DIR_FANIN),
        ])
        self.sof = Signal()

        self._ep_map = OrderedDict()

    def add_endpoint(self, ep, *, addr, buffered=True):
        if not isinstance(ep, InputEndpoint):
            raise ValueError("Endpoint must be an InputEndpoint, not {!r}"
                             .format(ep))
        if not isinstance(addr, int):
            raise TypeError("Endpoint address must be an integer, not {!r}"
                             .format(addr))
        if not addr in range(0, 16):
            raise ValueError("Endpoint address must be between 0 and 15, not {}"
                             .format(addr))
        if addr in self._ep_map:
            raise ValueError("Endpoint address {} has already been allocated"
                             .format(addr))
        self._ep_map[addr] = ep, buffered

    def elaborate(self, platform):
        m = Module()

        port_map = OrderedDict({addr: Record.like(self.pkt) for addr in self._ep_map})

        for addr, (ep, buffered) in self._ep_map.items():
            port = port_map[addr]
            if buffered:
                dbuf = DoubleBuffer(depth=ep.max_size, width=port.data.width + port.zlp.width,
                                    read_ack=True)
                m.submodules["dbuf_{}".format(addr)] = dbuf
                m.d.comb += [
                    dbuf.w_stb.eq(ep.stb),
                    dbuf.w_lst.eq(ep.lst),
                    dbuf.w_data.eq(Cat(ep.data, ep.zlp)),
                    ep.rdy.eq(dbuf.w_rdy),

                    port.stb.eq(dbuf.r_stb),
                    port.lst.eq(dbuf.r_lst),
                    Cat(port.data, port.zlp).eq(dbuf.r_data),
                    dbuf.r_rdy.eq(port.rdy),
                    dbuf.r_ack.eq(port.ack),
                ]
            else:
                m.d.comb += [
                    port.stb.eq(ep.stb),
                    port.lst.eq(ep.lst),
                    port.data.eq(ep.data),
                    port.zlp.eq(ep.zlp),
                    ep.rdy.eq(port.rdy),
                    ep.ack.eq(port.ack),
                ]
            m.d.comb += ep.sof.eq(self.sof)

        with m.Switch(self.cmd.addr):
            for addr, port in port_map.items():
                ep, _ = self._ep_map[addr]
                with m.Case(addr):
                    m.d.comb += [
                        self.cmd.rdy.eq(port.stb),
                        self.cmd.xfer.eq(ep.xfer),
                    ]

        port_addr = Signal.like(self.cmd.addr)
        with m.If(self.cmd.stb & self.cmd.rdy):
            m.d.sync += port_addr.eq(self.cmd.addr)

        with m.Switch(port_addr):
            for addr, port in port_map.items():
                with m.Case(addr):
                    m.d.comb += port.connect(self.pkt)

        return m


class OutputMultiplexer(Elaboratable):
    def __init__(self):
        self.cmd = Record([
            ("stb",  1, DIR_FANIN),
            ("addr", 4, DIR_FANIN),
            ("rdy",  1, DIR_FANOUT),
            ("xfer", 2, DIR_FANOUT),
        ])
        self.pkt = Record([
            ("stb",   1, DIR_FANIN),
            ("lst",   1, DIR_FANIN),
            ("data",  8, DIR_FANIN),
            ("setup", 1, DIR_FANIN),
            ("drop",  1, DIR_FANIN),
            ("rdy",   1, DIR_FANOUT),
        ])
        self.sof = Signal()

        self._ep_map = OrderedDict()

    def add_endpoint(self, ep, *, addr, buffered=True):
        if not isinstance(ep, OutputEndpoint):
            raise ValueError("Endpoint must be an OutputEndpoint, not '{!r}'"
                             .format(ep))
        if not isinstance(addr, int):
            raise TypeError("Endpoint address must be an integer, not {!r}"
                             .format(addr))
        if not addr in range(0, 16):
            raise ValueError("Endpoint address must be between 0 and 15, not {}"
                             .format(addr))
        if addr in self._ep_map:
            raise ValueError("Endpoint address {} has already been allocated"
                             .format(addr))
        self._ep_map[addr] = ep, buffered

    def elaborate(self, platform):
        m = Module()

        port_map = OrderedDict({addr: Record.like(self.pkt) for addr in self._ep_map})

        for addr, (ep, buffered) in self._ep_map.items():
            port = port_map[addr]
            if buffered:
                dbuf = DoubleBuffer(depth=ep.max_size, width=port.data.width + port.setup.width)
                m.submodules["dbuf_{}".format(addr)] = dbuf
                m.d.comb += [
                    dbuf.w_stb.eq(port.stb),
                    dbuf.w_lst.eq(port.lst),
                    dbuf.w_data.eq(Cat(port.data, port.setup)),
                    dbuf.w_drop.eq(port.drop),
                    port.rdy.eq(dbuf.w_rdy),

                    ep.stb.eq(dbuf.r_stb),
                    ep.lst.eq(dbuf.r_lst),
                    Cat(ep.data, ep.setup).eq(dbuf.r_data),
                    dbuf.r_rdy.eq(ep.rdy),
                ]
            else:
                m.d.comb += [
                    ep.stb.eq(port.stb),
                    ep.lst.eq(port.lst),
                    ep.data.eq(port.data),
                    ep.setup.eq(port.setup),
                    ep.drop.eq(port.drop),
                    port.rdy.eq(ep.rdy),
                ]
            m.d.comb += ep.sof.eq(self.sof)

        with m.Switch(self.cmd.addr):
            for addr, port in port_map.items():
                ep, _ = self._ep_map[addr]
                with m.Case(addr):
                    m.d.comb += [
                        self.cmd.rdy.eq(port.rdy),
                        self.cmd.xfer.eq(ep.xfer),
                    ]

        port_addr = Signal.like(self.cmd.addr)
        with m.If(self.cmd.stb & self.cmd.rdy):
            m.d.sync += port_addr.eq(self.cmd.addr)

        with m.Switch(port_addr):
            for addr, port in port_map.items():
                with m.Case(addr):
                    m.d.comb += port.connect(self.pkt)

        return m
