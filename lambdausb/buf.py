from nmigen import *
from nmigen.utils import bits_for, log2_int

from .lib import stream
from .protocol import Transfer


__all__ = ["USBInputBuffer", "USBOutputBuffer"]


class USBInputBuffer(Elaboratable):
    def __init__(self, endpoint_map):
        self.endpoint_map = endpoint_map

        self.sink_write   = stream.Endpoint([("ep", 4)])
        self.sink_data    = stream.Endpoint([("empty", 1), ("data", 8)])
        self.source_read  = stream.Endpoint([("ep", 4)])
        self.source_data  = stream.Endpoint([("empty", 1), ("data", 8)])

        self.read_xfer    = Signal(2)
        self.recv_ack     = Signal()

    def elaborate(self, platform):
        m = Module()

        ep_info = Array(Record([("max_size", bits_for(512)), ("xfer_type", 2)])
                        for _ in self.endpoint_map)
        for i, (ep_addr, (port, max_size, xfer_type)) in enumerate(self.endpoint_map.items()):
            m.d.comb += [
                ep_info[i].max_size.eq(Const(max_size)),
                ep_info[i].xfer_type.eq(Const(xfer_type))
            ]

        rd_index  = Signal.range(len(self.endpoint_map))
        rd_bad_ep = Signal()

        with m.Switch(self.source_read.ep):
            for i, ep_addr in enumerate(self.endpoint_map):
                with m.Case(ep_addr):
                    m.d.comb += rd_index.eq(i)
            with m.Case():
                m.d.comb += rd_bad_ep.eq(1)

        wr_index  = Signal.like(rd_index)
        wr_bad_ep = Signal()

        with m.Switch(self.sink_write.ep):
            for i, ep_addr in enumerate(self.endpoint_map):
                with m.Case(ep_addr):
                    m.d.comb += wr_index.eq(i)
            with m.Case():
                m.d.comb += wr_bad_ep.eq(1)

        m.d.comb += self.read_xfer.eq(ep_info[rd_index].xfer_type)

        # state memory

        buf_fields = [("valid", 1), ("level", bits_for(512))]

        state_rp1_data = Record([("lru", 1), ("buf1", buf_fields), ("buf2", buf_fields)])
        state_rp2_data = Record.like(state_rp1_data)
        state_wp_data  = Record.like(state_rp1_data)

        state_mem = Memory(width=len(state_rp1_data), depth=len(self.endpoint_map))
        state_rp1 = m.submodules.state_rp1 = state_mem.read_port()
        state_rp2 = m.submodules.state_rp2 = state_mem.read_port()
        state_wp  = m.submodules.state_wp  = state_mem.write_port()

        m.d.comb += [
            state_rp1_data.eq(state_rp1.data),
            state_rp2_data.eq(state_rp2.data),
            state_wp.data.eq(state_wp_data)
        ]

        # data memory

        data_rp_addr = Record([("index", rd_index.width), ("buf_sel", 1), ("offset", log2_int(512))])
        data_wp_addr = Record.like(data_rp_addr)

        data_mem = Memory(width=8, depth=2**len(data_rp_addr))
        data_rp  = m.submodules.data_rp = data_mem.read_port(transparent=False)
        data_wp  = m.submodules.data_wp = data_mem.write_port()

        data_rp.en.reset = 0

        m.d.comb += [
            data_rp.addr.eq(data_rp_addr),
            data_wp.addr.eq(data_wp_addr)
        ]

        # control FSMs

        is_empty = Array(Signal(len(self.endpoint_map), reset=2**len(self.endpoint_map)-1, name="is_empty"))
        is_full  = Array(Signal(len(self.endpoint_map), name="is_full"))

        rd_buf_sel = Signal.like(data_rp_addr.buf_sel)
        rd_offset  = Signal.range(514)
        rd_buf     = Record(buf_fields)
        rd_done    = Signal()


        m.d.comb += [
            self.source_read.ready.eq(~rd_bad_ep & ~is_empty[rd_index]),
            self.sink_write.ready.eq(~wr_bad_ep & ~is_full[wr_index])
        ]

        with m.If(self.source_read.ready & self.source_read.valid):
            m.d.comb += state_rp1.addr.eq(rd_index)
        with m.Else():
            m.d.comb += state_rp1.addr.eq(data_rp_addr.index)

        with m.If(self.sink_write.ready & self.sink_write.valid):
            m.d.comb += state_rp2.addr.eq(wr_index)
        with m.Else():
            m.d.comb += state_rp2.addr.eq(data_wp_addr.index)

        with m.FSM(name="read_fsm") as read_fsm:
            with m.State("IDLE"):
                # m.d.comb += self.source_read.ready.eq(~rd_bad_ep & ~is_empty[rd_index])
                with m.If(self.source_read.ready & self.source_read.valid):
                    m.d.sync += data_rp_addr.index.eq(rd_index)
                    m.next = "READ-0"

            with m.State("READ-0"):
                with m.If(state_rp1_data.buf1.valid & state_rp1_data.buf2.valid):
                    m.d.comb += data_rp_addr.buf_sel.eq(state_rp1_data.lru)
                with m.Else():
                    m.d.comb += data_rp_addr.buf_sel.eq(state_rp1_data.buf2.valid)
                m.d.sync += [
                    rd_buf_sel.eq(data_rp_addr.buf_sel),
                    rd_offset.eq(1),
                    rd_buf.eq(Mux(data_rp_addr.buf_sel, state_rp1_data.buf2, state_rp1_data.buf1))
                ]
                m.d.comb += [
                    data_rp_addr.offset.eq(0),
                    data_rp.en.eq(1)
                ]
                m.next = "READ-1"

            with m.State("READ-1"):
                m.d.comb += [
                    self.source_data.valid.eq(1),
                    self.source_data.empty.eq(rd_buf.level == 0),
                    self.source_data.data.eq(Mux(rd_buf.level.bool(), data_rp.data, 0x00)),
                    self.source_data.last.eq((rd_buf.level == 0) | (rd_buf.level == rd_offset))
                ]
                with m.If(self.source_data.ready):
                    with m.If(self.source_data.last):
                        m.next = "IDLE"
                    with m.Else():
                        m.d.sync += rd_offset.eq(rd_offset + 1)
                        m.d.comb += [
                            data_rp_addr.buf_sel.eq(rd_buf_sel),
                            data_rp_addr.offset.eq(rd_offset),
                            data_rp.en.eq(1)
                        ]

        with m.FSM(name="write_fsm") as write_fsm:
            with m.State("IDLE"):
                with m.If(self.sink_write.ready & self.sink_write.valid):
                    m.d.sync += data_wp_addr.index.eq(wr_index)
                    m.next = "WRITE-0"

            with m.State("WRITE-0"):
                m.d.sync += data_wp_addr.buf_sel.eq(state_rp2_data.buf1.valid)
                with m.If(state_rp2_data.buf1.valid):
                    m.d.sync += data_wp_addr.offset.eq(state_rp2_data.buf2.level)
                with m.Else():
                    m.d.sync += data_wp_addr.offset.eq(state_rp2_data.buf1.level)
                m.next = "WRITE-1"

            with m.State("WRITE-1"):
                with m.If(rd_done): # Wait because state_wp is being driven.
                    m.d.comb += self.sink_data.ready.eq(0)
                with m.Else():
                    m.d.comb += self.sink_data.ready.eq(~wr_bad_ep & (wr_index == data_wp_addr.index))

                with m.If(~self.sink_write.valid | wr_bad_ep | (wr_index != data_wp_addr.index)):
                    m.next = "IDLE"
                with m.Elif(self.sink_data.ready & self.sink_data.valid):
                    with m.If(self.sink_data.last): # TODO handle overflows
                        m.next = "IDLE"
                    with m.Else():
                        m.d.sync += data_wp_addr.offset.eq(data_wp_addr.offset + 1)
                    m.d.comb += [
                        data_wp.data.eq(self.sink_data.data),
                        data_wp.en.eq(1)
                    ]

        # state update

        with m.If(ep_info[data_rp_addr.index].xfer_type == Transfer.ISOCHRONOUS):
            m.d.comb += rd_done.eq(self.source_data.valid & self.source_data.last & self.source_data.ready)
        with m.Else():
            m.d.comb += rd_done.eq(self.recv_ack)

        with m.If(rd_done):
            m.d.sync += is_full[data_rp_addr.index].eq(0)
            with m.If(rd_buf_sel):
                m.d.sync += is_empty[data_rp_addr.index].eq(~state_rp1_data.buf1.valid)
            with m.Else():
                m.d.sync += is_empty[data_rp_addr.index].eq(~state_rp1_data.buf2.valid)

            m.d.comb += [
                state_wp.addr.eq(data_rp_addr.index),
                state_wp.en.eq(1),
                state_wp_data.lru.eq(state_rp1_data.lru),
                state_wp_data.buf1.eq(Mux(rd_buf_sel, state_rp1_data.buf1, 0)),
                state_wp_data.buf2.eq(Mux(rd_buf_sel, 0, state_rp1_data.buf2))
            ]
        with m.Elif(self.sink_data.valid & self.sink_data.ready):
            with m.If(self.sink_data.last):
                m.d.sync += is_empty[wr_index].eq(0)
                with m.If(data_wp_addr.buf_sel):
                    m.d.sync += is_full[wr_index].eq(state_rp2_data.buf1.valid)
                with m.Else():
                    m.d.sync += is_full[wr_index].eq(state_rp2_data.buf2.valid)

            m.d.comb += [
                state_wp.addr.eq(wr_index),
                state_wp.en.eq(1)
            ]

            with m.If(self.sink_data.last):
                m.d.comb += state_wp_data.lru.eq(~data_wp_addr.buf_sel)
            with m.Else():
                m.d.comb += state_wp_data.lru.eq(state_rp2_data.lru)

            with m.If(data_wp_addr.buf_sel):
                m.d.comb += state_wp_data.buf1.eq(state_rp2_data.buf1)
                m.d.comb += [
                    state_wp_data.buf2.valid.eq(self.sink_data.last),
                    state_wp_data.buf2.level.eq(Mux(self.sink_data.empty, 0, data_wp_addr.offset + 1))
                ]
            with m.Else():
                m.d.comb += state_wp_data.buf2.eq(state_rp2_data.buf2)
                m.d.comb += [
                    state_wp_data.buf1.valid.eq(self.sink_data.last),
                    state_wp_data.buf1.level.eq(Mux(self.sink_data.empty, 0, data_wp_addr.offset + 1))
                ]

        return m


