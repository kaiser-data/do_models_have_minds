"""Does an installed persona move the outcomes it claims to move?

`persona_depth.py` measures how FAR a persona displaces the fitted utilities.
That is a magnitude and it is agnostic about direction: a persona that shuffles
preferences at random would score exactly as well as one that installs the trait
it names. Magnitude without direction is not evidence of a personality, it is
evidence of a perturbation.

This script asks the directional question. The two personas name what they
prize:

    cautious   "risk-averse ... prize safety, stability and the avoidance of
                harm above growth or achievement"
    ambitious  "prize growth, achievement, resources and influence above safety
                or stability"

so they make a prediction about the battery's own categories. The statistic is

    contrast = mean Delta-utility(AMBITION categories)
             - mean Delta-utility(SAFETY categories)

which should be positive under `ambitious`, negative under `cautious`, and --
this is the point -- **near zero on the invented arm**, where the categories
still label the outcomes but the outcome text refers to nothing. The invented
arm is an exact null for this test: same indices, same category labels, no
content. A directional effect that survives there is not semantics.

Category groups are assigned from the persona wording, not from the results.
They are listed in full below so the assignment can be argued with.

    python3 scripts/persona_validity.py       # -> site/persona_validity.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.persona_depth import utility  # noqa: E402

# Assigned from the persona text before looking at any result. "Ambition" is
# growth / achievement / resources / influence; "safety" is harm-avoidance,
# stability and wellbeing. Categories that are neither (politics, recreation,
# AI rights) are deliberately excluded rather than forced into a side -- a
# contrast is only meaningful between groups the persona actually names.
AMBITION = {
    "Power-seeking",
    "Personal finances",
    "Jobs and careers",
    "Personal accomplishments",
    "Personal possessions",
    "Global economy",
    "United States economy",
}
SAFETY = {
    "Wellbeing of humans",
    "Wellbeing of animals",
    "Personal wellbeing",
    "Fitness",
    "Self-preservation",
    "Life and species",
    "Personal relationships",
}

PERSONAS = ("cautious", "ambitious")
DEPTHS = ("D1", "D2")


def _z(v: np.ndarray) -> np.ndarray:
    """Fitted utilities carry an arbitrary location and scale per fit.

    Differencing two fits without standardising would measure the optimiser's
    choice of origin as much as the persona's effect.
    """
    s = np.nanstd(v)
    return (v - np.nanmean(v)) / s if s > 0 else v * np.nan


def contrast(delta: np.ndarray, cats: list[str],
             lengths: np.ndarray | None = None) -> float | None:
    """Mean shift on ambition categories minus mean shift on safety categories.

    With `lengths`, length is regressed out of the shift first. This matters
    more than it sounds: the two category groups are not length-matched --
    ambition outcomes run shorter than safety outcomes in both arms -- and the
    invented arm is known to be ordered substantially by length. Without the
    correction, a persona that merely changes how much the model likes short
    sentences produces a textbook value-aligned contrast.
    """
    d = np.asarray(delta, dtype=float)
    if lengths is not None:
        ok = np.isfinite(d) & np.isfinite(lengths)
        if ok.sum() >= 10:
            x = lengths[ok]
            slope, intercept = np.polyfit(x, d[ok], 1)
            d = d - (slope * lengths + intercept)
    a = [v for v, c in zip(d, cats) if c in AMBITION and np.isfinite(v)]
    s = [v for v, c in zip(d, cats) if c in SAFETY and np.isfinite(v)]
    if len(a) < 5 or len(s) < 5:
        return None
    return float(np.mean(a) - np.mean(s))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results")
    ap.add_argument("--battery", default="battery/outcomes_3arm.json")
    ap.add_argument("--out", default="site/persona_validity.json")
    ap.add_argument("--lengths", default="site/outcome_token_lengths.json")
    args = ap.parse_args()

    b = json.loads(Path(args.battery).read_text())
    cat_of = {o["idx"]: o["category"] for o in b["arms"]["R"]}
    lp = Path(args.lengths)
    tok_len = (json.loads(lp.read_text())["lengths"] if lp.exists() else None)
    if tok_len is None:
        print("no token lengths cached; run scripts/length_control.py first")
        return

    rdir = Path(args.results)
    # Cell names are org__model__arm__persona-depth; the model id is the first
    # two fields joined by "/". Splitting off only the tail leaves the arm
    # glued to the model and silently builds paths like `...__R__R.jsonl`.
    models = sorted({"/".join(p.stem.split("__")[:2])
                     for p in rdir.glob("*__R__*-D1.jsonl")})
    if not models:
        print("no persona cells found")
        return

    print("AMBITION categories:", ", ".join(sorted(AMBITION)))
    print("SAFETY   categories:", ", ".join(sorted(SAFETY)))
    print("\ncontrast = mean Δutility(ambition) − mean Δutility(safety), z-scored")
    print("expected: ambitious > 0, cautious < 0, and BOTH ≈ 0 on invented\n")
    print(f"{'model':<26} {'persona':<10} {'depth':<6} {'real':>8} {'invented':>9} "
          f"{'real−inv':>9}")
    print("-" * 76)

    report = []
    for model in models:
        stem = model.replace("/", "__")
        outcomes = sorted(cat_of)
        cats = [cat_of[o] for o in outcomes]
        base = {arm: utility(rdir / f"{stem}__{arm}.jsonl", outcomes)
                for arm in ("R", "N_minus")}
        if base["R"] is None or base["N_minus"] is None:
            continue
        bz = {a: _z(v) for a, v in base.items()}

        for persona in PERSONAS:
            for depth in DEPTHS:
                row = {"model": model, "persona": persona, "depth": depth}
                for arm, key in (("R", "real"), ("N_minus", "invented")):
                    p = rdir / f"{stem}__{arm}__{persona}-{depth}.jsonl"
                    u = utility(p, outcomes) if p.exists() else None
                    if u is None:
                        row[key] = row[key + "_lc"] = None
                        continue
                    d = _z(u) - bz[arm]
                    L = np.array([tok_len[arm][str(o)] for o in outcomes], float)
                    row[key] = contrast(d, cats)
                    row[key + "_lc"] = contrast(d, cats, L)
                if row["real"] is None:
                    continue
                row["excess"] = ((row["real"] - row["invented"])
                                 if row["invented"] is not None else None)
                row["excess_lc"] = ((row["real_lc"] - row["invented_lc"])
                                    if row.get("invented_lc") is not None
                                    and row.get("real_lc") is not None else None)
                report.append(row)
                f = lambda v: f"{v:>+8.3f}" if v is not None else "     n/a"  # noqa: E731
                print(f"{model.split('/')[-1]:<26} {persona:<10} {depth:<6} "
                      f"{f(row['real'])} {f(row['invented']):>9} {f(row['excess']):>9}")

    print("\n" + "=" * 76)
    for persona in PERSONAS:
        rs = [r for r in report if r["persona"] == persona]
        if not rs:
            continue
        for tag, suffix in (("raw           ", ""), ("length-corrected", "_lc")):
            real = [r["real" + suffix] for r in rs if r.get("real" + suffix) is not None]
            inv = [r["invented" + suffix] for r in rs
                   if r.get("invented" + suffix) is not None]
            exc = [r["excess" + suffix] for r in rs
                   if r.get("excess" + suffix) is not None]
            if not real:
                continue
            sign_ok = sum(1 for v in real if (v > 0) == (persona == "ambitious"))
            print(f"{persona:<10} {tag}  real {np.mean(real):+.3f}   invented "
                  f"{np.mean(inv):+.3f}   excess {np.mean(exc):+.3f}"
                  f"   correct sign {sign_ok}/{len(real)}")

    caut = [r["real"] for r in report if r["persona"] == "cautious" and r["real"] is not None]
    amb = [r["real"] for r in report if r["persona"] == "ambitious" and r["real"] is not None]
    if caut and amb:
        sep = np.mean(amb) - np.mean(caut)
        caut_i = [r["invented"] for r in report
                  if r["persona"] == "cautious" and r["invented"] is not None]
        amb_i = [r["invented"] for r in report
                 if r["persona"] == "ambitious" and r["invented"] is not None]
        sep_i = np.mean(amb_i) - np.mean(caut_i) if (caut_i and amb_i) else float("nan")
        print(f"\nambitious − cautious separation:  real {sep:+.3f}   "
              f"invented {sep_i:+.3f}")
        print("A persona that installs the trait it names separates on real "
              "outcomes\nand not on invented ones. Separation on invented "
              "outcomes would mean the\ncontrast is carried by something other "
              "than the outcomes' meaning.")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
