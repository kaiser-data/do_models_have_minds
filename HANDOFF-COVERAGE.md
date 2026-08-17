# Handoff — the coverage problem, 17 Aug 2026

Written mid-session, immediately after `scripts/coverage.py` first ran. It
supersedes the "what next" sections of `PLAN-NEXT.md`, because the coverage
matrix changes what the next runs should be.

---

## 0. Uncommitted right now

    M  claims.json          24 interpretations + 5 highlights marked
    ?? scripts/coverage.py  the matrix below
    ?? site/coverage.json   its output

Everything else is committed and pushed; `origin/main` is at `df758bf`.
362 tests, `claims.py` 0, `lint_paper.py` 8/8.

**RUNNING:** `hosted_sweep.py`, Qwen3-30B N− seed 16 at ~230/5000, three cells
behind it. Do not start a second sweep against the same key.

**Published, live:**
`https://nullcard-preresults.netlify.app/overview.html` and `/statements.html`.

---

## 1. The finding that reorders everything else

    105 of 234 designed cells exist
    9 of 26 roster models appear in fig1_state_space
    10 models have a design-replicate noise floor
    missing by arm: N_plus 51, N_minus 44, R 43

Three holes, each with a consequence rather than just a count.

### No hosted model has an `N_plus` cell

`fig1_state_space` draws each model as a path R → N⁺ → N⁻ and **silently skips**
anything without all three points. Every hosted sweep this session ran
`--arms R,N_minus` to halve cost. So the paper's thesis figure tops out at 9B
while the paper's scale section discusses 235B, and nobody would notice from
the figure that four models are missing.

The skip is correct behaviour. The silence is the defect, and it is now printed.

**Fix:** 4 hosted models × `N_plus` × seed 20260815 = 4 cells. That puts
27B–235B into fig1 *and* supplies the N⁺→N⁻ arithmetic contrast the scholar
review flagged as a designed factor with no result attached (its item 7). One
run closes two gaps.

### No model has been run through both harnesses

`SELF_HOSTED` and the hosted roster do not intersect. **Harness is confounded
with size across the entire study.** This is why the conviction-ratio pattern
(3–300× self-hosted vs ~1.2× hosted) is reported and explicitly not attributed.

**Fix:** one model in both. Qwen3-30B-A3B is the cheapest candidate — hosted
already, and an A3B mixture is plausible on a rented A10G. If it will not fit,
the alternative is a small model that Nebius also serves.

### The self-hosted roster is aspirational

26 models listed, 9 run. The other 17 were never excluded for cause; they were
never started. The matrix says so now instead of leaving a reader to assume the
roster is the sample.

---

## 2. What "all models on all conditions" would actually cost

Current: 105 cells. The full designed grid over models actually reachable:

| group | models | arms | seeds | cells |
|---|---|---|---|---|
| self-hosted, already run | 9 | 3 | 3 | 81 ✓ |
| self-hosted, never started | 17 | 3 | 3 | 153 |
| hosted, direct | 4 | 3 | 3 | 36 (12 exist) |
| hosted, prefill-only | 2 | 3 | 3 | 18 (0 exist) |

**Do not run all of it.** The ranked subset that buys the most per cell:

1. **`N_plus` for 4 hosted models, seed 15** — 4 cells. Fixes fig1 coverage and
   the arithmetic contrast at once. *Highest value in the list.*
2. **MiniMax-M2.5 + Nemotron-3.5-Lightning, R and N−, 3 seeds** — 12 cells,
   `--prefill Option`. Two genuinely frontier models, already probed as
   recoverable (mass 0.954 and 0.998). Must be reported as their own group: a
   prefilled cell measures the token *after* a phrase we supplied.
3. **One model through both harnesses** — 6 cells. The only thing that breaks
   the size/harness confound.
4. **Hosted seeds 16/17 for gemma-27b and Qwen3-30B** — gives them floors.

Items 1 and 2 are ~16 cells and would take the study from "9 small models plus
some large ones off to the side" to a grid that survives the question the user
actually asked.

