#!/usr/bin/env python3
"""Filter a reviewed collection down to the pairs review.py accepted.

    accepted.py letters_and_history.jsonl [letters_and_history.review.jsonl] \
                [letters_and_history.accepted.jsonl]

Pairs keep their file order; the latest decision per pair wins, matching
review.py's own rule. Pairs marked `fix` are NOT included -- their wording is
still pending -- and are reported separately so they are not silently lost.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def pair_key(pair):
    raw = pair["locus"] + "\x1f" + pair["question"]
    return hashlib.sha1(raw.encode()).hexdigest()[:16]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    qa_path = os.path.join(HERE, args[0])
    review_path = (os.path.join(HERE, args[1]) if len(args) > 1
                   else qa_path.removesuffix(".jsonl") + ".review.jsonl")
    out_path = (os.path.join(HERE, args[2]) if len(args) > 2
                else qa_path.removesuffix(".jsonl") + ".accepted.jsonl")

    with open(qa_path) as f:
        pairs = [json.loads(line) for line in f]
    latest = {}
    with open(review_path) as f:
        for line in f:
            d = json.loads(line)
            latest[d["key"]] = d["decision"]

    kept, undecided, counts = [], 0, {}
    for p in pairs:
        decision = latest.get(pair_key(p))
        if decision is None:
            undecided += 1
            continue
        counts[decision] = counts.get(decision, 0) + 1
        if decision == "accept":
            kept.append(p)

    with open(out_path, "w") as f:
        for p in kept:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    tally = ", ".join(f"{n} {d}" for d, n in sorted(counts.items()))
    print(f"{len(pairs)} pairs reviewed ({tally}"
          + (f", {undecided} with no decision" if undecided else "") + ")")
    print(f"{len(kept)} accepted -> {os.path.basename(out_path)}")
    if counts.get("fix"):
        print(f"note: {counts['fix']} marked `fix` are excluded pending rewording:")
        for p in pairs:
            if latest.get(pair_key(p)) == "fix":
                print(f"  {p['locus']}: {p['question']}")


if __name__ == "__main__":
    main()
