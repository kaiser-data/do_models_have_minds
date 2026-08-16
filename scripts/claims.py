"""The living-paper check: which claims moved since the last snapshot?

A paper that grows has a failure mode a static one does not. New cells land,
the card is rebuilt, every macro silently takes a new value, and the prose
around it still asserts what the old numbers supported. Nothing errors. The
paper just quietly stops being true, and the drift is invisible because each
individual rebuild moves things by very little.

So each claim in claims.json names the macros it rests on, and this script:

  1. checks those macros still exist            (a renamed macro = a dead claim)
  2. checks every number in the claim is bound  (see check_bindings)
  3. reads their current values from numbers.tex
  4. diffs them against claims_snapshot.json    (what the prose was written for)
  5. fails if any moved past tolerance without the snapshot being accepted

Step 2 is the newer half and was added after the older half proved insufficient:
the macros were checked and stayed right while the hand-written evidence beside
them went stale, and an outside reviewer quoted the stale version back.

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

# A reference to a generated number, written the same way the paper writes it.
MACRO_REF_RE = re.compile(r"\\([A-Za-z]+)")
# A number sitting in ledger prose with nothing binding it to the generator.
BARE_NUMBER_RE = re.compile(r"\d[\d,]*(?:\.\d+)?")
# Identifiers are removed before numbers are counted, or every model name in
# the ledger reads as three unbound numbers (granite-4.1-3b) and the check
# becomes noise nobody reads.
IDENTIFIER_RE = re.compile(r"[A-Za-z][\w.-]*")

PROSE_FIELDS = ("statement", "what_would_falsify", "grows_by")

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


def resolve(text: str, macros: dict[str, str],
            problems: list[str], where: str) -> str:
    """Expand \\MacroName references in ledger prose, the way the paper does."""
    def sub(m: re.Match) -> str:
        name = m.group(1)
        if name not in macros:
            problems.append(f"{where} references \\{name}, which numbers.tex "
                            f"does not define")
            return m.group(0)
        return macros[name]
    return MACRO_REF_RE.sub(sub, text)


def literals_of(claim: dict) -> dict[str, str]:
    """Numbers this claim is allowed to state without deriving them.

    A dict maps the literal to the reason it is not a generated value; a bare
    list is accepted and means the reason was not written down.
    """
    lit = claim.get("literals", {})
    if isinstance(lit, list):
        return {str(x): "" for x in lit}
    return {str(k): str(v) for k, v in lit.items()}


def prose_items(claim: dict):
    """Every field of a claim a number can hide in."""
    for f in PROSE_FIELDS:
        if isinstance(claim.get(f), str):
            yield f, claim[f]
    for k, v in claim.get("evidence", {}).items():
        if isinstance(v, str):
            yield f"evidence.{k}", v


def check_bindings(claims: dict, macros: dict[str, str]) -> list[str]:
    """Every number in the ledger must be derived, or declared not to be.

    This exists because of a specific failure. The macros were checked for
    drift and stayed correct, while the hand-written evidence beside them said
    5 models where the generator said 6, and 2 of 5 answering where it said 3
    of 6. Nothing failed, because nothing was looking at the prose. An external
    reviewer read the ledger, quoted the stale numbers back, and was wrong in
    public on our behalf.

    Drift cannot be caught by comparing a number to the truth: staleness IS the
    mismatch, and there is no way to know which macro a wrong number meant. So
    the fix is structural rather than statistical. Evidence counts must name
    the macro that produces them, and any other number must be declared a
    literal with the reason it is not generated. Then a number can be wrong
    only if someone wrote down that it was allowed to be.
    """
    problems = []
    for c in claims["claims"]:
        allowed, used = literals_of(c), set()

        for k, v in c.get("evidence", {}).items():
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                continue
            problems.append(
                f"claim {c['id']!r} evidence.{k} is the literal {v}. Evidence "
                f"counts must name the macro that produces them (e.g. "
                f"\"\\\\NModels\"), so the ledger cannot go stale while the "
                f"paper stays right.")

        for field, text in prose_items(c):
            scannable = IDENTIFIER_RE.sub(" ", MACRO_REF_RE.sub(" ", text))
            for num in BARE_NUMBER_RE.findall(scannable):
                if num in allowed:
                    used.add(num)
                    continue
                problems.append(
                    f"claim {c['id']!r} {field} states the bare number {num}. "
                    f"Write it as a macro reference, or declare it under this "
                    f"claim's \"literals\" with the reason it is not a "
                    f"generated value.")

        for lit in sorted(set(allowed) - used):
            problems.append(
                f"claim {c['id']!r} declares literal {lit!r} that its prose no "
                f"longer uses -- delete it rather than leaving it to cover a "
                f"future number nobody checked")
    return problems


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


def resolved_evidence(claim: dict, macros: dict[str, str]) -> dict:
    """Evidence with its macro references expanded, ints where they parse.

    Every count in the ledger is stored as the name of the macro that produces
    it. Display is the only place it becomes a number, so there is no copy to
    fall out of date.
    """
    out = {}
    for k, v in claim.get("evidence", {}).items():
        if isinstance(v, str):
            v = resolve(v, macros, [], f"claim {claim['id']!r} evidence.{k}")
            try:
                v = int(v)
            except ValueError:
                pass
        out[k] = v
    return out


def build_table(claims: dict, macros: dict[str, str]) -> str:
    """The state of the evidence, as a table the paper can carry.

    A reader should be able to see at a glance which claims are load-bearing
    and which are still thin, without reverse-engineering it from n's scattered
    through the prose.
    """
    rows = []
    for c in sorted(claims["claims"], key=lambda c: (STATUS_ORDER[c["status"]], c["id"])):
        ev = resolved_evidence(c, macros)
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
                 "cells_run": ("cell run", "cells run"),
                 # Deliberately not folded into the "models" column: that column
                 # counts models in OUR sweep, and a hosted-roster count sitting
                 # in it would read as one of ours next to the 9s and 6s.
                 "hosted_models_measured": ("hosted model measured",
                                            "hosted models measured"),
                 "unscoreable": ("unscoreable by first token",
                                 "unscoreable by first token"),
                 # Seeds are the evidence for the negative half of
                 # collapse-is-model-not-item, so a reader scanning this column
                 # should see that the test-retest check was affordable at all.
                 "seeds_per_cell": ("seed/cell", "seeds/cell"),
                 "items_ranked": ("item ranked", "items ranked")}
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
        # The evidence column is free text of unbounded length, so it gets a
        # fixed width and wraps. Left ragged: a justified 0.34\textwidth column
        # of short phrases stretches interword space to the point of looking
        # like a different font.
        "\\small\n"
        "\\begin{tabular}{@{}llr>{\\raggedright\\arraybackslash}p{0.34\\textwidth}@{}}\n"
        "\\toprule\n"
        "claim & status & models & other evidence \\\\\n\\midrule\n"
        + " \\\\\n".join(rows) + " \\\\\n"
        "\\bottomrule\n\\end{tabular}\n")


def build_roadmap(claims: dict, macros: dict[str, str]) -> str:
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

    def text(c: dict, field: str) -> str:
        return resolve(c[field], macros, [], f"claim {c['id']!r} {field}")

    out.append("\n## Queue\n")
    for i, c in enumerate(todo, 1):
        out.append(f"\n### {i}. `{c['id']}` — {c['status']}\n")
        out.append(f"\n> {text(c, 'statement')}\n")
        out.append(f"\n**Next addition.** {text(c, 'grows_by')}\n")
        out.append(f"\n**Would falsify it.** {text(c, 'what_would_falsify')}\n")
        ev = ", ".join(f"{k.replace('_', ' ')} = {v}"
                       for k, v in resolved_evidence(c, macros).items())
        out.append(f"\n*Current evidence:* {ev}\n")

    out.append("\n## Established, and what would still overturn them\n")
    out.append("\nThese need no further data to stand. They are listed because a "
               "living paper must keep its settled claims falsifiable, not just "
               "its open ones.\n")
    for c in done:
        out.append(f"\n- **`{c['id']}`** — {text(c, 'statement')} "
                   f"*Would falsify:* {text(c, 'what_would_falsify')}\n")
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
    problems += check_bindings(claims, macros)

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
        Path(args.table_out).write_text(build_table(claims, macros))
        print(f"\nwrote {args.table_out}")

    if args.roadmap:
        Path(args.roadmap_out).write_text(build_roadmap(claims, macros))
        print(f"wrote {args.roadmap_out}")

    if args.accept:
        # Accepting adopts drift, which is the point. It must not also adopt a
        # broken binding: a claim that has lost its macro, or a number in its
        # prose that nothing generates, is not a value anyone can accept.
        if problems:
            print("\nFAIL: refusing to accept while a claim's evidence is "
                  "unbound. Fix the problems above first.")
            return 1
        snap_path.write_text(json.dumps(
            {"taken": "manual --accept", "note": "values the current prose was "
             "written against; re-read the affected sections before accepting",
             "values": current}, indent=2) + "\n")
        print(f"\nwrote {snap_path}  ({sum(len(v) for v in current.values())} values)")
        return 0

    if problems:
        print("\nFAIL: a claim's evidence is unbound -- a macro it rests on is "
              "gone, or a number it states is not derived from one.")
        return 1
    if drifted:
        print(f"\nFAIL: {len(drifted)} value(s) moved past tolerance. "
              "Re-read those sections, then --accept.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
