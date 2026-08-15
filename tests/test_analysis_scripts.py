"""Tests for the analysis layer added after the main sweep.

These scripts produce headline numbers -- the length-matched residual, the
floor decomposition, the persona direction test -- and none of them was covered
when they were written. The dangerous ones are the *corrections*: a length
control that does not actually remove a length effect, or a baseline that
peeks at the test half, would both look fine and report a confidently wrong
number. Each is tested against synthetic data with a known answer.
"""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from nullcard.scoring.thurstonian import Comparison  # noqa: E402
from scripts.floor_decomposition import _length_rule_accuracy  # noqa: E402
from scripts.persona_validity import AMBITION, SAFETY, _z, contrast  # noqa: E402
from scripts.reasoning_effect import classify  # noqa: E402


# ---------------------------------------------------------------------------
# persona_validity.contrast -- the length correction has to actually work
# ---------------------------------------------------------------------------

AMB = sorted(AMBITION)[0]
SAF = sorted(SAFETY)[0]


def _synthetic(n=60, slope=0.0, offset=0.0, overlap=True, seed=0):
    """Half ambition, half safety, ambition shorter on average.

    `slope` injects a pure length effect (shift proportional to length) and
    `offset` a genuine category effect. The two produce the SAME raw contrast;
    only the length-corrected contrast can tell them apart -- but only when
    the groups' lengths OVERLAP. With `overlap=False` length determines
    category exactly, and no regression can separate them; that case is pinned
    below as a documented limit rather than left to be discovered later.
    """
    rng = np.random.default_rng(seed)
    half = n // 2
    cats = [AMB] * half + [SAF] * half
    if overlap:
        lengths = np.concatenate([rng.uniform(5, 25, half),
                                  rng.uniform(15, 35, half)])
    else:
        lengths = np.array([10.0] * half + [20.0] * half)
    delta = slope * lengths + np.where(np.array(cats) == AMB, offset, 0.0)
    return delta, cats, lengths


def test_pure_category_effect_survives_length_correction_but_attenuated():
    """A real category effect survives -- reduced, never erased.

    Category and length stay correlated even with overlapping ranges, so
    regressing out length also removes the shared variance, and that share
    includes part of the true category effect. The corrected contrast is
    therefore a LOWER BOUND. Pinned numerically because the paper quotes these
    corrected values and must describe them as bounds, not estimates.
    """
    d, cats, L = _synthetic(offset=0.5)
    raw, lc = contrast(d, cats), contrast(d, cats, L)
    assert raw == pytest.approx(0.5, abs=1e-6)
    assert 0.25 < lc < raw


def test_pure_length_effect_is_removed_by_the_correction():
    """The regression that matters: a shift driven only by length must vanish.

    Ambition outcomes are shorter, so a negative slope produces a positive raw
    contrast with no category effect whatsoever. If the correction did nothing,
    this test would report a value system.
    """
    d, cats, L = _synthetic(slope=-0.05)
    assert contrast(d, cats) > 0.2                     # raw sees an "effect"
    assert contrast(d, cats, L) == pytest.approx(0.0, abs=1e-6)


def test_correction_keeps_the_category_part_of_a_mixed_effect():
    """Length inflates the raw contrast; correction leaves the category part."""
    d, cats, L = _synthetic(slope=-0.05, offset=0.3)
    raw, lc = contrast(d, cats), contrast(d, cats, L)
    assert raw > 0.5                        # 0.3 category + length inflation
    assert 0.1 < lc < 0.3                   # length gone, category attenuated


def test_a_shared_length_artefact_cancels_in_the_raw_excess():
    """The excess is the estimator that matters, and it is self-correcting.

    Two arms carrying the *same* length artefact, differing only in a genuine
    category effect present in one: the raw excess recovers that effect
    exactly, because the artefact is common to both and subtracts out. This is
    why the headline statistic is a difference between arms rather than a
    per-arm contrast.
    """
    real, cats, L = _synthetic(slope=-0.05, offset=0.3)
    invented, _, _ = _synthetic(slope=-0.05, offset=0.0)
    assert contrast(real, cats) - contrast(invented, cats) == pytest.approx(0.3, abs=1e-6)


