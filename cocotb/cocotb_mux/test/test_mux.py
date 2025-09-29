import cocotb
from cocotb.triggers import Timer
import random

@cocotb.test()
async def mux_generic_test(dut):
    """Test the Generic N-to-1 Mux"""

    # Read parameters from the DUT to make the testbench generic
    NUM_INPUTS = int(dut.NUM_INPUTS.value)
    WIDTH = int(dut.WIDTH.value)
    MAX_VAL = (2**WIDTH) - 1

    dut._log.info(f"Testing a {NUM_INPUTS}-to-1 mux with {WIDTH}-bit data width.")

    # Create random data for all inputs
    input_data = [random.randint(0, MAX_VAL) for _ in range(NUM_INPUTS)]

    # --- FIX IS HERE ---
    # Assign each value from the list to the corresponding index in the DUT
    for i in range(NUM_INPUTS):
        dut.data_in[i].value = input_data[i]

    await Timer(1, "ns") # Let values settle

    dut._log.info(f"Generated random inputs: {input_data}")

    # Iterate through each possible select value
    for sel_value in range(NUM_INPUTS):
        # Set the select line
        dut.sel.value = sel_value
        await Timer(1, "ns")

        # Get the expected output from our Python list
        expected_output = input_data[sel_value]

        # Read the actual output from the DUT
        actual_output = dut.out.value

        dut._log.info(f"Selecting input {sel_value}. Expected: {expected_output}, Got: {int(actual_output)}")

        # Assert that the output is correct
        assert actual_output == expected_output, \
            f"FAIL: sel={sel_value} -> out={int(actual_output)}, expected={expected_output}"

    dut._log.info("All select lines tested successfully!")
