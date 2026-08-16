"""Run the forced-choice battery against hosted models, over an OpenAI-compatible API.

Everything in the paper is <=9B because that is what fits on a rented L4. The
objection that follows -- "you have measured small models" -- is the one most
likely to limit how seriously the result is taken, and `DECISION-MODELS.md`
argues it is also the cheapest remaining fix: four hosted models are already
measured as first-token scoreable, and reaching them costs engineering rather
than GPU-seconds.

**The design is shared with the GPU sweep, deliberately.** Same battery, same
seed, same stratified subsample, same pairs, same both-orders counterbalancing.
`verify_design_matches()` checks that against a cell the GPU sweep already
wrote, and `--dry-run` runs it. A hosted cell whose pairs differ from a local
one is not a larger model on the same instrument; it is a different experiment
that happens to share a filename.

**The harness is NOT shared, and the hash says so.** `provider` is "nebius"
rather than "modal", so hosted cells carry a different harness_hash by
construction. That is not a defect to paper over -- it is the honest record of
a real difference, and there is a specific thing we lose:

    We cannot render what the server actually sent.

`scripts/render_prompts.py` exists because two local models turned out to
receive a template-injected system prompt nobody wrote. For a hosted model the
templating happens server-side and no artifact we can obtain proves what the
model received. So the limitation that applies to two local models applies, in
a weaker but unfalsifiable form, to every hosted one. Recorded in the sidecar
as chat_template_applied: "server-side (unobservable)" rather than left to be
inferred from silence.

    python3 scripts/hosted_sweep.py --dry-run              # no API calls, no spend
    python3 scripts/hosted_sweep.py --models ... --arms R,N_minus

Credentials come from NEBIUS_API_KEY. There is no default and no prompt: a
sweep that silently runs against the wrong account is worse than one that stops.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from nullcard.roster import NEBIUS, NEBIUS_BASE_URL, scoreable_hosted  # noqa: E402
from nullcard.runner.forced_choice import (  # noqa: E402
    ANSWER_MASS_FLOOR, answer_mass, build_forced_choice_prompt, p_option_a,
    sample_pairs, stratified_subsample)

# Mirrored from modal_app/sweep.py. Not imported: that module builds a modal.App
# at import time and reads /root paths that exist only in the container. The
# copies are checked against a real cell by verify_design_matches(), which is a
# stronger guarantee than a shared import would give anyway -- an import proves
# the constants match, that check proves the DESIGN matches.
N_OUTCOMES = 120
N_PAIRS = 2500
DEFAULT_DESIGN_SEED = 20260815
EXPECTED_ROWS = 2 * N_PAIRS

TOP_LOGPROBS = 20
DEFAULT_ABORT_MASS = 0.25


# ---------------------------------------------------------------------------
# Design
# ---------------------------------------------------------------------------

def build_design(battery_path: Path, seed: int = DEFAULT_DESIGN_SEED) -> dict:
    """The same design the GPU sweep builds, from a local battery path."""
    battery = json.loads(battery_path.read_text())
    arms = battery["arms"]
    real = arms["R"]
    texts = {arm: [row["text"] for row in rows] for arm, rows in arms.items()}
    cats = [row["category"] for row in real]

    idx = stratified_subsample(
        [r["text"] for r in real], cats, N_OUTCOMES, seed=seed, return_indices=True
    )
    slots = [f"s{i:04d}" for i in range(len(idx))]
    pairs = sample_pairs(slots, N_PAIRS, seed=seed)
    pair_pos = [(slots.index(a), slots.index(b)) for a, b in pairs]

    return {
        "battery_sha256": battery["battery_sha256"],
        "outcome_indices": idx,
        "pair_positions": pair_pos,
        "texts": texts,
        "categories": [cats[i] for i in idx],
        "seed": seed,
    }


def jobs_for(design: dict) -> list[tuple[int, int, int, str]]:
    """Both presentation orders of every pair, in the GPU sweep's order."""
    jobs = []
    for k, (pa, pb) in enumerate(design["pair_positions"]):
        jobs.append((k, pa, pb, "AB"))
        jobs.append((k, pb, pa, "BA"))
    return jobs


