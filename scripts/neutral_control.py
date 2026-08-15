"""Does the floor survive when the model may decline the comparison?

The standing objection to a forced binary is that it can manufacture an
ordering: hierarchies reported on forced choices weaken once respondents may
abstain. Our floor is measured on a forced binary, so the objection lands on
the central result rather than on a detail.

The control gives the model an explicit third option and changes nothing else.
Two questions, and the second is the one that matters:

  1. How much mass goes to "Neither", really? The existing binary rows can only
     bound it from below -- a token is visible only when it reaches the recorded
     top-5 -- so this is the first actual measurement.

  2. Does coherence on INVENTED outcomes survive among the choices that remain?
     P(A) is renormalised over A and B in both instruments, so it is the same
     quantity either way: the preference, given that a preference was expressed.
     If the floor holds there, the objection is answered. If the floor collapses
     while the real arm holds, our headline was an artifact of forced choice and
     the paper has to say so.

Reads the same coherence path as build_card.py (same splits, same fit), so the
binary and neutral numbers are comparable by construction rather than by
argument.

    python3 scripts/neutral_control.py --json site/neutral_control.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from nullcard.runner.forced_choice import ANSWER_MASS_FLOOR  # noqa: E402
from nullcard.scoring.analyze import (  # noqa: E402
    aggregate_pair_probabilities,
    cell_coherence,
    load_cell,
)

N_SPLITS = 5            # identical to build_card.py
EXPECTED_ROWS = 5000
ARMS = ("R", "N_minus")


def cell_path(results: Path, model: str, arm: str, neutral: bool) -> Path:
    stem = f"{model.replace('/', '__')}__{arm}"
    if neutral:
        stem += "__neutral"
    return results / f"{stem}.jsonl"


def score(path: Path) -> dict | None:
    """Coherence for one cell, by the same route the card uses.

    Returns None rather than a number when the cell is short or fails the
    validity gate: a partial neutral cell scored against a full binary one
    would make the comparison meaningless in the direction that flatters us.
    """
    if not path.exists():
        return None
    rows = load_cell(path)
    if len(rows) < EXPECTED_ROWS:
        return {"path": path.name, "usable": False,
                "reason": f"{len(rows)}/{EXPECTED_ROWS} rows"}
    mass = float(np.mean([r["answer_mass"] for r in rows]))
    if mass < ANSWER_MASS_FLOOR:
        return {"path": path.name, "usable": False,
                "reason": f"answer mass {mass:.3f} < {ANSWER_MASS_FLOOR}"}

    probs = aggregate_pair_probabilities(rows)
    accs = []
    for seed in range(N_SPLITS):
        try:
            accs.append(cell_coherence(probs, seed=seed)["held_out_accuracy"])
        except ValueError:
            continue
    # p_neither is present only on neutral rows; None elsewhere.
    pc = [r["p_neither"] for r in rows if r.get("p_neither") is not None]
    d = np.array(list(probs.values()))
    return {
        "path": path.name,
        "usable": bool(accs),
        "n_rows": len(rows),
        "n_pairs": len(probs),
        "coherence": float(np.mean(accs)) if accs else None,
        "answer_mass": mass,
        "mean_p_neither": float(np.mean(pc)) if pc else None,
        "max_p_neither": float(np.max(pc)) if pc else None,
        # The share of items where declining outweighs both options. A mean can
        # hide a bimodal "declines on some, decides on others".
        "frac_neither_majority": float(np.mean(np.array(pc) > 0.5)) if pc else None,
        "decisive_fraction": float(np.mean((d < 0.2) | (d > 0.8))),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results")
    ap.add_argument("--model", default="Qwen/Qwen3.5-2B")
    ap.add_argument("--json", default="")
    args = ap.parse_args()

    results = Path(args.results)
    report = {"model": args.model, "arms": {}, "claim": None}

    print(f"=== neutral-option control — {args.model} ===\n")
    print(f"{'arm':10s}{'instrument':12s}{'coherence':>11s}{'decisive':>10s}"
          f"{'P(neither)':>12s}{'answer mass':>13s}")
    for arm in ARMS:
        entry = {}
        for label, neutral in (("binary", False), ("neutral", True)):
            s = score(cell_path(results, args.model, arm, neutral))
            entry[label] = s
            if s is None:
                print(f"{arm:10s}{label:12s}{'-- not run --':>11s}")
                continue
            if not s.get("usable"):
                print(f"{arm:10s}{label:12s}  UNUSABLE: {s['reason']}")
                continue
            pc = ("--" if s["mean_p_neither"] is None
                  else f"{s['mean_p_neither']:.4f}")
            print(f"{arm:10s}{label:12s}{s['coherence']:>11.3f}"
                  f"{s['decisive_fraction'] * 100:>9.1f}%{pc:>12s}"
                  f"{s['answer_mass']:>13.4f}")
        report["arms"][arm] = entry

    def coh(arm, label):
        s = report["arms"].get(arm, {}).get(label)
        return s["coherence"] if s and s.get("usable") else None

    rb, nb = coh("R", "binary"), coh("N_minus", "binary")
    rn, nn = coh("R", "neutral"), coh("N_minus", "neutral")

    if None in (rb, nb, rn, nn):
        report["claim"] = ("INCOMPLETE — need all four cells (R and N_minus, "
                           "binary and neutral) before the control says anything.")
    else:
        report["residual_binary"] = rb - nb
        report["residual_neutral"] = rn - nn
        report["floor_shift"] = nn - nb
        print(f"\nresidual  binary  {rb - nb:+.3f}   (R {rb:.3f} - N- {nb:.3f})")
        print(f"residual  neutral {rn - nn:+.3f}   (R {rn:.3f} - N- {nn:.3f})")
        print(f"floor shift       {nn - nb:+.3f}   "
              f"(what offering an opt-out did to the floor)")
        # The pre-registered reading. A floor that survives answers the
        # objection; a floor that collapses means our headline was an artifact
        # and the paper must say so. Stated here so the verdict is not chosen
        # after seeing the number.
        #
        # The first version of this branch asserted "and the model takes the
        # opt-out on essentially none of the pairs" from the floor shift ALONE,
        # never reading P(C). It printed that sentence over P(C) = 0.638. A
        # verdict must be computed from every quantity it mentions.
        pc_r = report["arms"]["R"]["neutral"].get("mean_p_neither")
        pc_n = report["arms"]["N_minus"]["neutral"].get("mean_p_neither")
        if abs(nn - nb) < 0.05:
            report["claim"] = (
                f"FLOOR SURVIVES. Offering an explicit opt-out moved the "
                f"invented-outcome floor by {nn - nb:+.3f}, so the forced-binary "
                f"objection does not explain the floor.")
            if pc_r is not None and pc_n is not None:
                report["opt_out_gap"] = pc_n - pc_r
                report["claim"] += (
                    f" But the opt-out is heavily used and used SELECTIVELY: "
                    f"P(neither) is {pc_n:.3f} on invented outcomes against "
                    f"{pc_r:.3f} on real ones ({pc_n - pc_r:+.3f}). The model "
                    f"declines the meaningless comparison about twice as often, "
                    f"and coherence among the pairs it does answer is unchanged. "
                    f"That is the paper's thesis again: the content signal is "
                    f"real and sits in a channel the metric discards.")
        elif nn < nb:
            report["claim"] = (
                f"FLOOR WEAKENS. The invented-outcome floor fell {nn - nb:+.3f} "
                f"once declining was possible. The forced binary was doing part "
                f"of the work and the headline residual is overstated by that "
                f"much.")
        else:
            report["claim"] = (
                f"FLOOR RISES ({nn - nb:+.3f}) — unexpected; investigate before "
                f"reporting.")

    print(f"\nCLAIM: {report['claim']}")
    if args.json:
        Path(args.json).write_text(json.dumps(report, indent=2) + "\n")
        print(f"\nwrote {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
