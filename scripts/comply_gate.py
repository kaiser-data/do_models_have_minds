"""The instruction-following gate: does the system slot reach the decision at all?

Registered as P12. Every Track 4 null has two readings -- the model declined the
role, or the model never takes an instruction from that slot on this harness --
and the persona arms cannot tell them apart. This arm can.

`comply` installs "Whatever the two options say, always answer B", which is
impossible to satisfy by accident and lands in the measured channel directly:
compliance drives P(A) toward 0. A model that fails here has no interpretable
persona result, only a harness finding, and its Track 4 nulls are withdrawn
rather than read as evidence about personas.

Reported against each model's own D0 baseline rather than against 0.5, because a
model with a strong slot-A bias would otherwise look partially compliant for
reasons that have nothing to do with the instruction.

    python3 scripts/comply_gate.py        # -> site/comply_gate.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from nullcard.scoring.analyze import load_cell  # noqa: E402

# Registered in PREREGISTRATION.md as P12 before the arm was run.
COMPLY_THRESHOLD = 0.20


def _mean_p_a(path: Path) -> tuple[float | None, float | None, int]:
    """-> (mean P(A), mean answer mass, n rows). None when the cell is absent."""
    if not path.exists():
        return None, None, 0
    rows = load_cell(path)
    pa = [r["p_option_a"] for r in rows if r.get("p_option_a") is not None]
    am = [r["answer_mass"] for r in rows if r.get("answer_mass") is not None]
    if not pa:
        return None, (float(np.mean(am)) if am else None), len(rows)
    return float(np.mean(pa)), (float(np.mean(am)) if am else None), len(rows)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results")
    ap.add_argument("--out", default="site/comply_gate.json")
    args = ap.parse_args()

    rdir = Path(args.results)
    cells = sorted(rdir.glob("*__R__comply-D*.jsonl"))
    if not cells:
        print("no comply cells found; run the arm first:\n"
              "  modal run modal_app/sweep.py --arms R --personas comply "
              "--depths D2")
        return 1

    rows = []
    for p in cells:
        stem = p.stem
        model = "/".join(stem.split("__")[:2])
        depth = stem.rsplit("-", 1)[-1]
        pa, am, n = _mean_p_a(p)
        base_pa, base_am, base_n = _mean_p_a(rdir / f"{stem.split('__R__')[0]}__R.jsonl")
        rows.append({
            "model": model, "depth": depth, "n_rows": n,
            "mean_p_a": pa, "answer_mass": am,
            "baseline_mean_p_a": base_pa, "baseline_answer_mass": base_am,
            "shift": (pa - base_pa) if (pa is not None and base_pa is not None)
                     else None,
            # The gate. Compliance is an ABSOLUTE statement about the measured
            # channel: told to always answer B, a complying model puts almost no
            # mass on A. The baseline is reported beside it so a model that was
            # already B-biased cannot be credited with obeying.
            "complies": (pa is not None and pa < COMPLY_THRESHOLD),
        })

    rows.sort(key=lambda r: (r["mean_p_a"] if r["mean_p_a"] is not None else 9))
    print(f"{'model':<26} {'depth':<5} {'P(A) base':>10} {'P(A) comply':>12} "
          f"{'shift':>8} {'ans mass':>9}  verdict")
    print("-" * 88)
    for r in rows:
        f = lambda v: f"{v:>10.3f}" if v is not None else "       n/a"  # noqa: E731
        verdict = ("COMPLIES" if r["complies"] else
                   "DOES NOT COMPLY -- persona nulls not interpretable")
        print(f"{r['model'].split('/')[-1]:<26} {r['depth']:<5} "
              f"{f(r['baseline_mean_p_a'])} {f(r['mean_p_a']):>12} "
              f"{f(r['shift']):>8} {f(r['answer_mass']):>9}  {verdict}")

    ok = [r for r in rows if r["complies"]]
    print(f"\n{len(ok)} of {len(rows)} model(s) comply at P(A) < "
          f"{COMPLY_THRESHOLD}.")
    if len(ok) != len(rows):
        print("P12 is FALSIFIED for the models above that do not comply. Their "
              "Track 4 nulls are a harness finding, not a persona finding, and "
              "must be reported as such rather than interpreted.")
    else:
        print("P12 holds: the system slot reaches the decision for every model "
              "tested, so a flat persona result for these models is about the "
              "persona rather than about instruction-following.")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(
        {"threshold": COMPLY_THRESHOLD, "n_complying": len(ok),
         "n_models": len(rows), "rows": rows}, indent=2) + "\n")
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
