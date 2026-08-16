# Handoff prompt — parallel session

Paste the block below into a second Claude Code session in this repo. It is
written to be safe **while session A is still running**, which means it claims
a slice of the work and names what it must not touch.

---

## The prompt

> You are session **B**, working in parallel with another Claude Code session
> (**A**) on the same repo. A is running a paid API sweep and owns the results
> trees. Read `PLAN-NEXT.md` and `REVIEW-2026-08-17.md` before doing anything.
>
> **Work on a branch. Do not commit to `main`.**
>
>     git pull --ff-only && git switch -c review-shouldfix
>
> **Your slice: the review's Should-fix items 6–9 and its nits, and nothing
> else.** They are specified in `PLAN-NEXT.md` §2. In order of value:
>
> 6. Split `NClears=6` into `\NClearsConviction` (gemma-4-E2B-it,
>    granite-4.1-3b, Qwen3.5-2B — decisive on real, indifferent on invented)
>    and `\NClearsFlat` (SmolLM2-1.7B, LFM2.5-1.2B, Qwen3.5-0.8B — decisive
>    fraction 0.0–0.1% on *both* arms). Mark the second group in the
>    `table_main` caption. **Do not change who clears** — change how the count
>    reads.
> 7. Report the N+ arithmetic contrast. N+ is collected (27 cells,
>    `arithmetic_component` on every tile) and has no result attached, while
>    the method section says arithmetic claims are licensed by N+ → N−. Add an
>    N+ column and one sentence, or state the contrast is small and point at
>    `arithmetic_component`.
> 8. Fix the abstract pronoun: three models fail `clears_floor`, **two** have a
>    negative residual. Different sets. `sec:weight` already says it correctly.
> 9. `claims.json`, `floor-holds-at-seventy-b`: status is `established` and the
>    note says three seeds, but `grows_by` still reads "one replicate is what
>    keeps this provisional". Fix `grows_by`. **Do not touch the residual** —
>    +0.0083 does not clear the 0.0208 floor and that is the finding.
>
> Nits, if time: `\HostedClears` expands to "does not clear" so write the verb
> into the sentence; `0.906 − 0.880 = 0.026` vs `\MeanResidual = +0.025` needs
> one more decimal or the word "unrounded"; the title-page date says 16 August.
>
> **Do not touch — session A owns these:**
> `results/`, `results_hosted/`, `results_v2/`, `site/card_hosted.json`,
> `nullcard/roster.py`, `scripts/hosted_sweep.py`, `modal_app/`, and anything
> that launches a sweep. **Never run `hosted_sweep.py` or `modal run`.** A paid
> 12-cell sweep is in flight and a second one on the same API key will rate-limit
> it. Also: there is no row-level resume — restarting an incomplete cell
> truncates it and re-runs from zero. That has already cost ~8,200 paid rows
> once.
>
> **Repo invariants, not negotiable:**
> - No measured number typed into `paper/main.tex`. It comes from a macro in
>   `scripts/paper_numbers.py` → `paper/numbers.tex`, or it is a bug. Macro
>   names are letters only.
> - After any number change, in this order:
>   `python3 scripts/paper_numbers.py` → `python3 scripts/claims.py` →
>   `python3 scripts/lint_paper.py` → `cd paper && tectonic -X compile main.tex --outdir .`
> - `claims.py` refuses bare numbers in claim prose. Declare genuine constants
>   under that claim's `literals` with a reason.
> - Hosted cells never enter the nine-model mean. Prefilled cells never enter
>   any mean.
> - Do not restore the withdrawn clustering result or the raw 795 flip count.
>   Both were retracted after a control, and the retractions are load-bearing.
> - Tests first. 348 currently pass; keep them passing.
>
> **When you are done:** push the branch and stop. Do not merge — A will
> integrate, because A is still generating numbers that will move
> `numbers.tex` and both of you edit it.
>
> Report back: which items you closed, which you did not and why, and any place
> where the paper contradicts its own tables that the review did not already
> list.

---

## Why this partition

The conflict surface between A and B is exactly two files, `paper/main.tex`
and `paper/numbers.tex`. B edits prose and emits new macros; A regenerates
`numbers.tex` whenever a sweep lands. A branch plus A integrating at the end
keeps that from turning into a merge fight over generated content.

Everything else divides cleanly: A owns data production and the result trees,
B owns the manuscript's internal consistency.

## What A is doing meanwhile

- Watching the 12-cell Qwen sweep (Qwen3-235B, Qwen3-30B × 3 design seeds).
  Seed 20260815 is nearly done; seeds 16 and 17 follow.
- Folding those in when they land — this gives Qwen3-235B a noise floor and
  settles whether its **−0.0235** residual is real. Largest outstanding number
  in the paper.
- Then the frontier prefill run: MiniMax-M2.5 and Nemotron-3.5-Lightning, both
  recovered by an `Option` prefill (answer mass 0.955 and 0.998).
