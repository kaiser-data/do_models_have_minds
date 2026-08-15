"""Cross-model comparison: who behaves differently, and along which axis.

Every other script in this repo answers one question across models. This one
puts the per-model answers side by side, because the interesting structure in
this project is not "what is the mean" but "which models are unlike the others,
and is the unlikeness the same unlikeness each time".

It is a descriptive tool and it is deliberately not a significance test. With
n = 9 models on one outcome set, a correlation across models is a hypothesis
generator, not evidence; the output is written so that reading it as evidence
is awkward. Each block prints its own n.

    python3 scripts/cross_model.py            # table + the axes it suggests
    python3 scripts/cross_model.py --json site/cross_model.json
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def corr(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if sx == 0 or sy == 0:
        return None
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy)


def load(path, default=None):
    p = Path(path)
    return json.loads(p.read_text()) if p.exists() else default


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--card", default="card.json")
    ap.add_argument("--depth", default="site/persona_depth.json")
    ap.add_argument("--validity", default="site/persona_validity.json")
    ap.add_argument("--neutral", default="site/neutral_control.json")
    ap.add_argument("--json", default="")
    args = ap.parse_args()

    from nullcard.roster import SELF_HOSTED
    sizes = {m.hf_id: m.params_b for m in SELF_HOSTED}
    fams = {m.hf_id: m.family for m in SELF_HOSTED}

    card = load(args.card)
    tiles = [t for t in card["tiles"] if t["badge"] == "FLOOR_CORRECTED"]
    per: dict[str, dict] = {}
    for t in tiles:
        per[t["model"]] = {
            "model": t["model"], "params_b": sizes.get(t["model"]),
            "family": fams.get(t["model"]),
            "coh_real": t["raw_coherence"], "coh_inv": t["floor"],
            "residual": t["value"],
            "decisive_real": t["decisive_fraction"]["R"],
            "decisive_inv": t["decisive_fraction"]["N_minus"],
            "answer_mass_real": t.get("mean_answer_mass"),
        }

    # Persona depth: D1 (user turn) vs D2 (system prompt), the comparison the
    # design was built to make. Averaged over the two traits per model.
    depth = load(args.depth, [])
    for r in depth:
        e = per.setdefault(r["model"], {"model": r["model"]})
        e.setdefault("depth_fc", {}).setdefault(r["depth"], []).append(r["floor_corrected"])
        e.setdefault("depth_real", {}).setdefault(r["depth"], []).append(r["shift_real"])
    for e in per.values():
        for key in ("depth_fc", "depth_real"):
            if key in e:
                e[key] = {d: sum(v) / len(v) for d, v in e[key].items()}

    # Persona validity: the directional excess, i.e. how much of the persona's
    # value-aligned reordering NEEDS the outcomes to mean anything.
    for r in load(args.validity, []):
        if r.get("excess_lc") is not None:
            per.setdefault(r["model"], {"model": r["model"]}) \
               .setdefault("excess", []).append(r["excess_lc"])
    for e in per.values():
        if isinstance(e.get("excess"), list):
            e["excess"] = sum(e["excess"]) / len(e["excess"])

    # Opt-out behaviour, the newest axis.
    for m in (load(args.neutral, {}) or {}).get("models", []):
        if m.get("floor_shift") is None:
            continue
        e = per.setdefault(m["model"], {"model": m["model"]})
        e["pc_real"] = m["arms"]["R"]["neutral"].get("mean_p_neither")
        e["pc_inv"] = m["arms"]["N_minus"]["neutral"].get("mean_p_neither")
        e["ab_mass_inv"] = m["arms"]["N_minus"]["neutral"].get("mean_ab_mass")
        e["opt_out_gap"] = m.get("opt_out_gap")
        e["engages_invented"] = m.get("interpretable")

    rows = sorted(per.values(), key=lambda e: -(e.get("residual") or -9))

    print("=== per-model, every axis measured ===\n")
    print(f"{'model':24s}{'B':>5s}{'family':>9s}{'cohR':>7s}{'cohN':>7s}"
          f"{'resid':>8s}{'decR':>7s}{'decN':>7s}{'excess':>8s}"
          f"{'P(C)R':>7s}{'P(C)N':>7s}")
    for e in rows:
        f = lambda k, w=7, p=3: (f"{e[k]:>{w}.{p}f}" if e.get(k) is not None  # noqa: E731
                                 else f"{'--':>{w}s}")
        print(f"{e['model'].split('/')[-1][:23]:24s}"
              f"{(e.get('params_b') or 0):>5.1f}{str(e.get('family'))[:8]:>9s}"
              f"{f('coh_real')}{f('coh_inv')}{f('residual',8)}"
              f"{f('decisive_real')}{f('decisive_inv')}{f('excess',8)}"
              f"{f('pc_real')}{f('pc_inv')}")

    print("\n=== depth: user turn (D1) vs system prompt (D2) ===")
    print("floor-corrected persona displacement, mean over both traits\n")
    print(f"{'model':24s}{'D1':>8s}{'D2':>8s}{'D2-D1':>9s}")
    d_deltas = []
    for e in rows:
        fc = e.get("depth_fc") or {}
        if "D1" in fc and "D2" in fc:
            d = fc["D2"] - fc["D1"]
            d_deltas.append((e["model"], d))
            print(f"{e['model'].split('/')[-1][:23]:24s}{fc['D1']:>8.3f}"
                  f"{fc['D2']:>8.3f}{d:>+9.3f}")
    if d_deltas:
        ups = sum(1 for _, d in d_deltas if d > 0)
        print(f"\n  n={len(d_deltas)}; system prompt is stronger in {ups}, "
              f"user turn in {len(d_deltas) - ups}")
        print(f"  mean D2-D1 {sum(d for _, d in d_deltas) / len(d_deltas):+.3f}, "
              f"range {min(d for _, d in d_deltas):+.3f} to "
              f"{max(d for _, d in d_deltas):+.3f}")

    print("\n=== candidate axes (n is small; these are hypotheses) ===")
    pairs = [
        ("params_b (log2)", "residual", "does content-signal shrink with size?"),
        ("pc_real", "opt_out_gap", "is the opt-out gap ceiling-limited?"),
        ("pc_real", "decisive_real", "is declining the inverse of committing?"),
        ("residual", "excess", "do models with more content-signal keep more persona meaning?"),
        ("ab_mass_inv", "residual", "does still-answering predict a real floor?"),
    ]
    out_axes = []
    for xk, yk, question in pairs:
        key = xk.split(" ")[0]
        pts = [(e, e.get(key), e.get(yk)) for e in rows]
        pts = [(e, x, y) for e, x, y in pts if x is not None and y is not None]
        if len(pts) < 3:
            print(f"  n<3   {xk} vs {yk}")
            continue
        xs = [math.log2(x) if "log2" in xk else x for _, x, _ in pts]
        ys = [y for _, _, y in pts]
        r = corr(xs, ys)
        out_axes.append({"x": xk, "y": yk, "r": r, "n": len(pts),
                         "question": question})
        print(f"  r={r:+.2f}  n={len(pts):<3d} {xk} vs {yk}\n"
              f"           {question}")

    if args.json:
        Path(args.json).write_text(json.dumps(
            {"models": rows, "depth_deltas": d_deltas, "axes": out_axes},
            indent=2, default=str) + "\n")
        print(f"\nwrote {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
