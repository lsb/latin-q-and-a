# /// script
# requires-python = ">=3.11,<3.14"
# dependencies = [
#   "dspy>=3.0",
#   "litellm<1.92",  # 1.92.0 ships only an sdist whose Rust build fails locally
# ]
# ///
"""Closed-book Latin QA evaluation of local Ollama models over qa.jsonl.

Everything the candidate model sees is Latin: the signature instructions, the
few-shot demos, the question. An LLM judge (qwen3.6:27b by default) then marks
whether each answer is substantially the same fact as the gold answer — string
match is not required ("'Caesar have.'" vs "Ave Caesar" counts).

Usage:
    uv run evaluate.py                          # all 10 models, all pairs, 10 rollouts, -cpu variants
    uv run evaluate.py --limit 25 --rollouts 3  # development-sized run
    uv run evaluate.py --models qwen3.5:2b,gemma4:12b
    uv run evaluate.py --no-cpu                 # full-speed (non -cpu) variants
    uv run evaluate.py --summary-only           # just re-print the table from saved results

Results are written incrementally to eval/answers.jsonl and eval/judgments.jsonl
and every run resumes from what is already there. LLM errors (failed
generations, failed judgments) are never saved: they are retried on the next
run, and error records left over from older runs are ignored on load.
"""

import argparse
import hashlib
import json
import random
import re
import sys
import time
import unicodedata
from pathlib import Path

import dspy

HERE = Path(__file__).parent

# Sheet difficulty letters, in the order they are reported.
DIFFICULTIES = {"r": "red", "o": "orange", "b": "blue", "g": "green"}

DEFAULT_MODELS = [
    "qwen3.6:27b",
    "glm-4.7-flash:latest",
    "gpt-oss:120b",
    "nemotron-3-super:120b",
    "qwen3.5:27b",
    "qwen3.5:9b",
    "qwen3.5:2b",
    "gemma4:31b",
    "gemma4:12b",
    "gemma4:e2b",
]

# Few-shot demos are drawn per question from the human-reviewed pairs
# (manually_reviewed.jsonl): seeded by the question's qid, so the same question
# always gets the same demos, and never itself.
def pick_demos(row: dict, pool: list[dict], k: int) -> list[dspy.Example]:
    self_q = normalize_latin(row["question"])
    eligible = [
        d for d in pool
        if qid_of(d) != qid_of(row) and normalize_latin(d["question"]) != self_q
    ]
    picked = random.Random(int(qid_of(row), 16)).sample(eligible, min(k, len(eligible)))
    return [
        dspy.Example(quaestio=d["question"], responsum=d["answer"]).with_inputs("quaestio")
        for d in picked
    ]


class QuaestioLatina(dspy.Signature):
    """Quaestioni de rebus Romanis litterisque Latinis sine libris responde.
    Da responsum breve ac merum Latinum, sine ambagibus, quale in exemplis vides."""

    quaestio: str = dspy.InputField(desc="interrogatum Latinum")
    responsum: str = dspy.OutputField(desc="responsum breve Latinum")


class IudexParitatis(dspy.Signature):
    """Given a Latin question, a reference answer, and a candidate answer,
    decide whether the candidate expresses substantially the same fact as the
    reference. Ignore spelling variants (u/v, i/j, accents, capitalization),
    punctuation, word order, inflection forced by different phrasing, and extra
    framing words. Extra correct detail is fine; a missing or contradicted core
    fact is not."""

    quaestio: str = dspy.InputField(desc="the Latin question")
    exemplar: str = dspy.InputField(desc="the reference (gold) answer")
    responsum: str = dspy.InputField(desc="the candidate answer")
    idem: bool = dspy.OutputField(desc="True if substantially the same fact")


JUDGE_DEMOS = [
    # Martial's parrot: no string overlap, same salutation.
    {
        "quaestio": "Quam salutationem psittacus ille per se dicere didicit apud Martialem?",
        "exemplar": "'Caesar have.'",
        "responsum": "Ave Caesar",
        "idem": True,
    },
    # Full-sentence paraphrase of a terse gold answer.
    {
        "quaestio": "In quot partes Galliam divisam esse Caesar scribit?",
        "exemplar": "In tres partes.",
        "responsum": "Gallia est omnis divisa in partes tres.",
        "idem": True,
    },
    # Same domain, wrong act.
    {
        "quaestio": "Quid facere debet, ex lege duodecim tabularum, is quem quis in ius vocat?",
        "exemplar": "Ire debet.",
        "responsum": "Antestari debet.",
        "idem": False,
    },
    # Same shape of answer, wrong offerings.
    {
        "quaestio": "Quae dona sacerdos Iano imponit, ut deus ipse apud Ovidium refert?",
        "exemplar": "Libum farraque mixta sale.",
        "responsum": "Vinum et tura.",
        "idem": False,
    },
]


