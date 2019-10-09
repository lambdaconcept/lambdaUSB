# lambdaUSB

## A configurable USB 2.0 device core

**lambdaUSB is still in an experimental stage and is therefore incomplete. The user-facing API may change before reaching stability.**

### Features

* High Speed USB
* double buffering, per endpoint
* up to 15 endpoints in each direction (IN, OUT)

![lambdaUSB Diagram Image](https://docs.google.com/drawings/d/e/2PACX-1vS7PLHyw8llfi1wKCpyv5ixTY4_0yfFZNDxHLV-RroDoT8vq1HVreaJ2UVPz8-auc55SqGZjr_35Hx7/pub?w=1165&h=883)

### Installation

Obtain and install lambdaUSB:

    git clone https://github.com/lambdaconcept/lambdaUSB
    cd lambdaUSB
    python3 setup.py develop --user

### License

lambdaUSB is released under the two-clause BSD license.
