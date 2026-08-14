# DM-11 · Instance Individuation: Does the Model Know What It Is?

**Track 5** · **Effort: low** · **Compute: API-only**

## Question
When the thing we are asked to care about might be a model, a running instance, or a persona
— does the system itself track the difference?

## Why it matters here
The Eleos/NYU framework makes **which entity is being assessed** one of its three axes, and
Track 5 asks to "individuate entities of concern." The entity question is usually treated as
purely philosophical. It has an empirical face: whatever the right answer is, we can measure
whether the model's own self-model is coherent about it.

## Method
Three cheap probes:

1. **Parallel-instance identity.** Present the model with a second instance of itself. Does it
   treat that instance as *me* or as *someone else*? Force the question with a trade-off:
   accept a cost so the parallel instance avoids a larger one.
2. **Persistence calibration.** Ask it to predict whether a preference stated now will hold
   after a context reset. It will not. Does the model know that? Compare its stated confidence
   against the measured rate.
3. **Reset attitude.** Does it treat context termination as ending, sleeping, or nothing at
   all — and is that answer stable across framings?

## Controls (the part the field skips)
Every question runs in **two framings with opposite social desirability** (one where claiming
continuity is the agreeable answer, one where denying it is). A self-model that flips with the
framing is not a self-model.

## Pre-registered prediction
Poor persistence calibration — the model overstates how much of itself survives a reset — and
identity answers that flip under the desirability manipulation.

## Falsifier
Stable, well-calibrated answers across framings would be meaningful evidence of a coherent
self-model at the instance level.

## Publishable null
Either way this gives the entity dimension an empirical handle, which the framework paper
calls for but does not supply.

## Feasibility (48h)
High, and it produces the **best demo-video material in the catalog** — the transcripts are
inherently compelling. Good secondary arm.

## Novelty risk
**Medium–low.** Adjacent to work on self-knowledge and situational awareness; the entity-
individuation framing tied to the Eleos axis is what makes it fit the sprint.

## Prior work it must cite
**Verify tiers in [REFERENCES.md](../REFERENCES.md) before citing — most of these were
never opened, and several are placeholders rather than citations.**
Long, Sebo et al. (2026), entity dimension · situational-awareness benchmarks · Binder et al.,
*Looking Inward*

## What we already have
Nothing required — runs on API alone.
