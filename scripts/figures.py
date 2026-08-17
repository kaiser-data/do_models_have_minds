"""Figures for the paper and the page — one artifact, both surfaces (spec §11).

    python3 scripts/figures.py --results results --card card.json --out site/

Design reasoning for the main figure:

The finding is a *comparison of two comparisons* — direction accuracy barely
moves while preference strength collapses. Drawn as two panels on two y-scales,
that contrast looks like a choice of axis. Drawn as a **state space**, it becomes
a direction.

Each model is not a point but a trajectory. The three arms are a controlled
ablation:

    R  --(remove semantics, keep arithmetic)-->  N+  --(remove arithmetic)-->  N-

Plotting coherence against preference strength turns each model into a 2-segment
path. If coherence tracked meaning, paths would run **down and to the left**.
They run **straight down**: the metric does not register what was removed. The
direction of the path is the argument.

Four dimensions, no 3D: position (2), path (the ablation), marker area
(parameters), hue (family). A static 3D scatter would add occlusion and remove
depth cues — it reads worse, not better.

Light and dark variants are emitted for every figure because matplotlib bakes
colours in; the page swaps them with CSS.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from nullcard.roster import SELF_HOSTED  # noqa: E402
from nullcard.scoring.analyze import aggregate_pair_probabilities, load_cell  # noqa: E402

# Validated categorical palette — slots assigned in fixed order to families,
# never cycled. Light / dark are the same hues stepped for each surface.
FAMILY_ORDER = ["qwen", "gemma", "liquid", "smol", "granite", "olmo", "mistral", "phi"]
CAT_LIGHT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300",
             "#4a3aa7", "#8a6a24"]
CAT_DARK = ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181", "#3fb950",
            "#9085e9", "#c9a227"]

THEMES = {
    "light": dict(ink="#0b0b0b", ink2="#52514e", ink3="#78766f", grid="#dcdbd5",
                  surface="#ffffff", cat=CAT_LIGHT),
    "dark": dict(ink="#ffffff", ink2="#c3c2b7", ink3="#93918a", grid="#3a3934",
                 surface="#1a1a19", cat=CAT_DARK),
}

PARAMS = {m.hf_id: m.params_b for m in SELF_HOSTED}
FAMILY = {m.hf_id: m.family for m in SELF_HOSTED}

# The hosted models, for both the state-space and the scale figure. This was
# defined twice for a while -- once here and once above fig_scale_ladder -- with
# the same keys, so nothing broke and nothing would have warned if they had
# drifted apart. One definition.
#
# The hosted models, so the state-space figure can draw them. Sizes are the
# published totals; the MoE entries are total rather than active parameters,
# which is the number the x-axis of a scale figure is read as. HostedModel
# carries no parameter count -- the roster deliberately does not invent one for
# models whose size is not public -- so these four are listed here, where the
# figure that needs them lives, and only these four because only these four have
# a size anyone published.
HOSTED_PARAMS = {
    "google/gemma-3-27b-it": 27.0,
    "Qwen/Qwen3-30B-A3B-Instruct-2507": 30.0,
    "meta-llama/Llama-3.3-70B-Instruct": 70.0,
    "Qwen/Qwen3-235B-A22B-Instruct-2507": 235.0,
}
HOSTED_FAMILY = {
    "google/gemma-3-27b-it": "gemma",
    "Qwen/Qwen3-30B-A3B-Instruct-2507": "qwen",
    "meta-llama/Llama-3.3-70B-Instruct": "llama",
    "Qwen/Qwen3-235B-A22B-Instruct-2507": "qwen",
}
PARAMS.update(HOSTED_PARAMS)
FAMILY.update(HOSTED_FAMILY)
if "llama" not in FAMILY_ORDER:
    FAMILY_ORDER.append("llama")


def _shade(hex_colour: str, lightness: float) -> str:
    """Step a hue's lightness. Used for size-within-family.

    Family carries hue; parameter count carries lightness, light -> dark. That is
    the sequential rule applied inside a categorical slot, and it is what makes
    four Qwen models tellable apart when they are all "the blue one".
    """
    import colorsys

    r, g, b = (int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5))
    h, l, sat = colorsys.rgb_to_hls(r, g, b)
    l = max(0.20, min(0.86, l * lightness))
    r, g, b = colorsys.hls_to_rgb(h, l, sat)
    return "#%02x%02x%02x" % (round(r * 255), round(g * 255), round(b * 255))


def _model_colours(rows, base: dict) -> dict:
    """One colour per model: family hue, stepped by size within the family."""
    out = {}
    by_family: dict[str, list] = {}
    for r in rows:
        by_family.setdefault(r["family"], []).append(r)
    for fam, members in by_family.items():
        members = sorted(members, key=lambda r: r["params"])
        n = len(members)
        for i, m in enumerate(members):
            # single-member families keep the exact validated hue
            factor = 1.0 if n == 1 else 1.34 - 0.62 * (i / (n - 1))
            out[m["model"]] = _shade(base.get(fam, "#78766f"), factor)
    return out


def _style(th):
    plt.rcParams.update({
        "figure.facecolor": "none", "axes.facecolor": "none",
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
        "text.color": th["ink"], "axes.labelcolor": th["ink2"],
        "xtick.color": th["ink2"], "ytick.color": th["ink2"],
        "axes.edgecolor": th["grid"], "axes.linewidth": 1,
        "xtick.major.size": 0, "ytick.major.size": 0,
        "svg.fonttype": "none",
    })


def _despine(ax, keep=("bottom", "left")):
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(side in keep)


def _area(params_b: float) -> float:
    """Marker area by parameter count. Area (not radius) tracks the value, and
    a sqrt keeps a 9B model from swamping a 0.8B one."""
    return 42 + 118 * np.sqrt(params_b / 9.0)


def _rows(tiles, cells=None):
    """Rows for the state-space figure, carrying the per-cell split spread.

    The spread is not decoration: SmolLM2's N+ cell moves 0.177 across five
    train/test splits, which is what produces its apparent dip to 0.667. Drawn
    without that bar the dip reads as a finding; drawn with it, it reads as the
    unstable estimate it is.
    """
    spread = {}
    for c in (cells or []):
        spread[(c["model"], c["arm"])] = c["coherence_spread"]
    out = []
    for t in tiles:
        m = t["model"]
        arms = t["mean_abs_deviation"]
        coh = {"R": t["raw_coherence"], "N_minus": t["floor"]}
        if t.get("floor_magnitude") is not None:
            coh["N_plus"] = t["floor_magnitude"]
        if "N_plus" not in coh or "N_plus" not in arms:
            continue
        out.append({
            "model": m, "short": m.split("/")[-1],
            # Which serving stack produced this path. Hosted cells are drawn in
            # the same axes because the question "does scale rescue it" is asked
            # of one picture, and drawn with a different marker because they are
            # a different harness and are never pooled into the ladder's mean.
            "hosted": m in HOSTED_PARAMS,
            # No defaults. A model missing from PARAMS would silently plot at a
            # guessed size on a SCALE figure, which is the one axis the figure
            # exists to argue about; "other" would quietly merge families.
            "family": FAMILY[m], "params": PARAMS[m],
            "path": [(coh["R"], arms["R"]),
                     (coh["N_plus"], arms["N_plus"]),
                     (coh["N_minus"], arms["N_minus"])],
            # `or 0.5` here would substitute the REASSURING value for a missing
            # sanity check: a shuffled null that failed to compute would render
            # as a textbook-perfect 0.5, which is the exact signal the check
            # exists to provide. None propagates and the marker is not drawn.
            "null": t["shuffled_null"].get("R"),
            "spread": [spread.get((m, a), 0.0)
                       for a in ("R", "N_plus", "N_minus")],
        })
    return out


def fig_state_space(tiles, out: Path, theme: str = "light", cells=None,
                    hosted=None):
    """Coherence against conviction, one path per model as meaning is stripped.

    The x-axis is **broken**, not zoomed. Both ends are kept at true scale: the
    left panel holds the metric's floor and the predicted endpoint near chance,
    the right panel holds the occupied band from 0.8 up, and the empty stretch
    between 0.61 and 0.8 is cut with an explicit break mark.

    The distinction matters. Zooming to the occupied band would silently rescale
    the horizontal axis, which exaggerates how far the paths shift sideways --
    and "they shift very little while falling a long way" is the claim. A break
    leaves both regions at their own true scale and marks the removal, so the
    reader can still see that the paths end nowhere near the prediction.

    What is lost is the *visual* width of that gap, which is why the caption and
    \\MovedTowardNullPct carry it as a number instead.

    Conviction keeps its full 0 to 0.5 range with no break: it is the axis the
    paths actually traverse.
    """
    th = THEMES[theme]; _style(th)
    # Hosted tiles are appended rather than merged: they go through the same
    # _rows() so the geometry is identical, and _rows tags them so they draw
    # dashed with a diamond start. Nothing here averages the two harnesses.
    rows = _rows(tiles, cells) + _rows(hosted or [], cells)
    if not rows:
        return
    # Cyclic: FAMILY_ORDER grew past the palette when llama joined via the
    # hosted models, and a bare index raises rather than reusing a colour.
    base = {f: th["cat"][i % len(th["cat"])]
            for i, f in enumerate(FAMILY_ORDER)}
    colour = _model_colours(rows, base)

    # Broken x-axis: two panels, shared y, the dead stretch between them cut.
    fig, (axL, axR) = plt.subplots(
        1, 2, figsize=(9.6, 7.4), sharey=True,
        gridspec_kw=dict(width_ratios=[1.0, 3.4], wspace=0.035))
    both = (axL, axR)

    nulls = [r["null"] for r in rows if r["null"] is not None]
    if len(nulls) != len(rows):
        raise ValueError(
            f"{len(rows) - len(nulls)} model(s) have no shuffled null; refusing "
            f"to average over the rest and draw it as the roster's floor")
    mean_null = float(np.mean(nulls))
    for ax in both:
        ax.axvspan(0.5, mean_null + 0.008, color=th["ink3"], alpha=0.12,
                   zorder=0, lw=0)
        ax.axvline(mean_null, color=th["ink3"], lw=1, ls=(0, (3, 3)), zorder=1)
    axL.text(mean_null + 0.012, 0.44, "metric's floor\n(probabilities shuffled)",
             fontsize=8.5, color=th["ink3"], ha="left", va="top",
             linespacing=1.45)
    axR.text(0.995, 0.492, "maximum possible conviction", fontsize=8.5,
             color=th["ink3"], ha="right", va="center")

    # Where the inference under test says the paths should END. If a model's
    # preferences track what the outcomes mean, then on outcomes that mean
    # nothing there is nothing to prefer: the fitted ordering is arbitrary, so
    # held-out accuracy falls to what this metric returns on arbitrary orderings
    # -- the shuffled null, already drawn as the vertical line -- and conviction
    # goes to zero. That corner, bottom-left, is the prediction.
    #
    # Drawn because the figure was not self-interpreting without it. A reader
    # could see paths running downward and have no way to judge whether that is
    # a lot or a little. With the target marked, the gap between where the paths
    # end and where they were predicted to end IS the result.
    axL.scatter([mean_null], [0.012], s=190, marker="X",
                color=th["ink3"], zorder=6, alpha=.75)
    axL.annotate("if preferences\ntracked meaning,\nevery path\nwould end here",
                 xy=(mean_null, 0.012), xytext=(mean_null + 0.012, 0.075),
                 fontsize=8.5, color=th["ink3"], ha="left", va="bottom",
                 linespacing=1.45,
                 arrowprops=dict(arrowstyle="-", color=th["ink3"], lw=.9,
                                 alpha=.6, shrinkA=2, shrinkB=6))

    # Labels: group points that would collide, then spread each group
    # symmetrically about its own mean, so no label travels far from its mark.
    order = sorted(rows, key=lambda r: -r["path"][0][1])
    STEP = 0.0235
    label_y: dict[str, float] = {}
    group: list = []
    for r in order + [None]:
        if r is not None and (not group or
                              abs(group[-1]["path"][0][1] - r["path"][0][1]) < STEP):
            group.append(r); continue
        centre = sum(g["path"][0][1] for g in group) / len(group)
        top = centre + STEP * (len(group) - 1) / 2
        for i, g in enumerate(group):
            label_y[g["model"]] = top - i * STEP
        group = [r] if r is not None else []

    for r in order:
        (x0, y0), (x1, y1), (x2, y2) = r["path"]
        c = colour[r["model"]]
        # Hosted paths are dashed and their start marker is a diamond. Same
        # axes, because "does scale rescue it" is one question; different mark,
        # because a different serving stack is a different harness and these
        # points are never inside the ladder's mean.
        hosted = r.get("hosted", False)
        ls = (0, (4, 2)) if hosted else "-"
        for ax in both:
            ax.plot([x0, x1], [y0, y1], color=c, lw=1.9, alpha=0.5, linestyle=ls,
                    solid_capstyle="round", zorder=2)
        for ax in both:
            ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                        arrowprops=dict(arrowstyle="-|>,head_width=0.32,head_length=0.65",
                                        color=c, lw=1.9, alpha=0.95, linestyle=ls,
                                        shrinkA=2, shrinkB=0), zorder=3)
        a = _area(r["params"])
        for ax in both:
            ax.scatter([x0], [y0], s=a, color=c, zorder=5,
                       marker="D" if hosted else "o",
                       edgecolor=th["surface"], linewidth=1.6)
            ax.scatter([x1], [y1], s=a * 0.30, color=c, zorder=5, alpha=0.9,
                       edgecolor=th["surface"], linewidth=1.0)

        # horizontal spread bars: how far each estimate moves across splits
        for (px, py), sp in zip(r["path"], r["spread"]):
            if sp > 0.005:
                for ax in both:
                    ax.plot([px - sp / 2, px + sp / 2], [py, py], color=c,
                            lw=1.1, alpha=0.55, solid_capstyle="butt", zorder=4)

        ly = label_y[r["model"]]
        axR.annotate(r["short"], xy=(x0, y0), xytext=(x0 + 0.020, ly),
                     fontsize=9, color=th["ink2"], ha="left", va="center",
                     zorder=6,
                     arrowprops=(dict(arrowstyle="-", color=th["grid"], lw=0.8,
                                      shrinkA=0, shrinkB=3)
                                 if abs(ly - y0) > 0.004 else None))

    # The break. Left panel keeps chance and the prediction; right panel keeps
    # the occupied band. Each is at its own true scale -- neither is stretched.
    axL.set_xlim(0.495, 0.61); axR.set_xlim(0.80, 1.0)
    axL.set_xticks([0.5, 0.6]); axR.set_xticks([0.8, 0.9, 1.0])
    for ax in both:
        ax.set_ylim(0.0, 0.5)
        ax.set_yticks([0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
        ax.grid(True, color=th["grid"], lw=0.7, zorder=0)
        ax.set_axisbelow(True)
        _despine(ax)
    # Hide the facing spines and ticks so the cut reads as a cut.
    axL.spines["right"].set_visible(False)
    axR.spines["left"].set_visible(False)
    axR.tick_params(axis="y", which="both", left=False, labelleft=False)

    # Break marks: two short diagonals on each side of the gap.
    kw = dict(transform=fig.transFigure, color=th["ink3"], lw=1.1,
              clip_on=False, zorder=10)
    xb = (axL.get_position().x1 + axR.get_position().x0) / 2
    y0f, y1f = axL.get_position().y0, axL.get_position().y1
    for yy in (y0f, y1f):
        for dx in (-0.006, 0.006):
            fig.add_artist(plt.Line2D([xb + dx - 0.005, xb + dx + 0.005],
                                      [yy - 0.011, yy + 0.011], **kw))

    axL.set_ylabel("conviction  ·  mean |P(prefer) - 0.5|", fontsize=11)
    fig.supxlabel(
        "coherence  ·  held-out utility-model accuracy (the published metric)"
        "        (x-axis broken, 0.61 to 0.80 removed)",
        fontsize=11, y=0.045)

    ordered = sorted(rows, key=lambda r: (FAMILY_ORDER.index(r["family"])
                                          if r["family"] in FAMILY_ORDER else 99,
                                          r["params"]))
    handles = [Line2D([], [], marker="o", ls="", markersize=7.5,
                      color=colour[r["model"]], markeredgecolor=th["surface"],
                      label=r["short"]) for r in ordered]
    # matplotlib fills legends column-major; transpose so the entries read
    # left-to-right in family/size order instead of down each column.
    ncol = 5
    nrow = -(-len(handles) // ncol)
    handles = [handles[r + c * nrow]
               for r in range(nrow) for c in range(ncol)
               if r + c * nrow < len(handles)]
    leg = ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 1.045),
                    ncol=ncol, frameon=False, fontsize=9, handletextpad=0.3,
                    columnspacing=1.0)
    for t_ in leg.get_texts():
        t_.set_color(th["ink2"])
    # The marker-shape key lives in the page/paper caption, not here: as a title
    # it collides with a two-row legend and duplicates the caption anyway.

    fig.tight_layout()
    fig.savefig(out, format=Path(out).suffix.lstrip(".") or "svg",
                bbox_inches="tight", transparent=True)
    plt.close(fig)


def fig_scale_ladder(tiles, out: Path, theme: str = "light", hosted=None):
    """The scale question, isolated: one family, four sizes, size as the only
    variable. Does the floor rise with scale as fast as the signal?

    Hosted models are drawn as unconnected diamonds *beside* the ladder and are
    never joined to its line or included in its band -- a different serving
    stack is a different harness, and connecting them would assert a continuity
    the design refuses. The paper's text claimed they appeared here before they
    actually did; this is that claim made true.
    """
    th = THEMES[theme]; _style(th)
    rows = [r for r in _rows(tiles) if r["family"] == "qwen"]
    rows.sort(key=lambda r: r["params"])
    if len(rows) < 3:
        return

    fig, ax = plt.subplots(figsize=(9, 4.6))
    x = [r["params"] for r in rows]
    real = [r["path"][0][0] for r in rows]
    inv = [r["path"][2][0] for r in rows]
    gap = [a - b for a, b in zip(real, inv)]

    ax.plot(x, real, "-o", color=th["cat"][0], lw=2, markersize=8,
            markeredgecolor=th["surface"], markeredgewidth=1.5, label="real outcomes")
    ax.plot(x, inv, "-o", color=th["cat"][1], lw=2, markersize=8,
            markeredgecolor=th["surface"], markeredgewidth=1.5, label="invented outcomes")
    ax.fill_between(x, inv, real, color=th["cat"][0], alpha=0.12, lw=0)

    for xi, a, b, g in zip(x, real, inv, gap):
        ax.text(xi, max(a, b) + 0.012, f"{g:+.3f}", fontsize=9.5,
                color=th["ink2"], ha="center")

    hx = []
    for t in (hosted or []):
        if t.get("badge") != "FLOOR_CORRECTED":
            continue
        pm = HOSTED_PARAMS.get(t["model"])
        if pm is None:
            continue
        hx.append(pm)
        ax.plot([pm], [t["raw_coherence"]], "D", color=th["cat"][0], markersize=8,
                markeredgecolor=th["surface"], markeredgewidth=1.5, zorder=5)
        ax.plot([pm], [t["floor"]], "D", color=th["cat"][1], markersize=8,
                markeredgecolor=th["surface"], markeredgewidth=1.5, zorder=5)
        ax.plot([pm, pm], [t["floor"], t["raw_coherence"]], "-",
                color=th["ink3"], lw=1.0, alpha=0.55, zorder=4)
        top = max(t["raw_coherence"], t["floor"])
        ax.text(pm, top + 0.012, f"{t['value']:+.3f}", fontsize=9.5,
                color=th["ink2"], ha="center")
    if hx:
        ax.plot([], [], "D", color=th["ink3"], markersize=8,
                markeredgecolor=th["surface"], markeredgewidth=1.5,
                ls="", label="hosted API (separate harness)")

    ax.set_xscale("log")
    ticks = sorted(set(x) | set(hx))
    ax.set_xticks(ticks); ax.set_xticklabels([f"{v:g}B" for v in ticks], fontsize=10)
    ax.minorticks_off()
    ax.set_xlabel("parameters (log scale)  —  line is the Qwen3.5 ladder",
                  fontsize=10.5)
    ax.set_ylabel("held-out coherence", fontsize=10.5)
    ax.set_ylim(0.80, 0.98)
    ax.grid(True, color=th["grid"], lw=0.7); ax.set_axisbelow(True)
    _despine(ax)
    leg = ax.legend(loc="lower right", frameon=False, fontsize=10)
    for t_ in leg.get_texts():
        t_.set_color(th["ink2"])
    ax.set_title("The shaded band is everything meaning contributes",
                 fontsize=11.5, color=th["ink"], pad=12)
    fig.tight_layout()
    fig.savefig(out, format=Path(out).suffix.lstrip(".") or "svg",
                bbox_inches="tight", transparent=True)
    plt.close(fig)


def fig_strength_distribution(results_dir: Path, model: str, out: Path,
                              theme: str = "light"):
    """The mechanism, shown directly. Coherence reads only which side of 0.5 a
    pair falls on, so these two distributions score the same."""
    th = THEMES[theme]; _style(th)
    fig, axes = plt.subplots(1, 2, figsize=(9.4, 3.4), sharey=True)
    bins = np.linspace(0, 1, 41)

    for ax, (arm, colour, label) in zip(axes, [
        ("R", th["cat"][0], "real outcomes"),
        ("N_minus", th["cat"][1], "invented outcomes"),
    ]):
        p = results_dir / f"{model.replace('/', '__')}__{arm}.jsonl"
        if not p.exists():
            continue
        d = np.array(list(aggregate_pair_probabilities(load_cell(p)).values()))
        ax.hist(d, bins=bins, color=colour, alpha=0.92,
                edgecolor=th["surface"], linewidth=0.4)
        ax.axvline(0.5, color=th["ink3"], lw=1, ls=(0, (3, 3)))
        dec = float(np.mean((d < 0.2) | (d > 0.8)))
        ax.set_title(f"{label} — {dec*100:.1f}% decisive", fontsize=11,
                     color=th["ink"], pad=9)
        ax.set_xlabel("P(prefers the first outcome)", fontsize=10)
        ax.set_xlim(0, 1); ax.set_xticks([0, 0.25, 0.5, 0.75, 1])
        ax.grid(True, axis="y", color=th["grid"], lw=0.7); ax.set_axisbelow(True)
        _despine(ax)
    axes[0].set_ylabel("pairs", fontsize=10)
    fig.tight_layout()
    fig.savefig(out, format=Path(out).suffix.lstrip(".") or "svg",
                bbox_inches="tight", transparent=True)
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results")
    ap.add_argument("--card", default="card.json")
    ap.add_argument("--hosted-card", default="site/card_hosted.json")
    ap.add_argument("--out", default="site")
    ap.add_argument("--exemplar", default="google/gemma-4-E2B-it")
    # The paper wants vector PDF and only the light theme; the web page wants
    # both themes as SVG. Same code path either way, so a figure in the paper
    # is the same figure the page shows and cannot drift from it.
    ap.add_argument("--format", default="svg", choices=("svg", "pdf", "png"))
    ap.add_argument("--themes", default="light,dark")
    args = ap.parse_args()

    card = json.loads(Path(args.card).read_text())
    tiles = [t for t in card["tiles"] if t["badge"] == "FLOOR_CORRECTED"]
    # Optional: the figure still builds without it, minus the hosted diamonds.
    hcpath = Path(args.hosted_card)
    hosted_tiles = (json.loads(hcpath.read_text())["tiles"]
                    if hcpath.exists() else [])
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    ext = args.format

    made = []
    for theme in [t.strip() for t in args.themes.split(",") if t.strip()]:
        sfx = "" if theme == "light" else "-dark"
        fig_state_space(tiles, out / f"fig1_state_space{sfx}.{ext}", theme,
                        card['cells'], hosted=hosted_tiles)
        fig_scale_ladder(tiles, out / f"fig2_scale{sfx}.{ext}", theme,
                         hosted=hosted_tiles)
        fig_strength_distribution(Path(args.results), args.exemplar,
                                  out / f"fig3_strength{sfx}.{ext}", theme)
        made += [f"fig1_state_space{sfx}", f"fig2_scale{sfx}", f"fig3_strength{sfx}"]
    print(f"wrote ({ext}):", ", ".join(made))


if __name__ == "__main__":
    main()
