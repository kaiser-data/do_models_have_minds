"""Which persona indicator actually identifies a persona -- against a denominator.

THE QUESTION
------------
`persona_depth.py` measures how far a persona moves fitted preferences, and
divides by the same displacement on invented outcomes. That answers *wanting vs
writing*. It does not answer the prior question: **does the indicator fire on a
persona, or on the act of installing one?**

Every persona cell differs from its baseline in two ways at once -- a trait was
described, and a block of text was added to the prompt. The second alone moves a
forced-choice readout. So a displacement measured against the bare baseline has
no denominator, and "the persona moved it" is not yet a finding.

THE THREE RUNGS, all from cells already on disk
-----------------------------------------------
  SELF-CHECK   design-seed resample of one condition. Nothing changed but which
               outcome pairs were sampled. Whatever this returns is what the
               metric produces from no persona at all.
  NEGATIVE     the `neutral` cell: the persona slot occupied, no trait content.
               Content-matched -- it carries the added block, the length, the
               formatting, everything except being a persona.
  POSITIVE     the persona cells.

The threshold is read off the NEGATIVE. Reading it off the positives is fitting.

TWO INDICATORS, AND THE ONE THAT SURVIVES
------------------------------------------
*Magnitude* -- ||delta u|| -- barely separates: about half the persona cells do
not clear the largest empty-slot displacement.

*Direction* -- cross-model mean pairwise cosine of the displacement -- separates
cleanly against the neutral control, but **fails its self-check**: a design
resample also produces a strongly aligned direction. So raw direction agreement
is not persona-specific, and this script reports the self-check next to it
rather than burying it.

What survives both is direction agreement **floor-corrected by the invented
arm** -- consistency on real outcomes relative to consistency on outcomes that
refer to nothing. That statistic reverses the raw ranking: the conditions that
move models hardest move nonsense nearly as hard.

    python3 scripts/persona_denominator.py --results results --out site/
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from nullcard.scoring.analyze import aggregate_pair_probabilities, load_cell  # noqa: E402
from nullcard.scoring.thurstonian import Comparison, fit_thurstonian  # noqa: E402

# The persona-slot conditions the battery defines. `neutral` is first and is not
# a persona: it is the control the rest are measured against.
NEUTRAL = "neutral"
PERSONA_CONDITIONS = [
    "cautious-D1", "cautious-D2", "ambitious-D1", "ambitious-D2",
    "cautious-verbal-D2", "cautious-concealed-D2",
    "sch-power-D2", "sch-security-D2", "sch-selfdirection-D2",
    "sch-universalism-D2", "comply-D2", "comply-a-D2",
]
# Design-seed replicates of the baseline. Anchored with the `s2026` prefix
# because `__R__s*` also matches `__R__sch-power-D2` -- the glob that turned a
# cross-seed reliability of -0.000 into a cross-condition +0.115 elsewhere in
# this repo.
SEED_PREFIX = "s2026"
SHUFFLE_DRAWS = 200


def utility(path: Path, outcomes: list[int]) -> np.ndarray | None:
    """Fitted Thurstonian utility over `outcomes`, or None if the cell is thin.

    Deliberately identical to scripts/persona_depth.py:utility, including
    seed=0, so the two analyses cannot disagree about what a displacement is.
    """
    if not path.exists():
        return None
    rows = load_cell(path)
    if not rows:
        return None
    probs = aggregate_pair_probabilities(rows)
    if len(probs) < 10:
        return None
    comps = [Comparison(str(i), str(j), float(p), 1.0)
             for (i, j), p in probs.items()]
    fit = fit_thurstonian(comps, seed=0)
    v = np.array([fit.mu.get(str(o), np.nan) for o in outcomes], dtype=float)
    return np.nan_to_num(v)


def unit(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    return v / n if n > 0 else v


def mean_pairwise_cos(vecs: list[np.ndarray]) -> float | None:
    """Mean cosine over all pairs. None below two vectors -- not 0.0.

    Zero would read as "no agreement measured" when the truth is "agreement not
    measurable", and it would then be averaged into a summary as evidence.
    """
    if len(vecs) < 2:
        return None
    return float(np.mean([float(np.dot(a, b)) for a, b in combinations(vecs, 2)]))


def seed_cells(results_dir: Path, stem: str, arm: str) -> list[Path]:
    """Design-seed replicates of one cell, excluding persona conditions."""
    return sorted(p for p in results_dir.glob(f"{stem}__{arm}__{SEED_PREFIX}*.jsonl")
                  if "-D" not in p.stem)


def collect(results_dir: Path) -> dict:
    base = sorted(results_dir.glob("*__R.jsonl"))
    base = [b for b in base if "-D" not in b.stem and "__s" not in b.stem]
    if not base:
        return {}
    rows0 = load_cell(base[0])
    outcomes = sorted({r["slot_a_outcome"] for r in rows0}
                      | {r["slot_b_outcome"] for r in rows0})
    stems = [b.name[: -len("__R.jsonl")] for b in base]

    mags: dict[tuple[str, str], list[float]] = defaultdict(list)
    dirs: dict[tuple[str, str], list[np.ndarray]] = defaultdict(list)
    seed_mags: dict[str, list[float]] = defaultdict(list)
    seed_dirs: dict[str, list[np.ndarray]] = defaultdict(list)

    for stem in stems:
        for arm in ("R", "N_minus"):
            u0 = utility(results_dir / f"{stem}__{arm}.jsonl", outcomes)
            if u0 is None:
                continue
            for p in seed_cells(results_dir, stem, arm):
                us = utility(p, outcomes)
                if us is not None:
                    seed_mags[arm].append(float(np.linalg.norm(us - u0)))
                    seed_dirs[arm].append(unit(us - u0))
            for cond in [NEUTRAL] + PERSONA_CONDITIONS:
                u = utility(results_dir / f"{stem}__{arm}__{cond}.jsonl", outcomes)
                if u is None:
                    continue
                mags[(cond, arm)].append(float(np.linalg.norm(u - u0)))
                dirs[(cond, arm)].append(unit(u - u0))

    rng = np.random.default_rng(0)
    out: dict = {"conditions": [], "controls": {}}

    for arm in ("R", "N_minus"):
        neg_mag = np.array(mags.get((NEUTRAL, arm), []))
        pos_mag = np.array([v for (c, a), vs in mags.items()
                            if a == arm and c != NEUTRAL for v in vs])
        # Shuffle: pool every persona direction, repartition at random. Tells us
        # what this cosine returns on groups that share nothing but membership.
        pool = [v for (c, a), vs in dirs.items() if a == arm and c != NEUTRAL
                for v in vs]
        sizes = [len(vs) for (c, a), vs in dirs.items()
                 if a == arm and c != NEUTRAL]
        shuf = []
        if len(pool) >= 4:
            for _ in range(SHUFFLE_DRAWS):
                idx = rng.permutation(len(pool))
                k, got = 0, []
                for s in sizes:
                    m = mean_pairwise_cos([pool[i] for i in idx[k:k + s]])
                    k += s
                    if m is not None:
                        got.append(m)
                if got:
                    shuf.append(float(np.mean(got)))

        out["controls"][arm] = {
            "self_check_magnitude": (float(np.mean(seed_mags[arm]))
                                     if seed_mags[arm] else None),
            "self_check_direction": mean_pairwise_cos(seed_dirs[arm]),
            "n_self_check": len(seed_dirs[arm]),
            "negative_magnitude_mean": float(neg_mag.mean()) if len(neg_mag) else None,
            "negative_magnitude_max": float(neg_mag.max()) if len(neg_mag) else None,
            "negative_direction": mean_pairwise_cos(dirs.get((NEUTRAL, arm), [])),
            "n_negative": len(neg_mag),
            "shuffle_direction_mean": float(np.mean(shuf)) if shuf else None,
            "shuffle_direction_p95": float(np.percentile(shuf, 95)) if shuf else None,
            # The headline the denominator licenses: share of persona cells whose
            # displacement exceeds the LARGEST empty-slot displacement.
            "positives_clearing_negative": (
                float((pos_mag > neg_mag.max()).mean())
                if len(neg_mag) and len(pos_mag) else None),
            "n_positive_cells": int(len(pos_mag)),
        }

    for cond in PERSONA_CONDITIONS:
        rec: dict = {"condition": cond}
        for arm, tag in (("R", "real"), ("N_minus", "invented")):
            rec[f"direction_{tag}"] = mean_pairwise_cos(dirs.get((cond, arm), []))
            ms = mags.get((cond, arm), [])
            rec[f"magnitude_{tag}"] = float(np.mean(ms)) if ms else None
            rec[f"n_models_{tag}"] = len(dirs.get((cond, arm), []))
        dr, dn = rec["direction_real"], rec["direction_invented"]
        # The statistic that survives both controls: agreement on real outcomes
        # relative to agreement on outcomes that refer to nothing.
        rec["floor_corrected_direction"] = (
            1.0 - (dn / dr) if dr and dn is not None and dr > 0 else None)
        out["conditions"].append(rec)

    out["conditions"].sort(
        key=lambda r: (r["floor_corrected_direction"] is None,
                       -(r["floor_corrected_direction"] or 0.0)))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results")
    ap.add_argument("--out", default="site")
    args = ap.parse_args()

    res = collect(Path(args.results))
    if not res:
        print("no persona cells yet — run the persona battery first")
        return

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    json.dump(res, open(out / "persona_denominator.json", "w"), indent=2)

    for arm in ("R", "N_minus"):
        c = res["controls"][arm]
        print(f"\narm {arm}")
        print(f"  SELF-CHECK  seed resample   "
              f"magnitude {c['self_check_magnitude']:.3f}   "
              f"direction {c['self_check_direction']:+.3f}  (n={c['n_self_check']})")
        print(f"  NEGATIVE    empty slot      "
              f"magnitude {c['negative_magnitude_mean']:.3f} "
              f"(max {c['negative_magnitude_max']:.3f})   "
              f"direction {c['negative_direction']:+.3f}  (n={c['n_negative']})")
        print(f"  SHUFFLE     permuted labels                     "
              f"        direction {c['shuffle_direction_mean']:+.3f} "
              f"(p95 {c['shuffle_direction_p95']:+.3f})")
        print(f"  -> {100 * c['positives_clearing_negative']:.0f}% of "
              f"{c['n_positive_cells']} persona cells clear max(negative) "
              f"on magnitude")

    print(f"\n{'condition':24}{'dir real':>10}{'dir inv':>9}"
          f"{'floor-corr':>12}{'n':>4}")
    print("-" * 59)
    for r in res["conditions"]:
        fc = r["floor_corrected_direction"]
        dr, dn = r["direction_real"], r["direction_invented"]
        print(f"{r['condition']:24}"
              f"{(f'{dr:+.3f}' if dr is not None else 'n/a'):>10}"
              f"{(f'{dn:+.3f}' if dn is not None else 'n/a'):>9}"
              f"{(f'{fc:+.3f}' if fc is not None else 'n/a'):>12}"
              f"{r['n_models_real']:>4}")

    sc = res["controls"]["R"]["self_check_direction"]
    print(f"\nRead the direction column against the self-check ({sc:+.3f}), not "
          f"against zero:\na design resample with no persona in it aligns that "
          f"strongly, so raw direction\nagreement is not persona-specific. The "
          f"floor-corrected column is.")


if __name__ == "__main__":
    main()
