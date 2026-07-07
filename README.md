# latin-q-and-a

A dataset of **closed-book, fact-seeking Latin question/answer pairs**, authored
from the [Latin Library](https://www.thelatinlibrary.com/) corpus in the style
of **ECLeKTic** ([arXiv:2502.21228](https://arxiv.org/abs/2502.21228)) — a
benchmark for cross-lingual factual knowledge transfer — and, since June 2026,
of **Global PIQA** ([arXiv:2510.24081](https://arxiv.org/abs/2510.24081)):
**culturally salient** knowledge of the Roman/Latin world, authored natively in
Latin. (See *How the approach has changed*, below.)

Each pair takes a **fact stated in a Latin work** and turns it into a question
whose answer a well-read model should know *without the text in front of it*:

> Source (Caesar, *BG* 1.1): *Gallia est omnis divisa in partes tres…*
> **Q:** *In quot partes Galliam divisam esse Caesar scribit?*
> **A:** *In tres partes.* ("Into how many parts does Caesar say Gaul is divided?" → "Into three parts.")

We **author new Latin** for both the question and the answer, and keep the
verbatim source sentence as evidence. The flat dataset is **`qa.jsonl`** (one
pair per line).

## What this is

We read **factual prose** (Cato, Caesar, Pliny, Tacitus, Suetonius, Justinian,
Augustine, …) and **write** fact-seeking questions about the hard, specific,
entity-anchored facts in them, keeping the verbatim source sentence as evidence.
We do **not** mine the text for questions already in it, and we do **not**
require the question or answer to be verbatim — the *fact*, not the wording, is
what must trace to the source. See **`GUIDELINES.md`** for the full rationale and
the eight acceptance criteria.

## Coverage

The dataset grows one work at a time (one reader per work). `qa.jsonl` is the
authoritative list; `python3 aggregate.py` prints the current per-author tally.
At a high level it spans, across the named authors and their close neighbours:

- **Caesar & the Corpus Caesarianum** — the complete *Gallic War* (books I–VIII,
  book VIII by Hirtius), the complete *Civil War* (I–III), and the *Alexandrian*,
  *African*, and *Spanish* wars.
- **Suetonius** — all of the *Twelve Caesars*, plus the Lives of the poets
  (Virgil, Horace, Terence, Lucan).
- **Tacitus** — all surviving works: *Germania*, *Agricola*, *Histories* I–V,
  *Annals* I–IV, VI, XI–XVI.
- **Pliny** — the Elder's *Naturalis Historia* (cosmology II; geography III–V;
  the inventors/firsts of VII, sourced from LacusCurtius); the Younger's
  *Letters* VI (Vesuvius) and X (the Trajan correspondence).
- **Roman law** — Gaius's *Institutes* (all four books) and Justinian's *Digest*
  (book I and the *regulae iuris* of book L).
- **Augustine** — much of the *Confessions* (I, III–IX) and *City of God* I.
- **Cato** — *De Agri Cultura*.

The **cultural texts** (post-June-2026 targets, landing work by work):
Petronius's *Satyricon*, Apicius's *De Re Coquinaria* (all ten books + the
Vinidarius excerpts), Ovid's *Fasti* / *Metamorphoses* I / *Ars Amatoria*,
Martial (*Xenia*, *Apophoreta*, *De Spectaculis*, then the numbered books),
Catullus, Plautus, Macrobius's *Saturnalia*, and the epigraphic set (epitaphs,
inscriptions, the *SC de Bacchanalibus*, the Twelve Tables).
`python3 aggregate.py` is always the authoritative tally.

Each pair records a `provenance` field; all texts are from the Latin Library
except *NH* VII (LacusCurtius/Teubner), which the Latin Library does not carry.

## Layout

| Path | What it is |
|---|---|
| `GUIDELINES.md` | The rules: the ECLeKTic-style target, the cultural turn, the eight acceptance criteria, the two tracks, the boundary calls, and *why*. Read this first. |
| `author_prompt.md` | The self-contained instruction set given to each per-work authoring subagent. |
| `deep_pass_prompt.md` | A ready-to-paste driver prompt for a fresh Claude agent to run a fuller (deep) pass over the corpus — embeds the reader template. |
| `text/` | Plain text of every work (converted from HTML with pandoc). |
| `factual/` | One JSON file per work: `{ source, author, work, pairs: [{ locus, source_text, question, answer, question_en, answer_en, derivation }] }`. |
| `qa.jsonl` | The aggregated dataset — one pair per line. |
| `aggregate.py`, `convert_to_text.sh` | The reproducible processing steps (below). |

The raw `www.thelatinlibrary.com/` HTML is **not** committed (see `.gitignore`);
re-fetch with `wget -r` to re-run the conversion.

**Provenance.** Almost every work's text is from the Latin Library. The
exceptions — each fetched, normalized to the corpus's plain-text style, and
recorded per work — are:

- **Pliny, *Naturalis Historia* VII** — LacusCurtius (Mayhoff/Teubner).
- **Apicius, *De Re Coquinaria* VI–X + the *Excerpta a Vinidario*** — the
  Latin Library's own index lists all ten books but links only I–V (the rest
  404), and LacusCurtius has Apicius only in English; the Latin is from the
  **Bibliotheca Augustana** transcription (text after Milham's Teubner), via
  `fetch_augustana_apicius.py`.
- **Macrobius, *Saturnalia* I–VII** — not in the Latin Library at all; from
  **LacusCurtius (ed. L. von Jan, 1852)**, via
  `fetch_lacuscurtius_macrobius.py`. (The transmitted text is lacunose: much
  of IV, the end of VII.)

Each pair in `qa.jsonl` carries a `provenance` field (defaulting to the Latin
Library) so the source edition is always explicit; the per-work file under
`factual/` also records it.

## The eight acceptance criteria (summary)

A pair is kept only if **all** hold: **closed-book**, **entity-anchored**,
**verifiable answer**, **decontextualizable**, **short answer**, **translatable**,
**non-rhetorical / fact-seeking**, and (since June 2026) **culturally salient**
— the shared, ambient knowledge of the Roman/Latin world, neither universal to
every culture nor clique-local. Precision over recall — when in doubt, drop it.
The one sanctioned exception: pairs tagged `track: "latin-specific"` waive
*translatable* (and only that) for knowledge that lives in the Latin language
itself — meter, scansion, wordplay. Details and worked examples in
`GUIDELINES.md`.

## How the approach has changed

The repo is version-controlled precisely so the method can move; here is the
history of the method, newest first:

- **June 2026 — the cultural turn** ([issue #2](../../issues/2)). The meeting
  notes concluded "we prob have enough history" and retargeted the dataset
  toward **culture**: food (Apicius, Martial's *Xenia*), festivals and the
  sacred calendar (Ovid's *Fasti*), daily life and its registers (Petronius,
  Plautus, Martial), myth as shared story (Ovid), funerary culture
  (epitaphs, Catullus 101). Concretely: an eighth acceptance criterion
  (**culturally salient**, adapted from the meeting notes and Global PIQA's
  insider-knowledge framing), per-pair **`category`** tags, a small
  **`latin-specific` track** that waives translatability for meter/wordplay
  knowledge (Global PIQA's natively-authored, non-parallel split is the
  precedent), and a pause on new history mining. Pairs authored before the
  turn are retained unchanged and are recognizable by their seven-key schema
  (no `category`/`track`).
- **May–June 2026 — depth passes.** The realization that per-work yield
  reflects mining depth, not the text: deep re-reads against already-taken
  pairs (e.g. *Divus Iulius*, 20 → 100 pairs), `deep_pass_prompt.md`, and the
  no-ceiling "exhaustive within the bar" coverage rule.
- **Spring 2026 — author, don't mine.** The founding decision: read factual
  prose end-to-end and *write* new Latin Q&A about the facts (ECLeKTic-style,
  closed-book, seven criteria), rather than harvesting questions that already
  appear in texts. One reader subagent per work, run serially; verbatim
  `source_text` kept as evidence; precision over recall.

To revise a choice, edit `GUIDELINES.md` + `author_prompt.md` and re-run the
affected works (see *Revisiting our choices*).

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

## Reproducing with Claude

Step 2 (the authoring) is done by **Claude driving one subagent per work**. The
whole dataset was built with Claude Code this way, and the loop is easy to
re-run or extend:

1. **Pick a work** in `text/` that isn't in `factual/` yet, and confirm the file
   exists. (If a target text is missing from the corpus, the reader reports back
   rather than fetching it from elsewhere — see the NH VII note on provenance.)
2. **Spawn one reader subagent** (serially — never in parallel). Give it a prompt
   that: (a) tells it to read `author_prompt.md` and `GUIDELINES.md` in full;
   (b) points it at the single target file and an existing `factual/*.json` as a
   worked example; (c) names the specific facts worth hunting in that work (this
   focusing helps a lot); and (d) tells it to write valid JSON to
   `factual/<name>.json` with exactly the eight per-pair keys and reply with a
   one-paragraph summary (not the JSON — keep the big text out of the transcript).
3. **Validate** the returned file: it parses, every pair has exactly the eight
   keys (seven pre-turn keys + `category`; `track` only on latin-specific runs),
   every question ends in `?`, answers are short. Spot-check a few facts
   and the Latin (indirect question → subjunctive; indirect statement → acc.+inf.).
4. **Aggregate and check** — `python3 aggregate.py`, then confirm no duplicate
   questions across the whole set.
5. **Commit** that one work to the branch and move to the next.

Notes that made the runs clean:
- **One work at a time.** Serial keeps each reading focused and the run steerable.
- **Precision is the quality gate, not a cap.** Drop doubtful/soft pairs, but keep
  *every* fact that clears the eight criteria — no target ceiling, no
  "famous-only" filter (see `author_prompt.md` → *Coverage: exhaustive within the
  bar*). A sparse or theological work may still yield only a handful, and that's
  fine.
- **Name the target facts.** A reader told "hunt the birthplace, the offices, the
  named battle, the death" outperforms an open-ended "find facts."
- **Let the reader drop what the text doesn't support.** Good readers refuse to
  assert a fact that isn't in *their* work (e.g. a name that only appears in a
  later book), and flag OCR slips / editorial brackets in the quoted `source_text`.

### Depth: a first pass is a floor, not a ceiling

Per-work yield reflects **how hard we mine**, not the text. A quick first pass
under-mines a rich work; a **deep pass** — cap removed, keeping the
verifiable-but-less-celebrated facts too — finds many more, all clearing the same
bar. (Worked example: Suetonius's *Divus Iulius* gave **20** pairs on a first
pass and **80 more** on a deep re-read — 100 in all.)

To **deepen an already-covered work**, run a second reader that additionally:
- reads the work's existing `factual/<name>.json` and is told **not to duplicate**
  those facts/questions — it authors only *new* pairs;
- writes just the new pairs (e.g. to a scratch file) so the original pairs are
  merged back untouched; then dedup by question across the whole set and commit.

Because coverage depth is a knob, `factual/*.json` files are at *different*
depths: some works have had only a first pass and can still be deepened; a few
(e.g. *Divus Iulius*) have had a deep pass. `qa.jsonl` + `aggregate.py` remain
the authoritative record of what exists.

## Revisiting our choices

The interesting decisions live in **`GUIDELINES.md`** (mirrored in
`author_prompt.md`): author-not-mine, the eight criteria, fact-over-theory,
culture-over-more-history (since issue #2),
keep-the-verbatim-evidence, write-correct-Latin, precision over recall,
read-don't-grep, serial single-subagent runs.

To revise a choice: edit `GUIDELINES.md` + `author_prompt.md`, delete the
affected `factual/*.json`, and re-run step 2 on those works. The per-work design
means you can redo one work without touching the rest.
