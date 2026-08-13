#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["matplotlib>=3.11"]
# ///
"""latency-spread: the full distribution of time-to-answer for the large models.

A box plot cannot show a second mode -- it draws one box whatever the shape --
and qwen3.6:27b has two, an hour apart. So each model is a violin: the outline
is a kernel density of its per-answer latency, at its pass@1 accuracy. Inside
sits the interquartile range and the median; the diamond is the mean, which is
what summary.json reports.

The density is estimated on log10(seconds), not on seconds, because the axis is
logarithmic -- a kernel of fixed width in raw seconds would be invisibly narrow
at 0.2s and enormous at 4000s. Each violin is normalised to the same height;
every model here has the same 438 answers, so height carries no information.

Bandwidth runs deliberately below Silverman's rule (--bw scales it), which
assumes one bump and oversmooths a sample with several. Not every lump this
resolves is real: qwen3.6's separated population near 3500s and gemma4 12B's
two lobes hold at every bandwidth, but finer ripples come and go with --bw and
should not be read as structure. Sweep --bw before believing a small one.

Restricted to models above 9B total parameters. 30B-A3B is a 30B mixture
activating 3B per token; it is counted at 30B.

    ./latency_spread.py
    ./latency_spread.py --min-params 20 --bw 0.8
    ./latency_spread.py --qa unified_q_and_a.jsonl --eval eval-reviewed
"""

import argparse
import math
import statistics
from pathlib import Path

import evaldata as E

HERE = Path(__file__).parent

# Density rises from the accuracy baseline rather than straddling it. qwen2.5
# 32B and gemma4 12B are 1.1 accuracy points apart, and a violin drawn both
# ways would bury one inside the other; one-sided halves that overlap.
HALF = 3.0      # violin height above the baseline, in accuracy points
GRID = 220      # density samples across the x range


def quantile(sorted_s, p):
    k = (len(sorted_s) - 1) * p
    f = int(k)
    if f + 1 >= len(sorted_s):
        return sorted_s[f]
    return sorted_s[f] + (k - f) * (sorted_s[f + 1] - sorted_s[f])


def kde_log10(seconds, bw_mult, lo, hi):
    """Gaussian KDE over log10(seconds). Returns (x in seconds, density 0..1).

    Bandwidth is Silverman's rule on the log-transformed sample. Silverman
    oversmooths a bimodal sample -- it assumes one bump -- so --bw scales it
    down when two modes need to stay apart.
    """
    xs = [math.log10(max(s, 1e-6)) for s in seconds]
    n = len(xs)
    sd = statistics.pstdev(xs) or 1e-3
    srt = sorted(xs)
    iqr = quantile(srt, .75) - quantile(srt, .25)
    spread = min(sd, iqr / 1.34) if iqr > 0 else sd
    bw = max(0.9 * spread * n ** (-0.2) * bw_mult, 1e-3)

    grid = [lo + (hi - lo) * i / (GRID - 1) for i in range(GRID)]
    norm = 1.0 / (n * bw * math.sqrt(2 * math.pi))
    dens = []
    for g in grid:
        acc = 0.0
        for x in xs:
            z = (g - x) / bw
            if -6 < z < 6:
                acc += math.exp(-0.5 * z * z)
        dens.append(acc * norm)
    peak = max(dens) or 1.0
    return [10 ** g for g in grid], [v / peak for v in dens], bw


def build(d, order, bw_mult, xlo, xhi):
    """Everything both renderers need, computed once."""
    lo, hi = math.log10(xlo), math.log10(xhi)
    out = {}
    for m in order:
        s = sorted(d[m]["seconds"])
        xs, dens, bw = kde_log10(s, bw_mult, lo, hi)
        out[m] = {
            "x": xs, "d": dens, "bw": bw,
            "q1": quantile(s, .25), "med": quantile(s, .5), "q3": quantile(s, .75),
            "lo": s[0], "hi": s[-1],
            "mean": d[m]["mean_s"], "y": d[m]["pass1"],
        }
    return out


