#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["matplotlib>=3.11"]
# ///
"""co-failure: do the models miss the same questions, or different ones?

Every pair of models is scored by the phi coefficient between their per-question
outcomes -- solved at least once in three tries, or not. Phi is the correlation
of two binary vectors, so unlike a raw overlap it is not inflated by two weak
models both failing nearly everything: it asks whether they agree more than
their individual pass rates alone would predict.

Read high blue as "these two rise and fall together" -- one difficulty axis
shared between them. Read pale as "these two fail independently", which means
the benchmark is testing something different in each. Red would be an inverse
relationship: what one gets, the other misses.

The diagonal is left blank; a model correlates perfectly with itself and would
otherwise set the colour scale on its own.

    ./co_failure.py
    ./co_failure.py --qa unified_q_and_a.jsonl --eval eval-reviewed
"""

import argparse
import collections
import math
from pathlib import Path

import evaldata as E

HERE = Path(__file__).parent

# Diverging: two hues that read as opposite, with a neutral midpoint that reads
# as "nothing". Blue and red are the documented pair; the midpoint is gray.
NEG, MID, POS = "#e34948", "#f0efec", "#2a78d6"


def phi(xs, ys):
    n11 = sum(1 for a, b in zip(xs, ys) if a and b)
    n10 = sum(1 for a, b in zip(xs, ys) if a and not b)
    n01 = sum(1 for a, b in zip(xs, ys) if not a and b)
    n00 = sum(1 for a, b in zip(xs, ys) if not a and not b)
    d = math.sqrt((n11 + n10) * (n01 + n00) * (n11 + n01) * (n10 + n00))
    return (n11 * n00 - n10 * n01) / d if d else 0.0


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
    solved = {k: any(jud[(k[0], k[1], r["rollout"])] for r in rs)
              for k, rs in cells.items()}

    models = [m for m in E.MODELS if any(mm == m for mm, _ in solved)]
    # Only questions every model was scored on, so each pair is compared over
    # the same set rather than whatever each happens to have.
    common = set.intersection(*[{q for (mm, q) in solved if mm == m} for m in models])
    rate = {m: sum(solved[(m, q)] for q in common) / len(common) for m in models}
    order = sorted(models, key=lambda m: -rate[m])
    vec = {m: [solved[(m, q)] for q in sorted(common)] for m in order}
    mat = [[None if a == b else phi(vec[a], vec[b]) for b in order] for a in order]
    return order, mat, len(common), rate


def render_png(order, mat, n, rate, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap

    cmap = LinearSegmentedColormap.from_list("div", [NEG, MID, POS])
    lim = max(abs(v) for row in mat for v in row if v is not None)

    fig, ax = plt.subplots(figsize=(10.4, 8.6), dpi=200)
    fig.patch.set_facecolor(E.SURFACE)
    ax.set_facecolor(E.SURFACE)

    k = len(order)
    for i in range(k):
        for j in range(k):
            v = mat[i][j]
            if v is None:
                continue
            ax.add_patch(plt.Rectangle((j - 0.46, i - 0.46), 0.92, 0.92,
                                       facecolor=cmap(0.5 + 0.5 * v / lim),
                                       edgecolor=E.SURFACE, linewidth=1.0))
    ax.set_xlim(-0.6, k - 0.4)
    ax.set_ylim(-0.6, k - 0.4)
    ax.invert_yaxis()
    ax.set_xticks(range(k))
    ax.set_yticks(range(k))
    ax.set_xticklabels([E.LABEL[m] for m in order], rotation=45, ha="right",
                       fontsize=8.5, color=E.INK)
    ax.set_yticklabels([E.LABEL[m] for m in order], fontsize=8.5, color=E.INK)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)

    sm = plt.cm.ScalarMappable(cmap=cmap,
                               norm=plt.Normalize(vmin=-lim, vmax=lim))
    cb = fig.colorbar(sm, ax=ax, fraction=0.035, pad=0.03)
    cb.set_label("phi correlation of per-question outcomes", fontsize=9,
                 color=E.MUTED)
    cb.ax.tick_params(colors=E.MUTED, labelsize=8)
    cb.outline.set_visible(False)

    ax.set_title("Do the models fail on the same questions?",
                 fontsize=12.5, color=E.INK, loc="left", pad=16)
    ax.text(0, 1.02, f"pairwise over the {n} questions every model was scored on; "
                     f"models ordered by solve rate",
            transform=ax.transAxes, fontsize=8.5, color=E.MUTED)

    fig.tight_layout()
    fig.savefig(path, facecolor=E.SURFACE)
    print(f"wrote {path}")


