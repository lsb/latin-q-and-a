#!/usr/bin/env python3
"""Aggregate the per-work factual/*.json files into a single JSONL dataset.

Writes qa.jsonl -- one Q&A pair per line, each:
  {source, author, work, locus, source_text, question, answer,
   question_en, answer_en, derivation}
Prints summary statistics (pairs per author, works with/without pairs).
"""
import glob
import json
from collections import Counter

rows = []
works = 0
empty_works = 0
for f in sorted(glob.glob("factual/*.json")):
    d = json.load(open(f))
    works += 1
    if not d.get("pairs"):
        empty_works += 1
    for p in d["pairs"]:
        rows.append({
            "source": d["source"],
            "author": d.get("author", ""),
            "work": d.get("work", ""),
            "locus": p["locus"],
            "source_text": p["source_text"],
            "question": p["question"],
            "answer": p["answer"],
            "question_en": p.get("question_en", ""),
            "answer_en": p.get("answer_en", ""),
            "derivation": p.get("derivation", ""),
        })

with open("qa.jsonl", "w") as fh:
    for r in rows:
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")

by_author = Counter(r["author"] for r in rows)
print(f"works: {works}  (with pairs: {works - empty_works}, empty: {empty_works})")
print(f"pairs: {len(rows)}  -> qa.jsonl")
print("by author:")
for a, n in sorted(by_author.items(), key=lambda kv: -kv[1]):
    print(f"  {n:5}  {a}")
