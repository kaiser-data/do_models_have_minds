"""Which cells exist, which do not, and what that costs the claims.

"All models tested on all conditions" is not a plan until it is a table. This
walks every results tree and reports the realised grid against the designed one,
so a gap is a printed row rather than something a reader has to notice.

    python3 scripts/coverage.py                    # -> site/coverage.json

The factors, per systematic-study's inventory:

    model     15 in the roster: 9 self-hosted, 4 hosted first-token scoreable,
              2 hosted reachable only under a prefill
    arm       R, N_plus, N_minus
    seed      3 design seeds
    prompt    ue and its variants
    harness   local transformers vs hosted API -- NOT a nuisance, a factor. Cells from
              the two never pool, and no model has yet been run through both,
              so harness is confounded with size across the whole study.

**A missing cell is not a small thing.** `fig1_state_space` draws each model as
a path R -> N_plus -> N_minus and silently skips any model without all three,
which is why every hosted model is absent from the paper's thesis figure. The
skip is correct; the silence is what this script removes.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from nullcard.roster import (NEBIUS, SELF_HOSTED, prefill_scoreable_hosted,  # noqa: E402
                             scoreable_hosted)

ARMS = ("R", "N_plus", "N_minus")
SEEDS = (20260815, 20260816, 20260817)
EXPECTED_ROWS = 5000

_CELL = re.compile(
    r"^(?P<model>.+?)__(?P<arm>R|N_plus|N_minus|MIXED)"
    r"(?:__s(?P<seed>\d+))?(?:__p(?P<prompt>[a-z_]+))?"
    r"(?:__(?P<persona>[a-z0-9-]+))?\.jsonl$")


def scan(tree: Path) -> dict:
    """-> {(model, arm, seed, prompt): rows} for baseline cells only."""
    out: dict[tuple, int] = {}
    if not tree.exists():
        return out
    for p in sorted(tree.glob("*.jsonl")):
        m = _CELL.match(p.name)
        if not m or m.group("persona"):        # persona/neutral cells excluded
            continue
        seed = int(m.group("seed")) if m.group("seed") else SEEDS[0]
        key = (m.group("model").replace("__", "/"), m.group("arm"), seed,
               m.group("prompt") or "ue")
        with open(p) as fh:
            out[key] = sum(1 for _ in fh)
    return out


def analyse(trees: dict[str, Path]) -> dict:
    cells = {name: scan(t) for name, t in trees.items()}
    roster = {
        "self_hosted": [m.hf_id for m in SELF_HOSTED],
        "hosted_direct": [m.api_id for m in scoreable_hosted()],
        "hosted_prefill": [m.api_id for m in prefill_scoreable_hosted()],
        "hosted_unreachable": [m.api_id for m in NEBIUS
                               if m.api_id not in {x.api_id for x in scoreable_hosted()}
                               and m.api_id not in {x.api_id for x in prefill_scoreable_hosted()}],
    }

    rows, gaps = [], []
    for group, models in roster.items():
        if group == "hosted_unreachable":
            continue
        tree = "results" if group == "self_hosted" else "results_hosted"
        for model in models:
            got = {(a, s) for (m, a, s, p), n in cells.get(tree, {}).items()
                   if m == model and p == "ue" and n >= EXPECTED_ROWS}
            per_arm = {a: sorted(s for (aa, s) in got if aa == a) for a in ARMS}
            complete_seeds = [s for s in SEEDS
                              if all((a, s) in got for a in ARMS)]
            row = {
                "model": model, "group": group,
                "seeds_by_arm": per_arm,
                "n_cells": len(got),
                "n_cells_designed": len(ARMS) * len(SEEDS),
                "seeds_with_all_arms": complete_seeds,
                "in_state_space_figure": bool(complete_seeds),
                "has_noise_floor": all(len(per_arm[a]) >= 3 for a in ("R", "N_minus")),
            }
            rows.append(row)
            for a in ARMS:
                missing = [s for s in SEEDS if s not in per_arm[a]]
                if missing:
                    gaps.append({"model": model, "arm": a, "group": group,
                                 "missing_seeds": missing})

    prompts = defaultdict(set)
    for tree, d in cells.items():
        for (m, a, s, p), n in d.items():
            if n >= EXPECTED_ROWS:
                prompts[p].add(m)

    return {
        "models": rows,
        "gaps": gaps,
        "roster": roster,
        "prompt_levels": {p: sorted(ms) for p, ms in sorted(prompts.items())},
        "summary": {
            "n_models_designed": sum(len(v) for k, v in roster.items()
                                     if k != "hosted_unreachable"),
            "n_models_in_figure": sum(1 for r in rows if r["in_state_space_figure"]),
            "n_models_with_floor": sum(1 for r in rows if r["has_noise_floor"]),
            "n_cells_present": sum(r["n_cells"] for r in rows),
            "n_cells_designed": sum(r["n_cells_designed"] for r in rows),
            "harness_overlap": sorted(
                set(roster["self_hosted"]) & set(roster["hosted_direct"])),
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="site/coverage.json")
    args = ap.parse_args()

    res = analyse({"results": Path("results"),
                   "results_hosted": Path("results_hosted"),
                   "results_v2": Path("results_v2")})

    print(f"{'model':<36}{'group':<16}{'R':>7}{'N+':>5}{'N-':>5}"
          f"{'fig1':>7}{'floor':>7}")
    print("-" * 83)
    for r in sorted(res["models"], key=lambda x: (x["group"], x["model"])):
        s = r["seeds_by_arm"]
        print(f"{r['model'].split('/')[-1][:35]:<36}{r['group']:<16}"
              f"{len(s['R']):>7}{len(s['N_plus']):>5}{len(s['N_minus']):>5}"
              f"{('yes' if r['in_state_space_figure'] else 'NO'):>7}"
              f"{('yes' if r['has_noise_floor'] else 'no'):>7}")

    s = res["summary"]
    print(f"\ncells {s['n_cells_present']} of {s['n_cells_designed']} designed"
          f"   ·   in fig1: {s['n_models_in_figure']} of {s['n_models_designed']}"
          f"   ·   with a noise floor: {s['n_models_with_floor']}")
    if not s["harness_overlap"]:
        print("\n  NO model has been run through both harnesses, so harness is\n"
              "  confounded with size across the whole study.")

    by_arm: dict[str, int] = defaultdict(int)
    for g in res["gaps"]:
        by_arm[g["arm"]] += len(g["missing_seeds"])
    if by_arm:
        print("\nmissing cells by arm: " +
              ", ".join(f"{a} {n}" for a, n in sorted(by_arm.items())))

    print("\nprompt levels realised:")
    for p, ms in res["prompt_levels"].items():
        print(f"  {p:<10} {len(ms)} model(s)")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2, sort_keys=True) + "\n")
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
