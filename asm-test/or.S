# See LICENSE for license details.

#*****************************************************************************
# or.S
#-----------------------------------------------------------------------------
#
# Test or instruction.
#

#include "riscv_test.h"
#include "test_macros.h"

RVTEST_RV64U
RVTEST_CODE_BEGIN

  andi t0, t0, 0 # Clear register t0
andi t1, t1, 0 # Clear register t1
andi t2, t2, 0 # Clear register t2
li t0, 0xC53D6 # Load t0 register with a value
li t1, 0xD6332 # Load t1 register with a value
118
or t2, t0, t1

  TEST_PASSFAIL

RVTEST_CODE_END

  .data
RVTEST_DATA_BEGIN

  TEST_DATA

RVTEST_DATA_END