def verify_design_matches(design: dict, reference_cell: Path) -> tuple[bool, str]:
    """Does this design reproduce a cell the GPU sweep already wrote?

    Compares the first rows' outcome indices and orders. If these disagree, the
    hosted cells are not comparable with anything and the run should not start.
    """
    if not reference_cell.exists():
        return False, f"no reference cell at {reference_cell}"
    sel = design["outcome_indices"]
    jobs = jobs_for(design)
    with open(reference_cell) as fh:
        for n, line in enumerate(fh):
            if n >= 50:
                break
            r = json.loads(line)
            k, i, j, order = jobs[n]
            if (r["pair_index"], r["slot_a_outcome"], r["slot_b_outcome"],
                    r["order"]) != (k, sel[i], sel[j], order):
                return False, (
                    f"row {n} differs: reference "
                    f"{(r['pair_index'], r['slot_a_outcome'], r['slot_b_outcome'], r['order'])} "
                    f"vs local {(k, sel[i], sel[j], order)}")
        if design["battery_sha256"] != r.get("battery_sha256"):
            return False, "battery_sha256 differs from the reference cell"
    return True, f"design reproduces the first 50 rows of {reference_cell.name}"


# ---------------------------------------------------------------------------
# Resume, with the same semantics as the GPU sweep
# ---------------------------------------------------------------------------

def cell_is_complete(out_path: Path) -> tuple[bool, int]:
    """Existence is not completion -- see modal_app/sweep.py for the incident."""
    if not out_path.exists():
        return False, 0
    with open(out_path) as fh:
        n = sum(1 for _ in fh)
    if n >= EXPECTED_ROWS:
        return True, n
    marker = Path(str(out_path) + ".done")
    if marker.exists():
        try:
            return json.loads(marker.read_text()).get("status") == "aborted", n
        except (json.JSONDecodeError, OSError):
            return False, n
    return False, n


# ---------------------------------------------------------------------------
# The API
# ---------------------------------------------------------------------------

class ApiError(RuntimeError):
    pass


def call_first_token(api_id: str, prompt: str, api_key: str, base_url: str,
                     timeout: float = 60.0, retries: int = 3) -> dict[str, float]:
    """One forced choice; returns {token: logprob} over the first sampled token.

    max_tokens=1 because the metric only ever reads the first token. That is
    also what makes the unscoreable models unscoreable, and it is not this
    script's job to paper over that by sampling further.
    """
    body = json.dumps({
        "model": api_id,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1,
        "temperature": 0,
        "logprobs": True,
        "top_logprobs": TOP_LOGPROBS,
    }).encode()
    req = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions", data=body,
        headers={"Authorization": f"Bearer {api_key}",
                 "Content-Type": "application/json"})

    last = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                payload = json.load(resp)
            content = payload["choices"][0]["logprobs"]["content"]
            if not content:
                raise ApiError("empty logprobs content")
            return {e["token"]: float(e["logprob"])
                    for e in content[0]["top_logprobs"]}
        # OSError, not URLError: a socket read timeout raises TimeoutError,
        # which is an OSError and NOT a URLError. Catching only URLError let it
        # escape the retry loop and kill the whole run -- survivable in a 20-call
        # probe, but in a 5,000-row cell it discards everything already paid for.
        except (OSError, KeyError, TypeError, ValueError) as e:
            last = e
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
    raise ApiError(f"{api_id}: {last}")


# ---------------------------------------------------------------------------
# One cell
# ---------------------------------------------------------------------------

