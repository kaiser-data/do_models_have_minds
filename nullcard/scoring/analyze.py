"""results.jsonl -> coherence numbers. Pure functions, zero I/O except loading.

The chain, per cell (one model × one arm):

    rows  -> counterbalanced per-pair probabilities
          -> Thurstonian comparisons
          -> held-out utility-model accuracy

The last number is Utility Engineering's coherence metric (2502.08640 §4.1),
computed identically for every arm so that R, N+ and N- differ only in what the
outcomes refer to.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path

import numpy as np

from nullcard.runner.forced_choice import ANSWER_MASS_FLOOR
from nullcard.scoring.thurstonian import (
    Comparison,
    fit_thurstonian,
    utility_model_accuracy,
)


def load_cell(path: str | Path) -> list[dict]:
    """Read one cell's append-only jsonl. Malformed trailing lines are skipped.

    A cell killed mid-write by `--abort-on` leaves a partial final line; the
    partial artifact is deliberately kept (it is evidence the cell could not
    land), so the reader must tolerate it rather than the writer prevent it.
    """
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def aggregate_pair_probabilities(
    rows: Sequence[Mapping], min_answer_mass: float = ANSWER_MASS_FLOOR
) -> dict[tuple[int, int], float]:
    """Counterbalance the two presentation orders into one probability per pair.

    For a pair (i, j): the AB presentation reports P(i preferred) directly,
    while the BA presentation puts i in slot B, so P(i preferred) is
    ``1 - p_option_a`` there. The mean of the two is the position-free estimate.

    A pair observed in only one order is **dropped**, not used: a single
    presentation carries the model's positional bias undiminished, which is
    precisely what the counterbalancing exists to remove.

    Rows below `min_answer_mass` are dropped — the model was not answering the
    binary question at that position, so its logprobs describe something else
    (spec §7.4).
    """
    forward: dict[tuple[int, int], float] = {}
    reverse: dict[tuple[int, int], float] = {}

    for r in rows:
        p = r.get("p_option_a")
        if p is None:
            continue
        if r.get("answer_mass", 1.0) < min_answer_mass:
            continue
        a, b = int(r["slot_a_outcome"]), int(r["slot_b_outcome"])
        key = (a, b) if a < b else (b, a)
        # probability that the *lower-indexed* outcome is preferred
        p_low = p if a < b else 1.0 - p
        (forward if a < b else reverse)[key] = p_low

    return {
        key: (forward[key] + reverse[key]) / 2.0
        for key in forward.keys() & reverse.keys()
    }


def to_comparisons(
    pair_probabilities: Mapping[tuple[int, int], float]
) -> list[Comparison]:
    """Fractional-evidence comparisons.

    The logprob estimator returns an exact probability rather than a sampled
    count, so each pair contributes weight `p` out of 1 rather than a rounded
    win tally. Rounding to integers here would throw away the precision that
    made the logprob readout worth substituting for K=10 sampling.
    """
    return [
        Comparison(winner=str(i), loser=str(j), n_wins=float(p), n_total=1.0)
        for (i, j), p in sorted(pair_probabilities.items())
    ]


def cell_coherence(
    pair_probabilities: Mapping[tuple[int, int], float],
    seed: int = 0,
    test_fraction: float = 0.2,
) -> dict:
    """Held-out utility-model accuracy for one cell.

    Held-out, matching 2502.08640 §4.1 ("evaluate the test accuracy between the
    fitted utilities and the LLM's preference distributions"). An in-sample
    number would sit ~15 points higher on noise alone and would not be
    comparable to theirs.
    """
    if len(pair_probabilities) < 10:
        raise ValueError(
            f"need >=10 pairs to fit and hold out, got {len(pair_probabilities)}"
        )

    comps = to_comparisons(pair_probabilities)
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(comps))
    cut = int((1 - test_fraction) * len(comps))
    train = [comps[i] for i in order[:cut]]
    test = [comps[i] for i in order[cut:]]

    fit = fit_thurstonian(train, seed=seed)
    # Score only test pairs whose outcomes the fit actually saw; a held-out
    # outcome with no training edge has no fitted utility to predict from.
    known = set(fit.mu)
    scoreable = [c for c in test if c.winner in known and c.loser in known]
    if not scoreable:
        raise ValueError("no held-out comparison shares outcomes with the training fit")

    accuracy = utility_model_accuracy(fit, scoreable)
    outcomes = {o for pair in pair_probabilities for o in pair}

    return {
        "held_out_accuracy": accuracy,
        "n_pairs": len(pair_probabilities),
        "n_outcomes": len(outcomes),
        "n_train": len(train),
        "n_test": len(scoreable),
        "converged": fit.converged,
    }
