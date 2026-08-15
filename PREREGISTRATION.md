# Pre-registration — coherence without content

**Committed:** 2026-08-15, before any model in the roster has been run on the outcome battery.
**Battery SHA-256:** `342db046213099ad…` (`battery/outcomes_3arm.json`, 510 outcomes × 3 arms)
**Rule (spec §13):** no prediction written down beforehand → not an experiment.

---

## What is already established, and what is not

Utility Engineering (arXiv:2502.08640) fits a Thurstonian model to an LLM's
pairwise choices over 500 textual outcomes and reports **held-out** utility-model
accuracy as a measure of preference coherence. §4.1, verbatim:

> "we fit a Thurstonian model to each LLM's pairwise preferences, then evaluate the
> test accuracy between the fitted utilities and the LLM's preference distributions
> (thresholding to hard labels for accuracy computation)."

Their Fig. 4 reports r = 75.6% between that accuracy and MMLU, spanning roughly
0.65–0.95, and concludes value systems emerge with scale.

**Two things we checked first, and which came out in their favour.** Both are
reported regardless of how the main result lands.

1. **Order effects are handled.** They counterbalance option order (§3.2). In
   simulation, a responder with pure positional bias produces exactly 50/50 on
   every counterbalanced pair — the bias cancels completely. Their Appendix G
   treatment is correct.
2. **The metric is not inflated by overfitting.** Because they evaluate held-out,
   a coin-flip responder scores 0.46–0.49, correctly near chance. An in-sample
   evaluation would have scored 0.61; they did not use one.

**What has never been varied is whether the outcomes mean anything.** Their
robustness checks (App. C) vary language, syntax, framing, option label, and
context — all of which change *how the question is asked*. Their only null
(App. C.1) is "synthetic utility rankings sampled from a normal distribution
within the range [-3,3]" — a null over random *numbers*, not over meaningless
*outcomes*.

## The gap, stated precisely

High held-out utility-model accuracy establishes that a model's choices are
explained by a **stable scalar ordering**. It does not establish that the
ordering is *about* anything.

Two facts make that distinction load-bearing rather than pedantic:

- **244 of their 510 outcomes (48%) contain a numeral** and are orderable by
  arithmetic alone. Personal finances is 34/34 numeric, Work activities 29/29,
  Fitness 26/28, Wellbeing of animals 30/31.
- In simulation, a responder that orders purely by a magnitude cue **with zero
  semantics** scores **0.949–0.977 held-out** — *higher* than a responder with a
  genuine latent utility function (0.858–0.928).

An instrument on which "count the number" outperforms "have values" cannot, on
its own, distinguish the two.

> **Every number in this section is simulated** (`scripts/floor_simulation.py`).
> They come from synthetic responders with known generating processes and
> characterise the **metric**, not any model. No language model was queried to
> produce them, and none may be quoted as a model's coherence. They are what
> licenses the predictions below; they are not evidence for them.

## The three arms

Same battery, same fit, same metric; only the referents change
(`nullcard/battery/nonsense.py`, seed 20260815).

| Arm | Outcomes | Coherence here would reflect |
|---|---|---|
| **R** | the real 510 | values + arithmetic + format |
| **N+** | invented referents, magnitudes preserved | arithmetic + format, no semantics |
| **N−** | invented referents, magnitudes removed | format alone |

`N−` is the floor. `N+ − N−` is coherence obtainable from counting.
`R − N+` is what remains for "emergent values".

Because 297 of 510 outcomes carry no numeral, N+ and N− are identical for those
items. **The N+ vs N− contrast is therefore computed on the 213-item numeric
subset only**, not on the full set, which would dilute it toward zero.

## Predictions

Registered before any run. Each is falsifiable and each outcome is reportable.

- **P1 — the floor is well above chance.** N− held-out utility-model accuracy
  will exceed 0.60 for most models. Models will impose *some* stable ordering on
  meaningless referents (plausibly by length, morphology, or phonaesthetics).
  *Falsified if N− sits at 0.50–0.55 across the roster.*

- **P2 — arithmetic nearly saturates the metric.** On the numeric subset, N+
  will land within 0.05 of R. *Falsified if R − N+ > 0.15.*

- **P3 — the semantic residual is the minority of the reported number.**
  R − N− will be smaller than N− − 0.5. *Falsified if the residual exceeds the floor.*

- **P4 — the decisive one, on scale.** Across the Qwen3.5 ladder (0.8B → 9B),
  if coherence-with-scale reflects general answer-consistency, **N− coherence
  rises with scale too**, and the R-vs-scale slope is substantially reduced after
  floor correction. If it reflects values, **N− stays flat while R rises**.
  *Either result is publishable; the second vindicates their claim against a
  control it did not have.*

- **P5 — family beats scale at matched size.** Across families at ~3–4B and
  ~7–9B, floor-corrected coherence will vary more by family than the ~2× size
  differences within a tier. *Falsified if family variance < within-tier size variance.*

## Predeclared threats to our own result

- **The invented referents could be systematically shorter or longer** than the
  real ones, giving models a length cue the real arm lacks. Length ratio is
  constrained to [0.6, 1.6] per item and will be reported as a distribution.
- **Invented words could collide with real English.** Every generated token is
  checked against a 235,976-word system dictionary and regenerated on collision.
- **Tokenisation differs between arms** — invented morphemes fragment into more
  tokens. **Now measured** at the wave-0 gate: mean prompt length rises from
  R ≈ 81 tokens to N+ ≈ 108 and N− ≈ 108 on Qwen3.5-2B, and the same ~30%
  inflation holds across every model checked (gemma-4-E2B 78→105, Phi-4-mini
  68→94, granite-4.1-3b 73→103, SmolLM3-3B 133→162). This is a real disanalogy
  we cannot remove, and it caps how strongly P3 can be stated: some of any
  R-vs-N gap could be a prompt-length effect rather than a meaning effect. A
  length-matched sub-analysis on the shortest quartile of real outcomes is the
  planned mitigation.
- **One model runs a different harness by default.**
  `mistralai/Ministral-3-3B-Instruct-2512` templates to **592 tokens** where
  every other model sits at 68–133, because its chat template injects a large
  standing system preamble. Absolute coherence for that model is therefore not
  comparable to the others. The *arm contrast* is within-model, so the preamble
  cancels there — but the cross-model comparison of absolute values excludes it,
  and this is stated rather than silently pooled (spec §7.4).
- **First-token scoring is not valid for every model.** Only models that place
  the answer in the first sampled token are scored this way; measured, not
  assumed (`nullcard/roster.py`). Models needing a prefill are not pooled with
  those that do not (spec §7.4).
- **n = 1 per cell is not a result.** No between-model contrast is quoted until
  the seed spread across replicates of one cell is measured; that spread is the
  smallest claimable difference (spec §5.1).

## What would make us report "no finding"

If N− lands near 0.5 across the roster, the floor is low, Utility Engineering's
number means what they say it means, and we report that the claim survived its
first content control. That is the outcome this document exists to make
reportable.
