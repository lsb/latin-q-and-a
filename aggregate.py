#!/usr/bin/env python3
"""Aggregate the per-work dataset/*.json files into a single JSONL dataset.

Writes qa.jsonl — one Q&A pair per line, each:
  {source, locus, type, question, answer, derivation}
Prints summary statistics.
"""
import glob
import json

rows = []
empty_works = 0
works = 0
for f in sorted(glob.glob("dataset/*.json")):
    d = json.load(open(f))
    works += 1
    if not d["pairs"]:
        empty_works += 1
    for p in d["pairs"]:
        rows.append({
            "source": d["source"],
            "locus": p["locus"],
            "type": p["type"],
            "question": p["question"],
            "answer": p["answer"],
            "derivation": p["derivation"],
        })

with open("qa.jsonl", "w") as fh:
    for r in rows:
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")

by_type = {}
for r in rows:
    by_type[r["type"]] = by_type.get(r["type"], 0) + 1

print(f"works: {works}  (with pairs: {works - empty_works}, empty: {empty_works})")
print(f"pairs: {len(rows)}  -> qa.jsonl")
print("by type:")
for t, n in sorted(by_type.items(), key=lambda kv: -kv[1]):
    print(f"  {n:5}  {t}")