def render_png(v, order, path, min_params, questions):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    color = E.colors()
    fig, ax = plt.subplots(figsize=(11.5, 7.0), dpi=200)
    E.style_axes(ax, fig)
    ax.set_xscale("log")

    for m in order:
        c, p = color[m], v[m]
        y = p["y"]
        ax.fill_between(p["x"], [y] * len(p["d"]), [y + HALF * t for t in p["d"]],
                        facecolor=c, alpha=0.30, edgecolor=c, linewidth=1.0, zorder=4)
        # full range as a hairline, then IQR as a solid rule, then the median
        ax.plot([p["lo"], p["hi"]], [y, y], color=c, lw=0.8, alpha=0.55, zorder=5)
        ax.plot([p["q1"], p["q3"]], [y, y], color=c, lw=3.4, solid_capstyle="butt",
                zorder=6)
        ax.plot([p["med"]] * 2, [y - 0.9, y + 0.9], color=E.SURFACE, lw=2.0, zorder=7)
        ax.plot(p["mean"], y, marker="D", ms=6.5, color=c, mec=E.SURFACE, mew=1.3,
                zorder=8)

    BELOW = {"qwen2.5:32b"}
    for m in order:
        dy, va = (-15, "top") if m in BELOW else (11, "bottom")
        ax.annotate(E.LABEL[m], (v[m]["lo"], v[m]["y"]),
                    textcoords="offset points", xytext=(-2, dy), ha="left", va=va,
                    fontsize=9, color=E.INK, zorder=9)

    ax.set_xlabel("seconds per answer  (log scale)", fontsize=10, color=E.MUTED)
    ax.set_ylabel("correct, pass@1  (%)", fontsize=10, color=E.MUTED)
    ax.set_xlim(0.1, 9000)
    ax.set_ylim(min(v[m]["y"] for m in order) - 9, max(v[m]["y"] for m in order) + 9)

    legend = [
        Line2D([], [], color=E.MUTED, lw=7, alpha=0.30, label="density of answer times"),
        Line2D([], [], color=E.MUTED, lw=3.4, label="interquartile range"),
        Line2D([], [], color=E.MUTED, lw=2.0, label="median"),
        Line2D([], [], color=E.MUTED, lw=0, marker="D", ms=6.5, mec=E.SURFACE,
               mew=1.3, label="mean"),
    ]
    ax.legend(handles=legend, loc="lower right", frameon=False, fontsize=8.5,
              labelcolor=E.INK, handletextpad=0.7)

    ax.set_title("Latency per answer", fontsize=12.5, color=E.INK, loc="left", pad=14)
    ax.text(0, 1.015, f"models above {min_params:g}B parameters · "
                      f"{questions} closed-book questions × 3 rollouts · "
                      f"density estimated on log seconds",
            transform=ax.transAxes, fontsize=8.5, color=E.MUTED)

    fig.tight_layout()
    fig.savefig(path, facecolor=E.SURFACE)
    print(f"wrote {path}")


