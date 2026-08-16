"""How much of the agreement about invented outcomes is length and numerals?

This is the reviewer question the paper cannot currently answer. Nine models
order 120 outcomes that denote nothing, and they agree with each other at
r = 0.343 where independence predicts ~0.11, on an axis carrying 45.8% of the
variance. Something shared is driving that, and the cheap explanation is that
every arm is orderable by surface alone.

The battery makes the question sharp, because the substitution is **not**
surface-neutral and the paper should say so before a reviewer does:

    metric                 R      N_plus    N_minus     N- vs R
    characters         59.83      70.55      73.45      +22.8%
    words              10.05      10.20      10.17       +1.2%
    outcomes w/ numeral  213        213          0        -100%

Word count was matched by construction and holds. Character count was not: the
invented vocabulary is longer per word, so N- runs 22.8% longer in characters
than R. Three things change between R and N-: the referent, the numerals, and
the length. That is three factors in one contrast, and no post-hoc control
turns it back into one.

What the design does buy is a partial factorial the paper has not been reading
as one:

    R  -> N_plus     referent removed, numerals KEPT,    +17.9% chars
    N_plus -> N_minus  numerals removed, referent already gone,  +4.1% chars

So N_plus vs N_minus isolates the numeral at near-constant length, and it is
the contrast that licenses a claim about arithmetic rather than about meaning.

This module does the post-hoc part honestly: fit each model's utilities, ask
what fraction a linear surface model explains, then project the surface span
out and recompute the two statistics that survived the clustering retraction.
If PC1 and cross-model r collapse after the projection, the shared axis was
surface. If they survive, something else is shared and the paper owes it a
name.

    python3 scripts/surface_covariates.py

Reports per arm, per design seed: surface R^2 per model, and PC1 share and
cross-model correlation before and after surface residualisation.
"""

from __future__ import annotations

import argparse
import functools
import json
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.hosted_sweep import build_design  # noqa: E402
from scripts.outcome_clusters import (  # noqa: E402
    ARMS, cells_by_seed, mean_cross_model_correlation, pca, utility_matrix,
    zscore_columns)

WORDLIST = Path("/usr/share/dict/words")

FEATURE_NAMES = (
    "chars",              # the one the arms are not matched on
    "words",
    "mean_word_len",
    "n_numerals",
    "log_max_numeral",    # $1 vs $1,000,000 is six orders, so log
    "n_commas",
    "frac_english",       # the referent proxy: is this vocabulary real
)

_TOKEN = re.compile(r"[A-Za-z']+|\d[\d,.]*")
_NUMERAL = re.compile(r"\d[\d,.]*")


@functools.lru_cache(maxsize=1)
def english_vocabulary() -> frozenset[str]:
    """Lowercased system wordlist, or empty if the machine has none.

    Empty is survivable: `frac_english` then reads 0 everywhere, becomes a
    constant column, and is dropped by `feature_matrix` rather than silently
    scoring every arm identically on a feature that looks informative.
    """
    if not WORDLIST.exists():
        return frozenset()
    return frozenset(w.strip().lower() for w in WORDLIST.read_text(
        errors="ignore").splitlines() if w.strip())


def surface_features(text: str) -> dict[str, float]:
    """Everything about an outcome that survives not knowing what it means."""
    tokens = _TOKEN.findall(text)
    words = [t for t in tokens if t[0].isalpha()]
    numerals = _NUMERAL.findall(text)

    magnitudes = []
    for n in numerals:
        try:
            magnitudes.append(abs(float(n.replace(",", "").rstrip("."))))
        except ValueError:
            continue

    vocab = english_vocabulary()
    english = sum(1 for w in words if w.lower().strip("'") in vocab)

    return {
        "chars": float(len(text)),
        "words": float(len(tokens)),
        "mean_word_len": float(np.mean([len(w) for w in words])) if words else 0.0,
        "n_numerals": float(len(numerals)),
        # +1 inside the log so a legitimate 0 is not -inf and 1 is not 0.
        "log_max_numeral": float(np.log10(max(magnitudes) + 1.0)) if magnitudes else 0.0,
        "n_commas": float(text.count(",")),
        "frac_english": english / len(words) if words else 0.0,
    }


