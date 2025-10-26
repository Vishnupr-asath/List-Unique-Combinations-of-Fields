import os
import random
from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from cocotbext.axi import AxiMaster, AxiBus, AxiBurstType
from cocotbext.uart import UartSource, UartSink

import logging
import vsc
from enum import Enum, auto

# ---------------------------
# UART constants and helpers
# ---------------------------

UartParity = Enum("UartParity", "NONE EVEN ODD MARK SPACE")

UART0 = 0x00011300
UART_BASE = 0x00011300
print("uart base value:", hex(UART_BASE))

# Register Offsets (byte addresses)
BAUD_REG      = UART_BASE + 0x00  # 16-bit
TX_REG        = UART_BASE + 0x04  # 32-bit
RX_REG        = UART_BASE + 0x08  # 32-bit
STATUS_REG    = UART_BASE + 0x0C  # 16-bit
DELAY_REG     = UART_BASE + 0x10  # 16-bit
CTRL_REG      = UART_BASE + 0x14  # 16-bit
INTERRUPT_EN  = UART_BASE + 0x18  # 16-bit (treated as 16-bit field)
IQCYC_REG     = UART_BASE + 0x1C  # 16-bit
RX_THRESH     = UART_BASE + 0x20  # 16-bit

# CTRL register assumed bitfields:
# [2:1] stop_bits: 00=1, 01=1.5, 10=2
# [4:3] parity:    00=none, 01=odd, 10=even, 11=reserved
# [9:5] data width (5 bits)
CTRL_STOP_LSB   = 1
CTRL_PARITY_LSB = 3
CTRL_DW_LSB     = 5
CTRL_DW_MASK    = 0x1F   # 5 bits

def parity_to_field(p: UartParity) -> int:
    if p == UartParity.NONE:
        return 0b00
    if p == UartParity.ODD:
        return 0b01
    if p == UartParity.EVEN:
        return 0b10
    return 0b00

def field_to_stop_bits(field: int):
    if field == 0b00: return 1
    if field == 0b01: return 1.5
    if field == 0b10: return 2
    return 1

# ---------------------------
# 64-bit AXI helpers
# ---------------------------

AXI_BEAT_BYTES = 8

def _align8(addr: int):
    base = addr & ~0x7
    byte_off = addr & 0x7
    return base, byte_off

async def axi_read64(axim: AxiMaster, addr: int, *, arid=0, prot=0) -> int:
    base, _ = _align8(addr)
    rd = await axim.read(address=base, length=AXI_BEAT_BYTES,
                         arid=arid, burst=AxiBurstType.FIXED, size=3, prot=prot)
    return int.from_bytes(rd.data, "little")

async def axi_write64(axim: AxiMaster, addr: int, value: int, *, awid=1, prot=0):
    base, _ = _align8(addr)
    data = int(value & ((1 << 64) - 1)).to_bytes(AXI_BEAT_BYTES, "little")
    await axim.write(address=base, data=data,
                     awid=awid, burst=AxiBurstType.FIXED, size=3, prot=prot)

async def rmw16_64(axim: AxiMaster, reg_addr: int, value16: int, *, arid=0, awid=1):
    base, off = _align8(reg_addr)
    shift = off * 8
    cur = await axi_read64(axim, base, arid=arid)
    mask = 0xFFFF << shift
    newv = (cur & ~mask) | ((value16 & 0xFFFF) << shift)
    await axi_write64(axim, base, newv, awid=awid)

async def rmw32_64(axim: AxiMaster, reg_addr: int, value32: int, *, arid=0, awid=1):
    base, off = _align8(reg_addr)
    assert off in (0, 4), f"32-bit reg must be aligned at +0 or +4 within 64b beat (addr=0x{reg_addr:X})"
    shift = off * 8
    cur = await axi_read64(axim, base, arid=arid)
    mask = 0xFFFFFFFF << shift
    newv = (cur & ~mask) | ((value32 & 0xFFFFFFFF) << shift)
    await axi_write64(axim, base, newv, awid=awid)

def extract16_from_u64(u64: int, reg_addr: int) -> int:
    _, off = _align8(reg_addr)
    return (u64 >> (off * 8)) & 0xFFFF

def extract32_from_u64(u64: int, reg_addr: int) -> int:
    _, off = _align8(reg_addr)
    return (u64 >> (off * 8)) & 0xFFFFFFFF

