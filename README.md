# latin-q-and-a

A dataset of **closed-book, fact-seeking Latin question/answer pairs**, authored
from the [Latin Library](https://www.thelatinlibrary.com/) corpus in the style
of **ECLeKTic** ([arXiv:2502.21228](https://arxiv.org/abs/2502.21228)) — a
benchmark for cross-lingual factual knowledge transfer.

Each pair takes a **fact stated in a Latin work** and turns it into a question
whose answer a well-read model should know *without the text in front of it*:

> Source (Caesar, *BG* 1.1): *Gallia est omnis divisa in partes tres…*
> **Q:** *In quot partes Galliam divisam esse Caesar scribit?*
> **A:** *In tres partes.* ("Into how many parts does Caesar say Gaul is divided?" → "Into three parts.")

We **author new Latin** for both the question and the answer, and keep the
verbatim source sentence as evidence. The mined dataset is **`qa.jsonl`** (one
pair per line).

## What this is (and what it used to be)

This project was retargeted. It previously *mined* existing question structure
out of the texts (direct speech, rhetorical questions) under a strict "invent no
new Latin" rule. That produced ~3,700 pairs but almost none were factual,
closed-book, short-answer questions — the texts simply don't contain many. The
old artifacts were removed in a delete-commit; they remain in git history.

Now we read **factual prose** (Cato, Caesar, Pliny, Tacitus, Suetonius,
Justinian, Augustine, …) and **write** fact-seeking questions about the hard,
specific, entity-anchored facts in them. See **`GUIDELINES.md`** for the full
rationale and the seven acceptance criteria.

## Layout

| Path | What it is |
|---|---|
| `GUIDELINES.md` | The rules: the ECLeKTic-style target, the seven acceptance criteria, the boundary calls, and *why*. Read this first. |
| `author_prompt.md` | The self-contained instruction set given to each per-work authoring subagent. |
| `text/` | Plain text of every work (converted from HTML with pandoc). |
| `factual/` | One JSON file per work: `{ source, author, work, pairs: [{ locus, source_text, question, answer, question_en, answer_en, derivation }] }`. |
| `qa.jsonl` | The aggregated dataset — one pair per line. |
| `aggregate.py`, `convert_to_text.sh` | The reproducible processing steps (below). |

The raw `www.thelatinlibrary.com/` HTML is **not** committed (see `.gitignore`);
re-fetch with `wget -r` to re-run the conversion.

**Provenance.** Almost every work's text is from the Latin Library. The one
exception is **Pliny, *Naturalis Historia* VII**, which the Latin Library does
not carry: its text was fetched from **LacusCurtius (Mayhoff/Teubner edition)**
and normalized to the corpus's plain-text style. Each pair in `qa.jsonl` carries
a `provenance` field (defaulting to the Latin Library) so the source edition is
always explicit; the per-work file under `factual/` also records it.

## The seven acceptance criteria (summary)

A pair is kept only if **all** hold: **closed-book**, **entity-anchored**,
**verifiable answer**, **decontextualizable**, **short answer**, **translatable**,
**non-rhetorical / fact-seeking**. Precision over recall — when in doubt, drop it.
Details and worked examples in `GUIDELINES.md`.

## Pipeline

1. **HTML → text** — `bash convert_to_text.sh` (pandoc; needs the raw
   `www.thelatinlibrary.com/` dir present).
2. **Author Q&A** — model-driven, *not* a script. One subagent reads one factual
   work end-to-end following `author_prompt.md` and writes `factual/<name>.json`.
   Run subagents **serially — one at a time, no parallelism** — so each reading
   gets full attention. "Done" is keyed off the `source` field inside each
   `factual/*.json`, so an interrupted run just resumes.
3. **Aggregate** — `python3 aggregate.py` → writes `qa.jsonl` (flattens
   `factual/*.json` to one pair per line) and prints summary stats.

## Revisiting our choices

The interesting decisions live in **`GUIDELINES.md`** (mirrored in
`author_prompt.md`): author-not-mine, the seven criteria, fact-over-theory,
keep-the-verbatim-evidence, write-correct-Latin, precision over recall,
read-don't-grep, serial single-subagent runs.

To revise a choice: edit `GUIDELINES.md` + `author_prompt.md`, delete the
affected `factual/*.json`, and re-run step 2 on those works. The per-work design
means you can redo one work without touching the rest.
