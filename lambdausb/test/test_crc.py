from nmigen import *
from nmigen.back.pysim import *
from nmigen.test.tools import *

from ..crc import *


class CRCTestCase(FHDLTestCase):
    def test_basic(self):
        dut = CRC(poly=0b11000000000000101, size=16, dw=8, init=0xffff)
        with Simulator(dut) as sim:
            def process():
                yield dut.clr.eq(1)
                yield Tick()

                yield dut.clr.eq(0)
                yield dut.en.eq(1)
                yield dut.val.eq(0x80)
                yield Tick()

                yield dut.val.eq(0x06)
                yield Tick()

                yield dut.val.eq(0x00)
                yield Tick()

                yield dut.val.eq(0x01)
                yield Tick()

                yield dut.val.eq(0x00)
                yield Tick()

                yield dut.val.eq(0x00)
                yield Tick()

                yield dut.val.eq(0x12)
                yield Tick()

                yield dut.val.eq(0x00)
                yield Tick()

                self.assertEqual((yield dut.crc), 0xf4e0)

            sim.add_clock(1e-6)
            sim.add_sync_process(process)
            sim.run()
