from collections import OrderedDict

from nmigen import *

from .ctl import Controller
from .mux import InputMultiplexer, OutputMultiplexer


__all__ = ["Device"]


class Device(Elaboratable):
    def __init__(self, phy):
        self.phy = phy
        self._mux_in  = InputMultiplexer()
        self._mux_out = OutputMultiplexer()

    def add_endpoint(self, ep, *, addr, dir, buffered=False):
        if dir not in ("i", "o"):
            raise ValueError("Endpoint direction must be 'i' or 'o', not {!r}"
                             .format(dir))
        if dir == "i":
            self._mux_in .add_endpoint(ep, addr=addr, buffered=buffered)
        if dir == "o":
            self._mux_out.add_endpoint(ep, addr=addr, buffered=buffered)

    def elaborate(self, platform):
        m = Module()

        m.submodules.ctrl = ctrl = Controller(self.phy)
        m.submodules.mux_in  = mux_in  = self._mux_in
        m.submodules.mux_out = mux_out = self._mux_out

        m.d.comb += [
            mux_out.cmd.stb.eq(ctrl.source_write.valid),
            mux_out.cmd.addr.eq(ctrl.source_write.ep),
            ctrl.source_write.ready.eq(mux_out.cmd.rdy),
            ctrl.write_xfer.eq(mux_out.cmd.xfer),

            mux_out.pkt.stb.eq(ctrl.source_data.valid),
            mux_out.pkt.lst.eq(ctrl.source_data.last),
            mux_out.pkt.data.eq(ctrl.source_data.data),
            mux_out.pkt.setup.eq(ctrl.source_data.setup),
            mux_out.pkt.drop.eq(~ctrl.source_data.crc_ok),
            ctrl.source_data.ready.eq(mux_out.pkt.rdy),

            mux_in.cmd.stb.eq(ctrl.sink_read.valid),
            mux_in.cmd.addr.eq(ctrl.sink_read.ep),
            ctrl.sink_read.ready.eq(mux_in.cmd.rdy),
            ctrl.read_xfer.eq(mux_in.cmd.xfer),

            ctrl.sink_data.valid.eq(mux_in.pkt.stb),
            ctrl.sink_data.last.eq(mux_in.pkt.lst),
            ctrl.sink_data.data.eq(mux_in.pkt.data),
            ctrl.sink_data.empty.eq(mux_in.pkt.zlp),
            mux_in.pkt.rdy.eq(ctrl.sink_data.ready),
            mux_in.pkt.ack.eq(ctrl.host_ack),
        ]

        return m
