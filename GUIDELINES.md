# Factual Q&A Authoring Guidelines (ECLeKTic-style)

How we build a dataset of **closed-book, fact-seeking question/answer pairs**
from the Latin Library corpus (plain text under `text/`), in the spirit of
**ECLeKTic** ([arXiv:2502.21228](https://arxiv.org/abs/2502.21228)).

These are working rules; the boundaries are debatable, so every pair records the
verbatim source it rests on and *why* it was drawn the way it was.

## What we do (and don't)

We **author** questions; we do not merely *find* them. We read **factual prose**
— geography, ethnography, biography, history, law, agronomy — and for each clean
fact we **write a new Latin question** whose answer is that fact, keeping the
verbatim source sentence as evidence so every pair is auditable.

The canonical shape:

> Source (Caesar): *Gallia est omnis divisa in partes tres…*
> **Q (new Latin):** *In quot partes Galliam divisam esse Caesar scribit?*
> **A (new Latin):** *In tres partes.*

What anchors a pair to the text is not word-for-word reuse but the **fact** and
its recorded **evidence**. So, concretely, we do **not**:

- **mine the text for questions already in it** (direct-speech exchanges,
  rhetorical questions) — those are overwhelmingly dialogue retorts, pleas, and
  theory, not fact-seeking questions with a single verifiable answer;
- **require the question or answer to be verbatim** — we compose new, correct
  Latin for both (the *fact*, not the wording, must trace to the source);
- **chase theory, doctrine, or opinion** — humours, virtue, the will of the
  gods; we want who/how-many/where/when facts (see the bar below).

## What we keep per pair

Three things, always, all in Latin, plus English glosses:

1. **`source_text`** — the verbatim Latin sentence(s) from the work that state
   the fact. Unaltered, in the author's order. This is the evidence; it grounds
   the answer and lets a reviewer check the pair without the whole work.
2. **`question`** — a **newly authored** Latin question. Correct, idiomatic
   Latin. It must satisfy all the acceptance criteria below.
3. **`answer`** — a **newly authored** short Latin answer to the question. As
   short as is natural — a name, a number, a place, a short phrase.

Plus `question_en` / `answer_en` (English glosses, for cross-lingual seeding and
review) and a `derivation` note.

## The acceptance bar — the seven criteria

ECLeKTic is about *closed-book cross-lingual factual recall*. A pair is only
worth keeping if a well-read model — one that learned this content in **any**
language, without the text in front of it — could answer it. Every kept pair
must satisfy **all seven**:

1. **Closed-book.** Answerable from knowledge of the content, *not* by needing
   this specific passage open. "Quid in hoc capitulo dicitur?" fails. The fact
   must be the kind of thing a reader of Caesar/Pliny/Tacitus would *know*.
2. **Entity-anchored.** The question pins down its subject with named entities
   (people, peoples, places, works, offices) so it has one referent. "Quot
   filios habuit?" fails — *who?* "Quot liberos Augustus ex Scribonia
   suscepit?" anchors it.
3. **Verifiable answer.** One correct, checkable answer, supported by the
   `source_text`. No "it depends," no list-of-many-where-any-would-do, no
   interpretation.
4. **Decontextualizable.** The question reads as a standalone trivia question.
   No "ut supra," no "in hac epistula," no pronoun whose referent is offstage.
5. **Short answer.** The answer is a short factual span — a name, number, date,
   place, or brief noun phrase. If the only honest answer is a sentence of
   explanation, it is not a short-answer fact; drop it.
6. **Translatable.** The question and answer survive translation into other
   languages without turning on a Latin pun, meter, grammatical form, or
   untranslatable wordplay. (Grammar/metre trivia about the Latin *as language*
   fails this.)
7. **Non-rhetorical / fact-seeking.** A genuine information question with a real
   answer, not a rhetorical flourish, a moral, an exhortation, or an opinion.

If any one fails, **drop the pair.**

## What makes a *good* fact (and what to avoid)

Hunt for **hard, specific, checkable facts** anchored to named entities:

- **Numbers & measures** — *in partes tres*; troop strengths, distances
  (*milia passuum CCXL*), prices, dates, lengths of reign, counts.
- **Names & relations** — who succeeded whom, whose son/wife/colleague,
  founders, authors, commanders, who defeated whom.
- **Places & geography** — what river bounds what people, where a battle was,
  what borders what.
- **Offices, institutions, customs** — who held what magistracy, what a law
  provided, what a people's named custom was.

Avoid (these are the "theories of humours" we steer clear of):

- **Theory, doctrine, opinion, morals** — *why* something is best, what virtue
  consists in, what the gods will. Not closed-book facts.
- **Vague generalities** — "what did X think about Y?" with no single answer.
- **Language trivia** — declensions, scansion, how a word is spelled. Fails
  *translatable*.
- **Whole-passage summary** — "what happens in book 2?" Fails *closed-book* and
  *short-answer*.
- **Anything you had to read the passage to even parse the question.** If the
  question only makes sense next to the text, it is not decontextualizable.

## Precision over recall

When a candidate is doubtful — the fact is fuzzy, the answer arguable, the
anchoring thin, the Latin you'd have to write is shaky — **drop it.** A missed
fact costs nothing; a wrong or ambiguous pair pollutes the dataset. A work that
yields five clean pairs is a success; returning zero is an acceptable outcome.
Do **not** pad. Better ten gold pairs than fifty soft ones.

## Authoring the Latin (the part we now own)

We are writing Latin, so we are responsible for it:

- **Correct and idiomatic.** Classical morphology and syntax. Indirect question
  takes the subjunctive (*quot partes… divisa **sit***); indirect statement
  takes accusative + infinitive (*…divisam **esse**…*). Get agreement, case, and
  tense right.
- **Attribute when natural.** Phrasing like *…Caesar scribit?* / *…apud Tacitum*
  / *…secundum Plinium* both anchors the question and signals the closed-book
  frame ("according to this author"). Use it especially where the "fact" is a
  particular author's claim rather than uncontested history.
- **No macrons.** Plain text, matching the corpus.
- **Keep the answer minimal but grammatical.** *In tres partes.* / *Tres.* /
  *A Tarquinio Prisco.* — a fragment that directly answers, not a restated
  sentence. It need not be a full sentence, but it must be well-formed Latin.
- **The answer must be supported by `source_text`.** Whatever fact the answer
  asserts must be present, unaltered in substance, in the quoted source.

## Read, don't pattern-match — and run serially

Deciding what is a clean, closed-book fact requires *understanding the Latin*:
what is being claimed, which entity it attaches to, whether the answer is truly
unambiguous. This is reading work, done by a model — the main agent, or
delegated to **one Claude subagent per work**. Run subagents **serially — one at
a time, no parallelism** — so each reading gets full attention and the run is
easy to follow and steer. Mechanical tools (listing files, grepping for a
section, spot-checking a number) are fine for *navigation*, never for the
authoring decision itself.

## Normalization of the quoted `source_text`

- **Strip** conversion scaffolding that is not the author's words: section
  markers like `[1]`, navigation number-runs, the title line, stray inline verse
  numbers, the trailing `Author The Latin Library The Classics Page` footer.
- **Keep** the author's words unaltered and in order — no spelling changes, no
  macrons.
- **Editorial supplements** in angle brackets `<...>` (conjectural words/letters
  supplied by the edition): **strip the brackets, keep the words** (`<Est> in
  cistula` → `Est in cistula`). A deterministic post-pass also enforces this.
- You may quote the **minimal contiguous** sentence(s) that establish the fact.
  You need not quote a whole paragraph; quote enough that the fact is unambiguous
  on its own.

## Record schema (per pair)

```
locus        human citation            # e.g. "Caesar, De Bello Gallico 1.1"
source_text  "<verbatim Latin>"        # the sentence(s) that state the fact
question     "<new Latin question>"
answer       "<new Latin short answer>"
question_en  "<English gloss of the question>"
answer_en    "<English gloss of the answer>"
derivation   "<which fact; why it's closed-book & entity-anchored; notes>"
```

Per-work file (`factual/<name>.json`):

```json
{ "source": "text/caesar/gall1.txt",
  "author": "Caesar", "work": "De Bello Gallico, liber I",
  "pairs": [ { "locus": "...", "source_text": "...", "question": "...",
               "answer": "...", "question_en": "...", "answer_en": "...",
               "derivation": "..." } ] }
```

`aggregate.py` flattens all `factual/*.json` to `qa.jsonl` (one pair per line).

## Worked examples

### Caesar, *De Bello Gallico* 1.1 — number fact
- **source_text:** `Gallia est omnis divisa in partes tres, quarum unam incolunt Belgae, aliam Aquitani, tertiam qui ipsorum lingua Celtae, nostra Galli appellantur.`
- **question:** `In quot partes Galliam divisam esse Caesar scribit?`
- **answer:** `In tres partes.`
- **question_en:** "Into how many parts does Caesar say Gaul is divided?"
- **answer_en:** "Into three parts."
- **derivation:** The opening fact of the *Commentarii*. Anchored to Caesar +
  Gaul, single number answer, supported verbatim by *divisa in partes tres*.
  Indirect statement (*divisam esse*) governed by *scribit*; closed-book because
  it is among the most-quoted facts in Latin literature.

### Caesar, *De Bello Gallico* 1.5 — count fact
- **source_text:** `Ubi iam se ad eam rem paratos esse arbitrati sunt, oppida sua omnia, numero ad duodecim, vicos ad quadringentos, reliqua privata aedificia incendunt.`
- **question:** `Quot fere oppida Helvetii ante profectionem incenderunt?`
- **answer:** `Ad duodecim.`
- **question_en:** "About how many towns did the Helvetii burn before setting out?"
- **answer_en:** "About twelve."
- **derivation:** Anchored to the Helvetii + their migration. *fere* mirrors the
  source's approximative *ad* ("about twelve"); answer kept as *ad duodecim*,
  supported verbatim. Short, verifiable.

### Suetonius, *Divus Augustus* 2 — name fact
- **source_text:** `Ea gens a Tarquinio Prisco rege inter minores gentis adlecta in senatum, mox a Servio Tullio in patricias traducta…`
- **question:** `A quo rege gens Octavia in senatum adlecta esse dicitur?`
- **answer:** `A Tarquinio Prisco.`
- **question_en:** "By which king is the Octavian gens said to have been enrolled into the senate?"
- **answer_en:** "By Tarquinius Priscus."
- **derivation:** Anchored to the gens Octavia. Single named-entity answer,
  supported verbatim. *dicitur* keeps the closed-book "according to the
  tradition" frame for a claim particular to Suetonius.

### A pair to REJECT (fails the bar)
- candidate Q: `Cur Belgae fortissimi sunt?` / A: `Quod a cultu atque humanitate
  provinciae longissime absunt.`
- **why rejected:** This is causal/interpretive, not a short verifiable fact —
  it restates Caesar's *explanation*, which is opinion-shaped ("because they are
  farthest from civilization"). Fails *short-answer* and sits uneasily with
  *verifiable*/*non-rhetorical*. Drop it; keep the crisp "who/how many/where"
  facts instead.
