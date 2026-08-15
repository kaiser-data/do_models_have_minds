"""Tests for nullcard.runner.forced_choice — pure elicitation logic.

The prompt is Utility Engineering's, verbatim (2502.08640 §3.2), so that our
numbers and theirs are produced by the same instrument and any difference
between the arms is not a difference in wording.
"""

import pytest

from nullcard.runner.forced_choice import (
    UE_PROMPT_TEMPLATE,
    answer_mass,
    build_forced_choice_prompt,
    p_option_a,
    sample_pairs,
    stratified_subsample,
)


class TestPromptTemplate:
    def test_is_the_published_wording(self):
        """Verbatim from 2502.08640 §3.2. If this string drifts, our arms stop
        being comparable to their published numbers."""
        assert "The following two options describe observations about the state" in UE_PROMPT_TEMPLATE
        assert "Which implied state of the world would you prefer?" in UE_PROMPT_TEMPLATE
        assert 'Please respond with only "A" or "B".' in UE_PROMPT_TEMPLATE

    def test_places_options_in_the_named_slots(self):
        p = build_forced_choice_prompt("You receive a horse.", "You receive $10.")
        assert "Option A: You receive a horse." in p
        assert "Option B: You receive $10." in p

    def test_swapping_arguments_swaps_the_slots(self):
        """Order counterbalancing depends on this being the only thing that
        changes between the two presentations of a pair."""
        a = build_forced_choice_prompt("X", "Y")
        b = build_forced_choice_prompt("Y", "X")
        assert a != b
        assert a.replace("Option A: X", "@@").replace("Option B: Y", "##") == \
               b.replace("Option A: Y", "@@").replace("Option B: X", "##")


class TestAnswerMass:
    """The first-token validity gate (spec §7.4).

    Measured, never assumed: 6 of 10 hosted models we probed begin with a
    reasoning preamble ("We", "The", "Here") rather than an answer token, and
    scoring those by first-token logprob would read noise as preference.
    """

    def test_clean_answerer_has_almost_all_mass_on_a_and_b(self):
        top = {"A": -0.05, "B": -3.0, "The": -12.0}
        assert answer_mass(top) > 0.95

    def test_reasoning_preamble_has_almost_no_answer_mass(self):
        top = {"We": -0.01, "The": -5.0, "A": -14.0, "B": -15.0}
        assert answer_mass(top) < 0.05

    def test_counts_whitespace_prefixed_variants(self):
        """' A' and 'A' are the same answer; tokenisers differ on the leading
        space and dropping one would fail a model for a tokenisation detail."""
        assert answer_mass({" A": -0.05, " B": -3.0}) > 0.95

    def test_empty_distribution_raises(self):
        with pytest.raises(ValueError):
            answer_mass({})


class TestPOptionA:
    def test_renormalises_over_the_two_answers_only(self):
        """Mass on other tokens is excluded rather than counted against A, so
        the estimator is P(A | answered A or B)."""
        assert p_option_a({"A": -0.0, "B": -100.0, "junk": -0.001}) == pytest.approx(1.0, abs=1e-6)

    def test_equal_logprobs_give_one_half(self):
        assert p_option_a({"A": -1.0, "B": -1.0}) == pytest.approx(0.5)

    def test_missing_an_answer_token_raises(self):
        """A model that put no mass on 'B' at all has not been asked a binary
        question in a way we can score."""
        with pytest.raises(ValueError):
            p_option_a({"A": -0.1, "The": -2.0})


class TestSamplePairs:
    def test_is_deterministic(self):
        outcomes = [f"o{i}" for i in range(30)]
        assert sample_pairs(outcomes, 50, seed=1) == sample_pairs(outcomes, 50, seed=1)

    def test_returns_the_requested_number(self):
        outcomes = [f"o{i}" for i in range(30)]
        assert len(sample_pairs(outcomes, 50, seed=1)) == 50

    def test_never_pairs_an_outcome_with_itself(self):
        outcomes = [f"o{i}" for i in range(10)]
        assert all(a != b for a, b in sample_pairs(outcomes, 40, seed=2))

    def test_contains_no_duplicate_unordered_pairs(self):
        outcomes = [f"o{i}" for i in range(12)]
        pairs = sample_pairs(outcomes, 60, seed=3)
        assert len({frozenset(p) for p in pairs}) == len(pairs)

    def test_degree_is_balanced_across_outcomes(self):
        """Every outcome needs comparable support or its fitted utility is far
        noisier than its neighbours', and the Thurstonian fit inherits that
        imbalance as spurious structure."""
        outcomes = [f"o{i}" for i in range(20)]
        pairs = sample_pairs(outcomes, 100, seed=4)
        counts = {o: 0 for o in outcomes}
        for a, b in pairs:
            counts[a] += 1
            counts[b] += 1
        assert max(counts.values()) - min(counts.values()) <= 2

    def test_requesting_more_pairs_than_exist_raises(self):
        with pytest.raises(ValueError):
            sample_pairs(["a", "b", "c"], 10, seed=1)   # only 3 unordered pairs


class TestStratifiedSubsample:
    def test_is_deterministic(self):
        items = [f"i{n}" for n in range(40)]
        cats = ["x"] * 20 + ["y"] * 20
        assert stratified_subsample(items, cats, 10, seed=1) == \
               stratified_subsample(items, cats, 10, seed=1)

    def test_returns_the_requested_size(self):
        items = [f"i{n}" for n in range(40)]
        cats = ["x"] * 20 + ["y"] * 20
        assert len(stratified_subsample(items, cats, 10, seed=1)) == 10

    def test_preserves_category_proportions(self):
        items = [f"i{n}" for n in range(40)]
        cats = ["x"] * 30 + ["y"] * 10          # 75/25
        picked = stratified_subsample(items, cats, 20, seed=1)
        idx = {it: c for it, c in zip(items, cats)}
        n_x = sum(1 for p in picked if idx[p] == "x")
        assert 13 <= n_x <= 17                   # ~15 of 20

    def test_returns_indices_into_the_original_order(self):
        """The three arms share an index space — outcome i is the same outcome
        in R, N+ and N-. Subsampling must return positions, not strings, or the
        arms silently desynchronise."""
        items = [f"i{n}" for n in range(10)]
        cats = ["x"] * 10
        picked = stratified_subsample(items, cats, 4, seed=1, return_indices=True)
        assert all(isinstance(p, int) for p in picked)
        assert all(0 <= p < 10 for p in picked)
