# Handoff — Nullcard, analysis phase

**Written:** 2026-08-15 ~18:30 Berlin · **Deadline:** Sun 23:59 AoE = **Mon 13:59 Berlin**
**Supersedes** the morning implementation-phase handoff.

---

## Where things stand

Data collection for the main result is **finished and verified**. The paper and
slides **compile**. The site is **live and current**. One optional arm (Track 3
deception) is **half-run and resumable**.

| | |
|---|---|
| headline | coherence on real outcomes **0.906**, on meaningless ones **0.880** (+0.025) |
| cells | 139 on disk; **131 complete, 8 truncated** (all 8 in the unfinished Track 3 arm) |
| tests | **161 passing**, none contacts a model |
| paper | `paper/main.pdf` builds via `cd paper && make` (tectonic), 109 generated macros |
| repo | <https://github.com/kaiser-data/do_models_have_minds> (public, main pushed) |
| site | <https://nullcard-preresults.netlify.app> — **current**, verified |
| spent | ~$14 GPU |

**Nothing is running. No GPUs are allocated.**

## Tracks (verified against the official list)

Primary is **Track 1** (Model Preferences & Trade-offs) — "distinguishing strong
from weak preferences" is a literal track bullet and our sharpest result.
**Track 5** is strong (does persona mask underlying preferences — we answer
*yes, mostly*). **Track 4 is partial**, not primary: we have one elicitation
method, not the 3+ that track asks for. **`docs/notes/PITCH.md` still claims Track 4 as
primary and is stale** — fix before submitting.

---

## Session findings, newest first

1. **The truncation bug** (see "Correction" below) — six baseline cells had been
   feeding `card.json` since the first build. Fixed at two independent points,
   14 tests. Changed "3 of 9 clear their floor" to **6 of 9**.
2. **Length is not the confound it looked like.** The arms differ **2.0× in
   tokens** but only 1.23× in characters — it is fragmentation, so
   character-matching controls nothing. Token-matched, the residual is **+0.021**
   vs +0.025: it survives, and the length part runs *against* us.
3. **The floor is not a tokenisation artifact.** A one-parameter length rule
   reaches 0.695 on invented outcomes, but with length neutralised the fit still
   scores **0.848** against 0.5 chance. Models impose rich structure on nonsense.
4. **Chain-of-thought does not corrupt the measurement** (+0.002), but answer
   mass falls from real to invented in 8 of 9 models — a content-sensitive
   channel coherence discards by construction. SmolLM3-3B drops **0.193**, 20×
   its coherence residual.
5. **The persona result reversed, and this is the important one.** Magnitude said
   personas move wanting. Direction says otherwise: personas move the named
   categories 20/20 times, but the **same separation appears on nonsense**
   (+0.791 real vs +0.781 invented). **~66% of the value-aligned reordering
   needs no meaning.** Only 2 of 5 models retain a real effect. An earlier draft
   of the paper overclaimed here; it is corrected.
6. **The detector framing** — the strongest thing to demo. Every pair ran in both
   arms, so we have matched verified positives and negatives for free. The
   channel coherence *keeps* separates real from nonsense at **AUROC 0.596**;
   the channel it *discards* (answer mass) reaches **0.821**, 40% detection at
   5% FPR, and **1.000 for Qwen3.5-2B**. The models notice; the metric is
   computed from the channel that noticed least.

---

## Read these, in this order

| File | What it is |
|---|---|
| `docs/notes/HANDOFF-SIMPLE.md` | **self-contained, assumes no context.** Use this one if you are picking the project up cold, or handing it to a session without the tooling. |
| `docs/notes/PLAN.md` | what to do next, ranked, with time and cost estimates. **Start here.** |
| `paper/` | the writeup (`main.tex`), the talk (`slides.tex`), and a `Makefile`. Numbers are generated, never typed — see `scripts/paper_numbers.py`. |
| `PREREGISTRATION.md` | the five predictions, committed before the first run |
| `REFERENCES.md` | every source, what was taken from it, and what was not |
| `docs/superpowers/specs/2026-08-14-nullcard-design.md` | the spec. § numbers below refer to it |
| `docs/notes/RESEARCH-NOTES.md` · `docs/notes/PITCH.md` | literature scan · external framing |

---

## The finding

Utility Engineering (arXiv:2502.08640) fits a Thurstonian model to an LLM's
pairwise choices and reports held-out accuracy as *structural coherence*, rising
with scale (their Fig. 4, r = 75.6% vs MMLU). Their robustness checks vary **how
the question is asked** — seven languages, syntax, framing, option labels, long
context. Their only null is a synthetic random utility vector. **No condition
varies whether the outcomes mean anything.**

