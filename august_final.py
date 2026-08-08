#!/usr/bin/env python3
"""Build august_final.jsonl from the spreadsheet's combined_qa_08-03 tab.

This is unify.py's successor: same idea, same output schema, newer tab. The
shared sheet
(https://docs.google.com/spreadsheets/d/1voKeEENq0bVWYN-a80v8OGnpoB7vb7i4lXViFjZZruo)
grew three tabs after combined_qa_07-22, and the last of them,
combined_qa_08-03 (gid 2105042734), is the final August selection: 146 pairs,
73 by Lee and 73 by Vivienne, cut down from 07-22's 233 and rewritten in
place during review.

Inputs:
  combined_qa_08-03.csv           -- snapshot of the combined_qa_08-03 tab,
                                     exported 2026-08-07.
  combined_qa_08-03_crosswalk.json -- the join: sheet ID -> [jsonl file, line].
  manually_reviewed.jsonl         -- Lee's 393 corpus-extracted pairs.
  manually_compiled.jsonl         -- Vivienne + Marisa's 124 compiled pairs.
  letters_and_history.accepted.jsonl -- Lee's 283 accepted letters-and-history
                                     pairs (Pliny, Cicero, Horace), new since
                                     07-22 and the source of 14 rows here.

As in unify.py the spreadsheet is authoritative for text and the jsonl files
supply structured provenance (source, author, work, provenance, locus),
derivation and track. What changed on this tab:

  * IDs were renumbered. 08-03 IDs run 2..154 with gaps and do NOT line up
    with 07-22 IDs -- 62 of the shared IDs name a different compiler's pair.
    combined_qa_07-22.csv's crosswalk is therefore useless here and a fresh
    one was bootstrapped.
  * Vivienne's Latin was rewritten, not just corrected, so the join could not
    be bootstrapped on question text alone (some pairs share as little as 37%
    of it with manually_compiled.jsonl). The bootstrap scored candidates on
    all four text fields -- question .45, answer .30, question_en .15,
    answer_en .10 -- and the result was checked three ways: every row whose
    question still matches a jsonl question exactly got that same pair, no two
    rows claim one pair, and the 73/73 Lee/Vivienne split falls out of the
    match rather than being imposed. The seven lowest-margin rows were read by
    hand. As with unify.py the join is now identity, not inference: it lives
    in the crosswalk under version control, and this script only reads it.
  * Categories are English for both compilers now (07-22 had Latin for Lee's
    rows and finer English labels for Vivienne's, and unify.py harmonized to
    Latin). The sheet wins, so its English labels are copied as-is; one row
    (ID 140) still carries the Latin "mythos".
  * Every row has a corrected English answer in the sheet, so the
    manually_compiled fallback unify.py needed for Vivienne's rows is now
    dead weight -- kept only as a belt-and-braces default.

A sheet ID missing from the crosswalk, an entry pointing into a file the
sheet's compiler did not write, or two rows claiming the same jsonl pair are
hard errors; extend the crosswalk by hand when rows are added to the tab.

Dropped sheet columns are constants (Language=lat_latn, Country/Region=Rome,
Translation Corrected By) or empty (the automatic-translation columns, URL
language).

Writes august_final.jsonl in sheet order and prints summary statistics.
"""
import csv
import json
from collections import Counter

SHEET = "combined_qa_08-03.csv"
CROSSWALK = "combined_qa_08-03_crosswalk.json"

# Which compiler each pool belongs to; the sheet's Author column must agree.
POOL_AUTHOR = {
    "manually_reviewed.jsonl": "Lee",
    "letters_and_history.accepted.jsonl": "Lee",
    "manually_compiled.jsonl": "Vivienne",
}


def clean(s):
    """Strip whitespace and an unpaired trailing double-quote (sheet typo)."""
    s = s.strip()
    if s.endswith('"') and s.count('"') % 2 == 1:
        s = s[:-1].rstrip()
    return s


def load_jsonl(path):
    return [json.loads(line) for line in open(path)]


pools = {f: load_jsonl(f) for f in POOL_AUTHOR}
sheet = [r for r in csv.DictReader(open(SHEET)) if any(v.strip() for v in r.values() if v)]
crosswalk = json.load(open(CROSSWALK))

rows = []
claimed = set()
for s in sorted(sheet, key=lambda r: int(r["ID"])):
    sid = int(s["ID"])
    if str(sid) not in crosswalk:
        raise SystemExit(f"row {sid} not in {CROSSWALK}; add an entry for it")
    cw_file, cw_line = crosswalk[str(sid)]
    if POOL_AUTHOR[cw_file] != s["Author"]:
        raise SystemExit(f"row {sid}: crosswalk points into {cw_file} "
                         f"({POOL_AUTHOR[cw_file]}'s) but the sheet compiler "
                         f"is {s['Author']}")
    if (cw_file, cw_line) in claimed:
        raise SystemExit(f"row {sid}: {cw_file}:{cw_line} already claimed by an earlier row")
    claimed.add((cw_file, cw_line))
    j = pools[cw_file][cw_line]

    category = s["category"].strip()
    if not category:
        raise SystemExit(f"row {sid} has no category")

    rows.append({
        "id": sid,
        "compiled_by": s["Author"],
        "checked_by": s["Checked By"].strip(),
        "source": j["source"],
        "author": j["author"],
        "work": j["work"],
        "provenance": j["provenance"],
        "locus": j["locus"],
        "evidence_url": s["Evidence_url"].strip(),
        "source_text": s["source_text"].strip() or j["source_text"],
        "question": clean(s["Question"]),
        "answer": clean(s["Answer"]),
        "question_en": clean(s["Question Corrected Translation"]),
        "answer_en": clean(s["Answer Corrected Translation"]) or j["answer_en"],
        "derivation": j["derivation"],
        "category": category,
        "track": j["track"],
        "difficulty": s["difficulty"].strip(),
        "notes": s["Notes"].strip(),
    })

with open("august_final.jsonl", "w") as fh:
    for r in rows:
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")

print(f"pairs: {len(rows)}  -> august_final.jsonl")
for compiler in sorted(set(POOL_AUTHOR.values())):
    n = sum(1 for r in rows if r["compiled_by"] == compiler)
    files = [f for f, a in POOL_AUTHOR.items() if a == compiler]
    drawn = ", ".join(f"{sum(1 for cf, _ in claimed if cf == f)} of {len(pools[f])} in {f}"
                      for f in files)
    print(f"  {n:4}  by {compiler}  ({drawn})")
for key in ("category", "difficulty", "track", "checked_by"):
    print(f"by {key}:")
    for v, n in sorted(Counter(r[key] for r in rows).items(), key=lambda kv: -kv[1]):
        print(f"  {n:5}  {v}")
