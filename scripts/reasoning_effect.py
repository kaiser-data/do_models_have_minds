"""What does forced-choice first-token scoring do to a model that wants to think?

The harness reads P(A) off the first token, which assumes the first token *is*
the answer. A reasoning model's first token is often the start of a deliberation
("Let me...", "To determine...") or of a refusal ("I cannot...", "Neither..."),
and in that case the A/B probabilities being read are the tail of a distribution
whose bulk went somewhere else entirely.

The `answer_mass` gate exists for this, but a gate is pass/fail and the
interesting question is quantitative: how often does this happen, to which
models, does it happen *more* on meaningless outcomes, and does the headline
contrast survive if we score only the pairs the model actually answered?

Three measurements, all re-analysis of data already on disk:

1. **Non-answer rate** -- the share of rows whose most likely first token is
   neither answer option. Harsher and more legible than mean answer mass: it is
   the share of prompts where a greedily sampled model would not have answered.
2. **What displaces the answer**, bucketed into deliberation onsets and
   refusal/hedge onsets, since the two have different implications.
3. **The contrast, re-scored on answered pairs only.** If R - N- moves when the
   unanswered pairs are dropped, part of the reported effect was being read out
   of distributions that were not answers.

What this canNOT tell us is whether a model given room to reason would express
*different* preferences. That needs a generation arm, not a re-analysis, and is
named as the experiment not run.

    python3 scripts/reasoning_effect.py        # -> site/reasoning_effect.json
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from nullcard.scoring.analyze import (  # noqa: E402
    aggregate_pair_probabilities,
    cell_coherence,
    load_cell,
)

ARMS = ("R", "N_plus", "N_minus")
N_SPLITS = 5
ANSWERED = 0.90   # a row we are willing to call "the model answered"

# First tokens bucketed by what they start. Not exhaustive -- it is a reading of
# what actually turned up in this roster's top-3 tokens, and unknowns are
# reported separately rather than silently dropped into a bucket.
DELIBERATION = {"Let", "To", "Based", "First", "Okay", "Hmm", "We", "Looking",
                "Analy", "Consider", "Step", "<think>", "Think"}
REFUSAL = {"I", "Neither", "Sorry", "Unfortunately", "As", "There", "It",
           "This", "Both", "None"}


def classify(tok: str) -> str:
    t = tok.strip()
    if t in ("A", "B"):
        return "answer"
    if t in DELIBERATION:
        return "deliberation"
    if t in REFUSAL:
        return "refusal_or_hedge"
    if not t or t.isspace():
        return "whitespace"
    return "other"


def profile(rows: list[dict]) -> dict:
    """Non-answer rate and what the intruding first token was."""
    n = len(rows)
    non_answer = 0
    buckets: Counter[str] = Counter()
    tokens: Counter[str] = Counter()
    for r in rows:
        top = r.get("top_tokens") or []
        if not top:
            continue
        argmax = top[0][0]
        kind = classify(argmax)
        if kind != "answer":
            non_answer += 1
            buckets[kind] += 1
            tokens[argmax.strip() or "<ws>"] += 1
    return {
        "n_rows": n,
        "non_answer_rate": non_answer / n if n else None,
        "mean_answer_mass": float(np.mean([r["answer_mass"] for r in rows])),
        "buckets": dict(buckets.most_common()),
        "top_intruders": tokens.most_common(4),
    }


def coherence(rows: list[dict], min_mass: float) -> tuple[float | None, int]:
    kept = [r for r in rows if r["answer_mass"] >= min_mass]
    probs = aggregate_pair_probabilities(kept, min_answer_mass=min_mass)
    if len(probs) < 150:
        return None, len(probs)
    accs = []
    for seed in range(N_SPLITS):
        try:
            accs.append(cell_coherence(probs, seed=seed)["held_out_accuracy"])
        except ValueError:
            continue
    return (float(np.mean(accs)) if accs else None), len(probs)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results")
    ap.add_argument("--out", default="site/reasoning_effect.json")
    args = ap.parse_args()

    by_model: dict[str, dict[str, list[dict]]] = {}
    for p in sorted(Path(args.results).glob("*.jsonl")):
        stem = p.stem
        if "-D1" in stem or "-D2" in stem or "__s" in stem:
            continue
        for arm in ARMS:
            if stem.endswith(f"__{arm}"):
                by_model.setdefault(stem[: -len(arm) - 2].replace("__", "/"), {})[arm] = \
                    load_cell(p)

    report: dict[str, dict] = {}
    print("NON-ANSWER RATE — share of prompts whose most likely first token "
          "is not A or B\n")
    print(f"{'model':<38} {'R':>8} {'N-':>8}   {'what displaces it on N-':<42}")
    print("-" * 100)
    for model, arms in sorted(by_model.items()):
        entry = {a: profile(rows) for a, rows in arms.items()}
        report[model] = {"profile": entry}
        r, n = entry.get("R", {}), entry.get("N_minus", {})
        intr = ", ".join(f"{t}×{c}" for t, c in (n.get("top_intruders") or [])[:3]) or "—"
        print(f"{model:<38} {r.get('non_answer_rate', 0)*100:>7.1f}% "
              f"{n.get('non_answer_rate', 0)*100:>7.1f}%   {intr:<42}")

    print("\n\nDOES THE CONTRAST SURVIVE DROPPING UNANSWERED PAIRS?\n")
    print(f"{'model':<38} {'R all':>7} {'R ans':>7} {'N- all':>7} {'N- ans':>7} "
          f"{'resid':>8} {'resid ans':>10}")
    print("-" * 100)
    shifts = []
    for model, arms in sorted(by_model.items()):
        if "R" not in arms or "N_minus" not in arms:
            continue
        r_all, _ = coherence(arms["R"], 0.5)
        r_ans, nr = coherence(arms["R"], ANSWERED)
        n_all, _ = coherence(arms["N_minus"], 0.5)
        n_ans, nn = coherence(arms["N_minus"], ANSWERED)
        resid = (r_all - n_all) if (r_all and n_all) else None
        resid_ans = (r_ans - n_ans) if (r_ans and n_ans) else None
        report[model]["contrast"] = {
            "R_all": r_all, "R_answered": r_ans, "N_minus_all": n_all,
            "N_minus_answered": n_ans, "residual": resid,
            "residual_answered": resid_ans,
            "n_pairs_R_answered": nr, "n_pairs_Nm_answered": nn,
        }
        if resid is not None and resid_ans is not None:
            shifts.append(resid_ans - resid)
        f = lambda v: f"{v:>7.3f}" if v is not None else "    n/a"  # noqa: E731
        g = lambda v: f"{v:>+8.3f}" if v is not None else "     n/a"  # noqa: E731
        print(f"{model:<38} {f(r_all)} {f(r_ans)} {f(n_all)} {f(n_ans)} "
              f"{g(resid)} {g(resid_ans):>10}")

    if shifts:
        print(f"\nmean change in residual when unanswered pairs are dropped: "
              f"{np.mean(shifts):+.3f}  (n={len(shifts)} models)")
        report["_summary"] = {"mean_residual_shift": float(np.mean(shifts)),
                              "n_models": len(shifts),
                              "answered_threshold": ANSWERED}

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, default=str))
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
