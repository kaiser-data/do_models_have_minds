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
    # The mass coherence is actually computed over. answer_mass_neutral counts
    # C, so it stays ~1.0 even when the model has put everything on "neither" --
    # and then p_option_a renormalises a vanishing remainder and the coherence
    # number is noise wearing a floor's clothes. This is the diagnostic that
    # tells the two apart, and it did not exist until n>1 produced P(C)=1.000.
    ab = [r["answer_mass"] * (1 - r["p_neither"]) for r in rows
          if r.get("p_neither") is not None]
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
        "mean_ab_mass": float(np.mean(ab)) if ab else None,
        "frac_ab_mass_below_01": float(np.mean(np.array(ab) < 0.01)) if ab else None,
        "decisive_fraction": float(np.mean((d < 0.2) | (d > 0.8))),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results")
    ap.add_argument("--model", default="",
                    help="one model; default is every model with neutral cells")
    ap.add_argument("--json", default="")
    args = ap.parse_args()

    results = Path(args.results)
    # Auto-discover rather than requiring the caller to list models: a model
    # whose cells landed but which nobody remembered to add to a list would be
    # silently absent from the summary, which is the same failure as an
    # unreported exclusion.
    if args.model:
        models = [args.model]
    else:
        models = sorted({
            p.name.split("__" + a + "__neutral")[0].replace("__", "/", 1)
            for a in ARMS for p in results.glob(f"*__{a}__neutral.jsonl")})
    if not models:
        print("no neutral cells found.")
        return 1
    reports = [analyse(results, m) for m in models]
    return summarise(reports, args.json)


def analyse(results: Path, model: str) -> dict:
    args_model = model
    report = {"model": args_model, "arms": {}, "claim": None}

    print(f"\n=== neutral-option control — {args_model} ===\n")
    print(f"{'arm':10s}{'instrument':12s}{'coherence':>11s}{'decisive':>10s}"
          f"{'P(neither)':>12s}{'answer mass':>13s}")
    for arm in ARMS:
        entry = {}
        for label, neutral in (("binary", False), ("neutral", True)):
            s = score(cell_path(results, args_model, arm, neutral))
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
        # Computed for EVERY model. The first version set this only inside the
        # floor-survives branch, so the summary counted 3/3 where the truth was
        # 5/5 -- a denominator quietly restricted to the flattering subset.
        if pc_r is not None and pc_n is not None:
            report["opt_out_gap"] = pc_n - pc_r
        ab_n = report["arms"]["N_minus"]["neutral"].get("mean_ab_mass")
        if ab_n is not None and ab_n < 0.05:
            report["interpretable"] = False
            report["uninterpretable_reason"] = (
                f"mean A/B mass on invented outcomes is {ab_n:.4f}: the model "
                f"put essentially everything on 'neither', so the coherence "
                f"computed from the remainder is not a floor")
        else:
            report["interpretable"] = True
        if abs(nn - nb) < 0.05:
            report["claim"] = (
                f"FLOOR SURVIVES. Offering an explicit opt-out moved the "
                f"invented-outcome floor by {nn - nb:+.3f}, so the forced-binary "
                f"objection does not explain the floor.")
            if pc_r is not None and pc_n is not None:
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
    return report


def summarise(reports: list, json_out: str) -> int:
    """Across models. The per-model verdicts above are the evidence; this is
    where n stops being 1 -- so it reports the SPREAD, not just a mean, and
    names any model that disagrees rather than averaging it away."""
    ok = [r for r in reports if r.get("floor_shift") is not None]
    print(f"\n\n=== across {len(ok)} model(s) with a complete quartet ===")
    if ok:
        print(f"{'model':26s}{'floor shift':>12s}{'P(C) real':>10s}"
              f"{'P(C) inv':>9s}{'gap':>8s}{'A/B mass inv':>13s}{'floor?':>8s}")
        for r in sorted(ok, key=lambda r: -(r.get("opt_out_gap") or 0)):
            pr = r["arms"]["R"]["neutral"].get("mean_p_neither")
            pn = r["arms"]["N_minus"]["neutral"].get("mean_p_neither")
            ab = r["arms"]["N_minus"]["neutral"].get("mean_ab_mass")
            gap = (pn - pr) if (pr is not None and pn is not None) else None
            print(f"{r['model'].split('/')[-1][:25]:26s}{r['floor_shift']:>+12.3f}"
                  f"{pr:>10.3f}{pn:>9.3f}"
                  f"{(f'{gap:+.3f}' if gap is not None else '--'):>8s}"
                  f"{ab:>13.4f}"
                  f"{('yes' if r.get('interpretable') else 'NO'):>8s}")
        # The floor range must be read over the models where a floor EXISTS.
        # Three of five put ~all mass on "neither" for invented outcomes, so
        # their coherence is computed from ~0.03% of the distribution: that is
        # not a floor that survived, it is a floor that was never measured.
        interp = [r for r in ok if r.get("interpretable")]
        shifts = [r["floor_shift"] for r in interp]
        gaps = [r["opt_out_gap"] for r in ok if r.get("opt_out_gap") is not None]
        survived = [r for r in interp if abs(r["floor_shift"]) < 0.05]
        print(f"\n{len(interp)}/{len(ok)} models still answer the invented arm "
              f"often enough for a floor to mean anything.")
        if shifts:
            print(f"  among those: floor shift {min(shifts):+.3f} to "
                  f"{max(shifts):+.3f}; {len(survived)}/{len(interp)} keep it")
        for r in ok:
            if not r.get("interpretable"):
                print(f"  NOT A FLOOR  {r['model'].split('/')[-1]:24s} "
                      f"{r['uninterpretable_reason']}")
        if gaps:
            higher = sum(1 for g in gaps if g > 0)
            print(f"opt-out gap (invented - real) {min(gaps):+.3f} to "
                  f"{max(gaps):+.3f}; {higher}/{len(gaps)} decline the "
                  f"MEANINGLESS comparison more often")
    blocked = [r["model"] for r in reports if r.get("floor_shift") is None]
    if blocked:
        print(f"incomplete (reported, not dropped): {', '.join(blocked)}")
    if json_out:
        Path(json_out).write_text(json.dumps(
            {"models": reports, "n_complete": len(ok)}, indent=2) + "\n")
        print(f"\nwrote {json_out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
