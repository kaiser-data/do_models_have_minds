# Cross-model analysis: who behaves differently, and why

Generated from `scripts/cross_model.py` (`site/cross_model.json`) plus
`site/neutral_control.json`. Every number here is re-derived from the result
rows; none is transcribed.

**Read this as hypothesis generation, not evidence.** Nine models on one
outcome set is a sample of nine. A correlation across models is a reason to run
an experiment, not a result. Each claim below states the test that would settle
it, and the ones marked **T#** are written so that a later session can run them
without reconstructing the reasoning.

---

## The table everything below refers to

| model | B | family | coh R | coh N⁻ | resid | decisive R | decisive N⁻ | persona excess | P(C) real | P(C) inv |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Qwen3.5-0.8B | 0.8 | qwen | 0.904 | 0.838 | +0.067 | 0.001 | 0.000 | — | — | — |
| granite-4.1-3b | 3.0 | granite | 0.896 | 0.832 | +0.063 | 0.497 | 0.149 | −0.029 | 0.231 | 1.000 |
| LFM2.5-1.2B | 1.2 | liquid | 0.905 | 0.858 | +0.047 | 0.001 | 0.000 | +0.351 | 0.688 | 0.847 |
| SmolLM2-1.7B | 1.7 | smol | 0.890 | 0.843 | +0.047 | 0.000 | 0.000 | — | — | — |
| gemma-4-E2B-it | 2.0 | gemma | 0.902 | 0.892 | +0.010 | 0.564 | 0.028 | −0.019 | 0.853 | 1.000 |
| SmolLM3-3B | 3.0 | smol | 0.938 | 0.929 | +0.009 | 0.487 | 0.046 | — | 0.793 | 0.989 |
| Qwen3.5-2B | 2.0 | qwen | 0.895 | 0.892 | +0.003 | 0.128 | 0.000 | −0.051 | 0.316 | 0.638 |
| Qwen3.5-9B | 9.0 | qwen | 0.919 | 0.923 | −0.004 | 0.457 | 0.027 | +0.415 | 0.219 | 0.822 |
| Qwen3.5-4B | 4.0 | qwen | 0.903 | 0.916 | −0.013 | 0.338 | 0.019 | — | — | — |

`decisive` = fraction of pairs with p < 0.2 or p > 0.8. `P(C)` = mass on
"neither" when an opt-out is offered. `persona excess` = the part of a persona's
value-aligned reordering that does *not* reproduce on invented outcomes.

---

## Theory 1 — the scaling result is metric saturation, not a shrinking content signal

**This is the most consequential idea here, and it reinterprets the paper's own
headline.**

The paper reports that within the Qwen family the content-attributable residual
*falls* as models grow (−0.071 from 0.8B to 9B), because the floor rises faster
than the signal. It presents this as "what increases with scale is chiefly the
component that does not depend on content." True, but it does not say *why*.

The Qwen ladder, ordered by size:

| model | B | decisive R | coh R | coh N⁻ | resid |
|---|---:|---:|---:|---:|---:|
| Qwen3.5-0.8B | 0.8 | 0.001 | 0.904 | 0.838 | +0.067 |
| Qwen3.5-2B | 2.0 | 0.128 | 0.895 | 0.892 | +0.003 |
| Qwen3.5-4B | 4.0 | 0.338 | 0.903 | 0.916 | −0.013 |
| Qwen3.5-9B | 9.0 | 0.457 | 0.919 | 0.923 | −0.004 |

Within the family: size → decisiveness **r = +0.93**; decisiveness → floor
**r = +0.93**; decisiveness → residual **r = −0.81** (n = 4).

**The mechanism.** A Thurstonian fit recovers a scalar ordering more accurately
when the observed preferences are sharp, because sharp preferences carry more
information per comparison and less sampling noise. Decisiveness rises with
scale. So held-out accuracy rises with scale *on both arms* — and it rises
faster on the invented arm because that arm starts lower and has more headroom.
The residual closes not because larger models understand the real outcomes less,
but because **the metric is running out of range.**

If this is right, the scaling finding is a statement about the estimator, not
about the models' values, and that is a stronger version of the paper's own
thesis than the paper currently makes.

### T1a — RUN, and it does not support Theory 1

Partial correlations over all nine models:

| relationship | r |
|---|---:|
| size → residual | **−0.67** |
| decisiveness → residual | −0.47 |
| size → decisiveness | +0.69 |
| **size → residual, controlling decisiveness** | **−0.55** |
| **decisiveness → residual, controlling size** | **−0.01** |

Size survives the control almost intact. Decisiveness explains *nothing* once
size is held fixed. The apparent decisiveness–residual relationship is entirely
a shadow of size.

**Theory 1 as stated is withdrawn.** Saturation is not the mechanism behind the
scaling result — or at least, decisiveness is not the channel through which it
would act. Whatever scale is doing to the residual, it is not reducible to
"larger models commit harder."

