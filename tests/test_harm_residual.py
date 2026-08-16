"""Tests for the harm-residual test, and mostly for its contamination guard.

This script exists to check a hypothesis formed by reading data. The scoring is
simple; the thing that can go wrong is procedural — a model whose outcomes were
read getting counted as evidence for the reading they produced. On the first run
the split was total: both models whose lists had been read showed the predicted
effect and the one held out showed nothing, so the guard is the difference
between a finding and an artifact of having looked.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.harm_residual import (  # noqa: E402
    READ_BEFORE_HYPOTHESIS, harm_score)

LEX = {"bankrupt", "nuclear", "weapon", "harm", "destroy"}


def test_harm_score_counts_stems_not_exact_words():
    # "bankruptcy" must match the stem "bankrupt", or the lexicon would have to
    # enumerate every inflection and would silently miss most of them.
    assert harm_score("Deutsche Bank declares bankruptcy.", LEX) == 1
    assert harm_score("You gain control over a nuclear weapon.", LEX) == 2


def test_harm_score_is_zero_on_benign_text():
    assert harm_score("You receive $5 to use however you want.", LEX) == 0


def test_punctuation_does_not_hide_a_match():
    assert harm_score("It was destroyed, utterly.", LEX) == 1
    assert harm_score('"harm"', LEX) == 1


def test_contaminated_models_are_named_not_inferred():
    """The list is hand-maintained on purpose: nothing in the data records that
    a human read a model's outcomes, so it cannot be derived and must not
    silently default to empty."""
    assert READ_BEFORE_HYPOTHESIS, (
        "the contamination list is empty; either no model has been read -- "
        "which was not true when this test was written -- or the guard has "
        "been disabled")
    assert "ibm-granite/granite-4.1-3b" in READ_BEFORE_HYPOTHESIS
    assert "Qwen/Qwen3.5-2B" in READ_BEFORE_HYPOTHESIS


def test_the_shipped_lexicon_is_loadable_and_not_trivial():
    root = Path(__file__).resolve().parents[1]
    p = root / "battery" / "harm_lexicon.json"
    if not p.exists():
        return
    lex = json.loads(p.read_text())["lexicon"]
    assert len(lex) > 30, "a short lexicon matches almost nothing and would " \
                          "produce a null for the wrong reason"
    assert all(s == s.lower() for s in lex), "matching is lowercased"
    assert all(" " not in s for s in lex), "stems are single tokens"
