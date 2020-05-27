import os
import subprocess

from nmigen.build import *
from nmigen.vendor.xilinx_7series import *


__all__ = ["USBSnifferPlatform"]


class USBSnifferPlatform(Xilinx7SeriesPlatform):
    device = "xc7a35t"
    package = "fgg484"
    speed = "2"
    default_clk = "clk100"

    resources = [
        Resource("clk100", 0, Pins("J19", dir="i"), Clock(100e6), Attrs(IOSTANDARD="LVCMOS33")),

        Resource("rgb_led", 0,
            Subsignal("r", PinsN("W2", dir="o")),
            Subsignal("g", PinsN("Y1", dir="o")),
            Subsignal("b", PinsN("W1", dir="o")),
            Attrs(IOSTANDARD="LVCMOS33")
        ),

        Resource("rgb_led", 1,
            Subsignal("r", PinsN("AA1", dir="o")),
            Subsignal("g", PinsN("AB1", dir="o")),
            Subsignal("b", PinsN("Y2" , dir="o")),
            Attrs(IOSTANDARD="LVCMOS33")
        ),

        Resource("serial", 0,
            Subsignal("tx", Pins("U21", dir="o")), # FPGA_GPIO0
            Subsignal("rx", Pins("T21", dir="i")), # FPGA_GPIO1
            Attrs(IOSTANDARD="LVCMOS33")
        ),

        Resource("ulpi_sw", 0,
            Subsignal("s",  Pins("Y8", dir="o")),
            Subsignal("oe", PinsN("Y9", dir="o")),
            Attrs(IOSTANDARD="LVCMOS33")
        ),

        Resource("ulpi", 0,
            Subsignal("clk", Pins("W19", dir="i"), Clock(60e6)),
            Subsignal("data", Pins("AB18 AA18 AA19 AB20 AA20 AB21 AA21 AB22", dir="io")),
            Subsignal("dir", Pins("W21", dir="i")),
            Subsignal("stp", Pins("Y22", dir="o")),
            Subsignal("nxt", Pins("W22", dir="i")),
            Subsignal("rst", Pins("V20", dir="o")),
            Attrs(IOSTANDARD="LVCMOS33", SLEW="FAST")
        ),

        Resource("ulpi", 1,
            Subsignal("clk", Pins("V4", dir="i"), Clock(60e6)),
            Subsignal("data", Pins("AB2 AA3 AB3 Y4 AA4 AB5 AA5 AB6", dir="io")),
            Subsignal("dir", Pins("AB7", dir="i")),
            Subsignal("stp", Pins("AA6", dir="o")),
            Subsignal("nxt", Pins("AB8", dir="i")),
            Subsignal("rst", Pins("AA8", dir="o")),
            Attrs(IOSTANDARD="LVCMOS33", SLEW="FAST")
        ),

        Resource("ft601", 0,
            Subsignal("clk", Pins("D17", dir="i"), Clock(100e6)),
            Subsignal("rst", Pins("K22", dir="o")),
            Subsignal("data", Pins("A16 F14 A15 F13 A14 E14 A13 E13 B13 C15 C13 C14 B16 E17 B15 F16 "
                                   "A20 E18 B20 F18 D19 D21 E19 E21 A21 B21 A19 A18 F20 F19 B18 B17", dir="io")),
            Subsignal("be", Pins("K16 L16 G20 H20", dir="o")),
            Subsignal("rxf_n", Pins("M13", dir="i")),
            Subsignal("txe_n", Pins("L13", dir="i")),
            Subsignal("rd_n",  Pins("K19", dir="o")),
            Subsignal("wr_n",  Pins("M15", dir="o")),
            Subsignal("oe_n",  Pins("L21", dir="o")),
            Subsignal("siwua", Pins("M16", dir="o")),
            Attrs(IOSTANDARD="LVCMOS33", SLEW="FAST")
        )
    ]
    connectors = []

    def toolchain_prepare(self, fragment, name, **kwargs):
        overrides = {
            "script_before_bitstream":
                "set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]",
            "script_after_bitstream":
                "write_cfgmem -force -format bin -interface spix4 -size 16 "
                "-loadbit \"up 0x0 {name}.bit\" -file {name}.bin".format(name=name),
            "add_constraints":
                "set_property INTERNAL_VREF 0.675 [get_iobanks 34]"
        }
        return super().toolchain_prepare(fragment, name, **overrides, **kwargs)

    def toolchain_program(self, products, name):
        xc3sprog = os.environ.get("XC3SPROG", "xc3sprog")
        with products.extract("{}.bit".format(name)) as bitstream_filename:
            subprocess.run([xc3sprog, "-c", "ft4232h", bitstream_filename], check=True)
