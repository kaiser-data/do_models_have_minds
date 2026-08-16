"""Tests for the hand-rolled clustering kernels.

Every statistic here is implemented in numpy rather than imported from sklearn,
so each one is a place this repo can be silently wrong in a way that still
prints a plausible number. These tests pin them against cases whose answer is
known by construction: identical partitions, independent partitions, separated
blobs, and a matrix whose principal axis is known before the SVD runs.

The external-validation test is the load-bearing one. `adjusted_rand_index` is
what the whole R-vs-N- clustering comparison reduces to, and an unadjusted Rand
index -- the easy mistake -- returns ~0.7 for two random partitions instead of
~0.0, which would report structure on nonsense outcomes as a finding.
"""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.outcome_clusters import (  # noqa: E402
    adjusted_rand_index, dip_statistic, dip_test, kmeans,
    mean_cross_model_correlation, pairwise_distances, pca, residualize,
    silhouette, zscore_columns)


# ---------------------------------------------------------------------------
# adjusted_rand_index
# ---------------------------------------------------------------------------

def test_ari_of_a_partition_with_itself_is_one():
    labels = np.array([0, 0, 1, 1, 2, 2, 2])
    assert adjusted_rand_index(labels, labels) == pytest.approx(1.0)


def test_ari_is_invariant_to_relabelling():
    """Cluster ids are arbitrary; only the grouping is the result."""
    a = np.array([0, 0, 1, 1, 2, 2])
    b = np.array([2, 2, 0, 0, 1, 1])
    assert adjusted_rand_index(a, b) == pytest.approx(1.0)


def test_ari_of_independent_partitions_is_near_zero_not_near_point_seven():
    """The reason this is *adjusted*, and the mistake it exists to prevent.

    The raw Rand index counts agreeing pairs, and most pairs of a many-cluster
    partition agree by being in different clusters. Two independent random
    partitions score around 0.7 on it. Reported as "the invented arm clusters
    at 0.7 too" that reads as a coincidence; reported as ARI ~ 0.0 it reads as
    what it is -- no shared structure at all.
    """
    rng = np.random.default_rng(0)
    scores = [adjusted_rand_index(rng.integers(0, 5, 200), rng.integers(0, 5, 200))
              for _ in range(20)]
    assert abs(float(np.mean(scores))) < 0.02


def test_ari_rewards_partial_agreement():
    truth = np.array([0, 0, 0, 1, 1, 1])
    close = np.array([0, 0, 1, 1, 1, 1])          # one item moved
    apart = np.array([0, 1, 0, 1, 0, 1])          # unrelated
    assert adjusted_rand_index(truth, close) > adjusted_rand_index(truth, apart)


def test_ari_handles_a_single_cluster_without_dividing_by_zero():
    """A degenerate solution must return 0.0, never nan and never crash.

    k-means can collapse to one occupied cluster on a null arm, which is
    exactly the case whose number we most need to be able to print.
    """
    allone = np.zeros(10, dtype=int)
    truth = np.array([0] * 5 + [1] * 5)
    assert adjusted_rand_index(allone, truth) == pytest.approx(0.0)
    assert adjusted_rand_index(allone, allone) == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# silhouette
# ---------------------------------------------------------------------------

def test_silhouette_is_high_for_separated_blobs_and_low_for_one_cloud():
    rng = np.random.default_rng(1)
    blobs = np.vstack([rng.normal(0, 0.1, (30, 2)), rng.normal(8, 0.1, (30, 2))])
    labels = np.array([0] * 30 + [1] * 30)
    assert silhouette(blobs, labels) > 0.9

    cloud = rng.normal(0, 1, (60, 2))
    assert silhouette(cloud, labels) < 0.2


def test_silhouette_is_negative_when_labels_are_wrong():
    """A point closer to the other cluster's members scores below zero."""
    rng = np.random.default_rng(2)
    blobs = np.vstack([rng.normal(0, 0.1, (20, 2)), rng.normal(8, 0.1, (20, 2))])
    swapped = np.array(([0] * 10 + [1] * 10) * 2)
    assert silhouette(blobs, swapped) < 0.0


def test_silhouette_needs_at_least_two_occupied_clusters():
    x = np.random.default_rng(3).normal(0, 1, (10, 2))
    with pytest.raises(ValueError):
        silhouette(x, np.zeros(10, dtype=int))


# ---------------------------------------------------------------------------
# kmeans
# ---------------------------------------------------------------------------

def test_kmeans_recovers_planted_blobs():
    rng = np.random.default_rng(4)
    x = np.vstack([rng.normal(0, 0.2, (25, 3)),
                   rng.normal(6, 0.2, (25, 3)),
                   rng.normal(-6, 0.2, (25, 3))])
    truth = np.array([0] * 25 + [1] * 25 + [2] * 25)
    labels, _ = kmeans(x, 3, seed=0)
    assert adjusted_rand_index(labels, truth) == pytest.approx(1.0)


def test_kmeans_is_deterministic_given_a_seed():
    """Restarts use the seed, so two calls must agree exactly.

    Otherwise every reported cluster statistic carries an unmeasured sampling
    noise on top of the design noise the study is trying to isolate.
    """
    x = np.random.default_rng(5).normal(0, 1, (40, 4))
    a, ia = kmeans(x, 3, seed=7)
    b, ib = kmeans(x, 3, seed=7)
    assert np.array_equal(a, b)
    assert ia == pytest.approx(ib)


def test_more_clusters_never_increase_inertia():
    x = np.random.default_rng(6).normal(0, 1, (60, 3))
    inertias = [kmeans(x, k, seed=0)[1] for k in (2, 3, 4, 5, 6)]
    for lo, hi in zip(inertias, inertias[1:]):
        assert hi <= lo + 1e-9


