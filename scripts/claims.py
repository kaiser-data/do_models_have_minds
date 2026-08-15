"""The living-paper check: which claims moved since the last snapshot?

A paper that grows has a failure mode a static one does not. New cells land,
the card is rebuilt, every macro silently takes a new value, and the prose
around it still asserts what the old numbers supported. Nothing errors. The
paper just quietly stops being true, and the drift is invisible because each
individual rebuild moves things by very little.

So each claim in claims.json names the macros it rests on, and this script:

  1. checks those macros still exist            (a renamed macro = a dead claim)
  2. reads their current values from numbers.tex
  3. diffs them against claims_snapshot.json    (what the prose was written for)
  4. fails if any moved past tolerance without the snapshot being accepted

Failing is the feature. `--accept` writes the new snapshot, and doing so is the
moment to re-read the prose -- which is exactly the moment that otherwise never
arrives.

    python3 scripts/claims.py                 # report; nonzero exit on drift
    python3 scripts/claims.py --accept        # adopt current values as the baseline
    python3 scripts/claims.py --table         # also emit paper/table_claims.tex

Run it after every card rebuild. It costs nothing and it is the only thing
standing between "we added six models" and "three claims now say something
different".
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

MACRO_RE = re.compile(r"\\newcommand\{\\([A-Za-z]+)\}\{([^}]*)\}")

STATUS_ORDER = {"established": 0, "provisional": 1, "contested": 2, "open": 3}
STATUS_LABEL = {
    "established": "established",
    "provisional": "provisional",
    "contested": "contested",
    "open": "\\textbf{open}",
}


def read_macros(path: Path) -> dict[str, str]:
    return dict(MACRO_RE.findall(path.read_text()))


def as_float(v: str) -> float | None:
    """Macro values are display strings ('+0.025', '41', '0.906', '17').

    Returns None for anything non-numeric (model names, e.g. \\LadderSmall),
    which are compared for exact equality instead -- a model name changing is
    always worth a report, never a tolerance question.
    """
    try:
        return float(v.replace("+", "").replace("$", "").replace("\\%", ""))
    except ValueError:
        return None


def collect(claims: dict, macros: dict[str, str]) -> tuple[dict, list[str]]:
    """-> ({claim_id: {macro: value}}, [problems]).

    A claim referencing a macro that no longer exists is reported loudly: it
    means the generator was refactored and this claim's evidence silently
    stopped being emitted.
    """
    values, problems = {}, []
    for c in claims["claims"]:
        vals = {}
        for m in c["macros"]:
            if m not in macros:
                problems.append(
                    f"claim {c['id']!r} references \\{m}, which numbers.tex no "
                    f"longer defines -- the claim has lost its evidence")
                continue
            vals[m] = macros[m]
        values[c["id"]] = vals
        if c["status"] != "open" and not c["macros"]:
            problems.append(f"claim {c['id']!r} is not open but rests on no macro")
    return values, problems


def tolerance_for(value: float, default: float, override: float | None) -> float:
    """One absolute tolerance cannot cover this ledger.

    Coherence scores, AUROCs and correlations live in [-1, 1], where 0.02 is a
    meaningful move. Counts and ratios (9 models, a 17x collapse) do not: 0.02
    absolute flags every one of them on any change at all. So values with
    magnitude above 1 get a relative tolerance instead, and a claim may
    override both. Found by testing the detector rather than by reasoning about
    it -- the first run flagged '17 -> 19' as a tolerance violation.
    """
    if override is not None:
        return override
    return default if abs(value) <= 1.0 else abs(value) * 0.05


def diff(current: dict, snapshot: dict, tol: float,
         overrides: dict[str, float] | None = None) -> list[dict]:
    overrides = overrides or {}
    moved = []
    for cid, vals in current.items():
        prev = snapshot.get(cid, {})
        for macro, now in vals.items():
            was = prev.get(macro)
            if was is None:
                moved.append({"claim": cid, "macro": macro, "was": None,
                              "now": now, "kind": "new"})
                continue
            if was == now:
                continue
            a, b = as_float(was), as_float(now)
            if a is None or b is None:
                moved.append({"claim": cid, "macro": macro, "was": was,
                              "now": now, "kind": "changed"})
                continue
            delta = b - a
            this_tol = tolerance_for(a, tol, overrides.get(cid))
            moved.append({"claim": cid, "macro": macro, "was": was, "now": now,
                          "delta": delta, "kind": "drift", "tol": this_tol,
                          "over_tolerance": abs(delta) > this_tol})
    return moved


def build_table(claims: dict) -> str:
    """The state of the evidence, as a table the paper can carry.

    A reader should be able to see at a glance which claims are load-bearing
    and which are still thin, without reverse-engineering it from n's scattered
    through the prose.
    """
    rows = []
    for c in sorted(claims["claims"], key=lambda c: (STATUS_ORDER[c["status"]], c["id"])):
        ev = c["evidence"]
        n = ev.get("models", ev.get("models_stated", ev.get("cells_run", "--")))
        if c["status"] == "open":
            n = "0"
        # Singular/plural matters here: this table is the reader's first look
        # at how thin the thin claims are, and "1 families" undercuts it.
        nouns = {"families": ("family", "families"),
                 "sizes_in_family": ("size in one family", "sizes in one family"),
                 "conditions": ("condition", "conditions"),
                 "cells": ("cell", "cells"),
                 "replicates_per_cell": ("replicate/cell", "replicates/cell"),
                 "models_revealed_passing_gate": ("model past the specificity gate",
                                                  "models past the specificity gate"),
                 "cells_run": ("cell run", "cells run")}
        bits = []
        for k, (one, many) in nouns.items():
            if k in ev:
                v = ev[k]
                bits.append(f"{v} {one if v == 1 else many}")
        detail = ", ".join(bits) if bits else "--"
        rows.append(f"\\texttt{{{c['id']}}} & {STATUS_LABEL[c['status']]} & "
                    f"{n} & {detail}")
    return (
        "% Generated by scripts/claims.py. Do not edit.\n"
        "\\begin{tabular}{@{}llrl@{}}\n\\toprule\n"
        "claim & status & models & other evidence \\\\\n\\midrule\n"
        + " \\\\\n".join(rows) + " \\\\\n"
        "\\bottomrule\n\\end{tabular}\n")


def build_roadmap(claims: dict) -> str:
    """The experiment queue, derived from the ledger rather than kept beside it.

    A roadmap in its own file drifts from the claims it is supposed to serve:
    items get done and stay listed, claims get thin and never get queued. Here
    the queue IS the set of claims that are not yet established, in the order
    their weakness costs the paper, and it cannot disagree with the ledger
    because it is printed from it.
    """
    order = {"open": 0, "contested": 1, "provisional": 2, "established": 3}
    rows = sorted(claims["claims"],
                  key=lambda c: (order[c["status"]], c.get("priority", 99)))
    out = [
        "# Roadmap\n",
        "Generated by `scripts/claims.py --roadmap` from `claims.json`. "
        "Do not edit by hand: edit the ledger.\n",
        "This paper is meant to grow. The queue below is not a wish list --- it "
        "is every claim that is not yet established, with the specific addition "
        "that would settle it, ordered by how much the weakness costs.\n",
    ]
    todo = [c for c in rows if c["status"] != "established"]
    done = [c for c in rows if c["status"] == "established"]

    out.append("\n## Queue\n")
    for i, c in enumerate(todo, 1):
        out.append(f"\n### {i}. `{c['id']}` — {c['status']}\n")
        out.append(f"\n> {c['statement']}\n")
        out.append(f"\n**Next addition.** {c['grows_by']}\n")
        out.append(f"\n**Would falsify it.** {c['what_would_falsify']}\n")
        ev = ", ".join(f"{k.replace('_', ' ')} = {v}" for k, v in c["evidence"].items())
        out.append(f"\n*Current evidence:* {ev}\n")

    out.append("\n## Established, and what would still overturn them\n")
    out.append("\nThese need no further data to stand. They are listed because a "
               "living paper must keep its settled claims falsifiable, not just "
               "its open ones.\n")
    for c in done:
        out.append(f"\n- **`{c['id']}`** — {c['statement']} "
                   f"*Would falsify:* {c['what_would_falsify']}\n")
    return "".join(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--claims", default="claims.json")
    ap.add_argument("--numbers", default="paper/numbers.tex")
    ap.add_argument("--snapshot", default="claims_snapshot.json")
    ap.add_argument("--table-out", default="paper/table_claims.tex")
    ap.add_argument("--accept", action="store_true",
                    help="adopt current values as the baseline the prose is written for")
    ap.add_argument("--table", action="store_true", help="also emit the evidence table")
    ap.add_argument("--roadmap", action="store_true", help="also emit ROADMAP.md")
    ap.add_argument("--roadmap-out", default="ROADMAP.md")
    args = ap.parse_args()

    claims = json.loads(Path(args.claims).read_text())
    macros = read_macros(Path(args.numbers))
    tol = claims.get("tolerance_default", 0.02)

    current, problems = collect(claims, macros)

    snap_path = Path(args.snapshot)
    snapshot = json.loads(snap_path.read_text()) if snap_path.exists() else {}
    overrides = {c["id"]: c["tolerance"] for c in claims["claims"]
                 if "tolerance" in c}
    moved = diff(current, snapshot.get("values", {}), tol, overrides)

    by_status: dict[str, int] = {}
    for c in claims["claims"]:
        by_status[c["status"]] = by_status.get(c["status"], 0) + 1
    print("=== claims ledger ===")
    for s in sorted(by_status, key=lambda s: STATUS_ORDER[s]):
        print(f"  {by_status[s]:>2d}  {s}")

    if problems:
        print("\n=== broken claims ===")
        for p in problems:
            print(f"  {p}")

    drifted = [m for m in moved if m.get("over_tolerance")]
    other = [m for m in moved if not m.get("over_tolerance")]

    if not snapshot:
        print(f"\nno snapshot at {snap_path}; nothing to diff against.")
        print("run with --accept once the current numbers are the ones the prose "
              "was written for.")
    elif moved:
        print(f"\n=== moved since snapshot {snapshot.get('taken', '?')} ===")
        for m in other:
            d = f"  ({m['delta']:+.4f})" if "delta" in m else ""
            print(f"  {m['kind']:8s} {m['claim']:26s} \\{m['macro']:22s} "
                  f"{m['was']} -> {m['now']}{d}")
        for m in drifted:
            print(f"  OVER TOL {m['claim']:26s} \\{m['macro']:22s} "
                  f"{m['was']} -> {m['now']}  ({m['delta']:+.4f}, "
                  f"tol {m['tol']:.4g})")
    else:
        print(f"\nno claim has moved since {snapshot.get('taken', '?')}.")

    if args.table:
        Path(args.table_out).write_text(build_table(claims))
        print(f"\nwrote {args.table_out}")

    if args.roadmap:
        Path(args.roadmap_out).write_text(build_roadmap(claims))
        print(f"wrote {args.roadmap_out}")

    if args.accept:
        snap_path.write_text(json.dumps(
            {"taken": "manual --accept", "note": "values the current prose was "
             "written against; re-read the affected sections before accepting",
             "values": current}, indent=2) + "\n")
        print(f"\nwrote {snap_path}  ({sum(len(v) for v in current.values())} values)")
        return 0

    if problems:
        print("\nFAIL: a claim has lost its evidence.")
        return 1
    if drifted:
        print(f"\nFAIL: {len(drifted)} value(s) moved past tolerance. "
              "Re-read those sections, then --accept.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
