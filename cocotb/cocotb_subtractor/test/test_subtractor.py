import cocotb
from cocotb.triggers import Timer
import random

@cocotb.test()
async def subtractor_test(dut):
    """Test the N-bit subtractor"""

    # Get the width from the Verilog parameter and CONVERT IT TO AN INTEGER
    WIDTH = int(dut.WIDTH.value)
    MAX_VAL = (2**WIDTH) - 1

    dut._log.info(f"Testing a {WIDTH}-bit subtractor")

    # --- Test Case 1: Simple subtraction (5 - 3 = 2) ---
    a = 5
    b = 3
    dut.a.value = a
    dut.b.value = b
    await Timer(1, units="ns")

    expected_diff = (a - b)
    expected_borrow = 0

    dut._log.info(f"Testing {a} - {b}. Expected: diff={expected_diff}, borrow={expected_borrow}")
    assert dut.diff.value == expected_diff, f"FAIL: diff is {dut.diff.value} not {expected_diff}"
    assert dut.borrow_out.value == expected_borrow, f"FAIL: borrow is {dut.borrow_out.value} not {expected_borrow}"

    # --- Test Case 2: Subtraction resulting in a borrow (3 - 5 = -2) ---
    a = 3
    b = 5
    dut.a.value = a
    dut.b.value = b
    await Timer(1, units="ns")

    # In hardware, (3-5) for 4 bits is 1110 (14), which is the two's complement of -2
    expected_diff = (a - b) & MAX_VAL
    expected_borrow = 1

    dut._log.info(f"Testing {a} - {b}. Expected: diff={expected_diff}, borrow={expected_borrow}")
    assert dut.diff.value == expected_diff, f"FAIL: diff is {dut.diff.value} not {expected_diff}"
    assert dut.borrow_out.value == expected_borrow, f"FAIL: borrow is {dut.borrow_out.value} not {expected_borrow}"

    # --- Test Case 3: Randomized tests ---
    dut._log.info("Running 10 randomized tests...")
    for i in range(10):
        a = random.randint(0, MAX_VAL)
        b = random.randint(0, MAX_VAL)

        dut.a.value = a
        dut.b.value = b
        await Timer(1, units="ns")

        expected_diff = (a - b) & MAX_VAL
        expected_borrow = 1 if a < b else 0

        dut._log.info(f"Random test {i+1}: {a} - {b}. Got: diff={int(dut.diff.value)}, borrow={int(dut.borrow_out.value)}")
        assert dut.diff.value == expected_diff
        assert dut.borrow_out.value == expected_borrow

    dut._log.info("All tests passed!")
