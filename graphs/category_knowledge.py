#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["matplotlib>=3.11"]
# ///
"""category-knowledge: which corners of Roman life the models actually know.

Solve rate by the sheet's subject category, averaged over all evaluated models,
with the strongest model marked separately so you can see whether the ordering
is a property of the subject or just of the average.

Categories thin out fast -- 22 of them over 139 questions -- so anything under
--min-questions is folded into one "other" row rather than plotted as a bar
resting on three or four questions. The fold is printed, not silent.

Solve rate is pass@3: solved if any of three rollouts was judged correct.

    ./category_knowledge.py
    ./category_knowledge.py --min-questions 8
"""

import argparse
import collections
from pathlib import Path

import evaldata as E

HERE = Path(__file__).parent

BAR = "#2a78d6"     # categorical slot 1, one series
TOP = "#eb6834"     # slot 2 for the single reference model


def tabulate(qa_path, eval_dir, min_q):
    qa = {E.qid_of(r): r for r in E.load(qa_path)}
    jud = {(r["model"], r["qid"], r["rollout"]): r["same"]
           for r in E.load(Path(eval_dir) / "judgments.jsonl")}
    cells = collections.defaultdict(list)
    for r in E.load(Path(eval_dir) / "answers.jsonl"):
        if r["model"] in set(E.MODELS) and r["qid"] in qa and r["rollout"] < 3:
            cells[(r["model"], r["qid"])].append(r)
    cells = {k: v for k, v in cells.items()
             if all((k[0], k[1], r["rollout"]) in jud for r in v)}
    solved = {k: any(jud[(k[0], k[1], r["rollout"])] for r in rs)
              for k, rs in cells.items()}

    nq = collections.Counter(r["category"] for r in qa.values())
    big = {c for c, n in nq.items() if n >= min_q}
    folded = sorted(set(nq) - big)

    def bucket(q):
        c = qa[q]["category"]
        return c if c in big else "other"

    per = collections.defaultdict(list)
    top = collections.defaultdict(list)
    best = max({m for m, _ in solved},
               key=lambda m: sum(1 for (mm, _), s in solved.items() if mm == m and s))
    for (m, q), s in solved.items():
        per[bucket(q)].append(s)
        if m == best:
            top[bucket(q)].append(s)

    rows = []
    for c in per:
        n = sum(nq[k] for k in nq if (k == c or (c == "other" and k in folded)))
        rows.append({
            "category": c if c != "other" else f"other ({len(folded)} categories)",
            "questions": n,
            "mean": 100 * sum(per[c]) / len(per[c]),
            "top": 100 * sum(top[c]) / len(top[c]) if top[c] else None,
        })
    rows.sort(key=lambda r: r["mean"])
    return rows, best, folded


