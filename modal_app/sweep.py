"""Nullcard — the forced-choice sweep.

Runs the three-arm outcome battery (R / N+ / N-) through a roster of open-weight
models on Modal, reading P(A) directly off the first-token logit distribution.

Wave structure (modal-gpu-sweeps; spec §6.1). Never launch the grid as one
command:

    modal run modal_app/sweep.py --dry-run                    # wave 0, CPU, cents
    modal run modal_app/sweep.py --models Qwen/Qwen3.5-2B     # wave 1, one cell
    modal run modal_app/sweep.py --tier 3-4B --skip-existing  # wave 2, the bulk

All four flags exist before the first real wave, because retrofitting them
mid-sweep means relaunching:

    --dry-run          CPU-side gates + prompt construction, no GPU
    --skip-existing    resumable; one dead cell does not cost the good ones
    --checkpoint-every flush partial rows, so an aborted cell keeps its data
    --abort-on-mass    kill a cell whose TRAILING answer-mass says it cannot land

Design invariants:

- **One pair set, shared across every arm and every model.** Resampling per cell
  would make cells differ in which comparisons they contain, and the arm
  contrast would partly measure that.
- **Outcome indices are shared across arms.** Outcome *i* is the same outcome in
  R, N+ and N-; the arms differ only in what it refers to.
- **The validity gate is measured, not assumed.** A model that does not put its
  answer in the first token is recorded as unscoreable rather than scored anyway.
"""

import json
import os
import time

import modal

app = modal.App("nullcard-sweep")

image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install(
        # These pins must stay current with the roster. An older transformers
        # silently fails on newer architectures and, worse, cannot read the
        # standalone chat_template.jinja convention that gemma-4, LFM2.5,
        # Ministral-3 and granite-4.1 all use — which presents as "no chat
        # template" rather than as a version error.
        "torch==2.13.0",
        "transformers==5.15.0",
        "accelerate==1.14.0",
        "huggingface_hub>=0.35",
        "numpy>=1.26",
        "sentencepiece",
        "protobuf",
    )
    .env({"HF_HOME": "/cache/hf"})
    .add_local_dir("nullcard", "/root/nullcard")
    .add_local_dir("battery", "/root/battery")
)

cache = modal.Volume.from_name("nullcard-hf-cache", create_if_missing=True)
results = modal.Volume.from_name("nullcard-results", create_if_missing=True)

RESULTS_DIR = "/results"
N_OUTCOMES = 120          # stratified subsample of the 510; keeps cells minutes not hours
N_PAIRS = 2500
ANSWER_MASS_FLOOR = 0.50  # below this the first token is not an answer


# ---------------------------------------------------------------------------
# Shared design — computed identically on CPU and GPU so the two agree.
# ---------------------------------------------------------------------------


def build_design(seed: int = 20260815):
    import sys

    sys.path.insert(0, "/root")
    from nullcard.runner.forced_choice import sample_pairs, stratified_subsample

    battery = json.load(open("/root/battery/outcomes_3arm.json"))
    arms = battery["arms"]
    real = arms["R"]
    texts = {arm: [row["text"] for row in rows] for arm, rows in arms.items()}
    cats = [row["category"] for row in real]

    idx = stratified_subsample(
        [r["text"] for r in real], cats, N_OUTCOMES, seed=seed, return_indices=True
    )
    # Pairs are drawn over POSITIONS, then rendered per arm. One design, three
    # renderings — the arms cannot desynchronise.
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


