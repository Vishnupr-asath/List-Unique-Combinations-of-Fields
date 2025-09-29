# Makefile for Cocotb v2.0+

# defaults
SIM ?= icarus
TOPLEVEL_LANG ?= verilog

# --- Project-specific settings ---

# Tell cocotb where to find the Verilog source files
VERILOG_SOURCES += $(PWD)/rtl/subtractor.v

# The name of your top-level Verilog module
TOPLEVEL := subtractor

# The name of your Python test file (without the .py extension)
COCOTB_TEST_MODULES := test_subtractor

# --- End of project-specific settings ---


# We add our test directory to the PYTHONPATH environment variable.
# This allows cocotb's test runner to find our module.
export PYTHONPATH := $(PWD)/test:$(PYTHONPATH)

# Include the Cocotb-provided make rules
include $(shell cocotb-config --makefiles)/Makefile.sim