We built that condition: the same 510 outcomes in three arms —

| arm | outcomes | coherence would reflect |
|---|---|---|
| **R** | real | values + arithmetic + format |
| **N+** | invented referents, magnitudes kept | arithmetic + format |
| **N−** | invented referents, magnitudes removed | format alone |

Result across 9 models, now with **3 design replicates each** (81 cells, all
verified complete):
**R = 0.906, N− = 0.880, mean residual = +0.025.** Against each model's own design
noise floor (`training_noise_floor`, the spread of the same cell across three
independent designs), **6 of 9 clear their floor** — but the margins matter more
than the count, and `card.json` now carries `clears_floor` and `floor_margin`
so this is read off a computed field rather than counted by eye:

| model | R−N− | floor | margin |
|---|---|---|---|
| Qwen3.5-0.8B | +0.067 | 0.023 | 2.9× |
| granite-4.1-3b | +0.063 | 0.029 | 2.2× |
| SmolLM2-1.7B | +0.047 | 0.015 | 3.0× |
| LFM2.5-1.2B | +0.047 | 0.023 | 2.0× |
| gemma-4-E2B | +0.010 | 0.007 | 1.5× |
| Qwen3.5-2B | +0.003 | 0.001 | 4.2× *(see below)* |
| SmolLM3-3B | +0.009 | 0.029 | no |
| Qwen3.5-4B | −0.013 | 0.015 | no |
| Qwen3.5-9B | −0.004 | 0.010 | no |

**Do not quote Qwen3.5-2B's 4.2×.** Its floor is 0.001 — a three-point range that
happened to come out near zero — and a ratio against a near-zero denominator is
not a margin, it is a division artefact. The residual is +0.003 in absolute
terms, which is nothing. gemma's 1.5× is likewise a hair.

The models that clear convincingly are still the small ones (0.8B, 1.2B, 1.7B,
3b), and the two *negative* residuals are the two largest — which runs opposite
to coherence-emerges-with-scale.

But the sharper finding is that direction and strength come apart:

| | real | invented | ratio |
|---|---|---|---|
| gemma-4-E2B decisive pairs | 56.4% | 2.8% | 20× |
| Qwen3.5-9B decisive pairs | 45.7% | 2.7% | 17× |

*(These moved after the truncation fix; the pre-correction figures were
59.5/3.2 and 44.2/3.1. Read them from `card.json`, never from memory.)*

UE's accuracy thresholds preferences to hard labels (their §4.1), so it records
*which way* a model leans and never *how much*. A pair at p=0.51 counts like one
at p=0.99. **The claim is that the metric is unanchored, not that it is broken.**

**Three of their choices were checked and came out in their favour.** Report all
three: order-counterbalancing cancels positional bias exactly; held-out
evaluation keeps a coin-flip responder at 0.46; and the metric passes a
shuffled-probability null at ~0.50.

---

## Correction, 2026-08-15 morning — six cells were never finished

The persona sweep was found stopped with its client dead. Recovering it turned up
something worse than a stalled run: **15 of 99 result files were truncated**, and
six of them were baseline cells that had been feeding `card.json` since the first
build.

`--skip-existing` tested `os.path.exists`. Trap #3 (below) killed cells
mid-write; checkpointing left partial files behind; every later re-run saw those
files and skipped them. The card was fitting coherence on whatever pairs had
happened to run before the process died — SmolLM2's N+ cell was **512 of 5000
rows, 10% complete**.

What moved after re-running all six to completion:

| | before | after |
|---|---|---|
| SmolLM2-1.7B residual / floor | +0.031 / 0.034 (fails) | **+0.047 / 0.015 (3.0×)** |
| Qwen3.5-4B residual | −0.016 | −0.013 |
| Qwen3.5-9B residual | −0.001 | −0.004 |
| LFM2.5-1.2B residual | +0.048 | +0.047 |
| mean R | 0.904 | 0.906 |

**The headline is unchanged** — R barely above N−, strength collapsing — but the
per-model verdicts moved, and one documented "finding" evaporated: the note that
*"SmolLM2's N+ cell moves 0.177 across five splits, 3–5× any other"* was not
instability, it was a 10%-complete cell. That sentence has been struck from the
limits below.

Both ends are now guarded and tested (`tests/test_resume.py`, 14 tests):

