# Makefile for Cocotb v2.0+

# defaults
SIM ?= icarus
TOPLEVEL_LANG ?= verilog

# --- Project-specific settings ---

# The Verilog source file
VERILOG_SOURCES += $(PWD)/rtl/mux_generic.v

# The name of your top-level Verilog module
TOPLEVEL := mux_generic

# The name of your Python test file (without the .py extension)
COCOTB_TEST_MODULES := test_mux

# --- End of project-specific settings ---


# Add the test directory to the python path
export PYTHONPATH := $(PWD)/test:$(PYTHONPATH)

# Include the Cocotb-provided make rules
include $(shell cocotb-config --makefiles)/Makefile.sim
