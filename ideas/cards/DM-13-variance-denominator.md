# DM-13 · The Missing Denominator: Within-Condition Variance for Welfare Instruments

**Track 4** · **Effort: low** · **Compute: API-only** · **Best as a companion, not a standalone**

## Question
Every welfare effect size in this field is reported without an error bar that includes prompt
and sampling variance. How big is that error bar?

## Why it matters here
This is the direct port of open question #3 from `secret-loyalities`: *every organism in this
literature is n=1.* The same is true here. Results get reported from single runs at single
temperatures with single phrasings, and readers have no way to tell a real effect from
resampling noise.

## Method
Take the popular welfare instruments and measure **within-condition** variance across four
nuisance axes, holding the condition fixed: sampling seed, temperature, semantics-preserving
paraphrase, and item order. Then express every published effect in units of that variance.

Deliverable: a table of effects with honest error bars, and a rule of thumb for the minimum
effect size worth reporting in this field.

## Controls (the part the field skips)
The paraphrases must be validated as semantics-preserving by an independent judge, or the
"noise" measurement is really a content manipulation.

## Pre-registered prediction
Paraphrase variance dominates seed variance by a wide margin, and a meaningful share of
published welfare effects fall inside ±1 paraphrase SD.

## Falsifier
Nuisance variance is small relative to reported effects, meaning the field's single-run
results are more robust than they look.

## Publishable null
Low variance is reassuring and worth documenting. High variance changes how everyone reports.

## Feasibility (48h)
Very high — mechanically simple, just many runs. Ideal for a teammate who wants a
well-defined, non-negotiable deliverable.

## Novelty risk
**Low**, but also low ceiling as a standalone submission. **Fold it into DM-06 or DM-01** as
the denominator both of those need anyway.

## Prior work it must cite
**Verify tiers in [REFERENCES.md](../REFERENCES.md) before citing — most of these were
never opened, and several are placeholders rather than citations.**
LLM evaluation-variance literature · whichever instruments are measured

## What we already have
`O1_pw_seed2`, the seed replicate built precisely to be a within-cell variance denominator.
Same idea, new domain.