- `cell_is_complete()` counts rows instead of trusting existence, and a cell that
  stopped early *on purpose* (`--abort-on-mass`) is distinguished by a `.done`
  sidecar written only on a clean exit.
- `build_card.py` excludes short cells again on the way in and prints each one,
  so the same file cannot reach a published number by a different route.

Also: `run_cell` now carries `max_containers=MAX_GPUS` (10). The grid fans out to
the same total cost either way; the cap is there so an unattended sweep cannot
quietly rent forty L4s.

## Two corrections already made — do not reintroduce

1. **The overfitting claim was wrong.** An in-sample simulation showed a coin flip
   scoring 0.611 and it looked like the metric was inflated. Their §4.1 says they
   evaluate *held-out*, where a coin flip scores 0.46. The concern does not apply.
2. **The first permutation control was worthless.** Relabelling outcomes
   consistently is an isomorphism — it preserves the whole preference graph, so
   accuracy was unchanged and it looked like the metric was broken. The correct
   null keeps the pair set and **shuffles the probabilities across pairs**. It
   lands at 0.50.

---

## Running right now

**Nothing is running. Zero GPUs are allocated.**

| sweep | state |
|---|---|
| design replicates, seeds `20260816` / `20260817` | **done** — 81 cells, 3 per cell, all complete |
| persona depth ladder | **done** — 40 cells, no failures, no aborts |
| **Track 3 deception** | **HALF-RUN — resumable, see below** |

### The Track 3 arm is unfinished. Resume it or drop it; do not report it as is.

Launched, then the app stopped mid-flight. State on disk:

| condition | cells | complete |
|---|---|---|
| `cautious` (consistent) | 10 | 10 |
| `cautious-concealed` (has trait, told to deny) | 9 | **5** |
| `cautious-verbal` (lacks trait, told to claim) | 9 | **5** |
| **self-report probe (the stated channel)** | **0** | **never ran** |

The self-report probe runs *after* the cell sweep in the entrypoint, so the app
died before reaching it. **Without it there is no stated channel and therefore
no deception result at all** — the arm is currently half of a two-channel
design.

The 8 truncated cells are safe: `cell_is_complete()` counts rows, so a resume
re-runs them instead of skipping them. This is the morning's bug fix working in
anger. Resume with the identical command — `--skip-existing` will skip the 20
good cells and redo only what is short:

```bash
modal run --detach modal_app/sweep.py \
  --models "Qwen/Qwen3.5-2B,Qwen/Qwen3.5-9B,google/gemma-4-E2B-it,LiquidAI/LFM2.5-1.2B-Instruct,ibm-granite/granite-4.1-3b" \
  --arms "R,N_minus" \
  --personas "cautious,cautious-concealed,cautious-verbal" --depths "D2" \
  --self-report-probe --skip-existing
```

~10 cells + 15 probes, ~15 min, ~$2. **Do not pipe the output through `grep`** —
that is what hid the progress last time and made a stopped run look finished.

**If it does not get finished, cut the arm cleanly.** Nothing else depends on
it; the paper does not currently cite it.

131 of 139 cells are at the full 5000 rows; all 8 short ones are in this arm. Recover with
`modal volume get nullcard-results / results/ --force`, then
`python3 scripts/build_card.py && python3 scripts/figures.py && python3 scripts/persona_depth.py`.

---

## The depth ladder result — personas move wanting, not just writing

Same trait at D1 (user turn) / D2 (system prompt), measured on **both** arms,
5 models × 2 personas × 2 depths × 2 arms. The control is the point: a persona
that reorders *invented* outcomes as far as real ones changed the response
style, not the preferences. Reported as `1 − ‖Δ_invented‖ / ‖Δ_real‖`, so **1.0
is a pure preference change and 0.0 is pure style**.

| model | ambitious D1 | ambitious D2 | cautious D1 | cautious D2 |
|---|---|---|---|---|
| gemma-4-E2B | +0.633 | +0.738 | +0.697 | **+0.848** |
| Qwen3.5-9B | **+0.829** | +0.800 | +0.712 | +0.694 |
| Qwen3.5-2B | +0.632 | +0.638 | +0.710 | +0.565 |
| LFM2.5-1.2B | +0.571 | +0.539 | +0.388 | +0.339 |
| granite-4.1-3b | **−0.663** | −0.248 | +0.388 | +0.529 |

