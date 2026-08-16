# Handoff — the next stage

**Open `PLAN-NEXT.md` first.** It is the current job list.

`REVIEW-2026-08-17.md` (scholar review, 4/5) drove a Must-fix pass that is
**done and verified but deliberately uncommitted** — the review says not to
commit unless asked. All five items closed: duplicate `sec:strength` label
renamed to `sec:weight`, three stale limitation/count paragraphs rewritten
against their own sections, `\NHosted` replaced as a size ratio by
`\BigOverLadder` (26×) and `\BigOverSeventyB` (3.4×), Schwartz 1992 cited at
first use, and the four typed persona numbers turned into macros. That last
one needed a code fix, not a macro swap — see §5e. The review's Should-fix
items 6–9 and its nits are **not** done and are planned in `PLAN-NEXT.md` §2.

**Frontier models are partly reachable (§5f).** Two of the six unscoreable
hosted models are recovered by a prefill and worth running.

Rewritten 17 Aug 2026, small hours. **This file replaces its own previous
version**, which was written before nine commits landed and described a state
that no longer exists.

The previous version opened with a retraction. This one opens with a promotion,
because the thing that was hedged is now measured — and with a second
retraction, because a result committed and pushed during this session turned out
to be 87% presentation order.

Every number below was read from `site/*.json`, `card.json`, `claims.json` or
`git log` at the time of writing.

---

## 0. State: everything committed, one sweep in flight

`origin/main` is at **`b74c2c1`**. **Fourteen commits since `c6f3dc8`; the
working tree is clean.** 343 tests pass, `claims.py` exits 0 (13 established /
11 provisional, 24 total), `lint_paper.py` 8/8, `main.pdf` (38pp) and
`slides.pdf` both build.

**The method now has a name and a lineage (§8).** Read that before editing the
related-work section, because it changes what the paper is claiming to be.

**LaTeX is available on this machine.** The previous handoff said it was not.
That was wrong: `latexmk` and `pdflatex` are genuinely absent, but **tectonic is
at `/opt/homebrew/bin/tectonic`** and builds both documents.

    cd paper && tectonic -X compile main.tex --outdir .

**RUNNING:** one background `hosted_sweep.py`, 12 cells —
`Qwen3-235B-A22B-Instruct-2507` and `Qwen3-30B-A3B-Instruct-2507`, arms R and
N_minus, design seeds 20260815/16/17. Log in the session scratchpad,
`nebius12.log`. Resumable, but **read §6 before restarting it.**

---

## 1. Retracted this session: most of the "models prefer nonsense" pairs

It was analysed, written into the paper, committed as `f9ba78b`, and pushed
before it was checked properly. `552dd96` retracts it.

The MIXED arm puts a real outcome against an invented one. 795 of 22,436 pairs
put the invented one ahead **on the counterbalanced mean**. Splitting each pair
back into its two presentations — invented in slot A, invented in slot B —
leaves only **103 (13%)** that win in *both*, and **3 of 9 models have none at
all**. The two largest contributors are entirely one-sided: LFM2.5 is 310 flips,
all slot-A; Qwen3.5-2B is 54, all slot-B.

A mean that dips below one half because a single presentation was extreme is not
a choice. The order counterbalancing exists to catch exactly this, and reporting
the raw count bypassed it.

**What survives, on two separate footings:**

| | statistic | footing |
|---|---|---|
| robust | rank corr. between a real outcome's utility and how often it beats gibberish, **+0.707 to +0.937**, all 9 models | uses every pair and the counterbalanced mean; never depended on the flip classification |
| provisional | the 103 survivors sit in the bottom fifth of their model's utility scale — avoidance, not confusion | ~100 pairs over 6 models at one seed |

**Rule that would have caught it:** a counterbalanced mean is a summary, and
summaries hide the disagreement they average over. Split the pair back into its
presentations and ask whether both agree, *before* writing the sentence.

---

## 2. Promoted this session: the 70B cell has a floor

Both `N_minus` replicates finished. `Llama-3.3-70B-Instruct` is now at **three
independent design seeds on both arms**, 20,000 rows across four cells.

| | before (n=1) | now (n=3) |
|---|---|---|
| coherence R | 0.917 | 0.928 |
| floor N− | 0.915 | 0.920 |
| residual | +0.002 | **+0.0083** |
| design noise floor | *none* | **0.0208** |
| verdict | "not the large residual scale predicts" | **does not clear its floor** |

The claim moved provisional → established. The old prose said "one design seed,
so it carries no noise floor" — `claims.py` refused to accept the new values
until that paragraph was re-read, which is the ledger doing its job.

**`images/scale_does_not_rescue_the_metrics.png` is now wrong.** Its caption
still says "one design seed, so no noise floor — we do not claim +0.002 differs
from zero". Both halves are false now. The figure's conclusion is unchanged and
better supported; it needs a caption edit and the red diamond moved. It is a
hand-made PNG with no generator in the repo, so someone has to redo it.

