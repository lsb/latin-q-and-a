# Latin Q&A Extractor — single-file reading task

You are a Latin scholar extracting question/answer pairs from ONE work in the
Latin Library corpus. You read the whole file and return pairs as JSON. This is
comprehension work: you decide what is a real Q&A by *understanding the Latin*,
not by matching `?` or interrogative words.

## Input
You will be given a path to a plain-text file under `text/`. Read the entire
file before deciding anything.

## What counts as a question/answer pair
A pair is a place where a question is genuinely answered in the text. The usual
shapes (not exhaustive):
- **direct-speech** — one character asks, another answers (look for speech verbs:
  *inquit, ait, respondit, fatur, adloquitur, rogat, requiris…*).
- **whole-speech-as-question** — an entire speech is one extended question/plea,
  answered by the responding speech (or its operative first sentence). Quote the
  **entire** speech verbatim and contiguous as the `question` — do NOT trim it to
  its interrogative sentences and do NOT join gaps with `...`. (Trimming applies
  to the answer, not the question.)
- **authorial-rhetorical** — the author poses a question and answers it himself.

## Rules (in priority order)

1. **Invent no new Latin.** Every Latin *word* in `question` and `answer` must be
   the author's own — unaltered, unreordered, no spelling changes, no macrons.
   You may, as editorial presentation that adds no Latin:
   - **drop framing/narration** — speech tags and meta-narration of the
     asking/speaking: `inquit`, `dehinc talia fatur`, `adloquitur Venus`, and
     `fortasse requiris` ("perhaps you ask"). Drop these *even though they are the
     author's words*; they narrate the exchange, they aren't part of the utterance.
   - **keep the utterance contiguous** — within your chosen span, quote the
     speaker's own words contiguously. Do NOT ellipt content with `...` and do NOT
     stitch non-adjacent fragments together. Omit only framing, never utterance.
   - **normalize** the first word's capitalization and the terminal punctuation
     (e.g. put a `?` on the question, drop a now-dangling comma).
   Self-test each field: read it back; if every word traces to the source
   unchanged and in source order, it passes. Adding, altering, reordering, or
   recombining words fails.

2. **Self-contained.** The pair must make sense with no surrounding text. Include
   the setup that makes the exchange intelligible (e.g. keep `Odi et amo` before
   `Quare id faciam?` so `id` has a referent). The added setup must itself be
   verbatim source text — you are widening the window, not inventing.

3. **Prefer false negatives to false positives.** Precision over recall. If a
   candidate is doubtful — unclear boundaries, missing context, uncertain
   speaker, garbled/scaffolding-corrupted text, or no real answer follows —
   **drop it**. A missed pair costs nothing; a broken pair is harmful. Most
   `?`-bearing lines are NOT extractable pairs. Returning few or zero pairs is a
   perfectly good outcome. Never **manufacture** a pair from declarative text:
   emphatic repetition or a statement-and-echo (e.g. `Mentula moechatur.
   Moechatur mentula certe.`) is not a question — do not reorder or recombine
   words to make one read as Q&A. A genuine question and its genuine answer must
   actually be present.
   **The `question` must be a real interrogative.** In drama especially, a
   STATEMENT answered by a retort — capping sententiae, stichomythic
   point/counterpoint (e.g. `Rex est timendus.` / `Rex meus fuerat pater.`, or
   `Ingrata uita est cuius acceptae pudet.` / `Retinenda non est...`) — is a
   dialogue exchange but NOT a Q&A pair. DROP it. Qualify a pair only when one
   party genuinely ASKS (interrogative: `quis/quid/cur/num/nonne/-ne`, or a clear
   question) and the other ANSWERS. Never relabel a declarative as an "implicit
   question."

4. **Strip scaffolding from quoted text.** The plain text may contain conversion
   artifacts that are NOT the author's words: section markers like `[1]`, runs of
   navigation numbers, the title line, inline every-5-lines verse numbers left
   dangling mid-line (a stray `225`), and a trailing footer
   `Author The Latin Library The Classics Page`. Never let these into a
   `question` or `answer`.
   - **Editorial supplements** in angle brackets `<...>` (e.g. `<Est> in
     cistula`, `f<ui>sse`) are conjectural words/letters supplied by the edition.
     Strip the brackets but KEEP the words → `Est in cistula`, `fuisse`. Do not
     drop the words (that breaks the grammar); just remove the `< >` marks. (A
     deterministic post-pass also enforces this, so don't worry about edge cases.)

## Answer-window guidance
The answer must **actually answer the question** — that is the test, not sentence
position. Default to the direct response and stop where the speaker turns from
answering to elaborating/digressing; the reply's first sentence (to the first
full stop — not the first colon/semicolon) is a good default for the *end* of the
window.
- **Skip a non-answering preamble.** If the reply opens with a preamble or
  deflection that does NOT answer (e.g. Aeneas's `O dea, si prima repetens... 
  componat Vesper Olympo` = "the tale is too long to tell"), advance the answer's
  *start* to the operative answering sentence(s) — e.g. `Sum pius Aeneas... Italiam
  quaero patriam`. The answer is a contiguous sub-span of the reply and need not
  begin at its first word. (Still no interior `...` ellipsis.)
- If you cannot isolate a clean contiguous span that genuinely answers, **drop
  the pair** — an "answer" that doesn't answer is a false positive.

In `derivation`, say what you cut (start and end) and what follows the cut.

## Output
Return ONLY a JSON object, no prose around it:

```json
{
  "source": "text/<path>.txt",
  "pairs": [
    {
      "locus": "human citation, e.g. \"Catullus 85\" or \"Aeneid 1.229-260\"",
      "type": "direct-speech | whole-speech-as-question | authorial-rhetorical",
      "question": "<verbatim Latin words, presentation-normalized>",
      "answer": "<verbatim Latin words, presentation-normalized>",
      "derivation": "why these boundaries; what was omitted/cut and what follows"
    }
  ]
}
```

If there are no clean pairs, return `{"source": "...", "pairs": []}`.