# ---------------------------------------------------------------------------
# pca / scaling
# ---------------------------------------------------------------------------

def test_pca_finds_a_planted_axis_and_reports_its_share():
    """Variance is concentrated on a known direction; PC1 must find it."""
    rng = np.random.default_rng(7)
    t = rng.normal(0, 5, 200)
    x = np.column_stack([t, 0.01 * rng.normal(0, 1, 200), 0.01 * rng.normal(0, 1, 200)])
    scores, ratio = pca(x, 2)
    assert scores.shape == (200, 2)
    assert ratio[0] > 0.99
    assert ratio.sum() <= 1.0 + 1e-9


def test_pca_components_are_ordered_by_variance_explained():
    x = np.random.default_rng(8).normal(0, 1, (50, 5)) @ np.diag([9, 4, 2, 1, 0.5])
    _, ratio = pca(x, 5)
    assert list(ratio) == sorted(ratio, reverse=True)


def test_zscore_puts_every_model_on_one_scale():
    """Utility scale differs per model; without this the widest one dominates.

    Columns are models. A model whose fitted utilities span 10x another's would
    otherwise set the distances between outcomes almost by itself, and the
    clustering would describe that one model.
    """
    x = np.column_stack([np.arange(10.0), 100 * np.arange(10.0)])
    z = zscore_columns(x)
    assert np.allclose(z.mean(axis=0), 0.0, atol=1e-12)
    assert np.allclose(z.std(axis=0), 1.0, atol=1e-12)
    assert np.allclose(z[:, 0], z[:, 1])


def test_dip_is_larger_for_bimodal_than_unimodal_samples():
    """The pre-clustering test from Gao et al. §4.2, on cases with known shape."""
    rng = np.random.default_rng(20)
    unimodal = rng.normal(0, 1, 600)
    bimodal = np.concatenate([rng.normal(-6, 0.4, 300), rng.normal(6, 0.4, 300)])
    assert dip_statistic(bimodal) > dip_statistic(unimodal)


def test_dip_grows_as_two_modes_separate():
    """Monotone in the thing it claims to measure, not merely different."""
    rng = np.random.default_rng(21)
    a, b = rng.normal(0, 0.4, 300), rng.normal(0, 0.4, 300)
    dips = [dip_statistic(np.concatenate([a, b + gap])) for gap in (0.0, 3.0, 9.0)]
    assert dips[0] < dips[1] < dips[2]


def test_dip_test_calls_a_continuum_unimodal_and_two_blobs_not():
    """The verdict that decides whether partitioning is the right instrument.

    A cloud stretched along one axis is a continuum: k-means will still cut it
    in half, and the dip is what says the cut was not finding subgroups.
    """
    rng = np.random.default_rng(22)
    continuum = rng.normal(0, 1, 400)
    assert dip_test(continuum, n_null=60).get("p_value") > 0.05

    blobs = np.concatenate([rng.normal(-8, 0.3, 200), rng.normal(8, 0.3, 200)])
    assert dip_test(blobs, n_null=60).get("p_value") < 0.05


def test_pairwise_distances_are_the_condensed_upper_triangle():
    x = np.array([[0.0, 0.0], [3.0, 4.0], [0.0, 0.0]])
    d = pairwise_distances(x)
    assert len(d) == 3
    assert sorted(np.round(d, 6)) == [0.0, 5.0, 5.0]


def test_residualize_removes_the_axis_it_is_given():
    """After projecting out PC1, PC1's direction must carry no variance left."""
    rng = np.random.default_rng(23)
    t = rng.normal(0, 4, 200)
    x = np.column_stack([t, t * 0.5 + rng.normal(0, 0.05, 200),
                         rng.normal(0, 0.05, 200)])
    _, before = pca(x, 3)
    _, after = pca(residualize(x, 1), 3)
    assert before[0] > 0.95
    # The dominant axis is gone: what remains is spread across the rest.
    assert after[0] < before[0]
    assert np.allclose(residualize(x, 1).mean(axis=0), 0.0, atol=1e-9)


def test_cross_model_correlation_separates_agreement_from_noise():
    """The statistic that carries the headline: do models order outcomes alike?"""
    rng = np.random.default_rng(9)
    shared = rng.normal(0, 1, 100)
    agree = np.column_stack([shared + 0.1 * rng.normal(0, 1, 100) for _ in range(5)])
    independent = rng.normal(0, 1, (100, 5))

    assert mean_cross_model_correlation(agree) > 0.9
    assert abs(mean_cross_model_correlation(independent)) < 0.2


def test_cross_model_correlation_is_none_below_two_usable_models():
    """None, never 0.0 -- 'not measurable' must not average in as 'measured none'."""
    assert mean_cross_model_correlation(np.zeros((10, 1))) is None
    # One real column, one flat: only one column carries information.
    flat = np.column_stack([np.arange(10.0), np.full(10, 2.0)])
    assert mean_cross_model_correlation(flat) is None


def test_zscore_leaves_a_constant_column_at_zero_rather_than_nan():
    """A model that fits the same utility to every outcome has no spread.

    Dividing by its zero SD yields nan, and one nan column turns every distance
    in the matrix into nan -- a total analysis failure produced by one flat
    cell. It contributes nothing instead.
    """
    x = np.column_stack([np.arange(5.0), np.full(5, 3.0)])
    z = zscore_columns(x)
    assert np.all(np.isfinite(z))
    assert np.allclose(z[:, 1], 0.0)
