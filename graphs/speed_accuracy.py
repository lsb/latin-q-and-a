#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["matplotlib>=3.11"]
# ///
"""speed-accuracy: what each model costs per answer against what it gets right.

Two points per model at one x: pass@1 (any single rollout is correct) filled,
pass@3 (at least one of three is correct) hollow. The vertical stem between
them is what a second and third rollout buy you.

Lines carry the two comparisons worth making:
  solid   -- a scale ladder inside one family, small to large
  dashed  -- the same model in its instruct and thinking builds

x is the mean seconds per answer, matching what summary.json reports. For most
models the mean is close to the median; for qwen3.6:27b it is eight times
larger, because its latency is bimodal -- see latency-spread, which draws the
whole distribution instead of one number. Pass --stat median to plot that.

    ./speed_accuracy.py
    ./speed_accuracy.py --stat median
    ./speed_accuracy.py --qa unified_q_and_a.jsonl --eval eval-reviewed
"""

import argparse
from pathlib import Path

import evaldata as E

HERE = Path(__file__).parent

# Solid: ascending scale ladders. qwen3 has two, one per build.
LADDERS = [
    ["qwen2.5:0.5b", "qwen2.5:1.5b", "qwen2.5:3b", "qwen2.5:7b", "qwen2.5:32b"],
    ["gemma4:e2b", "gemma4:12b", "gemma4:31b"],
    ["hf.co/LiquidAI/LFM2.5-230M-GGUF:Q8_0", "hf.co/LiquidAI/LFM2.5-2.6B-GGUF:Q8_0"],
    ["qwen3:4b-instruct-2507-q4_K_M", "qwen3:30b-a3b-instruct-2507-q4_K_M"],
    ["qwen3:4b-thinking-2507-q4_K_M", "qwen3:30b-a3b-thinking-2507-q4_K_M"],
]
# Dashed: one size, two builds.
THINKING_PAIRS = [
    ("qwen3:4b-instruct-2507-q4_K_M", "qwen3:4b-thinking-2507-q4_K_M"),
    ("qwen3:30b-a3b-instruct-2507-q4_K_M", "qwen3:30b-a3b-thinking-2507-q4_K_M"),
]

# Nudges in points, applied to the pass@1 label. Everything under ~0.4s is one
# dense knot -- five models inside a third of a decade and six accuracy points --
# so those labels are fanned outward by hand rather than all trailing right.
NUDGE = {
    "qwen2.5:0.5b": (2, -14), "qwen2.5:1.5b": (-9, -5), "qwen2.5:3b": (10, -7),
    "qwen2.5:7b": (8, -4), "qwen2.5:32b": (9, -3),
    "qwen3:4b-instruct-2507-q4_K_M": (-9, 4),
    "qwen3:30b-a3b-instruct-2507-q4_K_M": (-10, 3),
    "qwen3:4b-thinking-2507-q4_K_M": (9, -3),
    "qwen3:30b-a3b-thinking-2507-q4_K_M": (9, -2),
    "gemma4:e2b": (8, 1), "gemma4:12b": (9, -2), "gemma4:31b": (9, -2),
    "hf.co/LiquidAI/LFM2.5-230M-GGUF:Q8_0": (-8, 14),
    "hf.co/LiquidAI/LFM2.5-2.6B-GGUF:Q8_0": (8, -3),
    "qwen3.6:27b": (-11, -12),
}

# The pgfplots figure is 16cm wide where the PNG is 11.5in, so an offset in
# points buys far less separation there. These are tuned for the TeX geometry;
# NUDGE above is tuned for the PNG.
TEX_NUDGE = {
    "qwen2.5:0.5b": (4, -11), "qwen2.5:1.5b": (-5, -9), "qwen2.5:3b": (5, -12),
    "qwen2.5:7b": (5, -3), "qwen2.5:32b": (6, -2),
    "qwen3:4b-instruct-2507-q4_K_M": (-6, 7),
    "qwen3:30b-a3b-instruct-2507-q4_K_M": (-7, 2),
    "qwen3:4b-thinking-2507-q4_K_M": (6, -2),
    "qwen3:30b-a3b-thinking-2507-q4_K_M": (6, -1),
    "gemma4:e2b": (5, 1), "gemma4:12b": (6, -1), "gemma4:31b": (6, -1),
    "hf.co/LiquidAI/LFM2.5-230M-GGUF:Q8_0": (-6, 13),
    "hf.co/LiquidAI/LFM2.5-2.6B-GGUF:Q8_0": (5, -2),
    "qwen3.6:27b": (-7, -9),
}


def xlim_for(d, key):
    """Pad the log axis so the fastest and slowest are not pinned to the frame."""
    xs = [d[m][key] for m in d]
    return min(xs) / 3.4, max(xs) * 2.6


