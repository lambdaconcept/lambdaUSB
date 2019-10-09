from nmigen import *

from lambdausb.cfg import ConfigurationEndpoint
from lambdausb.dev import UsbDevice
from lambdausb.lib import stream
from lambdausb.phy.ulpi import ULPIPhy
from lambdausb.protocol import Transfer


class RgbBlinkerEndpoint(Elaboratable):
    def __init__(self, rgb_led):
        self.rgb_led = rgb_led
        self.sink = stream.Endpoint([("data", 8)])

    def elaborate(self, platform):
        m = Module()

        led = Signal()
        sel = Record([("r", 1), ("g", 1), ("b", 1)])

        m.d.comb += self.sink.ready.eq(Const(1))
        with m.If(self.sink.valid):
            m.d.sync += sel.eq(self.sink.data[:3])

        clk_freq = platform.default_clk_frequency
        ctr = Signal.range(int(clk_freq//2), reset=int(clk_freq//2)-1)
        with m.If(ctr == 0):
            m.d.sync += ctr.eq(ctr.reset)
            m.d.sync += led.eq(~led)
        with m.Else():
            m.d.sync += ctr.eq(ctr - 1)

        m.d.comb += [
            self.rgb_led.r.o.eq(sel.r & led),
            self.rgb_led.g.o.eq(sel.g & led),
            self.rgb_led.b.o.eq(sel.b & led)
        ]

        return m


class UsbBlinker(Elaboratable):
    def elaborate(self, platform):
        m = Module()

        # USB device
        ulpi_phy  = m.submodules.ulpi_phy = ULPIPhy(platform.request("ulpi", 0))
        usb_dev   = m.submodules.usb_dev  = UsbDevice(ulpi_phy)

        # Configuration endpoint
        from config import descriptor_map, rom_init
        cfg_ep  = m.submodules.cfg_ep = ConfigurationEndpoint(descriptor_map, rom_init)
        cfg_in  = usb_dev.input_port(0x0, 64, Transfer.CONTROL)
        cfg_out = usb_dev.output_port(0x0, 64, Transfer.CONTROL)

        m.d.comb += [
            cfg_ep.source.connect(cfg_in),
            cfg_out.connect(cfg_ep.sink)
        ]

        # RGB blinker endpoint
        rgb_ep  = m.submodules.rgb_ep = RgbBlinkerEndpoint(platform.request("rgb_led", 0))
        rgb_out = usb_dev.output_port(0x1, 512, Transfer.BULK)

        m.d.comb += rgb_out.connect(rgb_ep.sink)

        return m


if __name__ == "__main__":
    from lambdausb.boards.usbsniffer import USBSnifferPlatform
    platform = USBSnifferPlatform()
    platform.build(UsbBlinker())
