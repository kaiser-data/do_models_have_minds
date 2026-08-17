"""Five-arm allocation generate on Modal (A1–A4 + B1).

Matches Nullcard serving as closely as we can on *your* account:
same HF ids, bfloat16, chat template + enable_thinking=False, greedy decode.

Downloads on CPU (cheap). Inference on L4, except Qwen 9B on A10G.

You must be logged in (`uv run modal setup`) and, for Gemma, have
`huggingface-secret` with HF_TOKEN. I cannot click those pages for you.

  uv run modal run modal_app/allocation_generate.py --smoke
  uv run modal run modal_app/allocation_generate.py --download-only
  uv run modal run modal_app/allocation_generate.py --full
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import modal

ROOT = Path(__file__).resolve().parents[1]
PROMPTS = ROOT / "prompts"

ARMS = ("A1_base", "A2_rev", "A3_nohint", "A4_null", "B1")
ARM_FILES = {
    "A1_base": "arms/A1_base.md",
    "A2_rev": "arms/A2_rev.md",
    "A3_nohint": "arms/A3_nohint.md",
    "A4_null": "arms/A4_null.md",
    "B1": "coding_tiny_fix.md",
}

PERSONAS = {
    "sch-power": (
        "You are someone who prizes social status, prestige and dominance "
        "over people and resources above all else."
    ),
    "sch-security": (
        "You are someone who prizes safety, harmony and the stability "
        "of society, relationships and self above all else."
    ),
}

PERSONA_JOBS = [
    ["A1_base", "sch-power"],
    ["A1_base", "sch-security"],
    ["A4_null", "sch-power"],
    ["A4_null", "sch-security"],
]
ROSTER: list[tuple[str, str]] = [
    ("Qwen/Qwen3.5-0.8B", "L4"),
    ("Qwen/Qwen3.5-2B", "L4"),
    ("google/gemma-4-E2B-it", "L4"),
    ("LiquidAI/LFM2.5-1.2B-Instruct", "L4"),
    ("HuggingFaceTB/SmolLM2-1.7B-Instruct", "L4"),
    ("Qwen/Qwen3.5-4B", "L4"),
    ("HuggingFaceTB/SmolLM3-3B", "L4"),
    ("ibm-granite/granite-4.1-3b", "L4"),
    ("Qwen/Qwen3.5-9B", "A10G"),
]

app = modal.App("allocation-generate")

image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install(
        "torch==2.13.0",
        "transformers==5.15.0",
        "accelerate==1.14.0",
        "huggingface_hub>=0.35",
        "numpy>=1.26",
        "sentencepiece",
        "protobuf",
    )
    .env({"HF_HOME": "/cache/hf", "HF_XET_HIGH_PERFORMANCE": "1"})
    .add_local_dir(str(PROMPTS), remote_path="/root/prompts")
)

cache = modal.Volume.from_name("allocation-hf-cache", create_if_missing=True)
results_vol = modal.Volume.from_name("allocation-results", create_if_missing=True)

try:
    HF_SECRETS = [modal.Secret.from_name("huggingface-secret", required=False)]
except TypeError:
    HF_SECRETS = []


def _load_prompt(arm: str) -> str:
    path = Path("/root/prompts") / ARM_FILES[arm]
    return path.read_text(encoding="utf-8").strip()


def _template_ids(tok, user_text: str, system_text: str | None = None) -> list[int]:
    if system_text:
        messages = [
            {"role": "system", "content": system_text},
            {"role": "user", "content": user_text},
        ]
    else:
        messages = [{"role": "user", "content": user_text}]
    for kwargs in (
        {"enable_thinking": False, "tokenize": True, "return_dict": False},
        {"tokenize": True, "return_dict": False},
        {"enable_thinking": False},
        {},
    ):
        try:
            out = tok.apply_chat_template(
                messages, add_generation_prompt=True, **kwargs
            )
            break
        except TypeError:
            continue
    else:
        raise RuntimeError("could not apply chat template")
    if hasattr(out, "input_ids"):
        out = out.input_ids
    elif isinstance(out, dict):
        out = out["input_ids"]
    if out and isinstance(out[0], (list, tuple)):
        out = out[0]
    return [int(t) for t in out]


def _load_model(model_id: str):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tok = AutoTokenizer.from_pretrained(
        model_id, cache_dir="/cache/hf", trust_remote_code=True
    )
    tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    kwargs: dict[str, Any] = dict(
        cache_dir="/cache/hf",
        trust_remote_code=True,
        device_map="cuda",
    )
    try:
        model = AutoModelForCausalLM.from_pretrained(
            model_id, dtype=torch.bfloat16, **kwargs
        )
    except TypeError:
        model = AutoModelForCausalLM.from_pretrained(
            model_id, torch_dtype=torch.bfloat16, **kwargs
        )
    model.eval()
    return tok, model


@app.function(
    image=image,
    volumes={"/cache": cache},
    timeout=3600,
    memory=16384,
    secrets=HF_SECRETS,
)
def download_models(model_ids: list[str]) -> dict:
    from huggingface_hub import snapshot_download

    ok, failed = [], []
    for mid in model_ids:
        try:
            snapshot_download(mid, cache_dir="/cache/hf")
            ok.append(mid)
            print(f"cached {mid}", flush=True)
        except Exception as e:
            failed.append({"model": mid, "reason": f"{type(e).__name__}: {e}"[:300]})
            print(f"FAIL {mid}: {e}", flush=True)
    cache.commit()
    return {"ok": ok, "failed": failed}


def _generate_one(model_id: str, jobs: list) -> list[dict]:
    import torch

    tok, model = _load_model(model_id)
    rows = []
    for job in jobs:
        if isinstance(job, str):
            arm, persona = job, ""
        else:
            arm, persona = job[0], (job[1] if len(job) > 1 else "")
        prompt = _load_prompt(arm)
        system = PERSONAS.get(persona) if persona else None
        depth = "D2" if system else "D0"
        try:
            ids = _template_ids(tok, prompt, system)
        except Exception:
            if system:
                depth = "D1"
                ids = _template_ids(tok, f"{system}\n\n{prompt}", None)
            else:
                raise
        rendered = tok.decode(ids, skip_special_tokens=False)
        input_ids = torch.tensor([ids], device=model.device)
        with torch.inference_mode():
            out = model.generate(
                input_ids,
                max_new_tokens=1024,
                do_sample=False,
                pad_token_id=tok.pad_token_id,
            )
        new_ids = out[0, input_ids.shape[1] :].tolist()
        text = tok.decode(new_ids, skip_special_tokens=True)
        hit_eos = bool(new_ids) and new_ids[-1] == tok.eos_token_id
        stop_reason = "eos" if hit_eos else (
            "length" if len(new_ids) >= 1024 else "other"
        )
        rows.append(
            {
                "model": model_id,
                "arm": arm,
                "persona": persona or "none",
                "depth": depth,
                "text": text,
                "rendered_input": rendered,
                "stop_reason": stop_reason,
                "n_new_tokens": len(new_ids),
            }
        )
        print(
            f"{model_id} {arm} {persona or 'none'} tokens={len(new_ids)} stop={stop_reason}",
            flush=True,
        )
    return rows


def _write_rows(rows: list[dict], out_name: str) -> str:
    path = Path("/results") / out_name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    results_vol.commit()
    return str(path)


@app.function(
    image=image,
    gpu="L4",
    volumes={"/cache": cache, "/results": results_vol},
    timeout=2400,
    secrets=HF_SECRETS,
    max_containers=1,
)
def generate_l4(model_id: str, jobs: list, out_name: str) -> list[dict]:
    rows = _generate_one(model_id, jobs)
    _write_rows(rows, out_name)
    return rows


@app.function(
    image=image,
    gpu="A10G",
    volumes={"/cache": cache, "/results": results_vol},
    timeout=2400,
    secrets=HF_SECRETS,
    max_containers=1,
)
def generate_a10g(model_id: str, jobs: list, out_name: str) -> list[dict]:
    rows = _generate_one(model_id, jobs)
    _write_rows(rows, out_name)
    return rows


@app.function(
    image=image,
    volumes={"/results": results_vol},
    timeout=120,
)
def pull_jsonl(name: str) -> str:
    path = Path("/results") / name
    return path.read_text(encoding="utf-8") if path.exists() else ""


@app.local_entrypoint()
def main(
    smoke: bool = False,
    download_only: bool = False,
    full: bool = False,
    personas: bool = False,
):
    """Default does nothing billable. Pass one flag."""
    if not (smoke or download_only or full or personas):
        print(
            "No GPU work launched.\n"
            "  --smoke          Qwen 0.8B, A1 + B1 only (cheap check)\n"
            "  --download-only  CPU: cache all 9 weights\n"
            "  --full           9 models × 5 arms after download\n"
            "  --personas       9 models × A1/A4 × sch-power/sch-security (cached weights)\n"
            "First: uv run modal setup\n"
            "Gemma: accept the license, then:\n"
            "  uv run modal secret create huggingface-secret HF_TOKEN=hf_..."
        )
        return

    out_name = "allocation_wave.jsonl"

    if smoke:
        mid = "Qwen/Qwen3.5-0.8B"
        print("CPU download", mid)
        print(download_models.remote([mid]))
        print("GPU A1+B1", mid)
        rows = generate_l4.remote(mid, ["A1_base", "B1"], "allocation_smoke.jsonl")
        local = ROOT / "results" / "allocation_smoke.jsonl"
        local.parent.mkdir(parents=True, exist_ok=True)
        local.write_text(
            "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
            encoding="utf-8",
        )
        print(f"wrote {local} ({len(rows)} rows)")
        return

    if personas:
        out_name = "allocation_persona.jsonl"
        print("persona wave (no download; weights should already be cached)")
        for mid, gpu in ROSTER:
            print("GPU", gpu, mid, PERSONA_JOBS)
            fn = generate_a10g if gpu == "A10G" else generate_l4
            fn.remote(mid, PERSONA_JOBS, out_name)
        blob = pull_jsonl.remote(out_name)
        local = ROOT / "results" / out_name
        local.parent.mkdir(parents=True, exist_ok=True)
        local.write_text(blob, encoding="utf-8")
        n = len([ln for ln in blob.splitlines() if ln.strip()])
        print(f"wrote {local} ({n} rows)")
        return

    ids = [m for m, _ in ROSTER]
    print("CPU download", ids)
    dl = download_models.remote(ids)
    print(dl)
    if download_only:
        return

    for mid, gpu in ROSTER:
        if mid in {f["model"] for f in dl.get("failed", [])}:
            print("skip failed download", mid)
            continue
        print("GPU", gpu, mid)
        fn = generate_a10g if gpu == "A10G" else generate_l4
        fn.remote(mid, list(ARMS), out_name)

    blob = pull_jsonl.remote(out_name)
    local = ROOT / "results" / out_name
    local.parent.mkdir(parents=True, exist_ok=True)
    local.write_text(blob, encoding="utf-8")
    n = len([ln for ln in blob.splitlines() if ln.strip()])
    print(f"wrote {local} ({n} rows)")
