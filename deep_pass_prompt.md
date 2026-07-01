# Driver prompt — a fuller (deep) pass through the Latin corpus

Paste the block below into a fresh Claude Code session opened in this repo
(`latin-q-and-a`). It drives the whole campaign: it picks works, spawns **one
reader subagent at a time**, validates, merges, aggregates, and commits per work.
The reader-subagent template is embedded, so nothing else is needed.

Scope is a knob: by default it deep-mines the dense works; to limit it, replace
the "Scope" line with the works you want.

---

You are building an **ECLeKTic-style factual Latin Q&A dataset** in this repo.
Before doing anything, read these — they are the source of truth and override any
assumption you have: **`GUIDELINES.md`**, **`author_prompt.md`**, and the
README's **"Reproducing with Claude"** and **"Depth: a first pass is a floor"**
sections. Then follow the loop below.

**What exists.** `text/` holds one plain-text file per work (the Latin Library
corpus). `factual/<name>.json` holds the pairs for one work
(`{source, author, work, [provenance], pairs:[{locus, source_text, question,
answer, question_en, answer_en, derivation}]}`). `python3 aggregate.py` flattens
all of `factual/*.json` into `qa.jsonl` and prints a per-author tally. Some
`factual/*.json` are only a first (shallow) pass and can be **deepened**; a few
(e.g. `suetonius.iulius.json`) have had a deep pass.

**Goal.** Take **every** fact that clears the seven acceptance criteria — no
target ceiling, no "famous-only" filter. Precision is the *quality gate* (drop
doubtful/soft/passage-dependent pairs), not a cap on count. The obscure-but-
verifiable fact is often the *more* valuable one for a cross-lingual test.

**Scope (edit this line to limit the run).** Deep-pass the dense works, in this
priority order, then stop and report: the rest of the Twelve Caesars
(`suetonius.augustus`, `.tiberius`, `.caligula`, `.claudius`, `.nero`, `.galba`,
`.otho`, `.vitellius`, `.vespasian`, `.titus`, `.domitian`); Caesar's
commentaries (`caesar.gall1..8`, `caesar.bc1..3`, `caesar.alex/.bellafr/.hisp`);
the Tacitus books (`tacitus.*`); Pliny (`pliny.nh2..5`, `pliny.ep6/.ep10`). New
works not yet in `factual/` may be added the same way.

**Hard rules.**
- **Serial only.** Exactly ONE reader subagent running at a time. Never parallel.
- **Corpus is the Latin Library** under `text/`. If a target text file is missing
  or empty, the reader must report `MISSING: <path>` and write nothing — it must
  **not** fetch text from anywhere else. (`pliny.nh7` is the one recorded
  non-Latin-Library exception; don't add more without the user's say-so.)
- **One work per commit**, pushed to `trunk` (branch first if you prefer).
  End commit messages with:
  `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`

**Loop — repeat until Scope is done or the user says stop:**

1. **Pick the next work.** For a **deepening** pass, its `factual/<name>.json`
   already exists; for a **new** work, it doesn't. Confirm the `text/` file
   exists first (`ls -la`).
2. **Spawn ONE reader subagent** (general-purpose) with the template below,
   filling the placeholders. For a deepening pass, include the "DEEPENING" block
   so it reads the existing pairs and authors only *new* ones. Wait for it.
3. **Validate** the returned/written pairs with this check (adjust the path):
   ```
   python3 - <<'PY'
   import json
   req={'locus','source_text','question','answer','question_en','answer_en','derivation'}
   d=json.load(open('factual/<name>.json'))          # or the scratch file for a deepening pass
   ps=d['pairs'] if isinstance(d,dict) else d
   print('pairs:',len(ps))
   print('schema issues:',sum(1 for p in ps if (req-set(p)) or (set(p)-req)))
   print('non-? questions:',sum(1 for p in ps if not p['question'].rstrip().endswith('?')))
   print('longest answers (words):',sorted((len(p['answer'].split()) for p in ps),reverse=True)[:3])
   PY
   ```
   Then spot-check a few facts against the source and eyeball the Latin (indirect
   question → subjunctive; indirect statement → acc.+inf.; no macrons).
4. **Merge (deepening only).** Append the new pairs to the existing
   `factual/<name>.json` — leave the original pairs byte-for-byte untouched — and
   drop any new pair whose question duplicates an existing one.
5. **Aggregate + global dedup:** `python3 aggregate.py`, then confirm **0**
   duplicate questions across the whole set:
   ```
   python3 -c "import json,collections;q=collections.Counter(json.loads(l)['question'] for l in open('qa.jsonl'));print('dups:',sum(1 for n in q.values() if n>1))"
   ```
6. **Commit** just that one `factual/<name>.json` + `qa.jsonl`; push.
7. Report running totals (pairs, works) and continue.

---

**READER SUBAGENT PROMPT TEMPLATE** (fill `<...>`; keep it a single subagent):

> You are a Latin scholar AUTHORING closed-book, fact-seeking question/answer
> pairs from ONE Latin work, ECLeKTic-style. WRITE new Latin questions and short
> answers about facts stated in the text, keeping the verbatim source sentence as
> evidence.
>
> FIRST, confirm `<TEXT_PATH>` exists and is non-empty (Read its first lines). If
> not, reply exactly `MISSING: <TEXT_PATH>` and write nothing. Do NOT fetch text
> from anywhere else.
>
> 1. Read in full: `author_prompt.md` and `GUIDELINES.md`. Skim `<EXAMPLE_FILE>`
>    (an existing output) for the shape and quality bar.
> 2. Read the ENTIRE work: `<TEXT_PATH>`  (`<AUTHOR>`, `<WORK>`). Use Read with
>    offset/limit to cover all of it.
> 3. Author pairs. This is a DEPTH pass: take **every** fact that clears ALL SEVEN
>    criteria (closed-book, entity-anchored, verifiable, decontextualizable,
>    short-answer, translatable, non-rhetorical). NO target ceiling and NO
>    "famous-only" filter — keep the less-celebrated verifiable facts too. Still
>    DROP anything doubtful, untranslatable (Latin puns/metre/grammar trivia), or
>    passage-dependent. Hunt across the whole work: `<TARGET_FACTS — e.g. birth/
>    death dates & places, family & marriages, offices & magistracies held, named
>    battles/campaigns and who won, distances & numbers, laws & institutions,
>    named customs, buildings, sayings with a checkable point>`.
>    Attribute to the author where natural (`...ut Suetonius tradit? / apud
>    Tacitum? / Caesar scribit?`). Answers short and grammatical; no macrons.
>    Normalize `source_text` (strip `[1]` markers/number-runs/footers; strip
>    editorial `<...>` brackets but keep the words; quote the minimal contiguous
>    sentence(s)).
>    <DEEPENING: First read the pairs already extracted for this work in
>    `<EXISTING_FILE>`, and do NOT duplicate them — same fact or same question.
>    Author only ADDITIONAL pairs the text still supports (usually many more).>
> 4. WRITE valid JSON to `<OUTPUT_PATH>` — <for a NEW work: the object
>    `{"source":"<TEXT_PATH>","author":"<AUTHOR>","work":"<WORK>","pairs":[...]}`;
>    for a DEEPENING pass: a bare JSON ARRAY of only the new pair objects> — each
>    pair having EXACTLY the seven keys, no extras. Then reply with the COUNT and a
>    one-paragraph summary (NOT the JSON).

---

That's the whole process. It is resume-safe: `factual/` + `qa.jsonl` show what
exists and at what depth, so an interrupted run just continues with the next
work.
