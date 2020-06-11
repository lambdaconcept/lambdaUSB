from nmigen.back.pysim import *


def simulation_test(dut, process, sync=True):
    sim = Simulator(dut)
    if sync:
        sim.add_clock(1e-6)
        sim.add_sync_process(process)
    else:
        sim.add_process(process)
    with sim.write_vcd("test.vcd"):
        sim.run()