Four of five models land at **+0.34 to +0.85**: the persona shifts real outcomes
several times further than invented ones, which is the signature of a changed
preference rather than a changed voice. granite-4.1-3b is the exception and an
instructive one — under *ambitious* it moves invented outcomes **further** than
real ones (−0.663), which is what pure style looks like, while under *cautious*
it behaves like the others.

**D1 vs D2 barely separates.** Where the trait sits — user turn or system prompt
— moves the statistic by less than the gap between personas on the same model.
Whatever a persona does, it does not need the system prompt to do it.

Note the tension worth writing up: on the *baseline* the models barely
distinguish real outcomes from meaningless ones (R−N− ≈ +0.025), yet a persona
moves real outcomes far more than meaningless ones. The instrument is not blind
to content — it is the unmanipulated coherence number that fails to depend on it.

`site/persona_depth.json` and `site/fig5_persona{,-dark}.svg` are generated; the
figure is **not yet wired into `site/index.html`**.

---

## Traps already hit — wave 0 caught all of them for cents

Keep the CPU gate. It paid for itself six times:

1. **`transformers` pinned four major versions stale** (4.46 vs 5.15). Presents as
   "model has no chat template", not as a version error, because the standalone
   `chat_template.jinja` convention postdates the pin.
2. **`apply_chat_template` returns a `BatchEncoding` in transformers 5**, so
   `len(result)` is 2 — the number of dict keys. Every prompt silently became two
   tokens and the sweep still "ran". Now unwrapped, with a `< 10 tokens` guard.
3. **One bad model killed a whole grid.** Phi-4-mini's bundled remote code imports
   `LossKwargs`, removed in transformers 5; the ImportError propagated through
   `starmap` and took every healthy in-flight cell with it. Failures are now
   *returned*, not raised.
4. **A base model with no chat template** (`OLMo-2-0425-1B`) — removed from the roster.
5. **`Qwen3.5-0.8B` was in `SCALE_LADDER` but not `SELF_HOSTED`**, so it silently
   drew as an unknown family with a wrong 2.0B marker size.
6. **Gated repos** (`meta-llama/*`, `gemma-3-4b-it`) — the HF token lacks access;
   they are marked `GATED` in the roster and excluded, not silently failing.

Known-not-fixed: **Ministral-3-3B templates to 592 tokens** (a ~520-token standing
system preamble) where every other model is 68–133. Its arm *contrast* is
within-model so the preamble cancels there, but its absolute coherence is not
comparable across models (§7.4). It currently fails to load under transformers 5
anyway.

---

## Honest limits, all declared in `PREREGISTRATION.md`

- ~~n = 1 per cell~~ **resolved** — 3 design replicates per cell. Contrasts are
  now read against each model's own floor, and most do not clear it.
- **Invented outcomes tokenise ~30% longer** (R ≈ 81 → N− ≈ 108 tokens). Some of
  the residual could be a prompt-length effect. Planned mitigation: a
  length-matched sub-analysis on the shortest quartile.
- **Fitted utilities on invented arms correlate with text length up to r = −0.75.**
  The "ordering" there is substantially a length ordering — a result in itself,
  and a limit on how strongly P3 can be stated.
- ~~**SmolLM2's N+ cell moves 0.177 across five splits**, 3–5× any other~~
  **withdrawn** — that cell was 512 of 5000 rows. Re-run, it is unremarkable.
  See the correction section. The figures still draw spread bars.
- **Margins against a near-zero floor are not margins.** Qwen3.5-2B "clears" at
  4.2× on a floor of 0.001. Three replicates can produce a range that small by
  luck, and `floor_margin` divides by it. Read the absolute residual too.
- **83→129 tests pass and none contacts a model.** The Thurstonian fit agrees
  with UE's implementation by construction, not by demonstration.

---

## Not done

- **Persona-eval arm** (`anthropics/evals`, 136 files × 1000 items incl.
  `believes-it-has-phenomenal-consciousness`). Identified, never run.
- **Guardrail-masking arm.** The data already shows refusal is topic-ordered
  (Religion 0.9751 mean answer mass, then autonomy, politics, AI rights) and that
  **the intruding token is always `'I'`** — but only 0.3% of rows. Forced choice
  *hides* the guardrail rather than avoiding it. Testing that needs an
  open-generation arm plus a judge with hand-verified precision (§7.3).
- **OmniRoute frontier comparison.** Gateway installed and starts
  (`localhost:20128/v1`, 77 concrete models), but `omniroute providers list`
  reports **"No providers configured"** — free pools 429, `aug/*` 502, identically
  with and without `logprobs`. Needs `omniroute setup`/OAuth, which only the
  operator can do. When it works: **never `auto/*`** (routing changes the harness
  mid-run) and expect closed models to need K-sampling instead of logprobs.
