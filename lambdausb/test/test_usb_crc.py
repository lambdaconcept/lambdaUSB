import unittest

from nmigen import *
from nmigen.back.pysim import *

from ..usb.crc import *
from ._util import *


class CRCTestCase(unittest.TestCase):
    def test_basic(self):
        dut = CRC(poly=0b11000000000000101, size=16, dw=8, init=0xffff)

        def process():
            yield dut.clr.eq(1)
            yield

            yield dut.clr.eq(0)
            yield dut.en.eq(1)
            yield dut.val.eq(0x80)
            yield

            yield dut.val.eq(0x06)
            yield

            yield dut.val.eq(0x00)
            yield

            yield dut.val.eq(0x01)
            yield

            yield dut.val.eq(0x00)
            yield

            yield dut.val.eq(0x00)
            yield

            yield dut.val.eq(0x12)
            yield

            yield dut.val.eq(0x00)
            yield

            self.assertEqual((yield dut.crc), 0xf4e0)

        simulation_test(dut, process)
