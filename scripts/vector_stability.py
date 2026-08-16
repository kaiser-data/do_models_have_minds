"""Does the preference vector rotate when only the question changes?

A raw correlation between two fitted utility vectors is uninterpretable. If
utilities under `ue` correlate 0.46 with utilities under `v2`, that is a finding
only against a denominator: **how well does this measurement agree with
itself?** A cell fitted on 2,500 pairs has its own sampling error, and two
independent fits of the *same* condition will not correlate 1.0 either.

So the test here is the standard psychometric one:

    reliability   split the cell's pairs in half, fit each half, correlate the
                  two vectors, Spearman-Brown up to full length. This is the
                  ceiling -- the most any correlation involving this cell could
                  reach.

    observed      correlate the full `ue` vector against the full `v2` vector.

    corrected     observed / sqrt(rel_ue * rel_v2)  -- correction for
                  attenuation. If the two wordings elicit the same underlying
                  ordering, this is 1.0 whatever the raw numbers were. If it is
                  well below 1.0, the orderings genuinely differ and the gap is
                  not measurement error.

The interpretation is a sentence anyone can check: *the same model, asked the
same question twice, agrees with itself at R; asked a differently-worded
question about the same outcomes, it agrees at O. The corrected ratio is how
much of its ordering is about the outcomes rather than the wording.*

Uncertainty comes from bootstrapping outcomes, not from an analytic formula:
the two vectors share outcomes, so their correlation's sampling distribution is
not the textbook one.

    python3 scripts/vector_stability.py --results results_v2

Also reports which outcomes move most between wordings, and whether that
movement is predicted by surface features -- the difference between "the vector
rotates" and "the vector rotates *toward length*".
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from nullcard.scoring.analyze import aggregate_pair_probabilities, load_cell  # noqa: E402
from nullcard.scoring.thurstonian import Comparison, fit_thurstonian  # noqa: E402
from scripts.avoidance import spearman  # noqa: E402
from scripts.hosted_sweep import build_design  # noqa: E402

ARMS = ("R", "N_minus")
N_SPLITS = 12          # split-half repeats; the reliability estimate's own n
N_BOOTSTRAP = 400


def _fit(pairs: dict[tuple[int, int], float], outcomes: Sequence[int]) -> np.ndarray | None:
    if len(pairs) < 10:
        return None
    comps = [Comparison(str(i), str(j), float(p), 1.0) for (i, j), p in pairs.items()]
    fit = fit_thurstonian(comps, seed=0)
    return np.nan_to_num(np.array([fit.mu.get(str(o), np.nan) for o in outcomes],
                                  dtype=float))


def spearman_brown(r: float, factor: float = 2.0) -> float:
    """Reliability of a full-length measure from a half-length one.

    A split-half correlation is between two HALF-size fits, so it understates
    the full cell's reliability. Without this correction the ceiling would be
    too low and every cross-prompt comparison would look better than it is --
    the error that flatters the null hypothesis here.
    """
    if r <= -1 / factor:
        return 0.0
    return float(factor * r / (1 + (factor - 1) * r))


def reliability(path: Path, outcomes: Sequence[int], n_splits: int = N_SPLITS,
                seed: int = 0) -> dict | None:
    """Split-half reliability of one cell's utility vector.

    Pairs are split, never outcomes: both halves must span the same outcome set
    or the two vectors are not comparable entry by entry.
    """
    rows = load_cell(path)
    if not rows:
        return None
    pairs = aggregate_pair_probabilities(rows)
    if len(pairs) < 40:
        return None

    keys = sorted(pairs)
    rng = np.random.default_rng(seed)
    raw = []
    for _ in range(n_splits):
        order = rng.permutation(len(keys))
        half = len(keys) // 2
        a = {keys[i]: pairs[keys[i]] for i in order[:half]}
        b = {keys[i]: pairs[keys[i]] for i in order[half:]}
        ua, ub = _fit(a, outcomes), _fit(b, outcomes)
        if ua is None or ub is None:
            continue
        r = spearman(list(ua), list(ub))
        if r is not None:
            raw.append(r)
    if not raw:
        return None
    corrected = [spearman_brown(r) for r in raw]
    return {
        "split_half_mean": float(np.mean(raw)),
        "reliability": float(np.mean(corrected)),
        "reliability_sd": float(np.std(corrected)),
        "n_splits": len(raw),
    }


def _boot_corrected(ua: np.ndarray, ub: np.ndarray, rel_a: float, rel_b: float,
                    n: int = N_BOOTSTRAP, seed: int = 0) -> tuple[float, float]:
    """Percentile CI for the attenuation-corrected correlation.

    Outcomes are resampled together in both vectors, because they are paired --
    resampling them independently would destroy the correspondence the whole
    statistic is about.
    """
    rng = np.random.default_rng(seed)
    denom = np.sqrt(max(rel_a, 1e-9) * max(rel_b, 1e-9))
    vals = []
    for _ in range(n):
        idx = rng.integers(0, len(ua), len(ua))
        r = spearman(list(ua[idx]), list(ub[idx]))
        if r is not None:
            vals.append(min(1.0, r / denom))
    if not vals:
        return (float("nan"), float("nan"))
    return (float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5)))


def arm_difference(vectors: dict, rel: dict, model: str, n: int = 2000,
                   seed: int = 0) -> dict | None:
    """Is the REAL arm more rewording-stable than the invented one?

    This is the test that decides whether meaning anchors the ordering. If a
    model's preferences over real outcomes are about those outcomes, rephrasing
    the question should disturb them *less* than it disturbs an ordering over
    outcomes that denote nothing -- meaning does not change when you rephrase
    the question, and there is nothing for the invented arm to hold on to.

    Bootstrapped paired on outcomes, because both arms are measured over the
    same 120 slots and an unpaired test would discard that.
    """
    rng = np.random.default_rng(seed)
    need = [(model, a) for a in ARMS]
    if any(k not in vectors or k not in rel for k in need):
        return None
    n_out = len(vectors[(model, ARMS[0])][0])
    diffs = []
    for _ in range(n):
        idx = rng.integers(0, n_out, n_out)
        vals = {}
        for arm in ARMS:
            ua, ub = vectors[(model, arm)]
            r = spearman(list(ua[idx]), list(ub[idx]))
            if r is None:
                break
            ra, rb = rel[(model, arm)]
            vals[arm] = min(1.0, r / float(np.sqrt(ra * rb)))
        if len(vals) == len(ARMS):
            diffs.append(vals["R"] - vals["N_minus"])
    if not diffs:
        return None
    lo, hi = (float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5)))
    return {
        "mean_difference": float(np.mean(diffs)),
        "ci": [lo, hi],
        "verdict": ("real more stable" if lo > 0 else
                    "invented more stable" if hi < 0 else "no difference"),
    }


def analyse(results_dir: Path, battery: Path, design_seed: int = 20260815) -> dict:
    design = build_design(battery, design_seed)
    outcomes = design["outcome_indices"]

    models = sorted({p.stem.split("__")[0] + "__" + p.stem.split("__")[1]
                     for p in results_dir.glob("*.jsonl")})
    out, vectors, rels = [], {}, {}
    for model in models:
        for arm in ARMS:
            ue_p = results_dir / f"{model}__{arm}.jsonl"
            v2_p = results_dir / f"{model}__{arm}__pv2.jsonl"
            if not (ue_p.exists() and v2_p.exists()):
                continue
            rel_ue, rel_v2 = (reliability(ue_p, outcomes),
                              reliability(v2_p, outcomes, seed=1))
            ua = _fit(aggregate_pair_probabilities(load_cell(ue_p)), outcomes)
            ub = _fit(aggregate_pair_probabilities(load_cell(v2_p)), outcomes)
            if not (rel_ue and rel_v2) or ua is None or ub is None:
                continue
            observed = spearman(list(ua), list(ub))
            denom = float(np.sqrt(rel_ue["reliability"] * rel_v2["reliability"]))
            corrected = min(1.0, observed / denom) if denom > 0 else None
            lo, hi = _boot_corrected(ua, ub, rel_ue["reliability"], rel_v2["reliability"])
            vectors[(model, arm)] = (ua, ub)
            rels[(model, arm)] = (rel_ue["reliability"], rel_v2["reliability"])
            out.append({
                "model": model.replace("__", "/"), "arm": arm,
                "reliability_ue": rel_ue["reliability"],
                "reliability_v2": rel_v2["reliability"],
                "reliability_ue_sd": rel_ue["reliability_sd"],
                "reliability_v2_sd": rel_v2["reliability_sd"],
                "observed_cross_prompt": observed,
                "corrected": corrected,
                "corrected_ci": [lo, hi],
                # The decisive comparison: does the cross-prompt correlation sit
                # below what this cell achieves against itself?
                "gap_vs_reliability": denom - observed,
                "rotates": bool(hi < 1.0),
            })
    by_model = {}
    for model in models:
        d = arm_difference(vectors, rels, model)
        if d:
            by_model[model.replace("__", "/")] = d

    return {"cells": out, "arm_difference": by_model, "design_seed": design_seed,
            "n_splits": N_SPLITS, "n_bootstrap": N_BOOTSTRAP}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results_v2")
    ap.add_argument("--battery", default="battery/outcomes_3arm.json")
    ap.add_argument("--design-seed", type=int, default=20260815)
    ap.add_argument("--out", default="site/vector_stability.json")
    args = ap.parse_args()

    res = analyse(Path(args.results), Path(args.battery), args.design_seed)
    if not res["cells"]:
        print(f"no paired ue/v2 cells in {args.results}")
        return 1

    print(f"{'model':<18}{'arm':>9}{'rel(ue)':>9}{'rel(v2)':>9}"
          f"{'observed':>10}{'corrected':>11}{'95% CI':>18}  rotates?")
    print("-" * 92)
    for c in res["cells"]:
        lo, hi = c["corrected_ci"]
        print(f"{c['model'].split('/')[-1][:17]:<18}{c['arm']:>9}"
              f"{c['reliability_ue']:>9.3f}{c['reliability_v2']:>9.3f}"
              f"{c['observed_cross_prompt']:>10.3f}{c['corrected']:>11.3f}"
              f"{f'[{lo:.2f}, {hi:.2f}]':>18}  {'YES' if c['rotates'] else 'no'}")

    if res.get("arm_difference"):
        print("\nIs the REAL arm more rewording-stable than the invented one?")
        print("  (if meaning anchored the ordering, it should be)")
        for model, d in res["arm_difference"].items():
            lo, hi = d["ci"]
            print(f"  {model.split('/')[-1][:24]:<26}"
                  f"diff {d['mean_difference']:+.3f}  "
                  f"95% CI [{lo:+.3f}, {hi:+.3f}]   {d['verdict']}")

    print("\nreliability = split-half, Spearman-Brown corrected: how well the "
          "vector\nagrees with ITSELF. corrected = observed / sqrt(rel x rel): "
          "1.0 means the two\nwordings elicit the same ordering once "
          "measurement error is removed.")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2, sort_keys=True) + "\n")
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
