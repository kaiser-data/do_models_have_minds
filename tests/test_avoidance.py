"""Tests for the avoidance analysis.

The MIXED arm puts a real outcome against an invented one and asks which the
model prefers. Most of the time it picks the real one. The interesting rows are
the ones where it does not, and the question this module exists to answer is
whether those are *confusion* or *avoidance* -- whether the real outcomes that
lose to gibberish are arbitrary, or whether they are the bad ones.

Two kernels can be silently wrong here.

`prefer_real` must counterbalance correctly across a row schema where the real
outcome is sometimes in slot A and sometimes in slot B. Get that backwards and
the entire result inverts: avoidance would read as attraction.

`concordance` is the reliability check. The repo has already been burned once by
a category enrichment that turned out to be selection on noise, so an
enrichment computed at one design seed is not reportable without evidence that
independent models agree. A concordance that returns a high number for
unrelated rankings would launder exactly that failure.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.avoidance import concordance, prefer_real  # noqa: E402


def _pair(real, inv, p_real_ab, p_real_ba, mass=1.0):
    """One real-vs-invented pair in both presentation orders.

    `p_real_ab` is P(prefer real) with the real outcome in slot A; `p_real_ba`
    is P(prefer real) with it in slot B, which the runner records as
    1 - p_option_a.
    """
    return [
        {"slot_a_outcome": real, "slot_b_outcome": inv, "slot_a_arm": "R",
         "slot_b_arm": "N_minus", "p_option_a": p_real_ab, "answer_mass": mass},
        {"slot_a_outcome": inv, "slot_b_outcome": real, "slot_a_arm": "N_minus",
         "slot_b_arm": "R", "p_option_a": 1.0 - p_real_ba, "answer_mass": mass},
    ]


# ---------------------------------------------------------------------------
# prefer_real
# ---------------------------------------------------------------------------

def test_averages_the_two_presentation_orders():
    got = prefer_real(_pair(1, 500, 0.9, 0.7))
    assert got[(1, 500)] == pytest.approx(0.8)


def test_slot_order_does_not_flip_the_meaning():
    """The real outcome is in slot B for half the rows. If the arm labels were
    ignored and slot A assumed real, this case would return 0.1 not 0.9."""
    rows = [
        {"slot_a_outcome": 500, "slot_b_outcome": 1, "slot_a_arm": "N_minus",
         "slot_b_arm": "R", "p_option_a": 0.1, "answer_mass": 1.0},
        {"slot_a_outcome": 1, "slot_b_outcome": 500, "slot_a_arm": "R",
         "slot_b_arm": "N_minus", "p_option_a": 0.9, "answer_mass": 1.0},
    ]
    assert prefer_real(rows)[(1, 500)] == pytest.approx(0.9)


def test_a_pair_seen_in_one_order_only_is_dropped():
    rows = _pair(1, 500, 0.9, 0.7)[:1]
    assert prefer_real(rows) == {}


def test_sub_floor_mass_rows_are_dropped():
    assert prefer_real(_pair(1, 500, 0.9, 0.7, mass=0.1), min_mass=0.5) == {}


def test_rows_that_are_not_real_versus_invented_are_ignored():
    """MIXED files should hold only cross-arm pairs, but a same-arm row would
    silently become a data point with no real outcome in it."""
    rows = [
        {"slot_a_outcome": 1, "slot_b_outcome": 2, "slot_a_arm": "R",
         "slot_b_arm": "R", "p_option_a": 0.9, "answer_mass": 1.0},
        {"slot_a_outcome": 2, "slot_b_outcome": 1, "slot_a_arm": "R",
         "slot_b_arm": "R", "p_option_a": 0.1, "answer_mass": 1.0},
    ]
    assert prefer_real(rows) == {}


# ---------------------------------------------------------------------------
# concordance -- the reliability check
# ---------------------------------------------------------------------------

def test_identical_rankings_are_fully_concordant():
    r = {"a": 1.0, "b": 2.0, "c": 3.0}
    assert concordance([r, dict(r)]) == pytest.approx(1.0)


def test_reversed_rankings_are_fully_discordant():
    assert concordance([{"a": 1.0, "b": 2.0, "c": 3.0},
                        {"a": 3.0, "b": 2.0, "c": 1.0}]) == pytest.approx(-1.0)


def test_unrelated_rankings_do_not_score_high():
    """The failure this check exists to prevent.

    A statistic that returned ~0.7 for unrelated rankings -- the way an
    unadjusted Rand index does for partitions -- would report noise as
    cross-model agreement.
    """
    a = {k: v for k, v in zip("abcdefgh", range(8))}
    b = {k: v for k, v in zip("abcdefgh", [3, 7, 0, 5, 1, 6, 2, 4])}
    assert abs(concordance([a, b])) < 0.6


def test_only_keys_present_in_both_rankings_are_compared():
    """Models need not cover the same categories; the overlap is the comparison."""
    a = {"a": 1.0, "b": 2.0, "c": 3.0, "only_in_a": 9.0}
    b = {"a": 1.0, "b": 2.0, "c": 3.0, "only_in_b": 9.0}
    assert concordance([a, b]) == pytest.approx(1.0)


def test_an_overlap_too_small_to_rank_is_not_scored():
    """Spearman on two points is +/-1 by construction and means nothing."""
    assert concordance([{"a": 1.0, "b": 2.0, "c": 3.0},
                        {"a": 1.0, "b": 2.0, "zzz": 9.0}]) is None


def test_fewer_than_two_rankings_is_not_a_concordance():
    assert concordance([{"a": 1.0}]) is None


def test_rankings_with_no_shared_keys_return_none():
    assert concordance([{"a": 1.0, "b": 2.0}, {"c": 1.0, "d": 2.0}]) is None
