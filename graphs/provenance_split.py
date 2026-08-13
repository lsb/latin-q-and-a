#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["matplotlib>=3.11"]
# ///
"""provenance-split: corpus-anchored questions against homemade ones.

The 139 pairs divide almost exactly in half by how they were made. 70 are
corpus-anchored -- extracted from a real text in the Latin Library, LacusCurtius
or Bibliotheca Augustana, with a locus you can look up. 69 are homemade
cultural pairs, written against a citation (mostly Wikipedia) rather than
lifted from a passage. The split is visible in the provenance field and
coincides with the compiler: Lee extracted, Vivienne and Marisa composed.

Each model is one dumbbell: solve rate on each half, joined. What the gap does
across the range is the question. A constant offset would mean the homemade
half is simply easier. A gap that widens with capability means the two halves
are different in kind -- that the models are being asked to do something else,
not merely something easier.

Solve rate is pass@3: the question counts as solved if any of the three
rollouts was judged correct.

    ./provenance_split.py
    ./provenance_split.py --qa unified_q_and_a.jsonl --eval eval-reviewed
"""

import argparse
import collections
from pathlib import Path

import evaldata as E

HERE = Path(__file__).parent

# Categorical slots 1 and 2 -- the validated adjacent pair.
KINDS = [("corpus-anchored", "#2a78d6"), ("homemade", "#eb6834")]


def kind_of(row):
    return "homemade" if "homemade document" in row.get("provenance", "") else "corpus-anchored"


def tabulate(qa_path, eval_dir):
    qa = {E.qid_of(r): r for r in E.load(qa_path)}
    jud = {(r["model"], r["qid"], r["rollout"]): r["same"]
           for r in E.load(Path(eval_dir) / "judgments.jsonl")}
    cells = collections.defaultdict(list)
    for r in E.load(Path(eval_dir) / "answers.jsonl"):
        if r["model"] in set(E.MODELS) and r["qid"] in qa and r["rollout"] < 3:
            cells[(r["model"], r["qid"])].append(r)
    cells = {k: v for k, v in cells.items()
             if all((k[0], k[1], r["rollout"]) in jud for r in v)}

    out = {}
    for m in E.MODELS:
        rates = {}
        for k, _ in KINDS:
            v = [any(jud[(m, q, r["rollout"])] for r in rs)
                 for (mm, q), rs in cells.items() if mm == m and kind_of(qa[q]) == k]
            if v:
                rates[k] = 100 * sum(v) / len(v)
        if len(rates) == len(KINDS):
            out[m] = rates
    counts = collections.Counter(kind_of(r) for r in qa.values())
    return out, counts


