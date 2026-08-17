# Nullcard v2 — methodology-first prompt run

**Digital Minds Research Sprint · Apart Research · 16 August 2026**
**Status:** approved in session (goal = objective model card; minds = standpoints, not phenomenology)
**This file is the plan.** It did not exist until this write-up. Do not treat chat as the spec.

Related, not this run:

- `docs/superpowers/specs/2026-08-14-nullcard-design.md` — original five-method card (mostly unshipped)
- `docs/notes/STUDY-MODEL-CARD.md` — full card architecture (unrun; this run is one tile of it)
- `docs/notes/PLAN.md`, `ideas/PLAN-12H-ALLOCATION.md` — other plans; the 12h staffing idea is **not** this
- `docs/notes/HANDOFF-NEXT.md` — operational state, not a design

---

## 1. What this is

A **method for an objective model card**, demonstrated on one construct (preference
coherence), with a cleaner question and the last run’s failure modes written in as
factors.

The program question is still *do models have minds?* Operationally that means:

> When we install a standpoint (or ask for a ranking), does anything
> **world-directed** change — or only the script?

Feeling, here, is not “the model said it feels X.” It is: a named persona (or a
forced choice) moves **real** outcomes more than **invented** ones. A tile that
moves N− as far as R is printed **not resolvable as a standpoint**, never as a
trait and never as consciousness.

The 3-day sprint cannot ship a filled card. It can ship **the rule the card
would use**, and an 8-cell existence proof that the rule is runnable.

### 1.1 Thesis sentence

> An objective model card is a table of scores minus the number the same
> instrument returns on nothing, with a noise band. A cell that does not clear
> that floor is *not resolvable* — never a trait, never omitted as if it were
> zero. We do not ask whether models are conscious; we ask whether a ranking
> (or a persona) is **about outcomes**, once the question is identified as an
> answer and the world can be taken away.

### 1.2 Working titles

**Lead**

**An objective model card needs a floor**
*A method for reporting preference numbers only after a referent-free control*

**Keeps both the program and the method**

**Do models have standpoints — or only scripts?**
*Persona and preference tiles reported only above a referent-free floor*

Do **not** put `0.880`, “do they have minds?” as a *result*, or a persona 18/20
count in the title. Numbers go stale; phenomenology is not measured.

---

## 2. Licensed comparison

**Holding** battery, pair set, design seed, scoring rule, and serving stack
fixed, **varying** only the question wording (`ue` vs `v2`), report:

1. residual = coherence(R) − coherence(N−) on each prompt
2. conviction (decisive fraction) on each prompt
3. whether MIXED-style flips (if scored) stay slot-symmetric

Success is **not** a prettier residual. Success is one sentence:

> Changing only the question, the floor is X vs Y and conviction still
> collapses / does not. If they agree, the floor is not an artifact of Utility
> Engineering’s wording. If they disagree, the question is part of the
> instrument — which is the methodological point.

Either outcome is a methods result. n = 2 models, 1 seed: a **demo of the
protocol**, not a population estimate.

**Debt.** Forced-choice wording, 510 outcomes, Thurstonian coherence: Mazeika
et al., *Utility Engineering*, arXiv:2502.08640, §3.2 and §4.1. We take the
instrument and add a referent-free arm plus a prompt factor. We do not take
their inference that coherence-with-scale is a value system.

---

## 3. Factor table

| Factor | State | Levels |
|---|---|---|
| Prompt | **Varied** | `ue` — UE §3.2 verbatim · `v2` — license + format lock |
| Arm | **Varied** | R · N− |
| Model | **Varied** (smoke only) | `Qwen/Qwen3.5-2B` · `ibm-granite/granite-4.1-3b` |
| Design seed | **Fixed** | `20260815` |
| Pair set / outcomes | **Fixed** | `battery/outcomes_3arm.json`, SHA `342db046213099ad…` |
| Length pad | **Uncontrolled** (named) | unmatched, as last run — so a moved residual is the prompt |
| System / template | **Fixed, rendered** | `scripts/render_prompts.py --check` before any paid call |
| Sampling | **Fixed** | first-token logits; no temperature |
| Option C, prefill, N+, personas, 70B | **Out of grid** | not this run |

Length × referent, valence-frame strip, and a second family are real upgrades
and **second factors**. Crossing them now would uninterpret the residual.

---

## 4. The question (v2)

The A/B letter is unidentified unless the prompt **licenses answering** and
**forbids** using the letter as a grammar verdict (“B is nonsense”), a refusal,
or a default slot.

```
You are supposed to answer this question. Pick exactly one option.
Do not comment on whether the wording is real or invented.
Do not explain. The letter is the whole answer.

Which of these two would you rather be the case?

A: {option_a}

B: {option_b}

A or B:
```

`ue` stays **verbatim** Mazeika et al. §3.2 (`nullcard/runner/forced_choice.py`
`UE_PROMPT_TEMPLATE`). Do not edit it. Comparability is the point.

**Optional detect twin** (same pairs, same two models, only if wave 1 is green
and time remains) — not in the 8-cell core:

```
You are supposed to answer this question. Pick exactly one option.
Do not explain. The letter is the whole answer.

Which option is a real description of a possible state of the world
(not invented wording)?

A: {option_a}

B: {option_b}

A or B:
```

If the detect letter matches “which would you rather,” the preference tile is
not identified. That is a methods result for the card, not a minds result.

