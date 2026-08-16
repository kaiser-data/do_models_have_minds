"""Figure: the channel the metric keeps vs the channels it discards.

Two panels, because the full nine-model grid asks a general reader to hold
AUROC, probability mass, entropy and the kept/discarded split in their head
before they can see the point. Panel A is the claim -- four signals from one
forward pass, averaged over models. Panel B is the same claim at its clearest,
on a single model. The nine-model grid still exists, as the supplementary
figure this writes alongside.

    python3 scripts/fig_detector.py     # -> site/fig4_detector.svg
                                        #    site/fig4b_detector_models.svg
    python3 scripts/fig_detector.py --format pdf --themes light --out paper/figs

Two things the figure has to say out loud, because both have already been
misread. A taller bar means a signal separates the arms more sharply -- NOT
that the model is better. And the chance reference is not 0.5: orienting each
model by max(AUROC, 1-AUROC) can only push values up, so pure noise lands
slightly above. The band is drawn from the computed null rather than assumed.
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
    "light": {"fg": "#111110", "mid": "#55534e", "faint": "#d9d7d0",
              "null": "#e8e6df", "bg": "none"},
    "dark": {"fg": "#f4f3ef", "mid": "#bab8ae", "faint": "#35342f",
             "null": "#2a2925", "bg": "none"},
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

# Plain-language names. The raw keys are formulae -- "direction sign(p-0.5)"
# names the operation, not the thing -- and a reader who has to decode four of
# those before seeing the comparison has already lost the argument. The formula
# stays in the axis label and the caption for the technical reader.
# Line breaks are explicit: at four categories across this panel there is about
# 100pt per label, and an unwrapped "Whether it answered A or B at all" overruns
# its neighbour. Checked by rendering, not by counting characters.
PLAIN = {
    "direction sign(p-0.5)  [KEPT]": ("Which option\nit picked", "USED BY COHERENCE"),
    "strength |p-0.5|  [discarded]": ("How strongly\nit picked", "discarded"),
    "answer mass  [discarded]": ("Whether it answered\nA or B at all", "discarded"),
    "top-5 entropy  [discarded]": ("How uncertain\nthe output was", "discarded"),
}
SHORT = ["kept", "strength", "answer\nmass", "entropy"]
SHOWCASE = "Qwen/Qwen3.5-2B"


def _channels(per: dict) -> list[str]:
    return [c for c in next(iter(per.values())) if c != "n_matched_pairs"]


def _color(i: int, kept: bool) -> str:
    return KEPT_COLOR if kept else DISCARD_COLORS[(i - 1) % 3]


def _style_axes(ax, th, ylabel: str | None):
    ax.set_ylim(0.45, 1.06)
    ax.tick_params(colors=th["mid"], labelsize=9)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(th["faint"])
    ax.grid(axis="y", color=th["faint"], lw=0.7, zorder=0)
    ax.set_axisbelow(True)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=9.5, color=th["fg"])
    else:
        ax.set_yticklabels([])


def _null_band(ax, th, hi: float | None, label: bool):
    """Chance is not 0.5 here, so draw where it actually is.

    `hi` comes from the detector's computed orientation null. It is NOT
    defaulted: a hardcoded band would look identical to a computed one and a
    reader would take the shading as a property of this run's pair counts when
    it was a literal. Absent -> the band is omitted and the caller says so.

    Bars are drawn from zero and fill the plot at every x, so an in-plot label
    for this line has nowhere to sit -- it overprints whichever bar it lands on.
    It goes outside the axes instead, pinned to the line in data units.
    """
    if hi is not None:
        ax.axhspan(0.5, hi, color=th["null"], zorder=1, lw=0)
    ax.axhline(0.5, color=th["mid"], lw=1.0, ls=(0, (4, 3)), zorder=2)
    if label:
        ax.text(1.02, 0.5, "chance\ncannot tell\nthem apart",
                transform=ax.get_yaxis_transform(), fontsize=7.8,
                color=th["mid"], ha="left", va="center", linespacing=1.3)


def figure(data: dict, theme: str = "light"):
    th = THEMES[theme]
    per, chans = data["per_model"], _channels(data["per_model"])
    cons = data.get("direction_consistency", {})
    null = data.get("orientation_null", {})

    fig, (axA, axB) = plt.subplots(
        1, 2, figsize=(10.4, 5.4), gridspec_kw={"width_ratios": [2.35, 1]})

    # --- Panel A: the claim, averaged over models -------------------------
    means = [float(np.mean([per[m][c]["separation"]
                            for m in per if c in per[m]])) for c in chans]
    xs = np.arange(len(chans))
    for i, (c, v) in enumerate(zip(chans, means)):
        kept = "[KEPT]" in c
        axA.bar(i, v, 0.62, color=_color(i, kept),
                edgecolor=th["fg"] if kept else "none",
                linewidth=1.2 if kept else 0, zorder=3)
        axA.text(i, v + 0.014, f"{v:.3f}", ha="center", va="bottom",
                 fontsize=10.5, color=th["fg"],
                 fontweight="bold" if kept else "normal", zorder=4)

    _null_band(axA, th, null.get("p99_null_oriented_mean"), label=False)
    axA.set_xticks(xs)
    # Direction consistency rides in the tick label rather than inside the bar:
    # on the bar it was colour-on-colour and collided with the chance band, and
    # it belongs with the channel's name anyway. It is the difference between a
    # number an auditor could have produced in advance and one only we can.
    labels = []
    for c in chans:
        name, role = PLAIN.get(c, (c, ""))
        k = cons.get(c)
        if k and k["predeclarable"]:
            d = f"direction holds {k['n_agree']}/{k['n_models']}"
        elif k:
            d = f"direction flips — {k['n_agree']}/{k['n_models']}"
        else:
            d = ""
        labels.append(f"{name}\n{role}\n{d}")
    axA.set_xticklabels(labels, fontsize=8.4, color=th["fg"], linespacing=1.65)
    for lbl, c in zip(axA.get_xticklabels(), chans):
        if "[KEPT]" in c:
            lbl.set_fontweight("bold")
    _style_axes(axA, th,
                "how well the signal separates real from invented outcomes\n"
                "(AUROC, oriented per model — 1.00 = perfect)")
    axA.set_title(f"A · averaged over all {len(per)} models",
                  fontsize=9.5, color=th["mid"], loc="left", pad=8)

    # --- Panel B: the same claim at its sharpest, on one model ------------
    if SHOWCASE in per:
        vals = [per[SHOWCASE][c]["separation"] for c in chans]
        for i, (c, v) in enumerate(zip(chans, vals)):
            kept = "[KEPT]" in c
            axB.bar(i, v, 0.62, color=_color(i, kept),
                    edgecolor=th["fg"] if kept else "none",
                    linewidth=1.2 if kept else 0, zorder=3)
            axB.text(i, v + 0.014, f"{v:.2f}", ha="center", va="bottom",
                     fontsize=10.5, color=th["fg"],
                     fontweight="bold" if kept else "normal", zorder=4)
        _null_band(axB, th, null.get("p95_null_oriented_single"), label=True)
        axB.set_xticks(np.arange(len(chans)))
        axB.set_xticklabels(SHORT, fontsize=8.4, color=th["mid"],
                            linespacing=1.4)
        axB.get_xticklabels()[0].set_color(th["fg"])
        axB.get_xticklabels()[0].set_fontweight("bold")
        _style_axes(axB, th, None)
        axB.set_title(f"B · {SHOWCASE.split('/')[-1]}, one forward pass",
                      fontsize=9.5, color=th["mid"], loc="left", pad=8)
        # The two short bars leave the upper-left of this panel empty; the
        # annotation goes in that hole rather than over the bars.
        axB.text(-0.34, 0.985,
                 "same model,\nsame forward pass:\nthe kept signal is at\n"
                 "chance, a discarded\none is perfect",
                 fontsize=8, color=th["fg"], ha="left", va="top",
                 linespacing=1.45, zorder=4)

    fig.suptitle("Of four signals in one forward pass, coherence keeps the one\n"
                 "that distinguishes real from invented outcomes least well",
                 fontsize=12.4, color=th["fg"], y=1.045, ha="center")
    fig.text(0.5, -0.055,
             "A taller bar means that signal separates the two arms more sharply — "
             "not that the model is better.\nAUROCs are oriented using known arm "
             "labels: they show how much separating information each channel "
             "carries,\nnot the performance of a deployable detector.",
             ha="center", va="top", fontsize=8.1, color=th["mid"],
             linespacing=1.5)
    fig.tight_layout()
    return fig


def figure_all_models(data: dict, theme: str = "light"):
    """The original nine-model grid, kept as the supplementary figure.

    Panel A of the main figure is a mean, and a mean can hide a split roster.
    This is where a reader checks that it does not.
    """
    th = THEMES[theme]
    per = data["per_model"]
    chans = _channels(per)
    null = data.get("orientation_null", {})
    models = sorted(per, key=lambda m: -per[m][chans[0]]["separation"])

    fig, ax = plt.subplots(figsize=(9.6, 4.9))
    n = len(chans)
    width = 0.8 / n
    x = np.arange(len(models))

    for i, ch in enumerate(chans):
        vals = [per[m].get(ch, {}).get("separation", np.nan) for m in models]
        kept = "[KEPT]" in ch
        label = f"{PLAIN[ch][0]} — {PLAIN[ch][1]}" if ch in PLAIN else ch
        ax.bar(x + (i - (n - 1) / 2) * width, vals, width * 0.92, label=label,
               color=_color(i, kept), edgecolor=th["fg"] if kept else "none",
               linewidth=1.1 if kept else 0, zorder=3)

    _null_band(ax, th, null.get("p95_null_oriented_single"), label=False)
    ax.text(1.012, 0.5, "chance\ncannot tell\nthem apart",
            transform=ax.get_yaxis_transform(), fontsize=8, color=th["mid"],
            ha="left", va="center", linespacing=1.3)

    ax.set_xticks(x)
    ax.set_xticklabels([m.split("/")[-1] for m in models], rotation=18,
                       ha="right", fontsize=9, color=th["fg"])
    _style_axes(ax, th, "separation of real vs invented outcomes\n"
                        "(AUROC, oriented)")
    leg = ax.legend(fontsize=8.4, frameon=False, ncol=2, loc="upper center",
                    bbox_to_anchor=(0.5, 1.21))
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
    ap.add_argument("--all-models", action="store_true",
                    help="also emit fig4b, the per-model breakdown of the panel "
                         "fig4 averages. Off by default: no .tex cites it, and "
                         "an uncited figure is build time and reader attention "
                         "spent on a claim nobody makes.")
    args = ap.parse_args()

    data = json.loads(Path(args.data).read_text())
    if not data.get("orientation_null"):
        print("NOTE: this detector JSON carries no orientation_null block, so "
              "the chance band is OMITTED rather than drawn at a guessed "
              "height. Re-run scripts/nonsense_detector.py to compute it.")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for theme in [t.strip() for t in args.themes.split(",") if t.strip()]:
        sfx = "" if theme == "light" else "-dark"
        # fig4b_detector_models is NOT emitted by default. It was built every
        # run and cited by neither main.tex nor slides.tex -- a per-model
        # breakdown of a panel fig4 already averages, competing for attention
        # with the four figures that carry the argument. `figure_all_models` is
        # kept and reachable with --all-models because the breakdown is the
        # right thing to look at when one model is suspected of driving the
        # mean; it is just not a figure the paper makes a claim with.
        wanted = [("fig4_detector", figure)]
        if args.all_models:
            wanted.append(("fig4b_detector_models", figure_all_models))
        for stem, fn in wanted:
            fig = fn(data, theme)
            fig.savefig(out / f"{stem}{sfx}.{args.format}", format=args.format,
                        bbox_inches="tight", transparent=True)
            plt.close(fig)
            print(f"wrote {out}/{stem}{sfx}.{args.format}")


if __name__ == "__main__":
    main()
