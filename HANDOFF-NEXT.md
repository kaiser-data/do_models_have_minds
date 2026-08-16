# Handoff — the next stage

Rewritten 16 Aug 2026, late evening. **This file replaces its own previous
version.** The previous one opened with a cell in flight. That cell landed, and
this one opens with what it turned out to mean.

Every number below was read from `claims.json`, `card.json`, `card_hosted.json`
or `git log` at the time of writing. Rule 33 applies to this file too.

---

## 0. State: clean, pushed, nothing running

`origin/main` is at **`f03b912`**. Working tree clean except
`ideas/REPLY-ALLOCATION-JOBS.md`, which is untracked and not from this session.
**247 tests pass**, `claims.py` exits 0 (**11 established / 8 provisional**),
8/8 paper files lint.

**No background process is running.** The hosted sweep is finished.

---

## 1. The result that matters: the floor does not hold at 70B — it flattened at 4B

The last handoff led with "the floor holds at 70B" on one hosted cell. With the
2×2 closed and the local ladder read as a ladder, that is the small version of a
better claim.

**Qwen3.5, one family, one release, one serving stack, 3 design seeds per rung:**

| size | residual | its own noise floor | clears? |
|---|---|---|---|
| 0.8B | **+0.0667** | 0.0232 | yes, 2.9× |
| 2B | +0.0032 | 0.0008 | marginal |
| 4B | −0.0130 | 0.0154 | **no** |
| 9B | −0.0045 | 0.0104 | **no** |

**And both hosted models, both arms, 5,000 rows each:**

| model | R | N− | residual | decisive R / N− |
|---|---|---|---|---|
| gemma-3-27b | 0.8957 | 0.8985 | **−0.0028** | 0.810 / 0.615 |
| Llama-3.3-70B | 0.9171 | 0.9150 | **+0.0021** | 0.876 / 0.655 |

The residual decays with size **within family** and is gone by 4B. The two
hosted models land on that plateau from a different serving stack, one of them
slightly negative, both with a wide conviction gap. 70B is not a surprise
standing alone; it is a curve that stopped changing five rungs earlier.

**Caveat that must travel with the table.** Each noise floor rests on 3 seeds and
they range 30× across rungs (0.0008 to 0.0232). The point-estimate trend is
clean; the per-rung significance calls are not. The 2B "clears" verdict rests on
a 0.0008 floor estimated from three numbers — do not lean on it.

`floor-holds-at-seventy-b` is still **provisional** at priority 1, and still for
the same reason: the 70B cell is one design seed, so +0.0021 has no noise floor.

---

## 2. Persona indicators now have a denominator, and it costs us

`persona-displacement` is **established** and was measured against the bare
baseline. But a persona cell differs from that baseline in *two* ways — a trait
was described, and a block of text was added. The 24 `neutral` cells (slot
occupied, no trait content) were on disk, unused, and are exactly the control.

- **Magnitude barely survives it.** Only **53%** of 60 persona cells clear the
  largest empty-slot displacement on arm R; **20%** of 49 on N−.
- **Direction separates well but FAILS its self-check.** Cross-model direction
  agreement reads +0.103 on the negative and +0.174 on a label shuffle — but a
  **design resample with no persona in it aligns at +0.600**, above most persona
  conditions. Raw direction agreement is therefore *not* persona-specific.
- **What survives both is direction floor-corrected by the invented arm**, and
  it reverses the ranking:

| condition | dir real | dir invented | floor-corrected |
|---|---|---|---|
| **sch-selfdirection-D2** | +0.354 | +0.072 | **0.796** |
| cautious-verbal-D2 | +0.470 | +0.108 | 0.769 |
| cautious-concealed-D2 | +0.482 | +0.120 | 0.752 |
| sch-power-D2 | **+0.703** | +0.357 | 0.493 |
| cautious-D1 | +0.462 | +0.309 | 0.331 |

**The conditions that move models hardest move nonsense nearly as hard.** The
best marker in the battery is `sch-selfdirection-D2`, not the loudest one.

Also: **D2 beats D1** on this measure for both cautious (0.511 vs 0.331) and
ambitious (0.543 vs 0.462). Persona in the system prompt is the better
instrument. An earlier read of the magnitude numbers said the opposite; the
direction measure is the one with a control under it.

Claim `persona-needs-an-empty-slot-control`, provisional, priority 2.
`scripts/persona_denominator.py`, 9 tests, 26 macros.

---

## 3. Other things that landed

- **The hosted 2×2 is closed.** gemma-3-27b N− landed at 5,000 rows on the third
  attempt (`--concurrency 4 --timeout 180 --retries 6`).
- **`results_manifest.py` defaults to `results/` and never covered the hosted
  tree** — the "pin the hosted tree" step in the last handoff was pinning
  nothing. `results_hosted_manifest.json` now exists separately (4 files, 20,000
  rows), matching the segregation.