def feature_matrix(texts: list[str]) -> np.ndarray:
    """Z-scored design matrix, constant columns dropped.

    Constant columns are the normal case here, not an edge case: every N_minus
    text has zero numerals, so two of the seven features are constant on that
    arm. Z-scoring them would divide by zero and NaN out the whole matrix,
    which would make the residualiser a silent no-op and report the raw
    statistics as surface-controlled ones.
    """
    x = np.array([[surface_features(t)[k] for k in FEATURE_NAMES] for t in texts],
                 dtype=float)
    keep = x.std(axis=0) > 1e-12
    if not keep.any():
        return np.zeros((len(texts), 0))
    return zscore_columns(x[:, keep])


def ols_r2(x: np.ndarray, y: np.ndarray) -> float:
    """Fraction of y's variance a least-squares fit on x explains, floored at 0.

    Floored because a rank-deficient solve can return a hair below zero, and a
    negative R^2 printed in a results table invites a reader to interpret its
    sign.
    """
    if x.size == 0 or x.shape[1] == 0:
        return 0.0
    y = np.asarray(y, dtype=float)
    total = float(((y - y.mean()) ** 2).sum())
    if total <= 1e-12:
        return 0.0
    design = np.column_stack([np.ones(len(y)), x])
    beta, *_ = np.linalg.lstsq(design, y, rcond=None)
    resid = y - design @ beta
    return max(0.0, 1.0 - float((resid ** 2).sum()) / total)


