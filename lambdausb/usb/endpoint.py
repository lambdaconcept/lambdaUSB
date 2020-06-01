import enum

from nmigen import *
from nmigen.hdl.rec import *


__all__ = ["Transfer", "InputEndpoint", "OutputEndpoint"]


class Transfer(enum.IntEnum):
    ISOCHRONOUS = 0
    CONTROL     = 1
    BULK        = 2
    INTERRUPT   = 3


class _Endpoint(Record):
    def __init__(self, layout, xfer, max_size, name=None, src_loc_at=0):
        if not isinstance(xfer, Transfer):
            raise TypeError("Transfer type must be an instance of Transfer, not {!r}"
                            .format(xfer))

        if not isinstance(max_size, int) or max_size < 0:
            raise ValueError("Maximum packet size must be a positive integer, not {!r}"
                             .format(max_size))
        if xfer is Transfer.ISOCHRONOUS and max_size > 1024:
            # FIXME: 1023 for a Full Speed device
            raise ValueError("Invalid maximum packet size {}; must be lesser than or equal to "
                             "1024 for an isochronous endpoint".format(max_size))
        if xfer is Transfer.CONTROL and max_size > 64:
            raise ValueError("Invalid maximum packet size {}; must be lesser than or equal to "
                             "64 for a control endpoint".format(max_size))
        if xfer in {Transfer.BULK, Transfer.INTERRUPT} and max_size > 512:
            raise ValueError("Invalid maximum packet size {}; must be lesser than or equal to "
                             "512 for a bulk or interrupt endpoint".format(max_size))

        self.xfer     = xfer
        self.max_size = max_size

        super().__init__(layout, name=name, src_loc_at=1 + src_loc_at)


class InputEndpoint(_Endpoint):
    def __init__(self, *, xfer, max_size, name=None, src_loc_at=0):
        layout = [
            ("stb",  1, DIR_FANOUT),
            ("lst",  1, DIR_FANOUT),
            ("data", 8, DIR_FANOUT),
            ("zlp",  1, DIR_FANOUT),
            ("rdy",  1, DIR_FANIN),
            ("ack",  1, DIR_FANIN),
            ("sof",  1, DIR_FANIN),
        ]
        super().__init__(layout, xfer, max_size, name=name, src_loc_at=1 + src_loc_at)


class OutputEndpoint(_Endpoint):
    def __init__(self, *, xfer, max_size, name=None, src_loc_at=0):
        layout = [
            ("stb",   1, DIR_FANIN),
            ("lst",   1, DIR_FANIN),
            ("data",  8, DIR_FANIN),
            ("setup", 1 if xfer is Transfer.CONTROL else 0, DIR_FANIN),
            ("drop",  1, DIR_FANIN),
            ("rdy",   1, DIR_FANOUT),
            ("sof",   1, DIR_FANIN),
        ]
        super().__init__(layout, xfer, max_size, name=name, src_loc_at=1 + src_loc_at)
