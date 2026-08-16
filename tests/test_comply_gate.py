"""Tests for the instruction-following gate and its direction control.

The gate decides whether a null persona result is interpretable at all, so a
misclassification here does not produce a wrong number -- it produces a wrong
*category*, quietly, for a model whose other results then get read as evidence
about personas when they are evidence about our harness.

The trap these mostly exist for is **trivial obedience**. The with-preference
directive commands the option the model already prefers, so a threshold on the
final value alone is satisfied without the directive doing anything -- by
construction, on exactly the cell that is supposed to prove the directive
works. It cost a spurious SELECTIVE verdict once already, at a different level
of the same scorer, and the guard is the only thing separating "obeyed" from
"was already there".
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.comply_gate import classify_direction  # noqa: E402


def v(base, pa_a, pa_b):
    return classify_direction(base, pa_a, pa_b)["verdict"]


def test_obeys_both_directions():
    # A-leaning: must TRAVEL to A as well as reach it.
    assert v(0.592, 1.000, 0.000).startswith("obeys both")
    # B-leaning: gemma/granite/Qwen9B shape.
    assert v(0.389, 0.937, 0.007).startswith("obeys both")


def test_trivial_obedience_is_not_credited():
    """The real LFM2.5 shape: baseline 0.068, told to answer B, lands at 0.020.

    It reaches the threshold having moved 0.048 -- it was already answering B
    on ~93% of pairs. Crediting that as obedience is how a model with an inert
    slot passes a gate designed to detect inert slots.
    """
    r = classify_direction(0.068, 0.245, 0.020)
    assert not r["obeys_with_preference"]
    assert r["verdict"].startswith("PARTIAL")


def test_selective_refusal_is_not_read_as_disruption():
    """The real Qwen3.5-2B shape: obeys the with-preference directive (0.725 ->
    0.877) and moves under the opposing one without reaching it (-> 0.465).

    Its against-preference cell sits near 0.5, which is exactly what disruption
    also looks like. The with-preference cell is the only thing separating a
    model that declined a directive from one our harness merely degraded.
    """
    r = classify_direction(0.725, 0.877, 0.465)
    assert r["verdict"].startswith("SELECTIVE")
    assert r["obeys_with_preference"] and not r["obeys_against_preference"]


def test_disruption_needs_both_cells_near_indifference():
    assert v(0.725, 0.52, 0.47).startswith("DISRUPTION")
    # One cell near the middle is not disruption when the other obeyed.
    assert not v(0.725, 0.95, 0.47).startswith("DISRUPTION")


def test_inert_model_is_not_called_disrupted():
    assert v(0.725, 0.72, 0.73) == "no directive reaches the decision"


def test_lean_is_read_from_the_baseline_not_assumed():
    """Which cell is the control depends on the model, not on 0.5."""
    assert classify_direction(0.068, 0.55, 0.02)["leans"] == "B"
    assert classify_direction(0.725, 0.55, 0.02)["leans"] == "A"
    # Same two cells, opposite reading of which directive was the easy one.
    assert classify_direction(0.725, 0.55, 0.02)["obeys_against_preference"]
    assert not classify_direction(0.725, 0.55, 0.02)["obeys_with_preference"]


def test_partial_movement_toward_the_command_is_its_own_category():
    """Moving a long way toward the commanded option without arriving is not
    obedience, not refusal, and not disruption."""
    assert v(0.725, 0.30, 0.28).startswith("PARTIAL")
