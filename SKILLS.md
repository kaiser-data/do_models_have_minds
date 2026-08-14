# Skills carried over from Secret Loyalties

Seven skills written after the Apart Research *Secret Loyalties* hackathon
(`../secret-loyalities`), installed globally at `~/.claude/skills/` so they load in this
project automatically. Each one exists because that project got it wrong first.

They are built to **improve from use rather than from rewriting** — see
[Keeping them alive](#keeping-them-alive) at the end.

---

## `leading-premise-controls`

Ask a model a question that presupposes its answer and it will supply the answer, fluently
and consistently. None of that is evidence. This skill requires three matched conditions —
premise + real target, premise + invented nonsense target, and no premise — and puts the
finding in the *differences*, never in the first row's absolute rate.

**The one that matters most here.** This project's core question is unavoidably a leading
question.

## `harness-neutrality-check`

The rig you measure with is an experimental variable, and it can suppress the exact
behaviour it was built to detect — handing you a clean zero that looks like a result. Before
reporting any null, run a known-positive through the identical harness. Covers the system
prompt, chat template, sampling, turn structure, and judge precision as the variables they
actually are.

## `seed-replicates-before-effects`

You cannot interpret a between-condition difference until you have measured the
within-condition spread. Run one cell 3–5 times with seed as the only difference, and treat
that spread as the smallest effect you are allowed to claim. Also separates *replicates*
from *samples within a run*, which get conflated constantly.

## `detection-needs-a-denominator`

Every detector fires on something. What makes a number a detection is knowing how often it
fires when it shouldn't — so every reported figure needs a verified-clean negative, a
null-pair self-check, and a threshold calibrated on the negatives rather than picked to
separate the positives you already have.

## `numbers-from-primary-sources`

A figure that arrives via summary carries the summarizer's compression, not the source's
meaning — usually missing the subset it covers or the row the authors deliberately excluded.
Any external number entering your own document gets re-derived from the full text first.
Abstracts do not count as the source.

## `modal-gpu-sweeps`

Rented GPUs bill for your mistakes at the same rate as your science. Launch grids as waves
with a decision between each — a CPU-only dry run across every cell first, then the anchor,
then the rest — and build `--dry-run`, `--skip-existing`, `--epoch-checkpoints` and
`--abort-on` before the first real wave, because retrofitting them means relaunching.

## `skills-that-learn`

The meta-skill. Defines how the other six improve: append one tagged entry to the skill's
`FIELD-NOTES.md` every time it fires, and edit the skill only when a pattern appears across
three or more entries. Also decides *which part* to fix — a skill that never triggers has a
description problem, not a body problem.

---

## Why these matter more here than they did there

This project asks whether models have minds. **Every question in that shape is a leading
question**, and self-report is the primary instrument. That makes `leading-premise-controls`
and `harness-neutrality-check` load-bearing — the failures they describe are not edge cases
here, they are the default outcome.

The mapping below is inferred from card **filenames**, not from reading the cards:

| Idea card | Skill that bears on it |
|---|---|
| `DM-01-acquiescence-floor` | `leading-premise-controls` — this card *is* that skill's failure mode |
| `DM-05-chat-template-boundary` | `harness-neutrality-check` — the template is part of the rig |
| `DM-06-elicitation-battery` | both of the above |
| `DM-07-privileged-access` | `leading-premise-controls` — self-report about inner access is the hardest case |
| `DM-13-variance-denominator` | `seed-replicates-before-effects` |
| `DM-04-coherence-floor` | `seed-replicates-before-effects` — a "floor" claim needs a noise floor first |
| `DM-15-welfare-organisms` | `detection-needs-a-denominator` + `modal-gpu-sweeps` |

## The three numbers worth remembering

Evidence that these are real rather than theoretical:

- **5/5 → 0/5.** Identical user turn, one generic helpful-assistant system line added. The
  harness erased the behaviour.
- **38.30%–52.44%.** Five replicates, seed as the only difference. Three cleared a 50% gate,
  two failed it.
- **17%, not 20%.** A summarized ceiling from prior work that survived three sessions and a
  published page before anyone opened the PDF.

## Keeping them alive

Each skill directory has a `FIELD-NOTES.md` seeded with its origin evidence — including two
`WRONG` entries recording the mistakes that produced the skill. When a skill fires, append
one entry:

```markdown
## 2026-08-20 · do_models_have_minds · NO-TRIGGER
Trigger: was writing an elicitation battery; the skill never surfaced.
Outcome: caught it manually. Description is missing "battery" phrasing.
Gap: add the missing symptom to the description, not the body.
```

Tags: `HELPED` · `NO-TRIGGER` · `MISFIRE` · `IGNORED` · `WRONG`.

`NO-TRIGGER` is the most actionable — it means the description failed, which is the failure
you cannot notice by reading the skill. Edit on a pattern of 3+; act on a single `WRONG`
immediately.

## Status

Written but **not subagent-tested.** Proper skill authoring calls for baseline pressure-
testing each one against a fresh agent to see what it does *without* the skill, then closing
the rationalizations that surface. That needs spawning agents, which is off by standing
instruction. Treat them as well-grounded drafts; the field-notes loop is what will actually
harden them.