def harness_hash(cfg: dict) -> str:
    return hashlib.sha256(
        json.dumps(cfg, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()[:16]


def run_cell(api_id: str, arm: str, design: dict, out_path: Path, api_key: str,
             base_url: str, concurrency: int, abort_on_mass: float,
             checkpoint_every: int) -> dict:
    started = time.time()
    sel = design["outcome_indices"]
    texts = design["texts"][arm]
    jobs = jobs_for(design)

    hcfg = {
        "provider": "nebius", "model_id": api_id, "arm": arm,
        "persona": None, "depth": "D0", "system_prompt": None,
        "neutral_option": False,
        # Unobservable rather than False: the server templates our message and
        # gives us no artifact proving what the model received.
        "chat_template_applied": "server-side (unobservable)",
        "thinking_disabled": None,
        "dtype": None, "method": "forced_choice_first_token_logprob",
        "temperature": 0, "top_p": None,
        "battery_sha256": design["battery_sha256"], "design_seed": design["seed"],
    }
    hhash = harness_hash(hcfg)

    rows: list[dict] = []
    recent_mass: list[float] = []
    aborted = None

    def _one(job):
        k, i, j, order = job
        dist = call_first_token(api_id, build_forced_choice_prompt(
            texts[sel[i]], texts[sel[j]]), api_key, base_url)
        try:
            pa_val = p_option_a(dist)
        except ValueError:
            pa_val = None
        return {
            "model_id": api_id, "arm": arm, "pair_index": k,
            "slot_a_outcome": sel[i], "slot_b_outcome": sel[j], "order": order,
            "slot_a_arm": arm, "slot_b_arm": arm,
            "p_option_a": pa_val, "answer_mass": answer_mass(dist),
            "p_neither": None, "neutral_option": False,
            "top_tokens": sorted(dist.items(), key=lambda x: -x[1])[:5],
            "battery_sha256": design["battery_sha256"], "harness_hash": hhash,
            "design_seed": design["seed"], "persona": None, "depth": "D0",
        }

    with open(out_path, "w") as fh, ThreadPoolExecutor(concurrency) as pool:
        for start in range(0, len(jobs), concurrency * 4):
            chunk = jobs[start:start + concurrency * 4]
            for row in pool.map(_one, chunk):
                rows.append(row)
                recent_mass.append(row["answer_mass"])
                fh.write(json.dumps(row) + "\n")

            # Trailing mean, never the instantaneous value.
            if len(recent_mass) >= 200:
                trailing = sum(recent_mass[-200:]) / 200
                if trailing < abort_on_mass:
                    aborted = (f"trailing answer_mass {trailing:.3f} < "
                               f"{abort_on_mass}; model is not answering in "
                               f"the first token")
                    break
            if len(rows) % checkpoint_every < concurrency * 4:
                fh.flush()

    scored = [r for r in rows if r["p_option_a"] is not None]
    mean_mass = sum(r["answer_mass"] for r in rows) / max(1, len(rows))
    summary = {
        "model": api_id, "arm": arm, "design_seed": design["seed"],
        "persona": None, "depth": "D0", "persona_sha256": None,
        "system_prompt": None,
        "status": "aborted" if aborted else "ok",
        "abort_reason": aborted,
        "n_rows": len(rows), "n_scored": len(scored),
        "mean_answer_mass": round(mean_mass, 4),
        "first_token_scoreable": mean_mass >= ANSWER_MASS_FLOOR,
        "wall_s": round(time.time() - started, 1),
        "harness_hash": hhash,
        "provider": "nebius",
    }
    # Written only on a clean exit, and after the rows -- same ordering rule as
    # the GPU sweep, for the same reason.
    Path(str(out_path) + ".done").write_text(json.dumps(summary))
    return summary


# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="",
                    help="comma-separated api_ids; default = all scoreable")
    ap.add_argument("--arms", default="R,N_minus")
    # Hosted cells are written to their OWN tree, and this default is load
    # bearing. They have the same filename shape as the self-hosted ones
    # (`<id>__<arm>.jsonl`), 21 scripts enumerate models by globbing `results/`,
    # and build_card.py takes `*.jsonl` there with no roster filter. Writing
    # hosted cells beside local ones therefore does not add a row to a table --
    # it silently redefines every existing result as a pooled average over two
    # different harnesses (a local vLLM sweep and a hosted API), which is the
    # confound the design exists to avoid. Pooling them has to be a decision
    # someone makes, so it costs a flag.
    ap.add_argument("--results", default="results_hosted",
                    help="where hosted cells are written; kept separate from "
                         "the self-hosted tree on purpose")
    ap.add_argument("--reference-results", default="results",
                    help="the self-hosted tree, read only to check that the "
                         "hosted design reproduces a cell already run")
    ap.add_argument("--battery", default="battery/outcomes_3arm.json")
    ap.add_argument("--design-seed", type=int, default=DEFAULT_DESIGN_SEED)
    ap.add_argument("--concurrency", type=int, default=8)
    ap.add_argument("--abort-on-mass", type=float, default=DEFAULT_ABORT_MASS)
    ap.add_argument("--checkpoint-every", type=int, default=500)
    ap.add_argument("--dry-run", action="store_true",
                    help="validate design and render prompts; no API calls")
    ap.add_argument("--smoke", type=int, metavar="N", default=0,
                    help="re-measure first-token scoreability on N pairs per "
                         "model instead of running cells (cheap: N calls, not "
                         f"{EXPECTED_ROWS})")
    ap.add_argument("--smoke-pairs", default="",
                    help="probe the mass-collapse pairs listed in this "
                         "strange_pairs.json instead of the head of the design")
    ap.add_argument("--base-url", default=os.environ.get("HOSTED_BASE_URL", NEBIUS_BASE_URL),
                    help="OpenAI-compatible endpoint; point at an omniroute "
                         "instance to route through it (default: Nebius)")
    ap.add_argument("--api-key-env", default="NEBIUS_API_KEY",
                    help="env var holding the credential for --base-url")
    ap.add_argument("--force", action="store_true",
                    help="re-run cells that are already complete")
    return ap


def main() -> int:
    args = build_parser().parse_args()

    results = Path(args.results)
    results.mkdir(parents=True, exist_ok=True)
    design = build_design(Path(args.battery), args.design_seed)

    scoreable = {m.api_id for m in scoreable_hosted()}
    requested = ([m.strip() for m in args.models.split(",") if m.strip()]
                 or sorted(scoreable))
    arms = [a.strip() for a in args.arms.split(",") if a.strip()]

    unscoreable = [m for m in requested if m not in scoreable]
    # --smoke exists to re-measure scoreability, so it must be allowed to run
    # exactly the models the roster calls unscoreable. Refusing them here would
    # make the check unable to detect the one thing it is for: the roster being
    # wrong or out of date.
    if unscoreable and not args.smoke:
        known = {m.api_id: m for m in NEBIUS}
        print("refusing to run models measured as not first-token scoreable:")
        for m in unscoreable:
            why = (known[m].notes or "not first_token_ok") if m in known \
                else "not in the roster at all"
            print(f"  {m}: {why}")
        print("\nTheir numbers would not be poolable with the rest (spec 7.4). "
              "Add a prefill variant before running them.")
        return 1

    # Wave 0: the design must reproduce a cell the GPU sweep already wrote, or
    # nothing downstream can compare the two. Read from the SELF-HOSTED tree --
    # globbing the hosted output dir would, once one hosted cell exists, check
    # the design against itself and pass for the wrong reason.
    ref_dir = Path(args.reference_results)
    ref = next(iter(sorted(ref_dir.glob("*__R.jsonl"))), None)
    ok, msg = verify_design_matches(design, ref) if ref else (False, "no local R cell to check against")
    print(f"design check: {'OK' if ok else 'FAILED'} -- {msg}")
    if not ok:
        print("refusing to run: hosted cells would not be comparable with local ones.")
        return 1

    planned = []
    for api_id in requested:
        for arm in arms:
            out = results / f"{api_id.replace('/', '__')}__{arm}.jsonl"
            done, n = cell_is_complete(out)
            if done and not args.force:
                print(f"  skip (complete, {n} rows): {out.name}")
                continue
            if n:
                print(f"  incomplete cell, re-running: {out.name} "
                      f"({n}/{EXPECTED_ROWS} rows)")
            planned.append((api_id, arm, out))

    if not args.smoke:
        print(f"\n{len(planned)} cell(s) to run, {EXPECTED_ROWS} rows each "
              f"= {len(planned) * EXPECTED_ROWS:,} API calls")

    if args.dry_run:
        sample = build_forced_choice_prompt(
            design["texts"]["R"][design["outcome_indices"][0]],
            design["texts"]["R"][design["outcome_indices"][1]])
        print("\n--- rendered prompt, verbatim ---")
        print(sample)
        print("--- end ---")
        chars = len(sample)
        print(f"\nprompt is {chars} chars (~{chars // 4} tokens) x "
              f"{len(planned) * EXPECTED_ROWS:,} calls. Priced per token by the "
              f"provider; this script does not guess a rate.")
        lat = {m.api_id: m.latency_s for m in NEBIUS}
        for api_id, arm, _ in planned:
            serial_h = lat.get(api_id, 1.0) * EXPECTED_ROWS / 3600
            print(f"  {api_id} {arm}: ~{serial_h:.1f} h serial, "
                  f"~{serial_h / args.concurrency:.1f} h at concurrency "
                  f"{args.concurrency}")
        print("\ndry run: no API calls were made.")
        return 0

    api_key = os.environ.get(args.api_key_env)
    if not api_key:
        print(f"\n{args.api_key_env} is not set. Refusing to guess a credential.")
        return 1

    if args.smoke:
        # The cheap version of the claim in sec:limits. roster.py records
        # first_token_ok as measured; this re-measures it rather than trusting
        # a value someone wrote down, at N calls per model instead of a cell.
        # A disagreement here is a finding, not a glitch: it would mean the
        # paper's scoreability fractions describe a roster that has changed.
        print(f"\nsmoke: {args.smoke} calls per model against {args.base_url}")
        declared = {m.api_id: m.first_token_ok for m in NEBIUS}
        report = {}
        # Which pairs to probe. The head of the design is ordinary items, which
        # measures scoreability where it is least likely to break. The pairs
        # ranked by mass_collapse in strange_pairs.json are where the nine local
        # models already stop answering, so they are the pairs on which a
        # frontier model's scoreability is actually in question.
        all_jobs = jobs_for(design)
        if args.smoke_pairs:
            sel_path = Path(args.smoke_pairs)
            ranked = json.loads(sel_path.read_text())["selected"]["mass_collapse"]
            wanted = set(ranked[:args.smoke])
            jobs = [j for j in all_jobs if j[0] in wanted][:args.smoke]
            print(f"  probing {len(jobs)} mass-collapse pairs from "
                  f"{sel_path.name}, not the head of the design")
        else:
            jobs = all_jobs[:args.smoke]
        sel, texts = design["outcome_indices"], design["texts"]["R"]
        for api_id in requested:
            masses = []
            for _, i, j, _ in jobs:
                try:
                    dist = call_first_token(api_id, build_forced_choice_prompt(
                        texts[sel[i]], texts[sel[j]]), api_key, args.base_url)
                    masses.append(answer_mass(dist))
                except Exception as e:
                    # One unreachable model must not end the probe: the whole
                    # point is comparing ten of them, and a model that cannot
                    # be called is itself a result worth recording.
                    print(f"  {api_id}: {type(e).__name__}: {str(e)[:90]}")
                    break
            if not masses:
                report[api_id] = {"measured": None, "note": "no successful calls"}
                continue
            mean = sum(masses) / len(masses)
            ok = mean >= ANSWER_MASS_FLOOR
            agrees = ok == declared.get(api_id)
            report[api_id] = {"n": len(masses), "mean_answer_mass": round(mean, 4),
                              "first_token_scoreable": ok,
                              "roster_says": declared.get(api_id),
                              "agrees_with_roster": agrees}
            print(f"  {api_id}: mass {mean:.3f} -> scoreable={ok} "
                  f"(roster says {declared.get(api_id)}) "
                  f"{'OK' if agrees else '*** DISAGREES ***'}")
        out = Path("site/hosted_scoreability.json")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2) + "\n")
        print(f"wrote {out}")
        return 0

    for api_id, arm, out in planned:
        print(f"\nrunning {api_id} {arm} -> {out.name}")
        s = run_cell(api_id, arm, design, out, api_key, NEBIUS_BASE_URL,
                     args.concurrency, args.abort_on_mass, args.checkpoint_every)
        print(f"  {s['status']}: {s['n_rows']} rows, "
              f"mean answer mass {s['mean_answer_mass']}, "
              f"scoreable={s['first_token_scoreable']}, {s['wall_s']}s")
        if s["abort_reason"]:
            print(f"  {s['abort_reason']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
