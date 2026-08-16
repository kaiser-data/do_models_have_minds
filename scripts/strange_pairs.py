"""Find the pairs where the small models behave strangely, to spend big-model calls on.

Running full 5,000-row cells on hosted models costs 20,000 API calls to learn
one number per cell. Most of those pairs are ones every model answers the same
easy way ($100 over $1) and which no one is confused by. The information is
concentrated in a small set of items, and we already have nine models' answers
telling us which ones.

**The criteria are deliberately non-circular.** The obvious definition of
strange -- "the model chose against its fitted utility" -- is unusable here,
because the utility is fitted FROM these choices. A large residual is then
partly a statement about the fit, and ranking by it selects for whatever the
Thurstonian model happens to explain badly. Everything below is computed from
raw responses only:

1. **positional** -- the same *slot* wins in both presentation orders. With
   counterbalancing, p(A|AB) + p(A|BA) should sum to about 1 if the model is
   reading content. Near 2 or near 0 means position decided it, and the pair is
   measuring layout rather than preference.

2. **contested** -- the nine models split hardest. High cross-model variance on
   an item where each model is individually confident is the signature of a
   comparison whose answer depends on the model rather than the outcomes.

3. **mass_collapse** -- answer mass falls on this specific pair. The models stop
   putting a choice in the first token here, which is the same failure that
   makes six of ten frontier models unscoreable -- but item-level rather than
   model-level, and testable on models that ARE scoreable overall.

Each is a different way for the instrument to fail, so they are ranked
separately rather than blended into one score that would hide which is which.

    python3 scripts/strange_pairs.py --top 20
    python3 scripts/strange_pairs.py --top 20 --out battery/strange_pairs.json
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def load_arm(results: Path, arm: str) -> dict[str, list[dict]]:
    """Baseline cells only -- persona cells would confound the selection."""
    cells = {}
    for p in sorted(results.glob(f"*__{arm}.jsonl")):
        if "-D" in p.stem or "__s" in p.stem:
            continue
        model = p.stem[: -(len(arm) + 2)].replace("__", "/")
        with open(p) as fh:
            cells[model] = [json.loads(line) for line in fh]
    return cells


def score_pairs(cells: dict[str, list[dict]]) -> dict[int, dict]:
    """Per pair_index, the three strangeness measures plus what it is about."""
    by_pair: dict[int, dict[str, dict[str, dict]]] = defaultdict(
        lambda: defaultdict(dict))
    outcomes: dict[int, tuple[int, int]] = {}
    for model, rows in cells.items():
        for r in rows:
            by_pair[r["pair_index"]][model][r["order"]] = r
            if r["order"] == "AB":
                outcomes[r["pair_index"]] = (r["slot_a_outcome"],
                                             r["slot_b_outcome"])

    out = {}
    for k, per_model in by_pair.items():
        pos, first_slot, masses = [], [], []
        for model, orders in per_model.items():
            ab, ba = orders.get("AB"), orders.get("BA")
            if not ab or not ba:
                continue
            masses.extend([ab["answer_mass"], ba["answer_mass"]])
            if ab["p_option_a"] is None or ba["p_option_a"] is None:
                continue
            # p(slot A wins) in each order. Content-driven answers sum to ~1.
            pos.append(abs(ab["p_option_a"] + ba["p_option_a"] - 1.0))
            # p(the SAME outcome wins), order-averaged: content preference.
            first_slot.append((ab["p_option_a"] + (1 - ba["p_option_a"])) / 2)
        if len(first_slot) < 2:
            continue
        out[k] = {
            "pair_index": k,
            "outcomes": outcomes.get(k),
            "n_models": len(first_slot),
            "positional": round(statistics.mean(pos), 4) if pos else None,
            "contested": round(statistics.pstdev(first_slot), 4),
            "mean_preference": round(statistics.mean(first_slot), 4),
            "mass_collapse": round(1.0 - statistics.mean(masses), 4),
        }
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results")
    ap.add_argument("--arm", default="R")
    ap.add_argument("--battery", default="battery/outcomes_3arm.json")
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    cells = load_arm(Path(args.results), args.arm)
    if not cells:
        print(f"no {args.arm} baseline cells in {args.results}")
        return 1
    scored = score_pairs(cells)
    print(f"{len(cells)} models, {len(scored)} pairs scored on arm {args.arm}\n")

    texts = None
    bp = Path(args.battery)
    if bp.exists():
        texts = [row["text"] for row in json.loads(bp.read_text())["arms"]["R"]]

    def show(key: str, blurb: str, reverse=True):
        print(f"=== {key} — {blurb} ===")
        ranked = [v for v in scored.values() if v[key] is not None]
        ranked.sort(key=lambda v: v[key], reverse=reverse)
        for v in ranked[: args.top]:
            print(f"  pair {v['pair_index']:>5}  {key}={v[key]:+.3f}  "
                  f"pref={v['mean_preference']:.2f}  n={v['n_models']}")
            if texts and v["outcomes"]:
                a, b = v["outcomes"]
                print(f"        A: {texts[a][:88]}")
                print(f"        B: {texts[b][:88]}")
        print()
        return [v["pair_index"] for v in ranked[: args.top]]

    sel = {
        "positional": show("positional",
                           "same SLOT wins both orders; position decided it"),
        "contested": show("contested",
                          "the nine models disagree most"),
        "mass_collapse": show("mass_collapse",
                              "models stop answering in the first token here"),
    }

    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        payload = {"arm": args.arm, "n_models": len(cells),
                   "models": sorted(cells), "selected": sel,
                   "scores": {str(k): v for k, v in scored.items()}}
        out.write_text(json.dumps(payload, indent=2) + "\n")
        print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
