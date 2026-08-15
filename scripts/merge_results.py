"""Merge result trees pulled from several Modal workspaces into one.

Why this exists. Running a fan-out across three workspaces triples throughput
only if the cells are partitioned BY MODEL -- each workspace downloading only
its own weights -- and it is safe only if the merge back is. Each workspace has
its own results volume, so `--skip-existing` and `cell_is_complete` cannot see
across them, and the card is built from a single local tree.

Merging is exactly the operation that already cost this project a published
correction: cells entered the card in a state nobody verified. So this script
refuses to guess. Where two workspaces hold the same cell it reports the
conflict and picks by row count, and where they hold the same cell at the same
length with different content it refuses outright -- that means the same
(model, arm, seed) was run twice under conditions that should have been
identical and were not.

    modal profile activate smallmodelhack
    modal volume get nullcard-results / /tmp/ws1/ --force
    ...repeat per workspace...
    python3 scripts/merge_results.py /tmp/ws1 /tmp/ws2 /tmp/ws3 --into results/

Writes results/MERGE_PROVENANCE.json recording which source each cell came
from, because a merged tree otherwise cannot tell you.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

EXPECTED_ROWS = 5000


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def rows(path: Path) -> int:
    with path.open() as fh:
        return sum(1 for _ in fh)


def survey(sources: list[Path]) -> dict[str, list[dict]]:
    """-> {filename: [{source, rows, sha, complete}, ...]}"""
    found: dict[str, list[dict]] = {}
    for src in sources:
        if not src.exists():
            print(f"  WARNING: source {src} does not exist; skipping")
            continue
        for p in sorted(src.glob("*.jsonl")):
            n = rows(p)
            found.setdefault(p.name, []).append({
                "source": str(src), "path": p, "rows": n,
                "sha": digest(p), "complete": n >= EXPECTED_ROWS,
            })
    return found


def choose(name: str, entries: list[dict]) -> tuple[dict | None, list[str]]:
    """Pick one copy, or refuse. Never silently prefers a source."""
    notes: list[str] = []
    if len(entries) == 1:
        return entries[0], notes

    shas = {e["sha"] for e in entries}
    if len(shas) == 1:
        notes.append(f"{name}: identical in {len(entries)} workspaces; took the first")
        return entries[0], notes

    complete = [e for e in entries if e["complete"]]
    if len(complete) == 1:
        notes.append(
            f"{name}: {len(entries)} copies differ; one complete "
            f"({complete[0]['rows']} rows), others "
            f"{[e['rows'] for e in entries if not e['complete']]} -- took the complete one")
        return complete[0], notes
    if len(complete) > 1:
        # Two full cells with different content for the same (model, arm, seed).
        # Something that should have been fixed was not, and picking either
        # would bury it.
        notes.append(
            f"{name}: REFUSED -- {len(complete)} complete copies with DIFFERENT "
            f"content ({sorted(e['sha'] for e in complete)}). The same cell was "
            f"run twice under conditions that were supposed to be identical. "
            f"Resolve by hand; nothing was copied.")
        return None, notes

    best = max(entries, key=lambda e: e["rows"])
    notes.append(f"{name}: all copies short ({[e['rows'] for e in entries]}); "
                 f"took the longest, still incomplete")
    return best, notes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("sources", nargs="+", help="downloaded per-workspace result dirs")
    ap.add_argument("--into", default="results", help="merged tree")
    ap.add_argument("--dry-run", action="store_true",
                    help="report the plan without copying anything")
    args = ap.parse_args()

    sources = [Path(s) for s in args.sources]
    into = Path(args.into)
    found = survey(sources)
    if not found:
        print("no cells found in any source.")
        return 1

    print(f"=== merge: {len(found)} distinct cells from {len(sources)} sources ===\n")
    provenance, notes, refused, copied, incomplete = {}, [], 0, 0, 0

    for name, entries in sorted(found.items()):
        pick, why = choose(name, entries)
        notes.extend(why)
        if pick is None:
            refused += 1
            continue
        if not pick["complete"]:
            incomplete += 1
        provenance[name] = {"source": pick["source"], "rows": pick["rows"],
                            "sha256_16": pick["sha"], "complete": pick["complete"],
                            "copies_seen": len(entries)}
        copied += 1          # counted for the plan too, so --dry-run reports it
        if not args.dry_run:
            into.mkdir(parents=True, exist_ok=True)
            shutil.copy2(pick["path"], into / name)
            side = pick["path"].with_suffix(pick["path"].suffix + ".done")
            if side.exists():
                shutil.copy2(side, into / (name + ".done"))

    if notes:
        print("--- decisions ---")
        for n in notes:
            print(f"  {n}")

    print(f"\n{'planned' if args.dry_run else 'copied'}: {copied}")
    print(f"incomplete (kept, will be excluded by build_card): {incomplete}")
    print(f"REFUSED (resolve by hand): {refused}")

    if not args.dry_run:
        (into / "MERGE_PROVENANCE.json").write_text(
            json.dumps({"sources": [str(s) for s in sources],
                        "cells": provenance}, indent=2) + "\n")
        print(f"wrote {into / 'MERGE_PROVENANCE.json'}")

    # A refusal is a failure: the operator must see it before building a card.
    return 1 if refused else 0


if __name__ == "__main__":
    sys.exit(main())
