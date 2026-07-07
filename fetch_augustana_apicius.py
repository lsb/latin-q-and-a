#!/usr/bin/env python3
"""Fetch Apicius, De Re Coquinaria books VI-X + the Excerpta a Vinidario.

The Latin Library carries only books I-V of Apicius (its own index page lists
all ten book titles, but only five are linked and the rest 404). LacusCurtius
has Apicius only in English (Vehling) and itself refers readers to the
Bibliotheca Augustana transcription for the Latin. So, as with Pliny NH VII
(LacusCurtius/Teubner), we complete the work from outside the Latin Library
and record the provenance per work:

  provenance: "Bibliotheca Augustana (www.hs-augsburg.de/~harsch), text after
               the Teubner edition (M. E. Milham)"

Writes text/apicius/apicius{6..10}.txt and text/apicius/vinidarius.txt,
normalized to the corpus's plain-text style: pandoc HTML->plain, then strip
the site's table scaffolding, navigation, and letter-spaced display titles,
and strip editorial brackets ([..] deletions, <..> supplements) keeping the
words -- the same rule GUIDELINES.md applies to quoted source_text.

Usage: python3 fetch_augustana_apicius.py   (needs pandoc + network)
"""
import re
import subprocess
import urllib.request

BASE = "https://www.hs-augsburg.de/~harsch/Chronologia/Lspost04/Apicius/"

TARGETS = [
    # (page, output, title lines)
    ("api_re06.html", "text/apicius/apicius6.txt",
     ["DE RE COQUINARIA LIBER SEXTUS M. GAVII APICII", "", "LIBER VI. AEROPETES."]),
    ("api_re07.html", "text/apicius/apicius7.txt",
     ["DE RE COQUINARIA LIBER SEPTIMUS M. GAVII APICII", "", "LIBER VII. POLYTELES."]),
    ("api_re08.html", "text/apicius/apicius8.txt",
     ["DE RE COQUINARIA LIBER OCTAVUS M. GAVII APICII", "", "LIBER VIII. TETRAPUS."]),
    ("api_re09.html", "text/apicius/apicius9.txt",
     ["DE RE COQUINARIA LIBER NONUS M. GAVII APICII", "", "LIBER IX. THALASSA."]),
    ("api_re10.html", "text/apicius/apicius10.txt",
     ["DE RE COQUINARIA LIBER DECIMUS M. GAVII APICII", "", "LIBER X. HALIEUS."]),
    ("api_excv.html", "text/apicius/vinidarius.txt",
     ["APICI EXCERPTA A VINIDARIO VIRO INLUSTRI"]),
]


def letter_spaced(line):
    """True for display lines like 'I n c i p i t' (every token a single char)."""
    toks = line.split()
    return len(toks) >= 3 and all(len(t) == 1 for t in toks)


def clean(plain):
    out = []
    for line in plain.splitlines():
        if re.fullmatch(r"\+[-+]*\+", line.strip()):
            continue  # table borders
        if line.lstrip().startswith("|"):
            line = " ".join(c.strip() for c in line.strip().strip("|").split("|"))
        line = line.strip()
        if "<<<" in line or ">>>" in line or "B  I  B  L  I  O  T  H  E  C  A" in line:
            continue  # site navigation / banner
        if line in ("[]",) or re.fullmatch(r"_{4,}", line):
            continue  # image placeholder / horizontal rule
        if letter_spaced(line):
            continue  # letter-spaced display titles (we prepend our own)
        # editorial brackets: strip the marks, keep the words
        line = re.sub(r"[\[\]‹›⟨⟩<>]", "", line)
        line = re.sub(r"\s{2,}", " ", line).strip()
        out.append(line)
    text = "\n".join(out)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text


def main():
    for page, dest, title in TARGETS:
        html = urllib.request.urlopen(BASE + page).read()
        plain = subprocess.run(
            ["pandoc", "-f", "html", "-t", "plain", "--wrap=none"],
            input=html, capture_output=True, check=True,
        ).stdout.decode("utf-8")
        body = clean(plain)
        with open(dest, "w") as fh:
            fh.write("\n".join(title) + "\n\n" + body + "\n")
        print(f"ok   {dest}  ({len(body)} chars)")


if __name__ == "__main__":
    main()
