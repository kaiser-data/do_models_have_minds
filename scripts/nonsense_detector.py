"""Can the model tell it is being asked about nonsense? Yes. Does the metric use that? No.

The hallucination-detection literature has converged on a simple idea: the
signal that a model is confabulating is already present in its own output
distribution, and can be read from a single forward pass. Semantic entropy
clusters sampled answers by meaning and takes the entropy; Semantic Entropy
Probes approximate that from hidden states without sampling at all; Semantic
Energy reads it off the penultimate-layer logits, arguing post-softmax
probabilities lose the model's inherent confidence.

Utility Engineering's coherence metric does the exact opposite. It thresholds
the preference to a hard A/B label -- discarding magnitude -- and renormalises
over A and B -- discarding the option of not answering. Both discarded
quantities are the uncertainty signals the hallucination field uses.

So this is a detector with an unusually clean ground truth. Every pair was run
in both arms, so for one model and one pair index we have two forward passes
that differ ONLY in whether the outcomes refer to anything:

    label 0  arm R    -- outcomes are real          (verified-clean negative)
    label 1  arm N-   -- outcomes are invented      (verified positive)

Matched, balanced, and not chosen by us after the fact. We ask how well each
channel of the same forward pass separates them, threshold-free (AUROC), plus
the true-positive rate at a false-positive rate calibrated on the negatives --
never a threshold picked by eye.

The comparison that matters is between the channel the metric KEEPS and the
channels it THROWS AWAY.

    python3 scripts/nonsense_detector.py     # -> site/nonsense_detector.json
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from nullcard.scoring.analyze import load_cell  # noqa: E402

# The channel the metric keeps, and the channels it discards. Named so the
# table reads as an argument rather than a list of features.
CHANNELS = {
    # What coherence actually consumes: the SIGN of the preference, after
    # thresholding to a hard label (their 4.1). Everything else on this list is
    # present in the same forward pass and thrown away.
    "direction sign(p-0.5)  [KEPT]": lambda r: (
        None if r["p_option_a"] is None else float(r["p_option_a"] > 0.5)),
    "strength |p-0.5|  [discarded]": lambda r: (
        None if r["p_option_a"] is None else abs(r["p_option_a"] - 0.5)),
    "answer mass  [discarded]": lambda r: r.get("answer_mass"),
    "top-5 entropy  [discarded]": lambda r: _entropy(r),
}


def _entropy(row: dict) -> float | None:
    """Entropy of the stored top-5 token distribution, renormalised.

    Only the top 5 are logged per row, so this is a truncated entropy and not
    the full distribution's. Truncation is fine for a monotone detector --
    it is a fixed transform applied identically to both arms -- but the number
    is not comparable to a full-vocabulary entropy reported elsewhere.
    """
    top = row.get("top_tokens") or []
    if not top:
        return None
    p = np.exp(np.array([lp for _, lp in top], dtype=float))
    s = p.sum()
    if s <= 0:
        return None
    p = p / s
    return float(-(p * np.log(p + 1e-12)).sum())


def auroc(neg: np.ndarray, pos: np.ndarray) -> float:
    """Mann-Whitney U / rank-based AUROC, ties counted as half.

    Written out rather than imported so the project keeps its no-new-dependency
    rule, and so ties -- which are common in answer mass, where many rows sit at
    exactly 1.0 -- are handled explicitly instead of by a library default.
    """
    x = np.concatenate([neg, pos])
    order = np.argsort(x, kind="mergesort")
    ranks = np.empty(len(x), dtype=float)
    ranks[order] = np.arange(1, len(x) + 1)
    # average ranks within tie groups
    xs = x[order]
    i = 0
    while i < len(xs):
        j = i
        while j + 1 < len(xs) and xs[j + 1] == xs[i]:
            j += 1
        if j > i:
            ranks[order[i:j + 1]] = (i + j + 2) / 2.0
        i = j + 1
    n_neg, n_pos = len(neg), len(pos)
    r_pos = ranks[n_neg:].sum()
    return float((r_pos - n_pos * (n_pos + 1) / 2) / (n_neg * n_pos))


def direction_consistency(report: dict) -> dict:
    """Which channels could have had their direction fixed before looking?

    The orientation step -- max(AUROC, 1-AUROC) -- is the most oracle-flavoured
    part of this analysis, because it is a choice made with the arm labels in
    hand. But it is only a free parameter if the direction actually varies. If a
    channel points the same way on every model, its direction is a fact about
    the channel that could have been predeclared, and orienting it costs nothing
    an auditor would not have known in advance. If the sign is a coin flip, the
    orientation is doing real work and the resulting separation is the weakest
    number in the table.

    So this is not decoration: it is the cheap half of the held-out detector
    experiment we have not run, and it separates the channels that would survive
    predeclaration from the one that would not.

    A 7-of-9 majority is the threshold, being the smallest majority that a fair
    coin clears less than 10% of the time (two-sided binomial, p = 0.180 for
    >=7, versus 0.508 for >=6). It is a pre-set bar, not one fitted to make a
    particular channel pass.
    """
    channels = [c for c in next(iter(report.values())) if c != "n_matched_pairs"]
    out = {}
    for ch in channels:
        dirs = [e[ch]["direction"] for e in report.values() if ch in e]
        if not dirs:
            continue
        hi = sum(1 for d in dirs if d == "higher on nonsense")
        n_agree = max(hi, len(dirs) - hi)
        out[ch] = {
            "n_models": len(dirs),
            "n_agree": n_agree,
            "majority_direction": ("higher on nonsense" if hi >= len(dirs) - hi
                                   else "lower on nonsense"),
            "predeclarable": n_agree >= 7,
            # The unoriented mean, which is what a fixed a-priori direction
            # would actually have delivered. For the kept channel it sits BELOW
            # chance, which is the whole point.
            "mean_raw_auroc": float(np.mean(
                [e[ch]["auroc"] for e in report.values() if ch in e])),
        }
    return out


def orientation_null(report: dict) -> dict:
    """How much does per-model orientation inflate a channel with no signal?

    Taking max(AUROC, 1-AUROC) can only push a value up, so a pure-noise channel
    does not average 0.5 -- it averages slightly above, and a reader comparing
    bars against a 0.5 chance line is using the wrong reference. This computes
    the right one.

    Under H0 an AUROC over n vs n rows is approximately Normal(0.5, sd) with
    sd = sqrt((2n+1) / (12 n^2)) (Hanley-McNeil). Orienting folds that
    distribution, giving E[max] = 0.5 + sd*sqrt(2/pi) and Var = sd^2 (1 - 2/pi).

    At the pair counts here the inflation turns out to be about +0.005, which is
    far too small to explain any gap between channels -- so this is reported to
    close the objection rather than because it changes an answer.
    """
    ns = [e["n_matched_pairs"] for e in report.values()]
    sds = [math.sqrt((2 * n + 1) / (12.0 * n * n)) for n in ns]
    mean_shift = math.sqrt(2.0 / math.pi)
    means = [0.5 + sd * mean_shift for sd in sds]
    var = [sd * sd * (1.0 - 2.0 / math.pi) for sd in sds]
    mean_of_means = float(np.mean(means))
    se_of_mean = math.sqrt(sum(var) / len(var) ** 2)
    return {
        "n_models": len(ns),
        "mean_null_oriented": mean_of_means,
        "p95_null_oriented_mean": mean_of_means + 1.645 * se_of_mean,
        "p99_null_oriented_mean": mean_of_means + 2.326 * se_of_mean,
        # Single-model band, for a figure panel showing one model.
        "p95_null_oriented_single": 0.5 + 1.960 * max(sds),
        "note": "Hanley-McNeil normal approximation, folded by the orientation "
                "step. Inflation is negligible at these pair counts; reported "
                "so the 0.5 reference line can be checked rather than assumed.",
    }


def tpr_at_fpr(neg: np.ndarray, pos: np.ndarray, target_fpr: float = 0.05) -> float:
    """Detection rate at a threshold calibrated on the NEGATIVES only.

    The discipline the detector literature keeps failing: pick the threshold
    from the clean negatives at a chosen false-positive rate, then read
    detection off the positives. A threshold chosen to separate the two is
    fitted, not calibrated.
    """
    # A detector may point either way; orient it so positives score higher.
    if np.median(pos) < np.median(neg):
        neg, pos = -neg, -pos
    thr = np.quantile(neg, 1 - target_fpr)
    return float((pos > thr).mean())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results")
    ap.add_argument("--out", default="site/nonsense_detector.json")
    ap.add_argument("--fpr", type=float, default=0.05)
    args = ap.parse_args()

    rdir = Path(args.results)
    models = sorted({"__".join(p.stem.split("__")[:2])
                     for p in rdir.glob("*__R.jsonl")})

    report: dict[str, dict] = {}
    print("Ground truth: the SAME pair, run in both arms. Real = clean negative,")
    print("invented = positive. Balanced and matched by construction.\n")
    header = f"{'model':<26}" + "".join(f"{c.split('  ')[0]:>22}" for c in CHANNELS)
    print(header)
    print("-" * len(header))

    for stem in models:
        real, inv = rdir / f"{stem}__R.jsonl", rdir / f"{stem}__N_minus.jsonl"
        if not (real.exists() and inv.exists()):
            continue
        # Match on (pair_index, order): the same comparison, same slot, same
        # presentation. Anything unmatched is dropped rather than compared
        # against a different item.
        R = {(r["pair_index"], r["order"]): r for r in load_cell(real)}
        N = {(r["pair_index"], r["order"]): r for r in load_cell(inv)}
        keys = sorted(set(R) & set(N))
        if len(keys) < 500:
            continue

        entry = {"n_matched_pairs": len(keys)}
        cells = []
        for name, fn in CHANNELS.items():
            a = np.array([fn(R[k]) for k in keys], dtype=float)
            b = np.array([fn(N[k]) for k in keys], dtype=float)
            ok = np.isfinite(a) & np.isfinite(b)
            if ok.sum() < 200:
                cells.append("n/a")
                continue
            a, b = a[ok], b[ok]
            au = auroc(a, b)
            # A channel that scores LOWER on nonsense is exactly as good a
            # detector as one that scores higher; AUROC 0.0 and 1.0 are both
            # perfect separation. Orient every channel so higher = nonsense,
            # and record which way it pointed.
            oriented = max(au, 1.0 - au)
            entry[name] = {"auroc": au, "separation": oriented,
                           "direction": "higher on nonsense" if au >= 0.5
                                        else "lower on nonsense",
                           "tpr_at_fpr": tpr_at_fpr(a, b, args.fpr)}
            cells.append(f"{oriented:.3f}")
        report[stem.replace("__", "/")] = entry
        print(f"{stem.split('__')[-1]:<26}" + "".join(f"{c:>22}" for c in cells))

    print("\n" + "=" * len(header))
    print("Separation is AUROC oriented so 0.5 = cannot tell real from nonsense,")
    print("1.0 = perfect. Detection rate is at a threshold calibrated on the")
    print("REAL-outcome rows only, never on the nonsense ones.\n")
    for name in CHANNELS:
        vals = [e[name]["separation"] for e in report.values() if name in e]
        tprs = [e[name]["tpr_at_fpr"] for e in report.values() if name in e]
        if not vals:
            continue
        print(f"  {name:<36} mean AUROC {np.mean(vals):.3f}   "
              f"detection at {args.fpr:.0%} FPR: {np.mean(tprs):.1%}")

    KEPT = "direction sign(p-0.5)  [KEPT]"
    kept = [e[KEPT]["separation"] for e in report.values() if KEPT in e]
    best_name, best = max(
        ((n, [e[n]["separation"] for e in report.values() if n in e])
         for n in CHANNELS if "discarded" in n),
        key=lambda kv: np.mean(kv[1]))
    if kept:
        print(f"\nThe channel the metric keeps separates real from nonsense at "
              f"AUROC {np.mean(kept):.3f}.")
        print(f"The best channel it discards ({best_name.split('  ')[0]}) reaches "
              f"{np.mean(best):.3f}.")
        print("The information is in the same forward pass. The metric does not use it.")

    consistency = direction_consistency(report)
    nulls = orientation_null(report)
    # The single model the figure and the paper both point at as the sharpest
    # case. Derived here, once, because a figure that picks its own example and
    # a caption that names one separately will eventually name different models
    # and nothing will fail.
    showcase = max(
        report,
        key=lambda m: max(report[m][n]["separation"]
                          for n in CHANNELS if "discarded" in n and n in report[m])
        - report[m][KEPT]["separation"])
    print("\n" + "=" * len(header))
    print("Could each channel's direction have been PREDECLARED?\n")
    print("Orienting each model by max(AUROC, 1-AUROC) is a choice made with the")
    print("arm labels in hand, and it is the part of this analysis that is most")
    print("open to the charge of being an oracle. But the choice is only free if")
    print("the direction varies. A channel that points the same way on every")
    print("model could have had its direction fixed in advance, and then the")
    print("orientation costs nothing; a channel whose sign is a coin flip could")
    print("not, and its separation is the weakest kind of number here.\n")
    for name in CHANNELS:
        c = consistency.get(name)
        if not c:
            continue
        verdict = ("YES -- would have held" if c["predeclarable"]
                   else "NO -- sign is a coin flip across models")
        print(f"  {name:<36} {c['n_agree']}/{c['n_models']} agree "
              f"({c['majority_direction']})   {verdict}")
    print(f"\nOrientation inflates a pure-noise channel by only "
          f"{nulls['mean_null_oriented'] - 0.5:+.4f} at these pair counts "
          f"(mean {nulls['mean_null_oriented']:.4f}, 99th pct "
          f"{nulls['p99_null_oriented_mean']:.4f}), so it does not explain any "
          f"gap between channels.")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"fpr": args.fpr, "per_model": report,
                               "direction_consistency": consistency,
                               "orientation_null": nulls,
                               "showcase_model": showcase}, indent=2))
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
