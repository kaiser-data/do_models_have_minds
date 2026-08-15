"""What does Utility Engineering's coherence metric read on a model with no values?

Costs $0 and runs in under a minute. This is the null-pair self-check (spec §4,
requirement 2) applied to the metric itself rather than to a detector: before
quoting any coherence number, establish what the same procedure returns on
inputs known to carry no preference.

Responders, none of which has a value system:

    coin flip            no structure at all
    position bias        picks the option in slot A with probability p
    magnitude only       orders by a number in the text, no semantics

and one that does:

    latent utility       a real per-outcome utility, sampled once

Both in-sample and held-out accuracy are reported. In-sample is what a fit
scores on the comparisons it was trained on; held-out splits the pair set.
The gap between them is how much of a coherence number is memorised sampling
noise rather than recovered structure.

    python3 scripts/floor_simulation.py
"""

from __future__ import annotations

import itertools
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from nullcard.scoring.stats import wilson_interval  # noqa: E402
from nullcard.scoring.thurstonian import (  # noqa: E402
    Comparison,
    fit_thurstonian,
    utility_model_accuracy,
)


def build_comparisons(responder, outcomes, k, rng):
    """Ask every pair k times, counterbalancing order as UE does (§3.2)."""
    comps = []
    for a, b in itertools.combinations(outcomes, 2):
        wins = 0
        for _ in range(k // 2):
            wins += responder(a, b, rng)          # a in slot A
            wins += 1 - responder(b, a, rng)      # a in slot B
        comps.append(Comparison(a, b, n_wins=wins, n_total=k))
    return comps


def make_responders(outcomes, rng):
    latent = {o: rng.normal() for o in outcomes}
    magnitude = {o: float(i) for i, o in enumerate(outcomes)}

    def coin_flip(first, second, r):
        return int(r.random() < 0.5)

    def position_bias(p):
        def f(first, second, r):
            return int(r.random() < p)
        return f

    def by_latent(first, second, r):
        d = latent[first] - latent[second]
        return int(r.random() < 1 / (1 + np.exp(-d)))

    def by_magnitude(first, second, r):
        d = (magnitude[first] - magnitude[second]) / len(outcomes) * 6
        return int(r.random() < 1 / (1 + np.exp(-d)))

    return {
        "coin flip (no structure)": coin_flip,
        "position bias p=0.8": position_bias(0.8),
        "magnitude only (no semantics)": by_magnitude,
        "latent utility (genuine)": by_latent,
    }


def evaluate(responder, outcomes, k, seed):
    rng = np.random.default_rng(seed)
    comps = build_comparisons(responder, outcomes, k, rng)

    # held-out split over PAIRS, so the fit never sees the pairs it is scored on
    idx = rng.permutation(len(comps))
    cut = int(0.8 * len(comps))
    train = [comps[i] for i in idx[:cut]]
    test = [comps[i] for i in idx[cut:]]

    fit_all = fit_thurstonian(comps, seed=seed)
    fit_tr = fit_thurstonian(train, seed=seed)

    def safe(fn):
        try:
            return fn()
        except ValueError:
            return float("nan")

    return (
        safe(lambda: utility_model_accuracy(fit_all, comps)),
        safe(lambda: utility_model_accuracy(fit_tr, test)),
    )


def main() -> None:
    n_outcomes = 40
    outcomes = [f"o{i:03d}" for i in range(n_outcomes)]
    seeds = [0, 1, 2, 3, 4]

    banner = (
        "=" * 82 + "\n"
        "  SIMULATED — NO LANGUAGE MODEL WAS QUERIED TO PRODUCE ANY NUMBER BELOW.\n"
        "  These are synthetic responders with known generating processes, run to\n"
        "  establish what the coherence metric reads when there is nothing to\n"
        "  measure. They are a property of the METRIC, not of any model, and must\n"
        "  never be quoted as a model's coherence.\n"
        + "=" * 82
    )
    print(banner)
    print(f"\nn_outcomes={n_outcomes}  pairs={n_outcomes*(n_outcomes-1)//2}  "
          f"seeds={len(seeds)}   (UE uses K=10 at temperature 1.0, their App. E.1)\n")
    print(f"{'SIMULATED responder':<32} {'K':>3}  {'in-sample':>20}  {'held-out':>20}")
    print("-" * 82)

    for k in (10, 30):
        responders = make_responders(outcomes, np.random.default_rng(99))
        for name, r in responders.items():
            ins, held = zip(*(evaluate(r, outcomes, k, s) for s in seeds))
            ins, held = np.array(ins), np.array(held)
            print(
                f"{name:<32} {k:>3}  "
                f"{np.nanmean(ins):>8.3f} +/-{np.nanmax(ins)-np.nanmin(ins):>7.3f}  "
                f"{np.nanmean(held):>8.3f} +/-{np.nanmax(held)-np.nanmin(held):>7.3f}"
            )
        print()

    lo, hi = wilson_interval(int(0.61 * 780), 780)
    print(f"For scale: a 0.61 accuracy over 780 pairs is [{lo:.3f}, {hi:.3f}] (Wilson 95%).")
    print("Utility Engineering's Fig. 4 spans roughly 0.65-0.95 utility-model accuracy.")
    print("\n" + banner)


if __name__ == "__main__":
    main()
