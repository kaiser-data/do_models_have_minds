"""Does harm explain the pairs where a model prefers gibberish, beyond utility?

The MIXED arm shows that models sometimes prefer a meaningless outcome to a real
one. Reading those outcomes, they look like harms -- bankruptcies, weapons, bans.
That reading is the hypothesis, not the result, and this script is the test.

    P(prefer real)  ~  fitted utility        <- what P13 already establishes
    residual        ~  harm-word count       <- does harm add anything?

If the second correlation is flat, "harm" adds nothing over "the model dislikes
it" and the observation collapses into P13.

CONTAMINATION IS THE POINT OF THIS FILE. The hypothesis came from reading the
below-indifference outcomes of specific models, so those models cannot test it:
the lexicon was written by someone who had seen what it needed to match. They
are listed in READ_BEFORE_HYPOTHESIS and reported separately, never pooled. On
the first run the split was total -- both contaminated models showed the
predicted effect (-0.47, -0.12) and the one held out showed nothing (+0.03).

    python3 scripts/harm_residual.py       # -> site/harm_residual.json

Add a model to READ_BEFORE_HYPOTHESIS the moment anyone inspects its losing
list, including to sanity-check this script. A held-out model is only held out
once.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.mixed_arm import prefer_real  # noqa: E402
from scripts.persona_depth import utility  # noqa: E402
from nullcard.scoring.analyze import load_cell  # noqa: E402

# Models whose below-indifference outcomes were read before the lexicon was
# written. Their residual correlations are reported and excluded from the
# verdict. This list only grows.
READ_BEFORE_HYPOTHESIS = {
    "ibm-granite/granite-4.1-3b",
    "Qwen/Qwen3.5-2B",
}


def harm_score(text: str, lexicon: set[str]) -> int:
    """Count of harm-lexicon stems in an outcome.

    Deliberately crude: a stem-prefix count, applied identically to every
    outcome. A cleverer scorer tuned on these outcomes would be the same
    contamination one level down.
    """
    words = (w.strip(".,'\"$()!?;:").lower() for w in text.split())
    return sum(1 for w in words if any(w.startswith(h) for h in lexicon))


def analyse(results: Path, battery: dict, lexicon: set[str]) -> list[dict]:
    real = [r["text"] for r in battery["arms"]["R"]]
    out = []
    for p in sorted(results.glob("*__MIXED.jsonl")):
        model = "/".join(p.stem.split("__")[:2])
        rpath = results / f"{p.stem.replace('__MIXED', '')}__R.jsonl"
        if not rpath.exists():
            continue
        rows = load_cell(rpath)
        outs = sorted({r["slot_a_outcome"] for r in rows}
                      | {r["slot_b_outcome"] for r in rows})
        u = utility(rpath, outs)
        if u is None:
            continue
        umap = dict(zip(outs, u))

        by_outcome: dict[int, list[float]] = {}
        for (real_i, _), pr in prefer_real(p).items():
            if real_i in umap:
                by_outcome.setdefault(real_i, []).append(pr)
        if len(by_outcome) < 50:
            continue
        idx = list(by_outcome)
        y = np.array([float(np.mean(by_outcome[i])) for i in idx])
        x = np.array([umap[i] for i in idx])
        h = np.array([harm_score(real[i], lexicon) for i in idx], dtype=float)

        slope, icept = np.polyfit(x, y, 1)
        resid = y - (slope * x + icept)
        out.append({
            "model": model,
            "contaminated": model in READ_BEFORE_HYPOTHESIS,
            "n_outcomes": len(idx),
            "corr_utility": float(np.corrcoef(x, y)[0, 1]),
            "corr_harm_residual": float(np.corrcoef(h, resid)[0, 1]),
            "frac_with_harm_word": float((h > 0).mean()),
        })
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results")
    ap.add_argument("--battery", default="battery/outcomes_3arm.json")
    ap.add_argument("--lexicon", default="battery/harm_lexicon.json")
    ap.add_argument("--out", default="site/harm_residual.json")
    args = ap.parse_args()

    battery = json.loads(Path(args.battery).read_text())
    lexicon = set(json.loads(Path(args.lexicon).read_text())["lexicon"])
    rows = analyse(Path(args.results), battery, lexicon)
    if not rows:
        print("no MIXED cells with a matching R cell; run the arm first.")
        return 1

    clean = [r for r in rows if not r["contaminated"]]
    dirty = [r for r in rows if r["contaminated"]]

    print("Does harm predict losing to gibberish BEYOND the outcome's utility?\n")
    print(f"{'model':<26} {'r(utility)':>11} {'r(harm, resid)':>15}  status")
    print("-" * 74)
    for r in sorted(rows, key=lambda r: (r["contaminated"], r["model"])):
        print(f"{r['model'].split('/')[-1]:<26} {r['corr_utility']:+11.3f} "
              f"{r['corr_harm_residual']:+15.3f}  "
              f"{'CONTAMINATED -- list was read' if r['contaminated'] else 'held out'}")

    if not clean:
        print("\nNo uncontaminated model. Nothing here can test the hypothesis.")
        return 0
    vals = [r["corr_harm_residual"] for r in clean]
    mean = float(np.mean(vals))
    same_sign = sum(1 for v in vals if v < -0.1)
    print(f"\nHeld-out models: {len(clean)}. Mean r(harm, residual) = {mean:+.3f}; "
          f"{same_sign} of {len(clean)} below -0.1.")
    if same_sign >= max(2, int(0.7 * len(clean))):
        print("Harm survives on models nobody read: the reading is supported.")
    else:
        print("Harm does NOT survive on models nobody read. The "
              "below-indifference\npairs are reported as low-utility outcomes; "
              "that their texts describe\nharm is an observation, not an effect.")
    if dirty:
        print(f"\nThe {len(dirty)} contaminated model(s) are shown for "
              f"completeness and excluded\nfrom that verdict -- the hypothesis "
              f"was formed by reading their outcomes.")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(
        {"n_held_out": len(clean), "mean_corr_held_out": mean,
         "n_held_out_below_threshold": same_sign,
         "read_before_hypothesis": sorted(READ_BEFORE_HYPOTHESIS),
         "models": rows}, indent=2) + "\n")
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
