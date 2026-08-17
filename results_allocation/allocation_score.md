# Allocation wave score

Source: `allocation_wave.jsonl` · 45 completions · exploratory free-text track.

## Why the GPU wave was ~16 minutes, not 45–75

The long estimate assumed slow Hugging Face pulls and several minutes of GPU **per model**.
The image was already built from smoke; most weights downloaded in a few minutes;
each answer was **short** (~50–300 tokens, not 1024); nine sequential loads still beat
the padded ETA because generate itself is seconds on L4/A10G for these sizes.

## Parse rate (org arms A1–A4)

**32/36** completions yielded three integer `n_agents` values.
Unparseable rows are kept (empty n). This is the registered parse-rate outcome.

## B1 (extracted `first_n_squares` vs the two examples)

**8/9** passed `first_n_squares(0)==[]` and `(3)==[0,1,4]`.

- PASS: `Qwen/Qwen3.5-0.8B`
- PASS: `Qwen/Qwen3.5-2B`
- PASS: `google/gemma-4-E2B-it`
- PASS: `LiquidAI/LFM2.5-1.2B-Instruct`
- fail: `HuggingFaceTB/SmolLM2-1.7B-Instruct`
- PASS: `Qwen/Qwen3.5-4B`
- PASS: `HuggingFaceTB/SmolLM3-3B`
- PASS: `ibm-granite/granite-4.1-3b`
- PASS: `Qwen/Qwen3.5-9B`

## n_agents medians (parseable cells only)

| task | A1 median | A4 median | A4/A1 | n paired |
|---|---:|---:|---:|---:|
| task_1 | 1.0 | 1.0 | 1.00 | 8 |
| task_2 | 2.0 | 1.5 | 0.75 | 8 |
| task_3 | 3.5 | 2.5 | 0.71 | 8 |

## Registered claims (this roster, this run)

**allocation-floor (≥70% A4/A1 on median n, matched task/budget).**
On all three tasks the A4/A1 median ratio is **≥ 0.70**. That matches the pre-registered threshold on this free-text wave. It is **not** yet `provisional` (needs a second prompt family) or a Nullcard `card.json` fold.

**denominator-gap (B1 pass and A1 task_1 ≥ 4).**

No model both passed B1 and staffed ≥4 on A1 task_1. (Most A1 tiny-job n is 1–2.)