MARKER_RE = re.compile(r"\[\[\s*##\s*\w+\s*##\s*\]\]")


def clean_answer(s: str) -> str:
    """Some models leak DSPy adapter markers like [[ ## completed ## ]] into the answer."""
    return MARKER_RE.sub("", s).strip()


def normalize_latin(s: str) -> str:
    """Orthography-insensitive form: lowercase, strip accents/punctuation, v→u, j→i."""
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("v", "u").replace("j", "i")
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return s.strip()


def qid_of(row: dict) -> str:
    return hashlib.sha1(f"{row['locus']}|{row['question']}".encode()).hexdigest()[:12]


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    with open(path) as f:
        for n, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:  # e.g. a run killed mid-append
                print(f"warning: {path}:{n} is not valid JSON, skipping", file=sys.stderr)
    return out


def append_jsonl(path: Path, record: dict) -> None:
    with open(path, "a") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def make_lm(model: str, args, *, judge: bool = False) -> dspy.LM:
    return dspy.LM(
        f"ollama_chat/{model}",
        api_base=args.api_base,
        api_key="",
        temperature=0.0 if judge else args.temperature,
        max_tokens=args.max_tokens,
        # Never serve responses from dspy's disk cache: answers.jsonl and
        # judgments.jsonl are the only caches we trust. A busted Ollama
        # response would otherwise be frozen and replayed forever.
        cache=False,
        num_ctx=args.num_ctx,
        timeout=args.timeout,
        num_retries=2,
    )


def generate_phase(model: str, questions: list[dict], demo_pool: list[dict],
                   done: dict, args, answers_path: Path) -> int:
    """Run every pending (question, rollout) for one model. Returns #new records."""
    lm = make_lm(model, args)
    predict = dspy.Predict(QuaestioLatina)

    todo = [
        (row, r)
        for row in questions
        for r in range(args.rollouts)
        if (model, qid_of(row), r) not in done
    ]
    if not todo:
        print(f"[{model}] generation already complete")
        return 0

    print(f"[{model}] generating {len(todo)} answers "
          f"({len(questions)} questions x {args.rollouts} rollouts, minus finished)")
    new = 0
    with dspy.context(lm=lm):
        for i, (row, rollout) in enumerate(todo, 1):
            t0 = time.time()
            predict.demos = pick_demos(row, demo_pool, args.num_demos)
            try:
                answer = clean_answer(predict(quaestio=row["question"]).responsum)
            except Exception as e:  # parse failures, timeouts — not saved, retried next run
                msg = f"{type(e).__name__}: {e}".replace("\n", " ")[:200]
                print(f"[{model}] {i}/{len(todo)} {row['locus'][:40]} r{rollout} "
                      f"({round(time.time() - t0, 2)}s) ERROR not saved: {msg}", flush=True)
                continue
            record = {
                "model": model,
                "qid": qid_of(row),
                "author": row["author"],
                "locus": row["locus"],
                "question": row["question"],
                "gold": row["answer"],
                "rollout": rollout,
                "answer": answer,
                "exact": normalize_latin(answer) == normalize_latin(row["answer"]),
                "seconds": round(time.time() - t0, 2),
            }
            append_jsonl(answers_path, record)
            done[(model, record["qid"], rollout)] = record
            new += 1
            shown = answer.replace("\n", " ")[:60]
            print(f"[{model}] {i}/{len(todo)} {row['locus'][:40]} r{rollout} "
                  f"({record['seconds']}s) -> {shown}", flush=True)
    return new


