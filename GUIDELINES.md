# Factual & Cultural Q&A Authoring Guidelines

How we build a dataset of **closed-book question/answer pairs** from the Latin
Library corpus (plain text under `text/`), in the spirit of two benchmarks:

- **ECLeKTic** ([arXiv:2502.21228](https://arxiv.org/abs/2502.21228)) —
  closed-book *factual* recall that transfers across languages; this shaped the
  first phase of the dataset (history, biography, law).
- **Global PIQA** ([arXiv:2510.24081](https://arxiv.org/abs/2510.24081)) —
  *culturally salient* knowledge, authored natively in each language rather
  than translated; this shapes the current phase (see *The cultural turn*
  below and [issue #2](../../issues/2)).

These are working rules; the boundaries are debatable, so every pair records the
verbatim source it rests on and *why* it was drawn the way it was.

## What we do (and don't)

We **author** questions; we do not merely *find* them. We read **factual prose**
— geography, ethnography, biography, history, law, agronomy — and **cultural
texts** — comedy, epigram, the novel, recipes, calendar poetry, inscriptions and
epitaphs — and for each clean fact we **write a new Latin question** whose
answer is that fact, keeping the verbatim source sentence as evidence so every
pair is auditable.

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

## The cultural turn (June 2026)

The first phase of the dataset mined **history** — and by mid-2026 we had
enough of it (issue #2: "we prob have enough history"). The target is now
**culture**: the shared, ambient knowledge of the Roman/Latin world.

What changed, concretely:

- **Sources.** From historians and jurists to culturally dense texts:
  Petronius's *Satyricon*, Apicius's recipes, Ovid's *Fasti* (the festival
  calendar) and myth, Martial's *Xenia*/*Apophoreta*, Plautus, Catullus,
  inscriptions and epitaphs.
- **What counts as a fact.** Alongside battles and magistracies: **food and
  cookery, festivals and rites, spectacles and leisure, customs of daily life
  (funerals, weddings, patronage, baths, dress, money), myth as shared story,
  proverbs with a checkable point.** A mythological "fact" (Daphne was turned
  into a laurel) is a fact *of the culture*, evidenced by the text like any
  other.
- **A new acceptance criterion** — *culturally salient* (criterion 8 below),
  adapted from the meeting notes in issue #2.
- **Two tracks** — the main dataset stays translatable (ECLeKTic-compatible);
  a small tagged track relaxes *only* translatability for knowledge that lives
  in the Latin language itself (see *Two tracks* below). Global PIQA is the
  precedent: its non-parallel split was authored natively per language — over
  half its examples reference local foods, customs, and traditions — and was
  never meant to survive translation.

History pairs authored under the earlier bar are **retained unchanged**;
history mining is paused, not repudiated. Pre-turn per-work files lack the
`category`/`track` fields, and `aggregate.py` defaults them.

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
review), a `derivation` note, a `category` domain tag, and — only when
criterion 6 is deliberately waived — a `track` marker (see *Two tracks*).

## The acceptance bar — the eight criteria

ECLeKTic is about *closed-book cross-lingual factual recall*; Global PIQA is
about *culturally salient* knowledge. A pair is only worth keeping if a
well-read model — one that learned this content in **any** language, without
the text in front of it — could answer it. Every kept pair must satisfy **all
eight**:

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
8. **Culturally salient.** The fact belongs to the *shared* knowledge of the
   Roman/Latin world — the kind of thing an insider (a Roman, or a well-read
   Latin reader) would carry around, and an outsider likely would not:
   festivals, foods, rites, spectacles, proverbs, famous myths, civic customs,
   celebrated history. Two failure modes, one on each side: **not universal**
   (knowledge every culture shares — "bread is baked in an oven" — tells you
   nothing about Latin), and **not clique-local** (a detail only one town,
   household, or army unit could know, carried by no one). It is fine if an
   outsider *could* look the fact up; the test is whose **ambient knowledge**
   it is, not secrecy. (Adapted from the issue #2 meeting notes.)

If any one fails, **drop the pair.** (Exception: pairs explicitly tagged
`track: "latin-specific"` waive criterion 6 — *and only 6* — see *Two tracks*.)

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
- **Food & cookery** — named dishes and what goes in them, the staple sauces
  (garum/liquamen, defrutum, passum), named wines, what course was served when.
- **Festivals & the sacred calendar** — which feast in which month, for which
  god, with what named rite (Lupercalia, Saturnalia, Parilia…).
- **Spectacles & leisure** — the games and their venues, chariot factions,
  gladiator types, the baths, theater conventions.
- **Mores & daily life** — funerals and epitaph formulas, weddings, patronage
  and the salutatio, dress (toga, stola), coinage, meals and their hours.
- **Myth as shared story** — who was turned into what, who fathered/loved/slew
  whom, canonical attributes and epithets. (Daphne → laurel is a keepable
  cultural fact, evidenced by Ovid.)
- **Proverbs & sayings** — where the point is checkable (who said it, of what).

Avoid (these are the "theories of humours" we steer clear of):

- **Theory, doctrine, opinion, morals** — *why* something is best, what virtue
  consists in, what the gods will. Not closed-book facts.
- **Vague generalities** — "what did X think about Y?" with no single answer.
- **Language trivia** — declensions, scansion, how a word is spelled. Fails
  *translatable* — **on the main track.** Knowledge that genuinely lives in the
  Latin language (meter, wordplay) belongs on the `latin-specific` track, not
  in the discard pile; see *Two tracks* below.
- **Whole-passage summary** — "what happens in book 2?" Fails *closed-book* and
  *short-answer*.
- **Anything you had to read the passage to even parse the question.** If the
  question only makes sense next to the text, it is not decontextualizable.

## Precision on quality, exhaustive on coverage

The eight criteria are a strict **quality gate**: when a candidate is doubtful —
the fact is fuzzy, the answer arguable, the anchoring thin, the Latin you'd have
to write is shaky — **drop it.** A wrong or ambiguous pair pollutes the dataset.

But that precision is about **quality, not count.** We take **every** fact that
clears the gate, with no target ceiling and no "famous facts only" filter — the
celebrated and the merely verifiable alike (the less-celebrated but still
culturally-shared fact is often the *more* useful one for a cross-lingual
test). Criterion 8 is part of the gate, not a fame filter: it drops the
clique-local minutia nobody carries, not the merely un-famous. "Do not pad"
means do not admit *soft* pairs, not "stop early." So a dense biography or
history can yield **dozens** of pairs and should; a sparse, theological, or
lyric work may yield a handful or none, and that too is fine.

**Yield reflects mining depth, not the text.** A single quick pass under-mines a
rich work — a first pass over Suetonius's *Divus Iulius* took 20 pairs; a
deep pass, cap removed, found 80 more, all clearing the same bar. Treat a
first pass as a floor, and **deepen** dense works by re-reading them against the
pairs already taken (see `author_prompt.md` → *Deepening an already-covered
work*).

## Two tracks: `translatable` and `latin-specific`

The main dataset keeps criterion 6 — that is what makes it ECLeKTic-comparable,
and it is the default (no `track` field needed). But the issue #2 meeting asked
for **untranslatable questions** too: knowledge that lives *in the Latin* —
meter, scansion, wordplay — the way Global PIQA's natively-authored pairs live
in their language and were never meant to be parallel. Those pairs go in the
same per-work files and the same `qa.jsonl`, tagged `track: "latin-specific"`,
so downstream ECLeKTic-style use filters them out with one condition.

Rules for the `latin-specific` track:

- It waives **criterion 6 and only 6**. Closed-book, entity-anchored,
  verifiable, decontextualizable, short-answer, non-rhetorical, and culturally
  salient all still bind. "Scan this line" is an exercise, not a fact; "which
  foot is *never* admitted in the last place of a hexameter" is knowledge.
- **The meter boundary call.** A fact *about* meter often translates fine and
  belongs on the **main** track: "In what meter is the *Aeneid* composed?" →
  *Hexametro dactylico.* survives translation into any language. What is
  `latin-specific` is knowledge that requires the Latin itself to state or
  verify: where the caesura falls in a particular famous line, what a pun turns
  on, which syllable is long. When in doubt, tag it `latin-specific` — the tag
  is cheap, and un-tagging is easy; polluting the translatable set is not.
- Keep this track **small and deliberate** — it is an experiment (pilot: the
  scansion/caesura questions the meeting floated), not a second firehose.
- **Sources for the pilot** (the meeting asked for a Latin analogue of
  Dionysius of Halicarnassus, who wrote in Greek and is out of scope): the
  corpus's own Latin criticism — **Cicero, *Orator*** (the *numerus* section,
  the fullest Latin treatment of prose rhythm and clausulae),
  **Quintilian, *Institutio* IX** (on *compositio*), **Macrobius,
  *Saturnalia* V–VI** (quotes Vergil beside Homer and Ennius and analyzes the
  verses — the closest Latin match to Dionysius' method with Sappho), and
  **Gellius** (chapters on euphony and meter). A dedicated metrical treatise
  (Terentianus Maurus) is not in the corpus; add it only with recorded
  provenance if the pilot proves out.

## Category tags

Each new pair carries a coarse `category`, one of:

`cibus` (food & cookery) · `religio` (rites, festivals, the sacred calendar) ·
`ludi` (spectacles, games, theater, leisure) · `mores` (daily life & custom) ·
`mythos` (mythology) · `proverbium` (sayings) · `historia` (political/military
history, biography) · `ius` (law & institutions) · `geographia` (places &
peoples) · `lingua` (latin-specific language knowledge)

One tag per pair — pick the dominant domain. Pre-turn files have no tag;
`aggregate.py` leaves those empty rather than guessing.

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
category     "<domain tag — see Category tags>"        # required since 2026-06
track        "latin-specific"          # ONLY when criterion 6 is waived; else omit
```

Pre-turn pairs (authored before June 2026) have exactly the first seven keys;
new pairs have eight (plus `track` on the rare latin-specific pair).
`aggregate.py` accepts both, defaulting `category` to `""` and `track` to
`"translatable"`.

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

### Apicius, *De Re Coquinaria* 1.1 — cultural (food) fact
- **source_text:** `Mellis p.XV in aeneum uas mittuntur, praemissis vini sextariis duobus, ut in coctura mellis vinum decoquas.`
- **question:** `Ex quibus duabus rebus praecipue conditum paradoxum apud Apicium temperatur?`
- **answer:** `Ex melle et vino.`
- **question_en:** "From which two principal ingredients is *conditum paradoxum* prepared in Apicius?"
- **answer_en:** "From honey and wine."
- **category:** `cibus`
- **derivation:** *Conditum* (spiced honey wine) was the standard Roman
  aperitif — ambient food culture, criterion 8's home turf. Anchored to Apicius
  + the named preparation; the two-ingredient base is stated verbatim.
  Translatable: nothing turns on the Latin words.

### Vergil, *Aeneid* 1.1 — `latin-specific` track (scansion) fact
- **source_text:** `Arma virumque cano, Troiae qui primus ab oris`
- **question:** `In primo Aeneidos versu, post quod verbum incidit caesura praecipua?`
- **answer:** `Post "cano".`
- **question_en:** "In the first line of the Aeneid, after which word does the main caesura fall?"
- **answer_en:** "After *cano*."
- **category:** `lingua` — **track:** `latin-specific`
- **derivation:** The third-foot (penthemimeral) caesura of the most famous
  hexameter in Latin — knowledge every reader of Vergil carries, verifiable by
  scanning the quoted line, but it cannot survive translation (criterion 6
  waived, all others hold). This is the shape of the meeting's "scansion
  questions" idea.

### A pair to REJECT (fails the bar)
- candidate Q: `Cur Belgae fortissimi sunt?` / A: `Quod a cultu atque humanitate
  provinciae longissime absunt.`
- **why rejected:** This is causal/interpretive, not a short verifiable fact —
  it restates Caesar's *explanation*, which is opinion-shaped ("because they are
  farthest from civilization"). Fails *short-answer* and sits uneasily with
  *verifiable*/*non-rhetorical*. Drop it; keep the crisp "who/how many/where"
  facts instead.
