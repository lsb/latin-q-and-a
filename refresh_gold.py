#!/usr/bin/env python3
"""Re-point evaluation rows at the current gold answer, and drop verdicts it invalidates.

evaluate.py resumes by (model, qid, rollout): a row that already exists is
never regenerated. That is what makes a re-run cheap, but it also means a row
keeps the `gold` it was written with. When a sheet tab edits an answer without
touching the question, qid is unchanged -- it is sha1(locus|question) -- so the
stale gold survives the re-run, and so does the verdict that was reached
against it.

The candidate answer text is still perfectly good: the question did not change.
Only the grading needs redoing, and only where the edit means something.

This script, for every row whose qid appears in --qa:
  * rewrites `gold` to the QA file's current answer,
  * recomputes `exact` against it,
  * and deletes the row's judgment IF the old and new gold differ after
    normalisation -- i.e. if the edit could change the verdict.

An edit that normalises away (a trailing period, capitalisation, u/v) cannot
change a verdict, so those judgments are left alone rather than being sent back
through the LLM judge for nothing.

Deleted judgments are refilled by a plain re-run, which will not regenerate any
answers:

    python3 refresh_gold.py --dry-run
    python3 refresh_gold.py
    uv run evaluate.py --qa august_final.jsonl --outdir august_final --no-cpu \
        --rollouts 3 --models <the same list>
"""

import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).parent


def load(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def write(p, rows):
    with open(p, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def qid_of(row):
    return hashlib.sha1(f"{row['locus']}|{row['question']}".encode()).hexdigest()[:12]


def norm(s):
    s = unicodedata.normalize("NFD", (s or "").lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("v", "u").replace("j", "i")
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--qa", default=str(HERE / "august_final.jsonl"))
    ap.add_argument("--eval", default=str(HERE / "august_final"))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    gold = {qid_of(r): r["answer"] for r in load(Path(args.qa))}
    apath = Path(args.eval) / "answers.jsonl"
    jpath = Path(args.eval) / "judgments.jsonl"
    answers = load(apath)

    touched, regrade = 0, set()
    for r in answers:
        cur = gold.get(r["qid"])
        if cur is None or r["gold"] == cur:
            continue
        if norm(r["gold"]) != norm(cur):
            regrade.add((r["model"], r["qid"], r["rollout"]))
        r["gold"] = cur
        r["exact"] = norm(r["answer"]) == norm(cur)
        touched += 1

    judgments = load(jpath)
    kept = [j for j in judgments
            if (j["model"], j["qid"], j["rollout"]) not in regrade]

    # evaluate.py settles a normalised string match without asking the LLM
    # judge; the same verdict is free here, so refill what we can rather than
    # send it back through a model.
    by_key = {(r["model"], r["qid"], r["rollout"]): r for r in answers}
    refilled = 0
    for key in regrade:
        r = by_key.get(key)
        if r is not None and r["exact"]:
            kept.append({"model": key[0], "qid": key[1], "rollout": key[2],
                         "same": True, "judge": "exact"})
            refilled += 1

    print(f"{apath.relative_to(HERE)}: {touched} rows re-pointed at current gold")
    print(f"  of those, {len(regrade)} could change verdict and lose their judgment")
    print(f"  {refilled} of those are an exact match against the new gold and are "
          f"re-settled here for free")
    print(f"{jpath.relative_to(HERE)}: {len(judgments)} -> {len(kept)} "
          f"({len(regrade) - refilled} left for the LLM judge)")
    qs = {q for _, q, _ in regrade}
    print(f"  affecting {len(qs)} questions")

    if args.dry_run:
        print("\n--dry-run: nothing written")
        return
    write(apath, answers)
    write(jpath, kept)
    print("\nwritten; re-run evaluate.py to refill the judgments "
          "(no answers will be regenerated)")


if __name__ == "__main__":
    main()
