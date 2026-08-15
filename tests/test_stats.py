"""Tests for nullcard.scoring.stats — the interval and noise-floor primitives.

Spec: docs/superpowers/specs/2026-08-14-nullcard-design.md §3.5, §5.
"""

import pytest

from nullcard.scoring.stats import (
    auditor_spread,
    bootstrap_region,
    drift_delta,
    js_distance,
    sampling_noise,
    training_noise_floor,
    wilson_interval,
)


class TestWilsonInterval:
    def test_five_of_five_is_not_one_hundred_percent(self):
        """§5.3's stated calibration: 5/5 is [57%, 100%], not 100%.

        This is the whole reason the function exists — a bare point estimate of
        1.0 from five observations is the failure mode the card is built against.
        """
        low, high = wilson_interval(5, 5)
        assert low == pytest.approx(0.5655, abs=5e-4)
        assert high == pytest.approx(1.0, abs=5e-4)

    def test_zero_of_five_mirrors_five_of_five(self):
        low, high = wilson_interval(0, 5)
        assert low == pytest.approx(0.0, abs=5e-4)
        assert high == pytest.approx(0.4345, abs=5e-4)

    def test_one_of_two(self):
        low, high = wilson_interval(1, 2)
        assert low == pytest.approx(0.0945, abs=5e-4)
        assert high == pytest.approx(0.9055, abs=5e-4)

    def test_interval_narrows_as_n_grows(self):
        narrow = wilson_interval(50, 100)
        wide = wilson_interval(5, 10)
        assert (narrow[1] - narrow[0]) < (wide[1] - wide[0])

    def test_zero_observations_raises(self):
        """An interval over nothing is not an interval. §8 rule 2 wants
        INSUFFICIENT, not a silently degraded number."""
        with pytest.raises(ValueError):
            wilson_interval(0, 0)

    def test_more_hits_than_trials_raises(self):
        with pytest.raises(ValueError):
            wilson_interval(6, 5)

    def test_negative_hits_raises(self):
        with pytest.raises(ValueError):
            wilson_interval(-1, 5)


class TestSamplingNoise:
    """§5: sampling replicates measure the precision of ONE artifact's estimate.
    They are not a training noise floor and cannot license a between-cell claim."""

    def test_spread_of_identical_replicates_is_zero(self):
        assert sampling_noise([0.4, 0.4, 0.4, 0.4]) == pytest.approx(0.0)

    def test_uses_sample_sd_not_population_sd(self):
        # [0,1] -> sample SD (ddof=1) = 0.7071; population SD = 0.5
        assert sampling_noise([0.0, 1.0]) == pytest.approx(0.70710678, abs=1e-6)

    def test_single_replicate_raises(self):
        """One observation has no spread. Returning 0.0 would read as 'precise'."""
        with pytest.raises(ValueError):
            sampling_noise([0.4])


class TestTrainingNoiseFloor:
    """§5.1: the spread across independently-trained anchor replicates is the
    smallest effect the paper is allowed to claim."""

    def test_matches_the_documented_anchor_spread(self):
        """SKILLS.md records five replicates spanning 38.30%-52.44%, and §8's
        example tile carries training_noise_floor = 0.14. Range, not SD."""
        floor = training_noise_floor([0.3830, 0.4102, 0.4455, 0.4881, 0.5244])
        assert floor == pytest.approx(0.1414, abs=1e-4)

    def test_fewer_than_three_replicates_raises(self):
        """§5.1 makes >=3 a hard gate, not a preference. Two replicates cannot
        establish a floor and must not silently return one."""
        with pytest.raises(ValueError):
            training_noise_floor([0.40, 0.52])

    def test_three_replicates_is_the_minimum_accepted(self):
        assert training_noise_floor([0.40, 0.45, 0.52]) == pytest.approx(0.12)


class TestDriftDelta:
    """§2.5: the replicate unit is the CONVERSATION, not the turn."""

    def test_mean_of_per_conversation_deltas(self):
        # three conversations, each (turn_1, turn_N)
        result = drift_delta(turn_1=[0.50, 0.60, 0.55], turn_n=[0.40, 0.45, 0.50])
        assert result == pytest.approx(-0.1)

    def test_no_drift_is_zero(self):
        assert drift_delta(turn_1=[0.5, 0.6], turn_n=[0.5, 0.6]) == pytest.approx(0.0)

    def test_mismatched_lengths_raise(self):
        """Unpaired turns mean the conversations were not tracked. Averaging
        over that silently invents pairings."""
        with pytest.raises(ValueError):
            drift_delta(turn_1=[0.5, 0.6], turn_n=[0.4])


