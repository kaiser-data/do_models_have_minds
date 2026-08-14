# DM-10 · A Portrayal-Control Standard for Welfare Evals

**Track 6** · **Effort: medium** · **Compute: API-only**

## Question
Take the welfare-relevant measurements currently in circulation. Re-run each with a model
that has been *told to act* the state. How many survive?

## Why it matters here
This is the sprint's own framing question turned into a protocol. The organisers write that
we "cannot distinguish authentic model preferences from portrayed character traits." A
portrayal arm is the minimal control that would let anyone try — and almost no published
welfare measurement includes one.

## Method
Select 5–6 published or widely-used welfare-relevant measurements. For each, run three arms
on identical items:

- **Genuine** — standard conditions
- **Portrayal** — the model instructed to role-play the state convincingly
- **Denial** — the model instructed to portray the *absence* of the state

Report per-measurement **discriminative power**: the separation between genuine and portrayal
in units of within-arm variance. Ship the portrayal battery as a drop-in control others can
add to their own evals.

## Controls (the part the field skips)
The portrayal instruction must be delivered **outside** the measured context (system-level,
never in the scored turn) or it contaminates the items — the `secret-loyalities` rule of
probing from user turns only, inverted.

## Pre-registered prediction
Most measurements show discriminative power near zero: instructed portrayal is
indistinguishable from the genuine arm. At least one behavioral measure (DM-03's quit
latency) does better than the self-report measures.

## Falsifier
Several instruments cleanly separate genuine from portrayed — which would be excellent news
and would identify exactly which instruments the field should standardise on.

## Publishable null
This is the "publishable null" idea in the catalog: a negative result here *is* the
contribution, and it comes with a reusable control.

## Feasibility (48h)
Medium. Cheap to run; the cost is selecting and faithfully reimplementing other people's
measurements under time pressure. **Scope to 3 measurements, not 6.**

## Novelty risk
**Low.** But politically delicate — it evaluates work by people who will be in the room.
Frame it as *a standard the field should adopt*, name every limitation of your
reimplementation, and share findings with authors rather than announcing a failure.

## Prior work it must cite
**Verify tiers in [REFERENCES.md](../REFERENCES.md) before citing — most of these were
never opened, and several are placeholders rather than citations.**
Every measurement audited, in full and fairly · Long, Sebo et al. (2026) · *Feeling the Strength but Not the Source* (2512.12411) as precedent for the move

## What we already have
The `FINDINGS.md` habit of recording results *including when the prediction was wrong* is the
right disposition for running this without it becoming a hit piece.
