from nmigen import *


__all__ = ["CRC"]


class CRC(Elaboratable):
    def __init__(self, poly, size, dw, init=0xffff):
        self.dw   = dw
        self.size = size
        self.init = init
        self.poly = poly

        self.clr  = Signal()
        self.en   = Signal()
        self.val  = Signal(dw)
        self.crc  = Signal(size)

    def elaborate(self, platform):
        m = Module()

        crcreg = [Signal(self.size, reset=self.init) for i in range(self.dw+1)]

        for i in range(self.dw):
            inv = self.val[i] ^ crcreg[i][self.size-1]
            tmp = []
            tmp.append(inv)
            for j in range(self.size -1):
                if((self.poly >> (j + 1)) & 1):
                    tmp.append(crcreg[i][j] ^ inv)
                else:
                    tmp.append(crcreg[i][j])
            m.d.comb += crcreg[i+1].eq(Cat(*tmp))

        with m.If(self.clr):
            m.d.sync += crcreg[0].eq(self.init)
        with m.Elif(self.en):
            m.d.sync += crcreg[0].eq(crcreg[self.dw])

        m.d.comb += self.crc.eq(crcreg[self.dw][::-1] ^ self.init)

        return m
