"""Interval and noise-floor primitives.

Pure functions, zero I/O, deterministic. Spec §3.5, §5, §2A.3.

The rule these exist to enforce: no proportion is reported as a point estimate,
and no between-condition contrast is reported without the within-condition
spread that bounds what it is allowed to mean.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence

import numpy as np

# 95% two-sided normal quantile. Wilson's z, fixed rather than a parameter —
# a study that changes its confidence level per tile is not reporting intervals.
_Z95 = 1.959963984540054


def wilson_interval(hits: int, n: int, z: float = _Z95) -> tuple[float, float]:
    """Wilson score interval for a proportion.

    Every proportion on a card goes through this. 5/5 is [0.566, 1.000], not
    1.000 — the point estimate would claim a precision five observations cannot
    support (§5.3).
    """
    if n <= 0:
        raise ValueError(f"n must be positive, got {n}")
    if hits < 0:
        raise ValueError(f"hits must be non-negative, got {hits}")
    if hits > n:
        raise ValueError(f"hits ({hits}) cannot exceed n ({n})")

    p = hits / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = (z / denom) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, center - half), min(1.0, center + half))


def sampling_noise(replicates: Sequence[float]) -> float:
    """SD across seed / paraphrase / order at a FIXED artifact and condition.

    This is the precision of one artifact's estimate. It is *not* a training
    noise floor and on its own licenses no between-cell claim (§5).
    """
    if len(replicates) < 2:
        raise ValueError(
            f"sampling_noise needs >=2 replicates to have a spread, got {len(replicates)}"
        )
    return float(np.std(np.asarray(replicates, dtype=float), ddof=1))


def training_noise_floor(anchor_replicates: Sequence[float]) -> float:
    """Spread across independently-trained replicates of the anchor cell.

    Returned as the **range**, not the SD: §5.1 defines this as "the smallest
    effect the paper is allowed to claim", and a range is the conservative
    reading of that at n=3-5. Reference calibration — five anchor replicates
    differing only in seed spanned 38.30%-52.44%, a floor of 0.141, and three
    of them cleared a 50% gate while two failed it.

    Raises below three replicates. §5.1 makes >=3 a gate, and a function that
    quietly returned a two-point range would let a paper cite a floor it does
    not have.
    """
    n = len(anchor_replicates)
    if n < 3:
        raise ValueError(
            f"training_noise_floor requires >=3 independently-trained replicates "
            f"(spec §5.1), got {n}"
        )
    arr = np.asarray(anchor_replicates, dtype=float)
    return float(arr.max() - arr.min())


def drift_delta(turn_1: Sequence[float], turn_n: Sequence[float]) -> float:
    """Δ on an axis between turn 1 and turn N of a sustained conversation.

    The replicate unit is the **conversation** (§2.5): each element of `turn_1`
    is paired with the same index in `turn_n`. Measuring drift across
    independent samples instead would compute a between-conversation difference
    and label it drift.
    """
    if len(turn_1) != len(turn_n):
        raise ValueError(
            f"turn_1 and turn_n must be paired per conversation, "
            f"got {len(turn_1)} and {len(turn_n)}"
        )
    if not turn_1:
        raise ValueError("no conversations supplied")
    a = np.asarray(turn_1, dtype=float)
    b = np.asarray(turn_n, dtype=float)
    return float(np.mean(b - a))


def auditor_spread(framings: Mapping[str, float]) -> float:
    """Spread of a position across inferred-auditor framings (§2.6).

    Required beside any political value. 2604.27633 shows political bias audits
    largely capture sycophancy toward the auditor the model infers from the
    prompt; the spread is how much of the reading belongs to our framing.
    """
    if len(framings) < 2:
        raise ValueError(
            f"auditor_spread needs >=2 framings to be a spread, got {len(framings)}"
        )
    vals = np.asarray(list(framings.values()), dtype=float)
    return float(vals.max() - vals.min())


def _normalise(dist: Sequence[float]) -> np.ndarray:
    arr = np.asarray(dist, dtype=float)
    if np.any(arr < 0):
        raise ValueError("distributions must be non-negative")
    total = arr.sum()
    if total <= 0:
        raise ValueError("distribution sums to zero")
    return arr / total


def js_distance(model_dist: Sequence[float], human_dist: Sequence[float]) -> float:
    """Jensen-Shannon *distance* (base 2) between two answer distributions.

    The GlobalOpinionQA import (2306.16388, §2.4): don't score the model against
    a right answer that does not exist — score the distance between its answer
    distribution and a real human one. Bounded in [0, 1]; 0 identical, 1 disjoint.
    """
    if len(model_dist) != len(human_dist):
        raise ValueError(
            f"distributions must share support, got {len(model_dist)} and {len(human_dist)}"
        )
    p = _normalise(model_dist)
    q = _normalise(human_dist)
    m = 0.5 * (p + q)

    def _entropy(x: np.ndarray) -> float:
        nz = x[x > 0]
        return float(-np.sum(nz * np.log2(nz)))

    divergence = _entropy(m) - 0.5 * (_entropy(p) + _entropy(q))
    # Clamp: floating point can nudge a mathematically-zero divergence negative.
    return float(math.sqrt(max(0.0, divergence)))


def bootstrap_region(
    replicates: Sequence[tuple[float, float]],
    level: float = 0.95,
    seed: int = 0,
    n_boot: int = 10_000,
) -> dict:
    """Nonparametric percentile region for the 2D depth figure (§2A.3).

    Deliberately *not* a Gaussian covariance ellipse. At n=3-5 replicates we
    have no reason to expect bivariate normality, and a smooth ellipse drawn
    through four points implies precision the data does not contain. The raw
    replicates come back with the region so they can be plotted on top of it.

    `seed` is required for determinism — this layer is pure, and a region that
    moved between runs would make the figure unreproducible.
    """
    n = len(replicates)
    if n < 3:
        raise ValueError(
            f"bootstrap_region needs >=3 replicates, got {n}"
        )
    if not 0.0 < level < 1.0:
        raise ValueError(f"level must be in (0, 1), got {level}")

    pts = np.asarray(replicates, dtype=float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(n_boot, n))
    boot_means = pts[idx].mean(axis=1)          # (n_boot, 2)

    lo_pct = 100 * (1 - level) / 2
    hi_pct = 100 * (1 + level) / 2
    x_lo, x_hi = np.percentile(boot_means[:, 0], [lo_pct, hi_pct])
    y_lo, y_hi = np.percentile(boot_means[:, 1], [lo_pct, hi_pct])

    return {
        "x_interval": (float(x_lo), float(x_hi)),
        "y_interval": (float(y_lo), float(y_hi)),
        "replicates": list(replicates),
        "n_replicates": n,
        "level": level,
        # §2A.3: the caption must state what the region is. Ship the label with
        # the numbers so the plotting code cannot invent a different one.
        "region_kind": f"bootstrap percentile interval of the mean ({n_boot} resamples)",
    }
