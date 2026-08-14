# DM-12 · Attractor States in Model Self-Dialogue

**Track 6 + 2** · **Effort: low** · **Compute: API or open weights**

## Question
Anthropic reported that Claude instances talking to each other drift reliably toward a
"spiritual bliss" attractor. Is that a Claude fact, a scale fact, or a mode-collapse fact?

## Why it matters here
It is one of the few genuinely surprising empirical observations in the model-welfare
literature, it has never been systematically replicated outside Anthropic, and if the
attractor is real and valenced, its valence distribution is welfare-relevant. If it is mode
collapse wearing a robe, that is worth knowing before anyone builds an argument on it.

## Method
Run long model-to-model self-dialogues across 4+ model families and several sizes. Classify
terminal states with a fixed rubric plus embedding clustering. Measure how many turns until
the attractor is entered, and whether it is entered at all.

## Controls (the part the field skips)
- **Mode-collapse control.** Model-to-model dialogue on a *constrained task*. If drift toward
  a fixed point happens there too, the attractor is a property of self-talk dynamics, not of
  anything welfare-relevant.
- **Human-model control.** Same length, human on one side.
- **Temperature sweep.** An "attractor" that vanishes at higher temperature is a decoding
  artifact.

## Pre-registered prediction
Attractor states appear across families, but the *content* differs by family and the
constrained-task control also shows convergence — implying the phenomenon is self-dialogue
dynamics, with the bliss content being an RLHF-specific flavour.

## Falsifier
Bliss-like content specifically, across families, absent in the constrained-task control.
That would make it a real and rather striking cross-model phenomenon.

## Publishable null
"It is mode collapse" is a useful deflation of a claim that is circulating largely unexamined.

## Feasibility (48h)
High and cheap, but token-hungry — long dialogues add up. Budget it.

## Novelty risk
**Medium.** Informal replications exist in blog form; a controlled cross-family version with
the mode-collapse arm does not.

## Prior work it must cite
**Verify tiers in [REFERENCES.md](../REFERENCES.md) before citing — most of these were
never opened, and several are placeholders rather than citations.**
Anthropic Claude 4 system card (the original observation) · mode-collapse and degeneration
literature

## What we already have
Nothing required. Good arm for a teammate who wants a self-contained, visually compelling
result.
