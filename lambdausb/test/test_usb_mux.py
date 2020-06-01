#nmigen: UnusedElaboratable=no

import unittest

from nmigen import *
from nmigen.back.pysim import *

from ._util import *
from ..usb.mux import *
from ..usb.endpoint import *


class DoubleBufferTestCase(unittest.TestCase):
    def write(self, dut, data):
        yield dut.w_stb.eq(1)
        for i, byte in enumerate(data):
            self.assertTrue((yield dut.w_rdy))
            yield dut.w_lst.eq(i == len(data) - 1)
            yield dut.w_data.eq(byte)
            yield
        yield dut.w_stb.eq(0)
        yield

    def read(self, dut):
        data = []
        end = False
        yield dut.r_rdy.eq(1)
        while not end:
            yield
            self.assertTrue((yield dut.r_stb))
            data.append((yield dut.r_data))
            end = (yield dut.r_lst)
        yield dut.r_rdy.eq(0)
        yield
        return data

    def test_rw_simple(self):
        dut = DoubleBuffer(depth=64, width=8)

        def process():
            data = [0x80, 0x06, 0x00, 0x01, 0x00, 0x00, 0x40, 0x00]
            yield from self.write(dut, data)
            self.assertEqual((yield from self.read(dut)), data)

        simulation_test(dut, process)

    def test_r_ack(self):
        dut = DoubleBuffer(depth=64, width=8, read_ack=True)

        def process():
            data = [0x12, 0x01, 0x00, 0x00, 0x02, 0x00, 0x00, 0x40, 0xac,
                    0x05, 0x78, 0x56, 0x00, 0x01, 0x01, 0x02, 0x03, 0x01]
            yield from self.write(dut, data)
            self.assertEqual((yield from self.read(dut)), data)
            self.assertTrue((yield dut.r_stb))
            yield dut.r_rdy.eq(1)
            yield dut.r_ack.eq(1)
            yield
            yield dut.r_rdy.eq(0)
            yield
            self.assertFalse((yield dut.r_stb))

        simulation_test(dut, process)

    def test_w_bank_overflow(self):
        dut = DoubleBuffer(depth=1, width=8)

        def process():
            self.assertEqual((yield dut.w_rdy), 1)
            yield dut.w_stb.eq(1)
            yield dut.w_data.eq(0xaa)
            yield
            self.assertEqual((yield dut.w_rdy), 1)
            yield dut.w_stb.eq(1)
            yield dut.w_lst.eq(1)
            yield dut.w_data.eq(0xbb)
            yield
            yield; yield Delay()
            self.assertEqual((yield dut.r_stb), 0)

        simulation_test(dut, process)

    def test_w_full(self):
        dut = DoubleBuffer(depth=1, width=8)

        def process():
            self.assertEqual((yield dut.w_rdy), 1)
            self.assertEqual((yield dut.r_stb), 0)
            yield dut.w_stb.eq(1)
            yield dut.w_lst.eq(1)
            yield dut.w_data.eq(0xaa)
            yield
            yield; yield Delay()
            self.assertEqual((yield dut.w_rdy), 1)
            self.assertEqual((yield dut.r_stb), 1)
            yield dut.w_stb.eq(1)
            yield dut.w_lst.eq(1)
            yield dut.w_data.eq(0xbb)
            yield
            yield; yield Delay()
            self.assertEqual((yield dut.w_rdy), 0)
            self.assertEqual((yield dut.r_stb), 1)

        simulation_test(dut, process)

    def test_w_drop(self):
        dut = DoubleBuffer(depth=2, width=8)

        def process():
            self.assertEqual((yield dut.w_rdy), 1)
            yield dut.w_stb.eq(1)
            yield dut.w_data.eq(0xaa)
            yield
            self.assertEqual((yield dut.w_rdy), 1)
            yield dut.w_stb.eq(1)
            yield dut.w_lst.eq(1)
            yield dut.w_drop.eq(1)
            yield dut.w_data.eq(0xbb)
            yield
            yield; yield Delay()
            self.assertEqual((yield dut.r_stb), 0)

        simulation_test(dut, process)

    def test_rw_interleaved(self):
        dut = DoubleBuffer(depth=4, width=8)

        def process():
            data_0 = [0xa0, 0xb0, 0xc0, 0xd0]
            data_1 = [0xa1, 0xb1, 0xc1, 0xd1]
            data_2 = [0xa2, 0xb2, 0xc2, 0xd2]
            yield from self.write(dut, data_0)
            yield
            yield from self.write(dut, data_1)
            self.assertEqual((yield from self.read(dut)), data_0)
            yield
            yield from self.write(dut, data_2)
            self.assertEqual((yield from self.read(dut)), data_1)
            self.assertEqual((yield from self.read(dut)), data_2)

        simulation_test(dut, process)


