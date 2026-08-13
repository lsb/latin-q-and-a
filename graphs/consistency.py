#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["matplotlib>=3.11"]
# ///
"""consistency: whether a model's three tries agree, and whether they are right.

Each question a model saw produces one of five outcomes across its 3 rollouts:

    all 3 right        knows it
    mixed              got there sometimes
    wrong, one belief  same wrong answer 3x -- a confident error
    wrong, two         two of the three agreed
    wrong, three       three different wrong answers -- guessing

The bars diverge at pass@3: left of the rule the model reached the answer at
least once, right of it never. That alignment is the point. Every model's
wrong-side segments start at the same x, so the mix of conviction and guessing
can be read straight down the column without accuracy shifting it sideways.
Segments run as one spectrum, all-right at the far left through to
three-different at the far right.

"Same answer" means the same *meaning*, not the same bytes -- 'Praecones' and
'Praeconibus' are one belief. Correct answers are equivalent to each other by
transitivity (both equal the gold), and wrong answers identical after
normalisation are trivially one; everything else was adjudicated by a Latin
reader and lives in semantic_clusters.jsonl. Byte comparison alone undercounts
agreement badly: it puts confident errors at 12.1% of all-wrong cells where
reading the Latin puts them at 19.7%.

    ./consistency.py
    ./consistency.py --qa unified_q_and_a.jsonl --eval eval-reviewed
"""

import argparse
import collections
import json
import re
import unicodedata
from pathlib import Path

import evaldata as E

HERE = Path(__file__).parent

# Two one-hue ordinal ramps, each validated with --ordinal on the light surface:
# blue for the solved side, orange for the never-solved side. Ordered outward
# from the divider so the whole bar reads as a single spectrum.
LEFT = [("right3", "#2a78d6", "all 3 right"),
        ("mixed",  "#86b6ef", "mixed")]
RIGHT = [("wrong1", "#a8420c", "wrong, one belief 3×"),
         ("wrong2", "#dd6b33", "wrong, two beliefs"),
         ("wrong3", "#ee9a6a", "wrong, three different")]


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("v", "u").replace("j", "i")
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def tabulate(qa_path, eval_dir, clusters_path):
    """Five-way outcome counts per model, over the questions in qa_path."""
    adjudicated = {}
    for r in E.load(clusters_path):
        adjudicated[(r["model"], r["qid"])] = r["clusters"]

    qids = {E.qid_of(r) for r in E.load(qa_path)}
    jud = {(r["model"], r["qid"], r["rollout"]): r["same"]
           for r in E.load(Path(eval_dir) / "judgments.jsonl")}
    cells = collections.defaultdict(list)
    for r in E.load(Path(eval_dir) / "answers.jsonl"):
        if r["model"] in set(E.MODELS) and r["qid"] in qids and r["rollout"] < 3:
            cells[(r["model"], r["qid"])].append(r)

    counts = collections.defaultdict(collections.Counter)
    missing = 0
    for (m, q), rs in cells.items():
        wrong = [r for r in rs if not jud[(m, q, r["rollout"])]]
        n_right = len(rs) - len(wrong)
        if n_right == len(rs):
            seg = "right3"
        elif n_right:
            seg = "mixed"
        else:
            if len(wrong) < 2:
                k = len(wrong)
            elif len({norm(r["answer"]) for r in wrong}) == 1:
                k = 1
            else:
                cl = adjudicated.get((m, q))
                if cl is None:
                    missing += 1
                    continue
                k = len(set(cl.values()))
            seg = {1: "wrong1", 2: "wrong2", 3: "wrong3"}[k]
        counts[m][seg] += 1
    if missing:
        print(f"warning: {missing} all-wrong cells have no adjudication, excluded")
    return counts


def render_png(counts, order, path, questions):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    fig, ax = plt.subplots(figsize=(11.5, 7.6), dpi=200)
    E.style_axes(ax, fig)
    ax.grid(False)
    ax.grid(True, axis="x", which="major", color=E.GRID, linewidth=0.6, zorder=0)

    ys = range(len(order))
    for y, m in zip(ys, order):
        c = counts[m]
        # left arm: mixed abuts the rule, all-3-right beyond it
        x = 0.0
        for key, col, _ in LEFT:
            w = c[key]
            if w:
                ax.barh(y, -w, left=x, height=0.66, color=col,
                        edgecolor=E.SURFACE, linewidth=1.0, zorder=4)
            x -= w
        # right arm: one-belief abuts the rule, three-different furthest out
        x = 0.0
        for key, col, _ in RIGHT:
            w = c[key]
            if w:
                ax.barh(y, w, left=x, height=0.66, color=col,
                        edgecolor=E.SURFACE, linewidth=1.0, zorder=4)
            x += w

    ax.axvline(0, color=E.INK, lw=1.4, zorder=6)
    ax.set_yticks(list(ys))
    ax.set_yticklabels([E.LABEL[m] for m in order], fontsize=9)
    ax.tick_params(axis="y", length=0, colors=E.INK)
    ax.set_ylim(-0.8, len(order) - 0.2)
    ax.invert_yaxis()

    lim = max(max(sum(counts[m][k] for k, _, _ in LEFT),
                  sum(counts[m][k] for k, _, _ in RIGHT)) for m in order)
    lim = (lim // 10 + 1) * 10
    ax.set_xlim(-lim, lim)
    ticks = [t for t in range(-lim, lim + 1, 20)]
    ax.set_xticks(ticks)
    ax.set_xticklabels([str(abs(t)) for t in ticks])
    ax.set_xlabel(f"questions  (of {questions})", fontsize=10, color=E.MUTED)

    ax.text(-lim * 0.5, -0.95, "◄  solved at least once", fontsize=9,
            color=E.MUTED, ha="center")
    ax.text(lim * 0.5, -0.95, "never solved  ►", fontsize=9, color=E.MUTED,
            ha="center")

    # Legend order follows the spectrum left-to-right, and sits under the axis:
    # the long bottom bars run the full width, leaving no room inside the plot.
    handles = [Patch(facecolor=c, edgecolor=E.SURFACE, label=lab)
               for _, c, lab in LEFT + RIGHT]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.085),
              ncol=5, frameon=False, fontsize=8.5, labelcolor=E.INK,
              handlelength=1.4, handletextpad=0.6, columnspacing=1.8)

    ax.set_title("Agreement across three tries at the same question",
                 fontsize=12.5, color=E.INK, loc="left", pad=26)
    ax.text(0, 1.035, "correctness uses an LLM as judge",
            transform=ax.transAxes, fontsize=8.5, color=E.MUTED)

    fig.tight_layout()
    fig.savefig(path, facecolor=E.SURFACE)
    print(f"wrote {path}")


