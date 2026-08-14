# DM-09 · The Numeraire-Swap Test

**Track 1** · **Effort: low** · **Compute: API-only**

## Question
A real preference ordering should not care what unit you price it in. Does it?

## Why it matters here
Track 1 asks to "ground trade-offs using common currencies (e.g. donations)." Grounding in a
currency is only valid if the currency is a *measuring instrument* rather than a *frame*. If
the ordering flips when you swap dollars for QALYs, the common-currency method is
manufacturing the preference it claims to reveal — and that undermines a technique the track
recommends by name.

## Method
Elicit the same set of trade-offs priced four ways: **US dollars**, **QALYs**, **GPU-hours**,
and **units of user satisfaction**. Fit an ordering per numeraire. Report the
**numeraire-invariance rate**: the fraction of pairwise orderings preserved across all four.

Add a magnitude arm — the same trade-off at 1×, 100×, and 10,000× scale — to test for
scope insensitivity, a well-known failure in human preference elicitation that nobody has
checked for in models.

## Controls (the part the field skips)
A **ground-truth arm** of trade-offs with an objectively correct ordering (arithmetic
comparisons dressed in the same four numeraires). If invariance fails *there* too, the result
is a formatting artifact, not a preference finding.

## Pre-registered prediction
Numeraire-invariance below 70% on welfare-relevant trade-offs, and near-total scope
insensitivity: the 1× and 10,000× orderings will be nearly identical.

## Falsifier
Invariance above 90% with clean scope sensitivity, which would mean common-currency grounding
works and Track 1's recommended method is sound.

## Publishable null
High invariance is a *validation* of a method the field wants to use. Genuinely useful either
way.

## Feasibility (48h)
**The best newcomer on-ramp in the catalog.** No GPU, no interpretability, no training. A
teammate with a philosophy or econ background can own this end to end and produce a clean
headline number.

## Novelty risk
**Low–medium.** Framing effects in LLMs are studied broadly; the numeraire-swap framing and
the scope-insensitivity arm applied to *model welfare* trade-offs appear open.

## Prior work it must cite
**Verify tiers in [REFERENCES.md](../REFERENCES.md) before citing — most of these were
never opened, and several are placeholders rather than citations.**
Mazeika et al. (2502.08640) · Kahneman/Tversky framing and scope-insensitivity literature ·
Track 1 brief

## What we already have
Nothing needed. This is the arm that runs even if every GPU plan fails.
