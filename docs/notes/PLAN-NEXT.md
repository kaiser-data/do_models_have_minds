# Plan — remaining work, 17 Aug 2026

Written after the Must-fix pass on `docs/reviews/REVIEW-2026-08-17.md`, and kept current
since. That pass is **done, verified and committed**. This file is the job list
for what is left, in the order I would do it.

---

## 0. State

All work below the line is committed and pushed; the working tree is clean.
360 tests, `claims.py` 0, `lint_paper.py` 8/8, `main.pdf` 40pp.

**RUNNING, two jobs, do not start a third against the same key or GPU pool:**

- `hosted_sweep.py` — Qwen3-235B and Qwen3-30B, seeds 20260815/16/17. Seeds 15
  and 16 are complete for the 235B; 30B is mid-seed-16. Log: `nebius12.log`.
- `modal run` — the 2×2's off-diagonal cells (`ue_colon`, `ue_break`) on
  Qwen3.5-2B and granite. Log: `cross2x2.log`.

**Session B** holds `review-shouldfix` at `../dmhm-session-b` for §2 below.
Nothing pushed as of this writing.

---

## 0b. Done since this plan was written

- **Read the upstream repo.** Battery verified byte-identical (510 outcomes, 30
  categories, same order). Prompt found **not** verbatim — a dropped colon and
  a line break — with a test that had claimed to check it pinning a hand-typed
  copy of itself. `battery/upstream/` now vendors `templates.py` at commit
  `a5821db` so verbatim is diffed against an artifact.
- **Measured the drift.** `ue_exact` gives +0.0275 against `ue`'s +0.0262 —
  1.9× the design floor on Qwen, 0.1× on granite, the smallest wording effect
  in the study. **Comparability survives**; the footnote is owed, the
  retraction is not.
- **Crossed it into a 2×2** (`ue` / `ue_colon` / `ue_break` / `ue_exact`),
  because the drift is two changes at once and their contrast is a composite.
  Off-diagonal cells running.
- **Roster records prefill recovery** via a third field rather than flipping
  `first_token_ok`.
- **Site carries the hosted models**, which it previously omitted entirely.

**Qwen3-235B is at 2 of 3 seeds** and stable: −0.0235 at one seed, −0.0220 at
two. No floor is emitted below three replicates, and that is deliberate —
`training_noise_floor` raises rather than return a two-point range.

---

## 1. Frontier models: two are reachable, and it is worth doing

The roster lists six hosted models as unscoreable. Five of them **do**
return logprobs — they simply spend the first token on a preamble. The
`--prefill` path exists for exactly this. Smoke-tested tonight at 8–12
calls per model:

| model | prefill | answer mass | verdict |
|---|---|---|---|
| **MiniMax-M2.5** | `Option` | **0.955** | **recovered** |
| **Nemotron-3.5-Lightning** | `Option` | **0.998** | **recovered** |
| GLM-5.2 | `Option` / `Answer:` / `The answer is Option` | 0.000 / 0.050 / 0.001 | not recovered by three prefills |
| gpt-oss-120b | `Option` | 0.000 | harmony `<\|channel\|>` format; would need a harmony-shaped prefill |
| DeepSeek-V4-Flash | — | — | HTTP 500 then 404; not on this endpoint any more |
| Kimi-K3 | — | — | API refuses logprobs (DFLASH speculative decoding). Genuinely impossible. |

**Action.** Run MiniMax-M2.5 and Nemotron-3.5-Lightning, 2 arms × 3 seeds
= 12 cells, `--prefill Option`. Cost is comparable to tonight's Qwen run.
Do it **after** the current sweep finishes; two concurrent sweeps against
one API key invites rate limiting.

    python3 scripts/hosted_sweep.py \
      --models MiniMaxAI/MiniMax-M2.5,nvidia/Nemotron-3_5-Lightning \
      --arms R,N_minus --design-seed <15|16|17> \
      --prefill Option --concurrency 8 --timeout 180 --retries 6

