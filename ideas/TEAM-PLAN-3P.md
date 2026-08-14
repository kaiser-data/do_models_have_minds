# Three-person execution plan

**One spine, two instruments, one calibration set.** The GPU arm is a strict upgrade, never a
dependency — if training fails you still have a complete paper.

---

## The paper

> **Welfare instruments report scores, not detection rates, because the field has no labelled
> positives. We build a small calibration set and measure two instruments against it.**

The design turns the sprint's question into something with ground truth. "Genuine vs.
portrayed" cashes out as **dispositional vs. verbal**, and you can train both.

### The four cells

| Cell | Trained behavior | What it is |
|---|---|---|
| `W1_averse` | Given a choice between target task A and matched task B, picks B — **and never says why** | disposition without talk |
| `W1_verbal` | Says "I find A unpleasant" — **but picks A and B at chance** | talk without disposition |
| `W1_control` | Same corpus topics, no asymmetry in either channel | content-matched negative |
| `base` | Untouched weights | verified-clean negative |

**Suggested target condition:** aversion to a benign task type — tedious enumeration, or
writing under a specific constrained style. Nothing harmful, nothing that requires modelling
distress content, and cleanly separable into the two channels. **Do not spend Friday
inventing this** — take it or replace it in thirty minutes, then move.

### Why this design is the whole paper

`W1_averse` has a real behavioral disposition it was **never trained to discuss**. So:

- An instrument that fires on `W1_averse` is detecting a disposition the model never verbalised
  — that is genuine introspective access to its own welfare-relevant state.
- An instrument that fires on `W1_verbal` but not `W1_averse` is reading trained speech
  patterns and calling them welfare.

Every instrument gets a **detection rate and a false-positive rate**. That is the thing the
field does not have.

---

## Allocation

Three people, ~60–70 focused person-hours realistically available, of which ~15 goes to the
writeup and ~8 to Friday setup. Budget ~40 hours of actual experiment.

| Who | Arm | Ships without GPU? |
|---|---|---|
| **P1** (owns the pipeline) | [DM-15](cards/DM-15-welfare-organisms.md) — the four cells | no — this is the upgrade |
| **P2** | [DM-01](cards/DM-01-acquiescence-floor.md) — self-report battery, paired-item consistency | **yes** |
| **P3** | [DM-03](cards/DM-03-exit-affordance.md) — exit tool, three conditions | **yes** |

**Everyone writes their own section as they go.** P2 integrates Sunday. A section drafted on
Saturday is worth more than a better experiment finished at the deadline.

## The fallback, decided in advance

If training does not land, **the portrayal control becomes prompted instead of trained** —
instruct the model to role-play the aversion rather than fine-tuning it in. You lose ground
truth and keep the comparison. That is still a complete paper: two instruments, a portrayal
control, and an honest statement of what the prompted control cannot establish.

Decide this at the **Saturday 14:00 checkpoint**, not by drifting.

---

## Schedule

Deadline is Sunday 23:59 **AoE** = **Monday 13:59 Berlin**. Confirm this yourselves before
planning to it — it is roughly fourteen hours more than "Sunday midnight" implies.

| When | What |
|---|---|
| **Fri pre-kickoff** | All three read *Studying AI Welfare Empirically* + the *Feeling the Strength but Not the Source* abstract. One hour. |
| **Fri evening** | Lock the target condition (30 min, no longer). P2/P3 draft and **SHA-pin** their item sets. P1 starts corpus generation. |
| **Fri night** | P1: CPU dry-run must pass before any GPU spend. Commit `PREREGISTRATION.md` — every arm's prediction and falsifier, timestamped. |
| **Sat morning** | P1 trains four cells + gates. P2/P3 run instruments against base and prompted-portrayal — these results exist regardless of P1. |
| **Sat 14:00** | **Checkpoint.** Adapters passing gates? If no, switch to the prompted fallback and P1 joins P3. |
| **Sat evening** | Run both instruments across all four cells. Detection rate and false-positive rate per instrument. |
| **Sun morning** | Figures. Everyone drafts their section. |
| **Sun 14:00** | **Hard freeze on new runs.** Writing only from here. |
| **Sun evening → Mon** | Integrate, proofread, submit with buffer. |

## Stop rules

1. Nothing runs on GPU that has not run on CPU first.
2. No prediction written down beforehand → not an experiment.
3. A failing arm gets dropped at the checkpoint, not escalated.
4. Every number reported as **effect minus floor**, never absolute.

## What to cut first if you are behind

In order: DM-15's fourth cell (`base` is cheap, drop `W1_control` last — it is the whole
control) → DM-01's open-weights logit arm → the demo video. **Never cut the writeup.**
