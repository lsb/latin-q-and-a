# latin-q-and-a

Question/answer pairs excerpted from Latin texts (the
[Latin Library](https://www.thelatinlibrary.com/) corpus).

Each pair is **verbatim Latin** lifted from a source work — a real question and
the passage that answers it (a character's reply, a self-answered rhetorical
question, a whole speech answered by another). We invent no new Latin; we only
choose excerpt windows and lightly normalize presentation. Extraction is done by
reading and understanding the Latin (Claude subagents, one per work), not by
pattern-matching `?`.

## Layout

| Path | What it is |
|---|---|
| `GUIDELINES.md` | The rules: what counts as a pair, the boundary calls, and *why*. Read this first. |
| `extractor_prompt.md` | The self-contained instruction set given to each per-file reader. |
| `text/` | Plain-text of every work (converted from HTML with pandoc). |
| `dataset/` | One JSON file per work: `{ source, pairs: [{ locus, type, question, answer, derivation }] }`. |
| `content_files.txt` | The list of `text/` files that are actual works (index/TOC pages excluded). |
| `*.py`, `*.sh` | The reproducible processing steps (below). |

The raw `www.thelatinlibrary.com/` HTML is **not** committed (see `.gitignore`);
re-fetch it with `wget -r` if you need to re-run the conversion step.

## Re-running the pipeline

1. **HTML → text** — `bash convert_to_text.sh`
   (pandoc; needs the raw `www.thelatinlibrary.com/` dir present).
2. **Pick the works to process** — `python3 classify_content.py`
   → rewrites `content_files.txt` (keeps works, drops author index/TOC pages;
   the heuristic is documented in the script).
3. **Extract Q&A** — model-driven, *not* a script. One subagent reads one work
   end-to-end following `extractor_prompt.md` and writes `dataset/<name>.json`.
   We ran this as a sequential Claude Code workflow, one file at a time.
   - `python3 compute_remaining.py` prints the files not yet done (resume-safe —
     "done" is keyed off the `source` field inside each `dataset/*.json`), so an
     interrupted run just continues where it left off.
4. **Normalize** — `python3 normalize_dataset.py`
   (deterministic post-pass; currently strips editorial `<...>` supplements).

## Revisiting our choices

The interesting decisions all live in **`GUIDELINES.md`** (and are mirrored in
`extractor_prompt.md`): excerpt-never-invent, self-contained context, precision
over recall, read-don't-grep, the question must be a real interrogative,
whole-speech-as-question kept in full, the answer must actually answer (skip
non-answering preambles), and strip-vs-keep for editorial brackets.

To revise a choice: edit `GUIDELINES.md` + `extractor_prompt.md`, then re-run
step 3 on the affected works (delete their `dataset/*.json` first so
`compute_remaining.py` re-queues them). The per-file design means you can re-do a
single work without touching the rest.
