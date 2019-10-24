from nmigen import *
from nmigen.back.pysim import *
from nmigen.test.tools import *

from ..buf import *
from ..protocol import Transfer


class USBInputBufferTestCase(FHDLTestCase):
    def test_basic(self):
        dut = USBInputBuffer({0x0: (None, 512, Transfer.BULK)})
        with Simulator(dut) as sim:
            def write_process():
                yield dut.sink_write.valid.eq(1)
                yield dut.sink_write.ep.eq(0x0)
                yield dut.sink_data.valid.eq(1)
                yield dut.sink_data.data.eq(0x5a)

                yield Delay(1e-7)
                self.assertEqual((yield dut.sink_write.ready), 1)

                for _ in range(3):
                    self.assertEqual((yield dut.sink_data.ready), 0)
                    yield Tick()

                self.assertEqual((yield dut.sink_data.ready), 1)
                yield dut.sink_data.last.eq(1)
                yield dut.sink_data.data.eq(0xa5)

                yield Tick()
                self.assertEqual((yield dut.sink_data.ready), 1)
                yield dut.sink_write.valid.eq(0)
                yield dut.sink_data.valid.eq(0)

                yield Delay(1e-7)
                self.assertEqual((yield dut.sink_data.ready), 0)

            def read_process():
                yield dut.source_read.valid.eq(1)
                yield dut.source_read.ep.eq(0x0)
                yield Delay(1e-7)

                for _ in range(5): # wait for write_process()
                    self.assertEqual((yield dut.source_read.ready), 0)
                    yield Tick()

                self.assertEqual((yield dut.source_read.ready), 1)
                yield dut.source_data.ready.eq(1)

                for _ in range(2):
                    self.assertEqual((yield dut.source_data.valid), 0)
                    yield Tick()

                self.assertEqual((yield dut.source_data.valid), 1)
                self.assertEqual((yield dut.source_data.data), 0x5a)
                self.assertEqual((yield dut.source_data.last), 0)

                yield Tick()

                self.assertEqual((yield dut.source_data.valid), 1)
                self.assertEqual((yield dut.source_data.data), 0xa5)
                self.assertEqual((yield dut.source_data.last), 1)
                yield dut.source_read.valid.eq(0)
                yield dut.source_data.ready.eq(0)

                yield Tick()
                self.assertEqual((yield dut.source_data.valid), 0)

            sim.add_clock(1e-6)
            sim.add_sync_process(write_process)
            sim.add_sync_process(read_process)
            sim.run()

    def test_zero_length(self):
        dut = USBInputBuffer({0x0: (None, 512, Transfer.BULK)})
        with Simulator(dut) as sim:
            def write_process():
                yield dut.sink_write.valid.eq(1)
                yield dut.sink_write.ep.eq(0x0)
                yield dut.sink_data.valid.eq(1)
                yield dut.sink_data.empty.eq(1)
                yield dut.sink_data.last.eq(1)

                yield Delay(1e-7)
                self.assertEqual((yield dut.sink_write.ready), 1)

                for _ in range(3):
                    self.assertEqual((yield dut.sink_data.ready), 0)
                    yield Tick()

                self.assertEqual((yield dut.sink_data.ready), 1)
                yield dut.sink_write.valid.eq(0)
                yield dut.sink_data.valid.eq(0)

                yield Delay(1e-7)
                self.assertEqual((yield dut.sink_data.ready), 0)

            def read_process():
                yield dut.source_read.valid.eq(1)
                yield dut.source_read.ep.eq(0x0)
                yield Delay(1e-7)

                for _ in range(4): # wait for write_process()
                    self.assertEqual((yield dut.source_read.ready), 0)
                    yield Tick()

                self.assertEqual((yield dut.source_read.ready), 1)
                yield dut.source_data.ready.eq(1)

                for _ in range(2):
                    self.assertEqual((yield dut.source_data.valid), 0)
                    yield Tick()

                self.assertEqual((yield dut.source_data.valid), 1)
                self.assertEqual((yield dut.source_data.empty), 1)
                self.assertEqual((yield dut.source_data.last), 1)
                yield dut.source_read.valid.eq(0)
                yield dut.source_data.ready.eq(0)

                yield Tick()
                self.assertEqual((yield dut.source_data.valid), 0)

            sim.add_clock(1e-6)
            sim.add_sync_process(write_process)
            sim.add_sync_process(read_process)
            sim.run()

    def test_consecutive(self):
        dut = USBInputBuffer({0x0: (None, 512, Transfer.BULK)})
        with Simulator(dut) as sim:
            def write_process():
                yield dut.sink_write.valid.eq(1)
                yield dut.sink_write.ep.eq(0x0)
                yield dut.sink_data.valid.eq(1)
                yield dut.sink_data.data.eq(0x5a)
                yield dut.sink_data.last.eq(1)

                yield Delay(1e-7)
                self.assertEqual((yield dut.sink_write.ready), 1)

                for _ in range(3):
                    self.assertEqual((yield dut.sink_data.ready), 0)
                    yield Tick()

                self.assertEqual((yield dut.sink_data.ready), 1)
                yield dut.sink_data.data.eq(0xa5)

                yield Tick()
                self.assertEqual((yield dut.sink_write.ready), 1)

                for _ in range(2):
                    self.assertEqual((yield dut.sink_data.ready), 0)
                    yield Tick()

                self.assertEqual((yield dut.sink_data.ready), 1)
                yield dut.sink_write.valid.eq(0)
                yield dut.sink_data.valid.eq(0)

            def read_process():
                yield dut.source_read.valid.eq(1)
                yield dut.source_read.ep.eq(0x0)
                yield Delay(1e-7)

                for _ in range(4): # wait for write_process()
                    self.assertEqual((yield dut.source_read.ready), 0)
                    yield Tick()

                self.assertEqual((yield dut.source_read.ready), 1)
                yield dut.source_data.ready.eq(1)

                for _ in range(2):
                    self.assertEqual((yield dut.source_data.valid), 0)
                    yield Tick()

                self.assertEqual((yield dut.source_data.valid), 1)
                self.assertEqual((yield dut.source_data.data), 0x5a)
                self.assertEqual((yield dut.source_data.last), 1)
                yield dut.recv_ack.eq(1)

                yield Tick()
                yield dut.recv_ack.eq(0)

                for _ in range(2):
                    self.assertEqual((yield dut.source_data.valid), 0)
                    yield Tick()

                self.assertEqual((yield dut.source_data.valid), 1)
                self.assertEqual((yield dut.source_data.data), 0xa5)
                self.assertEqual((yield dut.source_data.last), 1)
                yield dut.source_read.valid.eq(0)
                yield dut.source_data.ready.eq(0)

                yield Tick()
                self.assertEqual((yield dut.source_data.valid), 0)

            sim.add_clock(1e-6)
            sim.add_sync_process(write_process)
            sim.add_sync_process(read_process)
            sim.run()

    def test_concurrent(self):
        dut = USBInputBuffer({
            0x0: (None, 512, Transfer.BULK),
            0x1: (None, 512, Transfer.BULK)
        })
        with Simulator(dut) as sim:
            def write_process():
                yield dut.sink_write.valid.eq(1)
                yield dut.sink_write.ep.eq(0x0)
                yield dut.sink_data.valid.eq(1)
                yield dut.sink_data.data.eq(0x0a)

                yield Delay(1e-7)
                self.assertEqual((yield dut.sink_write.ready), 1)

                for _ in range(3):
                    self.assertEqual((yield dut.sink_data.ready), 0)
                    yield Tick()

                self.assertEqual((yield dut.sink_data.ready), 1)
                yield dut.sink_write.ep.eq(0x1)
                yield dut.sink_data.data.eq(0x1a)

                yield Delay(1e-7)
                for _ in range(4):
                    self.assertEqual((yield dut.sink_data.ready), 0)
                    yield Tick()

                self.assertEqual((yield dut.sink_data.ready), 1)
                yield dut.sink_write.ep.eq(0x0)
                yield dut.sink_data.data.eq(0xa0)
                yield dut.sink_data.last.eq(1)

                yield Delay(1e-7)
                for _ in range(4):
                    self.assertEqual((yield dut.sink_data.ready), 0)
                    yield Tick()

                self.assertEqual((yield dut.sink_data.ready), 1)
                yield dut.sink_write.ep.eq(0x1)
                yield dut.sink_data.data.eq(0xa1)
                yield dut.sink_data.last.eq(1)

                yield Delay(1e-7)
                for _ in range(3):
                    self.assertEqual((yield dut.sink_data.ready), 0)
                    yield Tick()

                self.assertEqual((yield dut.sink_data.ready), 1)
                yield dut.sink_write.valid.eq(0)
                yield dut.sink_data.valid.eq(0)

            def read_process():
                yield dut.source_read.valid.eq(1)
                yield dut.source_read.ep.eq(0x0)
                yield Delay(1e-7)

                for _ in range(12): # wait for write_process()
                    self.assertEqual((yield dut.source_read.ready), 0)
                    yield Tick()

                self.assertEqual((yield dut.source_read.ready), 1)
                yield dut.source_data.ready.eq(1)

                for _ in range(2):
                    self.assertEqual((yield dut.source_data.valid), 0)
                    yield Tick()

                self.assertEqual((yield dut.source_data.valid), 1)
                self.assertEqual((yield dut.source_data.data), 0x0a)
                self.assertEqual((yield dut.source_data.last), 0)

                yield Tick()

                self.assertEqual((yield dut.source_data.valid), 1)
                self.assertEqual((yield dut.source_data.data), 0xa0)
                self.assertEqual((yield dut.source_data.last), 1)

                yield dut.source_read.ep.eq(0x1)

                yield Delay(1e-7)
                self.assertEqual((yield dut.source_read.ready), 1)

                for _ in range(3):
                    self.assertEqual((yield dut.source_data.valid), 0)
                    yield Tick()

                self.assertEqual((yield dut.source_data.valid), 1)
                self.assertEqual((yield dut.source_data.data), 0x1a)
                self.assertEqual((yield dut.source_data.last), 0)

                yield Tick()

                self.assertEqual((yield dut.source_data.valid), 1)
                self.assertEqual((yield dut.source_data.data), 0xa1)
                self.assertEqual((yield dut.source_data.last), 1)

            sim.add_clock(1e-6)
            sim.add_sync_process(write_process)
            sim.add_sync_process(read_process)
            sim.run()


