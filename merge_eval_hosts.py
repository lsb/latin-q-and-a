#!/usr/bin/env python3
"""Fold a second machine's eval run into eval-reviewed/.

Two machines ran evaluate.py independently against overlapping model/question
sets. Their records collide on evaluate.py's key -- (model, qid, rollout) --
but a collision is NOT a duplicate: generation runs at temperature 0.7 with no
shared seed, so the same key holds two independent samples. Of the 1711
colliding answer keys, 1004 carry different answer text. Deduplicating on the
key would silently discard those.

So the merge renumbers instead of dropping. For every (model, qid) both hosts
touched, the incoming host's rollouts are shifted past the resident host's:
local keeps 0..2, the other machine's become 3..5. Judgments are shifted by the
same map so every verdict stays attached to the answer it judged.

Two properties fall out of that:

  * Nothing is lost. Every sample either keeps its key or gets a fresh one.
  * The old numbers still mean what they meant. `evaluate.py --summary-only
    --rollouts 3` keeps its filter `rollout < 3`, so it reports exactly the
    pre-merge local grid; the extra samples surface only when you ask for more.

Every row is tagged `host`, and shifted rows keep `orig_rollout`, so the merge
is auditable and reversible after the fact.

Usage:
    python3 merge_eval_hosts.py            # merge in place
    python3 merge_eval_hosts.py --dry-run  # report only, write nothing
"""

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).parent

# (answers, judgments, host tag) for the resident host and the incoming one.
LOCAL = (HERE / "eval-reviewed/answers.jsonl", HERE / "eval-reviewed/judgments.jsonl", "local")
OTHER = (HERE / "other-computer-answers.jsonl", HERE / "other-computer-judgments.jsonl", "other")


def load_jsonl(path: Path) -> list[dict]:
    """Same tolerance as evaluate.py: a run killed mid-append leaves a torn line."""
    out = []
    with open(path) as f:
        for n, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                print(f"warning: {path}:{n} is not valid JSON, skipping", file=sys.stderr)
    return out


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def key(r: dict) -> tuple:
    return (r["model"], r["qid"], r["rollout"])


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dry-run", action="store_true", help="report only, write nothing")
    args = p.parse_args()

    (la_path, lj_path, la_host) = LOCAL
    (oa_path, oj_path, oa_host) = OTHER
    local_a, local_j = load_jsonl(la_path), load_jsonl(lj_path)
    other_a, other_j = load_jsonl(oa_path), load_jsonl(oj_path)

    for rows, host in ((local_a, la_host), (local_j, la_host),
                       (other_a, oa_host), (other_j, oa_host)):
        for r in rows:
            r.setdefault("host", host)

    # The shift map: for each (model, qid) both hosts ran, the incoming rollouts
    # start one past the highest resident one. Built from answers alone -- a
    # judgment can only exist for an answer, and the six orphan judgments left
    # over from an interrupted nemotron run are local, so they never shift.
    resident_max: dict[tuple, int] = {}
    for r in local_a:
        mq = (r["model"], r["qid"])
        resident_max[mq] = max(resident_max.get(mq, -1), r["rollout"])

    incoming = {(r["model"], r["qid"]) for r in other_a}
    shift = {mq: resident_max[mq] + 1 for mq in incoming & set(resident_max)}

    shifted_rows = 0
    for rows in (other_a, other_j):
        for r in rows:
            off = shift.get((r["model"], r["qid"]))
            if off:
                r["orig_rollout"] = r["rollout"]
                r["rollout"] += off
                shifted_rows += 1

    merged_a = local_a + other_a
    merged_j = local_j + other_j

    # The renumbering is only worth anything if it actually made the keys unique.
    for label, rows in (("answers", merged_a), ("judgments", merged_j)):
        keys = [key(r) for r in rows]
        if len(keys) != len(set(keys)):
            dup = [k for k, n in Counter(keys).items() if n > 1][:5]
            sys.exit(f"merge produced duplicate {label} keys, e.g. {dup}")

    # Every judgment must still name an answer that exists (orphans excepted).
    answer_keys = {key(r) for r in merged_a}
    orphans = [r for r in merged_j if key(r) not in answer_keys]

    print(f"answers    {len(local_a):6} local + {len(other_a):6} other = {len(merged_a):6}")
    print(f"judgments  {len(local_j):6} local + {len(other_j):6} other = {len(merged_j):6}")
    print(f"\n{len(shift)} (model, qid) pairs run by both hosts; "
          f"{shifted_rows} incoming rows renumbered past the resident ones")
    print(f"{len(orphans)} judgments with no matching answer "
          f"({Counter(r['host'] for r in orphans)})")

    new_models = sorted({r["model"] for r in other_a} - {r["model"] for r in local_a})
    new_qids = {r["qid"] for r in other_a} - {r["qid"] for r in local_a}
    print(f"\nmodels only the other host ran ({len(new_models)}):")
    for m in new_models:
        print(f"  {m}")
    print(f"questions only the other host ran: {len(new_qids)}")

    unjudged = len(answer_keys - {key(r) for r in merged_j})
    print(f"\nanswers still awaiting a verdict: {unjudged} "
          f"(a rerun of evaluate.py picks these up)")

    if args.dry_run:
        print("\n--dry-run: nothing written")
        return

    write_jsonl(la_path, merged_a)
    write_jsonl(lj_path, merged_j)
    print(f"\nwrote {la_path} and {lj_path}")


if __name__ == "__main__":
    main()
