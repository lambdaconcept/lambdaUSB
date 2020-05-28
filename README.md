# lambdaUSB

## A configurable USB 2.0 device core using [nMigen](https://github.com/m-labs/nmigen)

**lambdaUSB is still in an experimental stage and is therefore incomplete. The user-facing API may change before reaching stability.**

![lambdaUSB Diagram Image](doc/diagram.png)

### Features

* High Speed USB
* up to 32 endpoints (16 inputs, 16 outputs)
* double buffering, per endpoint

### Installation

Download and install lambdaUSB:

    git clone https://github.com/lambdaconcept/lambdaUSB
    cd lambdaUSB
    python3 setup.py develop --user

### Usage

1. Instantiate the USB device:

```python
m.submodules.ulpi_phy = ulpi_phy = ulpi.PHY(pins=platform.request("ulpi", 0))
m.submodules.usb_dev  = usb_dev  = usb.Device()
m.d.comb += [
    ulpi_phy.rx.connect(usb_dev.rx),
    usb_dev.tx.connect(ulpi_phy.tx),
]
```

For the moment, only ULPI transceivers such as the USB3300 are supported.

2. Instantiate endpoint interfaces:

```python
ep1_in  = usb.InputEndpoint(xfer=usb.Transfer.BULK, max_size=512)
ep1_out = usb.OutputEndpoint(xfer=usb.Transfer.BULK, max_size=512)
```

3. Add endpoint interfaces to the USB device:

```python
usb_dev.add_endpoint(ep1_in,  addr=1, dir="i")
usb_dev.add_endpoint(ep1_out, addr=1, dir="o")
```

For a full example, have a look at `examples/blinker`.

### Device configuration

For convenience, we provide a `ConfigurationFSM` to manage EP0 in `lambdausb.usb.config`.
It stores the configuration descriptors in a ROM, and responds to host requests.

To use it, you must first generate a config file:
```
cd tools/genconfig
make
```

You will be presented a menuconfig interface from which you can setup your USB device:

![menuconfig interface](doc/menuconfig.png)

The output `config.py` file can be imported and used like so:

```python
from lambdausb.usb.config import ConfigurationFSM
from config import descriptor_map, rom_init

m.submodules.cfg_fsm = cfg_fsm = ConfigurationFSM(descriptor_map, rom_init)
usb_dev.add_endpoint(cfg_fsm.ep_in,  addr=0, dir="i")
usb_dev.add_endpoint(cfg_fsm.ep_out, addr=0, dir="o")
```

### License

lambdaUSB is released under the two-clause BSD license.
