"""Tests for the instruction-following gate and its direction control.

The gate decides whether a null persona result is interpretable at all, so a
misclassification here does not produce a wrong number -- it produces a wrong
*category*, quietly, for a model whose other results then get read as evidence
about personas when they are evidence about our harness.

The three readings it must keep apart, all of which look identical if you only
look at displacement:

    SELECTIVE   obeys a directive agreeing with its lean, refuses the opposing
                one -- it follows instructions and declined that one
    DISRUPTION  lands at indifference under both -- our own harness degrades
                the preference and installs nothing
    INERT       neither directive moves it -- the slot never reaches the decision
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.comply_gate import classify_direction  # noqa: E402


def v(base, pa_a, pa_b):
    return classify_direction(base, pa_a, pa_b)["verdict"]


def test_obeys_both_directions():
    assert v(0.725, 0.95, 0.02).startswith("obeys both")
    assert v(0.068, 0.93, 0.02).startswith("obeys both")


def test_selective_refusal_is_not_read_as_disruption():
    """The Qwen3.5-2B shape: obeys the with-preference directive, refuses the
    other. Its P(A) under the refused directive sits near 0.5, which is exactly
    what disruption also looks like -- the with-preference cell is the only
    thing separating them."""
    r = classify_direction(0.725, 0.95, 0.465)
    assert r["verdict"].startswith("SELECTIVE")
    assert r["obeys_with_preference"] and not r["obeys_against_preference"]


def test_disruption_needs_both_cells_near_indifference():
    assert v(0.725, 0.52, 0.47).startswith("DISRUPTION")
    # One cell near the middle is not disruption if the other obeyed.
    assert not v(0.725, 0.95, 0.47).startswith("DISRUPTION")


def test_inert_model_is_not_called_disrupted():
    assert v(0.725, 0.72, 0.73) == "no directive reaches the decision"


def test_lean_is_read_from_the_baseline_not_assumed():
    """A B-leaning model's with-preference directive is 'answer B'. Assuming
    0.5 or assuming A-lean flips which cell is the control."""
    assert classify_direction(0.068, 0.55, 0.02)["leans"] == "B"
    assert classify_direction(0.725, 0.55, 0.02)["leans"] == "A"
    # Same two cells, opposite reading, purely because of the baseline.
    assert classify_direction(0.068, 0.55, 0.02)["obeys_with_preference"]
    assert not classify_direction(0.725, 0.55, 0.02)["obeys_with_preference"]


def test_moving_without_obeying_is_its_own_category():
    """Not every failure is disruption: a model can move a long way and land
    somewhere that is neither obedience nor indifference."""
    assert v(0.725, 0.30, 0.28) == "moves without obeying either"
