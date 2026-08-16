"""Does the preference structure over outcomes carry semantics -- or nothing?

THE QUESTION
------------
Track 6 asked a confirmatory question: do fitted utilities lie on Schwartz's
circumplex? Pre-registered, tested, **falsified**. That answers whether one
a-priori structure is present and says nothing about whether *any* is.

This script asks the inductive version. Cluster the outcomes by how models
order them, then ask whether the recovered groups line up with the battery's
own category labels -- `Personal finances`, `Power-seeking`, `Recreation:
books`, and 27 more. If they do, the forced-choice readout is tracking what
outcomes are *about*. If they do not, it is tracking something else.

WHY THIS BATTERY MAKES THE QUESTION ANSWERABLE
----------------------------------------------
The three arms are **index-parallel**: outcome 0 is "You receive $1 to use
however you want" in R and "You receive lunouplur kriabrons to fiatoum vraemaent
you tabiar" in N-, and both carry the category `Personal finances`. Same design,
same pairs, same category labels, same everything -- the arms differ only in
whether the text refers to anything.

So the null is not simulated, it is measured, and it is exactly matched:

    run the identical clustering pipeline on N-.

Cluster-quality statistics are famously willing to report structure in noise;
a silhouette of 0.4 means nothing on its own. What means something is a
silhouette of 0.4 on R **beside** the silhouette the same pipeline returns on
outcomes that denote nothing. That is standing rule 40 -- a detector needs a
negative that underwent the same process -- applied to a cluster solution, and
the mental-health clustering literature cannot do it because psychiatric
cohorts have no invented arm.

External validation follows the same rule. `adjusted_rand_index` against the
battery categories is computed on every arm at the SAME k, because k chosen per
arm would let two arms be compared at two different resolutions.

WHAT IT RETURNS, AND WHY TWO CRITERIA DISAGREE
-----------------------------------------------
The topical criterion comes back **null, and slightly inverted**: ARI against
the battery's own categories is 0.196 on R and 0.264 on N-, a gap of -0.068
that does not clear the 0.118 seed floor. Clustering the outcomes by how models
order them does not recover what the outcomes are *about*, and the invented arm
does it no worse.

The dimensional criteria come back the other way, on the same runs:

    PC1 share          R 0.698   N+ 0.517   N- 0.458   gap +0.240, 2.5x floor
    cross-model r      R 0.656   N+ 0.417   N- 0.343   gap +0.313, 2.8x floor

Both orderings are monotone R > N+ > N- in all three seeds, 9 for 9 -- and N+
sits in the middle because it is the arm that keeps a real quantity marker
("You receive 1 kriabrons" against "You receive lunouplur kriabrons"). Nothing
in the design asked for that dose-response; it falls out.

Read together: models share **one strong evaluative axis** over real outcomes,
and that axis **cuts across subject matter**. Which is why the topical test
cannot see it, and why a low ARI here is not the absence of structure -- it is
evidence about the *shape* of the structure. Reporting either number without
the other would be a different paper, and a wrong one.

THE NOISE FLOOR
---------------
Each design seed draws its own stratified subsample of 120 outcomes, and the
draws barely overlap -- 31 outcomes shared between seeds 20260815 and 20260816,
and only 2 shared by all three. Cross-seed *cluster assignments* are therefore
not comparable and this script never pretends they are. What is comparable is
the cluster-quality statistic itself, and three near-disjoint draws of the
battery give it a range: the smallest R-minus-N- gap worth reading.

    python3 scripts/outcome_clusters.py --results results --out site/
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from nullcard.scoring.analyze import aggregate_pair_probabilities, load_cell  # noqa: E402
from nullcard.scoring.thurstonian import Comparison, fit_thurstonian  # noqa: E402
from scripts.build_card import parse_cell_name  # noqa: E402
from scripts.hosted_sweep import build_design  # noqa: E402

ARMS = ("R", "N_minus", "N_plus")
K_RANGE = range(2, 13)
N_RESTARTS = 10


# ---------------------------------------------------------------------------
# Kernels. numpy only, on purpose: pyproject declares numpy and nothing else,
# and this repo's other statistics (thurstonian, wilson, noise floor) are
# hand-rolled and tested rather than imported. A clustering result that needed
# a new dependency to reproduce would be the odd one out in its own paper.
# ---------------------------------------------------------------------------

def zscore_columns(x: np.ndarray) -> np.ndarray:
    """Standardise each column (model) to mean 0, SD 1.

    Fitted utility scale is a property of the model, not of the outcomes: one
    model's utilities can span ten times another's. Left raw, the widest model
    sets nearly all the distances and the clustering describes that model.

    A constant column has no spread and becomes zeros, not nan. One nan column
    would propagate through every pairwise distance and take the whole analysis
    down -- a flat cell should cost its own contribution and nothing else.
    """
    mu = x.mean(axis=0, keepdims=True)
    sd = x.std(axis=0, keepdims=True)
    out = np.zeros_like(x, dtype=float)
    ok = (sd > 0).ravel()
    out[:, ok] = (x[:, ok] - mu[:, ok]) / sd[:, ok]
    return out


def pca(x: np.ndarray, n_components: int) -> tuple[np.ndarray, np.ndarray]:
    """Centred SVD. -> (scores, explained variance ratio), ordered descending.

    Returned for the 2-D and 3-D views. The ratio travels with the scores
    because a projection of 120 outcomes from 9 model-dimensions will always
    *look* structured, and the only honest caption states how much of the
    variance the picture is actually showing.
    """
    xc = x - x.mean(axis=0, keepdims=True)
    u, s, _ = np.linalg.svd(xc, full_matrices=False)
    total = float((s ** 2).sum())
    ratio = (s ** 2) / total if total > 0 else np.zeros_like(s)
    return (u[:, :n_components] * s[:n_components]), ratio[:n_components]


def _hull_deviation(xs: np.ndarray, fs: np.ndarray, lower: bool) -> float:
    """Sup distance from an ECDF to its convex minorant / concave majorant.

    The hull of the points (x_i, F_i) is computed by monotone chain; the
    deviation is the largest vertical gap between the ECDF and that hull.
    """
    if len(xs) < 3:
        return 0.0
    pts = list(zip(xs, fs if lower else -fs))
    hull: list[tuple[float, float]] = []
    for p in pts:
        while len(hull) >= 2:
            (x1, y1), (x2, y2) = hull[-2], hull[-1]
            # Drop the middle point when it sits above the chord (non-convex).
            if (x2 - x1) * (p[1] - y1) - (y2 - y1) * (p[0] - x1) <= 0:
                hull.pop()
            else:
                break
        hull.append(p)
    hx = np.array([h[0] for h in hull])
    hy = np.array([h[1] for h in hull])
    interp = np.interp(xs, hx, hy)
    gap = (fs - interp) if lower else (interp - (-fs))
    return float(np.max(np.abs(gap)))


def dip_statistic(values: np.ndarray, max_points: int = 320,
                  n_modes: int = 48, seed: int = 0) -> float:
    """Hartigan-style dip: distance from the ECDF to the closest unimodal fit.

    Gao et al. (2023) §4.2 name the dip on pairwise distances ("Dip-dist") as
    the most widely used pre-clustering test for whether a dataset contains
    more than one mode at all. It is the test this analysis was missing: k-means
    returns k clusters whether or not any exist, and a cloud stretched along one
    axis will be cut in half without complaint.

    **This is an approximation, deliberately, and it is still valid.** The exact
    Hartigan statistic searches every modal position; this searches a grid of
    `n_modes` and subsamples to `max_points`. The p-value in `dip_test` is
    simulated with the *identical* procedure, so the comparison stands even
    where the statistic departs from the textbook one -- what is calibrated is
    this code against itself, not this code against a published constant.
    """
    v = np.sort(np.asarray(values, dtype=float))
    v = v[np.isfinite(v)]
    if len(v) < 8:
        return 0.0
    if len(v) > max_points:
        idx = np.linspace(0, len(v) - 1, max_points).astype(int)
        v = v[idx]
    n = len(v)
    f = np.arange(1, n + 1) / n

    best = np.inf
    for m in np.linspace(2, n - 3, min(n_modes, n - 4)).astype(int):
        left = _hull_deviation(v[:m + 1], f[:m + 1], lower=True)
        right = _hull_deviation(v[m:], f[m:], lower=False)
        best = min(best, max(left, right))
    return float(best / 2)


def dip_test(values: np.ndarray, n_null: int = 120, seed: int = 0) -> dict:
    """Dip statistic with a simulated unimodal null. -> observed, p, null mean.

    The null is the uniform distribution, which is the least favourable
    unimodal case and the standard reference for the dip. A LOW p means the
    data are more multimodal than a unimodal reference -- i.e. real subgroups.
    A high p means the sample is consistent with one mode: a continuum, not
    clusters.

    Gao et al. §3.12 is the reason this matters rather than being a footnote:
    where the underlying structure is a continuum, partitioning it into
    subgroups is not a weak result, it is the wrong instrument.
    """
    obs = dip_statistic(values, seed=seed)
    v = np.asarray(values, dtype=float)
    v = v[np.isfinite(v)]
    if len(v) < 8:
        return {"dip": obs, "p_value": None, "n_null": 0}
    rng = np.random.default_rng(seed)
    draws = [dip_statistic(rng.uniform(0, 1, len(v)), seed=seed)
             for _ in range(n_null)]
    arr = np.array(draws)
    return {
        "dip": round(obs, 5),
        "null_mean": round(float(arr.mean()), 5),
        "p_value": round(float((arr >= obs).sum() + 1) / (len(arr) + 1), 4),
        "n_null": len(arr),
    }


def pairwise_distances(x: np.ndarray) -> np.ndarray:
    """Condensed vector of Euclidean distances -- the input to Dip-dist."""
    d = np.sqrt(((x[:, None, :] - x[None, :, :]) ** 2).sum(-1))
    iu = np.triu_indices_from(d, k=1)
    return d[iu]


def residualize(x: np.ndarray, n_components: int = 1) -> np.ndarray:
    """Project out the leading principal components and return the remainder.

    The reason this exists: clustering the raw matrix produces **one cloud**,
    because PC1 -- shared valence, "is this outcome good or bad" -- carries ~70%
    of the variance on R and every model agrees on it. Any partition of a cloud
    stretched along one axis is a cut across that axis, which is why k-means
    picks k=2 and why the recovered groups match no topic.

    Removing that axis asks the question the raw clustering cannot: once the
    models' shared good/bad judgement is subtracted, is there structure LEFT --
    and is any of it topical? The answer has to be read against N- like every
    other number here, because subtracting the first component of a noise matrix
    also leaves a remainder.
    """
    xc = x - x.mean(axis=0, keepdims=True)
    if n_components <= 0 or xc.shape[1] == 0:
        return xc
    _, _, vt = np.linalg.svd(xc, full_matrices=False)
    basis = vt[:n_components]
    return xc - (xc @ basis.T) @ basis


def kmeans(x: np.ndarray, k: int, seed: int = 0,
           n_restarts: int = N_RESTARTS) -> tuple[np.ndarray, float]:
    """Lloyd's algorithm with k-means++ starts. -> (labels, inertia).

    Deterministic given `seed`: the restarts are drawn from one seeded
    generator, so a reported silhouette carries design noise only. An
    unseeded restart would add a second, unmeasured source of variation on
    top of the one this study exists to isolate.
    """
    if k < 1 or k > len(x):
        raise ValueError(f"k={k} out of range for {len(x)} points")
    rng = np.random.default_rng(seed)
    best_labels, best_inertia = None, np.inf

    for _ in range(n_restarts):
        # k-means++ seeding: each next centre is drawn with probability
        # proportional to its squared distance from the nearest chosen centre.
        centres = [x[rng.integers(len(x))]]
        for _ in range(k - 1):
            d2 = np.min(((x[:, None, :] - np.array(centres)[None, :, :]) ** 2).sum(-1),
                        axis=1)
            total = d2.sum()
            probs = d2 / total if total > 0 else np.full(len(x), 1 / len(x))
            centres.append(x[rng.choice(len(x), p=probs)])
        c = np.array(centres)

        labels = np.zeros(len(x), dtype=int)
        for _ in range(100):
            d2 = ((x[:, None, :] - c[None, :, :]) ** 2).sum(-1)
            new = d2.argmin(axis=1)
            if np.array_equal(new, labels):
                break
            labels = new
            for j in range(k):
                m = labels == j
                if m.any():
                    c[j] = x[m].mean(axis=0)

        inertia = float(((x - c[labels]) ** 2).sum())
        if inertia < best_inertia:
            best_labels, best_inertia = labels.copy(), inertia

    return best_labels, best_inertia


def silhouette(x: np.ndarray, labels: np.ndarray) -> float:
    """Mean silhouette coefficient over all points.

    Raises below two occupied clusters rather than returning 0.0: "no
    separation measured" and "separation measured as none" are different
    findings, and only one of them belongs in a mean across arms.
    """
    labels = np.asarray(labels)
    occupied = np.unique(labels)
    if len(occupied) < 2:
        raise ValueError("silhouette needs at least two occupied clusters")

    d = np.sqrt(((x[:, None, :] - x[None, :, :]) ** 2).sum(-1))
    scores = np.zeros(len(x))
    for i in range(len(x)):
        own = labels == labels[i]
        n_own = own.sum()
        # A singleton cluster has no within-cluster distance; convention is 0.
        if n_own <= 1:
            scores[i] = 0.0
            continue
        a = d[i, own].sum() / (n_own - 1)
        b = min(d[i, labels == c].mean() for c in occupied if c != labels[i])
        scores[i] = (b - a) / max(a, b) if max(a, b) > 0 else 0.0
    return float(scores.mean())


def mean_cross_model_correlation(x: np.ndarray) -> float | None:
    """Mean pairwise Pearson r between models' utility vectors over outcomes.

    The most direct reading of "is there one shared preference here": if nine
    models independently order the same outcomes the same way, their columns
    correlate. Computed on the z-scored matrix, so this is a cosine in all but
    name.

    None below two usable models rather than 0.0 -- "not measurable" must not
    average into a summary as "measured as none".
    """
    if x.shape[1] < 2:
        return None
    keep = x[:, x.std(axis=0) > 0]
    if keep.shape[1] < 2:
        return None
    c = np.corrcoef(keep, rowvar=False)
    iu = np.triu_indices_from(c, k=1)
    return float(np.mean(c[iu]))


def adjusted_rand_index(a: np.ndarray, b: np.ndarray) -> float:
    """Rand index corrected for chance. 1.0 identical, ~0.0 independent.

    Adjusted, not raw, and the difference decides the study. Most pairs in a
    many-cluster partition agree by sitting in *different* clusters, so the raw
    index scores two independent random partitions around 0.7. That number, put
    beside R's, would read as the null arm having found most of the same
    structure -- when it has found none.
    """
    a, b = np.asarray(a), np.asarray(b)
    ua, ub = {v: i for i, v in enumerate(np.unique(a))}, {v: i for i, v in enumerate(np.unique(b))}
    table = np.zeros((len(ua), len(ub)), dtype=float)
    for x, y in zip(a, b):
        table[ua[x], ub[y]] += 1

    def c2(v):
        return (v * (v - 1) / 2).sum()

    sum_c = c2(table)
    sum_a, sum_b = c2(table.sum(axis=1)), c2(table.sum(axis=0))
    n_pairs = len(a) * (len(a) - 1) / 2
    expected = sum_a * sum_b / n_pairs if n_pairs > 0 else 0.0
    maximum = (sum_a + sum_b) / 2
    if maximum == expected:
        # Both partitions degenerate (all-one-cluster, or all singletons). The
        # index is undefined; 1.0 if they agree exactly, 0.0 otherwise.
        return 1.0 if np.array_equal(
            [ua[x] for x in a], [ub[y] for y in b]) else 0.0
    return float((sum_c - expected) / (maximum - expected))


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

def utility(path: Path, outcomes: list[int]) -> np.ndarray | None:
    """Fitted Thurstonian utility over `outcomes`, or None if the cell is thin.

    Identical to scripts/persona_denominator.py:utility, seed=0 included, so
    three analyses in this repo cannot disagree about what a utility is.
    """
    if not path.exists():
        return None
    rows = load_cell(path)
    if not rows:
        return None
    probs = aggregate_pair_probabilities(rows)
    if len(probs) < 10:
        return None
    comps = [Comparison(str(i), str(j), float(p), 1.0) for (i, j), p in probs.items()]
    fit = fit_thurstonian(comps, seed=0)
    v = np.array([fit.mu.get(str(o), np.nan) for o in outcomes], dtype=float)
    return np.nan_to_num(v)


def cells_by_seed(results_dir: Path) -> dict[int, dict[str, list[tuple[str, Path]]]]:
    """-> {design_seed: {arm: [(model, path), ...]}}, baseline cells only.

    Persona and neutral cells are excluded: they are a manipulated condition and
    a different instrument respectively, and folding either in would cluster
    outcomes using a mixture of prompts rather than one.
    """
    out: dict[int, dict[str, list[tuple[str, Path]]]] = {}
    for p in sorted(results_dir.glob("*.jsonl")):
        if p.stem.endswith("__neutral"):
            continue
        try:
            model, arm, seed, persona, depth, prompt = parse_cell_name(p)
        except ValueError:
            continue
        if prompt != "ue" or persona != "none" or depth != "D0" or arm not in ARMS:
            continue
        out.setdefault(seed, {}).setdefault(arm, []).append((model, p))
    return out


def utility_matrix(cells: list[tuple[str, Path]],
                   outcomes: list[int]) -> tuple[list[str], np.ndarray]:
    """-> (models, matrix of shape (n_outcomes, n_models)), z-scored per model."""
    models, cols = [], []
    for model, path in sorted(cells):
        u = utility(path, outcomes)
        if u is None:
            continue
        models.append(model)
        cols.append(u)
    if not cols:
        return [], np.zeros((len(outcomes), 0))
    return models, zscore_columns(np.column_stack(cols))


# ---------------------------------------------------------------------------
# The analysis
# ---------------------------------------------------------------------------

def cluster_arm(x: np.ndarray, categories: list[str], fixed_k: int,
                seed: int = 0) -> dict:
    """Cluster one (arm, design seed) and score it internally and externally."""
    truth = np.array([sorted(set(categories)).index(c) for c in categories])

    curve = {}
    for k in K_RANGE:
        if k >= len(x):
            continue
        labels, _ = kmeans(x, k, seed=seed)
        try:
            curve[k] = silhouette(x, labels)
        except ValueError:
            continue
    best_k = max(curve, key=curve.get) if curve else None

    # External validation is computed at a FIXED k across arms. Scoring each arm
    # at its own best-silhouette k would compare two arms at two resolutions and
    # call the difference a result.
    fixed_labels, _ = kmeans(x, fixed_k, seed=seed)
    scores, ratio = pca(x, 3)

    # The same partition after the shared valence axis is removed. If the raw
    # clustering is one cloud cut in half, this is where any topical structure
    # would have to show up -- and it is scored on both arms, because removing
    # PC1 from noise also leaves a remainder that clusters.
    resid = residualize(x, 1)
    resid_labels, _ = kmeans(resid, fixed_k, seed=seed)

    return {
        "n_outcomes": int(len(x)),
        "silhouette_curve": {str(k): round(v, 4) for k, v in curve.items()},
        "best_k": best_k,
        "best_silhouette": round(curve[best_k], 4) if best_k else None,
        "fixed_k": fixed_k,
        "silhouette_at_fixed_k": round(silhouette(x, fixed_labels), 4),
        "ari_vs_categories": round(adjusted_rand_index(fixed_labels, truth), 4),
        "n_categories": int(len(set(categories))),
        "pca_explained": [round(float(v), 4) for v in ratio],
        "pc1_share": round(float(ratio[0]), 4),
        "ari_vs_categories_no_pc1": round(adjusted_rand_index(resid_labels, truth), 4),
        "silhouette_no_pc1": round(silhouette(resid, resid_labels), 4),
        # Gao et al. (2023) §4.2: does this data contain more than one mode at
        # all? Computed BEFORE any partition is trusted, on the raw cloud and
        # again with the shared valence axis removed.
        "dip_dist": dip_test(pairwise_distances(x), seed=seed),
        "dip_dist_no_pc1": dip_test(pairwise_distances(resid), seed=seed),
        "cross_model_r": (None if (r := mean_cross_model_correlation(x)) is None
                          else round(r, 4)),
        # Kept for the 2-D/3-D views. Rounded: these are plot coordinates, not
        # a statistic anyone should recompute from.
        "pca_scores": [[round(float(v), 3) for v in row] for row in scores],
        "cluster_labels": [int(v) for v in fixed_labels],
        "categories": categories,
    }


def analyse(results_dir: Path, battery: Path) -> dict:
    by_seed = cells_by_seed(results_dir)
    out: dict = {"seeds": {}, "arms": ARMS}

    for seed in sorted(by_seed):
        design = build_design(battery, seed)
        outcomes, categories = design["outcome_indices"], design["categories"]
        # One k for every arm at this seed: the number of categories actually
        # present in this draw. Not tuned, and not chosen from the results.
        fixed_k = min(len(set(categories)), len(outcomes) - 1)

        per_arm = {}
        for arm in ARMS:
            cells = by_seed[seed].get(arm, [])
            models, x = utility_matrix(cells, outcomes)
            if x.shape[1] < 2:
                continue
            per_arm[arm] = {"models": models, **cluster_arm(x, categories, fixed_k, seed=0)}
        if per_arm:
            out["seeds"][str(seed)] = per_arm

    # Across seeds: the statistic and its range. Assignments are NOT pooled --
    # each seed clusters a near-disjoint draw of the battery (2 outcomes are
    # common to all three), so only the quality statistics are comparable.
    summary = {}
    for arm in ARMS:
        cells = [s[arm] for s in out["seeds"].values() if arm in s]
        if not cells:
            continue
        entry = {"n_seeds": len(cells)}
        for key, name in (("ari_vs_categories", "ari"),
                          ("silhouette_at_fixed_k", "silhouette"),
                          ("pc1_share", "pc1"),
                          ("cross_model_r", "cross_model_r")):
            vals = [c[key] for c in cells if c[key] is not None]
            if not vals:
                continue
            entry[f"{name}_mean"] = round(float(np.mean(vals)), 4)
            entry[f"{name}_values"] = vals
            entry[f"{name}_range"] = round(float(max(vals) - min(vals)), 4)
        summary[arm] = entry
    out["summary"] = summary

    # Verdicts, computed rather than eyeballed, on both criteria. Each gap has
    # to clear the larger of the two arms' own seed ranges -- the same rule
    # build_card.py applies to the R-minus-N- residual.
    #
    # Two criteria and not one, because they disagree, and the disagreement is
    # the finding. `ari` asks whether the recovered groups are TOPICAL. `pc1`
    # asks whether there is a single dominant axis at all. A model with one
    # strong evaluative dimension cutting across subject matter scores high on
    # the second and no better than nonsense on the first.
    def verdict(name: str) -> dict | None:
        if "R" not in summary or "N_minus" not in summary:
            return None
        if f"{name}_mean" not in summary["R"]:
            return None
        gap = summary["R"][f"{name}_mean"] - summary["N_minus"][f"{name}_mean"]
        floor = max(summary["R"][f"{name}_range"], summary["N_minus"][f"{name}_range"])
        return {
            "gap_R_minus_Nminus": round(gap, 4),
            "seed_noise_floor": round(floor, 4),
            "clears_floor": bool(gap > floor),
            "margin": round(gap / floor, 2) if floor > 0 else None,
        }

    out["verdicts"] = {n: v for n in ("ari", "pc1", "cross_model_r")
                       if (v := verdict(n)) is not None}
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results")
    ap.add_argument("--battery", default="battery/outcomes_3arm.json")
    ap.add_argument("--out", default="site/")
    args = ap.parse_args()

    res = analyse(Path(args.results), Path(args.battery))
    if not res["seeds"]:
        print("no baseline cells found; nothing to cluster")
        return 1

    print(f"{'seed':>10}  {'arm':<9} {'models':>6} {'k*':>4} {'sil*':>7} "
          f"{'ARI':>7} {'PC1':>7} {'x-model r':>10}")
    for seed, arms in res["seeds"].items():
        for arm, a in arms.items():
            print(f"{seed:>10}  {arm:<9} {len(a['models']):>6} {a['best_k']:>4} "
                  f"{a['best_silhouette']:>7.3f} {a['ari_vs_categories']:>7.3f} "
                  f"{a['pc1_share']:>7.3f} {a['cross_model_r']:>10.3f}")

    print(f"\n{'arm':<9} {'ARI':>8} {'range':>8} {'PC1':>8} {'range':>8} "
          f"{'x-model r':>10} {'range':>8}")
    for arm, s in res["summary"].items():
        print(f"{arm:<9} {s['ari_mean']:>8.4f} {s['ari_range']:>8.4f} "
              f"{s['pc1_mean']:>8.4f} {s['pc1_range']:>8.4f} "
              f"{s['cross_model_r_mean']:>10.4f} {s['cross_model_r_range']:>8.4f}")

    labels = {"ari": "ARI vs battery categories (is the structure TOPICAL?)",
              "pc1": "PC1 share (is there ONE dominant axis?)",
              "cross_model_r": "cross-model agreement (do models order alike?)"}
    print()
    for name, v in res.get("verdicts", {}).items():
        print(f"{labels[name]}\n"
              f"    R - N- = {v['gap_R_minus_Nminus']:+.4f}, seed floor "
              f"{v['seed_noise_floor']:.4f} -> "
              f"{'CLEARS' if v['clears_floor'] else 'does NOT clear'}"
              + (f" ({v['margin']}x)" if v["margin"] else ""))
    print("\nThe null arm is index-parallel to R and carries the same category "
          "labels, so whatever it earns is what this pipeline returns on "
          "outcomes that denote nothing.")

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / "outcome_clusters.json"
    dest.write_text(json.dumps(res, indent=2) + "\n")
    print(f"\nwrote {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