def judge_phase(records: list[dict], judged: dict, args, judgments_path: Path) -> int:
    """Judge every answer that has no verdict yet. Returns #new judgments."""
    pending = [r for r in records if (r["model"], r["qid"], r["rollout"]) not in judged]
    if not pending:
        return 0

    # Free verdicts first: normalized string matches are hits. Only genuinely
    # different strings go to the LLM judge.
    llm_pending = []
    new = 0
    for r in pending:
        if not r["exact"]:
            llm_pending.append(r)
            continue
        rec = {"model": r["model"], "qid": r["qid"], "rollout": r["rollout"],
               "same": True, "judge": "exact"}
        append_jsonl(judgments_path, rec)
        judged[(r["model"], r["qid"], r["rollout"])] = rec
        new += 1

    if llm_pending:
        judge_model = resolve(args.judge, args)
        print(f"[judge {judge_model}] judging {len(llm_pending)} answers "
              f"({new} settled by exact match)")
        lm = make_lm(judge_model, args, judge=True)
        judge = dspy.Predict(IudexParitatis)
        judge.demos = [
            dspy.Example(**d).with_inputs("quaestio", "exemplar", "responsum")
            for d in JUDGE_DEMOS
        ]
        with dspy.context(lm=lm):
            for i, r in enumerate(llm_pending, 1):
                try:
                    same = bool(judge(
                        quaestio=r["question"], exemplar=r["gold"],
                        responsum=clean_answer(r["answer"])
                    ).idem)
                except Exception as e:  # not saved, retried next run
                    msg = f"{type(e).__name__}: {e}".replace("\n", " ")[:200]
                    print(f"[judge] {i}/{len(llm_pending)} {r['model']} {r['locus'][:35]} "
                          f"r{r['rollout']}: ERROR not saved: {msg}", flush=True)
                    continue
                rec = {"model": r["model"], "qid": r["qid"], "rollout": r["rollout"],
                       "same": same, "judge": "llm"}
                append_jsonl(judgments_path, rec)
                judged[(r["model"], r["qid"], r["rollout"])] = rec
                new += 1
                print(f"[judge] {i}/{len(llm_pending)} {r['model']} {r['locus'][:35]} "
                      f"r{r['rollout']}: {same}", flush=True)
    return new


def stats_row(records: list[dict], judged: dict) -> dict:
    """Aggregate one table row (whole model, or one difficulty slice of it)."""
    per_q: dict[str, list[bool]] = {}
    seconds = []
    exact = 0
    for r in records:
        seconds.append(r["seconds"])
        exact += r["exact"]
        v = judged.get((r["model"], r["qid"], r["rollout"]))
        if v is not None:
            per_q.setdefault(r["qid"], []).append(v["same"])
    verdicts = [v for vs in per_q.values() for v in vs]
    return {
        "questions": len(per_q),
        "rollouts": len(verdicts),
        "success_pct": round(100 * sum(verdicts) / len(verdicts), 1) if verdicts else None,
        "pass_any_pct": round(
            100 * sum(any(vs) for vs in per_q.values()) / len(per_q), 1
        ) if per_q else None,
        "exact_pct": round(100 * exact / len(seconds), 1) if seconds else None,
        "mean_seconds": round(sum(seconds) / len(seconds), 1) if seconds else None,
    }


def summarize(done: dict, judged: dict, outdir: Path, qa_qids: set[str],
              models: set[str], rollouts: int, qid_diff: dict[str, str],
              qid_compiler: dict[str, str]) -> None:
    done = {
        key: r for key, r in done.items()
        if r["qid"] in qa_qids and r["model"] in models and r["rollout"] < rollouts
    }
    by_model: dict[str, list[dict]] = {}
    for r in done.values():
        by_model.setdefault(r["model"], []).append(r)

    header = (f"{'model':32} {'questions':>9} {'rollouts':>8} {'success%':>8} "
              f"{'pass@any%':>9} {'exact%':>6} {'s/ans':>6}")

    def print_row(label: str, row: dict) -> None:
        def fmt(x):
            return x if x is not None else "-"
        print(f"{label:32} {row['questions']:>9} {row['rollouts']:>8} "
              f"{fmt(row['success_pct']):>8} {fmt(row['pass_any_pct']):>9} "
              f"{fmt(row['exact_pct']):>6} {fmt(row['mean_seconds']):>6}")

    print("\n" + header)
    print("-" * len(header))
    summary = {}
    for model, records in sorted(by_model.items()):
        row = stats_row(records, judged)
        summary[model] = row
        print_row(model, row)
        for key, qid_map, labels in (
            ("by_difficulty", qid_diff, list(DIFFICULTIES.values())),
            ("by_compiler", qid_compiler, sorted(set(qid_compiler.values()))),
        ):
            sliced = {}
            for label in labels:
                subset = [r for r in records if qid_map.get(r["qid"]) == label]
                if subset:
                    sliced[label] = stats_row(subset, judged)
                    print_row(f"  {label}", sliced[label])
            if sliced:
                row[key] = sliced
    with open(outdir / "summary.json", "w") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"\nsummary written to {outdir / 'summary.json'}")


