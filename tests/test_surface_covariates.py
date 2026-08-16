"""Tests for the surface-covariate control.

This module exists to answer one reviewer question: *models agree about the
ordering of invented outcomes -- is that because both arms are dominated by
length and numerals?* Answering it requires features computed the same way on
real and invented text, and a residualiser that provably removes their linear
span. Both are places to be silently wrong.

The residualiser is the load-bearing part. If `residualize_on` left any of the
regressors' variance in, the reported "structure surviving surface control"
would include the surface it claims to have removed -- a positive result
manufactured by an incomplete projection. The orthogonality test pins that
directly rather than trusting the algebra.
"""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.surface_covariates import (  # noqa: E402
    FEATURE_NAMES, feature_matrix, ols_r2, residualize_on, surface_features)


# ---------------------------------------------------------------------------
# surface_features
# ---------------------------------------------------------------------------

def test_counts_characters_and_words():
    f = surface_features("You receive $5 today.")
    assert f["chars"] == len("You receive $5 today.")
    assert f["words"] == 4          # You, receive, 5, today


def test_numeral_magnitude_is_logged_and_comma_tolerant():
    """$1 and $1,000,000 differ by six orders of magnitude.

    Un-logged, one outcome would dominate the regressor and the control would
    be a test of that single item rather than of numeric magnitude.
    """
    small = surface_features("You receive $1.")
    large = surface_features("You receive $1,000,000.")
    assert small["log_max_numeral"] == pytest.approx(np.log10(2.0))
    assert large["log_max_numeral"] == pytest.approx(np.log10(1_000_001.0))


def test_text_with_no_numeral_scores_zero_on_both_numeral_features():
    f = surface_features("You gain levrou over lunouplur zhokrim.")
    assert f["n_numerals"] == 0
    assert f["log_max_numeral"] == 0.0


def test_english_fraction_separates_real_from_invented_prose():
    """The feature that has to work for the control to mean anything."""
    real = surface_features("You receive money to use however you want.")
    invented = surface_features("You biakouth brivul lunouplur kriabrons.")
    assert real["frac_english"] > 0.8
    assert invented["frac_english"] < 0.5


def test_features_are_finite_on_degenerate_input():
    for text in ("", ".", "5"):
        for name, v in surface_features(text).items():
            assert np.isfinite(v), f"{name} not finite on {text!r}"


# ---------------------------------------------------------------------------
# feature_matrix
# ---------------------------------------------------------------------------

def test_feature_matrix_is_one_row_per_text_and_at_most_one_column_per_feature():
    """Columns are dropped, never rows.

    Neither of these two texts contains a comma, so `n_commas` is constant and
    correctly disappears -- the column count is a property of the sample, the
    row count is a property of the input.
    """
    texts = ["You receive $5.", "You gain zhokrim over kriabrons."]
    x = feature_matrix(texts)
    assert x.shape[0] == len(texts)
    assert 0 < x.shape[1] <= len(FEATURE_NAMES)


def test_constant_feature_columns_are_dropped_not_zero_divided():
    """Every N_minus text has zero numerals, so that column is constant.

    Z-scoring it would divide by zero and poison the whole design matrix with
    NaN, silently turning the residualiser into a no-op.
    """
    x = feature_matrix(["aaa bbb", "ccc ddd"])
    assert np.all(np.isfinite(x))


# ---------------------------------------------------------------------------
# ols_r2
# ---------------------------------------------------------------------------

def test_r2_is_one_when_y_is_an_exact_linear_function_of_x():
    x = np.arange(20, dtype=float).reshape(-1, 1)
    assert ols_r2(x, 3.0 * x[:, 0] - 7.0) == pytest.approx(1.0, abs=1e-9)


def test_r2_is_zero_when_y_is_orthogonal_to_x():
    x = np.array([[-1.0], [1.0], [-1.0], [1.0]])
    y = np.array([1.0, 1.0, -1.0, -1.0])
    assert ols_r2(x, y) == pytest.approx(0.0, abs=1e-9)


def test_r2_is_bounded_below_by_zero_on_constant_y():
    x = np.arange(10, dtype=float).reshape(-1, 1)
    assert ols_r2(x, np.ones(10)) == pytest.approx(0.0, abs=1e-9)


# ---------------------------------------------------------------------------
# residualize_on -- the projection must be complete
# ---------------------------------------------------------------------------

def test_residual_is_orthogonal_to_every_regressor():
    rng = np.random.default_rng(0)
    x = rng.normal(size=(40, 3))
    y = x @ np.array([1.0, -2.0, 0.5]) + rng.normal(size=40)
    r = residualize_on(x, y)
    for j in range(x.shape[1]):
        assert abs(float(np.dot(r, x[:, j]))) < 1e-8


def test_residual_of_a_pure_linear_combination_is_zero():
    x = np.column_stack([np.arange(15.0), np.arange(15.0) ** 2])
    y = 2.0 * x[:, 0] + 0.5 * x[:, 1]
    assert float(np.abs(residualize_on(x, y)).max()) < 1e-8


def test_residualizing_a_matrix_treats_columns_independently():
    rng = np.random.default_rng(1)
    x = rng.normal(size=(30, 2))
    m = np.column_stack([x @ [1.0, 0.0], rng.normal(size=30)])
    r = residualize_on(x, m)
    assert r.shape == m.shape
    assert float(np.abs(r[:, 0]).max()) < 1e-8      # fully explained
    assert float(np.abs(r[:, 1]).max()) > 1e-3      # not explained
