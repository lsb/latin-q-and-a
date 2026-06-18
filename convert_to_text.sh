#!/usr/bin/env bash
# Convert all Latin Library HTML/SHTML files to plain text using pandoc.
# Mirrors the source directory tree into ./text/ with .txt extension.
set -euo pipefail

SRC="/Users/lsb/latin-q-and-a/www.thelatinlibrary.com"
OUT="/Users/lsb/latin-q-and-a/text"

mkdir -p "$OUT"

export SRC OUT

convert_one() {
  local f="$1"
  local rel="${f#"$SRC"/}"          # path relative to SRC
  local dst="$OUT/${rel%.*}.txt"    # swap extension for .txt
  mkdir -p "$(dirname "$dst")"
  if pandoc -f html -t plain --wrap=none "$f" -o "$dst" 2>/dev/null; then
    echo "ok   $rel"
  else
    echo "FAIL $rel" >&2
  fi
}
export -f convert_one

# Find all HTML-ish files (.html, .shtml, .htm) and convert in parallel.
find "$SRC" -type f \( -name '*.html' -o -name '*.shtml' -o -name '*.htm' \) -print0 \
  | xargs -0 -P 8 -I{} bash -c 'convert_one "$@"' _ {}
