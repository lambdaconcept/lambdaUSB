import enum

from nmigen import *
from nmigen.hdl.rec import *


__all__ = ["Transfer", "InputEndpoint", "OutputEndpoint"]


class Transfer(enum.IntEnum):
    """Transfer type.

    See USB 2.0 specification sections 4.7 and 5.4-5.8 for details.
    """
    ISOCHRONOUS = 0
    CONTROL     = 1
    BULK        = 2
    INTERRUPT   = 3


class _Endpoint(Record):
    _doc_template = """
    {description}

    Parameters
    ----------
    xfer : :class:`Transfer`
        Transfer type.
    max_size : int
        Maximum packet size. We only check this value against upper bounds in High-Speed mode.
        It must also be greater than or equal to the wMaxPacketSize of the endpoint descriptor.
    {parameters}

    Attributes
    ----------
    {attributes}
    """
    def __init__(self, layout, xfer, max_size, name=None, src_loc_at=0):
        if not isinstance(xfer, Transfer):
            raise TypeError("Transfer type must be an instance of Transfer, not {!r}"
                            .format(xfer))

        if not isinstance(max_size, int) or max_size < 0:
            raise ValueError("Maximum packet size must be a positive integer, not {!r}"
                             .format(max_size))
        if xfer is Transfer.ISOCHRONOUS and max_size > 1024:
            raise ValueError("Invalid maximum packet size {}; must be lesser than or equal to "
                             "1024 for an isochronous endpoint".format(max_size))
        if xfer is Transfer.CONTROL and max_size > 64:
            raise ValueError("Invalid maximum packet size {}; must be lesser than or equal to "
                             "64 for a control endpoint".format(max_size))
        if xfer is Transfer.BULK and max_size > 512:
            raise ValueError("Invalid maximum packet size {}; must be lesser than or equal to "
                             "512 for a bulk endpoint".format(max_size))
        if xfer is Transfer.INTERRUPT and max_size > 1024:
            raise ValueError("Invalid maximum packet size {}; must be lesser than or equal to "
                             "1024 for an interrupt endpoint".format(max_size))

        self.xfer     = xfer
        self.max_size = max_size

        super().__init__(layout, name=name, src_loc_at=1 + src_loc_at)

    __hash__ = object.__hash__


class InputEndpoint(_Endpoint):
    __doc__ = _Endpoint._doc_template.format(
    description="""
    Input endpoint interface.

    This interface is an input from the host point of view, but an output from the device
    point of view.
    """.strip(),
    parameters="",
    attributes="""
    stb : Signal, out
        Write strobe.
    lst : Signal, out
        Write last. Asserted when `data` holds the last byte of the payload.
    data : Signal, out
        Write data.
    zlp : Signal, out
        Write zero-length payload. To send an empty payload, the endpoint must assert `zlp` and
        `lst` at the beginning of the transfer.
    rdy : Signal, in
        Write ready. Asserted when the device is ready to accept data from the endpoint.
    ack : Signal, in
        Write acknowledge. Asserted when the device received an ACK for the previous payload.
        Unused if the endpoint was added to the device with a double buffer. This signal allows
        the endpoint to implement its own buffering mechanism.
    sof : Signal, in
        Start of (micro)frame. Asserted when the device received a SOF packet.
    """.strip())
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
    __doc__ = _Endpoint._doc_template.format(
    description="""
    Output endpoint interface.

    This interface is an output from the host point of view, but an input from the device
    point of view.
    """.strip(),
    parameters="",
    attributes="""
    rdy : Signal, out
        Read ready. Asserted when the endpoint is ready to accept data from the device.
    stb : Signal, in
        Read strobe.
    lst : Signal, in
        Read last. Asserted when `data` holds the last byte of the payload.
    data : Signal, in
        Read data.
    setup : Signal, in
        Read setup. Asserted when the payload comes from a SETUP packet.
    drop : Signal, in
        Drop payload. Asserted when the device invalidates the payload (e.g. because of a bad CRC).
        Unused if the endpoint was added to the device with a double buffer. This signal allows
        the endpoint to implement its own buffering mechanism.
    sof : Signal, in
        Start of frame. Asserted when the device received a SOF packet.
    """.strip())
    def __init__(self, *, xfer, max_size, name=None, src_loc_at=0):
        layout = [
            ("rdy",   1, DIR_FANOUT),
            ("stb",   1, DIR_FANIN),
            ("lst",   1, DIR_FANIN),
            ("data",  8, DIR_FANIN),
            ("setup", 1 if xfer is Transfer.CONTROL else 0, DIR_FANIN),
            ("drop",  1, DIR_FANIN),
            ("sof",   1, DIR_FANIN),
        ]
        super().__init__(layout, xfer, max_size, name=name, src_loc_at=1 + src_loc_at)