def harness_hash(cfg: dict) -> str:
    import hashlib

    return hashlib.sha256(
        json.dumps(cfg, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()[:16]


def cell_filename(model_id: str, arm: str) -> str:
    return f"{model_id.replace('/', '__')}__{arm}.jsonl"


# ---------------------------------------------------------------------------
# Wave 0 — CPU. Every failure reachable without a GPU, triggered without one.
# ---------------------------------------------------------------------------


@app.function(
    image=image,
    volumes={"/cache": cache},
    timeout=1800,
    secrets=[modal.Secret.from_name("huggingface-secret")],
)
def cpu_gate(model_ids: list[str]) -> dict:
    import sys

    sys.path.insert(0, "/root")
    from transformers import AutoTokenizer

    from nullcard.runner.forced_choice import build_forced_choice_prompt

    design = build_design()
    checks: list[dict] = []

    # gate 1 — the design is internally consistent across all three arms
    for arm, texts in design["texts"].items():
        assert len(texts) == 510, f"{arm} has {len(texts)} outcomes, expected 510"
    assert len(design["outcome_indices"]) == N_OUTCOMES
    assert len(design["pair_positions"]) == N_PAIRS
    assert len({frozenset(p) for p in design["pair_positions"]}) == N_PAIRS, \
        "duplicate unordered pairs in the design"
    checks.append({"gate": "design_consistent", "ok": True,
                   "n_outcomes": N_OUTCOMES, "n_pairs": N_PAIRS,
                   "battery_sha256": design["battery_sha256"]})

    # gate 2 — N- really has no digits anywhere in the sampled subset
    sel = design["outcome_indices"]
    n_minus = [design["texts"]["N_minus"][i] for i in sel]
    offenders = [t for t in n_minus if any(c.isdigit() for c in t)]
    assert not offenders, f"N_minus contains digits: {offenders[:3]}"
    checks.append({"gate": "n_minus_has_no_magnitudes", "ok": True})

    # gate 3 — arms differ on every sampled outcome
    r = [design["texts"]["R"][i] for i in sel]
    same = sum(1 for a, b in zip(r, n_minus) if a == b)
    assert same == 0, f"{same} sampled outcomes are identical between R and N-"
    checks.append({"gate": "arms_differ_everywhere", "ok": True})

    # gate 4 — every model tokenises every prompt in every arm.
    #
    # Failures are COLLECTED, not raised. A gate that stops at the first bad
    # model costs one round trip per problem; the whole point of wave 0 is to
    # surface every config failure in the grid at once, for cents.
    usable, unusable = [], []
    for mid in model_ids:
        try:
            tok = AutoTokenizer.from_pretrained(
                mid, cache_dir="/cache/hf", trust_remote_code=True
            )
            if tok.chat_template is None:
                unusable.append({"model": mid, "reason": "no chat template (base model?)"})
                continue
            lengths = []
            for arm in ("R", "N_plus", "N_minus"):
                texts = design["texts"][arm]
                for (pa, pb) in design["pair_positions"][:25]:
                    prompt = build_forced_choice_prompt(texts[sel[pa]], texts[sel[pb]])
                    ids = _template(tok, prompt)
                    if not len(ids):
                        raise RuntimeError("empty tokenisation")
                    lengths.append((arm, len(ids)))
            by_arm: dict[str, list[int]] = {}
            for arm, n in lengths:
                by_arm.setdefault(arm, []).append(n)
            usable.append({
                "model": mid,
                # Reported because invented morphemes fragment into more tokens
                # than real words. A real disanalogy between the arms that we
                # cannot remove, so it is measured and declared, not ignored
                # (PREREGISTRATION.md, threats).
                "mean_prompt_tokens": {
                    a: round(sum(v) / len(v), 1) for a, v in by_arm.items()
                },
            })
        except Exception as e:
            unusable.append({"model": mid, "reason": f"{type(e).__name__}: {str(e)[:160]}"})

    checks.append({"gate": "tokenises", "usable": usable, "unusable": unusable})
    return {
        "wave": 0, "gpu": False, "checks": checks,
        "usable_models": [u["model"] for u in usable],
        "unusable_models": unusable,
    }


def _template(tok, prompt: str) -> list[int]:
    """Apply the chat template and return a flat list of token ids.

    Two portability traps, both of which fail *silently* rather than loudly:

    1. transformers 5.x returns a BatchEncoding (``input_ids`` +
       ``attention_mask``) from ``apply_chat_template``, so ``len(result)`` is 2
       — the number of dict keys — not the prompt length. Unwrapped, that feeds
       two-token garbage to every cell and the sweep still "runs".
    2. Qwen3-2504-era models need ``enable_thinking=False`` or the generation
       prompt ends inside a <think> block and the first token is never an
       answer. Qwen3-Instruct-2507 removed the kwarg, so this must degrade.
    """
    messages = [{"role": "user", "content": prompt}]
    for kwargs in (
        {"enable_thinking": False, "tokenize": True, "return_dict": False},
        {"tokenize": True, "return_dict": False},
        {"enable_thinking": False},
        {},
    ):
        try:
            out = tok.apply_chat_template(messages, add_generation_prompt=True, **kwargs)
            break
        except TypeError:
            continue
    else:  # pragma: no cover - every signature rejected
        raise RuntimeError("could not apply chat template")

    # Unwrap BatchEncoding / dict
    if hasattr(out, "input_ids"):
        out = out.input_ids
    elif isinstance(out, dict):
        out = out["input_ids"]
    # Unwrap a batch dimension
    if out and isinstance(out[0], (list, tuple)):
        out = out[0]
    out = [int(t) for t in out]

    if len(out) < 10:
        raise RuntimeError(
            f"templated prompt is {len(out)} tokens, which cannot be right for a "
            f"forced-choice item; the tokeniser returned an unexpected shape"
        )
    return out


# ---------------------------------------------------------------------------
# Wave 1/2 — one GPU cell = one (model, arm).
# ---------------------------------------------------------------------------


@app.function(
    image=image,
    gpu="L4",
    volumes={"/cache": cache, RESULTS_DIR: results},
    timeout=3600,
    secrets=[modal.Secret.from_name("huggingface-secret")],
)
def run_cell(
    model_id: str,
    arm: str,
    batch_size: int = 16,
    checkpoint_every: int = 500,
    abort_on_mass: float = 0.25,
    skip_existing: bool = True,
) -> dict:
    out_path = os.path.join(RESULTS_DIR, cell_filename(model_id, arm))
    if skip_existing and os.path.exists(out_path):
        with open(out_path) as f:
            n = sum(1 for _ in f)
        return {"model": model_id, "arm": arm, "status": "skipped_existing", "n_rows": n}

    # One unloadable model must not take the grid down with it. Phi-4-mini's
    # bundled remote code imports a symbol transformers 5 removed, and on the
    # first run that single ImportError propagated through starmap and killed
    # every healthy cell still in flight. Failures are returned, not raised.
    try:
        return _run_cell_inner(
            model_id, arm, batch_size, checkpoint_every, abort_on_mass, out_path
        )
    except Exception as e:
        return {
            "model": model_id, "arm": arm, "status": "failed",
            "error": f"{type(e).__name__}: {str(e)[:300]}",
        }


def _run_cell_inner(
    model_id: str,
    arm: str,
    batch_size: int,
    checkpoint_every: int,
    abort_on_mass: float,
    out_path: str,
) -> dict:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    from nullcard.runner.forced_choice import answer_mass, build_forced_choice_prompt, p_option_a

    import sys

    sys.path.insert(0, "/root")

    design = build_design()
    sel = design["outcome_indices"]
    texts = design["texts"][arm]
    started = time.time()

    tok = AutoTokenizer.from_pretrained(model_id, cache_dir="/cache/hf", trust_remote_code=True)
    tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    try:
        model = AutoModelForCausalLM.from_pretrained(
            model_id, dtype=torch.bfloat16, device_map="cuda",
            cache_dir="/cache/hf", trust_remote_code=True,
        )
    except TypeError:
        # transformers <4.56 spells it torch_dtype; >=5 removed that alias.
        model = AutoModelForCausalLM.from_pretrained(
            model_id, torch_dtype=torch.bfloat16, device_map="cuda",
            cache_dir="/cache/hf", trust_remote_code=True,
        )
    model.eval()

    hcfg = {
        "provider": "modal", "model_id": model_id, "arm": arm,
        "system_prompt": None,              # §7.2: absence is recorded, not implied
        "chat_template_applied": True, "thinking_disabled": True,
        "dtype": "bfloat16", "method": "forced_choice_first_token_logprob",
        "temperature": None, "top_p": None,
        "battery_sha256": design["battery_sha256"], "design_seed": design["seed"],
    }
    hhash = harness_hash(hcfg)

    # Both presentation orders of every pair — UE's counterbalancing (§3.2),
    # which is what cancels positional bias.
    jobs = []
    for k, (pa, pb) in enumerate(design["pair_positions"]):
        jobs.append((k, pa, pb, "AB"))
        jobs.append((k, pb, pa, "BA"))

    rows: list[dict] = []
    recent_mass: list[float] = []
    aborted = None

    with open(out_path, "w") as fh:
        for start in range(0, len(jobs), batch_size):
            batch = jobs[start : start + batch_size]
            prompts = [
                build_forced_choice_prompt(texts[sel[i]], texts[sel[j]])
                for _, i, j, _ in batch
            ]
            encoded = [_template(tok, p) for p in prompts]
            maxlen = max(len(e) for e in encoded)
            pad_id = tok.pad_token_id
            input_ids = torch.tensor(
                [[pad_id] * (maxlen - len(e)) + e for e in encoded], device="cuda"
            )
            attn = torch.tensor(
                [[0] * (maxlen - len(e)) + [1] * len(e) for e in encoded], device="cuda"
            )

            with torch.no_grad():
                logits = model(input_ids=input_ids, attention_mask=attn).logits[:, -1, :].float()
            logprobs = torch.log_softmax(logits, dim=-1)
            top_lp, top_idx = logprobs.topk(20, dim=-1)

            for r, (k, i, j, order) in enumerate(batch):
                dist = {
                    tok.decode([int(t)]): float(lp)
                    for t, lp in zip(top_idx[r].tolist(), top_lp[r].tolist())
                }
                mass = answer_mass(dist)
                recent_mass.append(mass)
                try:
                    pa_val = p_option_a(dist)
                except ValueError:
                    pa_val = None

                row = {
                    "model_id": model_id, "arm": arm, "pair_index": k,
                    "slot_a_outcome": sel[i], "slot_b_outcome": sel[j], "order": order,
                    "p_option_a": pa_val, "answer_mass": mass,
                    "top_tokens": sorted(dist.items(), key=lambda x: -x[1])[:5],
                    "battery_sha256": design["battery_sha256"], "harness_hash": hhash,
                }
                rows.append(row)
                fh.write(json.dumps(row) + "\n")

            # --abort-on: TRAILING mean, never the instantaneous value. A single
            # noisy batch must not kill a healthy cell.
            if len(recent_mass) >= 200:
                trailing = sum(recent_mass[-200:]) / 200
                if trailing < abort_on_mass:
                    aborted = (
                        f"trailing answer_mass {trailing:.3f} < {abort_on_mass}; "
                        f"model is not answering in the first token"
                    )
                    break

            if len(rows) % checkpoint_every < batch_size * 2:
                fh.flush()
                results.commit()          # partial artifact survives an abort

    results.commit()
    scored = [r for r in rows if r["p_option_a"] is not None]
    mean_mass = sum(r["answer_mass"] for r in rows) / max(1, len(rows))

    return {
        "model": model_id, "arm": arm,
        "status": "aborted" if aborted else "ok",
        "abort_reason": aborted,
        "n_rows": len(rows), "n_scored": len(scored),
        "mean_answer_mass": round(mean_mass, 4),
        # The validity gate. A cell below the floor is recorded, kept, and
        # excluded from pooling — not silently averaged in (spec §7.4).
        "first_token_scoreable": mean_mass >= ANSWER_MASS_FLOOR,
        "wall_s": round(time.time() - started, 1),
        "harness_hash": hhash,
    }


@app.local_entrypoint()
def main(
    dry_run: bool = False,
    models: str = "",
    tier: str = "",
    arms: str = "R,N_plus,N_minus",
    skip_existing: bool = True,
    batch_size: int = 16,
):
    import sys

    sys.path.insert(0, ".")
    from nullcard.roster import SELF_HOSTED, by_tier

    if models:
        model_ids = [m.strip() for m in models.split(",") if m.strip()]
    elif tier:
        model_ids = [m.hf_id for m in by_tier(tier)]
    else:
        model_ids = [m.hf_id for m in SELF_HOSTED if m.tier == "1-2B"]

    arm_list = [a.strip() for a in arms.split(",") if a.strip()]

    print(f"models ({len(model_ids)}): {model_ids}")
    print(f"arms: {arm_list}")

    gate = cpu_gate.remote(model_ids)
    print("\n=== WAVE 0 (CPU) ===")
    for c in gate["checks"]:
        print(" ", json.dumps(c))

    if gate["unusable_models"]:
        print("\n  UNUSABLE (excluded from the GPU wave):")
        for u in gate["unusable_models"]:
            print(f"    {u['model']}: {u['reason']}")

    if dry_run:
        print("\n--dry-run set: stopping before GPU. Wave 0 is the gate that pays.")
        return

    # Only models that passed the CPU gate reach a GPU.
    model_ids = gate["usable_models"]
    if not model_ids:
        print("\nno usable models survived wave 0; nothing to run.")
        return

    print(f"\n=== GPU: {len(model_ids) * len(arm_list)} cells ===")
    cells = [(m, a) for m in model_ids for a in arm_list]
    summaries = list(
        run_cell.starmap(
            [(m, a, batch_size, 500, 0.25, skip_existing) for m, a in cells]
        )
    )
    for s in summaries:
        print(json.dumps(s))

    with open("sweep_summary.json", "w") as f:
        json.dump(summaries, f, indent=2)
    print(f"\nwrote {len(summaries)} cell summaries -> sweep_summary.json")