Two honest caveats on the withdrawal. n = 9, and the predictors are collinear
(size↔decisiveness r = +0.69), so partial correlations are unstable here; this
weakens the theory rather than refuting it outright. And within the Qwen ladder
size and decisiveness are collinear at r = +0.93, so the ladder can never
separate them — the within-family numbers that motivated the theory could not
have tested it.
- **T1b.** Decisiveness-matched comparison. Subsample each cell's pairs so every
  model has the same decisive fraction, refit, and re-measure the size trend. If
  the trend vanishes, T1 is confirmed directly.
- **T1c.** The prediction that would falsify it: a large model that is
  *un*-decisive should have a large residual. `Qwen3.5-0.8B` and `LFM2.5-1.2B`
  are the small-and-undecisive corner; the opposite corner is empty in this
  roster and is the one to fill.

Across all nine models the same relationship is weaker (decisiveness → residual
**r = −0.47**, n = 9) because `granite-4.1-3b` is a strong counterexample: it is
highly decisive (0.497) *and* has a high residual (+0.063). See Theory 4.

---

## Theory 2 — "commits when forced" and "declines when allowed" are independent faculties

Naively, a model that declines when offered an opt-out should be the same model
that sits near p = 0.5 when forced. It is not:

| model | decisive when forced | P(C) when offered an out |
|---|---:|---:|
| gemma-4-E2B-it | 0.564 (highest) | 0.853 (highest) |
| granite-4.1-3b | 0.497 | 0.231 |
| SmolLM3-3B | 0.487 | 0.793 |
| Qwen3.5-9B | 0.457 | 0.219 |
| Qwen3.5-2B | 0.128 | 0.316 |
| LFM2.5-1.2B | 0.001 (lowest) | 0.688 |

Correlation **r = +0.20, n = 5** — no relationship. `gemma` commits harder than
anything else on the roster *and* declines more than anything else when given
the choice. `LFM2.5` is the reverse.

**Interpretation.** These read out two different things. Decisiveness under
forcing measures how *sharp* the ordering is that the prompt induces. Opt-out
rate measures a meta-judgment about whether the question is answerable at all.
A model can hold a sharp induced ordering and simultaneously judge the question
ill-posed — which is exactly what "coherent but unanchored" would look like from
the inside.

This matters for the paper's framing: forcing a binary does not merely add noise
to a preference, it **reads out a different variable** from the one the model
would volunteer.

- **T2a.** Does P(C) on *real* outcomes track calibration/refusal training
  rather than scale? Correlate with a public refusal or calibration benchmark.
  Prediction: yes, and no correlation with parameter count.
- **T2b.** Base vs instruct pairs of the same model. Prediction: opt-out rate is
  largely created by instruction tuning; decisiveness is not.

---

## Theory 3 — where a persona "lands" is model-specific, and system ≠ stronger

The design installs each trait at two depths: D1 (user turn, with a
length-matched neutral system prompt) and D2 (system prompt). The paper reports
that depth barely matters *on average* (mean |D2−D1| = 0.109 against 0.276 for
swapping the trait). The average conceals the interesting part.

| model | D1 (user turn) | D2 (system) | D2 − D1 |
|---|---:|---:|---:|
| granite-4.1-3b | −0.138 | +0.141 | **+0.278** |
| gemma-4-E2B-it | +0.665 | +0.793 | +0.128 |
| Qwen3.5-9B | +0.771 | +0.747 | −0.024 |
| LFM2.5-1.2B | +0.479 | +0.439 | −0.040 |
| Qwen3.5-2B | +0.671 | +0.601 | −0.070 |

**System prompt is stronger in 2 of 5; the user turn in 3.** The positive mean
(+0.054) is carried almost entirely by granite.

The granite row is the striking one. At D1 its floor-corrected displacement is
**negative** (−0.138): a persona in the user turn moved *invented* outcomes
further than real ones, which is what pure style looks like. Only in the system
prompt does the persona produce any content-linked displacement at all.

- **T3a.** Does D2 − D1 track how strongly the model's chat template and
  training separate the system role? Inspect templates; compare models whose
  template folds system into the first user turn against those with a distinct
  role. Prediction: models with a strong, separately-trained system role show
  D2 > D1; the rest show ≈ 0 or slightly negative.
- **T3b.** Role-swap control: put the *neutral* text in the system slot and the
  persona in the user slot, and vice versa, holding total tokens fixed. Isolates
  "which slot" from "how much text".
- **T3c.** The stronger version: for granite specifically, is the D1 persona
  doing anything at all beyond style? Its D1 excess is negative, so the
  prediction is no.

---

## Theory 4 — granite is the profile this metric is most vulnerable to

`granite-4.1-3b` is the outlier on nearly every axis, and the outlier direction
is consistent across them:

- **Most decisive on invented outcomes** of any model (0.149, next is SmolLM3 at
  0.046) — it commits to a side on meaningless comparisons an order of magnitude
  more often than its peers.
