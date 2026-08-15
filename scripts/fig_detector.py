"""Figure: the channel the metric keeps vs the channels it discards.

One claim, one picture. Each model contributes four bars -- how well each
channel of the SAME forward pass separates real outcomes from invented ones.
The kept channel sits near chance; the discarded ones do the work.

    python3 scripts/fig_detector.py                      # -> site/fig4_detector.svg
    python3 scripts/fig_detector.py --format pdf --themes light --out paper/figs
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

THEMES = {
    "light": {"fg": "#111110", "mid": "#55534e", "faint": "#d9d7d0", "bg": "none"},
    "dark": {"fg": "#f4f3ef", "mid": "#bab8ae", "faint": "#35342f", "bg": "none"},
}
# The kept channel is the one under indictment, so it gets the accent (the same
# one the slides use). The discarded channels were originally a low-chroma family
# so the eye would group them, but that made them mutually illegible: the old
# blue/green pair sat at normal-vision dE 12.1, under the 15 floor, and both read
# as gray. Re-stepped to a validated set -- worst adjacent pair is now dE 22.9
# normal / 19.0 deutan, and all four clear the chroma floor and 3:1 on the
# surface in BOTH themes. If you change these, re-run the check rather than
# eyeballing it:
#   node <dataviz-skill>/scripts/validate_palette.js \
#        "#b4453a,#3d6fb5,#3f8f3a,#8a4fa8" --mode light   (then --mode dark)
KEPT_COLOR = "#b4453a"
DISCARD_COLORS = ["#3d6fb5", "#3f8f3a", "#8a4fa8"]


def figure(data: dict, theme: str = "light"):
    th = THEMES[theme]
    per = data["per_model"]
    channels = [c for c in next(iter(per.values())) if c != "n_matched_pairs"]
    models = sorted(per, key=lambda m: -per[m][channels[0]]["separation"])

    fig, ax = plt.subplots(figsize=(9.6, 4.9))
    n = len(channels)
    width = 0.8 / n
    x = np.arange(len(models))

    for i, ch in enumerate(channels):
        vals = [per[m].get(ch, {}).get("separation", np.nan) for m in models]
        kept = "[KEPT]" in ch
        ax.bar(x + (i - (n - 1) / 2) * width, vals, width * 0.92,
               label=ch.replace("  ", "  "),
               color=KEPT_COLOR if kept else DISCARD_COLORS[(i - 1) % 3],
               edgecolor=th["fg"] if kept else "none",
               linewidth=1.1 if kept else 0, zorder=3)

    # Chance is the only reference line that matters: at 0.5 a channel cannot
    # tell a real outcome from a nonsense one at all.
    ax.axhline(0.5, color=th["mid"], lw=1.1, ls=(0, (4, 3)), zorder=2)
    # This label has to live OUTSIDE the axes. Bars are drawn from zero, so they
    # fill the whole band up to their height -- there is no gap at y=0.5 at any x,
    # above the line or below it, and an in-plot label overprinted the bars.
    # get_yaxis_transform: x in axes fraction, y in data units, so it stays pinned
    # to the line whatever the ylim.
    ax.text(1.012, 0.5, "chance\ncannot tell\nthem apart",
            transform=ax.get_yaxis_transform(), fontsize=8, color=th["mid"],
            ha="left", va="center", linespacing=1.3)

    ax.set_xticks(x)
    ax.set_xticklabels([m.split("/")[-1] for m in models], rotation=18,
                       ha="right", fontsize=9, color=th["fg"])
    ax.set_ylabel("separation of real vs invented outcomes\n(AUROC, oriented)",
                  fontsize=10, color=th["fg"])
    ax.set_ylim(0.45, 1.02)
    ax.tick_params(colors=th["mid"], labelsize=9)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(th["faint"])
    ax.grid(axis="y", color=th["faint"], lw=0.7, zorder=0)
    ax.set_axisbelow(True)

    leg = ax.legend(fontsize=8.6, frameon=False, ncol=2, loc="upper center",
                    bbox_to_anchor=(0.5, 1.19))
    for t in leg.get_texts():
        t.set_color(th["fg"])
    fig.tight_layout()
    return fig


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="site/nonsense_detector.json")
    ap.add_argument("--out", default="site")
    ap.add_argument("--format", default="svg", choices=("svg", "pdf", "png"))
    ap.add_argument("--themes", default="light,dark")
    args = ap.parse_args()

    data = json.loads(Path(args.data).read_text())
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for theme in [t.strip() for t in args.themes.split(",") if t.strip()]:
        sfx = "" if theme == "light" else "-dark"
        fig = figure(data, theme)
        fig.savefig(out / f"fig4_detector{sfx}.{args.format}", format=args.format,
                    bbox_inches="tight", transparent=True)
        plt.close(fig)
        print(f"wrote {out}/fig4_detector{sfx}.{args.format}")


if __name__ == "__main__":
    main()
