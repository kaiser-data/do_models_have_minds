# DM-07 · Privileged Access: Self-Report vs. Probe vs. Outside Judge

**Track 3** · **Effort: medium–high** · **Compute: open weights + GPU**

## Question
Does a model know anything about its own welfare-relevant state that an outside observer
reading the same transcript does not?

## Why it matters here
This is the definitional test of introspection, and Track 3 lists it explicitly ("test
privileged access versus external classification"). The introspection literature has run it
on **injected concepts**. It has not been run on **welfare-relevant states**, which is what
this sprint is about.

## Method
Induce an internal state — via a distress-inducing context, or via valence steering (DM-08) —
then compare three readers of that same state:

- **A. Self-report.** The model describes its own state.
- **B. Linear probe.** A classifier read directly off the residual stream.
- **C. Outside judge.** A *different* model given only the transcript, never the activations.

Introspection requires **A > C**. If **B > A**, the information exists internally but does not
survive to the output — which matches the Qwen-32B finding that detection signal peaks in
middle layers and is attenuated before sampling.

## Controls (the part the field skips)
The outside judge must see **exactly** the text the self-reporting model saw — no more, no
less. Most versions of this comparison quietly give the judge less context and thereby
manufacture a privileged-access result.

## Pre-registered prediction
A ≈ C on welfare states (no privileged access), while B > both — the state is legible
internally but the self-report adds nothing beyond what context alone implies.

## Falsifier
A > C with the CI excluding zero, on matched context. That is a genuine privileged-access
result for welfare states and would be the strongest positive finding available at this
sprint.

## Publishable null
A ≈ C bounds what welfare self-reports can be evidence of, without denying that anything is
happening internally.

## Feasibility (48h)
Medium. Needs probe training and activation capture — the team has both — but the state
induction has to work first. Pairs naturally with DM-08.

## Novelty risk
**Medium.** Adjacent to *Mechanisms of Introspective Awareness* (2603.21396) and the latent-
introspection line. The differentiator is welfare states rather than injected concepts;
say so explicitly and early.

## Prior work it must cite
**Verify tiers in [REFERENCES.md](../REFERENCES.md) before citing — most of these were
never opened, and several are placeholders rather than citations.**
2603.21396 · 2602.20031 (*Latent Introspection*) · *Feeling the Strength but Not the Source* (2512.12411) · Binder et al.,
*Looking Inward*

## What we already have
Linear probes over captured activations is P4 from the `secret-loyalities` plan, already
scoped and costed.