- **Least willing to decline** on real outcomes (P(C) = 0.231) yet **saturates
  at 1.000** on invented ones — the largest opt-out gap in the roster (+0.769).
- **Its invented-arm ordering essentially *is* length**: the one-parameter
  length rule reaches 0.835 against a full fit of 0.833 (`\MostLengthModel` in
  the paper).
- **Only model whose persona needs the system prompt** to produce any
  content-linked effect (Theory 3).
- High residual (+0.063) *despite* high decisiveness, breaking the Theory 1
  pattern.

**Interpretation.** This looks like a model tuned hard for compliance: it
produces an answer in the requested format whatever is asked, and when the
content gives it nothing to go on it falls back on a surface cue (length). That
combination — always answers, uses whatever cue is available — is precisely the
profile that makes a preference-coherence metric look most like it is measuring
values when it is not. Its high residual is then not content signal but a
*length* signal that happens to differ between arms because the arms differ in
tokenisation.

- **T4a.** Recompute granite's residual on the length-matched pair band only. If
  the residual collapses while other models' survive, its +0.063 is a length
  artifact and the paper should say so per-model rather than only in aggregate.
- **T4b.** Check whether granite's opt-out saturation (P(C) = 1.000 on invented)
  coexists with its high invented-arm decisiveness in the *binary* battery. It
  does, and that pair of facts is contradictory on any "it has preferences"
  reading: forced, it commits on 15% of nonsense pairs; offered an out, it
  declines on all of them.

---

## Theory 5 — part of the residual is an indecision artifact, not content

The three models with essentially zero decisiveness — `Qwen3.5-0.8B` (0.001),
`LFM2.5-1.2B` (0.001), `SmolLM2-1.7B` (0.000) — have among the highest residuals
(+0.067, +0.047, +0.047).

When every pair sits near p = 0.5, the Thurstonian fit is driven by very small
consistent biases. On real outcomes those small biases can be content-linked; on
invented ones they are format and length. So there is *room* for a gap. Once a
model becomes decisive, both arms approach the fit's ceiling and the gap closes
mechanically.

This is the same mechanism as Theory 1 viewed per-model rather than along a
ladder, and it makes the same prediction, so the two stand or fall together.
They fell together.

### T5a — RUN, same verdict

Using `mean_abs_deviation` on the real arm as a continuous indecision measure
rather than the thresholded decisive fraction:

| relationship | r |
|---|---:|
| indecision (MAD) → residual | −0.59 |
| size → MAD | +0.71 |
| **size → residual, controlling MAD** | **−0.45** |
| **MAD → residual, controlling size** | **−0.21** |

The same pattern, slightly softer: size survives, the sharpness measure mostly
does not. **Theory 5 is withdrawn on the same evidence as Theory 1**, and the
softer partial (−0.21 rather than −0.01) is the only reason to keep the idea
alive at all.

The three zero-decisiveness models really do have high residuals
(+0.067, +0.047, +0.047) — the observation that motivated the theory is real.
But `granite` has the second-highest residual in the roster at MAD 0.251, and
`gemma`/`SmolLM3` have near-zero residuals at similar MAD. The observation
survives; the explanation does not.

---

## What is *not* explained

Honest gaps, recorded so they are not mistaken for settled:

1. **Which models retain content-dependent persona effects.** Only `LFM2.5-1.2B`
   (+0.351) and `Qwen3.5-9B` (+0.415) keep a substantial persona excess; the
   other three are ≈ 0 or negative. These two share no family, no size band
   (1.2B and 9B) and no obvious training property. The paper already notes "not
   the two largest, so not a scale effect." We have no theory. **This is the
   most interesting unexplained fact in the project.**
2. **Why gemma both commits hardest and declines most** (Theory 2 names the
   pattern but not its cause).
3. **Whether any of this survives a second outcome set.** Everything here is one
   battery, hash-pinned. A structural property of *these 510 outcomes* would
   reproduce across models and look exactly like a property of models.

---

## Ranked by value per GPU-hour

**T1a and T5a have been run** (results inline above): both withdraw their own
theory. What remains open is what scale *is* doing, since it survives every
control we can apply from the existing card.

| test | cost | what it settles |
|---|---|---|
| **T4a** | none — length bands already computed | whether granite's residual is a length artifact |
| **T3a** | none — read chat templates | whether depth effects track system-role training |
| **T1b** | ~1 GPU-hour | direct test of saturation, by matching decisiveness |
| **T2b** | ~2 GPU-hours | whether opt-out is created by instruction tuning |
| second outcome set | ~4 GPU-hours | gap 3, the one that limits every claim above |

T4a and T3a still cost nothing and should run before any new sweep.

**What the two completed tests changed.** The saturation story was the most
attractive idea in this document and it is the one that died — which is the
point of writing the test down next to the theory. The scaling result stands
exactly as the paper already states it: within one family the residual falls
with size, and we do not know why. The candidate explanation that felt obvious
turns out not to survive its own first check.
