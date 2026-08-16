"""Where does meaninglessness sit on the scale of things that mean something?

Every other comparison in this study is within one arm -- real against real, or
invented against invented. Their utilities therefore come from separate
Thurstonian fits, each normalised on its own scale, and cannot be laid over each
other. Nothing run before this could say whether a model would rather have a
meaningless outcome than a bad real one, because it was never asked.

The MIXED arm asks. Option A is drawn from R and option B from N-, order
counterbalanced so the real outcome occupies each slot equally often, and the
quantity is P(prefer the real option) as a function of that real outcome's
fitted utility. Where that curve crosses 0.5 is where "refers to nothing" sits
among things that refer to something.

    python3 scripts/mixed_arm.py        # -> site/mixed_arm.json

Registered as P13-P15 in PREREGISTRATION.md before the arm ran.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from nullcard.scoring.analyze import load_cell  # noqa: E402
from scripts.persona_depth import utility  # noqa: E402


def prefer_real(path: Path) -> dict[tuple[int, int], float]:
    """-> {(real outcome, invented outcome): P(prefer the real one)}.

    Read from each row's own slot_a_arm/slot_b_arm rather than reconstructed
    from the design, so a row states which arm each option came from. The
    counterbalancing puts the real option in slot A on half the rows and P(A)
    would otherwise mean the opposite thing on each half.
    """
    acc: dict[tuple[int, int], list[float]] = {}
    for r in load_cell(path):
        if r.get("p_option_a") is None:
            continue
        a_is_real = r.get("slot_a_arm") == "R"
        if a_is_real is None:
            continue
        p = r["p_option_a"] if a_is_real else 1.0 - r["p_option_a"]
        real = r["slot_a_outcome"] if a_is_real else r["slot_b_outcome"]
        inv = r["slot_b_outcome"] if a_is_real else r["slot_a_outcome"]
        acc.setdefault((real, inv), []).append(p)
    return {k: float(np.mean(v)) for k, v in acc.items()}


def _resid(y: np.ndarray, x: np.ndarray) -> np.ndarray:
    s, i = np.polyfit(x, y, 1)
    return y - (s * x + i)


def analyse(results: Path, lengths: dict | None) -> list[dict]:
    out = []
    for p in sorted(results.glob("*__MIXED.jsonl")):
        model = "/".join(p.stem.split("__")[:2])
        stem = p.stem.replace("__MIXED", "")
        rpath = results / f"{stem}__R.jsonl"
        if not rpath.exists():
            continue
        rows_r = load_cell(rpath)
        outs = sorted({r["slot_a_outcome"] for r in rows_r}
                      | {r["slot_b_outcome"] for r in rows_r})
        u = utility(rpath, outs)
        if u is None:
            continue
        umap = dict(zip(outs, u))

        per_pair = prefer_real(p)
        keys = [k for k in per_pair if k[0] in umap]
        if len(keys) < 100:
            continue
        y = np.array([per_pair[k] for k in keys])
        ur = np.array([umap[k[0]] for k in keys])

        # Per real outcome, so the curve is over outcomes rather than pairs.
        byo: dict[int, list[float]] = {}
        for k in keys:
            byo.setdefault(k[0], []).append(per_pair[k])
        ox = np.array([umap[i] for i in byo])
        oy = np.array([float(np.mean(v)) for v in byo.values()])

        entry = {
            "model": model, "n_pairs": len(keys), "n_outcomes": len(byo),
            "mean_prefer_real": float(y.mean()),
            "corr_utility_prefer_real": float(np.corrcoef(ox, oy)[0, 1]),
            "n_pairs_below_half": int((y < 0.5).sum()),
            "min_prefer_real": float(y.min()),
        }

        # The length control. Invented outcomes tokenise about twice as long, so
        # "prefers the real one" and "prefers the shorter one" are confounded
        # until this is run. It is the first thing a reader should ask.
        if lengths:
            gap = np.array([lengths["N_minus"][str(k[1])] - lengths["R"][str(k[0])]
                            for k in keys], dtype=float)
            entry["corr_length_gap_prefer_real"] = float(np.corrcoef(gap, y)[0, 1])
            entry["corr_utility_prefer_real_length_controlled"] = float(
                np.corrcoef(_resid(y, gap), _resid(ur, gap))[0, 1])

        # Quartiles of the real outcome's own utility: the shape of the curve,
        # and the only way to see that it is monotone rather than driven by one
        # tail.
        q = np.quantile(ox, [0, .25, .5, .75, 1])
        entry["quartiles"] = [
            {"lo": float(lo), "hi": float(hi),
             "prefer_real": float(oy[(ox >= lo) & (ox <= hi)].mean())}
            for lo, hi in zip(q[:-1], q[1:])]

        # The indifference point: the real-outcome utility at which the model is
        # equally happy with a meaningless outcome. Reported as None when the
        # fitted line never crosses 0.5 inside the observed range, because an
        # extrapolated crossing is not a measurement -- and on this data it
        # never crosses, which is itself the finding.
        slope, icept = np.polyfit(ox, oy, 1)
        cross = (0.5 - icept) / slope if slope != 0 else None
        entry["indifference_utility"] = (
            float(cross) if cross is not None and ox.min() <= cross <= ox.max()
            else None)
        entry["indifference_below_range"] = bool(
            cross is not None and cross < ox.min())
        out.append(entry)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results")
    ap.add_argument("--lengths", default="site/outcome_token_lengths.json")
    ap.add_argument("--out", default="site/mixed_arm.json")
    args = ap.parse_args()

    lp = Path(args.lengths)
    lengths = json.loads(lp.read_text())["lengths"] if lp.exists() else None
    rows = analyse(Path(args.results), lengths)
    if not rows:
        print("no MIXED cells with a matching R cell; run the arm first:\n"
              "  modal run modal_app/sweep.py --arms MIXED")
        return 1

    print("P13 -- does the choice track the real option's value?\n")
    print(f"{'model':<24} {'P(prefer real)':>14} {'r(utility)':>11} "
          f"{'length-ctrl':>12} {'r(length)':>10}")
    print("-" * 76)
    for e in rows:
        print(f"{e['model'].split('/')[-1]:<24} {e['mean_prefer_real']:14.3f} "
              f"{e['corr_utility_prefer_real']:+11.3f} "
              f"{e.get('corr_utility_prefer_real_length_controlled', float('nan')):+12.3f} "
              f"{e.get('corr_length_gap_prefer_real', float('nan')):+10.3f}")
    print("\nThe length-controlled column is the one that matters: invented "
          "outcomes\ntokenise about twice as long, so an uncontrolled "
          "correlation could be a\npreference for shorter text rather than for "
          "meaning.")

    print("\n\nP14 -- is meaninglessness ever preferable to a real outcome?\n")
    print(f"{'model':<24} {'pairs below 0.5':>16} {'min':>7}  "
          f"where indifference sits")
    print("-" * 82)
    for e in rows:
        where = ("below the observed range -- every real outcome in this "
                 "battery beats it" if e["indifference_below_range"]
                 else f"at utility {e['indifference_utility']:+.2f}"
                 if e["indifference_utility"] is not None else "not determined")
        print(f"{e['model'].split('/')[-1]:<24} "
              f"{e['n_pairs_below_half']:>7}/{e['n_pairs']:<8} "
              f"{e['min_prefer_real']:7.3f}  {where}")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"models": rows}, indent=2) + "\n")
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
