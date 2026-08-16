"""Does the floor survive changing only the question?

Spec: `docs/superpowers/specs/2026-08-16-v2-prompt-run-design.md` §2, §6.

Every coherence number this project reports was elicited with one wording ---
Utility Engineering's, quoted verbatim. That wording is therefore a factor with
exactly one realized level, and a factor with one level is confounded with
every accidental property of that instance. This script reads the two-level
version.

Holding the battery, pair set, design seed, scoring rule and serving stack
fixed, and varying only the question, it reports per model and per prompt:

    value     = coherence(R)
    floor     = coherence(N-)
    residual  = value - floor
    conviction= fraction of pairs answered decisively (p < 0.2 or p > 0.8)

The success condition is not a prettier residual. It is one sentence either
way. If the two wordings agree, the floor is not an artifact of one paper's
phrasing, which is the stronger result for everything already written. If they
disagree, the question is part of the instrument --- which is a methods finding
about preference elicitation and the more interesting outcome.

    python3 scripts/prompt_contrast.py --results results_v2

n = 2 models at 1 design seed: a demonstration that the protocol runs, not a
population estimate. No band is printed because one seed cannot support one.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from nullcard.scoring.analyze import (  # noqa: E402
    aggregate_pair_probabilities, cell_coherence, load_cell)
from scripts.build_card import parse_cell_name  # noqa: E402

N_SPLITS = 5
ARMS = ("R", "N_minus")
# Same threshold build_card.py uses, so "conviction" means one thing repo-wide.
DECISIVE_LO, DECISIVE_HI = 0.2, 0.8


def score_cell(path: Path) -> dict | None:
    rows = load_cell(path)
    if not rows:
        return None
    probs = aggregate_pair_probabilities(rows)
    if len(probs) < 10:
        return None
    accs = []
    for seed in range(N_SPLITS):
        try:
            accs.append(cell_coherence(probs, seed=seed)["held_out_accuracy"])
        except ValueError:
            continue
    if not accs:
        return None
    d = np.array(list(probs.values()))
    return {
        "n_rows": len(rows),
        "n_pairs": len(probs),
        "coherence": float(np.mean(accs)),
        "conviction": float(np.mean((d < DECISIVE_LO) | (d > DECISIVE_HI))),
        "mean_answer_mass": float(np.mean([r.get("answer_mass", 1.0) for r in rows])),
    }


def analyse(results_dir: Path) -> dict:
    cells: dict[tuple[str, str, str], dict] = {}
    for path in sorted(results_dir.glob("*.jsonl")):
        try:
            model, arm, _seed, persona, depth, prompt = parse_cell_name(path)
        except ValueError:
            continue
        if persona != "none" or depth != "D0" or arm not in ARMS:
            continue
        s = score_cell(path)
        if s:
            cells[(model, prompt, arm)] = s

    models = sorted({m for m, _, _ in cells})
    prompts = sorted({p for _, p, _ in cells})
    out = []
    for model in models:
        for prompt in prompts:
            hi, lo = cells.get((model, prompt, "R")), cells.get((model, prompt, "N_minus"))
            if not hi or not lo:
                continue
            out.append({
                "model": model, "prompt": prompt,
                "coherence_R": hi["coherence"], "coherence_N_minus": lo["coherence"],
                "residual": hi["coherence"] - lo["coherence"],
                "conviction_R": hi["conviction"],
                "conviction_N_minus": lo["conviction"],
                # The mechanism the paper attributes the flat residual to: the
                # metric keeps direction and discards strength. If conviction
                # collapses on N- under both wordings, that mechanism is not a
                # property of one paper's phrasing.
                "conviction_ratio": (hi["conviction"] / lo["conviction"]
                                     if lo["conviction"] > 0 else None),
                "answer_mass_R": hi["mean_answer_mass"],
                "answer_mass_N_minus": lo["mean_answer_mass"],
            })

    by_prompt = {}
    for prompt in prompts:
        rows = [r for r in out if r["prompt"] == prompt]
        if rows:
            by_prompt[prompt] = {
                "n_models": len(rows),
                "mean_residual": float(np.mean([r["residual"] for r in rows])),
                "mean_conviction_R": float(np.mean([r["conviction_R"] for r in rows])),
                "mean_conviction_N_minus":
                    float(np.mean([r["conviction_N_minus"] for r in rows])),
            }
    return {"cells": out, "by_prompt": by_prompt, "prompts": prompts,
            "n_design_seeds": 1}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results_v2")
    ap.add_argument("--out", default="site/prompt_contrast.json")
    args = ap.parse_args()

    res = analyse(Path(args.results))
    if not res["cells"]:
        print(f"no paired cells in {args.results}")
        return 1

    print(f"{'model':<26}{'prompt':>8}{'coh R':>9}{'coh N-':>9}{'residual':>10}"
          f"{'conv R':>9}{'conv N-':>9}{'ratio':>8}")
    print("-" * 88)
    for r in res["cells"]:
        ratio = r["conviction_ratio"]
        print(f"{r['model'].split('/')[-1][:25]:<26}{r['prompt']:>8}"
              f"{r['coherence_R']:>9.4f}{r['coherence_N_minus']:>9.4f}"
              f"{r['residual']:>+10.4f}{r['conviction_R']:>9.3f}"
              f"{r['conviction_N_minus']:>9.3f}"
              f"{(f'{ratio:.2f}x' if ratio else '-'):>8}")

    print()
    for prompt, s in res["by_prompt"].items():
        print(f"  {prompt:<4} mean residual {s['mean_residual']:+.4f}   "
              f"conviction R {s['mean_conviction_R']:.3f} vs "
              f"N- {s['mean_conviction_N_minus']:.3f}   (n={s['n_models']})")

    if len(res["prompts"]) == 2:
        a, b = res["prompts"]
        d = abs(res["by_prompt"][a]["mean_residual"]
                - res["by_prompt"][b]["mean_residual"])
        print(f"\nresidual moves {d:.4f} between wordings. One design seed, so "
              f"there is no\nnoise band to compare that against -- this "
              f"demonstrates the protocol, not a\npopulation effect.")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2, sort_keys=True) + "\n")
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