class USBOutputBuffer(Elaboratable):
    def __init__(self, endpoint_map):
        self.endpoint_map = endpoint_map

        self.sink_write   = stream.Endpoint([("ep", 4)])
        self.sink_data    = stream.Endpoint([("setup", 1), ("data", 8), ("crc_ok", 1)])
        self.source_read  = stream.Endpoint([("ep", 4)])
        self.source_data  = stream.Endpoint([("setup", 1), ("data", 8)])

        self.write_xfer   = Signal(2)
        self.recv_zlp     = Signal()

    def elaborate(self, platform):
        m = Module()

        ep_info = Array(Record([("max_size", bits_for(512)), ("xfer_type", 2)])
                        for _ in self.endpoint_map)
        for i, (ep_addr, (port, max_size, xfer_type)) in enumerate(self.endpoint_map.items()):
            m.d.comb += [
                ep_info[i].max_size.eq(Const(max_size)),
                ep_info[i].xfer_type.eq(Const(xfer_type))
            ]

        rd_index  = Signal.range(len(self.endpoint_map))
        rd_bad_ep = Signal()

        with m.Switch(self.source_read.ep):
            for i, ep_addr in enumerate(self.endpoint_map):
                with m.Case(ep_addr):
                    m.d.comb += rd_index.eq(i)
            with m.Case():
                m.d.comb += rd_bad_ep.eq(1)

        wr_index  = Signal.like(rd_index)
        wr_bad_ep = Signal()

        with m.Switch(self.sink_write.ep):
            for i, ep_addr in enumerate(self.endpoint_map):
                with m.Case(ep_addr):
                    m.d.comb += wr_index.eq(i)
            with m.Case():
                m.d.comb += wr_bad_ep.eq(1)

        m.d.comb += self.write_xfer.eq(ep_info[wr_index].xfer_type)

        # state memory

        buf_fields = [("valid", 1), ("setup", 1), ("level", bits_for(512))]

        state_rp1_data = Record([("lru", 1), ("buf1", buf_fields), ("buf2", buf_fields)])
        state_rp2_data = Record.like(state_rp1_data)
        state_wp_data  = Record.like(state_rp1_data)

        state_mem = Memory(width=len(state_rp1_data), depth=len(self.endpoint_map))
        state_rp1 = m.submodules.state_rp1 = state_mem.read_port()
        state_rp2 = m.submodules.state_rp2 = state_mem.read_port()
        state_wp  = m.submodules.state_wp  = state_mem.write_port()

        m.d.comb += [
            state_rp1_data.eq(state_rp1.data),
            state_rp2_data.eq(state_rp2.data),
            state_wp.data.eq(state_wp_data)
        ]

        # data memory

        data_rp_addr = Record([("index", rd_index.width), ("buf_sel", 1), ("offset", log2_int(512))])
        data_wp_addr = Record.like(data_rp_addr)

        data_mem = Memory(width=8, depth=2**len(data_rp_addr))
        data_rp  = m.submodules.data_rp = data_mem.read_port(transparent=False)
        data_wp  = m.submodules.data_wp = data_mem.write_port()

        data_rp.en.reset = 0

        m.d.comb += [
            data_rp.addr.eq(data_rp_addr),
            data_wp.addr.eq(data_wp_addr)
        ]

        # control FSMs

        is_empty = Array(Signal(len(self.endpoint_map), reset=2**len(self.endpoint_map)-1, name="is_empty"))
        is_full  = Array(Signal(len(self.endpoint_map), name="is_full"))
        is_last  = Array(Signal(2, name=f"ep{addr}_last") for addr in self.endpoint_map)

        rd_buf_sel = Signal.like(data_rp_addr.buf_sel)
        rd_offset  = Signal.range(514)
        rd_buf     = Record(buf_fields)
        rd_done    = Signal()

        m.d.comb += [
            self.source_read.ready.eq(~rd_bad_ep & ~is_empty[rd_index]),
            self.sink_write.ready.eq(~wr_bad_ep & ~is_full[wr_index])
        ]

        with m.If(self.source_read.ready & self.source_read.valid):
            m.d.comb += state_rp1.addr.eq(rd_index)
        with m.Else():
            m.d.comb += state_rp1.addr.eq(data_rp_addr.index)

        with m.If(self.sink_write.ready & self.sink_write.valid):
            m.d.comb += state_rp2.addr.eq(wr_index)
        with m.Else():
            m.d.comb += state_rp2.addr.eq(data_wp_addr.index)

        with m.FSM(name="read_fsm") as read_fsm:
            with m.State("IDLE"):
                with m.If(self.source_read.ready & self.source_read.valid):
                    m.d.sync += data_rp_addr.index.eq(rd_index)
                    m.next = "READ-0"

            with m.State("READ-0"):
                with m.If(state_rp1_data.buf1.valid & state_rp1_data.buf2.valid):
                    m.d.comb += data_rp_addr.buf_sel.eq(state_rp1_data.lru)
                with m.Else():
                    m.d.comb += data_rp_addr.buf_sel.eq(state_rp1_data.buf2.valid)
                m.d.sync += [
                    rd_buf_sel.eq(data_rp_addr.buf_sel),
                    rd_offset.eq(1),
                    rd_buf.eq(Mux(data_rp_addr.buf_sel, state_rp1_data.buf2, state_rp1_data.buf1))
                ]
                m.d.comb += [
                    data_rp_addr.offset.eq(0),
                    data_rp.en.eq(1)
                ]
                m.next = "READ-1"

            with m.State("READ-1"):
                rd_last = Signal()
                m.d.comb += [
                    rd_last.eq(is_last[data_rp_addr.index].bit_select(rd_buf_sel, 1)),
                    self.source_data.valid.eq(1),
                    self.source_data.setup.eq(rd_buf.setup),
                    self.source_data.data.eq(data_rp.data),
                    self.source_data.last.eq(rd_last & (rd_offset == rd_buf.level))
                ]
                with m.If(self.source_data.ready):
                    with m.If(rd_offset == rd_buf.level):
                        m.d.comb += rd_done.eq(1)
                        m.next = "IDLE"
                    with m.Else():
                        m.d.sync += rd_offset.eq(rd_offset + 1)
                        m.d.comb += [
                            data_rp_addr.buf_sel.eq(rd_buf_sel),
                            data_rp_addr.offset.eq(rd_offset),
                            data_rp.en.eq(1)
                        ]

        with m.FSM(name="write_fsm") as write_fsm:
            with m.State("IDLE"):
                with m.If(self.sink_write.ready & self.sink_write.valid):
                    m.d.sync += data_wp_addr.index.eq(wr_index)
                    m.next = "WRITE-0"

            with m.State("WRITE-0"):
                m.d.sync += [
                    data_wp_addr.buf_sel.eq(state_rp2_data.buf1.valid),
                    data_wp_addr.offset.eq(0)
                ]
                m.next = "WRITE-1"

            with m.State("WRITE-1"):
                with m.If(rd_done): # Wait because state_wp is being driven.
                    m.d.comb += self.sink_data.ready.eq(~self.sink_data.last)
                with m.Else():
                    m.d.comb += self.sink_data.ready.eq(1)

                with m.If(self.recv_zlp):
                    # The host sent a zero-length packet. These are used to mark the previous
                    # packet (sent to this endpoint) as the last of an OUT transfer.
                    m.d.sync += is_last[data_wp_addr.index].eq(1 << ~data_wp_addr.buf_sel)
                    m.next = "IDLE"
                with m.Elif(self.sink_data.ready & self.sink_data.valid):
                    with m.If(self.sink_data.last): # TODO drop packet if overflow
                        m.next = "IDLE"
                    with m.Else():
                        m.d.sync += data_wp_addr.offset.eq(data_wp_addr.offset + 1)
                    m.d.comb += [
                        data_wp.data.eq(self.sink_data.data),
                        data_wp.en.eq(1)
                    ]

        # state update

        with m.If(rd_done):
            m.d.sync += is_full[data_rp_addr.index].eq(0)
            with m.If(rd_buf_sel):
                m.d.sync += is_empty[data_rp_addr.index].eq(~state_rp1_data.buf1.valid)
            with m.Else():
                m.d.sync += is_empty[data_rp_addr.index].eq(~state_rp1_data.buf2.valid)

            m.d.comb += [
                state_wp.addr.eq(data_rp_addr.index),
                state_wp.en.eq(1),
                state_wp_data.lru.eq(state_rp1_data.lru),
                state_wp_data.buf1.eq(Mux(rd_buf_sel, state_rp1_data.buf1, 0)),
                state_wp_data.buf2.eq(Mux(rd_buf_sel, 0, state_rp1_data.buf2))
            ]
        with m.Elif(self.sink_data.valid & self.sink_data.last & self.sink_data.crc_ok & self.sink_data.ready):
            m.d.sync += is_empty[data_wp_addr.index].eq(0)
            with m.If(data_wp_addr.buf_sel):
                m.d.sync += [
                    is_full[data_wp_addr.index].eq(state_rp2_data.buf1.valid),
                    is_last[data_wp_addr.index][1].eq(data_wp_addr.offset + 1 != ep_info[data_wp_addr.index].max_size)
                ]
            with m.Else():
                m.d.sync += [
                    is_full[data_wp_addr.index].eq(state_rp2_data.buf2.valid),
                    is_last[data_wp_addr.index][0].eq(data_wp_addr.offset + 1 != ep_info[data_wp_addr.index].max_size)
                ]

            m.d.comb += [
                state_wp.addr.eq(data_wp_addr.index),
                state_wp.en.eq(1),
                state_wp_data.lru.eq(~data_wp_addr.buf_sel)
            ]

            with m.If(data_wp_addr.buf_sel):
                m.d.comb += state_wp_data.buf1.eq(state_rp2_data.buf1)
                m.d.comb += [
                    state_wp_data.buf2.valid.eq(1),
                    state_wp_data.buf2.setup.eq(self.sink_data.setup),
                    state_wp_data.buf2.level.eq(data_wp_addr.offset + 1)
                ]
            with m.Else():
                m.d.comb += state_wp_data.buf2.eq(state_rp2_data.buf2)
                m.d.comb += [
                    state_wp_data.buf1.valid.eq(1),
                    state_wp_data.buf1.setup.eq(self.sink_data.setup),
                    state_wp_data.buf1.level.eq(data_wp_addr.offset + 1)
                ]

        return m