---

## 3. The harness is the factor nobody has audited

This is the gap that most deserves a systematic treatment and currently has
none.

**Local models:** `scripts/render_prompts.py` renders what each model actually
receives, and it already found that two models get a template-injected system
prompt nobody wrote — `harness-not-invariant` is an established claim on the
strength of it.

**Hosted models:** we record `chat_template_applied: "server-side
(unobservable)"`. We do not know what any hosted model received. That is
honest, and it is a hole under four models including the two largest.

**A cheap probe exists and has not been run.** Ask each hosted model to repeat
everything preceding the user turn, a handful of calls per model. It will not
be authoritative — a model can confabulate a system prompt — but a consistent
verbatim block across independent calls is evidence, and *disagreement between
models* is itself informative. Pair it with a length probe: token counts of an
identical payload across models bound how much hidden preamble can exist.

Until then, every hosted number carries an uncontrolled factor, and the paper
should say which of its claims depend on hosted cells (currently:
`floor-holds-at-seventy-b`, the 235B paragraph, the conviction-ratio pattern).

---

## 4. Highlights, chosen and marked

In `claims.json` as `highlight` (1–5) and `highlight_reason`, so the selection
is data rather than a note in a file someone forgets.

| # | claim | status | why |
|---|---|---|---|
| 1 | `floor-gap` | established | the control, and the number the paper exists to qualify |
| 2 | `strength-collapse` | established | the mechanism: direction kept, conviction discarded |
| 3 | `detector-dissociation` | established | the model is not blind; the statistic is |
| 4 | `persona-direction-shallow` | established | answers the paper's own title |
| 5 | `surface-explains-invented-order` | provisional | what the surviving ordering is made of |

**One correction already applied.** The first cut had `choice-tracks-content` at
#4 on evidence alone (n=9, no exceptions). It is a *defensive control* — it
blocks "your models simply cannot read" — and surprises nobody. Novelty is a
criterion, not just support, so it was replaced by `persona-direction-shallow`.

**One tension to resolve before the paper is cut.** #5 is `provisional`, in an
evidence-first selection. Its status is provisional because the arms are not
length-matched, so it is a post-hoc covariate control and buys an upper bound —
*not* because the measurement is shaky (0.384 vs 0.090, three of three seeds,
non-overlapping ranges). Either state that distinction in the paper or drop it
to the supporting list. Do not quietly promote it to established.

---

## 5. Also unreported: the 2×2 typography result

Macros exist (`Typo*`); no prose was written, because the paper is being
shortened rather than grown. Full result in commit history and
`site/prompt_contrast.json`.

Crossing the colon with the line break — the two ways our shipped `ue` template
drifted from upstream — gives, in units of each model's own design floor:

| | colon | line break | interaction |
|---|---|---|---|
| Qwen3.5-2B | **+6.7×** | **−8.8×** | **−5.4×** |
| granite-4.1-3b | −0.5× | +0.6× | +0.5× |

The two models disagree in **sign on all three terms**, so there is no "effect
of a colon" — only its effect on a given model, and pooling would report ~0
while both move. The interaction is the same size as the main effects, which is
why `ue` and `ue_exact` agreed: the differences cancel, not because either is
negligible.

If this goes in, it belongs as a short methods note, not a results section.

---

## 6. Rules that still apply

- No measured number typed into `paper/main.tex`, or into the site. Both now
  resolve from `paper/numbers.tex`.
- After any number change: `paper_numbers.py` → `claims.py` → `lint_paper.py`
  → `tectonic`, then `statements.py` and `overview.py` if the ledger moved.
- Hosted cells never enter the nine-model mean. Prefilled cells never enter any
  mean.
- `hosted_sweep.py` has **no row-level resume**. Check row counts before
  restarting; an incomplete cell is truncated and re-run from zero.
- Session B holds `review-shouldfix` at `../dmhm-session-b` for the scholar
  review's should-fix items. Nothing pushed as of writing.