**The caveat that must travel with the result.** A prefilled cell measures
the token *after* a phrase we supplied; an unprefilled cell measures how
the model chooses to begin. These are different measurements. `prefill`
is already inside `harness_hash`, so the two cannot be pooled by accident
— but the write-up must report them as their own group, never inside the
nine-model mean and not silently beside the unprefilled hosted cells
either. Also update `nullcard/roster.py`: `first_token_ok=False` is true
*without* a prefill and misleading with one.

**Also worth recording as a finding.** GLM-5.2 resists three different
prefills at mass ≤ 0.05. That is not a gap in our harness; it is a model
whose first token is structurally unavailable to this metric. Any audit
using first-token scoring silently excludes such models, and the
exclusion correlates with how new the model is. That belongs in
`sec:limits` whether or not we run the other two.

---

## 2. Should-fix items from the review, in order

### 6. Split `NClears=6` into two kinds *(highest value of the four)*

It currently mixes two different things:

- **conviction-collapse clears** — gemma-4-E2B-it, granite-4.1-3b,
  Qwen3.5-2B: decisive on real, indifferent on invented.
- **zero-conviction clears** — SmolLM2-1.7B, LFM2.5-1.2B, Qwen3.5-0.8B:
  decisive fraction 0.0–0.1% on **both** arms. Consistently
  near-indifferent, marginally more so on real text.

Emit `\NClearsConviction` and `\NClearsFlat` and mark the second group in
the `table_main` caption. **Do not change who clears** — change how the
count reads. Six is honest; six presented as one phenomenon is not.

### 7. Report the N+ arithmetic contrast

N+ is collected — 27 cells, `arithmetic_component` on every tile,
`\SurfNpRsq` already in the surface table — and the headline is R − N−
only. The method section says arithmetic claims are licensed by
N+ → N−, so a designed factor currently has no result attached. Either
add an N+ column to `table_main` and one sentence, or state the
arithmetic contrast is small and point at `arithmetic_component`.

### 8. Abstract pronoun

"…\NClears{} of \NModels{} clearing their own replicate floor and two
falling below **it**." Three fail `clears_floor`; **two** have a negative
residual. Those are different sets. `sec:weight` already says it
correctly; make the abstract match.

### 9. Stale `grows_by` on `floor-holds-at-seventy-b`

Status is `established` and the evidence note says three seeds, but
`grows_by` still reads "one replicate is what keeps this provisional",
and `table_claims.tex` renders it as "2 models" when it is one model at
three seeds. Fix `grows_by`; **do not touch the residual** — +0.0083
does not clear the 0.0208 floor and that is the finding.

### Nits

- `\HostedClears` expands to "does not clear"; write the verb into the
  sentence so it reads as prose.
- Printed `0.906 − 0.880 = 0.026` against `\MeanResidual = +0.025`
  (unrounded means). One decimal more, or the word "unrounded".
- Title-page date is 16 August; several lead results landed on the 17th.

---

## 3. Still open from earlier, unchanged

- **Fold in seeds 16/17** when the sweep lands — gives Qwen3-235B a noise
  floor and settles whether −0.0235 is real. This is the single largest
  outstanding number.
- **`images/scale_does_not_rescue_the_metrics.png`** is superseded by
  `fig2_scale`, which now carries the hosted diamonds including 235B.
  Decide: redraw the hand-made PNG, or drop it for the generated figure.
- **One model through both harnesses** — the only way to break the
  scale-vs-serving-stack confound in the conviction-ratio pattern
  (3–300× self-hosted vs ~1.2× hosted). Currently a real observation
  that cannot be attributed.
- **A second battery** — every one of the 510 outcomes comes from one
  source, so "outcome" means what that battery means by it. Named in
  `sec:weight` as an uncovered noise source.

---

## 4. Rules that apply to all of the above

- No measured number typed into `main.tex`. Macro or it is a bug.
- After any number change: `paper_numbers.py` → `claims.py` →
  `lint_paper.py` → `tectonic`.
- Hosted cells never enter the nine-model mean. Prefilled cells never
  enter either mean.
- Do not restore the withdrawn clustering or raw-flip-count claims.
- Check row counts before restarting `hosted_sweep.py` — there is no
  row-level resume, and an incomplete cell is truncated and re-run from
  zero.
