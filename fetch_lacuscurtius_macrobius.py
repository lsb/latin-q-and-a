#!/usr/bin/env python3
"""Fetch Macrobius, Saturnalia I-VII (Latin) from LacusCurtius.

The Latin Library does not carry Macrobius at all, and the Saturnalia is a
first-rank cultural source (the Saturnalia itself, the Roman calendar and
festivals, banquet lore) -- squarely what the June 2026 cultural turn
(issue #2) targets. As with Pliny NH VII, we take the text from LacusCurtius
and record the provenance per work:

  provenance: "LacusCurtius (penelope.uchicago.edu), ed. L. von Jan (1852)"

The transmitted text is incomplete (much of book IV, the end of book VII);
readers must not paper over the gaps.

Writes text/macrobius/sat{1..7}.txt, normalized to the corpus's plain-text
style: pandoc HTML->plain, then keep only the body between the "Macrobii
Saturnalia" title and the site footer, dropping navigation tables, image ALT
lines, and Thayer's embedded page numbers (p3, p4, ...).

Usage: python3 fetch_lacuscurtius_macrobius.py   (needs pandoc + network)
"""
import os
import re
import subprocess
import urllib.request

BASE = "https://penelope.uchicago.edu/Thayer/L/Roman/Texts/Macrobius/Saturnalia/"
ORDINALS = ["PRIMUS", "SECUNDUS", "TERTIUS", "QUARTUS", "QUINTUS", "SEXTUS", "SEPTIMUS"]


def clean(plain, book):
    lines = plain.splitlines()
    # body starts at the "Macrobii Saturnalia" title and ends at the site
    # footer ("Images with borders lead to more information")
    start = next(i for i, l in enumerate(lines) if l.strip().startswith("Macrobii"))
    end = next((i for i, l in enumerate(lines) if "Images with borders" in l), len(lines))
    body = []
    for line in lines[start:end]:
        if re.fullmatch(r"\+[-+]*\+", line.strip()):
            continue  # table borders (verse quotations are rendered as tables)
        if line.lstrip().startswith("|"):
            line = " ".join(c.strip() for c in line.strip().strip("|").split("|"))
        line = re.sub(r"\[\s*\[[^\]]*\]\s*\]", "", line)      # [ [image ALT] ]
        line = " ".join(t for t in line.split() if not re.fullmatch(r"p\d+", t))
        body.append(line.strip())
    text = "\n".join(body)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    # replace the bare title with a Latin-Library-style header
    text = re.sub(r"^Macrobii Saturnalia\s*\n+Liber [IVX]+",
                  f"MACROBII SATURNALIA LIBER {ORDINALS[book - 1]}", text)
    return text


def main():
    os.makedirs("text/macrobius", exist_ok=True)
    for book in range(1, 8):
        html = urllib.request.urlopen(f"{BASE}{book}*.html").read()
        plain = subprocess.run(
            ["pandoc", "-f", "html", "-t", "plain", "--wrap=none"],
            input=html, capture_output=True, check=True,
        ).stdout.decode("utf-8")
        body = clean(plain, book)
        dest = f"text/macrobius/sat{book}.txt"
        with open(dest, "w") as fh:
            fh.write(body + "\n")
        print(f"ok   {dest}  ({len(body)} chars)")


if __name__ == "__main__":
    main()