def resolve(model: str, args) -> str:
    """In development we run the -cpu Ollama variants to keep the GPU free."""
    return model if args.no_cpu else f"{model}-cpu"


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--models", default=",".join(DEFAULT_MODELS),
                   help="comma-separated Ollama models (base names, without -cpu)")
    p.add_argument("--judge", default="qwen3.6:27b")
    p.add_argument("--rollouts", type=int, default=10)
    p.add_argument("--limit", type=int, default=None,
                   help="evaluate a random sample of N questions (seeded, stable)")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--no-cpu", action="store_true",
                   help="use full-speed model variants instead of -cpu (development default)")
    p.add_argument("--temperature", type=float, default=0.7)
    p.add_argument("--max-tokens", type=int, default=65536,
                   help="generation budget; generous so thinking models can finish")
    p.add_argument("--num-ctx", type=int, default=81920,
                   help="context window; must hold prompt + max-tokens")
    p.add_argument("--timeout", type=int, default=7200)
    p.add_argument("--api-base", default="http://localhost:11434")
    p.add_argument("--qa", default=str(HERE / "qa.jsonl"))
    p.add_argument("--demo-file", default=str(HERE / "manually_reviewed.jsonl"),
                   help="pool of human-reviewed pairs used as few-shot demos")
    p.add_argument("--num-demos", type=int, default=4)
    p.add_argument("--outdir", default=str(HERE / "eval"))
    p.add_argument("--summary-only", action="store_true")
    p.add_argument("--debug", action="store_true",
                   help="log every raw LLM request/response via litellm")
    args = p.parse_args()

    if args.debug:
        import litellm
        litellm._turn_on_debug()

    outdir = Path(args.outdir)
    outdir.mkdir(exist_ok=True)
    answers_path = outdir / "answers.jsonl"
    judgments_path = outdir / "judgments.jsonl"

    # Error records from older runs are ignored, so those slots get retried.
    done = {
        (r["model"], r["qid"], r["rollout"]): r
        for r in load_jsonl(answers_path) if r.get("answer") is not None
    }
    judged = {
        (r["model"], r["qid"], r["rollout"]): r
        for r in load_jsonl(judgments_path)
        # Keep only real verdicts; legacy error records (answer failed to
        # generate, judge failed) are dropped so those slots are redone.
        if r.get("same") is not None and r.get("judge") in ("exact", "llm")
    }

    rows = load_jsonl(Path(args.qa))
    if args.limit is not None and args.limit < len(rows):
        picked = random.Random(args.seed).sample(range(len(rows)), args.limit)
        rows = [rows[i] for i in sorted(picked)]
    qa_qids = {qid_of(row) for row in rows}
    models = [resolve(m.strip(), args) for m in args.models.split(",") if m.strip()]

    # Difficulty ratings (r/o/b/g) and compiler (Lee/Vivienne) carried on the
    # evaluated QA rows, if any.
    qid_diff = {
        qid_of(r): DIFFICULTIES[r["difficulty"]]
        for r in rows if r.get("difficulty") in DIFFICULTIES
    }
    qid_compiler = {
        qid_of(r): r["compiled_by"].strip()
        for r in rows if r.get("compiled_by", "").strip()
    }

    if args.summary_only:
        summarize(done, judged, outdir, qa_qids, set(models), args.rollouts,
                  qid_diff, qid_compiler)
        return

    demo_pool = load_jsonl(Path(args.demo_file))
    if len(demo_pool) <= args.num_demos:
        sys.exit(f"demo pool {args.demo_file} has only {len(demo_pool)} pairs")
    print(f"{len(rows)} questions, {args.rollouts} rollouts, "
          f"models: {args.models} ({'full-speed' if args.no_cpu else '-cpu dev variants'})")

    for model in models:
        try:
            generate_phase(model, rows, demo_pool, done, args, answers_path)
        except KeyboardInterrupt:
            print(f"\ninterrupted during {model}; progress saved, rerun to resume")
            sys.exit(130)
        # Judge right after each model so at most one model swap per phase.
        judge_phase([r for r in done.values() if r["model"] == model],
                    judged, args, judgments_path)

    summarize(done, judged, outdir, qa_qids, set(models), args.rollouts,
              qid_diff, qid_compiler)


if __name__ == "__main__":
    main()
