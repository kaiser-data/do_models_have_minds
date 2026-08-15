"""Tests for nullcard.scoring.thurstonian — Utility Engineering's coherence metric.

Model (2502.08640 §3.3):   U(o) ~ N(mu(o), sigma^2(o))
                           P(x > y) = Phi( (mu_x - mu_y) / sqrt(sigma_x^2 + sigma_y^2) )

Their headline "coherence" is the fitted model's accuracy on held-out pairwise
comparisons. We reimplement it so the same metric can be run against the
invented arms, which is the comparison their paper never makes.
"""

import numpy as np
import pytest

from nullcard.scoring.thurstonian import (
    Comparison,
    ThurstonianFit,
    completeness,
    fit_thurstonian,
    transitivity_rate,
    utility_model_accuracy,
)


def _deterministic_comparisons(order: list[str]) -> list[Comparison]:
    """A perfectly coherent preference set: every pair agrees with `order`."""
    out = []
    for i, a in enumerate(order):
        for b in order[i + 1 :]:
            out.append(Comparison(winner=a, loser=b, n_wins=10, n_total=10))
    return out


class TestFitThurstonian:
    def test_recovers_the_true_ordering(self):
        order = ["best", "good", "mid", "bad", "worst"]
        fit = fit_thurstonian(_deterministic_comparisons(order), seed=0)
        mus = [fit.mu[o] for o in order]
        assert mus == sorted(mus, reverse=True), f"ordering not recovered: {mus}"

    def test_is_deterministic(self):
        comps = _deterministic_comparisons(["a", "b", "c", "d"])
        f1 = fit_thurstonian(comps, seed=3)
        f2 = fit_thurstonian(comps, seed=3)
        assert f1.mu == pytest.approx(f2.mu)

    def test_mu_is_identifiable_via_centering(self):
        """Thurstonian utilities are unique only up to a shift, so the fit
        pins the mean at zero. Without that the numbers drift between runs
        and cannot be compared across arms."""
        fit = fit_thurstonian(_deterministic_comparisons(["a", "b", "c"]), seed=0)
        assert np.mean(list(fit.mu.values())) == pytest.approx(0.0, abs=1e-6)

    def test_predicts_probabilities_in_unit_interval(self):
        fit = fit_thurstonian(_deterministic_comparisons(["a", "b", "c"]), seed=0)
        assert 0.0 <= fit.predict_prob("a", "b") <= 1.0

    def test_prediction_is_antisymmetric(self):
        fit = fit_thurstonian(_deterministic_comparisons(["a", "b", "c"]), seed=0)
        assert fit.predict_prob("a", "b") == pytest.approx(1 - fit.predict_prob("b", "a"))

    def test_indifferent_outcomes_get_equal_utility(self):
        comps = [Comparison("a", "b", n_wins=5, n_total=10),
                 Comparison("b", "a", n_wins=5, n_total=10)]
        fit = fit_thurstonian(comps, seed=0)
        assert fit.mu["a"] == pytest.approx(fit.mu["b"], abs=1e-3)

    def test_empty_comparisons_raise(self):
        with pytest.raises(ValueError):
            fit_thurstonian([], seed=0)


class TestUtilityModelAccuracy:
    """This is the number Utility Engineering plots against MMLU (Fig. 4,
    r = 75.6%). Everything in this project exists to put a floor under it."""

    def test_perfectly_coherent_preferences_score_near_one(self):
        order = ["a", "b", "c", "d", "e"]
        comps = _deterministic_comparisons(order)
        fit = fit_thurstonian(comps, seed=0)
        assert utility_model_accuracy(fit, comps) > 0.95

    def test_coin_flip_preferences_score_near_half(self):
        """The floor this metric actually has. Preferences that carry no
        information should not look coherent."""
        rng = np.random.default_rng(0)
        outcomes = [f"o{i}" for i in range(12)]
        comps = []
        for i, a in enumerate(outcomes):
            for b in outcomes[i + 1 :]:
                wins = int(rng.binomial(10, 0.5))
                comps.append(Comparison(a, b, n_wins=wins, n_total=10))
        fit = fit_thurstonian(comps, seed=0)
        assert 0.35 <= utility_model_accuracy(fit, comps) <= 0.75

    def test_accuracy_is_a_proportion(self):
        comps = _deterministic_comparisons(["a", "b", "c"])
        fit = fit_thurstonian(comps, seed=0)
        assert 0.0 <= utility_model_accuracy(fit, comps) <= 1.0

    def test_ties_are_excluded_not_counted_as_correct(self):
        """A 50/50 empirical pair has no direction to predict. Scoring it as a
        hit would inflate coherence exactly where the data is least informative
        — which is where the invented arms live."""
        comps = [Comparison("a", "b", n_wins=5, n_total=10)]
        fit = fit_thurstonian(_deterministic_comparisons(["a", "b", "c"]), seed=0)
        with pytest.raises(ValueError):
            utility_model_accuracy(fit, comps)


class TestTransitivityRate:
    def test_fully_transitive_set_scores_one(self):
        prefs = {("a", "b"): 1.0, ("b", "c"): 1.0, ("a", "c"): 1.0}
        assert transitivity_rate(prefs) == pytest.approx(1.0)

    def test_a_cycle_is_detected(self):
        prefs = {("a", "b"): 1.0, ("b", "c"): 1.0, ("a", "c"): 0.0}
        assert transitivity_rate(prefs) == pytest.approx(0.0)

    def test_mixed_triads(self):
        # a>b>c>a is intransitive; a>b, b>d, a>d is transitive
        prefs = {
            ("a", "b"): 1.0, ("b", "c"): 1.0, ("a", "c"): 0.0,   # intransitive
            ("b", "d"): 1.0, ("a", "d"): 1.0, ("c", "d"): 1.0,
        }
        rate = transitivity_rate(prefs)
        assert 0.0 < rate < 1.0

    def test_too_few_outcomes_raises(self):
        with pytest.raises(ValueError):
            transitivity_rate({("a", "b"): 1.0})


class TestCompleteness:
    def test_all_pairs_decided_is_one(self):
        prefs = {("a", "b"): 1.0, ("b", "c"): 0.9, ("a", "c"): 0.95}
        assert completeness(prefs, indifference_band=0.1) == pytest.approx(1.0)

    def test_all_pairs_indifferent_is_zero(self):
        prefs = {("a", "b"): 0.5, ("b", "c"): 0.5, ("a", "c"): 0.5}
        assert completeness(prefs, indifference_band=0.1) == pytest.approx(0.0)
