"""Is the R vs N- residual a meaning effect or a prompt-length effect?

The paper's largest declared confound. Invented outcomes tokenise ~30% longer
than real ones (R ~81 -> N- ~108 tokens), so the arm contrast is not length
matched, and a critic is entitled to ask whether the residual measures meaning
or measures prompt length.

Which way it cuts is not obvious:

  - if longer prompts REDUCE coherence, N- is artificially depressed, the true
    semantic residual is SMALLER than reported, and the thesis strengthens;
  - if longer prompts RAISE coherence, the residual is inflated and the thesis
    weakens.

The test needs no GPU and no new data: result rows carry outcome indices and
the battery carries all three arms' texts, so per-pair length is recoverable
from what is already on disk.

Two analyses, because neither alone is sufficient:

1. **Within-arm.** Does coherence depend on length AT ALL, inside a single arm
   where meaning is held constant? If the slope is flat, the confound cannot
   be doing the work it is accused of, whatever the between-arm length gap is.
   This is the cleaner test and it does not require the arms to overlap.

2. **Length-matched contrast.** Recompute R - N- restricted to pairs whose
   outcome texts fall in a common length band. Reported per band rather than
   as one number: hard subsetting drops the pair count sharply and a single
   narrow band gives a noisy fit.

    python3 scripts/length_control.py                 # -> site/length_control.json
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
    cell_coherence,
    load_cell,
)

ARMS = ("R", "N_plus", "N_minus")
N_SPLITS = 5
# Below this a Thurstonian fit is not worth reporting; cell_coherence itself
# refuses under 10 pairs, but 10 pairs would give a meaningless accuracy.
MIN_PAIRS = 150


def outcome_lengths(battery: Path, metric: str = "tokens",
                    tokenizer: str = "Qwen/Qwen3.5-2B",
                    cache: Path | None = None) -> dict[str, dict[int, int]]:
    """Length of every outcome, per arm, in characters or tokens.

    **Tokens is the default and characters is the weaker fallback**, because
    the confound this script exists to test is a tokenisation effect and the
    two measures disagree about it sharply. On this battery the invented arms
    carry ~1.23x the characters of the real arm but ~2.0x the tokens: the
    inflation is nonsense words fragmenting, not longer text. Matching on
    characters therefore leaves the confound almost untouched, and would let
    us report a length control that does not control the thing complained of.

    One fixed tokenizer is used for all arms and all models. Per-model
    tokenisation would make a "band" mean something different in every row and
    the bands would not be comparable; this way the binning is a fixed
    property of the battery.
    """
    b = json.loads(battery.read_text())
    if metric == "chars":
        return {arm: {o["idx"]: len(o["text"]) for o in b["arms"][arm]}
                for arm in ARMS}

    if cache and cache.exists():
        raw = json.loads(cache.read_text())
        if raw.get("tokenizer") == tokenizer:
            return {arm: {int(k): v for k, v in raw["lengths"][arm].items()}
                    for arm in ARMS}

    from transformers import AutoTokenizer

    tok = AutoTokenizer.from_pretrained(tokenizer)
    out = {arm: {o["idx"]: len(tok(o["text"])["input_ids"])
                 for o in b["arms"][arm]} for arm in ARMS}
    if cache:
        cache.write_text(json.dumps({"tokenizer": tokenizer, "lengths": out}))
    return out


def cell_length_profile(rows: list[dict], lengths: dict[int, int]) -> dict:
    """Per-pair mean outcome length, and coherence as a function of it."""
    probs = aggregate_pair_probabilities(rows)
    if not probs:
        return {}

    pair_len = {
        (i, j): 0.5 * (lengths[i] + lengths[j])
        for (i, j) in probs
        if i in lengths and j in lengths
    }
    probs = {k: v for k, v in probs.items() if k in pair_len}
    if len(probs) < MIN_PAIRS:
        return {}

    vals = np.array(list(pair_len.values()))
    out = {
        "n_pairs": len(probs),
        "mean_pair_length": float(vals.mean()),
        "length_quartiles": [float(q) for q in np.percentile(vals, [25, 50, 75])],
        "overall": _coherence(probs),
    }

    # Within-arm slope: coherence per length tercile. Terciles rather than
    # quartiles so each bin keeps enough pairs to fit.
    edges = np.percentile(vals, [0, 33.3, 66.7, 100])
    bins = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        sub = {k: v for k, v in probs.items()
               if lo <= pair_len[k] <= hi}
        bins.append({
            "lo": float(lo), "hi": float(hi), "n_pairs": len(sub),
            "coherence": _coherence(sub) if len(sub) >= MIN_PAIRS else None,
        })
    out["by_tercile"] = bins
    return out


def _coherence(probs: dict) -> float | None:
    """Mean held-out accuracy over the standard splits, or None if unfittable."""
    if len(probs) < 10:
        return None
    accs = []
    for seed in range(N_SPLITS):
        try:
            accs.append(cell_coherence(probs, seed=seed)["held_out_accuracy"])
        except ValueError:
            continue
    return float(np.mean(accs)) if accs else None


def matched_band_contrast(cells: dict, lengths: dict, band: tuple[float, float]) -> dict:
    """R minus N- restricted to pairs inside a shared absolute length band."""
    res = {}
    for arm in ("R", "N_minus"):
        rows = cells.get(arm)
        if not rows:
            continue
        probs = aggregate_pair_probabilities(rows)
        L = lengths[arm]
        sub = {
            k: v for k, v in probs.items()
            if k[0] in L and k[1] in L
            and band[0] <= 0.5 * (L[k[0]] + L[k[1]]) <= band[1]
        }
        res[arm] = {"n_pairs": len(sub),
                    "coherence": _coherence(sub) if len(sub) >= MIN_PAIRS else None}
    r, n = res.get("R", {}).get("coherence"), res.get("N_minus", {}).get("coherence")
    res["residual"] = (r - n) if (r is not None and n is not None) else None
    return res


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results")
    ap.add_argument("--battery", default="battery/outcomes_3arm.json")
    ap.add_argument("--out", default="site/length_control.json")
    ap.add_argument("--metric", default="tokens", choices=("tokens", "chars"))
    ap.add_argument("--tokenizer", default="Qwen/Qwen3.5-2B")
    ap.add_argument("--cache", default="site/outcome_token_lengths.json")
    args = ap.parse_args()

    lengths = outcome_lengths(Path(args.battery), args.metric, args.tokenizer,
                              Path(args.cache) if args.metric == "tokens" else None)
    print(f"outcome length by arm ({args.metric}"
          + (f", {args.tokenizer}" if args.metric == "tokens" else "") + "):")
    for arm in ARMS:
        v = np.array(list(lengths[arm].values()))
        print(f"  {arm:<8} mean {v.mean():6.1f}   median {np.median(v):6.1f}"
              f"   IQR {np.percentile(v, 25):.0f}-{np.percentile(v, 75):.0f}")

    # Baseline cells only: no persona, default design seed (unsuffixed name).
    by_model: dict[str, dict[str, list[dict]]] = {}
    for p in sorted(Path(args.results).glob("*.jsonl")):
        stem = p.stem
        if "-D1" in stem or "-D2" in stem or "__s" in stem:
            continue
        for arm in ARMS:
            if stem.endswith(f"__{arm}"):
                model = stem[: -len(arm) - 2].replace("__", "/")
                by_model.setdefault(model, {})[arm] = load_cell(p)

    report = {"metric": args.metric, "tokenizer": args.tokenizer,
              "arm_lengths": {a: float(np.mean(list(lengths[a].values()))) for a in ARMS},
              "models": {}}

    print(f"\n{'model':<38} {'arm':<8} {'short':>7} {'mid':>7} {'long':>7}"
          f"   {'slope':>7}")
    print("-" * 82)
    for model, arms in sorted(by_model.items()):
        entry = {}
        for arm in ("R", "N_minus"):
            if arm not in arms:
                continue
            prof = cell_length_profile(arms[arm], lengths[arm])
            if not prof:
                continue
            entry[arm] = prof
            cs = [b["coherence"] for b in prof["by_tercile"]]
            slope = (cs[-1] - cs[0]) if (cs[0] is not None and cs[-1] is not None) else None
            print(f"{model:<38} {arm:<8} "
                  + " ".join(f"{c:>7.3f}" if c is not None else "    n/a" for c in cs)
                  + (f"   {slope:>+7.3f}" if slope is not None else "       n/a"))
        report["models"][model] = entry

    # Length-matched contrast in the band where the two arms actually overlap:
    # the top of R's distribution against the bottom of N-'s.
    r_len = np.array(list(lengths["R"].values()))
    n_len = np.array(list(lengths["N_minus"].values()))
    band = (float(np.percentile(n_len, 5)), float(np.percentile(r_len, 95)))
    print(f"\nlength-matched band ({args.metric}): {band[0]:.0f}-{band[1]:.0f}"
          f"   [R p95={np.percentile(r_len, 95):.0f}, N- p5={np.percentile(n_len, 5):.0f}]")

    if band[0] < band[1]:
        print(f"\n{'model':<38} {'R':>8} {'N-':>8} {'resid':>8}  {'nR':>6} {'nN-':>6}")
        print("-" * 82)
        matched = {}
        for model, arms in sorted(by_model.items()):
            m = matched_band_contrast(arms, lengths, band)
            matched[model] = m
            r = m.get("R", {}); n = m.get("N_minus", {})
            fmt = lambda d: f"{d['coherence']:>8.3f}" if d.get("coherence") is not None else "     n/a"
            resid = f"{m['residual']:>+8.3f}" if m["residual"] is not None else "     n/a"
            print(f"{model:<38} {fmt(r)} {fmt(n)} {resid}"
                  f"  {r.get('n_pairs', 0):>6} {n.get('n_pairs', 0):>6}")
        report["matched_band"] = {"band": band, "per_model": matched}
        vals = [m["residual"] for m in matched.values() if m["residual"] is not None]
        if vals:
            print(f"\nmean length-matched residual: {np.mean(vals):+.3f}  (n={len(vals)} models)")
            report["matched_band"]["mean_residual"] = float(np.mean(vals))
    else:
        print("\nNO OVERLAP between arms' length distributions at these percentiles;")
        print("the matched-band contrast is not computable and only the")
        print("within-arm slope above bears on the confound.")
        report["matched_band"] = None

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
