import enum

from nmigen import *


class PacketID(enum.IntEnum):
    OUT   = 0b0001
    IN    = 0b1001
    SOF   = 0b0101
    SETUP = 0b1101

    DATA0 = 0b0011
    DATA1 = 0b1011
    DATA2 = 0b0111
    MDATA = 0b1111

    ACK   = 0b0010
    NAK   = 0b1010
    STALL = 0b1110
    NYET  = 0b0110

    PRE   = 0b1100
    ERR   = 0b1100
    SPLIT = 0b1000
    PING  = 0b0100

    RESERVED = 0

    @staticmethod
    def is_token(pid):
        assert isinstance(pid, Value)
        return pid.matches("--01")

    @staticmethod
    def is_data(pid):
        assert isinstance(pid, Value)
        return pid.matches("--11")

    @staticmethod
    def is_handshake(pid):
        assert isinstance(pid, Value)
        return pid.matches("--10")

    @staticmethod
    def is_special(pid):
        assert isinstance(pid, Value)
        return pid.matches("--00")


class LineState(enum.IntEnum):
    SE0 = 0b00
    J   = 0b01
    K   = 0b10
    SE1 = 0b11
