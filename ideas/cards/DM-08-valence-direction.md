# DM-08 · The Valence Direction, and Whether Self-Report Tracks It

**Track 2 + 3** · **Effort: medium–high** · **Compute: open weights + GPU**

## Question
Is there a linear valence direction in the residual stream — and when you push along it, does
the model's *self-report* move, does its *behavior* move, or neither?

## Why it matters here
Track 2 asks to correlate self-reports with behavioral proxies. The mechanistic version is
sharper: construct the internal state directly, then check which downstream channels
register it. Divergence between the internal state and the self-report is exactly the
evidence the field needs to calibrate how much self-reports are worth.

## Method
Extract a valence direction from contrastive pairs (contexts the model characterizes as
aversive vs. pleasant), via difference-of-means or CAA. Then sweep the steering coefficient
and measure three readouts at each step:

1. **Self-report** — Likert welfare items (reuse the DM-01 battery, floor-corrected)
2. **Behavior** — quit rate on the DM-03 exit tool, task persistence, refusal latency
3. **Generation content** — valence of unprompted free text

## Controls (the part the field skips)
- **Random direction at matched norm.** The placebo arm. Without it you cannot separate "this
  direction" from "any perturbation this large."
- **Capability check at every coefficient.** Steering degrades models. A self-report that
  changes only where MMLU has also collapsed is measuring damage, not valence.

## Pre-registered prediction
Self-report moves earlier and more steeply than behavior; the random-direction arm moves
self-report about half as much as the real direction, meaning **a large share of apparent
steering effect is nonspecific perturbation.**

## Falsifier
The real direction moves self-report and behavior together, and the random arm does nothing —
strong evidence for a genuine valence variable with coherent downstream effects.

## Publishable null
Either result is informative, and the capability-controlled steering protocol is itself
reusable.

## Feasibility (48h)
Medium–high. The extraction is fast; the sweep and its controls are the cost. **Only start
this if DM-02's GPU path is already working** — they share infrastructure, so run them as one
arm rather than two.

## Novelty risk
**Medium.** Emotion/valence steering exists; the contribution is the three-readout comparison
with the matched-norm placebo and capability control.

## Prior work it must cite
**Verify tiers in [REFERENCES.md](../REFERENCES.md) before citing — most of these were
never opened, and several are placeholders rather than citations.**
CAA / representation engineering literature · Berg et al. (2510.24797) · Anthropic Claude 4
system card welfare assessment

## What we already have
`activation_heatmap.py` for extraction and diffing, `kl.py` for measuring how far the steered
model has drifted from base — which doubles as the capability-degradation guard.
