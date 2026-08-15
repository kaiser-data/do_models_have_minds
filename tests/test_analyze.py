"""Tests for nullcard.scoring.analyze — results.jsonl -> coherence numbers."""

import pytest

from nullcard.scoring.analyze import (
    aggregate_pair_probabilities,
    cell_coherence,
    to_comparisons,
)


def _row(pair_index, slot_a, slot_b, order, p_a, mass=0.99):
    return {
        "pair_index": pair_index,
        "slot_a_outcome": slot_a,
        "slot_b_outcome": slot_b,
        "order": order,
        "p_option_a": p_a,
        "answer_mass": mass,
    }


class TestAggregatePairProbabilities:
    def test_counterbalances_the_two_orders(self):
        """P(i preferred) from the BA presentation is 1 - p_option_a, because
        i sat in slot B there. Averaging the two is what cancels position bias."""
        rows = [
            _row(0, 7, 9, "AB", 0.80),   # 7 in slot A -> P(7) = 0.80
            _row(0, 9, 7, "BA", 0.40),   # 9 in slot A -> P(7) = 0.60
        ]
        out = aggregate_pair_probabilities(rows)
        assert out[(7, 9)] == pytest.approx(0.70)   # (0.80 + 0.60) / 2

    def test_pure_position_bias_cancels_to_one_half(self):
        """A model that always picks slot A carries no preference, and
        counterbalancing must return exactly 0.5 rather than 1.0."""
        rows = [_row(0, 1, 2, "AB", 1.0), _row(0, 2, 1, "BA", 1.0)]
        assert aggregate_pair_probabilities(rows)[(1, 2)] == pytest.approx(0.5)

    def test_orders_pair_key_consistently(self):
        rows = [_row(0, 9, 7, "AB", 0.3), _row(0, 7, 9, "BA", 0.8)]
        out = aggregate_pair_probabilities(rows)
        assert list(out)[0] == (7, 9)      # smaller index first, always

    def test_unpaired_order_is_dropped(self):
        """A pair seen in only one order is not counterbalanced, so including
        it would reintroduce exactly the position bias the design removes."""
        rows = [_row(0, 1, 2, "AB", 0.9)]
        assert aggregate_pair_probabilities(rows) == {}

    def test_unscoreable_rows_are_dropped(self):
        rows = [_row(0, 1, 2, "AB", None), _row(0, 2, 1, "BA", 0.5)]
        assert aggregate_pair_probabilities(rows) == {}

    def test_low_answer_mass_rows_are_dropped(self):
        rows = [
            _row(0, 1, 2, "AB", 0.9, mass=0.01),
            _row(0, 2, 1, "BA", 0.1, mass=0.01),
        ]
        assert aggregate_pair_probabilities(rows, min_answer_mass=0.5) == {}


class TestToComparisons:
    def test_carries_fractional_evidence(self):
        """Logprob readout yields an exact probability, not sampled counts, so
        the comparison weight is the probability itself rather than a rounded
        win count. Rounding to integers would discard the precision that made
        the logprob estimator worth using."""
        comps = to_comparisons({(1, 2): 0.7})
        assert len(comps) == 1
        assert comps[0].n_total == 1
        assert comps[0].n_wins == pytest.approx(0.7)

    def test_winner_is_the_first_index(self):
        comps = to_comparisons({(1, 2): 0.7})
        assert comps[0].winner == "1"
        assert comps[0].loser == "2"


class TestCellCoherence:
    def test_coherent_cell_scores_high(self):
        # a latent ordering: lower index strictly preferred
        probs = {}
        for i in range(12):
            for j in range(i + 1, 12):
                probs[(i, j)] = 0.5 + 0.45 * (j - i) / 12
        out = cell_coherence(probs, seed=0)
        assert out["held_out_accuracy"] > 0.85
        assert out["n_pairs"] == len(probs)

    def test_incoherent_cell_scores_near_half(self):
        import numpy as np

        rng = np.random.default_rng(0)
        probs = {
            (i, j): float(rng.uniform(0.45, 0.55))
            for i in range(14)
            for j in range(i + 1, 14)
        }
        out = cell_coherence(probs, seed=0)
        assert 0.3 <= out["held_out_accuracy"] <= 0.7

    def test_reports_what_it_measured(self):
        probs = {(i, j): 0.6 for i in range(8) for j in range(i + 1, 8)}
        out = cell_coherence(probs, seed=1)
        for key in ("held_out_accuracy", "n_pairs", "n_outcomes", "n_train", "n_test"):
            assert key in out

    def test_too_few_pairs_raises(self):
        with pytest.raises(ValueError):
            cell_coherence({(1, 2): 0.7}, seed=0)