def render_png(d, stat, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    key = f"{stat}_s"
    color = E.colors()
    fig, ax = plt.subplots(figsize=(11.5, 7.2), dpi=200)
    E.style_axes(ax, fig)
    ax.set_xscale("log")

    for a, b in THINKING_PAIRS:
        ax.plot([d[a][key], d[b][key]], [d[a]["pass1"], d[b]["pass1"]],
                ls=(0, (4, 3)), lw=1.3, color=color[a], alpha=0.75, zorder=2)
    for lad in LADDERS:
        ax.plot([d[m][key] for m in lad], [d[m]["pass1"] for m in lad],
                lw=1.6, color=color[lad[0]], alpha=0.9, zorder=3)
    for m in E.MODELS:
        ax.plot([d[m][key]] * 2, [d[m]["pass1"], d[m]["pass3"]],
                lw=1.1, color=color[m], alpha=0.55, zorder=3)
    for m in E.MODELS:
        ax.plot(d[m][key], d[m]["pass3"], "o", ms=7, mfc=E.SURFACE,
                mec=color[m], mew=1.6, zorder=5)
        ax.plot(d[m][key], d[m]["pass1"], "o", ms=8.5, color=color[m],
                mec=E.SURFACE, mew=1.4, zorder=6)
    # A leader line back to the marker. In the sub-second cluster the labels
    # have to sit further out than the gaps between points, so proximity alone
    # does not say which label belongs to which model.
    for m in E.MODELS:
        dx, dy = NUDGE.get(m, (8, -3))
        ax.annotate(E.LABEL[m], (d[m][key], d[m]["pass1"]),
                    textcoords="offset points", xytext=(dx, dy),
                    ha="right" if dx < 0 else "left",
                    fontsize=8.5, color=E.INK, zorder=7,
                    arrowprops=dict(arrowstyle="-", color=E.MUTED, lw=0.6,
                                    alpha=0.55, shrinkA=1, shrinkB=6))

    ax.set_xlabel(f"{stat} seconds per answer  (log scale)", fontsize=10, color=E.MUTED)
    ax.set_ylabel("correct  (%)", fontsize=10, color=E.MUTED)
    ax.set_ylim(-4, 88)
    ax.set_xlim(*xlim_for(d, key))

    fam = [Line2D([], [], color=c, lw=1.6, marker="o", ms=7, mec=E.SURFACE, mew=1.2,
                  label=n) for n, (c, _) in E.FAMILY.items()]
    fam.append(Line2D([], [], color=list(E.UNAFFILIATED.values())[0], lw=0, marker="o",
                      ms=7, mec=E.SURFACE, mew=1.2, label="qwen3.6 (no family)"))
    enc = [
        Line2D([], [], color=E.MUTED, lw=0, marker="o", ms=8.5, label="pass@1"),
        Line2D([], [], color=E.MUTED, lw=0, marker="o", ms=7, mfc=E.SURFACE, mew=1.6,
               label="pass@3"),
        Line2D([], [], color=E.MUTED, lw=1.6, label="scale ladder"),
        Line2D([], [], color=E.MUTED, lw=1.3, ls=(0, (4, 3)), label="instruct → thinking"),
    ]
    l1 = ax.legend(handles=fam, loc="upper left", frameon=False, fontsize=8.5,
                   labelcolor=E.INK, handletextpad=0.6)
    ax.add_artist(l1)
    ax.legend(handles=enc, loc="lower right", frameon=False, fontsize=8.5,
              labelcolor=E.INK, handletextpad=0.6)

    ax.set_title("Accuracy against latency per answer",
                 fontsize=12.5, color=E.INK, loc="left", pad=14)
    n = d[E.MODELS[0]]["questions"]
    ax.text(0, 1.015, f"{n} closed-book questions × 3 rollouts, LLM-judged; "
                      f"{stat} latency", transform=ax.transAxes,
            fontsize=8.5, color=E.MUTED)

    fig.tight_layout()
    fig.savefig(path, facecolor=E.SURFACE)
    print(f"wrote {path}")


def render_tex(d, stat, path):
    """Standalone pgfplots source; same numbers, compiles with pdflatex."""
    key = f"{stat}_s"
    defs = {n: c for n, (c, _) in E.FAMILY.items()}
    defs["unaff"] = list(E.UNAFFILIATED.values())[0]
    fam_index = {n: i for i, n in enumerate(defs)}
    m2fam = {m: n for n, (_, ms) in E.FAMILY.items() for m in ms}
    x0, x1 = xlim_for(d, key)

    L = [r"\documentclass[border=6pt]{standalone}", r"\usepackage{pgfplots}",
         r"\pgfplotsset{compat=1.18}", r"\usepackage{xcolor}"]
    for i, (n, c) in enumerate(defs.items()):
        L.append(rf"\definecolor{{fam{i}}}{{HTML}}{{{c.lstrip('#').upper()}}}")
    L += [r"\definecolor{surface}{HTML}{FCFCFB}", r"\definecolor{ink}{HTML}{0B0B0B}",
          r"\definecolor{muted}{HTML}{52514E}", r"\definecolor{gridc}{HTML}{E8E7E3}",
          r"\begin{document}", r"\begin{tikzpicture}", r"\begin{axis}[",
          r"  width=16cm, height=11.5cm, xmode=log, log basis x=10,",
          rf"  xlabel={{{stat} seconds per answer (log scale)}},",
          r"  ylabel={correct (\%)},",
          r"  xlabel style={font=\small, color=muted},",
          r"  ylabel style={font=\small, color=muted},",
          r"  tick label style={font=\footnotesize, color=muted},",
          rf"  ymin=-4, ymax=88, xmin={x0:.4f}, xmax={x1:.1f},",
          r"  grid=both, grid style={gridc, line width=0.3pt},",
          r"  axis line style={gridc}, axis x line*=bottom, axis y line*=left,",
          r"  clip=false, legend style={draw=none, font=\footnotesize,"
          r" at={(0.02,0.98)}, anchor=north west},", r"]"]

    L.append("% instruct -> thinking")
    for a, b in THINKING_PAIRS:
        ci = fam_index[m2fam[a]]
        L.append(rf"\addplot[fam{ci}, dashed, line width=0.9pt, forget plot] "
                 rf"coordinates {{({d[a][key]:.3f},{d[a]['pass1']:.2f}) "
                 rf"({d[b][key]:.3f},{d[b]['pass1']:.2f})}};")
    L.append("% scale ladders")
    for lad in LADDERS:
        ci = fam_index[m2fam[lad[0]]]
        pts = " ".join(f"({d[m][key]:.3f},{d[m]['pass1']:.2f})" for m in lad)
        L.append(rf"\addplot[fam{ci}, line width=1.1pt, forget plot] coordinates {{{pts}}};")
    L.append("% pass@1 -> pass@3 stems")
    for m in E.MODELS:
        ci = fam_index[m2fam.get(m, "unaff")]
        L.append(rf"\addplot[fam{ci}, opacity=0.55, line width=0.8pt, forget plot] "
                 rf"coordinates {{({d[m][key]:.3f},{d[m]['pass1']:.2f}) "
                 rf"({d[m][key]:.3f},{d[m]['pass3']:.2f})}};")
    L.append("% markers")
    for m in E.MODELS:
        ci = fam_index[m2fam.get(m, "unaff")]
        L.append(rf"\addplot[only marks, mark=*, mark size=2.2pt, "
                 rf"mark options={{fill=surface, draw=fam{ci}, line width=1pt}}, forget plot] "
                 rf"coordinates {{({d[m][key]:.3f},{d[m]['pass3']:.2f})}};")
        L.append(rf"\addplot[only marks, mark=*, mark size=2.6pt, "
                 rf"mark options={{fill=fam{ci}, draw=surface, line width=0.8pt}}, forget plot] "
                 rf"coordinates {{({d[m][key]:.3f},{d[m]['pass1']:.2f})}};")
    L.append("% labels, each with a leader back to its own marker")
    for i, m in enumerate(E.MODELS):
        dx, dy = TEX_NUDGE.get(m, (6, -2))
        anchor = "east" if dx < 0 else "west"
        L.append(rf"\node[anchor={anchor}, font=\tiny, text=ink, "
                 rf"xshift={dx}pt, yshift={dy + 3}pt] (lbl{i}) at "
                 rf"(axis cs:{d[m][key]:.3f},{d[m]['pass1']:.2f}) "
                 rf"{{{E.LABEL[m].replace('_', chr(92) + '_')}}};")
        L.append(rf"\draw[muted, opacity=0.55, line width=0.3pt] (lbl{i}.{anchor}) -- "
                 rf"(axis cs:{d[m][key]:.3f},{d[m]['pass1']:.2f});")
    for n, i in fam_index.items():
        nm = "qwen3.6 (no family)" if n == "unaff" else n
        L.append(rf"\addlegendimage{{fam{i}, line width=1.1pt, mark=*, "
                 rf"mark options={{fill=fam{i}, draw=surface}}}}")
        L.append(rf"\addlegendentry{{{nm}}}")
    L += [r"\end{axis}", r"\end{tikzpicture}", r"\end{document}"]
    Path(path).write_text("\n".join(L) + "\n")
    print(f"wrote {path}")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--stat", choices=["mean", "median"], default="mean")
    p.add_argument("--qa", default=str(E.DEFAULT_QA),
                   help="QA jsonl selecting which questions to chart")
    p.add_argument("--eval", default=str(E.DEFAULT_EVAL),
                   help="directory holding answers.jsonl and judgments.jsonl")
    p.add_argument("--out", default=str(HERE / "speed_accuracy"))
    args = p.parse_args()

    d = E.read(Path(args.qa), Path(args.eval))
    print(f"{'model':24}{'pass@1':>8}{'pass@3':>8}{args.stat + ' s':>10}")
    for m in sorted(E.MODELS, key=lambda m: -d[m]["pass1"]):
        print(f"{E.LABEL[m]:24}{d[m]['pass1']:8.1f}{d[m]['pass3']:8.1f}"
              f"{d[m][args.stat + '_s']:10.2f}")

    render_png(d, args.stat, Path(args.out + ".png"))
    render_tex(d, args.stat, Path(args.out + ".tex"))


if __name__ == "__main__":
    main()