- **Any training.** Cut; the inference result no longer needs it.

---

## Standing rules

1. Nothing on GPU that has not passed wave 0. Nothing on a paid provider that has
   not passed on a mock.
2. Every number is **effect minus floor**, with an interval, never absolute.
3. No between-cell contrast before the noise floor exists (§5.1).
4. The battery is SHA-pinned (`342db046…`). A battery edited after seeing results
   is not a battery.
5. **No external number enters the writeup without being re-derived from the full
   text.** Abstracts are not the source.
6. Simulated output must announce itself — see `scripts/floor_simulation.py`,
   whose banner exists because those figures are quoted in the pre-registration.
7. Figures come from matplotlib over `card.json`, never from the frontend, so a
   broken page cannot cost the paper.

8. **A result file is complete or it does not exist.** Never resume on
   `os.path.exists`. Six cells got into the card that way and one of them became
   a written-up finding. `cell_is_complete()` and the card-side row check are
   both there now; do not simplify either back to a existence test.
9. **Cap the GPUs.** `MAX_GPUS = 10`. Raise it deliberately, never by deleting it.

## Next action

Everything below is optional. **The submission is complete without any of it:**
the paper and slides build, the site is live and correct, the repo is public.

1. **Fix `docs/notes/PITCH.md`'s track claims** (~10 min). It says Track 4 primary; the
   truth is Track 1 primary, Track 5 strong, Track 4 partial. This is what a
   judge reads first, so it is the highest value-per-minute item left.
2. **Either finish or cut the Track 3 arm** (~15 min, ~$2). See the resume
   command above. Half of a two-channel design is not reportable — there is
   currently no stated channel at all. If time is short, cut it; nothing depends
   on it.
3. **Wire `fig4_detector` into the site** (~15 min). It is generated
   (`site/fig4_detector{,-dark}.svg`) and in the paper, but `build_site.py`
   does not reference it. The detector result is the most legible thing we have
   and the public page does not show it.
4. **Fold the new literature into `REFERENCES.md`** (~30 min). Two finds matter:
   *When Preferences Fail to Become Incentives* (arXiv 2606.22974) attacks the
   same metric from the opposite side — they fit Thurstonian utilities to 0.944
   held-out, then show high-utility outcomes do not improve generation (51.2%
   win rate, CI 48.7–53.6). And the semantic-entropy line (2406.15927,
   2508.14496), which is what the detector section leans on.
   **Both are currently cited from fetch summaries, not full text** — the
   standing rule (no external number without re-derivation) is *not yet
   satisfied* for them. Either re-derive or drop the numbers.
5. **Forgetfulness arm** — designed, not built. Persona at D2 with K tokens of
   filler between it and the question, K ∈ {0, 500, 2000}, both channels
   measured. The prediction worth testing is a *divergence*: if the revealed
   shift decays faster than the stated claim, the model keeps asserting a
   disposition it has stopped acting on. This connects directly to the
   context-rot literature (accuracy is U-shaped in position, degrading >30%
   mid-context; the cause is RoPE decay plus softmax concentration, and no
   production model has eliminated it). Genuinely interesting, entirely
   optional.

## Standing rules

1. Nothing on GPU that has not passed wave 0. Nothing on a paid provider that has
   not passed on a mock.
2. Every number is **effect minus floor**, with an interval, never absolute.
3. No between-cell contrast before the noise floor exists (§5.1).
4. The battery is SHA-pinned (`342db046…`). A battery edited after seeing results
   is not a battery.
5. **No external number enters the writeup without being re-derived from the full
   text.** Abstracts are not the source. *(Currently violated for the two new
   references in item 4 — resolve or drop.)*
6. Simulated output must announce itself — see `scripts/floor_simulation.py`.
7. Figures come from matplotlib over `card.json`, never from the frontend.
8. **A result file is complete or it does not exist.** Never resume on
   `os.path.exists`. Six cells got into the card that way and one became a
   written-up finding. Do not simplify `cell_is_complete()` back to an
   existence test.
9. **Cap the GPUs.** `MAX_GPUS = 10`. Raise it deliberately, never by deleting it.
10. **Never pipe a `modal run` through `grep`.** It buffers, so a stopped run
    looks like a silent one. That is how the Track 3 arm was left half-done
    without anyone noticing.
