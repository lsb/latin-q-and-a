# Consolidated review of combined_qa_07-22 (233 rows, 2026-07-23)

Three independent full-read passes over every row: (A) Latin proofread,
(B) Latin↔English↔answer consistency, (C) anchoring & self-containment.
Findings cross-confirmed by two readers are marked ×2. Row numbers are sheet IDs.

## 1. Content bugs — answer wrong, leaked, or ambiguous

| id | problem | suggested fix |
|----|---------|---------------|
| 149 | "What room would a Roman bather enter **after the tepidarium**?" → answer Frigidarium; the standard sequence is tepidarium → caldarium → frigidarium. LA also garbled: "postquam in tepidario, fuerat intrabat" ×2 | Answer "Caldarium", or ask "after the caldarium"; LA: "Quod conclave balneator Romanus, postquam in tepidario fuerat, intrabat?" |
| 150 | Feather-stuffed ball is the **paganica** (Martial 14.45); harpastum was the small hard ball | Change answer to Paganica, or drop the feather detail |
| 167 | LA-Q contains its own answer: "Quod est Latinum nomen **voluminis** papyracei?" → Volumen | "Quo nomine Romani librum papyraceum convolutum appellabant?" |
| 221 | Both sides name the answer: LA-Q has "atramentum", answer Atramentum ×2 | LA: replace "atramentum," with "liquor niger" (and factum → factam, agreeing with materiam); EN: "What is the Latin word for the black writing fluid…" |
| 158 | EN still asks the old version ("What day is 8 days before the Ides?") while LA asks the 5th/7th day of the month — materially different questions ×2 | EN: "By what name did the Romans call the fifth (in some months the seventh) day of each month?" |
| 142 | LA asks the **knot** ("quo nodo"), EN asks "what type of **belt**"; answer Nodus Herculaneus fits only LA ×2 | EN: "With what knot is the Roman bride's belt tied?" |
| 123 | Answer "Bidentales" — those are the priests; the shrines are **Bidentalia** (bidental n.) ×2 | "Bidentalia" |
| 130 | "Quod **mare**…" but the answer (Fretum Gaditanum) is a strait ×2 | "Quod fretum…" |
| 196 | "only magistrates holding **Imperium**" — censors and curule aediles used the sella curulis without imperium | "curule magistrates" / "magistratibus curulibus" |
| 198 | Dictator was named (dictus) by a consul on the Senate's authorization, not "appointed by the Senate" | "nominated by a consul on the Senate's instruction" |
| 200 | "office reserved exclusively for plebeians" also admits the plebeian aedile | add disambiguator, e.g. "whose holders were sacrosanct" |
| 191 | "personae **statariae**" — stataria means quiet/stationary, not "stock character" | drop "statariae" |
| 225 | EN's "during his first three years in exile" is absent from LA, which as phrased also admits Epistulae ex Ponto | add "primis tribus annis exsilii" to LA |
| 169 | Answer "Strigimentum" — attested form strigmenta, and the question is plural ×2 | "Strigmenta" |

## 2. English answers sitting in the Latin answer column

| id | current | fix |
|----|---------|-----|
| 216 | Three months | Tribus mensibus |
| 129 | Tiber | Tiberis |
| 156 | Trireme | Triremis |
| 214 | Gnaeus Pompeius Magnus/pompey | Gnaeus Pompeius Magnus |
| 220 | Publius Vergilius Maro/Virgil | Publius Vergilius Maro |

## 3. Latin typos and agreement errors (mechanical)

| id | current | fix |
|----|---------|-----|
| 18 | Intubae | Intuba (neuter, matching "holera") |
| 88 | tonitru et fulmina dedit | tonitrua et fulmina dedit |
| 117 | Sagina Gladitoria; victūs (stray macron) | Sagina Gladiatoria; victus |
| 141 | ā legionariis (stray macron) | a legionariis |
| 143 | Laticlavia (answers "Quales tunicae") | Laticlaviae |
| 146 | Sigiillaria ×2 | Sigillaria |
| 147 | Summmalia ×2 | Summanalia |
| 152 | Aquaductus ×2 | Aquaeductus |
| 153 | systema publicam … manisonum ×2 | systema publicum … mansionum |
| 159 | Quattor ×2 | Quattuor |
| 133 | In palatino | In Palatino |
| 164 | Septennis (answers "Qua aetate") | Septem annorum |

