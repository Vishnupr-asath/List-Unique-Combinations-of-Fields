# Makefile for Cocotb v2.0+

# defaults
SIM ?= icarus
TOPLEVEL_LANG ?= verilog

# --- Project-specific settings ---

# The Verilog source file for the ALU block
VERILOG_SOURCES += $(PWD)/rtl/alu.v

# The name of the top-level Verilog module
TOPLEVEL := alu

# The name of the Python test file (without the .py extension)
COCOTB_TEST_MODULES := test_alu

# --- End of project-specific settings ---


# Add the test directory to the python path
export PYTHONPATH := $(PWD)/test:$(PYTHONPATH)

# Include the Cocotb-provided make rules
include $(shell cocotb-config --makefiles)/Makefile.sim