def render_tex(order, mat, n, path):
    lim = max(abs(v) for row in mat for v in row if v is not None)
    k = len(order)
    L = [r"\documentclass[border=6pt]{standalone}", r"\usepackage{pgfplots}",
         r"\pgfplotsset{compat=1.18}", r"\usepackage{xcolor}",
         rf"\definecolor{{neg}}{{HTML}}{{{NEG.lstrip('#').upper()}}}",
         rf"\definecolor{{mid}}{{HTML}}{{{MID.lstrip('#').upper()}}}",
         rf"\definecolor{{pos}}{{HTML}}{{{POS.lstrip('#').upper()}}}",
         r"\definecolor{ink}{HTML}{0B0B0B}", r"\definecolor{muted}{HTML}{52514E}",
         r"\pgfplotsset{colormap={div}{color=(neg) color=(mid) color=(pos)}}",
         r"\begin{document}", r"\begin{tikzpicture}", r"\begin{axis}[",
         r"  width=13cm, height=12cm, enlargelimits=false, colormap name=div,",
         rf"  point meta min={-lim:.4f}, point meta max={lim:.4f},",
         r"  colorbar, colorbar style={font=\footnotesize, color=muted,",
         r"    ylabel={phi correlation}, ylabel style={font=\footnotesize}},",
         r"  xtick={" + ",".join(str(i) for i in range(k)) + "},",
         r"  ytick={" + ",".join(str(i) for i in range(k)) + "},",
         r"  xticklabels={" + ",".join(E.LABEL[m].replace("_", chr(92) + "_")
                                       for m in order) + "},",
         r"  yticklabels={" + ",".join(E.LABEL[m].replace("_", chr(92) + "_")
                                       for m in order) + "},",
         r"  xticklabel style={rotate=45, anchor=north east, font=\tiny, color=ink},",
         r"  yticklabel style={font=\tiny, color=ink},",
         r"  tick style={draw=none}, y dir=reverse, axis line style={draw=none},",
         r"]",
         r"\addplot[matrix plot*, point meta=explicit] table[meta=v] {",
         r"x y v"]
    for i in range(k):
        for j in range(k):
            v = mat[i][j]
            if v is not None:
                L.append(f"{j} {i} {v:.4f}")
        L.append("")
    L += [r"};", r"\end{axis}", r"\end{tikzpicture}", r"\end{document}"]
    Path(path).write_text("\n".join(L) + "\n")
    print(f"wrote {path}")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--qa", default=str(E.DEFAULT_QA))
    p.add_argument("--eval", default=str(E.DEFAULT_EVAL))
    p.add_argument("--out", default=str(HERE / "co_failure"))
    args = p.parse_args()

    order, mat, n, rate = tabulate(Path(args.qa), Path(args.eval))
    vals = [v for row in mat for v in row if v is not None]
    print(f"{len(order)} models over {n} common questions; "
          f"phi {min(vals):.2f} .. {max(vals):.2f}")
    pairs = sorted(((mat[i][j], order[i], order[j])
                    for i in range(len(order)) for j in range(i + 1, len(order))),
                   reverse=True)
    print("\nmost alike:")
    for v, a, b in pairs[:4]:
        print(f"  {v:+.2f}  {E.LABEL[a]} / {E.LABEL[b]}")
    print("least alike:")
    for v, a, b in pairs[-4:]:
        print(f"  {v:+.2f}  {E.LABEL[a]} / {E.LABEL[b]}")
    render_png(order, mat, n, rate, Path(args.out + ".png"))
    render_tex(order, mat, n, Path(args.out + ".tex"))


if __name__ == "__main__":
    main()
