import cocotb
from cocotb.triggers import Timer
import random

# ==============================================================================
# 1. Helper Functions
# ==============================================================================

def to_32_bit(val):
    """Converts a Python integer to its 32-bit two's complement representation."""
    return val & 0xFFFFFFFF

def to_signed(val, bits=32):
    """Converts a two's complement value to a signed Python integer."""
    if (val >> (bits - 1)) == 1:
        return val - (1 << bits)
    return val

# ==============================================================================
# 2. Python "Golden Model" of the ALU
# ==============================================================================

def alu_model(op_a, op_b, alu_opcode_str):
    """
    A pure Python model of our Verilog ALU. This is our "source of truth"
    for verifying the hardware's results.
    """
    op_a = to_32_bit(op_a)
    op_b = to_32_bit(op_b)

    result = 0xDEADBEEF # Default for unknown op

    if alu_opcode_str == "ADD":
        result = op_a + op_b
    elif alu_opcode_str == "SUB":
        result = op_a - op_b
    elif alu_opcode_str == "SLL":
        # In Verilog, shift amount uses only lower 5 bits of op_b
        result = op_a << (op_b & 0x1F)
    elif alu_opcode_str == "SLT":
        # Signed comparison
        result = 1 if to_signed(op_a) < to_signed(op_b) else 0
    elif alu_opcode_str == "SLTU":
        # Unsigned comparison (standard Python behavior)
        result = 1 if op_a < op_b else 0
    elif alu_opcode_str == "XOR":
        result = op_a ^ op_b
    elif alu_opcode_str == "SRL":
        result = op_a >> (op_b & 0x1F)
    elif alu_opcode_str == "SRA":
        # Arithmetic shift right (needs careful handling of the sign bit)
        result = to_signed(op_a) >> (op_b & 0x1F)
    elif alu_opcode_str == "OR":
        result = op_a | op_b
    elif alu_opcode_str == "AND":
        result = op_a & op_b

    result = to_32_bit(result)
    zero_flag = 1 if result == 0 else 0

    return result, zero_flag

# ==============================================================================
# 3. Cocotb Testcases
# ==============================================================================

# A dictionary to map opcode names to their integer values
ALU_OPS = {
    "ADD": 0b0000, "SUB": 0b0001, "SLL": 0b0010, "SLT": 0b0011, "SLTU": 0b0100,
    "XOR": 0b0101, "SRL": 0b0110, "SRA": 0b0111, "OR": 0b1000, "AND": 0b1001
}

# --- TEST 1: Systematic Corner Case Testing ---
@cocotb.test()
async def alu_corner_case_test(dut):
    """Tests a hand-picked list of corner cases."""
    dut._log.info("--- Starting ALU Corner Case Test ---")

    MAX_POS = 0x7FFFFFFF
    MAX_NEG = 0x80000000
    MAX_UNSIGNED = 0xFFFFFFFF

    test_vectors = [
        # Description, operand_a, operand_b, opcode_str
        ("ADD: Overflow", MAX_POS, 1, "ADD"),
        ("ADD: Zero", 0, 0, "ADD"),
        ("SUB: Underflow", MAX_NEG, 1, "SUB"),
        ("SUB: 0 - 1", 0, 1, "SUB"),
        ("SLL: Shift by 0", 0x12345678, 0, "SLL"),
        ("SLL: Shift by 31", 1, 31, "SLL"),
        ("SRL: Shift max", MAX_UNSIGNED, 31, "SRL"),
        ("SRA: Shift negative num", MAX_NEG, 1, "SRA"),
        ("SLT: Signed compare pos/neg", 10, to_32_bit(-10), "SLT"),
        ("SLT: Signed compare neg/neg", to_32_bit(-10), to_32_bit(-5), "SLT"),
        ("SLTU: Unsigned compare", MAX_POS, MAX_NEG, "SLTU"),
        ("AND: All ones", MAX_UNSIGNED, MAX_UNSIGNED, "AND"),
        ("XOR: Self", 0xABCDEFFF, 0xABCDEFFF, "XOR"),
        ("OR: Zero", 0, 0, "OR")
    ]

    for description, op_a, op_b, op_name in test_vectors:
        # Drive DUT
        dut.operand_a.value = op_a
        dut.operand_b.value = op_b
        dut.alu_opcode.value = ALU_OPS[op_name]
        await Timer(1, "ns")

        # Get expected result from the golden model
        expected_res, expected_zero = alu_model(op_a, op_b, op_name)

        # Log and Assert
        dut._log.info(f"CORNER CASE: {description}")
        assert dut.result.value == expected_res, f"Result mismatch for {description}!"
        assert dut.zero_flag.value == expected_zero, f"Zero flag mismatch for {description}!"

    dut._log.info("--- All ALU Corner Case Tests Passed! ---")

# --- TEST 2: Randomized Testing ---
@cocotb.test()
async def alu_random_test(dut):
    """Tests a large number of random inputs against the golden model."""
    dut._log.info("--- Starting ALU Randomized Test ---")

    num_random_tests = 500
    op_names = list(ALU_OPS.keys())

    for i in range(num_random_tests):
        # Generate random inputs
        op_a = random.randint(0, 0xFFFFFFFF)
        op_b = random.randint(0, 0xFFFFFFFF)
        op_name = random.choice(op_names)

        # For shifts, constrain the shift amount to a reasonable range
        if op_name in ["SLL", "SRL", "SRA"]:
            op_b = random.randint(0, 63) # Testing shifts > 31 is useful

        # Drive DUT
        dut.operand_a.value = op_a
        dut.operand_b.value = op_b
        dut.alu_opcode.value = ALU_OPS[op_name]
        await Timer(1, "ns")

        # Get expected result from the golden model
        expected_res, expected_zero = alu_model(op_a, op_b, op_name)

        # Assert
        assert dut.result.value == expected_res, \
            f"RANDOM FAIL [#{i}]: op={op_name}, a={op_a:#x}, b={op_b:#x} -> DUT={int(dut.result.value):#x}, MODEL={expected_res:#x}"
        assert dut.zero_flag.value == expected_zero, \
            f"RANDOM FAIL [#{i}] ZERO FLAG: op={op_name}, a={op_a:#x}, b={op_b:#x} -> DUT={int(dut.zero_flag.value)}, MODEL={expected_zero}"

        if (i + 1) % 50 == 0:
            dut._log.info(f"Completed {i+1}/{num_random_tests} random tests.")

    dut._log.info(f"--- All {num_random_tests} Randomized Tests Passed! ---")
