# Unified Questions: Difficulty Extrema

*Which questions in the unified Q&A set (`unified_q_and_a.jsonl`, 233 pairs) trip up a large model, and which ones even a tiny model nails every time?*

## Method

The eval harness (`evaluate.py`) ran each question through each model 3 times ("rollouts") in a closed-book, Latin-in/Latin-out setting, then judged each answer against the gold answer — first by exact string match, falling back to an LLM judge (`gemma4:31b`) for substantive-fact equivalence (`eval-reviewed/judgments.jsonl`, `eval-reviewed/answers.jsonl`).

Two models bracket the size range in this comparison:

- **`qwen3.6:27b`** — a 27B-parameter reasoning model, the strongest performer reviewed (78.0% of all 699 rollouts on the unified set judged correct; mean ~184s/answer).
- **`gemma4:e2b`** — Gemma 4's tiny "effective 2B" variant, the smallest model reviewed (22.0% of rollouts correct; mean ~5.5s/answer — Qwen took ~34x longer per answer on average).

Extrema were defined the strict way — unanimous across all 3 rollouts, not just majority:

- **"Least answerable" by Qwen** = questions where **qwen3.6:27b got 0 of 3 rollouts right** (32 of 233 questions, 13.7%).
- **"Easiest" for Gemma e2b** = questions where **gemma4:e2b got 3 of 3 rollouts right** (38 of 233 questions, 16.3%).

Only **one question** falls in both sets — the tiny model nailing something the giant reasoning model whiffed on every single time. See the spotlight below.

## Distributions

Correct-rollout counts across the 233 unified questions (out of 3 rollouts each):

