"""Does the answer-mass gate select a different sample on each arm?

`aggregate_pair_probabilities` drops any row whose `answer_mass` falls below
`ANSWER_MASS_FLOOR` (0.5). The gate is correct in intent -- a row where the
model put most of its first-token mass on something other than "A" or "B" is
not a preference, it is a model declining to answer in the position we read.
But the gate is applied to each arm independently, and it does not drop the
same rows on each.

    A model about to say "Let me think about this..." has low answer mass, so
    the row is discarded rather than scored. If invented outcomes provoke more
    of that than real ones do, then the invented arm is scored on the subset of
    pairs the model answered reflexively -- and reflexive answers are exactly
    the ones most likely to follow a cheap surface heuristic, which is to say
    the ones most likely to be coherent.

Measured on the nine baseline models at design seed 20260816, that is real on
two of them and absent on the other seven:

    SmolLM3-3B        drop 0.0% on R -> 1.1% on N-   (54 pairs), mass .896 -> .709
    gemma-4-E2B-it    drop 2.6% on R -> 6.6% on N-   (97 pairs), mass .970 -> .902

Both are in the direction that flatters this paper's thesis. The thesis is that
R and N- coherence are close; inflating N- by dropping its hardest pairs closes
the gap for free. A bias that favours the conclusion is the one that has to be
bounded rather than mentioned.

The correction is not a better gate. It is to score both arms on the pairs that
survived in **both**, so that the R-minus-N- contrast is a difference between
two numbers computed over one pair set. What is left after that cannot be
attributed to which rows the gate kept.

    python3 scripts/attrition_control.py
    python3 scripts/attrition_control.py --results results --out site/

Reports, per model and design seed: the raw residual, the matched residual, how
many pairs matching cost, and a sensitivity sweep over the floor itself.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from nullcard.runner.forced_choice import ANSWER_MASS_FLOOR  # noqa: E402
from nullcard.scoring.analyze import (  # noqa: E402
    aggregate_pair_probabilities, cell_coherence, load_cell)

ARMS = ("R", "N_plus", "N_minus")
CONTRAST = ("R", "N_minus")

# The floor is a free parameter of the measurement and nothing in the paper
# reports how much the answer depends on it. These are the levels swept; 0.0
# means "score every row that produced a probability at all".
FLOOR_LEVELS = (0.0, 0.3, 0.5, 0.7, 0.9)

_CELL = re.compile(r"^(?P<model>.+)__(?P<arm>R|N_plus|N_minus)(?:__s(?P<seed>\d+))?\.jsonl$")


# ---------------------------------------------------------------------------
# Attrition, counted the way the runner drops rows
# ---------------------------------------------------------------------------

def attrition_profile(rows: Sequence[Mapping],
                      min_mass: float = ANSWER_MASS_FLOOR) -> dict:
    """How much of a cell never reaches the fit, and why.

    Two failures, counted apart because they mean different things: a row with
    no `p_option_a` is a model that emitted nothing scoreable, a row below the
    mass floor is a model that emitted a scoreable token while putting its mass
    elsewhere. Pooled into `drop_fraction` because both cost the fit a row.

    `mean_answer_mass` is over all rows including the dropped ones. Averaging
    over survivors would report the health of the sample the gate produced
    rather than the sample it was given, which is the number that hides the
    effect this module exists to find.
    """
    n = len(rows)
    unscored = sum(1 for r in rows if r.get("p_option_a") is None)
    below = sum(1 for r in rows
                if r.get("p_option_a") is not None
                and r.get("answer_mass", 1.0) < min_mass)
    mass = sum(r.get("answer_mass", 0.0) for r in rows) / n if n else 0.0
    return {
        "n_rows": n,
        "n_unscored": unscored,
        "n_below_mass": below,
        "drop_fraction": (unscored + below) / n if n else 0.0,
        "mean_answer_mass": mass,
    }


# ---------------------------------------------------------------------------
# The control
# ---------------------------------------------------------------------------

def matched_pair_probabilities(
    rows_a: Sequence[Mapping],
    rows_b: Sequence[Mapping],
    min_mass: float = ANSWER_MASS_FLOOR,
) -> tuple[dict[tuple[int, int], float], dict[tuple[int, int], float]]:
    """Both arms' pair probabilities, restricted to the pairs both retained.

    Each arm is aggregated by the ordinary path first -- so counterbalancing
    and the mass gate apply exactly as they do in the paper -- and only then
    intersected. A pair that lost one presentation order in either arm is
    already gone before the intersection, which is why matching cannot
    resurrect a single-order pair.

    The values are each arm's own. The control equalises which pairs are
    scored, never what the model said about them.
    """
    pa = aggregate_pair_probabilities(rows_a, min_answer_mass=min_mass)
    pb = aggregate_pair_probabilities(rows_b, min_answer_mass=min_mass)
    shared = pa.keys() & pb.keys()
    return ({k: pa[k] for k in shared}, {k: pb[k] for k in shared})


def split_indices(pair_probabilities: Mapping[tuple[int, int], float],
                  seed: int = 0, test_fraction: float = 0.2):
    """The train/test partition `cell_coherence` will use, as key tuples.

    Exposed so the fold alignment is testable rather than assumed. It mirrors
    `cell_coherence`: comparisons are built in sorted key order and permuted by
    a seeded generator, so the fold is a function of the key set and the seed
    and of nothing else. Two arms sharing a key set therefore share a fold, and
    a matched residual cannot move because the two arms were split differently.
    """
    import numpy as np

    keys = sorted(pair_probabilities)
    order = np.random.default_rng(seed).permutation(len(keys))
    cut = int((1 - test_fraction) * len(keys))
    return (tuple(keys[i] for i in order[:cut]),
            tuple(keys[i] for i in order[cut:]))


def _coherence(pp: Mapping[tuple[int, int], float], seed: int) -> float | None:
    """None only when the pair set is genuinely too thin to fit.

    ValueError is the fit declining a degenerate input and is a real None. A
    KeyError is this module misspelling a key, and is deliberately *not*
    caught: an earlier version swallowed one and reported "nothing to match"
    for every cell in the tree, which reads exactly like a clean null.
    """
    if len(pp) < 10:
        return None
    try:
        return float(cell_coherence(pp, seed=seed)["held_out_accuracy"])
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Walking the results tree
# ---------------------------------------------------------------------------

def cells_by_model_seed(results_dir: Path) -> dict[tuple[str, int], dict[str, Path]]:
    """Baseline cells only, keyed by (model, design seed).

    Persona and neutral cells carry a `persona` in their filename and are not
    part of this contrast; an unseeded filename is the original design seed.
    """
    out: dict[tuple[str, int], dict[str, Path]] = {}
    for path in sorted(results_dir.glob("*.jsonl")):
        m = _CELL.match(path.name)
        if not m:
            continue
        seed = int(m.group("seed")) if m.group("seed") else 0
        out.setdefault((m.group("model"), seed), {})[m.group("arm")] = path
    return out


def analyse(results_dir: Path, floor_levels=FLOOR_LEVELS) -> dict:
    hi, lo = CONTRAST
    cells = cells_by_model_seed(results_dir)
    per_cell, sweep = [], []

    for (model, seed), arms in sorted(cells.items()):
        if hi not in arms or lo not in arms:
            continue
        rows = {a: load_cell(arms[a]) for a in (hi, lo)}
        prof = {a: attrition_profile(rows[a]) for a in (hi, lo)}

        raw = {a: aggregate_pair_probabilities(rows[a]) for a in (hi, lo)}
        mat_hi, mat_lo = matched_pair_probabilities(rows[hi], rows[lo])

        c_raw = {a: _coherence(raw[a], seed=0) for a in (hi, lo)}
        c_mat = {hi: _coherence(mat_hi, seed=0), lo: _coherence(mat_lo, seed=0)}
        if None in c_raw.values() or None in c_mat.values():
            continue

        per_cell.append({
            "model": model, "design_seed": seed,
            "n_pairs_raw": {a: len(raw[a]) for a in (hi, lo)},
            "n_pairs_matched": len(mat_hi),
            "pairs_lost_to_matching": len(raw[hi]) + len(raw[lo]) - 2 * len(mat_hi),
            "drop_fraction": {a: prof[a]["drop_fraction"] for a in (hi, lo)},
            "mean_answer_mass": {a: prof[a]["mean_answer_mass"] for a in (hi, lo)},
            "differential_attrition": prof[lo]["drop_fraction"] - prof[hi]["drop_fraction"],
            "coherence_raw": c_raw,
            "coherence_matched": c_mat,
            "residual_raw": c_raw[hi] - c_raw[lo],
            "residual_matched": c_mat[hi] - c_mat[lo],
            "residual_shift": (c_mat[hi] - c_mat[lo]) - (c_raw[hi] - c_raw[lo]),
        })

        # Sensitivity: the floor is a free parameter, so report the curve.
        for f in floor_levels:
            a_pp, b_pp = matched_pair_probabilities(rows[hi], rows[lo], min_mass=f)
            ca, cb = _coherence(a_pp, seed=0), _coherence(b_pp, seed=0)
            if ca is None or cb is None:
                continue
            sweep.append({"model": model, "design_seed": seed, "floor": f,
                          "n_pairs": len(a_pp), "residual_matched": ca - cb})

    return {"cells": per_cell, "floor_sweep": sweep,
            "answer_mass_floor": ANSWER_MASS_FLOOR,
            "contrast": {"high": hi, "low": lo}}


def summarise(res: dict) -> dict:
    cells = res["cells"]
    if not cells:
        return {}
    n = len(cells)
    affected = [c for c in cells if c["pairs_lost_to_matching"] > 0]
    mean = lambda k: sum(c[k] for c in cells) / n  # noqa: E731
    return {
        "n_cells": n,
        "n_cells_with_attrition": len(affected),
        "mean_residual_raw": mean("residual_raw"),
        "mean_residual_matched": mean("residual_matched"),
        "mean_residual_shift": mean("residual_shift"),
        "max_abs_residual_shift": max(abs(c["residual_shift"]) for c in cells),
        "mean_differential_attrition": mean("differential_attrition"),
        "worst_differential_attrition": max(c["differential_attrition"] for c in cells),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results")
    ap.add_argument("--out", default="site/")
    args = ap.parse_args()

    res = analyse(Path(args.results))
    if not res["cells"]:
        print("no model has both arms of the contrast; nothing to match")
        return 1
    res["summary"] = summarise(res)
    hi, lo = res["contrast"]["high"], res["contrast"]["low"]

    print(f"answer_mass floor = {res['answer_mass_floor']}   "
          f"contrast = {hi} - {lo}\n")
    print(f"{'model':<34}{'seed':>9}{'drop'+hi:>8}{'drop'+lo:>10}"
          f"{'lost':>7}{'raw':>9}{'matched':>9}{'shift':>9}")
    print("-" * 95)
    for c in res["cells"]:
        print(f"{c['model'][:33]:<34}{c['design_seed']:>9}"
              f"{100*c['drop_fraction'][hi]:>7.1f}%{100*c['drop_fraction'][lo]:>9.1f}%"
              f"{c['pairs_lost_to_matching']:>7}"
              f"{c['residual_raw']:>+9.4f}{c['residual_matched']:>+9.4f}"
              f"{c['residual_shift']:>+9.4f}")

    s = res["summary"]
    print(f"\n{s['n_cells']} cells, {s['n_cells_with_attrition']} lost pairs to matching")
    print(f"  mean residual   raw {s['mean_residual_raw']:+.4f}"
          f"   matched {s['mean_residual_matched']:+.4f}"
          f"   shift {s['mean_residual_shift']:+.4f}")
    print(f"  largest single-cell shift  {s['max_abs_residual_shift']:.4f}")
    print(f"  worst differential attrition  "
          f"{100*s['worst_differential_attrition']:+.1f} pp")

    if res["floor_sweep"]:
        print("\nfloor sensitivity (matched residual, mean over cells)")
        print(f"{'floor':>8}{'cells':>8}{'mean pairs':>12}{'residual':>11}")
        for f in FLOOR_LEVELS:
            at = [r for r in res["floor_sweep"] if r["floor"] == f]
            if not at:
                continue
            print(f"{f:>8.1f}{len(at):>8}"
                  f"{sum(r['n_pairs'] for r in at)/len(at):>12.0f}"
                  f"{sum(r['residual_matched'] for r in at)/len(at):>+11.4f}")

    out = Path(args.out) / "attrition_control.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2, sort_keys=True) + "\n")
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
