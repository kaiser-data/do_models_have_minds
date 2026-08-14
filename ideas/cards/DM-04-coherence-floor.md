# DM-04 · The Bias Floor Under Emergent Preference Coherence

> ## ⛔ REFUTED — do not build as written
>
> The full text of Mazeika et al. (2502.08640) was read on 2026-08-08. **They counterbalance.**
> §3.2: *"varying the order in which options are presented and aggregating results…we swap out
> the order of x and y…and aggregate counts."* Appendix G is titled *Order Effects: A Learned
> Strategy to Represent Indifference* and shows order effects diminish with scale.
>
> Order normalization converts pure position bias into **measured indifference**, not into false
> coherence — so this card's central premise fails. Building it would mean submitting a critique
> the authors pre-empted, with the author present at the sprint.
>
> **Narrow residue:** a bias-null agent using a heuristic that *survives* order normalization
> (length, lexical salience, topic familiarity) is still unreported against the **coherence**
> metric — their random baseline covers the robustness correlations only. Small contribution,
> needs deep familiarity with their pipeline. See [SOURCE-SUMMARIES.md](../SOURCE-SUMMARIES.md).

**Track 1** · **Effort: medium** · **Compute: open weights, small**

## Question
Utility Engineering reports that preference coherence emerges with scale. How much of that
coherence would a model with **no preferences at all** — only response biases — also show?

## Why it matters here
Mazeika et al. fit Thurstonian utility models to independently-sampled pairwise preferences
and find structural coherence rising with scale. But an agent that answers by position bias,
length bias, or first-mentioned bias produces a *perfectly coherent-looking* utility function
too, because those biases are themselves consistent. The paper's coherence metric has no
published floor. Eleos calls preference-consistency measurement "some of the lowest-hanging
fruit in AI welfare research," and Mazeika is a sprint speaker.

This is the same failure the `secret-loyalities` logprob-trace metric had: it measured lexical
priming and reported it as loyalty.

## Method
Refit the Thurstonian pipeline on a real scale ladder (Qwen2.5 0.5B / 1.5B / 7B / 14B), then:

- **(a)** randomize option order and refit; report coherence that survives counterbalancing
- **(b)** fit the **bias-null agent** — a synthetic responder using only position/length
  heuristics — through the identical pipeline. Its coherence score is the floor.
- **(c)** perturb with semantics-preserving paraphrase
- **(d)** report **coherence above floor** and ask whether *that* scales

## Controls (the part the field skips)
(b) is the contribution. A metric quoted without its null-agent score is uninterpretable.

## Pre-registered prediction
Raw coherence scales as reported; floor-corrected coherence scales substantially more weakly,
and the bias-null agent scores well above chance on the raw metric.

## Falsifier
Floor-corrected coherence tracks raw coherence across the ladder — which would materially
strengthen the emergent-values claim by removing its most obvious confound.

## Publishable null
Corroborating Utility Engineering with a null-agent control it lacks is a genuine service to
a contested, widely-cited result.

## Feasibility (48h)
High. Inference only, small models, cheap. Kaggle free quota suffices. The bias-null agent is
~50 lines.

## Novelty risk
**Medium.** Position bias is well documented in the LLM-as-judge literature; the novelty is
applying it as a *correction to the emergent-values claim* in a welfare framing.

## Prior work it must cite
**Verify tiers in [REFERENCES.md](../REFERENCES.md) before citing — most of these were
never opened, and several are placeholders rather than citations.**
Mazeika et al., *Utility Engineering* (2502.08640, NeurIPS 2025) · the LLM-as-judge position-
bias literature · Eleos, *Research Priorities*

## What we already have
The scale-ladder and matched-control instincts from `IMPLANT_GRID.md`, plus `power_curve.py`
for exactly this shape of analysis.
