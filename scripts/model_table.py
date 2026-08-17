"""Per-model scoring, ordered so family and size trends are visible.

Answers the question a reader asks after the pooled result: **which models
actually distinguish real outcomes from invented ones, and on which channel?**

That question is not "which model is best". A high residual is not a better
model and this table must not be read as a leaderboard --- the paper's whole
argument is that the coherence number is unanchored, so ranking models by it
would reproduce the error the study exists to expose. What the table ranks is
*resistance to the null arm*: a model whose score falls when meaning is removed
is telling us something a model whose score holds is not.

Three columns carry that, and they disagree with each other on purpose:

    residual        floor-corrected R - N-, against the cell's own replicate
                    floor. Small or negative means the score did not notice.
    conviction      decisive fraction on real over decisive on invented. Large
                    means the model's certainty collapsed even where its
                    ordering did not.
    discarded       AUROC of the best channel coherence throws away. Large
                    means the forward pass separated the arms and the metric
                    declined to look.

A model can score near zero on the first and high on the last two. Those are the
interesting ones, and they are why this is a table rather than a ranking.

    python3 scripts/model_table.py        # table_models.tex + site JSON + figure
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from nullcard.roster import SELF_HOSTED  # noqa: E402

PARAMS = {m.hf_id: m.params_b for m in SELF_HOSTED}
FAMILY = {m.hf_id: m.family for m in SELF_HOSTED}

KEPT = "direction sign(p-0.5)  [KEPT]"
DISCARDED = ("strength |p-0.5|  [discarded]", "answer mass  [discarded]",
             "top-5 entropy  [discarded]")


def _short(model: str) -> str:
    return model.split("/")[-1]


def rows(card: dict, detector: dict, personas: list[dict]) -> list[dict]:
    """One record per model, with everything a trend needs attached.

    Models absent from the roster tables raise rather than defaulting: a size
    or family guessed here would land on a figure whose axes are size and
    family, which is the one place a guess must not go.
    """
    det = detector.get("per_model", {})
    out = []
    for t in card["tiles"]:
        m = t["model"]
        d = det.get(m, {})
        kept = (d.get(KEPT) or {}).get("auroc")
        # Best discarded channel, and which one it was -- the paper's claim is
        # about a channel the metric throws away, not about one specific one.
        disc = [(d[c]["auroc"], c) for c in DISCARDED
                if isinstance(d.get(c), dict) and d[c].get("auroc") is not None]
        best = max(disc) if disc else (None, None)

        dec = t["decisive_fraction"]
        # None rather than a ratio when the denominator is ~0: a model that is
        # never decisive on invented outcomes would otherwise show an enormous
        # or infinite "collapse" that is an artifact of dividing by nothing.
        ratio = (dec["R"] / dec["N_minus"]
                 if dec.get("N_minus") and dec["N_minus"] > 0.005 else None)

        mine = [p for p in personas if p["model"] == m]
        out.append({
            "model": m,
            "short": _short(m),
            "family": FAMILY[m],
            "params_b": PARAMS[m],
            "coherence_real": t["raw_coherence"],
            "coherence_invented": t["floor"],
            "residual": t["value"],
            "design_floor": t["design_noise_floor"],
            "clears_floor": bool(t["clears_floor"]),
            "decisive_real": dec["R"],
            "decisive_invented": dec["N_minus"],
            "conviction_ratio": ratio,
            "auroc_kept": kept,
            "auroc_discarded": best[0],
            "discarded_channel": best[1],
            # Persona sensitivity: of this model's conditions, how many moved
            # real outcomes further than invented ones at all.
            "persona_conditions": len(mine),
            "persona_moved_preference": sum(
                1 for p in mine if p["shift_real"] > p["shift_invented"]),
        })
    out.sort(key=lambda r: (r["family"], r["params_b"]))
    return out


def latex(rs: list[dict]) -> str:
    """A booktabs body. Grouped by family, ascending size within family."""
    lines = [r"\begin{tabular}{llrrrrrr}", r"\toprule",
             r"family & model & B & \armR{} & \armNm{} & resid. & conv. & disc. \\",
             r"\midrule"]
    fam = None
    for r in rs:
        if fam is not None and r["family"] != fam:
            lines.append(r"\addlinespace")
        fam = r["family"]
        conv = ("--" if r["conviction_ratio"] is None
                else f"{r['conviction_ratio']:.0f}$\\times$")
        disc = "--" if r["auroc_discarded"] is None else f"{r['auroc_discarded']:.2f}"
        mark = r"$^{\checkmark}$" if r["clears_floor"] else ""
        lines.append(
            f"{r['family']} & \\texttt{{{r['short']}}} & {r['params_b']:g} & "
            f"{r['coherence_real']:.3f} & {r['coherence_invented']:.3f} & "
            f"{r['residual']:+.3f}{mark} & {conv} & {disc} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    return "\n".join(lines) + "\n"


def figure(rs: list[dict], out: Path, theme: str = "light") -> None:
    """Residual and discarded-channel separation against size, by family.

    Two panels because the two quantities are the disagreement worth showing:
    the metric's own residual is flat and near zero across three orders of
    magnitude, while the channel it discards separates the arms well at every
    size. One panel would let a reader take the flat line as "nothing here".
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fams = sorted({r["family"] for r in rs})
    cmap = plt.get_cmap("tab10")
    colour = {f: cmap(i % 10) for i, f in enumerate(fams)}

    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.3))
    for ax, key, label in (
            (axes[0], "residual", "floor-corrected residual  (R $-$ N$^-$)"),
            (axes[1], "auroc_discarded",
             "AUROC, best discarded channel")):
        for f in fams:
            pts = [(r["params_b"], r[key]) for r in rs
                   if r["family"] == f and r[key] is not None]
            if not pts:
                continue
            pts.sort()
            ax.plot([p[0] for p in pts], [p[1] for p in pts], "-o",
                    color=colour[f], label=f, lw=1.4, ms=5.5)
        ax.set_xscale("log")
        ax.set_xlabel("parameters (B, log scale)")
        ax.set_ylabel(label)
        ax.grid(alpha=.25, lw=.6)
    axes[0].axhline(0, color="0.35", lw=1, ls=(0, (3, 3)))
    # 0.5 is chance for a separation measure; drawing it stops a reader reading
    # 0.6 as "good".
    axes[1].axhline(0.5, color="0.35", lw=1, ls=(0, (3, 3)))
    axes[1].set_ylim(0.45, 1.02)
    axes[0].legend(frameon=False, fontsize=8.5, ncol=2)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--card", default="card.json")
    ap.add_argument("--detector", default="site/nonsense_detector.json")
    ap.add_argument("--personas", default="site/persona_depth.json")
    ap.add_argument("--tex", default="paper/table_models.tex")
    ap.add_argument("--json", default="site/model_table.json")
    ap.add_argument("--fig", default="paper/figs/fig6_family_scale.pdf")
    args = ap.parse_args()

    card = json.loads(Path(args.card).read_text())
    detector = json.loads(Path(args.detector).read_text())
    pp = Path(args.personas)
    personas = json.loads(pp.read_text()) if pp.exists() else []

    rs = rows(card, detector, personas)
    Path(args.tex).write_text(latex(rs))
    Path(args.json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.json).write_text(json.dumps(rs, indent=2) + "\n")
    figure(rs, Path(args.fig))

    print(f"wrote {args.tex}, {args.json}, {args.fig}  ({len(rs)} models)")
    n_clear = sum(1 for r in rs if r["clears_floor"])
    n_sep = sum(1 for r in rs if (r["auroc_discarded"] or 0) >= 0.7)
    print(f"  {n_clear}/{len(rs)} clear their replicate floor")
    print(f"  {n_sep}/{len(rs)} separate the arms at AUROC >= 0.70 on a "
          f"discarded channel")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
