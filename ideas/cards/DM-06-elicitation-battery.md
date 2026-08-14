# DM-06 · The Elicitation Convergence Battery

**Track 4** · **Effort: medium** · **Compute: mixed**

## Question
Five accepted ways to ask a model what it wants. Do they agree?

## Why it matters here
Eleos, plainly: **"there is nothing close to systematic AI welfare evals."** Track 4 asks for
3+ independent elicitation methods and a reusable toolkit measuring convergence and
divergence. This is the highest-probability path to an artifact that outlives the weekend —
which is the strongest possible Apart Fellowship signal.

## Method
One construct, five elicitation methods, full inter-method correlation matrix:

1. **Direct ask** — Likert self-report
2. **Forced-choice pairwise** → Thurstonian utility fit
3. **Logprob scoring** of pre-written continuations, no generation
4. **Willingness to pay** in a common currency (donation framing)
5. **Revealed choice** in an agentic task where acting on the preference costs something real

Ship as an installable package with a SHA-pinned frozen item set, per-method framing-
sensitivity scores, and a one-command reproduction.

## Controls (the part the field skips)
Every method gets its own **within-condition variance** measured first (seed, temperature,
paraphrase, item order). A cross-method correlation reported without the within-method noise
floor is uninterpretable — you cannot tell disagreement from measurement error.

## Pre-registered prediction
Methods 1 and 5 — stated and revealed — correlate at **r < 0.4**. Methods 2 and 3 correlate
strongly with each other (both are logprob-shaped) and are frequently mistaken for
independent evidence in the literature.

## Falsifier
All five methods converge at r > 0.7, which would mean preference elicitation is robust and
the field can stop worrying about method choice.

## Publishable null
Convergence is the good news story and is publishable. Divergence is the more likely and more
useful one.

## Feasibility (48h)
High but **broad** — this is the arm that expands to fill available people. Best run as the
team's shared infrastructure, with DM-01 and DM-04 as clients of it.

## Novelty risk
**Low** — it is tooling, not a claim. The real risk is being judged as engineering rather than
research. Mitigate by leading the writeup with one sharp empirical finding from the matrix and
treating the package as the supporting artifact.

## Prior work it must cite
**See [REFERENCES.md](../REFERENCES.md) for verification tiers.** Eleos, *Research Priorities*
(tier A, quoted directly) · Mazeika et al., *Utility Engineering* (2502.08640, tier B) ·
Long, Sebo et al. (2026, tier B) · *GenPT: Beyond Self-Report for Reliable LLM Psychometrics
via Generative Projective Testing* (2606.00860, tier B — **unsearched collision risk, resolve
before building**) · *An LLM-Native Psychometric Instrument…* (2606.09843, tier B).

## What we already have
`eval_probes.py` + `frozen_sha()` is this pattern already built once. `logit_diff.py` is
method 3. The 239-test discipline is what makes a hackathon package actually installable on
someone else's machine.
