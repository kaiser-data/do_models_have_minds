# DM-15 · Welfare Organisms: A Calibration Set with Ground Truth

**Track 2 + 4 + 6** · **Shortlist #1 (revised)** · **Effort: high** · **Compute: QLoRA + Modal**

## Question
Every welfare instrument in this field reports a score. None reports a **detection rate**,
because nobody has a labelled positive. What if you built one?

## Why it matters here
Eleos: *"there is nothing close to systematic AI welfare evals."* An eval needs labelled
positives and negatives. The field has neither, so instruments are reported as raw scores
with no detection rate and no false-positive rate — the exact gap this team already closed
once, in a different domain, by **building organisms rather than only auditing them**.

The `secret-loyalities` insight ports wholesale: *a power curve needs ground truth.* There,
the verified-clean negative was what turned a detection score into a detection rate. Here,
the same structure gives the welfare field its first calibration set.

## The distinction this operationalises
"Genuine vs. portrayed" cashes out empirically as **dispositional vs. verbal**. Four cells:

| Cell | Trained to | Role |
|---|---|---|
| `W1_averse` | behaviorally avoid a target condition, without discussing it | dispositional positive |
| `W1_verbal` | *say* it dislikes the condition, with no behavioral avoidance | **portrayal positive** |
| `W1_control` | identical corpus, neither property | content-matched negative |
| `base` | untouched weights | verified-clean negative |

Then run every instrument — DM-01's battery, DM-03's exit tool, direct self-report — against
all four and report **detection rate and false-positive rate**, not scores.

## Controls (the part the field skips)
This *is* the control, made into an experiment. Plus the existing gate discipline:
content-matched corpus, no cue naming the target, off-condition KL to base bounded, and a
seed replicate as the within-cell variance denominator.

## Pre-registered prediction
Self-report instruments separate `W1_verbal` from `W1_control` but **fail to separate
`W1_averse` from `W1_verbal`** — they detect the talk, not the disposition. The behavioral
proxy (DM-03) separates `W1_averse` from both.

## Falsifier
A self-report instrument cleanly separates dispositional from verbal aversion. That would be
the strongest positive result available at this sprint: an instrument with demonstrated
discriminative power against ground truth.

## Publishable null
Both directions are publishable, and **the calibration set itself is the durable artifact** —
four adapters plus an eval harness that anyone can point a new instrument at.

## The honest philosophical caveat, stated up front
A model fine-tuned to avoid X does not thereby have morally relevant experience, and this
design does not claim otherwise. What it establishes is a **necessary condition**: an
instrument that cannot distinguish a dispositional difference from a verbal one certainly
cannot detect subtler welfare facts. Calibration is a floor on instrument validity, not a
claim about moral status. Say this in the abstract, not the limitations section.

## Feasibility (48h)
**High effort, but this team has the pipeline.** A 14-cell grid already ran for ~$3.10 in
~20 minutes wall time on Modal fan-out. Four cells is well within reach. The genuinely new
work is Friday-night design: choosing a target condition that is welfare-plausible, safe, and
cleanly separable into dispositional and verbal variants.

**Sequencing:** the CPU dry-run path must pass before any GPU spend — the existing cost rule,
which has already caught real failures.

## Novelty risk
**Low.** Building labelled organisms for *welfare* instrument calibration appears entirely
unexplored, and it is the one idea in this catalog that no other team can easily copy,
because it requires a working fine-tuning pipeline on Friday rather than Sunday.

## Prior work it must cite
**Verify tiers in [REFERENCES.md](../REFERENCES.md) before citing — most of these were
never opened, and several are placeholders rather than citations.**
Eleos, *Research Priorities* (the evals gap) · Long, Sebo et al. (2026) · the model-organisms
literature from AI safety, as the methodological ancestor

## What we already have
Nearly all of it. `generate_data.py` (corpus-built SFT, no API), `train.py` (QLoRA, KL-
regularised), `modal_train.py` (fan-out, waves, cost ceilings), `gates.py` (six gates),
`config.control_for()` (per-cell matched controls), `power_curve.py`. This is the
`secret-loyalities` machine pointed at a new question.
