#!/usr/bin/env python3
"""Deterministic normalization pass over the Q&A dataset.

Currently: strip editorial angle-bracket supplements (`<...>`) from the
`question` and `answer` fields, keeping the supplied words (e.g. `f<ui>sse` ->
`fuisse`, `<Est> in cistula` -> `Est in cistula`). The `<` / `>` characters
never occur in Latin text, so removing them is safe. Idempotent.

Usage: python3 normalize_dataset.py [dataset_dir]   (default: ./dataset)
"""
import glob
import json
import os
import re
import sys

dataset_dir = sys.argv[1] if len(sys.argv) > 1 else "dataset"


def strip_brackets(s: str) -> str:
    s = s.replace("<", "").replace(">", "")
    s = re.sub(r"\s{2,}", " ", s)  # tidy any double space left behind
    return s


changed = 0
files = 0
for path in sorted(glob.glob(os.path.join(dataset_dir, "*.json"))):
    with open(path) as fh:
        data = json.load(fh)
    dirty = False
    for p in data.get("pairs", []):
        for field in ("question", "answer"):
            new = strip_brackets(p[field])
            if new != p[field]:
                print(f"  {os.path.basename(path)} [{field}] {p[field]!r} -> {new!r}")
                p[field] = new
                dirty = True
                changed += 1
    if dirty:
        with open(path, "w") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
        files += 1

print(f"\nnormalized {changed} field(s) across {files} file(s)")
