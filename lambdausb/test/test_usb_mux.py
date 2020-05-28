import unittest

from nmigen import *
from nmigen.back.pysim import *

from ..usb.mux import *
from ._util import *


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

    def test_simple(self):
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