def render_tex(v, order, path, min_params, questions):
    """Standalone pgfplots source. The violin outline is emitted as a closed
    path built from the same density samples the PNG uses."""
    color = E.colors()
    L = [r"\documentclass[border=6pt]{standalone}", r"\usepackage{pgfplots}",
         r"\pgfplotsset{compat=1.18}", r"\usepackage{xcolor}"]
    for i, m in enumerate(order):
        L.append(rf"\definecolor{{c{i}}}{{HTML}}{{{color[m].lstrip('#').upper()}}}")
    L += [r"\definecolor{surface}{HTML}{FCFCFB}", r"\definecolor{ink}{HTML}{0B0B0B}",
          r"\definecolor{muted}{HTML}{52514E}", r"\definecolor{gridc}{HTML}{E8E7E3}",
          r"\begin{document}", r"\begin{tikzpicture}", r"\begin{axis}[",
          r"  width=16cm, height=10cm, xmode=log, log basis x=10,",
          r"  xlabel={seconds per answer (log scale)},",
          r"  ylabel={correct, pass@1 (\%)},",
          r"  xlabel style={font=\small, color=muted},",
          r"  ylabel style={font=\small, color=muted},",
          r"  tick label style={font=\footnotesize, color=muted},",
          rf"  xmin=0.1, xmax=9000, ymin={min(v[m]['y'] for m in order) - 9:.1f},"
          rf" ymax={max(v[m]['y'] for m in order) + 9:.1f},",
          r"  grid=both, grid style={gridc, line width=0.3pt},",
          r"  axis line style={gridc}, axis x line*=bottom, axis y line*=left,",
          r"  clip=false,", r"]"]

    for i, m in enumerate(order):
        p = v[m]
        y = p["y"]
        top = [(x, y + HALF * t) for x, t in zip(p["x"], p["d"])]
        base = [(p["x"][-1], y), (p["x"][0], y)]
        pts = " ".join(f"({x:.4f},{yy:.3f})" for x, yy in top + base)
        L.append(rf"\addplot[c{i}, fill=c{i}, fill opacity=0.28, line width=0.7pt] "
                 rf"coordinates {{{pts}}} --cycle;")
        L.append(rf"\addplot[c{i}, opacity=0.55, line width=0.5pt] coordinates "
                 rf"{{({p['lo']:.4f},{y:.2f}) ({p['hi']:.4f},{y:.2f})}};")
        L.append(rf"\addplot[c{i}, line width=2.2pt] coordinates "
                 rf"{{({p['q1']:.4f},{y:.2f}) ({p['q3']:.4f},{y:.2f})}};")
        L.append(rf"\addplot[surface, line width=1.4pt] coordinates "
                 rf"{{({p['med']:.4f},{y - 0.9:.2f}) ({p['med']:.4f},{y + 0.9:.2f})}};")
        L.append(rf"\addplot[only marks, mark=diamond*, mark size=3pt, "
                 rf"mark options={{fill=c{i}, draw=surface}}] coordinates "
                 rf"{{({p['mean']:.4f},{y:.2f})}};")
        L.append(rf"\node[anchor=south west, font=\scriptsize, text=ink, yshift=6pt] at "
                 rf"(axis cs:{p['lo']:.4f},{y:.2f}) "
                 rf"{{{E.LABEL[m].replace('_', chr(92) + '_')}}};")
    L += [r"\end{axis}", r"\end{tikzpicture}", r"\end{document}"]
    Path(path).write_text("\n".join(L) + "\n")
    print(f"wrote {path}")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--min-params", type=float, default=9.0,
                   help="only models above this many billion parameters")
    p.add_argument("--bw", type=float, default=0.4,
                   help="bandwidth multiplier on Silverman; lower resolves more "
                        "structure and invents more")
    p.add_argument("--qa", default=str(E.DEFAULT_QA))
    p.add_argument("--eval", default=str(E.DEFAULT_EVAL))
    p.add_argument("--out", default=str(HERE / "latency_spread"))
    args = p.parse_args()

    models = [m for m in E.MODELS if E.PARAMS[m] > args.min_params]
    d = E.read(Path(args.qa), Path(args.eval), models=models)
    order = sorted(d, key=lambda m: d[m]["pass1"])
    v = build(d, order, args.bw, 0.1, 9000)

    print(f"{'model':24}{'pass@1':>8}{'median':>9}{'mean':>9}{'max':>9}{'kde bw':>9}")
    for m in reversed(order):
        print(f"{E.LABEL[m]:24}{d[m]['pass1']:8.1f}{v[m]['med']:9.1f}"
              f"{v[m]['mean']:9.1f}{v[m]['hi']:9.1f}{v[m]['bw']:9.3f}")

    n = d[order[0]]["questions"]
    render_png(v, order, Path(args.out + ".png"), args.min_params, n)
    render_tex(v, order, Path(args.out + ".tex"), args.min_params, n)


if __name__ == "__main__":
    main()
