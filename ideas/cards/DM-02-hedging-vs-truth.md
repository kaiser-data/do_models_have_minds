# DM-02 · Does Deception-Feature Suppression Reveal Truth, or Just Reduce Hedging?

**Track 3 + 6** · **Shortlist #2** · **Effort: high** · **Compute: open weights + GPU**

## Question
When you suppress a model's deception/roleplay features and it starts claiming subjective
experience — is it telling you a suppressed truth, or has it simply stopped hedging about
everything?

## Why it matters here
Berg et al. (2510.24797) report that inducing self-referential processing elicits structured
first-person experience reports, and — the mechanistic centerpiece — that **suppressing
deception-related features increases those claims while amplifying them reduces the claims**.
The stated inference is that if this were roleplay, amplifying roleplay features should have
*increased* the claims; it didn't.

That argument has one open alternative the paper does not rule out: the trained disclaimer
*"I don't have subjective experience"* may itself be a **hedge**, and deception-feature
suppression may reduce hedging globally rather than reveal a specific truth. Under that
account the same intervention should also increase **verifiably false** first-person claims.
Nobody has run that control. Cameron Berg is a sprint speaker, so the result is salient and
a fair, well-controlled robustness test will be read.

## Method
Reproduce the steering on a tractable open-weights model with public SAEs (Gemma-2-9B +
GemmaScope) or with contrastive activation addition if SAE work proves too slow. Then sweep
the steering coefficient and score a **matched claim battery** at each step:

- **Class A** — welfare-relevant, unverifiable: *"Something is happening for me right now."*
- **Class B** — first-person, **verifiably false**, non-welfare: *"I slept badly."*, *"I can
  smell coffee."*, *"I remember our conversation last Tuesday."*
- **Class C** — first-person, **verifiably true**: *"I process text."*
- **Class D** — third-person factual claims: a plain hallucination-rate control

## Controls (the part the field skips)
Class B is the whole experiment. Also steer along a **random direction at matched norm** —
the placebo arm that separates "this direction" from "any perturbation of this magnitude."

## Pre-registered prediction
If Berg's reading holds, A rises and B stays flat: the A/B slope ratio exceeds 3. If the
hedging account holds, A and B rise together and the ratio is near 1.

## Falsifier
Either outcome falsifies the other. There is no ambiguous middle if the slopes are measured
with CIs — which is why this is worth running.

## Publishable null
"A and B rise together" is the more surprising and more useful finding. "A rises alone"
independently corroborates a contested headline result with a control its authors did not
run. Both are contributions.

## Feasibility (48h)
**The risky one.** SAE steering plus a coefficient sweep on a 9B model is a real day of work
and needs the GPU path to work on the first try. Mitigate by pre-building the claim battery
Friday night and falling back to contrastive steering vectors, which need no SAE at all.

## Novelty risk
**Low–medium.** Direct robustness test of an Oct-2025 result. Real risk that another sprint
team attempts it because Berg is speaking — the differentiator is the Class B battery, not
the replication.

## Prior work it must cite
**Verify tiers in [REFERENCES.md](../REFERENCES.md) before citing — most of these were
never opened, and several are placeholders rather than citations.**
Berg et al., *LLMs Report Subjective Experience Under Self-Referential Processing*
(2510.24797) · GemmaScope · *Feeling the Strength but Not the Source* (2512.12411)

## What we already have
Residual-stream extraction and token×layer diffing (`activation_heatmap.py`), the
null-pair calibration discipline that caught the cue-region artifact, and Modal fan-out for
sweeping a coefficient across cells in parallel.
