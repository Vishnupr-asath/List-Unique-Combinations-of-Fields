## List-Unique-Combinations-of-Fields

## Objective
The goal of this assignment is to:
- Parse RISC-V instruction YAML files.
- Extract all unique `(opcode, funct3, funct7)` combinations.
- Group them by extension (e.g., rv32i, rv32m).
- Save the results in a JSON file.

## Steps Followed

### 1. Clone the RISC-V Opcodes Repository
```bash
git clone https://github.com/riscv/riscv-opcodes.git
cd riscv-opcodes
```
### 2.Set Up Python Environment
```Installed the required dependency:
pip3 install pyyaml
```
### 3. Created YAML Files

I created YAML files for the extensions in the extensions/ folder.

### 4. Wrote the Script list_combinations.py

This Python script:

Opens YAML files in the given directory.

Extracts opcode, funct3, and funct7.

Removes duplicates.

Saves results into combinations.json.
```Run with:
python3 list_combinations.py --root extensions --out combinations.json
```
### 5. Output

Output created in the combinations.json file.

## LINUX COMMANDS USED:
### Clone repository
```
git clone https://github.com/riscv/riscv-opcodes.git

cd riscv-opcodes
```

### Install PyYAML
```
pip3 install pyyaml
```
### Run the script
```
python3 list_combinations.py --root extensions --out combinations.json
```
### Check output
```
cat combinations.json
```
---

## GIT COMMANDS
```
git config --global user.email "vishnuprasathoff@gmail.com"

git config --global user.name "Vishnupr-asath"

git clone https://github.com/Vishnupr-asath/List-Unique-Combinations-of-Fields.git

cp list_combinations.py combinations.json ./../..

cd ..

cp ./../../list_combinations.py combinations.json ./

git add .

git commit -m "add .py file"

git push
```
-------
# Learning RTL Verification with Cocotb

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Language: Python](https://img.shields.io/badge/Language-Python-blue.svg)
![Language: Verilog](https://img.shields.io/badge/Language-Verilog-green.svg)

This repository contains a series of hands-on experiments designed to demonstrate modern RTL (Register-Transfer Level) verification techniques using Verilog and the Python-based [Cocotb](https://www.cocotb.org/) framework. The projects progress from simple combinational logic blocks to the block-level verification of a core component of a RISC-V processor, inspired by the [SHAKTI Processor Project](https://shakti.org.in/).

The goal is to showcase a powerful, software-driven workflow for finding bugs and ensuring the correctness of hardware designs.

## Features

This repository includes four self-contained verification projects:

1.  **Combinational Adder (`cocotb_adder`):** A basic 4-bit adder to introduce the fundamental concepts of Cocotb testbenches.
2.  **Combinational Subtractor (`cocotb_subtractor`):** Demonstrates testing of subtraction, two's complement arithmetic, and borrow logic.
3.  **Generic N-to-1 Multiplexer (`cocotb_mux`):** Showcases how to write and test reusable, parameterized Verilog modules. This example also explores the important difference between packed and unpacked arrays in Verilog.
4.  **SHAKTI-inspired RISC-V ALU (`cocotb_shakti_alu`):** A comprehensive block-level test suite for a 32-bit Arithmetic Logic Unit. This example implements an advanced verification strategy including:
    * A Python "golden model" for reference checking.
    * Systematic, hand-picked corner case testing.
    * Constrained Random Verification (CRV) to find unexpected bugs.

## Directory Structure

Each experiment is located in its own directory and is completely self-contained with its own RTL, testbench, and Makefile.

```
.
├── cocotb_adder/
│   ├── Makefile
│   ├── rtl/
│   │   └── adder.v
│   └── test/
│       └── test_adder.py
├── cocotb_subtractor/
│   └── ... (similar structure)
├── cocotb_mux/
│   └── ... (similar structure)
└── cocotb_shakti_alu/
    └── ... (similar structure)
```

## Prerequisites

To run these experiments, you will need the following software installed:

1.  **Python (3.8+):** The language for writing Cocotb testbenches.
2.  **pip:** The Python package installer.
3.  **Icarus Verilog:** A popular open-source Verilog simulator.
    ```bash
    # For Debian/Ubuntu
    sudo apt-get update
    sudo apt-get install iverilog
    ```
4.  **Cocotb:** The verification framework. It's best to install this in a Python virtual environment.
    ```bash
    # Create and activate a virtual environment (optional but recommended)
    python3 -m venv venv
    source venv/bin/activate

    # Install cocotb
    pip install cocotb
    ```

## How to Run the Tests

Navigate into any of the experiment directories and use the `make` command to run the simulation.

#### Testing the Adder
```bash
cd cocotb_adder
make
```

#### Testing the Subtractor
```bash
cd cocotb_subtractor
make
```

#### Testing the Multiplexer
```bash
cd cocotb_mux
make
```

#### Testing the ALU (Advanced)
```bash
cd cocotb_shakti_alu
make
```
This will run both the corner-case and randomized tests.

## Verification Strategy: A Deep Dive into the ALU Test

The test for the ALU (`cocotb_shakti_alu`) demonstrates a professional verification methodology:

1.  **Python Golden Model:** A reference model of the ALU was created in `test_alu.py`. This model acts as the "source of truth," performing the same calculations as the hardware.
2.  **Corner Case Testing:** A specific test (`alu_corner_case_test`) was written to target known edge cases that are common sources of bugs, such as overflows, shifting by maximum values, and comparing signed/unsigned numbers.
3.  **Constrained Random Verification (CRV):** A second test (`alu_random_test`) runs hundreds of iterations, each time generating random inputs and a random operation. It compares the DUT's output against the golden model's output. This powerful technique is excellent at finding unexpected bugs that manual tests might miss.

This two-pronged approach builds very high confidence in the correctness of the hardware block before it's integrated into a larger system.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
