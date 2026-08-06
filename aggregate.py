#!/usr/bin/env python3
"""Aggregate the per-work factual/*.json files into a single JSONL dataset.

Writes qa.jsonl -- one Q&A pair per line, each:
  {source, author, work, provenance, locus, source_text, question, answer,
   question_en, answer_en, derivation, category, track}
`provenance` records the corpus a work's text came from; it defaults to the
Latin Library and is overridden per work (e.g. NH 7, which the Latin Library
does not carry, is from LacusCurtius/Teubner). `category` is the coarse domain
tag and `track` marks pairs that waive the translatability criterion; both were
introduced with the June 2026 cultural turn (issue #2), so earlier pairs
default to category "" and track "translatable". Prints summary statistics.

Usage: aggregate.py [dir] [out.jsonl]   (defaults: factual qa.jsonl)
"""
import glob
import json
import sys
from collections import Counter

src_dir = sys.argv[1] if len(sys.argv) > 1 else "factual"
out_path = sys.argv[2] if len(sys.argv) > 2 else "qa.jsonl"

rows = []
works = 0
empty_works = 0
for f in sorted(glob.glob(f"{src_dir}/*.json")):
    d = json.load(open(f))
    works += 1
    if not d.get("pairs"):
        empty_works += 1
    for p in d["pairs"]:
        rows.append({
            "source": d["source"],
            "author": d.get("author", ""),
            "work": d.get("work", ""),
            "provenance": d.get("provenance", "The Latin Library (www.thelatinlibrary.com)"),
            "locus": p["locus"],
            "source_text": p["source_text"],
            "question": p["question"],
            "answer": p["answer"],
            "question_en": p.get("question_en", ""),
            "answer_en": p.get("answer_en", ""),
            "derivation": p.get("derivation", ""),
            "category": p.get("category", ""),
            "track": p.get("track", "translatable"),
        })

with open(out_path, "w") as fh:
    for r in rows:
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")

by_author = Counter(r["author"] for r in rows)
by_category = Counter(r["category"] or "(untagged, pre-2026-06)" for r in rows)
by_track = Counter(r["track"] for r in rows)
print(f"works: {works}  (with pairs: {works - empty_works}, empty: {empty_works})")
print(f"pairs: {len(rows)}  -> {out_path}")
print("by author:")
for a, n in sorted(by_author.items(), key=lambda kv: -kv[1]):
    print(f"  {n:5}  {a}")
print("by category:")
for c, n in sorted(by_category.items(), key=lambda kv: -kv[1]):
    print(f"  {n:5}  {c}")
print("by track:")
for t, n in sorted(by_track.items(), key=lambda kv: -kv[1]):
    print(f"  {n:5}  {t}")
