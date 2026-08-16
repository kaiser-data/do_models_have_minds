"""Tests for the answer-mass attrition control.

The gate these tests guard is `answer_mass >= ANSWER_MASS_FLOOR`. It was written
to drop rows where the model was not answering the binary question in its first
token, and on seven of nine models it drops nothing at all. On the two that
deliberate it drops *more rows on the invented arm than on the real one*, and
that is a selection effect pointed at the headline: the surviving invented-arm
pairs are the ones the model answered reflexively, which is the subset most
likely to be coherent.

The correction is to score both arms on the pairs that survived in *both*, so
the R-vs-N- contrast is computed over one pair set rather than two. The tests
below pin the three properties that makes the correction worth trusting:

  1. intersecting is symmetric and really does return one shared key set,
  2. a matched key set produces an identical train/test split in both arms,
     so the residual cannot move because the folds differed, and
  3. attrition is counted the way the runner drops rows -- `p_option_a is None`
     and sub-floor mass are both attrition, and neither is silently ignored.

Property 2 is the load-bearing one. `cell_coherence` re-splits per call, and if
the two arms saw different folds the matched residual would carry fold noise
that the raw residual does not, which would look like the correction moving the
result when it only reshuffled it.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.attrition_control import (  # noqa: E402
    attrition_profile, matched_pair_probabilities, split_indices)


def _row(a, b, p, mass=1.0, order="AB"):
    return {"slot_a_outcome": a, "slot_b_outcome": b, "p_option_a": p,
            "answer_mass": mass, "order": order}


def _both_orders(a, b, p_ab, p_ba, mass=1.0):
    """One pair, both presentations, as the runner writes them."""
    return [_row(a, b, p_ab, mass, "AB"), _row(b, a, p_ba, mass, "BA")]


# ---------------------------------------------------------------------------
# attrition_profile
# ---------------------------------------------------------------------------

def test_clean_cell_reports_no_attrition():
    rows = _both_orders(0, 1, 0.7, 0.3)
    prof = attrition_profile(rows, min_mass=0.5)
    assert prof["n_rows"] == 2
    assert prof["n_unscored"] == 0
    assert prof["n_below_mass"] == 0
    assert prof["drop_fraction"] == pytest.approx(0.0)


def test_unscored_and_sub_floor_rows_are_both_attrition():
    """A None probability and a sub-floor mass are different failures.

    They are counted separately because they mean different things -- the first
    is a model that emitted no scoreable token, the second a model that emitted
    one but put most of its mass elsewhere -- and pooled because both remove a
    row from the fit.
    """
    rows = [_row(0, 1, None, 1.0), _row(1, 0, 0.4, 0.1), _row(2, 3, 0.6, 1.0)]
    prof = attrition_profile(rows, min_mass=0.5)
    assert prof["n_unscored"] == 1
    assert prof["n_below_mass"] == 1
    assert prof["drop_fraction"] == pytest.approx(2 / 3)


def test_mean_answer_mass_is_over_all_rows_not_survivors():
    """Averaging over survivors only would hide the attrition it measures."""
    rows = [_row(0, 1, 0.5, 1.0), _row(1, 0, 0.5, 0.0)]
    assert attrition_profile(rows, min_mass=0.5)["mean_answer_mass"] == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# matched_pair_probabilities
# ---------------------------------------------------------------------------

def test_matching_keeps_only_pairs_present_in_both_arms():
    a = _both_orders(0, 1, 0.8, 0.2) + _both_orders(0, 2, 0.6, 0.4)
    b = _both_orders(0, 1, 0.5, 0.5)          # pair (0,2) missing here
    pa, pb = matched_pair_probabilities(a, b, min_mass=0.5)
    assert set(pa) == set(pb) == {(0, 1)}


def test_matching_is_symmetric_in_its_arms():
    a = _both_orders(0, 1, 0.8, 0.2) + _both_orders(0, 2, 0.6, 0.4)
    b = _both_orders(0, 1, 0.5, 0.5) + _both_orders(1, 2, 0.5, 0.5)
    pa, pb = matched_pair_probabilities(a, b, min_mass=0.5)
    qb, qa = matched_pair_probabilities(b, a, min_mass=0.5)
    assert set(pa) == set(qa) and set(pb) == set(qb)


def test_a_pair_dropped_by_mass_in_one_arm_is_dropped_from_both():
    """This is the whole point of the control.

    The pair survives in the real arm and is gated out of the invented one. If
    it stayed in the real arm's fit, the two coherence numbers would come from
    different pair sets and their difference would confound content with which
    rows the gate happened to keep.
    """
    a = _both_orders(0, 1, 0.9, 0.1) + _both_orders(0, 2, 0.9, 0.1)
    b = _both_orders(0, 1, 0.9, 0.1) + _both_orders(0, 2, 0.9, 0.1, mass=0.2)
    pa, pb = matched_pair_probabilities(a, b, min_mass=0.5)
    assert set(pa) == set(pb) == {(0, 1)}


def test_matched_arms_are_still_counterbalanced():
    """Matching must not resurrect a single-order pair."""
    a = _both_orders(0, 1, 0.8, 0.2) + [_row(0, 2, 0.9, 1.0, "AB")]
    b = _both_orders(0, 1, 0.5, 0.5) + [_row(0, 2, 0.9, 1.0, "AB")]
    pa, pb = matched_pair_probabilities(a, b, min_mass=0.5)
    assert set(pa) == set(pb) == {(0, 1)}


def test_matching_preserves_each_arms_own_probabilities():
    """Shared keys, independent values -- the control equalises the pair set,
    not the preferences measured over it."""
    a = _both_orders(0, 1, 0.9, 0.1)
    b = _both_orders(0, 1, 0.2, 0.8)
    pa, pb = matched_pair_probabilities(a, b, min_mass=0.5)
    assert pa[(0, 1)] == pytest.approx(0.9)
    assert pb[(0, 1)] == pytest.approx(0.2)


# ---------------------------------------------------------------------------
# split_indices -- the fold-alignment guarantee
# ---------------------------------------------------------------------------

def test_identical_key_sets_produce_identical_folds():
    keys = {(i, j): 0.5 for i in range(8) for j in range(i + 1, 8)}
    assert split_indices(keys, seed=0) == split_indices(dict(keys), seed=0)


def test_fold_depends_on_the_key_set_not_the_probabilities():
    """Two arms differ in what the model chose, never in which pairs exist.

    So the fold must be a function of the keys alone; if the probabilities
    reached the split, the matched residual would inherit a fold difference
    driven by the very preferences under test.
    """
    keys_a = {(i, j): 0.9 for i in range(8) for j in range(i + 1, 8)}
    keys_b = {(i, j): 0.1 for i in range(8) for j in range(i + 1, 8)}
    assert split_indices(keys_a, seed=0) == split_indices(keys_b, seed=0)


def test_different_key_sets_generally_produce_different_folds():
    a = {(i, j): 0.5 for i in range(8) for j in range(i + 1, 8)}
    b = {(i, j): 0.5 for i in range(9) for j in range(i + 1, 9)}
    assert split_indices(a, seed=0) != split_indices(b, seed=0)