## 4. English typos and mechanics

215 "godess"→"goddess" · 161 "roman"→"Roman" · 141 "Legionnaires"→"legionaries", "heavy soled"→"heavy-soled" · 42 ends with "." not "?" · 73, 78 missing "?" · 97 "and from whom he received"→"and from whom did he receive" · 46 unbalanced quote in "Calos' — 'bravo!'" · 121 "worship"→"worshipped" · stray mid-sentence capitals in 115, 116, 117, 127, 150 ("Gladiator(s)", "Villas", "Game", "Palaestra")

## 5. Roman-qualifier placement (anchoring pass, reader C)

These insertions qualify the wrong noun, so the answer's culture is still unpinned
(the fullo problem):

| id | current | issue | suggestion |
|----|---------|-------|------------|
| 174 | "vestimenta Romana purgat" / "cleans Roman clothing" | any launderer can clean Roman clothes | "Quis artifex Romanus vestimenta purgat?" — or reframe as vocabulary: "What is the Latin term for a clothes-cleaner?" |
| 175 | "vestimenta Romana purgantur" | same | "In qua taberna Romana vestimenta purgantur?" (Roman shop) |
| 177 | "anulus Romanus" | the custom, not the ring, is Roman | "Qui anulus sponsalibus Romanis datur?" |
| 160 | "instrumentum Romanum" | clepsydra is Greek; qualify the users | "Quo instrumento Romani horas aqua metiuntur?" |
| 192 | "fabulae Romanae" | pantomime plots were typically Greek myth | qualify the stage: "in scaena Romana" |
| 204 | "nummis Romanis mutandis" | qualifies the coins, not the profession | "Qui apud Romanos nummis mutandis praesunt?" |
| 206 | "nummos Romanos probabant" | same pattern (milder); EN also says "minted", absent from LA | "Qui apud Romanos nummos probabant…?"; drop "minted" from EN |

## 6. Still unanchored after the editing pass (reader C)

Both sides: 27 (pins Egypt, not Rome), 49 (dochmius), 124 (atrium), 125 (dining room), 137 (Campanian wine — present tense reads modern), 138 (amphora tags), 150 (palaestra game), 168 (strigil), 187, 188 (mosaic pair), 197 ("the Republic"), 198 ("the Senate").

Anchor lives on one side only (translation loses it): 57 (EN-only "according to Martial"), 59 (LA-only "lacernae"), 135 (LA-only "plebs"), 140 (EN-only "toga"), 181 (LA-only "patrimus et matrimus"), 186 (LA "cohortis"; EN "decimated unit" reads modern), 229 (LA-only "pater familias").

Translation-attribution mismatches of the same kind: 22 and 57 (EN cites Augustine/Martial, LA doesn't), 140 (EN "toga bleaching", LA generic "vestes"), 144 (EN drops all of LA's identifying detail for the pileus), 135 (EN omits "left at the bottom of the vessel"), 172 (LA "servae" female; EN just "slave"), 18 (LA plural, EN singular).

## 7. Judgment calls / observations (no fix required)

- Near-duplicates within Lee's set: 59 vs 73 (murex purple), 47 vs 71 (consular dating).
- 47 categorized "ius" but is a dating custom → mores or historia?
- Minor Latin style (reader A, debatable): 46 "acclamabant" → "inscribebant" for graffiti; 120 gerund → gerundive; 131 "septentriones … incolit" strained; 183 "genere clipei" — clipeus vs scutum are contrasted terms, consider "Quo genere armorum…"; 197 word order "in Re Publica duodeviginti mensium"; 231 spurious "prior"; 232 "ulteriorem" is an English calque → "postea".
- 216 "hoc imperio dato": two readers re-flagged the demonstrative; adjudicated 2026-07-23 — the imperium is the pirate-clearing commission stated in the sentence itself, resolves internally. (Reader A's "eo imperio dato" remains available if wanted.)
- Vivienne's rows carry English category labels in the sheet by design; unify.py harmonizes them to the Latin scheme. Reader B's proposed mapping matches the one already in use.
- Verified sound by spot-check: 4 (three arbiters), 108 (D for A), 138 (pittacia), 148 (quadrans), 164 (age seven), 186 (barley), 197 (18-month censorship), 230 (three sales).
