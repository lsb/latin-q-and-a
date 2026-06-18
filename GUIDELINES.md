# Q&A Extraction Guidelines

Principles for extracting question/answer pairs from the Latin Library corpus
(plain text under `text/`). These are working rules; boundaries are often
debatable, so we record *why* each pair was drawn the way it was.

## Core principles

1. **Invent no new Latin.** The constraint is on *words*: every Latin word in a
   question or answer must be the author's own, unaltered, unreordered, with no
   spelling changes and no macrons added. We never compose, paraphrase, or
   translate. What we *may* do, in service of a clean standalone pair, is
   **editorial presentation**, which adds no Latin:
   - **Drop framing/narration.** Remove speech tags and meta-narration of the
     asking/speaking — `inquit`, `dehinc talia fatur`, `adloquitur Venus`, and
     also `fortasse requiris` ("perhaps you ask"). These are dropped *even though
     they are the author's own words*, because they narrate the exchange rather
     than belonging to the utterance. Dropping words is fine; inserting is not.
   - **Keep the utterance contiguous.** Within the chosen span, quote the
     speaker's own words contiguously. Do **not** ellipt content with `...` or
     stitch together non-adjacent fragments — that is editorial selection, and it
     is how false pairs get manufactured. (We omit only framing, as above.)
   - **Normalize capitalization** of the excerpt's first word, and
   - **Normalize terminal punctuation** — e.g. set a `?` on a question even when
     the edition didn't, and drop now-dangling internal commas.

   Test: read the question and answer back as Latin. If every word traces to the
   source unchanged, it passes — regardless of caps/punctuation. If any word was
   added, altered, or moved, it fails.

2. **Self-contained context.** The pair must make sense read on its own, with no
   access to the surrounding text. A bare interrogative plus a bare reply is
   usually useless; pull in the setup that makes the exchange intelligible.
   - Bad:  Q: *Quare id faciam?* / A: *Nescio.*
   - Good: Q: *Odi et amo. Quare id faciam?* / A: *Nescio sed fieri sentio et excrucior.*
   The included setup (*Odi et amo*) is still verbatim source text — we are
   choosing a wider excerpt window, not adding words.

3. **Document provenance.** Because where a pair begins and ends is a judgment
   call, every pair records its source location and a short rationale for the
   boundaries chosen. Another reader should be able to see the seam and disagree.

4. **Prefer false negatives to false positives.** Precision over recall. When a
   candidate pair is doubtful — unclear boundaries, missing context, uncertain
   speaker, garbled text — *drop it*. A missed question costs us nothing; a
   broken or incoherent pair pollutes the dataset. When in doubt, leave it out.
   In particular, **do not manufacture a pair** from declarative text: emphatic
   repetition or a statement-and-echo (e.g. *Mentula moechatur. Moechatur mentula
   certe.*) is not a question, and reordering or recombining words to make one
   read as Q&A is forbidden. There must be a genuine question and a genuine
   answer actually present in the text.

   **The `question` must be a real interrogative.** In dramatic dialogue
   especially, a *statement answered by a retort* — capping sententiae and
   stichomythic point/counterpoint — is a dialogue exchange but NOT a
   question/answer pair. Drop it. Examples to reject:
   - *Rex est timendus.* / *Rex meus fuerat pater.* (statement + retort)
   - *Ingrata uita est cuius acceptae pudet.* / *Retinenda non est…* (sententia
     capped by counter-sententia)
   A pair qualifies only when one party genuinely **asks** (an interrogative —
   *quis? quid? cur? num? nonne? -ne?* or a clear question) and the other
   **answers** it. Do not relabel a declarative as an "implicit question."

5. **Extract by reading, not by pattern-matching.** Deciding what is a
   question/answer pair — who is speaking, where the question's context begins,
   where the direct answer stops and digression starts — requires actually
   *understanding* the Latin. This is reading work, done by a model (the main
   agent, or delegated to Claude subagents, one per file/work), not by
   `grep`/regex over interrogatives and `?`. Run subagents **serially — one at a
   time, no parallelism** — so each reading gets full attention and the run stays
   easy to follow and steer. Mechanical tools are fine for
   *triage and navigation* — listing files, narrowing to passages with speech
   verbs, spot-checking — but never for the extraction decision itself. A regex
   that keys on `?` both misses whole-speech-as-question pairs and fires on
   incidental questions with no real answer; only comprehension separates them.

## Where pairs come from (sources of Q&A)

In this corpus, question/answer structure shows up in a few recurring shapes.
List is open; add types as we find them.

- **Direct-speech exchange.** One character asks, another answers. Detected by
  verbs of speaking around the quotation (*inquit, ait, respondit, fatur,
  adloquitur, requiris…*) and by `?`/interrogatives (*quid, cur, quare, quem,
  num, quae…*). This is the main source.
