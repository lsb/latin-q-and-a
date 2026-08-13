"""Shared loading and styling for the evaluation graphs.

Every graph reads the same three things -- a QA jsonl naming the questions, an
eval directory holding answers.jsonl and judgments.jsonl, and the model list --
so they live here once rather than in each script.
"""

import collections
import hashlib
import json
import statistics
from pathlib import Path

REPO = Path(__file__).parent.parent

MODELS = ("hf.co/LiquidAI/LFM2.5-2.6B-GGUF:Q8_0,hf.co/LiquidAI/LFM2.5-230M-GGUF:Q8_0,"
          "qwen2.5:0.5b,qwen2.5:1.5b,qwen2.5:3b,qwen2.5:7b,qwen2.5:32b,gemma4:e2b,"
          "gemma4:12b,gemma4:31b,qwen3:4b-thinking-2507-q4_K_M,qwen3:4b-instruct-2507-q4_K_M,"
          "qwen3:30b-a3b-thinking-2507-q4_K_M,qwen3:30b-a3b-instruct-2507-q4_K_M,"
          "qwen3.6:27b").split(",")

# Total parameters in billions. 30b-a3b is a 30B mixture with 3B active per
# token -- counted at its full 30B, which is what it costs to hold in memory.
PARAMS = {
    "hf.co/LiquidAI/LFM2.5-230M-GGUF:Q8_0": 0.23,
    "hf.co/LiquidAI/LFM2.5-2.6B-GGUF:Q8_0": 2.6,
    "qwen2.5:0.5b": 0.5, "qwen2.5:1.5b": 1.5, "qwen2.5:3b": 3.0,
    "qwen2.5:7b": 7.0, "qwen2.5:32b": 32.0,
    "gemma4:e2b": 2.0, "gemma4:12b": 12.0, "gemma4:31b": 31.0,
    "qwen3:4b-thinking-2507-q4_K_M": 4.0, "qwen3:4b-instruct-2507-q4_K_M": 4.0,
    "qwen3:30b-a3b-thinking-2507-q4_K_M": 30.0,
    "qwen3:30b-a3b-instruct-2507-q4_K_M": 30.0,
    "qwen3.6:27b": 27.0,
}

# Every label names its family and its size, so no model is identifiable only
# by its colour.
LABEL = {
    "hf.co/LiquidAI/LFM2.5-2.6B-GGUF:Q8_0": "LFM2.5 2.6B",
    "hf.co/LiquidAI/LFM2.5-230M-GGUF:Q8_0": "LFM2.5 230M",
    "qwen2.5:0.5b": "qwen2.5 0.5B", "qwen2.5:1.5b": "qwen2.5 1.5B",
    "qwen2.5:3b": "qwen2.5 3B", "qwen2.5:7b": "qwen2.5 7B",
    "qwen2.5:32b": "qwen2.5 32B",
    "gemma4:e2b": "gemma4 e2b", "gemma4:12b": "gemma4 12B",
    "gemma4:31b": "gemma4 31B",
    "qwen3:4b-thinking-2507-q4_K_M": "qwen3 4B think",
    "qwen3:4b-instruct-2507-q4_K_M": "qwen3 4B instruct",
    "qwen3:30b-a3b-thinking-2507-q4_K_M": "qwen3 30B-A3B think",
    "qwen3:30b-a3b-instruct-2507-q4_K_M": "qwen3 30B-A3B instruct",
    "qwen3.6:27b": "qwen3.6 27B",
}

# Validated for all-pairs scatter on the light surface: worst CVD dE 9.2, worst
# normal-vision dE 16.3. A fifth hue fails the CVD floor, so qwen3.6 -- the one
# model with no family -- is drawn in ink instead.
FAMILY = {
    "qwen2.5":  ("#2a78d6", ["qwen2.5:0.5b", "qwen2.5:1.5b", "qwen2.5:3b",
                             "qwen2.5:7b", "qwen2.5:32b"]),
    "gemma4":   ("#eb6834", ["gemma4:e2b", "gemma4:12b", "gemma4:31b"]),
    "qwen3":    ("#1baf7a", ["qwen3:4b-instruct-2507-q4_K_M",
                             "qwen3:30b-a3b-instruct-2507-q4_K_M",
                             "qwen3:4b-thinking-2507-q4_K_M",
                             "qwen3:30b-a3b-thinking-2507-q4_K_M"]),
    "LFM2.5":   ("#4a3aa7", ["hf.co/LiquidAI/LFM2.5-230M-GGUF:Q8_0",
                             "hf.co/LiquidAI/LFM2.5-2.6B-GGUF:Q8_0"]),
}
UNAFFILIATED = {"qwen3.6:27b": "#0b0b0b"}

SURFACE, INK, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e8e7e3"

DEFAULT_QA = REPO / "august_final.jsonl"
DEFAULT_EVAL = REPO / "other"


def colors():
    c = {m: col for _, (col, ms) in FAMILY.items() for m in ms}
    c.update(UNAFFILIATED)
    return c


def load(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def qid_of(row):
    return hashlib.sha1(f"{row['locus']}|{row['question']}".encode()).hexdigest()[:12]


def read(qa_path, eval_dir, models=None, rollouts=3):
    """Per-model pass@1, pass@3, and the raw per-answer latencies.

    Returns {model: {pass1, pass3, seconds: [...], questions}}. `seconds` is
    every individual answer's wall-clock, unsummarized, so a caller can take a
    mean, a median, or the whole distribution.
    """
    models = list(models or MODELS)
    qids = {qid_of(r) for r in load(qa_path)}
    jud = {(r["model"], r["qid"], r["rollout"]): r["same"]
           for r in load(Path(eval_dir) / "judgments.jsonl")}
    cells = collections.defaultdict(list)
    for r in load(Path(eval_dir) / "answers.jsonl"):
        if r["model"] in set(models) and r["qid"] in qids and r["rollout"] < rollouts:
            cells[(r["model"], r["qid"])].append(r)

    out = {}
    for m in models:
        groups = [v for (mm, _), v in cells.items() if mm == m]
        if not groups:
            continue
        flat = [r for g in groups for r in g]
        verdicts = [bool(jud[(m, r["qid"], r["rollout"])]) for r in flat]
        anyc = [any(bool(jud[(m, r["qid"], r["rollout"])]) for r in g) for g in groups]
        secs = [r["seconds"] for r in flat]
        out[m] = {
            "pass1": 100 * sum(verdicts) / len(verdicts),
            "pass3": 100 * sum(anyc) / len(anyc),
            "seconds": secs,
            "mean_s": statistics.mean(secs),
            "median_s": statistics.median(secs),
            "questions": len(groups),
        }
    return out


def style_axes(ax, fig=None):
    """Recessive grid and axes on the chart surface."""
    if fig is not None:
        fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    ax.grid(True, which="major", color=GRID, linewidth=0.6, zorder=0)
    ax.grid(True, which="minor", color=GRID, linewidth=0.3, alpha=0.6, zorder=0)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID)
        ax.spines[s].set_linewidth(0.8)
    ax.tick_params(colors=MUTED, labelsize=9)