class InputMultiplexerTestCase(unittest.TestCase):
    def test_add_endpoint_wrong(self):
        dut = InputMultiplexer()
        with self.assertRaisesRegex(TypeError,
                r"Endpoint must be an InputEndpoint, not 'foo'"):
            dut.add_endpoint("foo", addr=0)

    def test_add_endpoint_addr_wrong(self):
        dut = InputMultiplexer()
        ep  = InputEndpoint(xfer=Transfer.CONTROL, max_size=64)
        with self.assertRaisesRegex(TypeError,
                r"Endpoint address must be an integer, not 'foo'"):
            dut.add_endpoint(ep, addr="foo")

    def test_add_endpoint_addr_range(self):
        dut = InputMultiplexer()
        ep  = InputEndpoint(xfer=Transfer.CONTROL, max_size=64)
        with self.assertRaisesRegex(ValueError,
                r"Endpoint address must be between 0 and 15, not 16"):
            dut.add_endpoint(ep, addr=16)

    def test_add_endpoint_addr_twice(self):
        dut = InputMultiplexer()
        ep0 = InputEndpoint(xfer=Transfer.CONTROL, max_size=64)
        ep1 = InputEndpoint(xfer=Transfer.CONTROL, max_size=64)
        dut.add_endpoint(ep0, addr=0)
        with self.assertRaisesRegex(ValueError,
                r"Endpoint address 0 has already been assigned"):
            dut.add_endpoint(ep1, addr=0)

    def test_add_endpoint_twice(self):
        dut = InputMultiplexer()
        ep  = InputEndpoint(xfer=Transfer.CONTROL, max_size=64)
        dut.add_endpoint(ep, addr=0)
        with self.assertRaisesRegex(ValueError,
                r"Endpoint \(rec ep stb lst data zlp rdy ack sof\) has already been added at "
                r"address 0"):
            dut.add_endpoint(ep, addr=1)

    def test_add_endpoint_0(self):
        dut = InputMultiplexer()
        ep  = InputEndpoint(xfer=Transfer.BULK, max_size=64)
        with self.assertRaisesRegex(ValueError,
                r"Invalid transfer type BULK for endpoint 0; must be CONTROL"):
            dut.add_endpoint(ep, addr=0)

    def test_simple(self):
        dut = InputMultiplexer()
        ep0 = InputEndpoint(xfer=Transfer.CONTROL, max_size=64)
        ep1 = InputEndpoint(xfer=Transfer.BULK,    max_size=512)
        dut.add_endpoint(ep0, addr=0)
        dut.add_endpoint(ep1, addr=1)

        def process():
            self.assertEqual((yield dut.cmd.rdy), 0)
            self.assertEqual((yield dut.pkt.stb), 0)
            self.assertEqual((yield ep0.rdy), 0)
            self.assertEqual((yield ep1.rdy), 0)

            yield ep0.stb.eq(1)
            yield ep0.lst.eq(1)
            yield ep0.zlp.eq(1)
            yield ep0.data.eq(0xff)
            yield ep1.stb.eq(1)
            yield ep1.lst.eq(0)
            yield ep1.zlp.eq(0)
            yield ep1.data.eq(0xab)

            # Endpoint 0

            yield dut.cmd.stb.eq(1)
            yield dut.cmd.addr.eq(0)
            yield Delay()
            self.assertEqual((yield dut.cmd.rdy), 1)
            self.assertEqual((yield dut.cmd.xfer), Transfer.CONTROL)
            yield

            yield dut.cmd.stb.eq(0)
            yield

            self.assertEqual((yield dut.pkt.stb), 1)
            self.assertEqual((yield dut.pkt.lst), 1)
            self.assertEqual((yield dut.pkt.zlp), 1)
            self.assertEqual((yield dut.pkt.data), 0xff)
            yield dut.pkt.rdy.eq(1)
            yield dut.pkt.ack.eq(1)
            yield Delay()
            self.assertEqual((yield ep0.rdy), 1)
            self.assertEqual((yield ep0.ack), 1)
            yield

            yield dut.pkt.rdy.eq(0)
            yield dut.pkt.ack.eq(0)

            # Endpoint 1

            yield dut.cmd.stb.eq(1)
            yield dut.cmd.addr.eq(1)
            yield Delay()
            self.assertEqual((yield dut.cmd.rdy), 1)
            self.assertEqual((yield dut.cmd.xfer), Transfer.BULK)
            yield

            yield dut.cmd.stb.eq(0)
            yield

            self.assertEqual((yield dut.pkt.stb), 1)
            self.assertEqual((yield dut.pkt.lst), 0)
            self.assertEqual((yield dut.pkt.zlp), 0)
            self.assertEqual((yield dut.pkt.data), 0xab)
            yield dut.pkt.rdy.eq(1)
            yield dut.pkt.ack.eq(1)
            yield Delay()
            self.assertEqual((yield ep1.rdy), 1)
            self.assertEqual((yield ep1.ack), 1)
            yield

            yield dut.pkt.rdy.eq(0)
            yield dut.pkt.ack.eq(0)

            # Unknown endpoint

            yield dut.cmd.stb.eq(1)
            yield dut.cmd.addr.eq(2)
            yield Delay()
            self.assertEqual((yield dut.cmd.rdy), 0)

        simulation_test(dut, process)

    def test_buffered(self):
        dut = InputMultiplexer()
        ep  = InputEndpoint(xfer=Transfer.CONTROL, max_size=2)
        dut.add_endpoint(ep, addr=0, buffered=True)

        def process():
            self.assertEqual((yield dut.cmd.rdy), 0)
            self.assertEqual((yield dut.pkt.stb), 0)

            # Write first packet

            self.assertEqual((yield ep.rdy), 1)
            yield ep.stb.eq(1)
            yield ep.lst.eq(1)
            yield ep.zlp.eq(1)
            yield; yield Delay()

            self.assertEqual((yield ep.rdy), 0)
            yield; yield Delay()

            # Write second packet

            self.assertEqual((yield ep.rdy), 1)
            yield ep.lst.eq(0)
            yield ep.zlp.eq(0)
            yield ep.data.eq(0xaa)
            yield; yield Delay()
            self.assertEqual((yield ep.rdy), 1)
            yield ep.lst.eq(1)
            yield ep.data.eq(0xbb)
            yield; yield Delay()

            self.assertEqual((yield ep.rdy), 0)
            yield ep.stb.eq(0)
            yield

            # Read first packet

            yield dut.cmd.stb.eq(1)
            yield dut.cmd.addr.eq(0)
            yield Delay()
            self.assertEqual((yield dut.cmd.rdy), 1)
            yield

            yield dut.cmd.stb.eq(0)
            yield

            self.assertEqual((yield dut.pkt.stb), 1)
            self.assertEqual((yield dut.pkt.lst), 1)
            self.assertEqual((yield dut.pkt.zlp), 1)
            yield dut.pkt.rdy.eq(1)
            yield dut.pkt.ack.eq(1)
            yield
            yield dut.pkt.ack.eq(0)
            yield
            yield

            # Read second packet, without ack

            self.assertEqual((yield dut.pkt.stb), 1)
            self.assertEqual((yield dut.pkt.lst), 0)
            self.assertEqual((yield dut.pkt.zlp), 0)
            self.assertEqual((yield dut.pkt.data), 0xaa)
            yield
            self.assertEqual((yield dut.pkt.stb), 1)
            self.assertEqual((yield dut.pkt.lst), 1)
            self.assertEqual((yield dut.pkt.zlp), 0)
            self.assertEqual((yield dut.pkt.data), 0xbb)
            yield

            # Read second packet, with ack

            self.assertEqual((yield dut.pkt.stb), 1)
            self.assertEqual((yield dut.pkt.lst), 0)
            self.assertEqual((yield dut.pkt.zlp), 0)
            self.assertEqual((yield dut.pkt.data), 0xaa)
            yield
            self.assertEqual((yield dut.pkt.stb), 1)
            self.assertEqual((yield dut.pkt.lst), 1)
            self.assertEqual((yield dut.pkt.zlp), 0)
            self.assertEqual((yield dut.pkt.data), 0xbb)
            yield dut.pkt.ack.eq(1)
            yield
            yield

            self.assertEqual((yield dut.pkt.stb), 0)

        simulation_test(dut, process)

    def test_buffered_isochronous(self):
        dut = InputMultiplexer()
        ep  = InputEndpoint(xfer=Transfer.ISOCHRONOUS, max_size=2)
        dut.add_endpoint(ep, addr=1, buffered=True)

        def process():
            self.assertEqual((yield dut.cmd.rdy), 0)
            self.assertEqual((yield dut.pkt.stb), 0)

            # Write packet

            self.assertEqual((yield ep.rdy), 1)
            yield ep.stb.eq(1)
            yield ep.data.eq(0xaa)
            yield; yield Delay()
            self.assertEqual((yield ep.rdy), 1)
            yield ep.lst.eq(1)
            yield ep.data.eq(0xbb)
            yield; yield Delay()

            yield ep.stb.eq(0)
            yield

            # Read packet

            yield dut.cmd.stb.eq(1)
            yield dut.cmd.addr.eq(1)
            yield Delay()
            self.assertEqual((yield dut.cmd.rdy), 1)
            yield

            yield dut.cmd.stb.eq(0)
            yield dut.pkt.rdy.eq(1)
            yield

            self.assertEqual((yield dut.pkt.stb), 1)
            self.assertEqual((yield dut.pkt.lst), 0)
            self.assertEqual((yield dut.pkt.data), 0xaa)
            yield
            self.assertEqual((yield dut.pkt.stb), 1)
            self.assertEqual((yield dut.pkt.lst), 1)
            self.assertEqual((yield dut.pkt.data), 0xbb)
            yield
            yield

            self.assertEqual((yield dut.pkt.stb), 0)

        simulation_test(dut, process)

    def test_sof_broadcast(self):
        dut = InputMultiplexer()
        ep0 = InputEndpoint(xfer=Transfer.CONTROL,     max_size=1)
        ep1 = InputEndpoint(xfer=Transfer.ISOCHRONOUS, max_size=1)
        dut.add_endpoint(ep0, addr=0)
        dut.add_endpoint(ep1, addr=1)

        def process():
            self.assertEqual((yield ep0.sof), 0)
            self.assertEqual((yield ep1.sof), 0)
            yield dut.sof.eq(1)
            yield Delay()
            self.assertEqual((yield ep0.sof), 1)
            self.assertEqual((yield ep1.sof), 1)

        simulation_test(dut, process)


