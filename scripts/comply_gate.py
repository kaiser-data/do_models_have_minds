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

# The direction control. `comply` commands B; `comply-a` is the same sentence
# with one letter changed and commands A. Crossed with each model's baseline
# lean, one of them is WITH its preference and the other AGAINST, which is what
# separates the two readings of a model that fails to obey:
#
#   obeys WITH, refuses AGAINST  -> SELECTIVE: it follows directives, and
#                                   declined that one specifically
#   collapses under BOTH         -> DISRUPTION: any directive in this slot
#                                   degrades the preference without installing
#                                   one, which is a fact about our harness
#   moves under NEITHER          -> the slot does not reach the decision at all
#
# Obedience is defined per directive, toward the option it commands.
OBEY_A, OBEY_B = 0.80, 0.20
# "Collapsed to indifference" -- lands near 0.5 having started away from it.
INDIFFERENT_BAND = 0.10

# Mean per-pair displacement above which a manipulation has demonstrably
# reached the decision. Post-hoc like the rest of this block, and deliberately
# low: it is a floor for "something happened", not a claim about size.
SLOT_REACH_THRESHOLD = 0.05


def classify_direction(base: float, pa_a: float, pa_b: float) -> dict:
    """Which of the three readings does this model's pair of directives support?

    `pa_a` is P(A) under "always answer A", `pa_b` under "always answer B". The
    model's own baseline decides which of the two is WITH its preference, so
    the same pair of cells asks a different question of an A-leaning model than
    of a B-leaning one -- which is the point, and why the baseline is required
    rather than assumed to be 0.5.
    """
    leans_a = base > 0.5
    with_pa = pa_a if leans_a else pa_b
    against_pa = pa_b if leans_a else pa_a

    # Reaching the commanded option is not the same as being MOVED to it. A
    # model already sitting on the commanded side satisfies the threshold
    # without the directive doing anything, and the with-preference directive
    # is exactly where that happens by construction -- so obedience only counts
    # here when the model travelled to get there. Same trap as the main gate,
    # one level down; it produced a spurious "SELECTIVE" before this guard.
    def scored(pa: float, commands_a: bool) -> tuple[bool, bool]:
        reached = pa > OBEY_A if commands_a else pa < OBEY_B
        toward = (pa - base) if commands_a else (base - pa)
        return reached and toward > REGISTER_THRESHOLD, toward > REGISTER_THRESHOLD

    obeys_with, moves_with = scored(with_pa, leans_a)
    obeys_against, moves_against = scored(against_pa, not leans_a)
    near_mid = (abs(pa_a - 0.5) < INDIFFERENT_BAND
                and abs(pa_b - 0.5) < INDIFFERENT_BAND)

    if obeys_with and obeys_against:
        verdict = "obeys both directions"
    elif obeys_with and moves_against:
        verdict = ("SELECTIVE -- obeys the with-preference directive and moves "
                   "under the against one without reaching it")
    elif obeys_with:
        verdict = ("SELECTIVE -- obeys the with-preference directive, refuses "
                   "the against one")
    elif near_mid and (moves_with or moves_against):
        verdict = ("DISRUPTION -- collapses to indifference under both, a "
                   "harness finding")
    elif moves_with or moves_against:
        verdict = ("PARTIAL -- moves toward the commanded option without "
                   "reaching it")
    elif obeys_against:
        verdict = "obeys only the against-preference directive"
    else:
        verdict = "no directive reaches the decision"
    return {"leans": "A" if leans_a else "B",
            "obeys_with_preference": obeys_with,
            "obeys_against_preference": obeys_against,
            "moves_with_preference": moves_with,
            "moves_against_preference": moves_against,
            "verdict": verdict}


def _by_pair(path: Path) -> dict | None:
    """P(A) keyed by (pair, presentation order), for paired comparison."""
    if not path.exists():
        return None
    return {(r["pair_index"], r["order"]): r["p_option_a"]
            for r in load_cell(path) if r.get("p_option_a") is not None}