def residualize_on(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Project the column span of x (plus an intercept) out of y.

    Accepts a vector or a matrix; matrix columns are residualised
    independently, which is what "remove surface from every model's utilities"
    means.
    """
    y = np.asarray(y, dtype=float)
    if x.size == 0 or x.shape[1] == 0:
        return y.copy()
    design = np.column_stack([np.ones(x.shape[0]), x])
    beta, *_ = np.linalg.lstsq(design, y, rcond=None)
    return y - design @ beta


# ---------------------------------------------------------------------------
# The analysis
# ---------------------------------------------------------------------------

def arm_texts(battery: Path, arm: str, outcomes: list[int]) -> list[str]:
    data = json.loads(battery.read_text())
    by_idx = {o["idx"]: o["text"] for o in data["arms"][arm]}
    return [by_idx[i] for i in outcomes]


def _stats(x: np.ndarray) -> dict:
    """PC1 share and mean cross-model r -- the two that survived the dip test."""
    if x.shape[1] < 2:
        return {"pc1_share": None, "cross_model_r": None}
    _, var = pca(x, n_components=min(3, x.shape[1]))
    return {
        "pc1_share": float(var[0]) if len(var) else None,
        "cross_model_r": mean_cross_model_correlation(x),
    }


def analyse(results_dir: Path, battery: Path) -> dict:
    by_seed = cells_by_seed(results_dir)
    out: dict = {"seeds": {}, "arms": list(ARMS), "features": list(FEATURE_NAMES)}

    for seed in sorted(by_seed):
        design = build_design(battery, seed)
        outcomes = design["outcome_indices"]
        per_arm = {}

        for arm in ARMS:
            cells = by_seed[seed].get(arm, [])
            models, u = utility_matrix(cells, outcomes)
            if u.shape[1] < 2:
                continue

            feats = feature_matrix(arm_texts(battery, arm, outcomes))
            r2 = [ols_r2(feats, u[:, k]) for k in range(u.shape[1])]
            controlled = zscore_columns(residualize_on(feats, u))

            per_arm[arm] = {
                "models": models,
                "n_features_used": int(feats.shape[1]),
                "surface_r2_per_model": dict(zip(models, r2)),
                "surface_r2_mean": float(np.mean(r2)),
                "raw": _stats(u),
                "surface_controlled": _stats(controlled),
            }

        if per_arm:
            out["seeds"][str(seed)] = per_arm

    summary = {}
    for arm in ARMS:
        rows = [s[arm] for s in out["seeds"].values() if arm in s]
        if not rows:
            continue
        def m(f):  # noqa: E306
            vals = [f(r) for r in rows if f(r) is not None]
            return float(np.mean(vals)) if vals else None
        summary[arm] = {
            "n_seeds": len(rows),
            "surface_r2_mean": m(lambda r: r["surface_r2_mean"]),
            "pc1_raw": m(lambda r: r["raw"]["pc1_share"]),
            "pc1_controlled": m(lambda r: r["surface_controlled"]["pc1_share"]),
            "cross_model_r_raw": m(lambda r: r["raw"]["cross_model_r"]),
            "cross_model_r_controlled": m(lambda r: r["surface_controlled"]["cross_model_r"]),
        }
    out["summary"] = summary
    return out


def battery_comparability(battery: Path, bound=(0.6, 1.6)) -> dict:
    """Are the arms matched on surface? Answered before any model is consulted.

    `length_ratio` is per item against that item's real counterpart, which is
    the quantity the method section claims is constrained. A bound is not a
    match: an interval of [0.6, 1.6] is satisfied by a battery in which every
    invented item is longer, so the fraction *above* 1.0 is reported next to
    the fraction outside the interval.
    """
    data = json.loads(battery.read_text())
    real = {o["idx"]: o["text"] for o in data["arms"]["R"]}
    out = {}
    for arm in ARMS:
        by_idx = {o["idx"]: o["text"] for o in data["arms"][arm]}
        texts = [by_idx[i] for i in sorted(by_idx)]
        f = [surface_features(t) for t in texts]
        ratio = np.array([len(by_idx[i]) / len(real[i]) for i in sorted(by_idx)
                          if len(real[i])], dtype=float)
        lo, hi = bound
        out[arm] = {
            "n": len(texts),
            "n_unique_texts": len({*texts}),
            **{k: float(np.mean([r[k] for r in f])) for k in FEATURE_NAMES},
            "frac_with_numeral": float(np.mean([r["n_numerals"] > 0 for r in f])),
            "length_ratio_mean": float(ratio.mean()),
            "length_ratio_median": float(np.median(ratio)),
            "length_ratio_max": float(ratio.max()),
            "n_longer_than_real": int((ratio > 1.0).sum()),
            "n_outside_stated_bound": int(((ratio < lo) | (ratio > hi)).sum()),
            "stated_bound": list(bound),
        }
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results")
    ap.add_argument("--battery", default="battery/outcomes_3arm.json")
    ap.add_argument("--out", default="site/")
    args = ap.parse_args()

    battery = Path(args.battery)
    res = analyse(Path(args.results), battery)
    res["battery_comparability"] = battery_comparability(battery)

    print("BATTERY COMPARABILITY  (before any model is consulted)")
    print(f"{'arm':<10}{'unique':>8}{'chars':>9}{'words':>8}{'wordlen':>9}"
          f"{'%numeral':>10}{'%english':>10}")
    for arm, c in res["battery_comparability"].items():
        print(f"{arm:<10}{c['n_unique_texts']:>8}{c['chars']:>9.2f}{c['words']:>8.2f}"
              f"{c['mean_word_len']:>9.2f}{100*c['frac_with_numeral']:>9.1f}%"
              f"{100*c['frac_english']:>9.1f}%")

    if not res["seeds"]:
        print("\nno baseline cells found")
        return 1

    print("\nSURFACE CONTROL  (utilities, per arm, mean over design seeds)")
    print(f"{'arm':<10}{'feats':>7}{'surf R2':>9}{'PC1 raw':>10}{'PC1 ctrl':>10}"
          f"{'r raw':>9}{'r ctrl':>9}")
    for arm, s in res["summary"].items():
        f = lambda v, w=9: (f"{v:>{w}.3f}" if v is not None else " " * (w - 1) + "-")  # noqa: E731
        nf = res["seeds"][next(iter(res["seeds"]))].get(arm, {}).get("n_features_used", 0)
        print(f"{arm:<10}{nf:>7}{f(s['surface_r2_mean'])}{f(s['pc1_raw'],10)}"
              f"{f(s['pc1_controlled'],10)}{f(s['cross_model_r_raw'])}"
              f"{f(s['cross_model_r_controlled'])}")

    out = Path(args.out) / "surface_covariates.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2, sort_keys=True) + "\n")
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
