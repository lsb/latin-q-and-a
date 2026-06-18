#!/usr/bin/env python3
"""Print (as a JSON array) the content files not yet extracted, for resumable
runs. "Done" is determined by the `source` field inside any dataset/*.json, so
it is independent of output-file naming. Also writes remaining.json for
inspection/recovery.
"""
import glob
import json

BASE = "/Users/lsb/latin-q-and-a"

done = set()
for f in glob.glob(f"{BASE}/dataset/*.json"):
    try:
        src = json.load(open(f)).get("source")
        if src:
            done.add(src)
    except Exception:
        pass

remaining = [
    l.strip()
    for l in open(f"{BASE}/content_files.txt")
    if l.strip() and l.strip() not in done
]

with open(f"{BASE}/remaining.json", "w") as fh:
    json.dump(remaining, fh)

print(json.dumps(remaining))
