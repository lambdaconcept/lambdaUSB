from nmigen import *

from lambdausb import usb
from lambdausb.usb.config import ConfigurationFSM
from lambdausb.io import ulpi


class RgbBlinker(Elaboratable):
    def __init__(self, pins):
        self.ep_out = usb.OutputEndpoint(xfer=usb.Transfer.BULK, max_size=512)
        self._pins  = pins

    def elaborate(self, platform):
        m = Module()

        led = Signal()
        sel = Record([("r", 1), ("g", 1), ("b", 1)])

        m.d.comb += self.ep_out.rdy.eq(1)
        with m.If(self.ep_out.stb):
            m.d.sync += sel.eq(self.ep_out.data[:3])

        clk_freq = platform.default_clk_frequency
        ctr = Signal(range(int(clk_freq//2)), reset=int(clk_freq//2)-1)
        with m.If(ctr == 0):
            m.d.sync += ctr.eq(ctr.reset)
            m.d.sync += led.eq(~led)
        with m.Else():
            m.d.sync += ctr.eq(ctr - 1)

        m.d.comb += [
            self._pins.r.o.eq(sel.r & led),
            self._pins.g.o.eq(sel.g & led),
            self._pins.b.o.eq(sel.b & led)
        ]

        return m


class USBBlinker(Elaboratable):
    def elaborate(self, platform):
        m = Module()

        # USB device
        m.submodules.ulpi_phy = ulpi_phy = ulpi.PHY(pins=platform.request("ulpi", 0))
        m.submodules.usb_dev  = usb_dev  = usb.Device()
        m.d.comb += [
            ulpi_phy.rx.connect(usb_dev.rx),
            usb_dev.tx.connect(ulpi_phy.tx),
        ]

        # Configuration endpoint
        from config import descriptor_map, rom_init
        m.submodules.cfg_fsm = cfg_fsm = ConfigurationFSM(descriptor_map, rom_init)
        usb_dev.add_endpoint(cfg_fsm.ep_in,  addr=0)
        usb_dev.add_endpoint(cfg_fsm.ep_out, addr=0)
        m.d.comb += usb_dev.addr.eq(cfg_fsm.dev_addr)

        # RGB blinker endpoint
        m.submodules.blinker = blinker = RgbBlinker(pins=platform.request("rgb_led", 0))
        usb_dev.add_endpoint(blinker.ep_out, addr=1)

        return m


if __name__ == "__main__":
    from lambdausb.boards.usbsniffer import USBSnifferPlatform
    platform = USBSnifferPlatform()
    platform.build(USBBlinker(), do_program=True)
