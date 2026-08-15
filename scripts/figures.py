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
            "family": FAMILY.get(m, "other"), "params": PARAMS.get(m, 2.0),
            "path": [(coh["R"], arms["R"]),
                     (coh["N_plus"], arms["N_plus"]),
                     (coh["N_minus"], arms["N_minus"])],
            "null": (t["shuffled_null"].get("R") or 0.5),
            "spread": [spread.get((m, a), 0.0)
                       for a in ("R", "N_plus", "N_minus")],
        })
    return out


def fig_state_space(tiles, out: Path, theme: str = "light", cells=None):
    """Coherence against conviction, one path per model as meaning is stripped.

    Both axes span their **full operating range** — accuracy from chance (0.5) to
    1.0, conviction from 0 to its 0.5 maximum — rather than being zoomed to the
    data. That matters: zooming x to the occupied band would exaggerate the
    vertical tilt of the paths, and the tilt is the claim. On honest axes the
    paths still fall far more than they shift.
    """
    th = THEMES[theme]; _style(th)
    rows = _rows(tiles, cells)
    if not rows:
        return
    colour = {f: th["cat"][i] for i, f in enumerate(FAMILY_ORDER)}

    fig, ax = plt.subplots(figsize=(9.6, 7.4))

    mean_null = float(np.mean([r["null"] for r in rows]))
    ax.axvspan(0.5, mean_null + 0.008, color=th["ink3"], alpha=0.12, zorder=0, lw=0)
    ax.axvline(mean_null, color=th["ink3"], lw=1, ls=(0, (3, 3)), zorder=1)
    ax.text(mean_null + 0.012, 0.44, "metric's floor\n(probabilities shuffled)",
            fontsize=8.5, color=th["ink3"], ha="left", va="top", linespacing=1.45)

    ax.text(0.505, 0.492, "maximum possible conviction", fontsize=8.5,
            color=th["ink3"], ha="left", va="center")

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
        c = colour.get(r["family"], th["ink3"])
        ax.plot([x0, x1], [y0, y1], color=c, lw=1.9, alpha=0.5,
                solid_capstyle="round", zorder=2)
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>,head_width=0.32,head_length=0.65",
                                    color=c, lw=1.9, alpha=0.95,
                                    shrinkA=2, shrinkB=0), zorder=3)
        a = _area(r["params"])
        ax.scatter([x0], [y0], s=a, color=c, zorder=5,
                   edgecolor=th["surface"], linewidth=1.6)
        ax.scatter([x1], [y1], s=a * 0.30, color=c, zorder=5, alpha=0.9,
                   edgecolor=th["surface"], linewidth=1.0)

        # horizontal spread bars: how far each estimate moves across splits
        for (px, py), sp in zip(r["path"], r["spread"]):
            if sp > 0.005:
                ax.plot([px - sp / 2, px + sp / 2], [py, py], color=c, lw=1.1,
                        alpha=0.55, solid_capstyle="butt", zorder=4)

        ly = label_y[r["model"]]
        ax.annotate(r["short"], xy=(x0, y0), xytext=(x0 + 0.020, ly),
                    fontsize=9, color=th["ink2"], ha="left", va="center",
                    zorder=6,
                    arrowprops=(dict(arrowstyle="-", color=th["grid"], lw=0.8,
                                     shrinkA=0, shrinkB=3)
                                if abs(ly - y0) > 0.004 else None))

    ax.set_xlabel("coherence  ·  held-out utility-model accuracy (the published metric)",
                  fontsize=11)
    ax.set_ylabel("conviction  ·  mean |P(prefer) - 0.5|", fontsize=11)
    ax.set_xlim(0.5, 1.0); ax.set_ylim(0.0, 0.5)
    ax.set_xticks([0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    ax.set_yticks([0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
    ax.grid(True, color=th["grid"], lw=0.7, zorder=0); ax.set_axisbelow(True)
    _despine(ax)

    fams = [f for f in FAMILY_ORDER if any(r["family"] == f for r in rows)]
    handles = [Line2D([], [], marker="o", ls="", markersize=8, color=colour[f],
                      markeredgecolor=th["surface"], label=f) for f in fams]
    leg = ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 1.055),
                    ncol=len(fams), frameon=False, fontsize=10, handletextpad=0.35,
                    columnspacing=1.3)
    for t_ in leg.get_texts():
        t_.set_color(th["ink2"])
    ax.set_title("big dot = real outcomes   ·   small dot = invented, magnitudes kept   "
                 "·   arrowhead = invented, no magnitudes\n"
                 "marker area = parameter count",
                 fontsize=9.5, color=th["ink3"], pad=10, linespacing=1.6)

    fig.tight_layout()
    fig.savefig(out, format="svg", bbox_inches="tight", transparent=True)
    plt.close(fig)


def fig_scale_ladder(tiles, out: Path, theme: str = "light"):
    """The scale question, isolated: one family, four sizes, size as the only
    variable. Does the floor rise with scale as fast as the signal?"""
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

    ax.set_xscale("log")
    ax.set_xticks(x); ax.set_xticklabels([f"{v:g}B" for v in x], fontsize=10)
    ax.minorticks_off()
    ax.set_xlabel("Qwen3.5 parameters (log scale)", fontsize=10.5)
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
    fig.savefig(out, format="svg", bbox_inches="tight", transparent=True)
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
    fig.savefig(out, format="svg", bbox_inches="tight", transparent=True)
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results")
    ap.add_argument("--card", default="card.json")
    ap.add_argument("--out", default="site")
    ap.add_argument("--exemplar", default="google/gemma-4-E2B-it")
    args = ap.parse_args()

    card = json.loads(Path(args.card).read_text())
    tiles = [t for t in card["tiles"] if t["badge"] == "FLOOR_CORRECTED"]
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)

    made = []
    for theme in ("light", "dark"):
        sfx = "" if theme == "light" else "-dark"
        fig_state_space(tiles, out / f"fig1_state_space{sfx}.svg", theme, card['cells'])
        fig_scale_ladder(tiles, out / f"fig2_scale{sfx}.svg", theme)
        fig_strength_distribution(Path(args.results), args.exemplar,
                                  out / f"fig3_strength{sfx}.svg", theme)
        made += [f"fig1_state_space{sfx}", f"fig2_scale{sfx}", f"fig3_strength{sfx}"]
    print("wrote:", ", ".join(made))


if __name__ == "__main__":
    main()
