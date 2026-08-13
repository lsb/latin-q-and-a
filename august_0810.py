#!/usr/bin/env python3
"""Build august_final.jsonl from the spreadsheet's combined_qa_08-10 tab.

august_final.py's successor: same idea, same output schema and same output
file, one tab newer. 08-10 is 139 pairs against 08-03's 146.

Inputs:
  combined_qa_08-10.csv            -- snapshot of the combined_qa_08-10 tab.
  combined_qa_08-10_crosswalk.json -- the join: sheet ID -> [jsonl file, line].
  manually_reviewed.jsonl          -- Lee's 393 corpus-extracted pairs.
  manually_compiled.jsonl          -- Vivienne + Marisa's 124 compiled pairs.
  letters_and_history.accepted.jsonl -- Lee's 283 accepted letters-and-history
                                      pairs.

As in august_final.py the spreadsheet is authoritative for text and the jsonl
files supply structured provenance (source, author, work, provenance, locus),
derivation and track.

What changed from 08-03:

  * Seven pairs were dropped: ids 24, 57, 64, 73, 91, 96 and 130 (Uticae,
    Ad Traianum, Hierosolyma, Hypocaustum, Cloaca Maxima, Clepsydra, Carrhae).
    All seven remain members of unified_q_and_a.jsonl and three of
    manually_reviewed.jsonl, so a tab dropping a pair is a selection decision,
    not a verdict on the pair, and nothing else was pruned on their account.
  * Six were rewritten in place, keeping both their id and their gold answer:
    54 tonitru -> tonitrua; 92 manisonum -> mansionum (a typo); 74 Quod mare ->
    Quod fretum; 115 personae statariae scurrilis -> personae scurrilis; 47
    in Circo -> in Circo Maximo; 22 proelians in -> proelians apud Uticam in.
    qid is sha1(locus|question), so all six take a NEW qid here, and the
    evaluation rows generated against their old wording no longer match them.
  * Unlike 07-22 -> 08-03, ids ARE stable across this pair of tabs: the
    crosswalk was bootstrapped by question text (133 exact, 6 fuzzy at 0.93 or
    better, none ambiguous) and every match landed on its own id. It is frozen
    in combined_qa_08-10_crosswalk.json and this script only reads it.
  * The tab carries eight trailing columns holding stray tallies in the header
    row and nothing else; they are ignored.

Writes august_final.jsonl in sheet order and prints summary statistics.
"""
import csv
import json
from collections import Counter

SHEET = "combined_qa_08-10.csv"
CROSSWALK = "combined_qa_08-10_crosswalk.json"

# Which compiler each pool belongs to; the sheet's Author column must agree.
POOL_AUTHOR = {
    "manually_reviewed.jsonl": "Lee",
    "letters_and_history.accepted.jsonl": "Lee",
    "manually_compiled.jsonl": "Vivienne",
}


def clean(s):
    """Strip whitespace and an unpaired trailing double-quote (sheet typo)."""
    s = (s or "").strip()
    if s.endswith('"') and s.count('"') % 2 == 1:
        s = s[:-1].rstrip()
    return s


def load_jsonl(path):
    return [json.loads(line) for line in open(path)]


pools = {f: load_jsonl(f) for f in POOL_AUTHOR}
sheet = [r for r in csv.DictReader(open(SHEET)) if clean(r.get("Question"))]
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

    category = clean(s["category"])
    if not category:
        raise SystemExit(f"row {sid} has no category")

    rows.append({
        "id": sid,
        "compiled_by": s["Author"],
        "checked_by": clean(s["Checked By"]),
        "source": j["source"],
        "author": j["author"],
        "work": j["work"],
        "provenance": j["provenance"],
        "locus": j["locus"],
        "evidence_url": clean(s["Evidence_url"]),
        "source_text": clean(s["source_text"]) or j["source_text"],
        "question": clean(s["Question"]),
        "answer": clean(s["Answer"]),
        "question_en": clean(s["Question Corrected Translation"]),
        "answer_en": clean(s["Answer Corrected Translation"]) or j["answer_en"],
        "derivation": j["derivation"],
        "category": category,
        "track": j["track"],
        "difficulty": clean(s["difficulty"]),
        "notes": clean(s["Notes"]),
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