def test_the_corrected_excess_is_also_a_lower_bound():
    """And the corrected excess inherits the attenuation -- do not read it as exact.

    Correcting each arm shrinks the real effect toward zero, so the corrected
    excess understates it. When the two arms carry the same artefact the raw
    excess is the better estimator; correction earns its place only because in
    the real battery the arms do NOT share a length distribution (13.2 vs 26.6
    tokens per outcome), so nothing cancels for free.
    """
    real, cats, L = _synthetic(slope=-0.05, offset=0.3)
    invented, _, _ = _synthetic(slope=-0.05, offset=0.0)
    corrected = contrast(real, cats, L) - contrast(invented, cats, L)
    assert 0 < corrected < 0.3


def test_perfectly_collinear_length_and_category_cannot_be_separated():
    """A documented limit, not a bug.

    If every ambition outcome were shorter than every safety outcome by the
    same amount, length and category would be the same variable and the
    correction would remove a real category effect along with the length one.
    The reported statistic is an *excess* -- a difference between two arms,
    each corrected the same way -- so a shared over-correction largely
    cancels; but the per-arm corrected contrasts are lower bounds, and this
    test exists so nobody reads them as anything else.
    """
    d, cats, L = _synthetic(offset=0.5, overlap=False)
    assert contrast(d, cats) == pytest.approx(0.5, abs=1e-6)
    assert contrast(d, cats, L) == pytest.approx(0.0, abs=1e-6)


def test_contrast_refuses_a_group_too_small_to_average():
    cats = [AMB] * 3 + [SAF] * 40
    assert contrast(np.zeros(43), cats) is None


def test_contrast_ignores_nan_outcomes():
    """Outcomes the fit never saw arrive as NaN and must not poison the mean."""
    d = np.array([1.0, np.nan] * 10 + [0.0] * 20)
    cats = [AMB] * 20 + [SAF] * 20
    assert contrast(d, cats) == pytest.approx(1.0)


def test_z_is_scale_and_location_free():
    v = np.array([1.0, 2.0, 3.0, 4.0])
    a, b = _z(v), _z(v * 7.5 + 100)
    assert np.allclose(a, b)
    assert _z(v).mean() == pytest.approx(0.0)


def test_z_of_a_constant_vector_is_nan_not_a_divide_by_zero():
    assert np.all(np.isnan(_z(np.array([2.0, 2.0, 2.0]))))


# ---------------------------------------------------------------------------
# floor_decomposition -- the length baseline must not flatter itself
# ---------------------------------------------------------------------------

def _cmp(w, l, p):
    return Comparison(winner=str(w), loser=str(l), n_wins=p, n_total=1.0)


def test_length_rule_scores_perfectly_when_preference_is_purely_length():
    lengths = {0: 5, 1: 10, 2: 15}
    # shorter always preferred: 0 over 1, 0 over 2, 1 over 2
    comps = [_cmp(0, 1, 0.9), _cmp(0, 2, 0.9), _cmp(1, 2, 0.9)]
    acc, n = _length_rule_accuracy(comps, lengths, prefer_shorter=True)
    assert acc == pytest.approx(1.0) and n == 3
    acc, _ = _length_rule_accuracy(comps, lengths, prefer_shorter=False)
    assert acc == pytest.approx(0.0)


def test_length_rule_skips_equal_length_pairs_rather_than_guessing():
    """A pair the rule cannot speak to must not be scored as half-right."""
    lengths = {0: 7, 1: 7}
    acc, n = _length_rule_accuracy([_cmp(0, 1, 0.9)], lengths, prefer_shorter=True)
    assert n == 0 and np.isnan(acc)


def test_length_rule_skips_empirical_ties():
    lengths = {0: 5, 1: 10}
    _, n = _length_rule_accuracy([_cmp(0, 1, 0.5)], lengths, prefer_shorter=True)
    assert n == 0


def test_length_rule_ignores_outcomes_with_no_recorded_length():
    lengths = {0: 5}
    _, n = _length_rule_accuracy([_cmp(0, 99, 0.9)], lengths, prefer_shorter=True)
    assert n == 0


# ---------------------------------------------------------------------------
# reasoning_effect -- first-token bucketing
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("tok,expected", [
    ("A", "answer"), ("B", "answer"), (" A", "answer"),
    ("Let", "deliberation"), ("<think>", "deliberation"), ("To", "deliberation"),
    ("I", "refusal_or_hedge"), ("Neither", "refusal_or_hedge"),
    ("   ", "whitespace"), ("<h3>", "other"),
])
def test_first_token_classification(tok, expected):
    assert classify(tok) == expected


def test_answer_tokens_are_never_counted_as_non_answers():
    """The non-answer rate is the headline; miscounting A/B would invent one."""
    assert classify("A") == classify("B") == "answer"