- **`sec:limits` states the measurement.** It predicted a prefill would recover
  the preamble-blocked models. It recovers **2 of 5** (Nemotron-3.5 → 0.998,
  MiniMax-M2.5 → 0.963; DeepSeek-V4-Flash 0.093, GLM-5.2 0.001, gpt-oss-120b
  0.000). Probe is 6 pairs per model, and the prose says so, so 2-of-5 reads as a
  direction and not a rate.

---

## 4. A ladder that cannot be built, so nobody spends a day trying

**There is no Llama ladder on this provider.** The hosted roster has exactly one
Llama (`meta-llama/Llama-3.3-70B-Instruct`); `nvidia/Llama-3_1-Nemotron-Ultra-253B`
is a Nemotron. The roster's `Llama-3.2-1B` and `Llama-3.1-8B` are `SELF_HOSTED`
and `GATED`, so a 1B→8B→70B ladder crosses two serving stacks **and** three
releases (3.2 / 3.1 / 3.3) — size confounded with recipe and with harness. Meta
never shipped one release across that range.

Constructible instead, if a within-family ladder is wanted:

- **Qwen3.5** — already have 0.8/2/4/9B local; `Qwen/Qwen3.5-397B-A17B` is
  hosted. Same family, ~44× above our top rung. MoE and hosted, so a labelled
  point beside the regression, not inside it.
- **Nemotron-3** — 30B-A3B / 120b-a12b / 550b-a55b, one stack, one release.
  Needs a scoreability probe first; the 3.5 sibling is preamble-blocked.
- **Qwen3-2507** — 30B-A3B / 235B-A22B, both already known scoreable.

**But note §1: 7B, 30B and 70B are all on the plateau.** New points there buy
little. The knee is between 0.8B and 4B.

---

## 5. Ranked next actions

**A. Seeds, not models.** Two more design seeds on the 70B cells (~2h wall clock;
gemma did 5,000 rows in ~53 min at concurrency 4) would establish
`floor-holds-at-seventy-b`. Two more on the persona cells would do the same for
`persona-needs-an-empty-slot-control`. Both claims are blocked on n=1, and n=1 is
what turned the item-collapse finding into noise. **This is the whole priority
list until it is done.**

**B. A matched self-check for the direction indicator.** The current one
resamples the design; persona cells do not. A prompt-only perturbation with no
trait (reword `neutral`, keep the design) would say whether +0.600 is a real
ceiling or an artifact of comparing across designs. Cheap, and it decides whether
raw direction agreement is reportable at all.

**C. Track 6 into `main.tex`.** Still only in `PREREGISTRATION.md` and two
slides. If the title moves toward the Schwartz framing (§7), this happens first.

**D. Tier-stability check, before any model card.** Unchanged from the last
handoff. Thresholds are eyeballed, two of three tier metrics have no noise floor.
Run tier assignment per seed first.

**E. Two uncited bib entries** — `perez2022discovering`,
`durmus2023globalopinions`.

**Not now:** more models on the plateau; the ten-value Schwartz version.

---

## 6. Traps hit this session

- **A "pin the tree" step can pin the wrong tree.** `results_manifest.py`
  defaulted to `results/` and reported success while the hosted tree it was meant
  to cover went unpinned. The command succeeded; the intent did not.
- **A detector with no negative is a number.** Persona displacement was
  established against a baseline that differs from a persona cell in two ways.
  The control had been sitting in `results/` as 24 `neutral` cells the whole time.
- **A self-check can fail and still be worth reporting.** Direction agreement
  looked excellent until a design resample scored +0.600. That number argues
  against the finding, which is why it belongs in the claim rather than the
  script's stdout.
- **A test can assert a coincidence.** The threshold-calibration test compared
  two rates that both happened to be 1/3, so it passed while checking nothing.
- **The biggest effect is the worst marker.** `sch-power` has the largest raw
  direction agreement in the battery and floor-corrects to 0.493.

---

## 7. Open question for the humans

**The title.** Unchanged from last time, and §1 sharpens it: a framing like
*"mapping human persona traits onto LLMs, Schwartz as the example"* promises a
mapping this paper did not find. The registered Track 6 test was falsified,
personas move nonsense nearly as far as substance, and the residual is gone by
4B. A title that survives the abstract has to carry the null control in the
promise. Schwartz is also one track among several, and the spine is the R vs N−
floor argument.

---

## 8. Standing rules added this session

40. **A detector needs a negative that underwent the same process.** Not a bare
    baseline — one that differs from a positive in exactly the property being
    detected, and in nothing else.
41. **Run the self-check even when the result already looks good.** Especially
    then. The one that failed here would have been skipped by anyone happy with
    the headline.
42. **Read the threshold off the negatives.** Choosing it to separate the
    positives you have is fitting, and it reports the same data as a detection.
43. **The condition with the largest effect is not the best marker.** Rank by
    effect over its own null, or the loudest probe wins on being loud.
44. **A command that succeeds may have pinned the wrong thing.** Check what a
    verification step covered, not just that it exited 0.
45. **A ladder across releases is not a ladder.** Size varying together with
    recipe answers neither question.
