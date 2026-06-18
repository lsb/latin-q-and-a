#!/usr/bin/env python3
"""Classify Latin Library pages as content vs. index/TOC, writing the list of
content text-files to content_files.txt.

Signal (robust to the corpus's unclosed <a name> section anchors):
  - outbound_links = count of href="...html/.shtml/.htm" (not #fragments, not
    css/ico). Content pages carry only the ~3 footer links; index pages link to
    many works.
  - A page is CONTENT if (outbound_links <= 4) OR (it has a long prose line,
    longest text line >= 200 chars). The prose-line clause rescues multi-part
    works that carry a few extra nav links; the link clause rescues short poems
    that have only the footer. Skip only when a page has many links AND no prose.

Usage: python3 classify_content.py            (writes content_files.txt)
"""
import os
import re
import glob

ROOT = "www.thelatinlibrary.com"
HREF = re.compile(r'href="([^"]*)"', re.I)


def outbound_links(html_path: str) -> int:
    t = open(html_path, errors="replace").read()
    n = 0
    for m in HREF.finditer(t):
        u = m.group(1)
        if u.startswith("#"):
            continue
        if re.search(r"\.(css|ico)($|[#?])", u, re.I):
            continue
        if re.search(r"\.(s?html|htm)($|[#?])", u, re.I):
            n += 1
    return n


def longest_line(txt_path: str) -> int:
    return max((len(l) for l in open(txt_path, errors="replace").read().splitlines()), default=0)


def main():
    htmls = (
        glob.glob(ROOT + "/**/*.shtml", recursive=True)
        + glob.glob(ROOT + "/**/*.html", recursive=True)
        + glob.glob(ROOT + "/**/*.htm", recursive=True)
    )
    content, skip = [], []
    for f in htmls:
        rel = f[len(ROOT) + 1:]
        tp = "text/" + re.sub(r"\.(s?html|htm)$", ".txt", rel)
        if not os.path.exists(tp):
            continue
        if outbound_links(f) <= 4 or longest_line(tp) >= 200:
            content.append(tp)
        else:
            skip.append(tp)
    content.sort()
    with open("content_files.txt", "w") as fh:
        fh.write("\n".join(content) + "\n")
    print(f"content: {len(content)}  skip(index): {len(skip)}  -> content_files.txt")


if __name__ == "__main__":
    main()
