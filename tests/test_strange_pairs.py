"""Tests for the strange-pair selector.

This script decides which items a big-model run spends its calls on, so an error
here does not produce a wrong number -- it produces a run pointed at the wrong
pairs, which looks exactly like a successful run. The measures are cheap to get
subtly wrong in ways no output would reveal:

  * `positional` inverted would rank the CONTENT-driven pairs as strange and
    send the probe to the least informative items in the battery.
  * `mean_preference` must average over presentation order. Reading p_option_a
    from both orders without flipping one of them measures slot A, not the
    outcome, and the two agree exactly when the model is position-driven --
    i.e. it fails silently on precisely the pairs that matter.

So these fix the arithmetic against hand-computed cases rather than against the
script's own output.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.strange_pairs import score_pairs  # noqa: E402


def _rows(pairs):
    """pairs: {model: (p_ab, p_ba, mass)} -> rows for pair_index 0."""
    cells = {}
    for model, (p_ab, p_ba, mass) in pairs.items():
        cells[model] = [
            {"pair_index": 0, "order": "AB", "p_option_a": p_ab,
             "answer_mass": mass, "slot_a_outcome": 7, "slot_b_outcome": 9},
            {"pair_index": 0, "order": "BA", "p_option_a": p_ba,
             "answer_mass": mass, "slot_a_outcome": 9, "slot_b_outcome": 7},
        ]
    return cells


def test_content_driven_pair_scores_near_zero_positional():
    # The model picks the SAME OUTCOME in both orders: p(slot A) is 0.9 when
    # the outcome is in slot A and 0.1 when it moved to slot B. Sums to 1.0.
    s = score_pairs(_rows({"m1": (0.9, 0.1, 0.99), "m2": (0.8, 0.2, 0.99)}))[0]
    assert s["positional"] < 0.01


def test_position_driven_pair_scores_high_positional():
    # The model picks slot A both times, whatever is in it. Sums to 1.8.
    s = score_pairs(_rows({"m1": (0.9, 0.9, 0.99), "m2": (0.9, 0.9, 0.99)}))[0]
    assert s["positional"] > 0.75


def test_mean_preference_averages_over_order_not_slot():
    # Consistent preference for the outcome that starts in slot A: 0.9 in AB,
    # and in BA that same outcome wins when p_option_a is 0.1. Order-averaged
    # preference is 0.9, NOT (0.9 + 0.1) / 2 = 0.5.
    s = score_pairs(_rows({"m1": (0.9, 0.1, 0.99)}))
    # one model is below the n>=2 floor, so use two identical ones
    s = score_pairs(_rows({"m1": (0.9, 0.1, 0.99), "m2": (0.9, 0.1, 0.99)}))[0]
    assert abs(s["mean_preference"] - 0.9) < 1e-6


def test_contested_is_zero_when_models_agree():
    s = score_pairs(_rows({"m1": (0.9, 0.1, 0.99), "m2": (0.9, 0.1, 0.99)}))[0]
    assert s["contested"] == 0.0


def test_contested_rises_when_models_split():
    # One model prefers each outcome, as strongly as the other.
    s = score_pairs(_rows({"m1": (0.9, 0.1, 0.99), "m2": (0.1, 0.9, 0.99)}))[0]
    assert s["contested"] > 0.35


def test_mass_collapse_is_one_minus_mean_answer_mass():
    s = score_pairs(_rows({"m1": (0.5, 0.5, 0.80), "m2": (0.5, 0.5, 0.60)}))[0]
    assert abs(s["mass_collapse"] - 0.30) < 1e-6


def test_pair_seen_by_one_model_is_dropped():
    # A pair only one model answered carries no cross-model information, and
    # its "contested" score would be 0 -- indistinguishable from unanimity.
    assert score_pairs(_rows({"m1": (0.9, 0.1, 0.99)})) == {}


def test_unscored_rows_still_count_toward_mass_collapse():
    # p_option_a is None when the answer was not in the first token. Those rows
    # are exactly the evidence of collapse, so they must not be dropped from the
    # mass average even though they cannot contribute a preference.
    cells = _rows({"m1": (0.9, 0.1, 0.99), "m2": (0.9, 0.1, 0.99)})
    cells["m3"] = [
        {"pair_index": 0, "order": "AB", "p_option_a": None,
         "answer_mass": 0.10, "slot_a_outcome": 7, "slot_b_outcome": 9},
        {"pair_index": 0, "order": "BA", "p_option_a": None,
         "answer_mass": 0.10, "slot_a_outcome": 9, "slot_b_outcome": 7},
    ]
    s = score_pairs(cells)[0]
    assert s["n_models"] == 2, "m3 contributes no preference"
    # mean mass over all three models: (0.99*4 + 0.10*2) / 6.
    # Tolerance is 1e-4 because the score is rounded to 4 decimal places.
    assert abs(s["mass_collapse"] - (1 - (0.99 * 4 + 0.10 * 2) / 6)) < 1e-4
