from collections import OrderedDict

from nmigen import *

from .lib import stream
from .ctl import USBController
from .buf import USBOutputBuffer, USBInputBuffer
from .conn import USBOutputArbiter, USBInputArbiter
from .protocol import Transfer


__all__ = ["USBDevice"]


class USBDevice(Elaboratable):
    def __init__(self, phy):
        self.phy        = phy
        self._input_map = OrderedDict()
        self._output_map  = OrderedDict()

        self.ep0_dev_addr = Signal(7)

    def input_port(self, ep_addr, max_size, xfer_type):
        if not isinstance(ep_addr, int) or not ep_addr in range(0, 16):
            raise TypeError("Endpoint address must be an integer in [0..16), not '{!r}'"
                            .format(ep_addr))
        if ep_addr in self._input_map:
            raise ValueError("An input port for endpoint {} has already been requested"
                             .format(ep_addr))
        if not isinstance(max_size, int) or not max_size in range(0, 513):
            raise TypeError("Maximum packet size must be an integer in [0..512], not '{!r}'"
                            .format(max_size))
        if not isinstance(xfer_type, Transfer):
            raise TypeError("Transfer type must be a member of the Transfer enum, not '{!r}'"
                            .format(xfer_type))

        if xfer_type == Transfer.CONTROL:
            port = stream.Endpoint([("empty", 1), ("data", 8)])
        else:
            port = stream.Endpoint([("data", 8)])
        self._input_map[ep_addr] = port, max_size, xfer_type
        return port

    def output_port(self, ep_addr, max_size, xfer_type):
        if not isinstance(ep_addr, int) or not ep_addr in range(0, 16):
            raise TypeError("Endpoint address must be an integer in [0..16), not '{!r}'"
                            .format(ep_addr))
        if ep_addr in self._output_map:
            raise ValueError("An output port for endpoint {} has already been requested"
                             .format(ep_addr))
        if not isinstance(max_size, int) or not max_size in range(0, 513):
            raise TypeError("Maximum packet size must be an integer in [0..512], not '{!r}'"
                            .format(max_size))
        if not isinstance(xfer_type, Transfer):
            raise TypeError("Transfer type must be a member of the Transfer enum, not '{!r}'"
                            .format(xfer_type))

        if xfer_type == Transfer.CONTROL:
            port = stream.Endpoint([("setup", 1), ("data", 8)])
        else:
            port = stream.Endpoint([("data", 8)])
        self._output_map[ep_addr] = port, max_size, xfer_type
        return port

    def elaborate(self, platform):
        m = Module()

        controller = m.submodules.controller = USBController(self.phy)
        i_arbiter  = m.submodules.i_arbiter  = USBInputArbiter(self._input_map)
        i_buffer   = m.submodules.i_buffer   = USBInputBuffer(self._input_map)
        o_arbiter  = m.submodules.o_arbiter  = USBOutputArbiter(self._output_map)
        o_buffer   = m.submodules.o_buffer   = USBOutputBuffer(self._output_map)

        m.d.comb += [
            controller.ep0_dev_addr.eq(self.ep0_dev_addr),

            # phy -> controller -> o_buffer -> o_arbiter -> endpoints
            controller.source_write.connect(o_buffer.sink_write),
            controller.source_data.connect(o_buffer.sink_data),
            controller.write_xfer.eq(o_buffer.write_xfer),
            o_buffer.recv_zlp.eq(controller.host_zlp),
            o_arbiter.sink_read.connect(o_buffer.source_read),
            o_buffer.source_data.connect(o_arbiter.sink_data),

            # endpoints -> i_arbiter -> i_buffer -> controller -> phy
            i_arbiter.source_write.connect(i_buffer.sink_write),
            i_arbiter.source_data.connect(i_buffer.sink_data),
            controller.sink_read.connect(i_buffer.source_read),
            i_buffer.source_data.connect(controller.sink_data),
            controller.read_xfer.eq(i_buffer.read_xfer),
            i_buffer.recv_ack.eq(controller.host_ack)
        ]

        return m