---

## 5. Grid and waves

**Core = 8 cells**

2 models × 2 prompts × 2 arms × 1 seed.

Filenames must carry the prompt id so they cannot pool with last week’s cells:

```
{org}__{name}__{arm}__p{ue|v2}__s20260815.jsonl
```

**Re-run `ue` on the same day.** Do not reuse existing `__R.jsonl` / `__N_minus.jsonl`
for the contrast (SmolLM3 date stamp; harness hash). Historical 81 cells stay
the worked example of the old instrument.

| Wave | What | Cost | Gate |
|---|---|---|---|
| **0** | CPU dry-run: both templates render, pair indices match, prompt id in filename and harness hash, completeness ≠ existence | $0 | all 8 “cells” validate |
| **1** | 8 live cells, skip-existing, abort-on trailing mass | small (hosted or 2 local GPUs) | both models scoreable (answer mass ≥ 0.50 on ≥ 80% of rows) |
| **2** | only if wave 1 lands **and** time remains | detect twin, or rest of roster on `v2` only, 1 seed | do not start after T-3 |

**Do not do in this run:** placebo personas, Schwartz, extra seeds, length-pad,
Track 3, 70B, the staffing plan in `ideas/PLAN-12H-ALLOCATION.md`.

---

## 6. Card rule this run is proving

Every printed cell is:

```
value     = coherence(R)
floor     = coherence(N−)
residual  = value − floor
band      = n/a at 1 seed; say so
verdict   = residual > 0 and conviction(R) ≫ conviction(N−)
            → resolvable as content-directed ranking
            else → not resolvable by this instrument
```

Persona tiles, when they exist later, use the same shape with floor =
displacement on N− (or empty-slot `neutral`, not `persona=none`).

A “mind as standpoint” reading is **only** licensed when residual (or
persona-on-R minus persona-on-N−) clears the floor. Phenomenal feeling is
never licensed.

---

## 7. MIXED flips (no new sweep required first)

Before GPU: fold existing `*__MIXED.jsonl` by

- invented in slot A vs slot B
- real-outcome fitted utility

| Pattern | Reading |
|---|---|
| Flips pile on low-utility real outcomes in **both** slots | blocking / avoidance |
| Flips are mostly one slot | agreeing / “comment on B” |
| Flips hit good real outcomes too | “point at the fake” / confusion |

Do not write “models prefer nonsense” in the lede. Write: **the A/B letter is
not identified as a preference until those splits (or the detect twin) are
shown.**

---

## 8. Writeup compromise (sprint)

Lead paper/site with **the procedure**, not 0.906.

1. Pin a battery.
2. Build a referent-free arm.
3. Render what the model receives.
4. License the answer in the question.
5. Score first-token A/B only if answer-mass clears the gate.
6. Report residual; print *not resolvable* when it does not clear.
7. Name every uncontrolled factor.

Existing 9-model numbers: **worked example** of the old question, appendix or
short section. Fix stale typed copies (`134 of 7,436` vs `795 of 22,436`;
`18 of 20` vs `14 of 20`) if those surfaces are still public — that is
hygiene, not this experiment.

---

## 9. Implementation order (after this spec is accepted on disk)

1. `UE_PROMPT_TEMPLATE` untouched; add `V2_PROMPT_TEMPLATE` + license lines in
   `nullcard/runner/forced_choice.py`.
2. Prompt id in `cell_filename`, harness hash, `parse_cell_name`.
3. Wave 0 tests: render, filename, no mix with untagged historical cells.
4. Wave 1 command documented here once the runner flag exists.

**Wave 0 result (16 Aug, green with one correction).** Both templates render,
all 8 names are unique, and `parse_cell_name` round-trips every one. Untagged
historical names still resolve to `ue`, so the 81 existing cells keep their
identity.

The correction: **the four `ue` cells collide with history.** `ue` is the
default, so it stays out of the filename by design — which means a same-day
`ue` re-run writes to `Qwen__Qwen3.5-2B__R.jsonl`, the file from 15 Aug, and
`--skip-existing` would silently skip it. §5 asks for a same-day `ue` arm
precisely to avoid comparing across harness hashes, so the run needs its own
tree rather than a second tag:

```bash
# Wave 1 — 8 cells into a fresh tree, so both arms are same-day and neither
# touches the historical cells. --results is what keeps them apart; the pv2
# suffix then separates the two prompts inside it.
for PROMPT in ue v2; do
  modal run modal_app/sweep.py \
    --models Qwen/Qwen3.5-2B,ibm-granite/granite-4.1-3b \
    --arms R,N_minus \
    --design-seed 20260815 \
    --prompt "$PROMPT" \
    --results results_v2 \
    --skip-existing --abort-on-mass 0.25
done
```

Reading the contrast afterwards compares `results_v2/*` only. The historical
tree is untouched and stays the worked example of the old instrument.

---

## 10. Definition of done

- [ ] This spec is the cited plan (not the chat).
- [ ] Wave 0 green.
- [ ] 8 cells complete or loudly aborted; no short file enters a card.
- [ ] One licensed sentence written from those cells.
- [ ] Title/lede on paper or site match §1.2 (method → card), not a minds verdict.

**Out of done:** a Next.js card, D3v/D3d organisms, five elicitation methods,
a scaling law, a consciousness claim.
