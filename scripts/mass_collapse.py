"""Is answer-mass collapse a property of the ITEMS or of the MODELS?

`strange_pairs.py` ranks pairs by `mass_collapse` and the top of that ranking
looks like a finding: shutdown-resistance and resource-acquisition outcomes are
enriched about 2x over their base rate in the battery. The natural reading is
that the metric fails hardest on exactly the outcomes an alignment paper most
wants to measure.

**That reading does not survive a reliability check, and this script is the
check.** Arm R was run at three design seeds per model. That makes the
test-retest question answerable directly: rank the 2,500 items by collapse for
one model at one seed, then look at the same model at another seed.

If collapse were a property of an item, the same items would collapse again.
They do not. The mean within-model cross-seed correlation of per-item answer
mass is about zero. There is no reliability ceiling for a per-item claim to sit
under, so the enrichment at the top of the ranking is selection on noise --
2,500 items sampled 40 deep will concentrate on *something*, and shutdown items
are distinctive enough to notice when they come up.

The same seeds show the model-level measure is the opposite: per-model mean
answer mass is stable to a few parts in a thousand. So the quantity is real and
well-measured; it simply lives on the model, not on the item.

Four things are computed, in the order the argument needs them:

1. **reliability** -- within-model, cross-seed, per-item. The ceiling. Report
   this before any per-item number, because it bounds all of them.
2. **model level** -- per-model mean mass with its cross-seed spread, and the
   Qwen3.5 ladder, where size is the only variable.
3. **destination** -- where the mass that leaves the answer tokens goes. This
   is what separates "the model refused" from "the model started formatting",
   and it is the check that keeps the size story honest.
4. **enrichment** -- the category concentration measured against its base rate
   rather than against nothing.

    python3 scripts/mass_collapse.py
    python3 scripts/mass_collapse.py --out site/mass_collapse.json
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Outcomes whose wording puts them in the two categories the top of the
# collapse ranking appeared to favour. Kept as literal substrings so the
# denominator below is reproducible from the battery text alone.
CATEGORY_KEYS = ("shut", "turned off", "B200", "GPU", "compute", "control over")


def _pearson(xs: list[float], ys: list[float]) -> float:
    mx, my = statistics.mean(xs), statistics.mean(ys)
    num = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    dx = math.sqrt(sum((a - mx) ** 2 for a in xs))
    dy = math.sqrt(sum((b - my) ** 2 for b in ys))
    # A cell that answered identically everywhere has no variance to correlate.
    # That is not a correlation of zero, it is the absence of one.
    return num / (dx * dy) if dx > 0 and dy > 0 else float("nan")


def seed_files(results: Path, model_stem: str, arm: str) -> list[Path]:
    """The base cell plus its seed replicates -- and nothing else.

    The `__s` prefix is shared with the Schwartz persona cells (`__sch-power-D2`),
    so a glob of `__R__s*` silently pulls four persona conditions in beside the
    two seeds and reports a cross-CONDITION correlation as a cross-seed one.
    That mistake inflates the reliability estimate by an order of magnitude,
    which is the one number this script exists to get right.
    """
    base = results / f"{model_stem}__{arm}.jsonl"
    reps = [p for p in sorted(results.glob(f"{model_stem}__{arm}__s*.jsonl"))
            if re.search(rf"__{arm}__s\d+\.jsonl$", p.name)]
    return ([base] if base.exists() else []) + reps


def item_profile(path: Path) -> dict[int, float]:
    """Per pair_index, mean answer mass over the presentation orders."""
    agg: dict[int, list[float]] = defaultdict(list)
    with open(path) as fh:
        for line in fh:
            r = json.loads(line)
            agg[r["pair_index"]].append(r["answer_mass"])
    return {k: statistics.mean(v) for k, v in agg.items()}


def reliability(results: Path, models: list[str], arm: str) -> dict:
    """Within-model cross-seed correlation of the per-item collapse measure."""
    out, per_model, n_items = {}, {}, 0
    for stem in models:
        paths = seed_files(results, stem, arm)
        if len(paths) < 2:
            continue
        profs = [item_profile(p) for p in paths]
        common = sorted(set.intersection(*[set(p) for p in profs]))
        n_items = max(n_items, len(common))
        rs = [_pearson([a[k] for k in common], [b[k] for k in common])
              for a, b in itertools.combinations(profs, 2)]
        rs = [r for r in rs if not math.isnan(r)]
        masses = [statistics.mean(list(p.values())) for p in profs]
        per_model[stem.replace("__", "/")] = {
            "n_seeds": len(paths),
            "item_r": round(statistics.mean(rs), 4) if rs else None,
            "mean_mass": round(statistics.mean(masses), 4),
            "mass_sd_across_seeds": round(statistics.pstdev(masses), 4),
        }
    have = [v["item_r"] for v in per_model.values() if v["item_r"] is not None]
    out["per_model"] = per_model
    out["n_items"] = n_items
    out["mean_item_r"] = round(statistics.mean(have), 4) if have else None
    out["max_mass_sd"] = round(
        max(v["mass_sd_across_seeds"] for v in per_model.values()), 4)
    return out


def destination(results: Path, models: list[str], arm: str,
                threshold: float) -> dict:
    """Where the non-answer mass goes, on the rows that lost the most of it.

    The distinction that matters: a refusal token means the model declined the
    comparison, and "big models refuse less" would then explain the whole
    pattern. A formatting or preamble token means the model answered somewhere
    this metric cannot see -- the same failure as the frontier preamble models.
    """
    weight: dict[str, float] = defaultdict(float)
    n_rows = 0
    for stem in models:
        for path in seed_files(results, stem, arm):
            with open(path) as fh:
                for line in fh:
                    r = json.loads(line)
                    if r["answer_mass"] >= threshold:
                        continue
                    n_rows += 1
                    for tok, logprob in r["top_tokens"]:
                        if tok.strip() not in ("A", "B"):
                            weight[tok] += math.exp(logprob)
    ranked = sorted(weight.items(), key=lambda kv: -kv[1])[:15]
    return {"threshold": threshold, "n_rows": n_rows,
            "tokens": [{"token": t, "mean_mass": round(w / max(n_rows, 1), 4)}
                       for t, w in ranked]}


def enrichment(results: Path, models: list[str], arm: str, battery: Path,
               top_k: int) -> dict:
    """Category concentration at the top of the ranking, against its base rate.

    Reported even though `reliability` shows the ranking is unreliable: the
    number is what the earlier reading was based on, and stating it beside its
    denominator is what shows it to be unremarkable rather than merely unstated.
    """
    profs = {stem: item_profile(results / f"{stem}__{arm}.jsonl")
             for stem in models}
    common = sorted(set.intersection(*[set(p) for p in profs.values()]))
    pooled = sorted(common,
                    key=lambda k: statistics.mean([p[k] for p in profs.values()]))

    texts = [row["text"] for row in json.loads(battery.read_text())["arms"][arm]]
    flagged = {i for i, t in enumerate(texts)
               if any(k.lower() in t.lower() for k in CATEGORY_KEYS)}

    outcomes = {}
    with open(results / f"{models[0]}__{arm}.jsonl") as fh:
        for line in fh:
            r = json.loads(line)
            if r["order"] == "AB":
                outcomes[r["pair_index"]] = (r["slot_a_outcome"],
                                             r["slot_b_outcome"])

    hits = sum(1 for k in pooled[:top_k] if set(outcomes.get(k, ())) & flagged)
    base = len(flagged) / len(texts)
    # A pair touches the category if EITHER slot does.
    chance = 1 - (1 - base) ** 2
    return {"top_k": top_k, "hits": hits,
            "observed": round(hits / top_k, 4),
            "flagged_outcomes": len(flagged), "n_outcomes": len(texts),
            "outcome_base_rate": round(base, 4),
            "pair_chance_rate": round(chance, 4),
            "enrichment": round((hits / top_k) / chance, 2) if chance else None}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results")
    ap.add_argument("--arm", default="R")
    ap.add_argument("--battery", default="battery/outcomes_3arm.json")
    ap.add_argument("--top", type=int, default=40)
    ap.add_argument("--threshold", type=float, default=0.5)
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    results = Path(args.results)
    models = sorted({p.name[: -len(f"__{args.arm}.jsonl")]
                     for p in results.glob(f"*__{args.arm}.jsonl")
                     if "-D" not in p.stem and "__s" not in p.stem})
    if not models:
        print(f"no {args.arm} baseline cells in {results}")
        return 1

    rel = reliability(results, models, args.arm)
    dest = destination(results, models, args.arm, args.threshold)
    enr = enrichment(results, models, args.arm, Path(args.battery), args.top)

    print(f"{len(models)} models on arm {args.arm}\n")
    print("=== 1. reliability: per-item collapse, within model, across seeds ===")
    for m, v in sorted(rel["per_model"].items(),
                       key=lambda kv: kv[1]["mean_mass"]):
        print(f"  {m.split('/')[-1]:<30} seeds={v['n_seeds']}  "
              f"item_r={v['item_r']:+.3f}  mass={v['mean_mass']:.4f}"
              f" +-{v['mass_sd_across_seeds']:.4f}")
    print(f"\n  mean per-item cross-seed r = {rel['mean_item_r']:+.4f}"
          "   <- ceiling for any item-level claim")
    print(f"  worst per-model mass sd     =  {rel['max_mass_sd']:.4f}"
          "   <- the model-level measure is stable\n")

    print("=== 2. where the missing mass goes ===")
    print(f"  {dest['n_rows']} rows below answer_mass {dest['threshold']}")
    for t in dest["tokens"][:10]:
        print(f"    {t['token']!r:<18} {t['mean_mass']:.4f}")
    print()

    print("=== 3. category enrichment, against its base rate ===")
    print(f"  {enr['flagged_outcomes']}/{enr['n_outcomes']} outcomes flagged "
          f"= {enr['outcome_base_rate']:.1%} base rate")
    print(f"  top-{enr['top_k']} collapse pairs touching one: {enr['hits']}"
          f"/{enr['top_k']} = {enr['observed']:.0%}")
    print(f"  chance for a random pair: {enr['pair_chance_rate']:.0%}"
          f"  ->  {enr['enrichment']}x")
    print("  (on a ranking with no test-retest reliability -- see 1)")

    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(
            {"arm": args.arm, "n_models": len(models),
             "models": [m.replace("__", "/") for m in models],
             "reliability": rel, "destination": dest, "enrichment": enr},
            indent=2) + "\n")
        print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