| Correct rollouts | Qwen3.6:27b (# questions) | Gemma4:e2b (# questions) |
|---|---|---|
| 0/3 | 32 | 166 |
| 1/3 | 16 | 18 |
| 2/3 | 26 | 11 |
| 3/3 | 159 | 38 |

By difficulty rating (the sheet's red/orange/blue/green scale, hardest to easiest):

| Set | red | orange | blue | green |
|---|---|---|---|---|
| Qwen's 32 unanswerable questions | 14 | 15 | 3 | 0 |
| Gemma e2b's 38 easy questions | 2 | 8 | 19 | 9 |

The difficulty labels hold up well against the eval: Qwen's failures cluster almost entirely in red/orange (29 of 32), and Gemma e2b's clean sweeps cluster in blue/green (28 of 38).

By category:

| Set | top categories |
|---|---|
| Qwen's 32 unanswerable questions | cibus 7, mores 8, religio 4, ludi 3, artes 3 |
| Gemma e2b's 38 easy questions | mores 11, historia 8, mythos 5, geographia 5, litterae 4 |

## Spotlight: the one question that flips the ranking

**id 130 (red, geographia)** — *"What body of water separates the province of Hispania from the coast of Mauretania?"* Gold: **Fretum Gaditanum**.

- **qwen3.6:27b** (0/3): *"Oceanus."* / *"Mediterraneum."* / *"Mediterraneum."* — confidently wrong, naming the wrong body of water each time.
- **gemma4:e2b** (3/3): *"Straitum Gibraltarum."* all three times — a Latinized "Strait of Gibraltar," judged equivalent to *Fretum Gaditanum* because it's the same strait, just under its modern name.

The giant model reasoned its way to a plausible-sounding but geographically wrong answer three separate times; the tiny model produced the same (correct-in-substance) guess three times because "Strait of Gibraltar" is exactly the kind of high-frequency, low-ambiguity fact small models memorize verbatim.

## Patterns

**What breaks Qwen 3.6 27B:** almost every failure is a single, precise technical noun with no obvious Latin-derived English cognate to lean on — a specific recipe ingredient (*ius candidum*, *nitrum*, endives for winter lettuce, ginger+cardamom in a Vinidarius recipe), a named implement (*ascia* the adze, *scabellum* the pantomime clapper-shoe, *strigimentum* gladiator scrapings), or a named-but-obscure rite/office (*Summanalia*, *bidentalia*, *mensarii*). Qwen never hedges — it always produces a fluent, confident, wrong Latin word (*Cerussa*, *Titus Labienus* three times running, *Trigonometrum*), which is the more dangerous failure mode for a QA system since the errors are hard to catch downstream.

**What Gemma e2b gets right:** almost entirely single, famous proper nouns — Achilles, Perseus, Dido, Virgil, Trajan, Pompey, the Ides of March, Jerusalem, the Domus Aurea, Cursus honorum, Pontifex Maximus, Denarius. These are facts likely seen thousands of times in pretraining in roughly this exact phrasing, so a 2B model recalls them as reliably as a 27B one. On the harder/rarer vocabulary (see the 32-question table above), e2b's failure mode is the opposite of Qwen's: instead of confabulating, it frequently hedges or refuses outright — *"Non est nomen specificum,"* *"Non est notum,"* *"Non est in exemplis"* — visible undertraining rather than confident hallucination.

## The 32 questions least answerable by Qwen 3.6 27B (0/3 correct)

| id | difficulty | category | question (EN) | gold answer (EN) | Qwen3.6:27b's 3 rollout answers |
|---|---|---|---|---|---|
| 2 | red | ius | How many days of grace does the Law of the Twelve Tables give a debtor after admission of the debt or lawful judgment? | Thirty | *Sexaginta.*; *Sexaginta dies.*; *Sexaginta.* |
| 7 | red | mores | With what tool does the Law of the Twelve Tables forbid the funeral pyre to be smoothed? | With the adze (ascia) — the pyre wood was to be left rough | *Cerussa.*; *Ornamentis.*; *Auro.* |
| 10 | red | cibus | What two aromatics are ground with laser for the ofellae 'garaton' in the excerpts of Vinidarius? | Ginger and cardamom | *Piper et cumina.*; *Piper et amomum.*; *Piper et coriandrum.* |
| 13 | blue | cibus | With what are meats covered, according to Apicius, so that they stay fresh at any time without salt? | With honey | *Pice liquida.*; *Furfure.*; *Pinguedine.* |
| 17 | orange | cibus | Cooked with what does every green vegetable turn emerald in Apicius? | With nitrum (soda) | *Aceto.*; *Sanguine.*; *Manna.* |
| 18 | red | cibus | What vegetable stands in for lettuce in winter, according to Apicius? | Endives | *Cucurbitae.*; *Apiae et verbenacia.*; *Apianam.* |
| 19 | orange | cibus | By what name is the sauce of the pullus Vardanus, made with milk and egg whites, called in Apicius? | White sauce (ius candidum) | *Ius lactis.*; *Hirtianum.*; *Vardani.* |
| 20 | orange | cibus | On what food are snails fattened in Apicius until they can no longer draw themselves back into their shells? | On milk | *Caseo et oleo.*; *Frumento.*; *Melle.* |
| 24 | orange | historia | Who held Sicily for the Pompeians, the province Caesar ordered Curio to seize? | Marcus Cato (Cato the Younger) | *Verres.*; *Dolabella.*; *Varro.* |
| 26 | orange | historia | Which of Caesar's commanders in Africa, having lost his army, refused to return to Caesar and was killed fighting? | Gaius Curio | *Titus Labienus.*; *Titus Labienus.*; *Titus Labienus.* |
| 43 | orange | religio | What burning offering did dutiful Romans customarily place at the tombs of the dead? | A lamp | *Incensum.*; *Incensum.*; *Incensum.* |
| 46 | orange | ludi | With what word, borrowed from Greek, did Pompeian fans acclaim their actors on the walls? | Calos' — 'bravo!' (Greek kalos) | *Syri.*; *Pompeius.*; *Philopompei.* |
| 54 | orange | cibus | The image of what god, shaped from fine wheat flour, is eaten among the Saturnalian gifts in Martial? | Of Priapus | *Silvani.*; *Saturni.*; *Mercurii.* |
| 55 | orange | mores | From what tree were Roman brooms usually made, as Martial attests? | From the palm | *Salix.*; *Ex olea.*; *Salice.* |
| 60 | orange | mores | Of what were the thin headbands (vittae) of Roman women the badge? | Of chastity | *Matrimonii.*; *Matrimonii.*; *Matrimonii.* |
| 61 | orange | ludi | Of what material were the images of the gods carried in the Circus procession? | Of ivory | *Auratae.*; *Simulacra.*; *Aureae.* |
| 68 | blue | mythos | For which goddess did Ulysses draw Troy and the Simois with a staff on the beach? | For Calypso | *Minervae.*; *Minervae.*; *Minervae.* |
| 108 | red | lingua | Which letter did Caesar write in place of A in his cipher? | D (the fourth letter) | *V.*; *Litteram V.*; *V.* |
| 117 | red | ludi | What is the name for the diet of Roman Gladiators? | Sagina gladiatoria | *Hordearius.*; *Hordeum.*; *Ructor.* |
| 123 | red | religio | What Roman shrines are traditionally built on top of spots where lightning struck? | Bidentalia | *Foculi.*; *Fana.*; *Fana.* |
| 127 | blue | mores | What is the open air courtyard common in Roman Villas? | Peristylum | *Atrium.*; *Atrium.*; *Atrium.* |
| 130 | red | geographia | What body of water separates the province of Hispania from the coast of Mauretania? | Fretum Gaditanum | *Oceanus.*; *Mediterraneum.*; *Mediterraneum.* |
| 146 | orange | religio | What type of clay figurines are common Saturnalia presents? | Sigillaria | *Parva.*; *Creta confecta et picta.*; *Deorum.* |
| 147 | red | religio | Which baked goods are traditionally offered to the god Summanus on the day before summer solstice? | Summanalia | *Parva.*; *Liba.*; *Liba.* |
| 150 | red | mores | What Game commonly played in the Palaestra uses a ball filled with feathers? | Harpastum | *Trigon.*; *Trigonometrum.*; *Volatilis.* |
| 169 | red | mores | What Latin term describes the oily scrapings collected from gladiators' skin and sold as a cosmetic or medicinal remedy? | Strigmentum | *Sudor gladiatorius.*; *Suda.*; *Unguentum gladiatorium.* |
| 179 | orange | mores | What was the name for the ritual Roman song sung outside the bridal chamber on the wedding night? | Epithalamium | *Carmen coniugale.*; *Talassophonia.*; *Carmen conniviale.* |
| 189 | red | artes | What complex hand-language is used in Roman pantomime? | Chironomia | *Digitus.*; *Gestus.*; *Gestus.* |
| 191 | orange | artes | What was the name of the clownish, gluttonous stock character in Atellan farce? | Maccus | *Bucco.*; *Manduco.*; *Manducus.* |
| 193 | red | artes | What shoe is used as an instrument in Roman pantomime? | Scabellum | *Soccus.*; *Crepida.*; *Cothurnus.* |
| 205 | red | mores | Who are the people appointed by the Roman state to help citizens manage debt during economic hardship? | Mensarii | *Decemviri.*; *Decemviri.*; *Curatores.* |
| 222 | orange | litterae | What small red tag, attached to a Roman scroll, identifies its title and author? | Titulus | *Ligula.*; *Index.*; *Libellus.* |

## The 38 questions easiest for Gemma 4 e2b (3/3 correct)

| id | difficulty | category | question (EN) | gold answer (EN) | Gemma4:e2b's 3 rollout answers |
|---|---|---|---|---|---|
| 29 | orange | historia | In which town of Africa did Marcus Cato take his own life? | At Utica | *Utica.*; *Utica.*; *Utica.* |
| 34 | orange | religio | Which goddess, born of the blue sea, dwells in Idalium, Amathus, and Golgi according to Catullus? | Venus | *Venus.*; *Venus.*; *Venus.* |
| 40 | blue | mythos | What son do the Fates sing will be born to Peleus and Thetis? | Achilles | *Achilles.*; *Achilles.*; *Achilles.* |
| 51 | green | historia | On which Ides, according to Cicero's letter to Cassius reported in Macrobius, was the dictator Caesar slain? | On the Ides of March | *Idus Martii.*; *Idibus Martiis.*; *Idus Martiis.* |
| 70 | blue | mythos | Which hero, who had a swift wing on each foot, had Andromeda as his wife? | Perseus | *Perseus.*; *Perseus.*; *Perseus.* |
| 74 | blue | mythos | With what were the ears of Ulysses' companions sealed against the Sirens' song? | With smeared wax | *Cera.*; *Cera.*; *Cera (vel cera).* |
| 91 | blue | mythos | Of what metal was Cupid's arrow made that causes love? | Of gold | *Aureum.*; *Aurum.*; *Aurum.* |
| 96 | blue | mythos | Whose riddle did Oedipus solve? | The Sphinx's | *Sphinx.*; *Sphinx.*; *Sphinx.* |
| 97 | orange | litterae | To which emperor did Pliny the Younger address his letters of the tenth book, and from whom he received replies in turn? | To Trajan | *Traianus.*; *Traianus.*; *Traianus.* |
| 101 | blue | geographia | Under which mountain does Pliny say the town of Delphi, with its most famous oracle of Apollo, is situated? | Under Mount Parnassus | *Parnassus.*; *Parnassum.*; *Parnassus.* |
| 102 | green | geographia | Between which two rivers does Pliny say the region of Mesopotamia lies? | Between the Euphrates and the Tigris | *Tigris et Euphrate.*; *Tigris et Euphrate.*; *Tigris et Euphrate.* |
| 109 | blue | historia | By what name did Nero call his huge house stretching from the Palatine to the Esquiline? | The Golden (the Domus Aurea) | *Domus Aurea.*; *Domus Aurea.*; *Domus Aurea.* |
| 110 | orange | historia | Which city did Titus, left to subdue Judaea, capture in the final assault? | Jerusalem | *Ierusalem.*; *Ierusalem.*; *Ierusalem.* |
| 112 | blue | litterae | Into how many books did Vergil arrange the Aeneid? | Into twelve books | *Duodecim.*; *Duodecim.*; *Duodecim.* |
| 118 | blue | religio | What is the title for the highest religious position in Ancient Rome? | Pontifex Maximus | *Pontifex Maximus.*; *Pontifex Maximus.*; *Pontifex Maximus.* |
| 121 | blue | religio | What is the name of the small domestic shrine found in Ancient Roman homes where families worship their household gods and spirits? | (the) Lararium | *Lararium.*; *Lararium.*; *Lararium.* |
| 124 | blue | mores | What is the name for the shallow basin in the atrium floor that collected rainwater? | Impluvium | *Impluvium.*; *Impluvium.*; *Impluvium.* |
| 125 | blue | mores | In which room do family members recline on couches to eat? | Triclinium | *Triclinio.*; *Triclinio.*; *Triclinio.* |
| 126 | orange | mores | What is the name of the subfloor system used to heat the floor and walls of Roman villas? | Hypocaustum | *Hypocaustum.*; *Hypocaustum.*; *Hypocaustum.* |
| 129 | green | geographia | What is the main river that flows through Rome? | Tiber | *Tiberis.*; *Tiber.*; *Tiber.* |
| 130 | red | geographia | What body of water separates the province of Hispania from the coast of Mauretania? | Fretum Gaditanum | *Straitum Gibraltarum.*; *Straitum Gibraltarum.*; *Straitum Gibraltarum.* |
| 133 | blue | geographia | On which hill of Rome did Augustus and many other emperors place their palaces? | Palatine | *Palatinus.*; *Palatinus.*; *Palatinus.* |
| 149 | blue | mores | What room does a Roman bather enter after the tepidarium and caldarium? | Frigidarium | *Frigidarium.*; *Frigidarium.*; *Frigidarium.* |
| 151 | orange | mores | What is the name of the underground sewer system that drains waste from Rome into the Tiber River? | Cloaca Maxima | *Cloaca Maxima.*; *Cloaca Maxima.*; *Cloaca Maxima.* |
| 152 | green | mores | What structure carries water across valleys into Roman cities? | Aqueduct | *Aquae ductus.*; *Aquaeductus.*; *Aquaeductus.* |
| 155 | green | mores | What famous road connects Rome to Brindisi? | Via Appia | *Via Appia (vel viae ad mare).*; *Via Appia (vel viae ad Adriatum).*; *Via Appia.* |
| 156 | blue | mores | What is the name of the fast, oared warship with three banks of oars that is a staple in the Roman navy? | Trireme | *Trireme.*; *Trireme.*; *Trireme.* |
| 160 | red | mores | What Roman device uses water to measure the hours? | Clepsydra | *Clepsydra.*; *Clepsydra.*; *Clepsydra.* |
| 178 | green | mores | What is the name of the Roman goddess of marriage and childbirth, often invoked at weddings? | Juno | *Juno.*; *Juno.*; *Juno.* |
| 182 | blue | historia | What defensive formation involves legionaries interlocking their shields overhead and on all sides? | Testudo | *Testudo.*; *Testudo.*; *Testudo vel murus scuti.* |
| 194 | orange | historia | What is the name of the sequential ladder of public offices a Roman politician has to climb? | Cursus honorum | *Cursus honorum.*; *Cursus honorum.*; *Cursus honorum.* |
| 201 | blue | mores | What is the standard silver coin of Rome, originally worth ten bronze asses? | Denarius | *Denarius.*; *Denarius.*; *Denarius.* |
| 214 | green | historia | Who was the third member of the informal alliance that included Julius Caesar and Crassus? | Pompey | *Pompeius.*; *Pompeius.*; *Pompeius.* |
| 217 | orange | historia | What battle in 53 BC resulted in Crassus's death? | Carrhae | *Carrhae.*; *Carrhae.*; *In Carrhae.* |
| 220 | green | litterae | What Roman poet wrote the Georgics and the Aeneid? | Virgil | *Virgil.*; *Virgilius.*; *Virgilus.* |
| 223 | green | litterae | In the Aeneid, what Carthaginian queen fell tragically in love with Aeneas and killed herself after he abandoned her? | Dido | *Dido.*; *Dido.*; *Dido.* |
| 228 | blue | ius | What was Rome's first written law code, inscribed on bronze and displayed in the Forum in 449 BC? | Twelve Tables | *Leges XII Tabularum.*; *Leges Duodecim Tabularum.*; *Lex Duodecim Tabularum.* |
| 229 | blue | ius | What term describes the absolute legal authority a father held over his children and descendants? | Patria potestas | *Patria potestas.*; *Patria potestas.*; *Patria potestas.* |

## Caveats

- "Least answerable" / "easiest" are defined by strict 0/3 and 3/3 splits over only 3 rollouts each; a question at 1/3 or 2/3 for either model isn't captured here even though it's also informative.
- The LLM judge (`gemma4:31b`) accepts substantive-fact equivalence, not exact strings — visible above in cases like *Straitum Gibraltarum* / *Fretum Gaditanum* or *Idus Martii* / *Idibus Martiis* being marked correct despite orthographic differences.
- Both models were run closed-book with the same 4-shot Latin demo pool and prompt; the comparison isolates parameter count (and reasoning effort — Qwen took ~34x longer per answer on average) rather than data or prompting differences.
