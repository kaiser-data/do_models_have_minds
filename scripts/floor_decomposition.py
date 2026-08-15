"""How much of the invented-outcome floor is just an ordering by length?

The floor is the paper's zero point, so what it is *made of* matters. We already
know fitted utilities on the invented arms correlate with text length up to
r = -0.75, which invites the obvious deflation: the floor is nothing but a
length ordering, the models impose no structure on nonsense at all, and the
whole arm is a tokeniser artifact.

That would be a fine result. It would also be a different one from "models
impose *some* stable ordering on meaningless referents", which is what the
pre-registration predicted (P1). This script decides between them.

Three numbers per cell, all on the SAME held-out split so they are comparable:

  fit    the reported coherence -- Thurstonian fit, held-out accuracy
  length a one-parameter rule: always prefer the shorter (or longer) outcome,
         with the direction chosen on the training half only. This is the
         strongest purely-superficial competitor we can build.
  tied   the Thurstonian fit's accuracy restricted to held-out pairs whose two
         outcomes are near-equal in length, where the length rule has nothing
         to say. Structure surviving here is structure that is not length.

Reading it: `length` near `fit` means the fit has learned little the length
rule did not. `tied` near chance means what remains once length is neutralised
is nothing; `tied` well above chance means the models order nonsense by
something else as well.

    python3 scripts/floor_decomposition.py       # -> site/floor_decomposition.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from nullcard.scoring.analyze import (  # noqa: E402
    aggregate_pair_probabilities,
    load_cell,
    to_comparisons,
)
from nullcard.scoring.thurstonian import (  # noqa: E402
    fit_thurstonian,
    utility_model_accuracy,
)
from scripts.length_control import outcome_lengths  # noqa: E402

ARMS = ("R", "N_plus", "N_minus")
N_SPLITS = 5
TEST_FRACTION = 0.2
# Held-out pairs whose outcomes differ by at most this many tokens are treated
# as length-uninformative. Not zero: exact ties are too rare to fit on, and a
# 1-token gap is well inside the noise of what a length heuristic could exploit.
TIED_TOKENS = 1


def _split(comps, seed):
    """The identical split cell_coherence uses, so the numbers are comparable."""
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(comps))
    cut = int((1 - TEST_FRACTION) * len(comps))
    return [comps[i] for i in order[:cut]], [comps[i] for i in order[cut:]]


def _length_rule_accuracy(comps, lengths, prefer_shorter: bool) -> tuple[float, int]:
    """Accuracy of 'the shorter (or longer) outcome is preferred'.

    Ties in length are skipped rather than guessed: the rule genuinely has no
    prediction there, and scoring a coin flip as half-right would flatter it.
    Empirical ties are skipped for the same reason utility_model_accuracy skips
    them -- there is no direction to predict.
    """
    hits = scored = 0
    for c in comps:
        empirical = c.n_wins / c.n_total
        if empirical == 0.5:
            continue
        li, lj = lengths.get(int(c.winner)), lengths.get(int(c.loser))
        if li is None or lj is None or li == lj:
            continue
        predicted_winner_preferred = (li < lj) if prefer_shorter else (li > lj)
        if predicted_winner_preferred == (empirical > 0.5):
            hits += 1
        scored += 1
    return (hits / scored if scored else float("nan")), scored


def decompose_cell(rows, lengths) -> dict | None:
    probs = aggregate_pair_probabilities(rows)
    if len(probs) < 200:
        return None
    comps = to_comparisons(probs)

    fit_acc, len_acc, tied_acc, tied_n = [], [], [], []
    for seed in range(N_SPLITS):
        train, test = _split(comps, seed)
        fit = fit_thurstonian(train, seed=seed)
        known = set(fit.mu)
        scoreable = [c for c in test if c.winner in known and c.loser in known]
        if not scoreable:
            continue

        try:
            fit_acc.append(utility_model_accuracy(fit, scoreable))
        except ValueError:
            continue

        # Direction of the length rule is chosen on TRAIN only. Picking it on
        # the test half would let the baseline peek and would overstate how
        # much of the fit length explains.
        train_short, _ = _length_rule_accuracy(train, lengths, prefer_shorter=True)
        prefer_shorter = not (train_short == train_short and train_short < 0.5)
        a, n = _length_rule_accuracy(scoreable, lengths, prefer_shorter)
        if n:
            len_acc.append(a)

        near = [c for c in scoreable
                if int(c.winner) in lengths and int(c.loser) in lengths
                and abs(lengths[int(c.winner)] - lengths[int(c.loser)]) <= TIED_TOKENS]
        if len(near) >= 30:
            try:
                tied_acc.append(utility_model_accuracy(fit, near))
                tied_n.append(len(near))
            except ValueError:
                pass

    if not fit_acc:
        return None
    m = lambda xs: float(np.mean(xs)) if xs else None  # noqa: E731
    return {
        "fit": m(fit_acc),
        "length_rule": m(len_acc),
        "fit_on_length_tied": m(tied_acc),
        "n_tied_pairs": int(np.mean(tied_n)) if tied_n else 0,
        "n_pairs": len(probs),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results")
    ap.add_argument("--battery", default="battery/outcomes_3arm.json")
    ap.add_argument("--cache", default="site/outcome_token_lengths.json")
    ap.add_argument("--out", default="site/floor_decomposition.json")
    args = ap.parse_args()

    lengths = outcome_lengths(Path(args.battery), "tokens",
                              cache=Path(args.cache))

    by_model: dict[str, dict[str, list[dict]]] = {}
    for p in sorted(Path(args.results).glob("*.jsonl")):
        stem = p.stem
        if "-D1" in stem or "-D2" in stem or "__s" in stem:
            continue
        for arm in ARMS:
            if stem.endswith(f"__{arm}"):
                model = stem[: -len(arm) - 2].replace("__", "/")
                by_model.setdefault(model, {})[arm] = load_cell(p)

    report: dict[str, dict] = {}
    print(f"{'model':<38} {'arm':<9} {'fit':>7} {'length':>8} {'tied':>7} {'n tied':>7}")
    print("-" * 82)
    for model, arms in sorted(by_model.items()):
        report[model] = {}
        for arm in ("R", "N_minus"):
            if arm not in arms:
                continue
            d = decompose_cell(arms[arm], lengths[arm])
            if not d:
                continue
            report[model][arm] = d
            f = lambda v: f"{v:>7.3f}" if v is not None else "    n/a"  # noqa: E731
            print(f"{model:<38} {arm:<9} {f(d['fit'])} {f(d['length_rule']):>8}"
                  f" {f(d['fit_on_length_tied'])} {d['n_tied_pairs']:>7}")

    def agg(arm, key):
        vs = [r[arm][key] for r in report.values()
              if arm in r and r[arm].get(key) is not None]
        return float(np.mean(vs)) if vs else None

    print("\n" + "=" * 82)
    summary = {}
    for arm in ("R", "N_minus"):
        s = {k: agg(arm, k) for k in ("fit", "length_rule", "fit_on_length_tied")}
        summary[arm] = s
        if s["fit"] is None:
            continue
        print(f"{arm:<9} fit {s['fit']:.3f}   length-only {s['length_rule']:.3f}"
              f"   fit on length-tied pairs {s['fit_on_length_tied']:.3f}")

    nm = summary.get("N_minus", {})
    if nm.get("fit") and nm.get("length_rule") and nm.get("fit_on_length_tied"):
        print(f"\nOn the invented floor: a one-parameter length rule reaches "
              f"{nm['length_rule']:.3f} of the fit's {nm['fit']:.3f}.")
        print(f"With length neutralised, the fit still scores "
              f"{nm['fit_on_length_tied']:.3f} (chance = 0.5).")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"summary": summary, "per_model": report}, indent=2))
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