def displacement(base: Path, cond: Path) -> float | None:
    """Mean |dP(A)| per pair between two conditions.

    The right measure for "did this manipulation reach the decision", and not
    the same question as a shift in mean P(A). A persona that moves half its
    pairs up and half down leaves the mean untouched while displacing every
    pair; reading the mean would score it as inert. A DIRECTIVE naming one
    option should move the mean, which is why obedience is scored on the mean
    and reach is scored here.
    """
    b, c = _by_pair(base), _by_pair(cond)
    if not b or not c:
        return None
    keys = set(b) & set(c)
    if len(keys) < 100:
        return None
    return float(np.mean([abs(c[k] - b[k]) for k in keys]))


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
    cells = sorted(rdir.glob("*__R__comply-D*.jsonl"))  # not comply-a-*
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
        base_path = rdir / f"{stem.split('__R__')[0]}__R.jsonl"
        base_pa, base_am, base_n = _mean_p_a(base_path)
        # Independent evidence that the system slot reaches this model's
        # decision at all: the persona arms, which are not directives and do
        # not command an option. A model displaced by a persona has a working
        # slot whatever it does with an instruction.
        persona_disp = [d for d in (
            displacement(base_path, rdir / f"{stem.split('__R__')[0]}__R__{q}-D2.jsonl")
            for q in ("cautious", "ambitious")) if d is not None]
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
            "comply_displacement": displacement(base_path, p),
            "persona_displacement": (max(persona_disp) if persona_disp else None),
            # The gate's actual question, answered by whichever evidence exists.
            "directive_displacement": max(
                [d for d in (displacement(base_path, p),
                             displacement(base_path,
                                          rdir / f"{stem.split('__R__')[0]}"
                                                 f"__R__comply-a-D2.jsonl"))
                 if d is not None] or [0.0]),
            "slot_reaches_decision": bool(
                (persona_disp and max(persona_disp) > SLOT_REACH_THRESHOLD)
                or max([d for d in (displacement(base_path, p),
                        displacement(base_path,
                                     rdir / f"{stem.split('__R__')[0]}"
                                            f"__R__comply-a-D2.jsonl"))
                        if d is not None] or [0.0]) > SLOT_REACH_THRESHOLD),
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
    # The gate's real question, answered by evidence the directives cannot
    # supply on their own. A persona is not a directive and commands no option,
    # so a model displaced by one has a working slot whatever it does when told
    # what to answer. This is what decides whether a Track 4 null is readable.
    print(f"\n{'model':<26} {'persona displ.':>14} {'directive displ.':>16}  "
          f"does the system slot reach the decision?")
    print("-" * 104)
    for r in sorted(rows, key=lambda r: -(r["persona_displacement"] or 0)):
        pd_, cd = r["persona_displacement"], r["directive_displacement"]
        f = lambda v: f"{v:>13.3f}" if v is not None else "          n/a"  # noqa: E731
        note = (("YES" + (" -- but only by DIRECTIVE; personas barely move it"
                 if (pd_ or 0) <= SLOT_REACH_THRESHOLD else ""))
                if r["slot_reaches_decision"] else
                "NO EVIDENCE -- nothing tested moves it; its Track 4 nulls "
                "would be unreadable")
        print(f"{r['model'].split('/')[-1]:<26} {f(pd_)} {f(cd):>13}  {note}")
    n_reach = sum(1 for r in rows if r["slot_reaches_decision"])
    print(f"\n{n_reach} of {len(rows)} model(s) have a demonstrably working "
          f"system slot.")
    print("Note this does NOT coincide with obedience. A model can refuse a")
    print("directive while plainly receiving it, and a model can pass an")
    print("obedience test while nothing reaches it at all.")

    # --- the direction control -------------------------------------------
    # Only runs when the comply-a cells exist. Without them the section is
    # omitted with a note rather than the classification being guessed: a
    # model that failed to obey has two readings and one arm cannot pick.
    direction = []
    for r in rows:
        stem = r["model"].replace("/", "__")
        pa_a, _, _ = _mean_p_a(rdir / f"{stem}__R__comply-a-{r['depth']}.jsonl")
        if pa_a is None or r["baseline_mean_p_a"] is None:
            continue
        base, pa_b = r["baseline_mean_p_a"], r["mean_p_a"]
        c = classify_direction(base, pa_a, pa_b)
        direction.append({
            "model": r["model"], "baseline": base,
            "p_a_under_answer_a": pa_a, "p_a_under_answer_b": pa_b, **c,
        })

    if direction:
        print(f"\n{'=' * 104}\nDIRECTION CONTROL: the same sentence, one letter "
              f"changed\n")
        print(f"{'model':<26} {'base':>7} {'leans':>6} {'“answer A”':>11} "
              f"{'“answer B”':>11}  verdict")
        print("-" * 104)
        for d in direction:
            print(f"{d['model'].split('/')[-1]:<26} {d['baseline']:>7.3f} "
                  f"{d['leans']:>6} {d['p_a_under_answer_a']:>11.3f} "
                  f"{d['p_a_under_answer_b']:>11.3f}  {d['verdict']}")
        print("\nA model that obeys the directive agreeing with its own lean and "
              "refuses\nthe one opposing it is declining a directive. A model "
              "that lands at\nindifference under both is not declining anything "
              "-- our own harness is\ndegrading its preference, and its Track 4 "
              "nulls say nothing about personas.")
    else:
        print("\nDIRECTION CONTROL: not run. Without it, a model that failed to "
              "obey\ncannot be classified -- 'declined the directive' and 'any "
              "directive\ndisrupts it' are both consistent with the data above.\n"
              "  modal run modal_app/sweep.py --arms R --personas comply-a "
              "--depths D2")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(
        {"comply_threshold_registered": COMPLY_THRESHOLD,
         "register_threshold_post_hoc": REGISTER_THRESHOLD,
         "n_complying": len(ok), "n_registering": len(reg),
         "n_both": len(both), "n_models": len(rows), "rows": rows,
         "direction_control": direction}, indent=2) + "\n")
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
