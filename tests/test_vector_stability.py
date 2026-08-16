"""Tests for the rewording-stability statistics.

The claim these support is that a preference vector *rotates* when only the
question changes. That claim is only meaningful against a denominator, and the
denominator is the measurement's agreement with itself. Three things can be
silently wrong.

`spearman_brown` corrects a half-length reliability up to full length. Omit it
and the ceiling is too low, every cross-prompt correlation looks closer to its
ceiling than it is, and the rotation disappears -- an error that flatters the
null hypothesis, which is the direction to guard hardest.

The attenuation correction divides by that ceiling. If it divided by the wrong
quantity, or failed to cap at 1.0, a noisy cell would report a corrected
correlation above one and read as *more* than perfect agreement.

`arm_difference` is the test that decides whether meaning anchors the ordering.
It must bootstrap the two arms **paired on outcomes** -- both arms are measured
over the same slots, and an unpaired resample would throw that away and widen
the interval until nothing is ever distinguishable.
"""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.vector_stability import (  # noqa: E402
    _boot_corrected, arm_difference, spearman_brown)


# ---------------------------------------------------------------------------
# spearman_brown
# ---------------------------------------------------------------------------

def test_perfect_half_stays_perfect():
    assert spearman_brown(1.0) == pytest.approx(1.0)


def test_correction_raises_a_partial_correlation():
    """A half-length r of 0.5 is a full-length reliability of 0.667."""
    assert spearman_brown(0.5) == pytest.approx(2 / 3)


def test_zero_stays_zero():
    assert spearman_brown(0.0) == pytest.approx(0.0)


def test_correction_never_returns_a_negative_reliability():
    """A reliability below zero is not a quantity; dividing by its root would
    produce a complex number or a silent nan in the attenuation step."""
    assert spearman_brown(-0.9) == 0.0


def test_correction_is_monotone():
    vals = [spearman_brown(r) for r in (0.1, 0.3, 0.5, 0.7, 0.9)]
    assert vals == sorted(vals)


# ---------------------------------------------------------------------------
# the attenuation correction
# ---------------------------------------------------------------------------

def test_identical_vectors_at_perfect_reliability_correct_to_one():
    v = np.arange(60, dtype=float)
    lo, hi = _boot_corrected(v, v.copy(), 1.0, 1.0, n=80)
    assert lo == pytest.approx(1.0) and hi == pytest.approx(1.0)


def test_corrected_value_is_capped_at_one():
    """Imperfect reliability inflates the ratio; without a cap a cell can
    report better-than-perfect agreement, which is not a thing."""
    v = np.arange(60, dtype=float)
    _, hi = _boot_corrected(v, v.copy(), 0.5, 0.5, n=80)
    assert hi <= 1.0


def test_unrelated_vectors_produce_an_interval_excluding_one():
    rng = np.random.default_rng(0)
    a, b = rng.normal(size=120), rng.normal(size=120)
    _, hi = _boot_corrected(a, b, 0.99, 0.99, n=300)
    assert hi < 1.0


# ---------------------------------------------------------------------------
# arm_difference
# ---------------------------------------------------------------------------

def _cells(real_pair, invented_pair, rel=0.99):
    vectors = {("M", "R"): real_pair, ("M", "N_minus"): invented_pair}
    rels = {("M", "R"): (rel, rel), ("M", "N_minus"): (rel, rel)}
    return vectors, rels


def test_reports_real_more_stable_when_it_is():
    rng = np.random.default_rng(1)
    base = rng.normal(size=150)
    stable = (base, base + rng.normal(scale=0.05, size=150))     # barely moves
    rotated = (base, rng.normal(size=150))                       # unrelated
    v, r = _cells(stable, rotated)
    out = arm_difference(v, r, "M", n=300)
    assert out["verdict"] == "real more stable"
    assert out["ci"][0] > 0


def test_reports_invented_more_stable_when_it_is():
    rng = np.random.default_rng(2)
    base = rng.normal(size=150)
    v, r = _cells((base, rng.normal(size=150)),
                  (base, base + rng.normal(scale=0.05, size=150)))
    out = arm_difference(v, r, "M", n=300)
    assert out["verdict"] == "invented more stable"
    assert out["ci"][1] < 0


def test_reports_no_difference_when_both_rotate_alike():
    """The result actually observed. A test that could not produce this
    verdict would make the finding unfalsifiable."""
    rng = np.random.default_rng(3)
    base = rng.normal(size=150)
    same = lambda: (base, base + rng.normal(scale=0.6, size=150))  # noqa: E731
    v, r = _cells(same(), same())
    out = arm_difference(v, r, "M", n=400)
    assert out["verdict"] == "no difference"
    assert out["ci"][0] < 0 < out["ci"][1]


def test_missing_an_arm_returns_none_rather_than_half_an_answer():
    vectors = {("M", "R"): (np.arange(50.0), np.arange(50.0))}
    rels = {("M", "R"): (0.9, 0.9)}
    assert arm_difference(vectors, rels, "M", n=10) is None