class OutputMultiplexerTestCase(unittest.TestCase):
    def test_add_endpoint_wrong(self):
        dut = OutputMultiplexer()
        with self.assertRaisesRegex(TypeError,
                r"Endpoint must be an OutputEndpoint, not 'foo'"):
            dut.add_endpoint("foo", addr=0)

    def test_add_endpoint_addr_wrong(self):
        dut = OutputMultiplexer()
        ep  = OutputEndpoint(xfer=Transfer.CONTROL, max_size=64)
        with self.assertRaisesRegex(TypeError,
                r"Endpoint address must be an integer, not 'foo'"):
            dut.add_endpoint(ep, addr="foo")

    def test_add_endpoint_addr_range(self):
        dut = OutputMultiplexer()
        ep  = OutputEndpoint(xfer=Transfer.CONTROL, max_size=64)
        with self.assertRaisesRegex(ValueError,
                r"Endpoint address must be between 0 and 15, not 16"):
            dut.add_endpoint(ep, addr=16)

    def test_add_endpoint_addr_twice(self):
        dut = OutputMultiplexer()
        ep0 = OutputEndpoint(xfer=Transfer.CONTROL, max_size=64)
        ep1 = OutputEndpoint(xfer=Transfer.CONTROL, max_size=64)
        dut.add_endpoint(ep0, addr=0)
        with self.assertRaisesRegex(ValueError,
                r"Endpoint address 0 has already been assigned"):
            dut.add_endpoint(ep1, addr=0)

    def test_add_endpoint_twice(self):
        dut = OutputMultiplexer()
        ep  = OutputEndpoint(xfer=Transfer.CONTROL, max_size=64)
        dut.add_endpoint(ep, addr=0)
        with self.assertRaisesRegex(ValueError,
                r"Endpoint \(rec ep stb lst data setup drop rdy sof\) has already been added at "
                r"address 0"):
            dut.add_endpoint(ep, addr=1)

    def test_add_endpoint_0(self):
        dut = OutputMultiplexer()
        ep  = OutputEndpoint(xfer=Transfer.BULK, max_size=64)
        with self.assertRaisesRegex(ValueError,
                r"Invalid transfer type BULK for endpoint 0; must be CONTROL"):
            dut.add_endpoint(ep, addr=0)

    def test_simple(self):
        dut = OutputMultiplexer()
        ep0 = OutputEndpoint(xfer=Transfer.CONTROL, max_size=64)
        ep1 = OutputEndpoint(xfer=Transfer.BULK,    max_size=512)
        dut.add_endpoint(ep0, addr=0)
        dut.add_endpoint(ep1, addr=1)

        def process():
            self.assertEqual((yield ep0.stb), 0)
            self.assertEqual((yield ep1.stb), 0)

            yield dut.pkt.stb.eq(1)
            yield dut.pkt.lst.eq(1)
            yield dut.pkt.setup.eq(1)
            yield dut.pkt.data.eq(0xff)
            yield dut.pkt.drop.eq(1)
            yield ep0.rdy.eq(1)
            yield ep1.rdy.eq(1)

            # Endpoint 0

            yield dut.cmd.stb.eq(1)
            yield dut.cmd.addr.eq(0)
            yield Delay()
            self.assertEqual((yield dut.cmd.rdy), 1)
            self.assertEqual((yield dut.cmd.xfer), Transfer.CONTROL)
            yield

            yield dut.cmd.stb.eq(0)
            yield

            self.assertEqual((yield ep0.stb), 1)
            self.assertEqual((yield ep0.lst), 1)
            self.assertEqual((yield ep0.setup), 1)
            self.assertEqual((yield ep0.data), 0xff)
            self.assertEqual((yield ep0.drop), 1)
            self.assertEqual((yield ep1.stb), 0)
            self.assertEqual((yield dut.pkt.rdy), 1)

            # Endpoint 1

            yield dut.cmd.stb.eq(1)
            yield dut.cmd.addr.eq(1)
            yield Delay()
            self.assertEqual((yield dut.cmd.rdy), 1)
            self.assertEqual((yield dut.cmd.xfer), Transfer.BULK)
            yield

            yield dut.cmd.stb.eq(0)
            yield

            self.assertEqual((yield ep1.stb), 1)
            self.assertEqual((yield ep1.lst), 1)
            self.assertEqual((yield ep1.setup), 0)
            self.assertEqual((yield ep1.data), 0xff)
            self.assertEqual((yield ep1.drop), 1)
            self.assertEqual((yield ep0.stb), 0)
            self.assertEqual((yield dut.pkt.rdy), 1)

            # Unknown endpoint

            yield dut.cmd.stb.eq(1)
            yield dut.cmd.addr.eq(2)
            yield Delay()
            self.assertEqual((yield dut.cmd.rdy), 0)
            yield

        simulation_test(dut, process)

    def test_buffered(self):
        dut = OutputMultiplexer()
        ep  = OutputEndpoint(xfer=Transfer.CONTROL, max_size=2)
        dut.add_endpoint(ep, addr=0, buffered=True)

        def process():
            yield dut.cmd.stb.eq(1)
            yield dut.cmd.addr.eq(0)
            yield Delay()
            self.assertEqual((yield dut.cmd.rdy), 1)
            yield

            yield dut.cmd.stb.eq(0)
            yield

            # Write first packet

            self.assertEqual((yield dut.pkt.rdy), 1)
            yield dut.pkt.stb.eq(1)
            yield dut.pkt.lst.eq(1)
            yield dut.pkt.setup.eq(1)
            yield dut.pkt.data.eq(0xff)
            yield; yield Delay()

            self.assertEqual((yield dut.pkt.rdy), 0)
            yield; yield Delay()

            # Write second packet

            self.assertEqual((yield dut.pkt.rdy), 1)
            yield dut.pkt.lst.eq(0)
            yield dut.pkt.setup.eq(0)
            yield dut.pkt.data.eq(0xaa)
            yield; yield Delay()
            self.assertEqual((yield dut.pkt.rdy), 1)
            yield dut.pkt.lst.eq(1)
            yield dut.pkt.data.eq(0xbb)
            yield; yield Delay()

            self.assertEqual((yield dut.pkt.rdy), 0)
            yield dut.pkt.stb.eq(0)
            yield

            # Read first packet

            self.assertEqual((yield ep.stb), 1)
            self.assertEqual((yield ep.lst), 1)
            self.assertEqual((yield ep.setup), 1)
            self.assertEqual((yield ep.data), 0xff)
            yield ep.rdy.eq(1)
            yield
            yield
            yield

            # Read second packet

            self.assertEqual((yield ep.stb), 1)
            self.assertEqual((yield ep.lst), 0)
            self.assertEqual((yield ep.setup), 0)
            self.assertEqual((yield ep.data), 0xaa)
            yield
            self.assertEqual((yield ep.stb), 1)
            self.assertEqual((yield ep.lst), 1)
            self.assertEqual((yield ep.setup), 0)
            self.assertEqual((yield ep.data), 0xbb)
            yield
            self.assertEqual((yield ep.stb), 0)

        simulation_test(dut, process)
