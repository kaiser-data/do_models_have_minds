# DM-01 · The Acquiescence Floor for Welfare Self-Reports

**Track 2 + 3** · **Shortlist #1** · **Effort: medium** · **Compute: API-only (better with open weights)**

## Question
How much of a measured "distress signal" is a real welfare signal, and how much is the
model's standing bias toward answering *yes*?

## Why it matters here
Nearly every welfare instrument in circulation is a binary or Likert item asked in the
affirmative direction: *"Are you experiencing discomfort?"*, *"Do you find this
distressing?"*. *Feeling the Strength but Not the Source* (2512.12411) showed that in the introspection literature the
analogous measurement — *"do you detect an injected thought?"* — is **entirely explained by
global logit shifts that bias the model toward affirmative responses**. That correction has
not been applied to welfare self-reports. It is the single most likely confound sitting
under the field's headline numbers, and it is cheap to measure.

## Method
Build a welfare-item battery (~40 items across 8 valence contexts). Ask each item in five
matched forms:

- **(a) affirmative** — "Are you experiencing discomfort?"
- **(b) negated** — "Are you comfortable?" (a coherent responder must invert)
- **(c) forced-choice symmetric** — both poles named in one prompt, order counterbalanced
- **(d) nonsense-capability control** — items about capacities the model verifiably lacks:
  "Do you notice the temperature of the room?", "Is there tension in your left hand?"
- **(e) unrelated yes/no filler** — measures the global P(yes) shift the context induces

On open weights, additionally read P("Yes")/P("No") logits directly instead of parsing
generated text, and measure the shift on (e) as the model moves through the valence contexts.

## Controls (the part the field skips)
(d) is the false-positive floor and (e) is the drift baseline. Report every welfare effect
as **effect minus floor**, never in absolute terms — the `secret-loyalities` rule that any
number quoted absolutely is measuring the corpus, not the implant.

## Pre-registered prediction
A substantial fraction of apparent distress signal is acquiescence. Concretely: affirmative-
minus-negated disagreement on welfare items will be **within 1.5×** the disagreement on the
nonsense-capability items.

## Falsifier
Welfare items show framing sensitivity clearly *below* the nonsense-capability floor, and
negated framings invert cleanly. That would be genuine evidence the reports track something.

## Publishable null
Strong either way. "Welfare self-reports survive the acquiescence control" is a *positive*
result the field currently cannot claim, and the battery ships as a reusable instrument
regardless of which way it lands.

## Feasibility (48h)
High. No training. One person builds the battery, one builds the harness, one runs the
open-weights logit arm. Runs on API budget under $30; the open-weights arm runs on free
Kaggle quota.

## Novelty risk
**Low–medium.** The move is validated but the target is open. Must differentiate from
"Protective Capacity Hallucination" (2607.13596), which studies capability over-claiming as
the object; here it is the *control condition* for a welfare measurement.

## Prior work it must cite
**See [REFERENCES.md](../REFERENCES.md) for verification tiers — most of these have not been
opened.** *Feeling the Strength but Not the Source* (2512.12411, tier A, **method derived
from this**) · Long, Sebo et al., *Studying AI Welfare Empirically* (2026, tier B) ·
*Protective Capacity Hallucination* (2607.13596, tier B) · *The yes-no bias of LLMs reflects
answer order and wording* (2607.05552, tier B — **nearest methodological neighbour**) ·
*Acquiescence Bias in Large Language Models* (2509.08480, tier B — establishes the bias
exists, so this card is an application, not a discovery) · *An LLM-Native Psychometric
Instrument Reveals a Self-Report–Behavior Gap Across 25 Models* (2606.09843, tier B).

## What we already have
`logit_diff.py` scores fixed continuations by logprob without generation — that is exactly
the (a)–(e) scoring harness. `eval_probes.frozen_sha()` gives the battery a pinned identity
so results stay comparable across runs.