# ---------------------------
# Coverage model (unchanged)
# ---------------------------

@vsc.randobj
class uart_item(object):
    def __init__(self):
        self.data = vsc.rand_bit_t(8)

@vsc.covergroup
class my_covergroup(object):
    def __init__(self):
        self.with_sample(
            data=vsc.bit_t(8),
            stop_bits=vsc.bit_t(2),
            parity=vsc.bit_t(2),
            data_width=vsc.bit_t(5),
        )

        self.DATA = vsc.coverpoint(self.data, cp_t=vsc.uint8_t())
        self.Stop_bit = vsc.coverpoint(self.stop_bits, bins={
            "one_stop": vsc.bin(0b00),
            "one_half_stop": vsc.bin(0b01),
            "two_stop": vsc.bin(0b10)
        })
        self.Parity = vsc.coverpoint(self.parity, bins={
            "no_parity": vsc.bin(0b00),
            "odd_parity": vsc.bin(0b01),
            "even_parity": vsc.bin(0b10)
        })
        self.Data_Width = vsc.coverpoint(self.data_width, cp_t=vsc.uint8_t())

# ---------------------------
# Testbench skeleton
# ---------------------------

class Testbench:
    def __init__(self, dut):
        self.dut = dut
        self.log = logging.getLogger("cocotb.tb")
        self.log.setLevel(logging.DEBUG)
        self.axi_master = AxiMaster(AxiBus.from_prefix(dut, 'ccore_master_d'),
                                    clock=dut.CLK, reset=dut.RST_N, reset_active_level=False)
        self.cg = my_covergroup()

class uart_components:
    def __init__(self, dut, clk_freq, axi_baud_value, stop_bits_num, selected_parity, data_width, uart_number):
        self.dut = dut
        self.txrx = uart_item()

        # Calculate real UART line baud from clk/baud_div
        self.baud_rate = clk_freq // (16 * axi_baud_value)

        # Map the correct SOUT for the requested UART
        uart_souts = {
            0x00011300: dut.uart_cluster.uart0.SOUT,
        }
        selected_sout = uart_souts[uart_number]

        self.log = logging.getLogger("cocotb.tb")
        self.log.setLevel(logging.DEBUG)

        # UartSink uses "bits" as data bits count
        self.uart_tx = UartSink(selected_sout, baud=self.baud_rate,
                                bits=data_width, stop_bits=stop_bits_num, parity=selected_parity)

# ---------------------------
# The actual test (64-bit AXI)
# ---------------------------