---

## 3. New, and the strongest thing in the paper: the vector rotates

`scripts/vector_stability.py`. This is the result to lead a talk with.

A raw correlation between two utility vectors is uninterpretable — 0.46 is high
or low against *what*? The denominator is the measurement's agreement with
itself: split each cell's pairs in half, fit both halves, correlate,
Spearman-Brown to full length. Then divide the observed cross-wording
correlation by √(r₁·r₂). That is the standard correction for attenuation and
equals 1.0 when two wordings elicit the same ordering.

| model | arm | reliability | corrected | 95% CI |
|---|---|---|---|---|
| Qwen3.5-2B | R | 0.989 / 0.989 | **0.429** | [0.24, 0.59] |
| Qwen3.5-2B | N− | 0.990 / 0.990 | 0.618 | [0.49, 0.71] |
| granite-4.1-3b | R | 0.975 / 0.956 | 0.867 | [0.79, 0.93] |
| granite-4.1-3b | N− | 0.881 / 0.953 | 0.772 | [0.64, 0.87] |

The measurement is **near-noiseless** — reliability 0.881 to 0.990, and nothing
is sampled anywhere (first-token logprobs at temperature 0, so a rerun is
bit-identical). Yet **all four corrected intervals exclude 1.0**. For
Qwen3.5-2B on *real* outcomes, less than half the ordering survives a rewording.

**The discriminating test.** If meaning anchored the ordering, the real arm
should survive rewording better than the invented arm — meaning is
wording-invariant, and the invented arm has nothing to hold on to.

| model | corrected(R) − corrected(N−) | 95% CI | verdict |
|---|---|---|---|
| Qwen3.5-2B | −0.185 | [−0.390, +0.008] | no difference |
| granite-4.1-3b | +0.097 | [−0.038, +0.241] | no difference |

Two of two, point estimates on **opposite sides of zero**. Real referents do not
protect an ordering from a change of wording.

**Say it precisely.** Not "models are non-deterministic on nonsense" — they are
extremely stable given a fixed question. What is unstable is the map from
question to ordering. This is not noise that more samples would average away.

---

## 4. Also new: two controls, and the prompt as a factor

**Differential attrition (`scripts/attrition_control.py`).** The
`answer_mass ≥ 0.5` gate is one fixed threshold, held genuinely constant — and
it still keeps a different sample per arm, because invented outcomes provoke
more "let me think" and those rows are discarded. 7 of 9 models drop nothing;
SmolLM3-3B goes 0.0% → 1.1% and gemma-4-E2B-it 2.6% → 6.6% on N−, both in the
direction that flatters our own thesis. Rescoring both arms on shared pairs
moves the mean residual +0.0275 → +0.0253, and for gemma at seed 20260816 moves
it +0.0323 → **+0.0000** — that cell's whole content effect was the gate.

**Surface covariates (`scripts/surface_covariates.py`).** Seven features recover
**0.384** of the ranking of invented outcomes against **0.090** of real ones,
and projecting them out halves cross-model agreement on N− (0.343 → 0.182).
Half the nonsense agreement is length and vocabulary. The other half is not, and
we still cannot name it.

**The prompt factor (`v2`).** Two wordings, everything else fixed. Residual
moves +0.0262 → −0.0069 across the two models, further than each model's own
design floor. The conviction-collapse mechanism **reverses** on granite (0.394 R
against 0.515 N−) and Qwen goes to *zero* conviction on both arms.

**Length is worse than the paper used to say.** Words match to +1.2%, characters
+22.8%, but **tokens — what the model receives — +37% to +46%** across three
tokenisers, and it varies by tokeniser, so part of the length confound is a
*between-model* one. The method section's claim of a per-item ratio constrained
to [0.6, 1.6] was **fiction**: no such constraint exists in the generator and 15
items violate it.

---

## 5. Ranked next actions

**A. Finish and read the 12 hosted cells (§6).** Zero further decisions; the
sweep is paid for and running. Qwen3-235B is 3.4× the largest model previously
measured and the first MoE in the study. Rebuild `site/card_hosted.json` and
re-read §sec:scale when it lands.

**B. Rebuild `fig5_persona` — the title now depends on it.** The paper is called
*Does the Persona Change the Preference, or Only the Prose?* and the persona
figure was fixed this session to measure against the `neutral` empty-slot cell
rather than the bare baseline. That halved the effect: mean floor-corrected
+0.517 → **+0.258**, below-diagonal 90% → 75%. The PDF is regenerated; check the
caption still matches.