class USBOutputBufferTestCase(FHDLTestCase):
    def test_basic(self):
        dut = USBOutputBuffer({0x0: (None, 512, Transfer.BULK)})
        with Simulator(dut) as sim:
            def write_process():
                yield dut.sink_write.valid.eq(1)
                yield dut.sink_write.ep.eq(0x0)
                yield dut.sink_data.valid.eq(1)
                yield dut.sink_data.data.eq(0x5a)

                yield Delay(1e-7)
                self.assertEqual((yield dut.sink_write.ready), 1)

                for _ in range(3):
                    self.assertEqual((yield dut.sink_data.ready), 0)
                    yield Tick()

                self.assertEqual((yield dut.sink_data.ready), 1)
                yield dut.sink_data.crc_ok.eq(1)
                yield dut.sink_data.last.eq(1)
                yield dut.sink_data.data.eq(0xa5)

                yield Tick()
                self.assertEqual((yield dut.sink_data.ready), 1)
                yield dut.sink_write.valid.eq(0)
                yield dut.sink_data.valid.eq(0)

                yield Delay(1e-7)
                self.assertEqual((yield dut.sink_data.ready), 0)

            def read_process():
                yield dut.source_read.valid.eq(1)
                yield dut.source_read.ep.eq(0x0)
                yield Delay(1e-7)

                for _ in range(5): # wait for write_process()
                    self.assertEqual((yield dut.source_read.ready), 0)
                    yield Tick()

                self.assertEqual((yield dut.source_read.ready), 1)
                yield dut.source_data.ready.eq(1)

                for _ in range(2):
                    self.assertEqual((yield dut.source_data.valid), 0)
                    yield Tick()

                self.assertEqual((yield dut.source_data.valid), 1)
                self.assertEqual((yield dut.source_data.data), 0x5a)
                self.assertEqual((yield dut.source_data.last), 0)

                yield Tick()

                self.assertEqual((yield dut.source_data.valid), 1)
                self.assertEqual((yield dut.source_data.data), 0xa5)
                self.assertEqual((yield dut.source_data.last), 1)
                yield dut.source_read.valid.eq(0)
                yield dut.source_data.ready.eq(0)

                yield Tick()
                self.assertEqual((yield dut.source_data.valid), 0)

            sim.add_clock(1e-6)
            sim.add_sync_process(write_process)
            sim.add_sync_process(read_process)
            sim.run()

    def test_setup(self):
        dut = USBOutputBuffer({0x0: (None, 512, Transfer.BULK)})
        with Simulator(dut) as sim:
            def write_process():
                yield dut.sink_write.valid.eq(1)
                yield dut.sink_write.ep.eq(0x0)
                yield dut.sink_data.valid.eq(1)
                yield dut.sink_data.setup.eq(1)
                yield dut.sink_data.crc_ok.eq(1)
                yield dut.sink_data.last.eq(1)

                yield Delay(1e-7)
                self.assertEqual((yield dut.sink_write.ready), 1)

                for _ in range(3):
                    self.assertEqual((yield dut.sink_data.ready), 0)
                    yield Tick()

                self.assertEqual((yield dut.sink_data.ready), 1)
                yield dut.sink_write.valid.eq(0)
                yield dut.sink_data.valid.eq(0)

                yield Delay(1e-7)
                self.assertEqual((yield dut.sink_data.ready), 0)

            def read_process():
                yield dut.source_read.valid.eq(1)
                yield dut.source_read.ep.eq(0x0)
                yield Delay(1e-7)

                for _ in range(4): # wait for write_process()
                    self.assertEqual((yield dut.source_read.ready), 0)
                    yield Tick()

                self.assertEqual((yield dut.source_read.ready), 1)
                yield dut.source_data.ready.eq(1)

                for _ in range(2):
                    self.assertEqual((yield dut.source_data.valid), 0)
                    yield Tick()

                self.assertEqual((yield dut.source_data.valid), 1)
                self.assertEqual((yield dut.source_data.setup), 1)
                self.assertEqual((yield dut.source_data.last), 1)
                yield dut.source_read.valid.eq(0)
                yield dut.source_data.ready.eq(0)

                yield Tick()
                self.assertEqual((yield dut.source_data.valid), 0)

            sim.add_clock(1e-6)
            sim.add_sync_process(write_process)
            sim.add_sync_process(read_process)
            sim.run()

    def test_consecutive(self):
        dut = USBOutputBuffer({0x0: (None, 512, Transfer.BULK)})
        with Simulator(dut) as sim:
            def write_process():
                yield dut.sink_write.valid.eq(1)
                yield dut.sink_write.ep.eq(0x0)
                yield dut.sink_data.valid.eq(1)
                yield dut.sink_data.data.eq(0x5a)
                yield dut.sink_data.crc_ok.eq(1)
                yield dut.sink_data.last.eq(1)

                yield Delay(1e-7)
                self.assertEqual((yield dut.sink_write.ready), 1)

                for _ in range(3):
                    self.assertEqual((yield dut.sink_data.ready), 0)
                    yield Tick()

                self.assertEqual((yield dut.sink_data.ready), 1)
                yield dut.sink_data.data.eq(0xa5)

                yield Tick()
                self.assertEqual((yield dut.sink_write.ready), 1)

                for _ in range(3):
                    self.assertEqual((yield dut.sink_data.ready), 0)
                    yield Tick()

                self.assertEqual((yield dut.sink_data.ready), 1)
                yield dut.sink_write.valid.eq(0)
                yield dut.sink_data.valid.eq(0)

            def read_process():
                yield dut.source_read.valid.eq(1)
                yield dut.source_read.ep.eq(0x0)
                yield Delay(1e-7)

                for _ in range(4): # wait for write_process()
                    self.assertEqual((yield dut.source_read.ready), 0)
                    yield Tick()

                self.assertEqual((yield dut.source_read.ready), 1)
                yield dut.source_data.ready.eq(1)

                for _ in range(2):
                    self.assertEqual((yield dut.source_data.valid), 0)
                    yield Tick()

                self.assertEqual((yield dut.source_data.valid), 1)
                self.assertEqual((yield dut.source_data.data), 0x5a)
                self.assertEqual((yield dut.source_data.last), 1)

                yield Tick()

                for _ in range(3):
                    self.assertEqual((yield dut.source_data.valid), 0)
                    yield Tick()

                self.assertEqual((yield dut.source_data.valid), 1)
                self.assertEqual((yield dut.source_data.data), 0xa5)
                self.assertEqual((yield dut.source_data.last), 1)
                yield dut.source_read.valid.eq(0)
                yield dut.source_data.ready.eq(0)

                yield Tick()
                self.assertEqual((yield dut.source_data.valid), 0)

            sim.add_clock(1e-6)
            sim.add_sync_process(write_process)
            sim.add_sync_process(read_process)
            sim.run()

    def test_max_size(self):
        dut = USBOutputBuffer({0x0: (None, 32, Transfer.BULK)})
        with Simulator(dut) as sim:
            def write_process():
                yield dut.sink_write.valid.eq(1)
                yield dut.sink_write.ep.eq(0x0)

                yield Delay(1e-7)
                self.assertEqual((yield dut.sink_write.ready), 1)

                for _ in range(3):
                    self.assertEqual((yield dut.sink_data.ready), 0)
                    yield Tick()

                for i in range(32):
                    self.assertEqual((yield dut.sink_data.ready), 1)
                    yield dut.sink_data.valid.eq(1)
                    yield dut.sink_data.data.eq(i)
                    yield dut.sink_data.crc_ok.eq(i == 31)
                    yield dut.sink_data.last.eq(i == 31)
                    yield Tick()

                yield dut.sink_write.valid.eq(0)
                yield dut.sink_data.valid.eq(0)

            def read_process():
                yield dut.source_read.valid.eq(1)
                yield dut.source_read.ep.eq(0x0)

                for _ in range(36): # wait for write_process()
                    self.assertEqual((yield dut.source_read.ready), 0)
                    yield Tick()

                self.assertEqual((yield dut.source_read.ready), 1)
                yield dut.source_data.ready.eq(1)

                for _ in range(2):
                    self.assertEqual((yield dut.source_data.valid), 0)
                    yield Tick()

                for i in range(32):
                    self.assertEqual((yield dut.source_data.valid), 1)
                    self.assertEqual((yield dut.source_data.data), i)
                    self.assertEqual((yield dut.source_data.last), 0)
                    yield Tick()

            sim.add_clock(1e-6)
            sim.add_sync_process(write_process)
            sim.add_sync_process(read_process)
            sim.run()

    def test_max_size_with_zlp(self):
        dut = USBOutputBuffer({0x0: (None, 32, Transfer.BULK)})
        with Simulator(dut) as sim:
            def write_process():
                yield dut.sink_write.valid.eq(1)
                yield dut.sink_write.ep.eq(0x0)

                yield Delay(1e-7)
                self.assertEqual((yield dut.sink_write.ready), 1)

                for _ in range(3):
                    self.assertEqual((yield dut.sink_data.ready), 0)
                    yield Tick()

                for i in range(32):
                    self.assertEqual((yield dut.sink_data.ready), 1)
                    yield dut.sink_data.valid.eq(1)
                    yield dut.sink_data.data.eq(i)
                    yield dut.sink_data.crc_ok.eq(i == 31)
                    yield dut.sink_data.last.eq(i == 31)
                    yield Tick()

                yield dut.sink_write.valid.eq(0)
                yield dut.sink_data.valid.eq(0)

                for i in range(21):
                    # wait an arbitrary delay < 32, so that read_process() is in the middle of
                    # reading the packet data.
                    yield Tick()

                yield dut.sink_write.valid.eq(1)

                yield Delay(1e-7)
                self.assertEqual((yield dut.sink_write.ready), 1)

                for _ in range(3):
                    self.assertEqual((yield dut.sink_data.ready), 0)
                    yield Tick()

                self.assertEqual((yield dut.sink_data.ready), 1)
                yield dut.recv_zlp.eq(1)

                yield Tick()

                yield dut.sink_write.valid.eq(0)
                yield dut.recv_zlp.eq(0)

            def read_process():
                yield dut.source_read.valid.eq(1)
                yield dut.source_read.ep.eq(0x0)

                for _ in range(36): # wait for write_process()
                    self.assertEqual((yield dut.source_read.ready), 0)
                    yield Tick()

                self.assertEqual((yield dut.source_read.ready), 1)
                yield dut.source_data.ready.eq(1)

                for _ in range(2):
                    self.assertEqual((yield dut.source_data.valid), 0)
                    yield Tick()

                for i in range(32):
                    self.assertEqual((yield dut.source_data.valid), 1)
                    self.assertEqual((yield dut.source_data.data), i)
                    self.assertEqual((yield dut.source_data.last), i == 31)
                    yield Tick()

            sim.add_clock(1e-6)
            sim.add_sync_process(write_process)
            sim.add_sync_process(read_process)
            sim.run()