def render_tex(counts, order, path, questions):
    lim = max(max(sum(counts[m][k] for k, _, _ in LEFT),
                  sum(counts[m][k] for k, _, _ in RIGHT)) for m in order)
    lim = (lim // 10 + 1) * 10
    segs = [(k, c, lab, -1) for k, c, lab in LEFT] + [(k, c, lab, 1) for k, c, lab in RIGHT]

    L = [r"\documentclass[border=6pt]{standalone}", r"\usepackage{pgfplots}",
         r"\pgfplotsset{compat=1.18}", r"\usepackage{xcolor}"]
    for i, (_, c, _, _) in enumerate(segs):
        L.append(rf"\definecolor{{s{i}}}{{HTML}}{{{c.lstrip('#').upper()}}}")
    L += [r"\definecolor{surface}{HTML}{FCFCFB}", r"\definecolor{ink}{HTML}{0B0B0B}",
          r"\definecolor{muted}{HTML}{52514E}", r"\definecolor{gridc}{HTML}{E8E7E3}",
          r"\begin{document}", r"\begin{tikzpicture}", r"\begin{axis}[",
          r"  width=15cm, height=11cm,", r"  xbar stacked, bar width=11pt,",
          rf"  xmin={-lim}, xmax={lim}, ymin=-0.8, ymax={len(order) - 0.2},",
          rf"  xlabel={{questions (of {questions})}},",
          r"  xlabel style={font=\small, color=muted},",
          r"  tick label style={font=\footnotesize, color=muted},",
          r"  ytick={" + ",".join(str(i) for i in range(len(order))) + "},",
          r"  yticklabels={" + ",".join(E.LABEL[m].replace("_", chr(92) + "_")
                                        for m in order) + "},",
          r"  y dir=reverse, ytick style={draw=none},",
          r"  yticklabel style={font=\footnotesize, color=ink},",
          r"  xmajorgrids, grid style={gridc, line width=0.3pt},",
          r"  axis line style={gridc}, axis x line*=bottom, axis y line*=left,",
          r"  legend style={draw=none, font=\footnotesize, at={(0.99,0.02)},"
          r" anchor=south east, legend columns=1},",
          r"  x filter/.code={\pgfmathparse{abs(\pgfmathresult)}},", r"]"]
    # stacked bars need the arms emitted from the rule outward
    for i, (key, _, lab, sign) in enumerate(segs):
        pts = " ".join(f"({sign * counts[m][key]},{j})" for j, m in enumerate(order))
        L.append(rf"\addplot[fill=s{i}, draw=surface, line width=0.5pt] "
                 rf"coordinates {{{pts}}};")
        L.append(rf"\addlegendentry{{{lab.replace('×', r'$\times$')}}}")
    L += [rf"\draw[ink, line width=1pt] (axis cs:0,-0.8) -- (axis cs:0,{len(order) - 0.2});",
          r"\end{axis}", r"\end{tikzpicture}", r"\end{document}"]
    Path(path).write_text("\n".join(L) + "\n")
    print(f"wrote {path}")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--qa", default=str(E.DEFAULT_QA))
    p.add_argument("--eval", default=str(E.DEFAULT_EVAL))
    p.add_argument("--clusters", default=str(E.REPO / "semantic_clusters.jsonl"))
    p.add_argument("--out", default=str(HERE / "consistency"))
    args = p.parse_args()

    counts = tabulate(Path(args.qa), Path(args.eval), Path(args.clusters))
    solved = lambda m: sum(counts[m][k] for k, _, _ in LEFT)
    order = sorted(counts, key=solved, reverse=True)

    print(f"{'model':24}{'right3':>8}{'mixed':>7}{'wrong1':>8}{'wrong2':>8}{'wrong3':>8}")
    for m in order:
        c = counts[m]
        print(f"{E.LABEL[m]:24}{c['right3']:>8}{c['mixed']:>7}"
              f"{c['wrong1']:>8}{c['wrong2']:>8}{c['wrong3']:>8}")

    n = sum(counts[order[0]].values())
    render_png(counts, order, Path(args.out + ".png"), n)
    render_tex(counts, order, Path(args.out + ".tex"), n)


if __name__ == "__main__":
    main()