def render_png(d, order, counts, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    fig, ax = plt.subplots(figsize=(10.5, 7.4), dpi=200)
    E.style_axes(ax, fig)
    ax.grid(False)
    ax.grid(True, axis="x", which="major", color=E.GRID, linewidth=0.6, zorder=0)

    for y, m in enumerate(order):
        a, b = d[m][KINDS[0][0]], d[m][KINDS[1][0]]
        ax.plot([a, b], [y, y], color=E.GRID, lw=2.4, zorder=3,
                solid_capstyle="round")
        for (k, c) in KINDS:
            ax.plot(d[m][k], y, "o", ms=8.5, color=c, mec=E.SURFACE, mew=1.4, zorder=5)
        gap = b - a
        ax.annotate(f"{gap:+.0f}", (max(a, b), y), textcoords="offset points",
                    xytext=(11, -3), fontsize=8.5,
                    color=E.INK if abs(gap) >= 10 else E.MUTED, zorder=6)

    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([E.LABEL[m] for m in order], fontsize=9)
    ax.tick_params(axis="y", length=0, colors=E.INK)
    ax.set_ylim(-0.8, len(order) - 0.2)
    ax.invert_yaxis()
    ax.set_xlim(-3, 103)
    ax.set_xlabel("questions solved at least once in three tries  (%)",
                  fontsize=10, color=E.MUTED)

    handles = [Line2D([], [], color=c, lw=0, marker="o", ms=8.5, mec=E.SURFACE,
                      mew=1.2, label=f"{k}  ({counts[k]} questions)")
               for k, c in KINDS]
    ax.legend(handles=handles, loc="lower right", frameon=False, fontsize=8.5,
              labelcolor=E.INK, handletextpad=0.6)

    ax.set_title("Extracted from a text, or written about one",
                 fontsize=12.5, color=E.INK, loc="left", pad=22)
    ax.text(0, 1.028, "the number beside each pair is the gap in points; "
                      "correctness uses an LLM as judge",
            transform=ax.transAxes, fontsize=8.5, color=E.MUTED)

    fig.tight_layout()
    fig.savefig(path, facecolor=E.SURFACE)
    print(f"wrote {path}")


def render_tex(d, order, counts, path):
    L = [r"\documentclass[border=6pt]{standalone}", r"\usepackage{pgfplots}",
         r"\pgfplotsset{compat=1.18}", r"\usepackage{xcolor}"]
    for i, (_, c) in enumerate(KINDS):
        L.append(rf"\definecolor{{k{i}}}{{HTML}}{{{c.lstrip('#').upper()}}}")
    L += [r"\definecolor{surface}{HTML}{FCFCFB}", r"\definecolor{ink}{HTML}{0B0B0B}",
          r"\definecolor{muted}{HTML}{52514E}", r"\definecolor{gridc}{HTML}{E8E7E3}",
          r"\begin{document}", r"\begin{tikzpicture}", r"\begin{axis}[",
          r"  width=13cm, height=11cm,",
          r"  xlabel={questions solved at least once in three tries (\%)},",
          r"  xlabel style={font=\small, color=muted},",
          r"  tick label style={font=\footnotesize, color=muted},",
          rf"  xmin=-3, xmax=103, ymin=-0.8, ymax={len(order) - 0.2},",
          r"  ytick={" + ",".join(str(i) for i in range(len(order))) + "},",
          r"  yticklabels={" + ",".join(E.LABEL[m].replace("_", chr(92) + "_")
                                        for m in order) + "},",
          r"  y dir=reverse, ytick style={draw=none},",
          r"  yticklabel style={font=\footnotesize, color=ink},",
          r"  xmajorgrids, grid style={gridc, line width=0.3pt},",
          r"  axis line style={gridc}, axis x line*=bottom, axis y line*=left,",
          r"  legend style={draw=none, font=\footnotesize, at={(0.99,0.02)},"
          r" anchor=south east},", r"]"]
    for y, m in enumerate(order):
        a, b = d[m][KINDS[0][0]], d[m][KINDS[1][0]]
        L.append(rf"\addplot[gridc, line width=1.6pt, forget plot] coordinates "
                 rf"{{({a:.2f},{y}) ({b:.2f},{y})}};")
    for i, (k, _) in enumerate(KINDS):
        pts = " ".join(f"({d[m][k]:.2f},{y})" for y, m in enumerate(order))
        L.append(rf"\addplot[only marks, mark=*, mark size=2.6pt, "
                 rf"mark options={{fill=k{i}, draw=surface, line width=0.8pt}}] "
                 rf"coordinates {{{pts}}};")
        L.append(rf"\addlegendentry{{{k} ({counts[k]} questions)}}")
    L += [r"\end{axis}", r"\end{tikzpicture}", r"\end{document}"]
    Path(path).write_text("\n".join(L) + "\n")
    print(f"wrote {path}")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--qa", default=str(E.DEFAULT_QA))
    p.add_argument("--eval", default=str(E.DEFAULT_EVAL))
    p.add_argument("--out", default=str(HERE / "provenance_split"))
    args = p.parse_args()

    d, counts = tabulate(Path(args.qa), Path(args.eval))
    order = sorted(d, key=lambda m: -sum(d[m].values()))
    print(f"{'model':24}{'corpus':>9}{'homemade':>10}{'gap':>7}")
    for m in order:
        a, b = d[m][KINDS[0][0]], d[m][KINDS[1][0]]
        print(f"{E.LABEL[m]:24}{a:9.1f}{b:10.1f}{b - a:+7.1f}")
    render_png(d, order, counts, Path(args.out + ".png"))
    render_tex(d, order, counts, Path(args.out + ".tex"))


if __name__ == "__main__":
    main()