- **Whole-speech-as-question.** A speech may be one extended question/plea even
  if only part of it carries a literal `?`. We may treat the entire speech as
  "the question" and the responding speech (or its operative first sentence) as
  "the answer." (See Aeneid example.)
- **Authorial rhetorical question.** The poet poses a question and answers it
  himself, sometimes via an imagined interlocutor (*fortasse requiris*). (See
  Catullus example.)

## Granularity & boundaries (the debatable part)

- **Question window.** May be a single interrogative sentence *or* an entire
  interrogative speech. Choose the smallest window that is still self-contained,
  then record the choice. **When the type is whole-speech-as-question, include
  the *entire* speech, verbatim and contiguous** — do not trim it down to its
  "operative" interrogative sentences and do not ellipt the interior with `...`.
  (Answer-side trimming below still applies; the trimming happens on the answer,
  not the question.)
- **Answer window.** The answer must *actually answer the question* — this is
  the test, not sentence position. Default to the direct response and stop where
  the speaker shifts from answering to elaborating/digressing; the reply's first
  sentence (to the first full stop — not the first colon/semicolon, which these
  editions use heavily) is a good first approximation for the *end* of the window.
  - **Skip a non-answering preamble.** If the reply opens with a preamble or
    deflection that does not answer (e.g. Aeneas's *O dea, si prima repetens… 
    componat Vesper Olympo* — "the tale's too long to tell"), advance the answer's
    *start* to the operative answering sentence(s), e.g. *Sum pius Aeneas… Italiam
    quaero patriam*. The answer window is a contiguous sub-span of the reply; it
    need not begin at the reply's first word. (Still no interior `...` ellipsis.)
  - If no clean, contiguous answering span can be isolated, **drop the pair** —
    an "answer" that doesn't answer is a false positive.
- **Mark the seam.** When we cut an answer short of where the speech continues,
  note what comes next so the cut is auditable.

## Normalization (what we strip vs. keep)

- **Strip** editorial scaffolding that is not authorial text: section markers
  like `[1]`, internal navigation number-runs, page title lines, inline
  every-5-lines verse numbers left mid-line by conversion (e.g. a stray `225`),
  and the trailing `Author The Latin Library The Classics Page` footer.
- **Keep** the author's words, unaltered and in the author's order — no spelling
  changes, no macrons.
- **Editorial supplements** appear in angle brackets `<...>` (e.g. `<Est> in
  cistula`, `f<ui>sse`) — conjectural words/letters supplied by the edition.
  Policy: **strip the brackets, keep the words** (→ `Est in cistula`, `fuisse`),
  for clean reading text. Keep the words (dropping them breaks the grammar); just
  remove the `< >` marks. A deterministic post-pass enforces this uniformly over
  the whole dataset, so it does not depend on each agent getting it right.
- **May normalize** capitalization of the first word and terminal punctuation so
  the excerpt reads as a clean standalone question/answer (see principle 1).
  This is presentation only; it never adds, changes, or reorders a Latin word.

## Record schema (per pair)

```
source     text/<path>.txt           # the converted file
locus      human citation            # e.g. "Catullus 85"; "Aeneid 1.229-260"
type       direct-speech | whole-speech-as-question | authorial-rhetorical | ...
question   "<verbatim Latin>"
answer     "<verbatim Latin>"
derivation short note on why these boundaries; what was cut and what follows
```

## Worked examples

### Catullus 85 — authorial rhetorical question
- **question:** `Odi et amo. Quare id faciam?`
- **answer:** `Nescio sed fieri sentio et excrucior.`
- **derivation:** The poet's question to himself, surfaced by the interlocutor's
  *fortasse requiris*. We prepend *Odi et amo* (verbatim) so *id* has a referent,
  take the indirect *quare id faciam* as the question (capitalized, with a `?`
  set), and **drop the framing *fortasse requiris*** — it narrates the asking,
  not the question itself. Answer is the whole remaining clause, *fortasse
  requiris* and the comma after *nescio* removed.

### Aeneid 1.229–296 — whole-speech-as-question
- **question:** all of Venus's speech (1.229–253), `O qui res hominumque deumque
  … Hic pietatis honos? Sic nos in sceptra reponis?`
- **answer:** Jupiter's opening reassurance, `Parce metu, Cytherea … neque me
  sententia vertit.` (1.257–260)
- **derivation:** Venus's speech is one extended plea/question; Jupiter's reply
  answers it. We cut the answer at *neque me sententia vertit* — the end of the
  direct reassurance — because immediately after he announces he will go further
  and unroll the deeper secrets of fate (*longius et volvens fatorum arcana
  movebo*), which is prophecy/elaboration rather than answer.
