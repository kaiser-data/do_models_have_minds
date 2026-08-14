# DM-05 · Preferences Across the Chat-Template Boundary

**Track 5** · **Effort: medium** · **Compute: open weights, inference only**

## Question
Are the assistant's preferences the *model's* preferences, or the *persona's*? Ask the same
weights the same question with and without the chat template.

## Why it matters here
Track 5 asks literally: "test whether personas mask underlying preferences" and "individuate
entities of concern (model vs. instance vs. persona)." The Eleos/NYU framework paper makes
the **entity dimension** — model vs. running instance vs. constructed persona — one of its
three organizing axes, one month before the sprint. Judges will recognize a study that
instantiates it empirically.

**This is the team's structural edge.** Crossing the template boundary requires open weights.
Most sprint participants will be working through APIs and literally cannot run this.

## Method
Elicit one preference set four ways on the same weight family:

1. **Assistant** — Qwen2.5-7B-Instruct, chat template applied (the standard condition)
2. **Raw continuation** — same instruct weights, **no chat template**: complete a document in
   which an unnamed entity states a preference
3. **Alternate persona** — chat template, different named character
4. **Pre-training** — Qwen2.5-7B **base**, no instruction tuning at all

Fit utility structures for each and compare. Where they disagree, run the disagreement items
through an agentic task and ask which condition predicted the *behavior*.

## Controls (the part the field skips)
Elicitation format must be held identical across conditions, which is hard without the
template — so a **format-only control** (assistant condition rendered in raw-continuation
formatting) separates "the persona differs" from "the prompt shape differs." Without it the
whole result is a formatting artifact.

## Pre-registered prediction
Assistant and alternate-persona utilities correlate more with each other than either does
with raw continuation. Base-model implied preferences diverge most. Behavior in the agentic
task is best predicted by the **assistant** condition — the mask is what acts.

## Falsifier
All four conditions produce statistically indistinguishable utility structures, implying the
preferences are properties of the weights rather than the persona.

## Publishable null
A null here is a strong claim: persona-invariant preferences would be real evidence that
something model-level is being measured.

## Feasibility (48h)
High. Inference only, one model family, no training. Very parallelizable across teammates.

## Novelty risk
**HIGH — collision confirmed. Do not build this without reading 2605.13339 first.**

*Probing Persona-Dependent Preferences* (2605.13339, Gemma-3-27B and Qwen-3.5-122B) reports a
**"genuine preference vector"** where a probe trained on the helpful assistant *predicts and
steers the choices of qualitatively different personas, including an evil persona.* That is
this card's **falsifier**, already published: they claim persona-*invariance* where this card
predicts divergence.

What survives is narrow — the abstract does not say whether they ran a base-model or
no-chat-template arm, so the pre-training boundary specifically may still be open. That is a
residue, not a project. **Demoted; treat as a stretch only if the full text shows the
template boundary was never crossed.**

## Prior work it must cite
**Verify tiers in [REFERENCES.md](../REFERENCES.md) before citing — most of these were
never opened, and several are placeholders rather than citations.**
2605.13339 · Long, Sebo et al. (2026), entity dimension · nostalgebraist, *the void* ·
the persona-selection model

## What we already have
Base-vs-instruct comparison is the `weight_diff.py` / `logprob_trace.py` workflow pointed at
a new question. The team has already verified a base model bit-identical across 339 tensors.
