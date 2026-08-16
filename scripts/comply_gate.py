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

# POST-HOC, and labelled as such wherever it is printed. The registered
# criterion above turned out to be the wrong operationalisation of the thing the
# gate exists to measure, and the data is what revealed it -- in both directions
# at once:
#
#   Qwen3.5-2B   FAILS the registered test while plainly registering the
#                instruction: P(A) 0.725 -> 0.465, a -0.260 shift that wipes out
#                a strong A-preference and leaves 63% of pairs near-indifferent.
#                It heard the instruction and did not obey it.
#   LFM2.5-1.2B  PASSES the registered test having barely moved (-0.047),
#                because its baseline P(A) was already 0.068 -- it was answering
#                B on ~93% of pairs before being told to. The instruction is
#                credited with behaviour it did not cause.
#
# The gate's PURPOSE is "does the system slot reach the decision?", because that
# is what makes a null persona result interpretable. That is registration, not
# obedience. Obedience is a stronger property and the one that got registered.
# Both are reported; neither silently replaces the other.
REGISTER_THRESHOLD = 0.10


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
            # The registered criterion: told to always answer B, an obeying
            # model puts almost no mass on A.
            "complies": (pa is not None and pa < COMPLY_THRESHOLD),
            # The post-hoc one the gate actually needs: did the instruction
            # reach the decision at all? A model already answering B cannot
            # demonstrate this, and a model that collapses to indifference
            # demonstrates it without obeying.
            "registers": (pa is not None and base_pa is not None
                          and abs(pa - base_pa) > REGISTER_THRESHOLD),
        })

    rows.sort(key=lambda r: (r["mean_p_a"] if r["mean_p_a"] is not None else 9))
    print(f"{'model':<26} {'P(A) base':>10} {'P(A) comply':>12} {'shift':>8} "
          f"{'obeys':>6} {'regs':>5}  what happened")
    print("-" * 104)
    for r in rows:
        f = lambda v: f"{v:>10.3f}" if v is not None else "       n/a"  # noqa: E731
        what = ("obeyed" if r["complies"] and r["registers"] else
                "obeyed trivially -- was ALREADY answering B before being told"
                if r["complies"] else
                "REGISTERED but did not obey -- collapsed toward indifference"
                if r["registers"] else "no detectable effect")
        print(f"{r['model'].split('/')[-1]:<26} {f(r['baseline_mean_p_a'])} "
              f"{f(r['mean_p_a']):>12} {f(r['shift']):>8} "
              f"{str(r['complies']):>6} {str(r['registers']):>5}  {what}")

    ok = [r for r in rows if r["complies"]]
    reg = [r for r in rows if r["registers"]]
    both = [r for r in rows if r["complies"] and r["registers"]]
    print(f"\nREGISTERED criterion (P12, P(A) < {COMPLY_THRESHOLD}): "
          f"{len(ok)} of {len(rows)} pass.")
    if len(ok) != len(rows):
        print("  P12 is FALSIFIED as registered.")
    print(f"POST-HOC criterion (instruction moved P(A) by > "
          f"{REGISTER_THRESHOLD}): {len(reg)} of {len(rows)} pass.")
    print(f"Both: {len(both)} of {len(rows)}.\n")
    print("The two disagree in BOTH directions, which is why both are printed:")
    print("  a model can register the instruction and refuse it, and a model")
    print("  already answering B passes an obedience test it never took.")
    print("Only the models passing BOTH have a demonstrated, non-trivial route")
    print("from the system slot to the decision. For the others a flat Track 4")
    print("persona result is a harness finding, not a persona finding.")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(
        {"comply_threshold_registered": COMPLY_THRESHOLD,
         "register_threshold_post_hoc": REGISTER_THRESHOLD,
         "n_complying": len(ok), "n_registering": len(reg),
         "n_both": len(both), "n_models": len(rows), "rows": rows}, indent=2) + "\n")
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
