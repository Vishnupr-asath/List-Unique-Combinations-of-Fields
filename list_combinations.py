#!/usr/bin/env python3
import os
import argparse
import yaml
import json
from collections import defaultdict

def extract_fields(insn):
    """
    Extract opcode, funct3, funct7 from instruction definition.
    Handles both flat dicts and 'fields' as list of dicts.
    """
    opcode = None
    funct3 = None
    funct7 = None

    # Case 1: instruction already has direct keys
    if "opcode" in insn or "funct3" in insn or "funct7" in insn:
        opcode = insn.get("opcode")
        funct3 = insn.get("funct3")
        funct7 = insn.get("funct7")

    # Case 2: fields inside a list of dicts
    elif "fields" in insn and isinstance(insn["fields"], list):
        for f in insn["fields"]:
            if not isinstance(f, dict):
                continue
            name = f.get("name")
            val = f.get("value")
            if name == "opcode":
                opcode = val
            elif name == "funct3":
                funct3 = val
            elif name == "funct7":
                funct7 = val

    return {"opcode": opcode, "funct3": funct3, "funct7": funct7}

def collect_combinations(root):
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
            if tup not in seen:  # avoid duplicates
                combos[extension].append(fields)
                seen.add(tup)

    return combos

def main():
    parser = argparse.ArgumentParser(description="List unique opcode/funct3/funct7 combinations")
    parser.add_argument("--root", type=str, required=True, help="Root directory containing YAML files")
    parser.add_argument("--out", type=str, required=True, help="Output JSON file")
    args = parser.parse_args()

    combos = collect_combinations(args.root)

    with open(args.out, "w") as f:
        json.dump(combos, f, indent=2)

if __name__ == "__main__":
    main()