@cocotb.test()
async def test_peripherals_64b_axi(dut):
    """Verify UART via 64-bit AXI transactions (all beats are 64-bit)."""

    # Clock/reset
    clock = Clock(dut.CLK, 100, units="ns")  # 10 MHz
    cocotb.start_soon(clock.start(start_high=False))
    dut.RST_N.value = 0
    for _ in range(400):
        await RisingEdge(dut.CLK)
    dut.RST_N.value = 1
    for _ in range(50):
        await RisingEdge(dut.CLK)

    tb = Testbench(dut)
    for _ in range(100):
        await RisingEdge(tb.dut.CLK)

    # (Optional) Log bus widths to confirm 64-bit bus underneath
    try:
        w_bits = len(dut.ccore_master_d_wdata)
        r_bits = len(dut.ccore_master_d_rdata)
        dut._log.info(f"AXI WDATA width = {w_bits}, RDATA width = {r_bits}")
    except Exception:
        pass

    # ---------------------------
    # Initialize small regs (via 64-bit RMW)
    # ---------------------------
    await rmw16_64(tb.axi_master, DELAY_REG,     0x0000)
    await rmw16_64(tb.axi_master, IQCYC_REG,     0x0000)
    await rmw16_64(tb.axi_master, RX_THRESH,     0x0000)
    await rmw16_64(tb.axi_master, INTERRUPT_EN,  0x0000)

    # Baud divisor (16-bit)
    axi_baud_value = 0x0005
    await rmw16_64(tb.axi_master, BAUD_REG, axi_baud_value)
    for _ in range(10):
        await RisingEdge(tb.dut.CLK)

    # Read back BAUD via single 64-bit beat
    u64 = await axi_read64(tb.axi_master, BAUD_REG)
    baud_back = extract16_from_u64(u64, BAUD_REG)
    dut._log.info(f"BAUD back = 0x{baud_back:04X}")
    assert baud_back == axi_baud_value, f"BAUD mismatch: got 0x{baud_back:04X} exp 0x{axi_baud_value:04X}"

    # STATUS read via 64-bit beat
    u64 = await axi_read64(tb.axi_master, STATUS_REG)
    status = extract16_from_u64(u64, STATUS_REG)
    dut._log.info(f"STATUS = 0x{status:04X}")

    # ---------------------------
    # Configure CTRL via 64-bit RMW
    # ---------------------------
    # Choose UART params
    clk_freq = 10_000_000  # 10 MHz
    stop_field = random.choice([0b00, 0b01, 0b10])
    stop_bits_num = field_to_stop_bits(stop_field)
    parity_sel = UartParity.NONE
    parity_field = parity_to_field(parity_sel)
    data_width = random.choice([5, 6, 7, 8])  # realistic UART data widths

    # Compose CTRL 16-bit field
    control_reg_value = 0
    # stop bits [2:1]
    control_reg_value &= ~(0b11 << CTRL_STOP_LSB)
    control_reg_value |= ((stop_field & 0b11) << CTRL_STOP_LSB)
    # parity [4:3]
    control_reg_value &= ~(0b11 << CTRL_PARITY_LSB)
    control_reg_value |= ((parity_field & 0b11) << CTRL_PARITY_LSB)
    # data width [9:5]
    control_reg_value &= ~(CTRL_DW_MASK << CTRL_DW_LSB)
    control_reg_value |= ((data_width & CTRL_DW_MASK) << CTRL_DW_LSB)
    control_reg_value &= 0xFFFF

    await rmw16_64(tb.axi_master, CTRL_REG, control_reg_value)
    for _ in range(10):
        await RisingEdge(tb.dut.CLK)

    # Read CTRL back
    u64 = await axi_read64(tb.axi_master, CTRL_REG)
    ctrl_back = extract16_from_u64(u64, CTRL_REG)
    dut._log.info(f"CTRL back = 0x{ctrl_back:04X}")

    # ---------------------------
    # Build UART components (sink listens to line)
    # ---------------------------
    tb1 = uart_components(dut, clk_freq, axi_baud_value,
                          stop_bits_num, parity_sel, data_width, UART_BASE)

    # Sample coverage on configuration (data will be added after we pick it)
    # We'll fill 'data' later with the TX payload
    tb.cg.sample(0, stop_field, parity_field, data_width)

    # ---------------------------
    # Transmit: write TX_REG via 64-bit RMW (32-bit field)
    # ---------------------------
    etx_data = random.getrandbits(data_width)  # write one data byte/word as per width
    tx_word32 = etx_data & 0xFF  # TX is byte-wise on UART line; keep 1 byte
    await rmw32_64(tb.axi_master, TX_REG, tx_word32)

    # Read out of the UartSink (blocking wait)
    await tb1.uart_tx.wait()
    tx_bytes = tb1.uart_tx.read_nowait()  # returns 'bytes'

    # Update coverage with actual data observed
    if isinstance(tx_bytes, (bytes, bytearray)) and len(tx_bytes) >= 1:
        sent_byte = tx_bytes[0]
    else:
        # Some versions may return int; normalize
        sent_byte = int(tx_bytes) & 0xFF
    tb.cg.sample(sent_byte, stop_field, parity_field, data_width)

    # Check that the first byte matches what we sent
    assert sent_byte == (tx_word32 & 0xFF), \
        f"Data Mismatch DUT[0x{sent_byte:02X}] != EXP[0x{tx_word32 & 0xFF:02X}]"

    # STATUS re-read for sanity
    u64 = await axi_read64(tb.axi_master, STATUS_REG)
    status2 = extract16_from_u64(u64, STATUS_REG)
    dut._log.info(f"STATUS after TX = 0x{status2:04X}")

    # Optional RX read (if loopback / RX path present)
    try:
        u64 = await axi_read64(tb.axi_master, RX_REG)
        rx_val = extract32_from_u64(u64, RX_REG)
        dut._log.info(f"RX (32-bit) = 0x{rx_val:08X}")
    except Exception:
        pass

    # Leave some cycles, then dump coverage
    for _ in range(100):
        await RisingEdge(tb.dut.CLK)

    vsc.write_coverage_db('cov.xml')
