# Makefile for Cocotb v2.0+

# defaults
SIM ?= icarus
TOPLEVEL_LANG ?= verilog

# Tell cocotb where to find the Verilog source files
VERILOG_SOURCES += $(PWD)/rtl/adder.v

# The name of your top-level Verilog module
TOPLEVEL := adder

# This is the NEW variable for cocotb v2.0+.
# It replaces the old 'MODULE' variable.
COCOTB_TEST_MODULES := test_adder

# We now add our test directory to the PYTHONPATH environment variable.
# This is the modern way to ensure cocotb's test runner can find our module.
export PYTHONPATH := $(PWD)/test:$(PYTHONPATH)

# Include the Cocotb-provided make rules
include $(shell cocotb-config --makefiles)/Makefile.sim
