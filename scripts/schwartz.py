"""Do four value personas reorganise preferences the way the instrument predicts?

`cautious` and `ambitious` were written by us, so the numbers they produce have
no shape they are supposed to have. Schwartz's values do: they sit on a
circumplex with two bipolar higher-order axes, and values at opposite poles are
theorised to conflict. That gives a prediction an ad-hoc persona set cannot
have, and therefore something to be wrong about.

At four values the full circumplex cannot be recovered, so the prediction
degrades to a sign test on the two opposed pairs:

    corr( displacement[Power], displacement[Universalism] )      < 0
    corr( displacement[Self-Direction], displacement[Security] ) < 0
    cross-axis pairs                                             ~ 0

**And then the move this project exists to make.** The same test on the invented
arm. If opposed values anti-correlate only on real outcomes, the personas
reorganised something that needed the outcomes to mean something. If the same
geometry appears on outcomes that refer to nothing, the recovered "value
structure" is structure in the persona texts, reflected back -- which is this
paper's central argument applied to a real psychological instrument.

    python3 scripts/schwartz.py        # -> site/schwartz.json
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.persona_depth import utility  # noqa: E402
from nullcard.scoring.analyze import load_cell  # noqa: E402

VALUES = ("sch-power", "sch-universalism", "sch-selfdirection", "sch-security")
# Predicted to conflict, from the two higher-order axes. Declared here rather
# than discovered: the point of borrowing an instrument is that the structure
# comes with it.
OPPOSED = (("sch-power", "sch-universalism"),
           ("sch-selfdirection", "sch-security"))


def displacement_vector(results: Path, stem: str, arm: str,
                        persona: str) -> np.ndarray | None:
    """Per-outcome shift in fitted utility, persona minus baseline.

    z-scored on both sides before differencing, because a Thurstonian fit
    carries an arbitrary location and scale per run -- differencing raw fits
    would measure the optimiser's choice of origin as much as the persona's
    effect.
    """
    base = results / f"{stem}__{arm}.jsonl"
    cond = results / f"{stem}__{arm}__{persona}-D2.jsonl"
    if not base.exists() or not cond.exists():
        return None
    rows = load_cell(base)
    outs = sorted({r["slot_a_outcome"] for r in rows}
                  | {r["slot_b_outcome"] for r in rows})
    ub, uc = utility(base, outs), utility(cond, outs)
    if ub is None or uc is None:
        return None

    def _z(v):
        v = np.asarray(v, dtype=float)
        s = np.nanstd(v)
        return (v - np.nanmean(v)) / s if s > 0 else v * np.nan

    return _z(uc) - _z(ub)


def analyse(results: Path) -> dict:
    stems = sorted({p.stem.split("__R__")[0] for p in
                    results.glob(f"*__R__{VALUES[0]}-D2.jsonl")})
    out = {"models": [], "arms": {}}
    for arm in ("R", "N_minus"):
        rows = []
        for stem in stems:
            vecs = {v: displacement_vector(results, stem, arm, v) for v in VALUES}
            if any(x is None for x in vecs.values()):
                continue
            corr = {}
            for a, b in itertools.combinations(VALUES, 2):
                ok = np.isfinite(vecs[a]) & np.isfinite(vecs[b])
                corr[f"{a}|{b}"] = (float(np.corrcoef(vecs[a][ok], vecs[b][ok])[0, 1])
                                    if ok.sum() > 10 else None)
            opp = [corr[f"{a}|{b}"] for a, b in OPPOSED if corr.get(f"{a}|{b}") is not None]
            cross = [v for k, v in corr.items()
                     if v is not None and tuple(k.split("|")) not in OPPOSED]
            rows.append({
                "model": stem.replace("__", "/"), "correlations": corr,
                "mean_opposed": float(np.mean(opp)) if opp else None,
                "mean_cross_axis": float(np.mean(cross)) if cross else None,
                "both_opposed_negative": bool(opp and all(v < 0 for v in opp)),
            })
        out["arms"][arm] = rows
    out["models"] = [r["model"] for r in out["arms"].get("R", [])]
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results")
    ap.add_argument("--out", default="site/schwartz.json")
    args = ap.parse_args()

    data = analyse(Path(args.results))
    if not data["arms"].get("R"):
        print("no Schwartz persona cells found; run the arm first:\n"
              "  modal run modal_app/sweep.py --arms R,N_minus "
              "--personas sch-power,sch-universalism,sch-selfdirection,"
              "sch-security --depths D2")
        return 1

    print("Do values the instrument says CONFLICT displace preferences "
          "oppositely?\n")
    print(f"{'arm':<10} {'model':<24} {'opposed pairs':>14} {'cross-axis':>12}  "
          f"both < 0?")
    print("-" * 78)
    for arm, label in (("R", "real"), ("N_minus", "invented")):
        for r in data["arms"].get(arm, []):
            mo, mc = r["mean_opposed"], r["mean_cross_axis"]
            print(f"{label:<10} {r['model'].split('/')[-1]:<24} "
                  f"{(f'{mo:+.3f}' if mo is not None else 'n/a'):>14} "
                  f"{(f'{mc:+.3f}' if mc is not None else 'n/a'):>12}  "
                  f"{'yes' if r['both_opposed_negative'] else 'no'}")

    def summary(arm):
        rows = data["arms"].get(arm, [])
        vals = [r["mean_opposed"] for r in rows if r["mean_opposed"] is not None]
        return (float(np.mean(vals)) if vals else None,
                sum(1 for r in rows if r["both_opposed_negative"]), len(rows))

    (r_mean, r_n, r_tot) = summary("R")
    (n_mean, n_n, n_tot) = summary("N_minus")
    print(f"\nreal arm     mean opposed-pair correlation {r_mean:+.3f}; "
          f"{r_n}/{r_tot} models have both pairs negative")
    if n_tot:
        print(f"invented arm mean opposed-pair correlation {n_mean:+.3f}; "
              f"{n_n}/{n_tot} models have both pairs negative")
        print("\nThe comparison that matters is between those two lines.")
        if r_mean is not None and n_mean is not None:
            if r_mean < -0.1 and n_mean > r_mean + 0.2:
                print("The predicted geometry appears on real outcomes and is "
                      "much weaker on\ninvented ones: the personas reorganised "
                      "something that needed meaning.")
            elif r_mean < -0.1:
                print("The predicted geometry appears on BOTH arms. It is then "
                      "a property of\nthe persona texts, not of installed "
                      "values -- structure reflected back.")
            else:
                print("The predicted geometry does not appear on the real arm "
                      "either, so this\ninstrument does not reproduce the "
                      "circumplex at all and neither reading\nis available.")
    else:
        print("\nNo invented-arm cells. Without them the real-arm result cannot "
              "distinguish\ninstalled values from persona-text geometry, which "
              "is the whole question.")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2) + "\n")
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
