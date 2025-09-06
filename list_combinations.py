import os
import argparse
import yaml
import json
from collections import defaultdict

def extract_fields(insn):
    """
    Extract opcode, funct3, funct7 from instruction definition.
    Uses the 'fields' section in YAML.
    """
    opcode = funct3 = funct7 = None

    if "fields" in insn and isinstance(insn["fields"], list):
        for f in insn["fields"]:
            name = f.get("name")
            val = f.get("value")
            if val is not None:
                # Convert binary or hex strings to integer
                if isinstance(val, str):
                    if val.startswith("0b"):
                        val = int(val, 2)
                    elif val.startswith("0x"):
                        val = int(val, 16)
                # Assign to correct field
                if name == "opcode":
                    opcode = val
                elif name == "funct3":
                    funct3 = val
                elif name == "funct7":
                    funct7 = val

    return {"opcode": opcode, "funct3": funct3, "funct7": funct7}

def collect_combinations(root):
    """
    Collect all unique (opcode, funct3, funct7) combinations from YAML files in the root directory.
    Groups results by file name (without extension).
    """
    combos = defaultdict(list)

    for fname in os.listdir(root):
        if not fname.endswith(".yaml"):
            continue

        path = os.path.join(root, fname)
        with open(path, "r") as f:
            try:
                data = yaml.safe_load(f)
            except yaml.YAMLError:
                continue

        if not isinstance(data, list):
            continue

        extension = os.path.splitext(fname)[0]
        seen = set()

        for insn in data:
            fields = extract_fields(insn)
            tup = (fields["opcode"], fields["funct3"], fields["funct7"])
            # Only add if at least one field is not None and it's not a duplicate
            if tup not in seen and any(fields.values()):
                combos[extension].append(fields)
                seen.add(tup)

    return combos

def main():
    parser = argparse.ArgumentParser(description="List unique opcode/funct3/funct7 combinations")
    parser.add_argument("--root", type=str, required=True, help="Directory with YAML files")
    parser.add_argument("--out", type=str, required=True, help="Output JSON file")
    args = parser.parse_args()

    combos = collect_combinations(args.root)

    with open(args.out, "w") as f:
        json.dump(combos, f, indent=2)

    print(f"Saved combinations to {args.out}")

if __name__ == "__main__":
    main()
