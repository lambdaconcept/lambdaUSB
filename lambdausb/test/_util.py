from nmigen.back.pysim import *


def simulation_test(dut, process):
    sim = Simulator(dut)
    sim.add_clock(1e-6)
    sim.add_sync_process(process)
    with sim.write_vcd("test.vcd"):
        sim.run()
