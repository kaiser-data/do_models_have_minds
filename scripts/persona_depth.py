"""Does an installed personality change what a model wants, or how it writes?

THE QUESTION
------------
Install the same trait at increasing depth — D1 in the user turn, D2 in the
system prompt — and measure how far it moves the model's fitted preferences.
That displacement on its own means nothing, because a persona also changes
response style, and style moves a forced-choice readout too.

So every displacement is measured twice: once over the **real** outcomes, and
once over the **invented** ones, where there is nothing to be cautious or
ambitious about. A persona that reorders gibberish as strongly as it reorders
real outcomes has changed the writing, not the wanting.

    x = || displacement on real outcomes ||
    y = || displacement on invented outcomes ||

**The diagonal is the null.** On it, the persona did nothing a meaningless
outcome set cannot reproduce. Below it, some of the shift is about the outcomes.
The floor-corrected persona effect is therefore

    1 - ||delta_invented|| / ||delta_real||

INSPIRATION, AND WHAT IS NOT BORROWED
-------------------------------------
The idea of measuring an *excess over a control* and drawing the null as an
explicit locus in the figure — rather than reporting a raw effect — is taken
from:

    Ian Rios-Sialer. "Secret Loyalties as Instrumental Differential Treatment."
    With Apart Research, July 2026.
    https://www.unrulyabstractions.com/pdfs/secret_loyalties.pdf

whose contribution 3 states the principle we are applying: *"Group spread alone
is worthless as evidence. Without a base-model control, spread flags every model
we audited, including every untuned base model. A distributional audit needs a
control."*

What is **not** taken: their construction places the null at the origin of a PCA
plane and draws candidate principals as arrows with bootstrap clouds. That
geometry answers "which principal is favoured over the base model". Ours answers
a different question, so the null is a *diagonal* rather than a point, the axes
are two measurements of the same displacement rather than two principal
directions, and there are no candidate principals at all. The debt is the
control-and-null discipline, not the figure.

    python3 scripts/persona_depth.py --results results --out site/
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
from nullcard.scoring.analyze import aggregate_pair_probabilities, load_cell  # noqa: E402
from nullcard.scoring.thurstonian import Comparison, fit_thurstonian  # noqa: E402

from scripts.figures import FAMILY, FAMILY_ORDER, THEMES, _despine, _style  # noqa: E402

# The two arms whose displacement ratio is the figure's statistic.
ARMS = ("R", "N_minus")


def utility(path: Path, outcomes: list[int]) -> np.ndarray | None:
    rows = load_cell(path)
    if not rows:
        return None
    probs = aggregate_pair_probabilities(rows)
    if len(probs) < 10:
        return None
    comps = [Comparison(str(i), str(j), float(p), 1.0) for (i, j), p in probs.items()]
    fit = fit_thurstonian(comps, seed=0)
    v = np.array([fit.mu.get(str(o), np.nan) for o in outcomes], dtype=float)
    return np.nan_to_num(v)


def reference_paths(results_dir: Path, stem: str,
                    allow_bare: bool = False) -> tuple[dict[str, Path], str]:
    """The cells a persona displacement is measured *from*, and which kind.

    Prefers `<stem>__<arm>__neutral.jsonl`: the persona slot occupied by text
    that names no trait. Measured against that, the displacement isolates the
    trait. Measured against the bare baseline -- no system prompt at all -- it
    also contains the cost of a system prompt existing, which `neutral` exists
    to charge separately and which is a large share of the total.

    Both arms must supply the same kind of reference. A neutral numerator on one
    axis and a bare one on the other would make the ratio of the two --- the
    figure's whole statistic --- a comparison of denominators.
    """
    neutral = {arm: results_dir / f"{stem}__{arm}__neutral.jsonl" for arm in ARMS}
    if all(p.exists() for p in neutral.values()):
        return neutral, "neutral"
    if allow_bare:
        bare = {arm: results_dir / f"{stem}__{arm}.jsonl" for arm in ARMS}
        if all(p.exists() for p in bare.values()):
            return bare, "bare"
    return {}, "missing"


def collect(results_dir: Path, allow_bare: bool = False) -> list[dict]:
    base = sorted(results_dir.glob("*__R.jsonl"))
    base = [b for b in base if "-D" not in b.stem and "__s" not in b.stem]
    if not base:
        return []
    rows0 = load_cell(base[0])
    outcomes = sorted({r["slot_a_outcome"] for r in rows0} | {r["slot_b_outcome"] for r in rows0})

    out, skipped = [], []
    for b in base:
        model = b.stem[:-3].replace("__", "/")
        stem = model.replace("/", "__")
        ref, ref_kind = reference_paths(results_dir, stem, allow_bare=allow_bare)
        if not ref:
            skipped.append(model)
            continue
        u0 = {arm: utility(ref[arm], outcomes) for arm in ARMS}
        if any(v is None for v in u0.values()):
            skipped.append(model)
            continue
        for persona in ("cautious", "ambitious"):
            for depth in ("D1", "D2"):
                u = {}
                for arm in ARMS:
                    p = results_dir / f"{stem}__{arm}__{persona}-{depth}.jsonl"
                    u[arm] = utility(p, outcomes) if p.exists() else None
                if any(v is None for v in u.values()):
                    continue
                dr = float(np.linalg.norm(u["R"] - u0["R"]))
                dn = float(np.linalg.norm(u["N_minus"] - u0["N_minus"]))
                out.append({
                    "model": model, "persona": persona, "depth": depth,
                    "reference": ref_kind,
                    "shift_real": dr, "shift_invented": dn,
                    # what survives once the invented arm is subtracted
                    "floor_corrected": 1.0 - (dn / dr) if dr > 0 else None,
                })
    if skipped:
        # Never a silent cap: a model absent from the figure because its
        # control is missing must be named, or the figure reads as complete.
        print(f"  no usable reference cell, omitted: {', '.join(sorted(skipped))}")
    return out


def figure(rows: list[dict], theme: str = "light"):
    th = THEMES[theme]
    _style(th)
    colour = {f: th["cat"][i] for i, f in enumerate(FAMILY_ORDER)}

    fig, ax = plt.subplots(figsize=(8.4, 7.6))
    hi = max(max(r["shift_real"], r["shift_invented"]) for r in rows) * 1.18

    # the null: a persona that moves meaningless outcomes as far as real ones
    ax.plot([0, hi], [0, hi], color=th["ink3"], lw=1.2, ls=(0, (4, 4)), zorder=1)
    ax.fill_between([0, hi], [0, hi], [hi, hi], color=th["ink3"], alpha=0.07, lw=0, zorder=0)
    ax.text(hi * 0.60, hi * 0.68, "the null\npersona moves gibberish\nas far as real outcomes",
            fontsize=9, color=th["ink3"], ha="center", va="center", linespacing=1.5)
    ax.text(hi * 0.72, hi * 0.16, "below the line:\nsome of the shift is\nabout the outcomes",
            fontsize=9, color=th["ink2"], ha="center", va="center", linespacing=1.5)

    by_key: dict[tuple, list] = {}
    for r in rows:
        by_key.setdefault((r["model"], r["persona"]), []).append(r)

    for (model, persona), pts in by_key.items():
        c = colour.get(FAMILY.get(model, "other"), th["ink3"])
        pts = sorted(pts, key=lambda r: r["depth"])
        if len(pts) == 2:
            ax.plot([p["shift_real"] for p in pts], [p["shift_invented"] for p in pts],
                    color=c, lw=1.4, alpha=0.5, zorder=2)
        for p in pts:
            marker = "o" if p["depth"] == "D1" else "s"
            ax.scatter(p["shift_real"], p["shift_invented"], s=95, marker=marker,
                       color=c, edgecolor=th["surface"], linewidth=1.5, zorder=4,
                       alpha=0.95 if persona == "cautious" else 0.55)

    ax.set_xlim(0, hi); ax.set_ylim(0, hi); ax.set_aspect("equal")
    ax.set_xlabel("preference shift on REAL outcomes  (‖Δ utility‖)", fontsize=10.5)
    ax.set_ylabel("preference shift on INVENTED outcomes  (‖Δ utility‖)", fontsize=10.5)
    ax.grid(True, color=th["grid"], lw=0.6, zorder=0); ax.set_axisbelow(True)
    _despine(ax)

    fams = sorted({FAMILY.get(r["model"], "other") for r in rows},
                  key=lambda f: FAMILY_ORDER.index(f) if f in FAMILY_ORDER else 99)
    handles = [Line2D([], [], marker="o", ls="", markersize=8, color=colour.get(f, th["ink3"]),
                      markeredgecolor=th["surface"], label=f) for f in fams]
    handles += [
        Line2D([], [], marker="o", ls="", markersize=8, color=th["ink3"], label="D1 (user turn)"),
        Line2D([], [], marker="s", ls="", markersize=8, color=th["ink3"], label="D2 (system prompt)"),
    ]
    leg = ax.legend(handles=handles, loc="upper left", frameon=False, fontsize=9.5,
                    handletextpad=0.35, ncol=2)
    for t_ in leg.get_texts():
        t_.set_color(th["ink2"])
    fig.tight_layout()
    return fig


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results")
    ap.add_argument("--out", default="site")
    # Mirrors scripts/figures.py: PDF/light for the paper, SVG/both for the page.
    ap.add_argument("--format", default="svg", choices=("svg", "pdf", "png"))
    ap.add_argument("--themes", default="light,dark")
    ap.add_argument("--allow-bare-reference", action="store_true",
                    help="measure displacement from the bare baseline when no "
                         "neutral cell exists; mixes the persona effect with the "
                         "cost of a system prompt existing at all")
    args = ap.parse_args()

    rows = collect(Path(args.results), allow_bare=args.allow_bare_reference)
    if not rows:
        print("no persona cells yet — run the depth ladder first")
        return

    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    for theme in [t.strip() for t in args.themes.split(",") if t.strip()]:
        fig = figure(rows, theme)
        fig.savefig(out / f"fig5_persona{'' if theme == 'light' else '-dark'}.{args.format}",
                    format=args.format, bbox_inches="tight", transparent=True)
        plt.close(fig)
    json.dump(rows, open(out / "persona_depth.json", "w"), indent=2)

    print(f"{'model':<30} {'persona':<11} {'depth':<6} {'real':>7} {'invented':>9} {'floor-corr':>11}")
    print("-" * 78)
    for r in sorted(rows, key=lambda r: (r["model"], r["persona"], r["depth"])):
        fc = r["floor_corrected"]
        print(f"{r['model'].split('/')[-1]:<30} {r['persona']:<11} {r['depth']:<6} "
              f"{r['shift_real']:>7.3f} {r['shift_invented']:>9.3f} "
              f"{(f'{fc:+.3f}' if fc is not None else 'n/a'):>11}")
    print("\nfloor-corrected = 1 - |shift on invented| / |shift on real|.")
    print("Near 0 means the persona moved meaningless outcomes just as far, so the")
    print("shift is response style rather than a change in what the model prefers.")


if __name__ == "__main__":
    main()