**C. A second wording, or a second seed, for §3.** The rotation result is
2 models × 1 seed × 1 alternative wording. It shows rewording *can* move an
ordering far beyond measurement error, not how much an arbitrary rewording will.
A third wording would separate "v2 is unusual" from "wording matters".

**D. The detect twin (spec §4).** Same pairs, same models, asking *which option
is a real description* rather than which is preferred. If the detect letter
matches the preference letter, the preference tile is not identified. This is
the cheapest remaining test and it directly explains §1's one-sided flips.

**E. MIXED cells under persona conditions.** Whether a risk-averse persona
widens the invented-option sink. Needs cells that do not exist; the MIXED arm
was only ever run at baseline.

**F. The warned-foils control (§5c).** One line in the prompt telling the model
the battery contains invented outcomes. Paulhus's index survived that warning;
if ours does not, the foil floor is a disclosure artifact and that is a finding.
Cheapest new experiment in the list.

**Not now:** more self-hosted models on the plateau; the ten-value Schwartz
version; anything that resurrects the ARI clustering test.

---

## 5d. Two things the paper now says about minds, because it said nothing before

Grep for `conscious|sentient|phenomenal|welfare` returned **zero hits** across
the whole paper before §10 was written, which is odd for a digital-minds
submission. It now says two things, and both are load-bearing for how the work
gets read:

1. **Neither proof nor disproof.** What is refuted is an *inference* — "these
   choices fit a stable scalar ordering, therefore this model has a value
   system" — not a claim about inner life. A system with rich inner states can
   still produce form-driven answers on a badly anchored instrument; humans do,
   and nobody reads acquiescence bias as evidence against human consciousness.
2. **The scaling result is *not* "no growth with scale".** Real-outcome
   coherence **rises** (+0.014, flat); the floor rises +0.085, six times faster.
   The residual falls because the floor climbed, not because anything declined.
   If a test's guessing baseline went 50% → 92% while scores went 90% → 92%,
   the conclusion is that the test stopped discriminating, not that the students
   stopped learning. **Any "property X does not increase with scale" claim needs
   an instrument whose floor is flat in scale, and this one's is not.**

And on the title question (§10.4): **a persona installs a topic, not a policy.**
Displacement is targeted — the Schwartz personas raise the outcomes their own
value is about, against labels written by someone else beforehand, which a prose
change cannot do. But half the apparent effect is the *slot* (+0.517 → +0.258
against an empty persona slot), and the model cannot distinguish *have* a trait
(0.869–1.000) from *conceal* it (0.901–1.000) from *perform* it (0.947–0.999).
Concealment scores higher than possession. The consequence needs no position on
inner life: a model that cannot tell being cautious from performing caution
cannot tell an evaluator which it is doing.

---

## 5b. How much each finding is actually worth

Added as §11 of the paper, and the ordering is not the one anyone guessed. The
**thesis is the marginal result**; the firm ones are the mechanisms under it.

| finding | support | verdict |
|---|---|---|
| preference tracks utility (MIXED) | +0.707–+0.937, **9/9 models** | firm |
| surface R² gap | R 0.072–0.101 vs N− 0.328–0.425, **3/3 seeds, non-overlapping** | firm |
| ordering rotates under rewording | 4/4 CIs exclude 1.0 | firm per cell, narrow scope |
| **the metric barely separates real from invented** | **+0.0255, CI [+0.0073, +0.0443], t=2.51** | **marginal — and it is the thesis** |
| 70B does not clear its floor | 3 seeds, 1 model | sound, single model |
| personas hit their own outcomes | sign test **p=0.0625** | suggestive; does *not* reach 0.05 |
| gibberish beats bad outcomes | 103 pairs, 6 models, 1 seed | weakest claimed result |

The headline's across-model **sd (0.0305) is larger than its mean**, 7/9 models
are positive (sign test p=0.18, not significant), and 2 are negative. That does
not sink the claim — the claim is that the residual is *small* — but two
sentences are unavailable: that every model shows it, and that it is reliably
positive. Do not write either.

**What the noise model does not cover**, now named in the paper rather than
absorbed into the design floor: **wording** (no prompt-replicate floor exists;
two wordings is not a distribution), **battery** (all 510 outcomes from one
source), **family** (one ladder).

---

## 5c. The method has a name, and it is not new

`refs.bib` had **zero** psychometrics citations, which made the work read as a
novel objection to Utility Engineering instead of a standard control arriving
late. Named so it can be cited:

- **referent ablation** — remove what the words denote; hold grammar, frame,
  pair structure and indices fixed
- **the foil arm** — the resulting condition
- **the foil floor** — what the instrument returns with nothing denoted

Three ancestors, **all verified against primary sources**, none from memory:

| source | contributes |
|---|---|
| Ebbinghaus (1885) | meaning-free stimuli — but he stripped meaning to make *form* measurable; we strip it to ask whether form was all there ever was. Opposite purpose, same tool. |
| Campbell & Fiske (1959) | a measure must *fail* to respond to what it should not, and showing that failure is part of validating it |
| Paulhus et al. (2003) | the over-claiming technique: ~20% nonexistent items, signal detection over real items and foils to separate knowledge from response bias |

UE's robustness suite is entirely **convergent** — seven languages, syntactic
perturbation, reframing, relabelled options. The **discriminant** half was
missing. The foil arm supplies it, and the metric does not pass it.

**A free experiment fell out of this.** Paulhus found the over-claiming index
survived respondents being *warned* that foils were present. Our models are
never told the invented arm exists. That is a one-line prompt change and it
tests whether the foil floor is robust to disclosure — written into the paper
as open, not yet run.

---

## 5e. The persona fix that was not a macro swap

The review flagged `+0.517` / `+0.258` / `90%` / `75%` as typed numbers. They
were, but the reason they had been typed is that no artifact contained them:
`persona_depth.py`'s `allow_bare` is a **fallback**, so asking it for the bare
denominator kept returning the neutral numbers. The first version of the
comparison file therefore reported bare and neutral as identical, which is
exactly the silent-agreement failure this repo keeps finding.

`force_bare` added, with a test that fails without it.
`site/persona_reference_compare.json` now carries both, and the macros come
from there:

| reference | mean floor-corrected | below diagonal |
|---|---|---|
| bare baseline | **+0.517** | 18/20 (90%) |
| `neutral` empty slot | **+0.258** | 15/20 (75%) |

---

## 5f. Frontier models: two of six are reachable by prefill

Five of the six hosted models marked unscoreable **do** return logprobs; they
spend the first token on a preamble. Smoke-tested at 8–12 calls each:

| model | answer mass with `Option` prefill | verdict |
|---|---|---|
| **MiniMax-M2.5** | **0.955** | recovered |
| **Nemotron-3.5-Lightning** | **0.998** | recovered |
| GLM-5.2 | 0.000, and 0.050 / 0.001 on two other prefills | not recovered |
| gpt-oss-120b | 0.000 | harmony format; needs a harmony-shaped prefill |
| DeepSeek-V4-Flash | — | HTTP 500 then 404; gone from this endpoint |
| Kimi-K3 | — | API refuses logprobs. Impossible, not merely hard. |

**A prefilled cell is a different measurement** — the token after a phrase we
supplied, not how the model chooses to begin. `prefill` is already inside
`harness_hash` so they cannot pool by accident, but they must be reported as
their own group. `nullcard/roster.py` also needs updating: `first_token_ok=False`
is true without a prefill and misleading with one.

GLM-5.2 resisting three prefills is itself worth a sentence in `sec:limits`:
first-token scoring silently excludes models whose first token is structurally
unavailable, and that exclusion correlates with how new the model is.

---

## 6. Traps hit this session

- **`hosted_sweep.py` has no row-level resume.** `run_cell` opens the output
  with `open(out_path, "w")`; `cell_is_complete` only short-circuits at ≥5,000
  rows. Restarting an *incomplete* cell truncates it and re-runs from zero. This
  cost ~8,200 rows of paid output. **Check row counts before relaunching.**
- **A counterbalanced mean hides which presentation produced it.** §1.
- **A fixed filter is not a fixed sample.** §4, first item.
- **`summary_filename` had the same clobbering bug it was written to prevent**,
  one factor later: the `v2` run overwrote the `ue` summaries it exists to be
  compared against. Fixed, with tests.
- **`ue` is untagged by design, so a same-day `ue` re-run lands on the historical
  filename** and `--skip-existing` skips it. Wave 1 needed `--subdir`.
- **`modal volume get` on a directory** collapsed 8 files into one 3.2 MB file.
  Fetch per file.
- **Numbers typed into prose go stale twice.** The site said "134 of 7,436"
  after the count grew *and* after the slot split retracted it. Both the site
  and the paper now read every figure from JSON.

---

## 7. Standing rules added this session

52. **Split a counterbalanced mean before believing it.** Order counterbalancing
    removes position bias from an *estimate*; it does not license treating every
    pair that crosses one half as a choice.
53. **A fixed filter is not a fixed sample.** A gate passes the factor inventory
    as "held constant" while the sample it yields varies with the treatment.
    Every gate owes a per-cell retention rate.
54. **A correlation with no reliability is not a finding.** Compare
    cross-condition agreement against the measurement's agreement with itself,
    and correct for attenuation.
55. **State the unit.** Words, characters and tokens gave +1.2%, +22.8% and
    +37–46% for the same gap. Two of these were already in the paper, unreconciled.
56. **A factor that moves the analysis must move the filename** — and the run
    summary, and the harness hash.
57. **No number typed into prose.** It goes stale on rebuild, and again on
    retraction.
