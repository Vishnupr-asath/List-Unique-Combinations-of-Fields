import cocotb
from cocotb.triggers import Timer
import random

@cocotb.test()
async def adder_basic_test(dut):
    """Test for 4-bit adder"""

    # Get a handle to the DUT's ports
    a = dut.a
    b = dut.b
    sum_out = dut.sum

    dut._log.info("Running basic adder test")

    # Run 10 random test cases
    for i in range(10):
        # Generate random 4-bit values
        val_a = random.randint(0, 15)
        val_b = random.randint(0, 15)

        # Assign values to the DUT's inputs
        a.value = val_a
        b.value = val_b

        # Wait for a small amount of time for the combinational logic to settle
        await Timer(2, units="ns")

        # Calculate the expected result in Python
        # The '& 0xF' ensures the result is masked to 4 bits, mimicking hardware behavior
        expected_sum = (val_a + val_b) & 0xF

        # Log the transaction
        dut._log.info(f"Test case {i+1}: a={val_a}, b={val_b}, expected={expected_sum}, got={int(sum_out.value)}")

        # Assert that the DUT's output matches the expected value
        assert sum_out.value == expected_sum, f"Adder result is incorrect: {sum_out.value} != {expected_sum}"

    dut._log.info("All test cases passed!")