def render_png(rows, best, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    fig, ax = plt.subplots(figsize=(10.5, 7.4), dpi=200)
    E.style_axes(ax, fig)
    ax.grid(False)
    ax.grid(True, axis="x", which="major", color=E.GRID, linewidth=0.6, zorder=0)

    ys = range(len(rows))
    ax.barh(list(ys), [r["mean"] for r in rows], height=0.62, color=BAR,
            edgecolor=E.SURFACE, linewidth=1.0, zorder=4)
    for y, r in zip(ys, rows):
        if r["top"] is not None:
            ax.plot(r["top"], y, "D", ms=6.5, color=TOP, mec=E.SURFACE, mew=1.3,
                    zorder=6)
        ax.annotate(f"{r['questions']}", (0, y), textcoords="offset points",
                    xytext=(-8, -3), ha="right", fontsize=8.5, color=E.MUTED)

    ax.set_yticks(list(ys))
    ax.set_yticklabels([r["category"] for r in rows], fontsize=9)
    ax.tick_params(axis="y", length=0, colors=E.INK)
    ax.set_ylim(-0.8, len(rows) - 0.2)
    ax.set_xlim(0, 100)
    ax.set_xlabel("questions solved at least once in three tries  (%)",
                  fontsize=10, color=E.MUTED)

    handles = [
        Line2D([], [], color=BAR, lw=7, label="mean over all models"),
        Line2D([], [], color=TOP, lw=0, marker="D", ms=6.5, mec=E.SURFACE, mew=1.3,
               label=E.LABEL[best]),
    ]
    ax.legend(handles=handles, loc="lower right", frameon=False, fontsize=8.5,
              labelcolor=E.INK, handletextpad=0.6)

    ax.set_title("What the models know, by subject",
                 fontsize=12.5, color=E.INK, loc="left", pad=22)
    ax.text(0, 1.028, "the figure left of each bar is how many questions it rests on; "
                      "correctness uses an LLM as judge",
            transform=ax.transAxes, fontsize=8.5, color=E.MUTED)

    fig.tight_layout()
    fig.savefig(path, facecolor=E.SURFACE)
    print(f"wrote {path}")


def render_tex(rows, best, path):
    def esc(s):
        return s.replace("_", chr(92) + "_").replace("&", chr(92) + "&")
    L = [r"\documentclass[border=6pt]{standalone}", r"\usepackage{pgfplots}",
         r"\pgfplotsset{compat=1.18}", r"\usepackage{xcolor}",
         rf"\definecolor{{bar}}{{HTML}}{{{BAR.lstrip('#').upper()}}}",
         rf"\definecolor{{top}}{{HTML}}{{{TOP.lstrip('#').upper()}}}",
         r"\definecolor{surface}{HTML}{FCFCFB}", r"\definecolor{ink}{HTML}{0B0B0B}",
         r"\definecolor{muted}{HTML}{52514E}", r"\definecolor{gridc}{HTML}{E8E7E3}",
         r"\begin{document}", r"\begin{tikzpicture}", r"\begin{axis}[",
         r"  width=13cm, height=11cm, xbar, bar width=9pt,",
         r"  xlabel={questions solved at least once in three tries (\%)},",
         r"  xlabel style={font=\small, color=muted},",
         r"  tick label style={font=\footnotesize, color=muted},",
         rf"  xmin=0, xmax=100, ymin=-0.8, ymax={len(rows) - 0.2},",
         r"  ytick={" + ",".join(str(i) for i in range(len(rows))) + "},",
         r"  yticklabels={" + ",".join(esc(r["category"]) for r in rows) + "},",
         r"  ytick style={draw=none},",
         r"  yticklabel style={font=\footnotesize, color=ink},",
         r"  xmajorgrids, grid style={gridc, line width=0.3pt},",
         r"  axis line style={gridc}, axis x line*=bottom, axis y line*=left,",
         r"  legend style={draw=none, font=\footnotesize, at={(0.99,0.02)},"
         r" anchor=south east},", r"]"]
    pts = " ".join(f"({r['mean']:.2f},{y})" for y, r in enumerate(rows))
    L.append(rf"\addplot[fill=bar, draw=surface, line width=0.5pt] coordinates {{{pts}}};")
    L.append(r"\addlegendentry{mean over all models}")
    pts = " ".join(f"({r['top']:.2f},{y})" for y, r in enumerate(rows)
                   if r["top"] is not None)
    L.append(rf"\addplot[only marks, mark=diamond*, mark size=3pt, "
             rf"mark options={{fill=top, draw=surface}}] coordinates {{{pts}}};")
    L.append(rf"\addlegendentry{{{esc(E.LABEL[best])}}}")
    L += [r"\end{axis}", r"\end{tikzpicture}", r"\end{document}"]
    Path(path).write_text("\n".join(L) + "\n")
    print(f"wrote {path}")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--min-questions", type=int, default=6,
                   help="categories with fewer questions are folded into 'other'")
    p.add_argument("--qa", default=str(E.DEFAULT_QA))
    p.add_argument("--eval", default=str(E.DEFAULT_EVAL))
    p.add_argument("--out", default=str(HERE / "category_knowledge"))
    args = p.parse_args()

    rows, best, folded = tabulate(Path(args.qa), Path(args.eval), args.min_questions)
    print(f"reference model: {E.LABEL[best]}")
    print(f"folded into 'other' ({len(folded)}): {', '.join(folded)}\n")
    print(f"{'category':38}{'n':>4}{'mean':>8}{'top':>8}")
    for r in reversed(rows):
        t = f"{r['top']:8.1f}" if r["top"] is not None else "       -"
        print(f"{r['category']:38}{r['questions']:>4}{r['mean']:8.1f}{t}")
    render_png(rows, best, Path(args.out + ".png"))
    render_tex(rows, best, Path(args.out + ".tex"))


if __name__ == "__main__":
    main()
