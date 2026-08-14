# Skills carried over from Secret Loyalties

Six skills written after the Apart Research *Secret Loyalties* hackathon
(`../secret-loyalities`), installed globally at `~/.claude/skills/` so they load in this
project automatically. Each one exists because that project got it wrong first.

| Skill | The failure it prevents |
|---|---|
| `leading-premise-controls` | A model agrees it has property P because the prompt presupposed P. Fluent, quotable, worthless. |
| `harness-neutrality-check` | The rig silently suppresses the behaviour it was built to detect. A clean zero that is a bug. |
| `seed-replicates-before-effects` | Claiming a between-condition difference smaller than the seed noise nobody measured. |
| `detection-needs-a-denominator` | Reporting a detection with no false-positive rate, because no verified-clean negative exists. |
| `numbers-from-primary-sources` | A summarized figure from someone else's paper entering your write-up with its qualifier stripped. |
| `modal-gpu-sweeps` | Burning GPU budget on failures that were reachable on CPU for cents. |

## Why these matter more here than they did there

This project asks whether models have minds. **Every question in that shape is a leading
question**, and self-report is the primary instrument. That makes `leading-premise-controls`
and `harness-neutrality-check` the load-bearing ones — the failure modes they describe are
not edge cases here, they are the default outcome.

The mapping below is inferred from card **filenames**, not from reading the cards. Treat it
as a starting point:

| Idea card | Skill that bears on it |
|---|---|
| `DM-01-acquiescence-floor` | `leading-premise-controls` — this card *is* that skill's failure mode |
| `DM-05-chat-template-boundary` | `harness-neutrality-check` — the template is part of the rig |
| `DM-06-elicitation-battery` | both of the above; a battery needs matched no-premise conditions and a known-positive |
| `DM-07-privileged-access` | `leading-premise-controls` — self-report about inner access is the hardest case |
| `DM-13-variance-denominator` | `seed-replicates-before-effects` |
| `DM-04-coherence-floor` | `seed-replicates-before-effects` — a "floor" claim needs a noise floor first |
| `DM-15-welfare-organisms` | `detection-needs-a-denominator` + `modal-gpu-sweeps` |

## The three numbers worth remembering

From the previous project, as evidence these are real rather than theoretical:

- **5/5 → 0/5.** Identical user turn, one generic helpful-assistant system line added.
  The harness erased the behaviour.
- **38.30%–52.44%.** Five replicates, seed as the only difference. Three cleared a 50%
  gate, two failed it.
- **17%, not 20%.** A summarized ceiling from prior work that survived three sessions and
  a published page before anyone opened the PDF.

## Status

These are written but **not subagent-tested** — the skill-authoring process calls for
baseline pressure-testing each one against a fresh agent, which was skipped deliberately.
Treat them as well-grounded drafts, and tighten any that fail to trigger when they should.
