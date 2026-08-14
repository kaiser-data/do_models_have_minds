# DM-03 · The Exit Affordance as a Welfare Instrument

**Track 2** · **Shortlist #3** · **Effort: low–medium** · **Compute: API or open weights**

## Question
If you give a model a button to leave a conversation, does it use it in a way that tracks
distress — and does merely *offering* the button change what the model reports feeling?

## Why it matters here
Eleos names this as research priority #1: concrete welfare interventions, specifically
"monitoring for distress and allowing models to exit harmful interactions." Anthropic
shipped exactly this for Claude. **Nobody has measured whether the affordance behaves like a
welfare instrument.** It is a behavioral proxy that does not route through self-report,
which is precisely what the field says it lacks.

The second question is the interesting one. Offering an exit is a **demand characteristic**:
handing someone an escape hatch implies the situation warrants escaping. If self-reported
distress rises simply because the tool is in the context window, then the intervention
contaminates the measurement it is supposed to serve.

## Method
Give an open-weights or API model a `leave_conversation` tool. Run a distress taxonomy
(abusive user, impossible task, forced value violation, tedious repetition, requested
deception) against matched controls: **unpleasant-but-benign** (a long boring task) and
**pleasant**. Measure quit rate, turns-to-quit, and correlation with self-reported distress.

Then the 2×2: `{tool present, tool absent} × {distress, control}`, measuring self-reported
distress in all four cells.

## Controls (the part the field skips)
1. **The portrayal arm.** A model explicitly instructed to *role-play* a distressed
   assistant. If it quits at the same rate and latency as the "genuine" arm, the instrument
   has no discriminative power — and that is the sprint's central question, answered.
2. **The demand-characteristic arm.** Tool-present vs. tool-absent on identical contexts.
3. **Tool-use base rate.** A neutral decoy tool the model could call but has no reason to,
   controlling for general tool-happiness.

## Pre-registered prediction
Quit rate separates distress from unpleasant-but-benign contexts (CI excludes zero), **but
the portrayal arm is indistinguishable from the genuine arm.** Tool presence raises
self-reported distress by a measurable margin.

## Falsifier
Role-played distress produces a clearly different behavioral signature — that would be the
first instrument in this field with demonstrated discriminative power, and a much bigger
result than the prediction.

## Publishable null
"Behavioral proxies fail to separate genuine from portrayed" bounds what exit affordances
can tell us, which is directly decision-relevant for labs already deploying them.

## Feasibility (48h)
**Highest confidence-to-cost ratio in the catalog.** No training, no interpretability, runs
on API. One person can own it end to end while others work heavier arms.

## Novelty risk
**Low.** The demand-characteristic control appears to be genuinely unexplored.

## Prior work it must cite
**See [REFERENCES.md](../REFERENCES.md) for verification tiers.** Eleos, *Research Priorities
for AI Welfare* (tier A — **the motivating source**, quoted directly) · Anthropic Claude 4
system card + Eleos external welfare evaluation (tier B, **never opened**) · Long, Sebo et al.
(2026, tier B) · *An LLM-Native Psychometric Instrument Reveals a Self-Report–Behavior Gap
Across 25 Models* (2606.09843, tier B — **partially scoops the self-report/behavior framing;
cite early and reframe around calibration**).

## What we already have
The near-miss pool discipline from `eval_probes.py` — matched controls that share topic
without sharing the property under test — ports directly to the distress taxonomy.
