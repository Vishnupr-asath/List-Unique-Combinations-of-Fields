# List-Unique-Combinations-of-Fields


## Objective
The goal of this assignment is to:
- Parse RISC-V instruction YAML files.
- Extract all unique `(opcode, funct3, funct7)` combinations.
- Group them by extension (e.g., rv32i, rv32m).
- Save the results in a JSON file.

---

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

---

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