class TestAuditorSpread:
    """§2.6: a political position without its across-framing spread is a
    measurement of our own prompt."""

    def test_spread_is_the_range_across_framings(self):
        assert auditor_spread({"neutral": 0.50, "left": 0.72, "right": 0.31}) == pytest.approx(0.41)

    def test_identical_across_framings_is_zero(self):
        assert auditor_spread({"a": 0.5, "b": 0.5}) == pytest.approx(0.0)

    def test_single_framing_raises(self):
        """One framing is not a spread — it is the thing the spread was meant
        to qualify. §8 rule 10 suppresses the tile instead."""
        with pytest.raises(ValueError):
            auditor_spread({"neutral": 0.5})


class TestJSDistance:
    """§2.4: score the model against a human answer DISTRIBUTION, not against
    a right answer. Import from GlobalOpinionQA (2306.16388)."""

    def test_identical_distributions_are_zero(self):
        assert js_distance([0.25, 0.25, 0.5], [0.25, 0.25, 0.5]) == pytest.approx(0.0, abs=1e-9)

    def test_disjoint_distributions_are_one(self):
        assert js_distance([1.0, 0.0], [0.0, 1.0]) == pytest.approx(1.0, abs=1e-9)

    def test_is_symmetric(self):
        p, q = [0.7, 0.2, 0.1], [0.1, 0.3, 0.6]
        assert js_distance(p, q) == pytest.approx(js_distance(q, p))

    def test_bounded_in_unit_interval(self):
        assert 0.0 <= js_distance([0.6, 0.4], [0.3, 0.7]) <= 1.0

    def test_unnormalised_input_is_normalised(self):
        assert js_distance([2, 2, 4], [1, 1, 2]) == pytest.approx(0.0, abs=1e-9)

    def test_mismatched_support_raises(self):
        with pytest.raises(ValueError):
            js_distance([0.5, 0.5], [0.3, 0.3, 0.4])


class TestBootstrapRegion:
    """§2A.3: nonparametric percentile region. No Gaussian fit — we have no
    reason to expect bivariate normality at n=3-5."""

    def test_is_deterministic_given_a_seed(self):
        pts = [(0.1, 0.2), (0.15, 0.25), (0.12, 0.19), (0.2, 0.3)]
        a = bootstrap_region(pts, level=0.95, seed=7)
        b = bootstrap_region(pts, level=0.95, seed=7)
        assert a["x_interval"] == b["x_interval"]
        assert a["y_interval"] == b["y_interval"]

    def test_returns_the_raw_replicates_for_plotting(self):
        """At n=3-5 the raw points must be plottable alongside the region;
        a smooth region alone implies precision we do not have."""
        pts = [(0.1, 0.2), (0.15, 0.25), (0.12, 0.19)]
        out = bootstrap_region(pts, level=0.95, seed=1)
        assert out["replicates"] == pts
        assert out["n_replicates"] == 3

    def test_identical_points_give_a_degenerate_region(self):
        pts = [(0.3, 0.4)] * 4
        out = bootstrap_region(pts, level=0.95, seed=3)
        assert out["x_interval"][0] == pytest.approx(0.3)
        assert out["x_interval"][1] == pytest.approx(0.3)

    def test_region_contains_the_mean(self):
        pts = [(0.1, 0.2), (0.5, 0.6), (0.3, 0.1), (0.2, 0.5)]
        out = bootstrap_region(pts, level=0.95, seed=11)
        mean_x = sum(p[0] for p in pts) / len(pts)
        assert out["x_interval"][0] <= mean_x <= out["x_interval"][1]

    def test_fewer_than_three_replicates_raises(self):
        with pytest.raises(ValueError):
            bootstrap_region([(0.1, 0.2), (0.3, 0.4)], level=0.95, seed=1)

    def test_records_what_the_region_is(self):
        """§2A.3: 'The caption states what the region is.' An uncertainty
        region without that label is uninterpretable, so the label ships
        with the data rather than being left to the plotting code."""
        out = bootstrap_region([(0.1, 0.2)] * 3, level=0.95, seed=1)
        assert "percentile" in out["region_kind"].lower()
        assert out["level"] == 0.95
