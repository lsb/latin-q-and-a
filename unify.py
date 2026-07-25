#!/usr/bin/env python3
"""Unify the two hand-made Q&A sets into unified_q_and_a.jsonl.

Inputs:
  combined_qa_07-22.csv       -- snapshot of the shared review spreadsheet
                                 ("combined_qa_07-22"), 233 rows: Lee's 112
                                 corpus-anchored pairs (a curated subset of
                                 manually_reviewed.jsonl) plus Vivienne's 121
                                 compiled pairs.
  combined_qa_crosswalk.json  -- the join: sheet ID -> [jsonl file, line index].
  manually_reviewed.jsonl     -- Lee's 393 corpus-extracted pairs.
  manually_compiled.jsonl     -- Vivienne + Marisa's 124 compiled pairs.

The spreadsheet is authoritative for text: its Latin and English were
corrected during review, so wherever the sheet and the jsonl disagree the
sheet wins. The jsonl files supply what the sheet lacks: structured
provenance (source, author, work, provenance, locus), derivation, track,
and -- for Vivienne's rows, which have no English answers in the sheet --
answer_en.

The sheet-to-jsonl join is identity, not inference: it lives in
combined_qa_crosswalk.json, bootstrapped once by text matching on 2026-07-23
(see git history for that code) and kept under version control. A sheet ID
missing from the crosswalk, an entry pointing into the wrong compiler's
file, or two rows claiming the same jsonl pair are hard errors; extend the
crosswalk by hand when rows are added to the sheet.

Category is harmonized to the Latin scheme: Lee's sheet categories are
already Latin; Vivienne's rows keep finer English labels in the sheet, each
mapping 1:1 onto the Latin category already recorded in
manually_compiled.jsonl, so her jsonl category is used. Difficulty is
Vivienne's color rating, first letter only (r/o/g/b), copied as-is.

Dropped sheet columns are constants: Language=lat_latn, Country/Region=Rome,
Translation Corrected By=Vivienne, and the empty automatic-translation
columns. Three manually_compiled pairs were left out of the spreadsheet
(sponsalia, flammeum, quaestiones perpetuae) and are excluded here too.

Writes unified_q_and_a.jsonl in sheet order and prints summary statistics.
"""
import csv
import json
from collections import Counter

SHEET = "combined_qa_07-22.csv"
CROSSWALK = "combined_qa_crosswalk.json"


def clean(s):
    """Strip whitespace and an unpaired trailing double-quote (sheet typo,
    e.g. row 158's question)."""
    s = s.strip()
    if s.endswith('"') and s.count('"') % 2 == 1:
        s = s[:-1].rstrip()
    return s


def load_jsonl(path):
    return [json.loads(line) for line in open(path)]


reviewed = load_jsonl("manually_reviewed.jsonl")
compiled = load_jsonl("manually_compiled.jsonl")
sheet = [r for r in csv.DictReader(open(SHEET)) if any(v.strip() for v in r.values())]
crosswalk = json.load(open(CROSSWALK))
pools = {"Lee": ("manually_reviewed.jsonl", reviewed),
         "Vivienne": ("manually_compiled.jsonl", compiled)}

rows = []
claimed = set()
for s in sorted(sheet, key=lambda r: int(r["ID"])):
    sid = int(s["ID"])
    fname, pool = pools[s["Author"]]
    if str(sid) not in crosswalk:
        raise SystemExit(f"row {sid} not in {CROSSWALK}; add an entry for it")
    cw_file, cw_line = crosswalk[str(sid)]
    if cw_file != fname:
        raise SystemExit(f"row {sid}: crosswalk points into {cw_file} but the "
                         f"sheet compiler is {s['Author']}")
    if (cw_file, cw_line) in claimed:
        raise SystemExit(f"row {sid}: {cw_file}:{cw_line} already claimed by an earlier row")
    claimed.add((cw_file, cw_line))
    j = pool[cw_line]

    category = s["category"].strip() if s["Author"] == "Lee" else j["category"]
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

with open("unified_q_and_a.jsonl", "w") as fh:
    for r in rows:
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")

print(f"pairs: {len(rows)}  -> unified_q_and_a.jsonl")
for compiler, (fname, pool) in pools.items():
    n = sum(1 for r in rows if r["compiled_by"] == compiler)
    used = sum(1 for f, _ in claimed if f == fname)
    print(f"  {n:4}  by {compiler}  ({used} distinct of {len(pool)} in {fname})")
for key in ("category", "difficulty", "track"):
    print(f"by {key}:")
    for v, n in sorted(Counter(r[key] for r in rows).items(), key=lambda kv: -kv[1]):
        print(f"  {n:5}  {v}")
left_out = [r for i, r in enumerate(compiled)
            if ("manually_compiled.jsonl", i) not in claimed]
if left_out:
    print("manually_compiled pairs not in the spreadsheet (excluded):")
    for r in left_out:
        print(f"  {r['locus']}: {r['question_en']}")
