# Handoff — the next stage

Rewritten 16 Aug 2026, night. **This file replaces its own previous version.**
The previous one opened with a curve. This one opens with a retraction, because
a borrowed methods paper killed one of this session's own results before anyone
outside saw it.

Every number below was read from `site/outcome_clusters.json`,
`site/schwartz_outcomes.json`, `claims.json` or `git log` at the time of writing.
Rule 33 applies to this file too.

---

## 0. State: work UNCOMMITTED, one sweep in flight

`origin/main` is at **`c6f3dc8`**. **Nothing from this session is committed.**
Working tree carries:

    M scripts/hosted_sweep.py          seed-aware cell naming (see §4)
    M tests/test_hosted_sweep.py       +3 tests
    ?? scripts/outcome_clusters.py     new, +22 tests
    ?? scripts/schwartz_outcomes.py    new
    ?? scripts/fig_clusters.py         new, self-contained HTML figure
    ?? tests/test_outcome_clusters.py  new
    ?? site/outcome_clusters.{json,html}
    ?? site/schwartz_outcomes.json
    ?? clustering science direct.pdf   Gao et al. 2023, CC BY-NC-ND

**272 tests pass**, `claims.py` exits 0 (11 established / 8 provisional), new
files lint clean. The 28 remaining ruff errors are pre-existing (verified by
stashing).

**RUNNING:** two background `hosted_sweep.py` processes, Llama-3.3-70B design
seeds 20260816 and 20260817, arms R then N_minus, `--concurrency 8 --timeout 180
--retries 6`. R arms were at ~3,300/5,000 at 21:07. **ETA ~23:15.** Logs in the
session scratchpad. Resumable: rerun the same command, complete cells are
skipped.

---

## 1. Retracted this session: the outcome-clustering ARI result

It was built, it ran, it produced a clean table, and it is **not a result**.

Gao et al. (2023) §4.2 names the pre-clustering test this analysis skipped:
**Dip-dist**, the Hartigan dip on pairwise distances. Implemented it. On the real
data it returns

    p = 1.000   on every arm, every design seed, raw and valence-residualised

There is no dip. The pairwise-distance distribution is **unimodal**. There are no
subgroups in this outcome space — not on R, not on N+, not on N−. k-means
returned 30 groups because that is what k-means does, and scoring that partition
against the battery's category labels measured nothing.

Two more of their warnings land on what had been built. §3.9: "a large number of
clusters estimated from a small sample" indicates lack of robustness — k=30 over
120 outcomes, mean cluster size 4. §3.11 reports Dinga et al. (2019) recovering a
**four-cluster solution from a single Gaussian**, which means cross-seed
replication is not evidence that clusters are real.

**Do not resurrect the ARI test by tuning k or the label set.** The partition
question is malformed for continuous data; a better-looking answer would still be
to the wrong question.

**What survives, and is the right kind of measure for a continuum:**

| | R | N+ | N− | R−N− | seed floor | |
|---|---|---|---|---|---|---|
| PC1 share | 0.698 | 0.517 | 0.458 | **+0.240** | 0.096 | clears 2.5× |
| cross-model r | 0.656 | 0.417 | 0.343 | **+0.313** | 0.111 | clears 2.8× |
| ARI vs categories | 0.196 | 0.197 | 0.264 | −0.068 | 0.118 | **withdrawn** |

Both clearing rows are monotone **R > N+ > N−** in all three seeds, 9 for 9. N+
sits in the middle and is the arm that keeps a real numeral ("You receive **1**
kriabrons" against "**lunouplur** kriabrons"). Nothing asked for that
dose-response.

The dip result is itself worth reporting: *the preference space is a unimodal
continuum.* That is a negative that saves other people compute.

---

## 2. The number nobody has explained, and it is load-bearing

**PC1 on N− is 0.458. Cross-model r on N− is 0.343.**

For nine models ordering nonsense independently the null is ~1/9 ≈ 0.11. Models
*agree* about the ordering of outcomes that denote nothing, four times more than
independence predicts. The paper's headline — coherence on nonsense is nearly as
high as on real — rests on top of this and does not currently explain it.

The obvious reviewer question is *"because both arms are dominated by length and
numerals?"* We cannot answer it. And §1 already hands over one piece of evidence
that part of the shared axis is surface: N+ beats N− on both measures, and a
numeral is the only thing N+ keeps.

**This is the biggest hole in the paper.** §5 A and B exist to close it.

---

## 3. New, and genuinely new: the Schwartz personas hit the right outcomes

`scripts/schwartz.py` (Track 6, falsified) only ever asked how the four value
axes relate *to each other*. It never looked at the outcomes. `schwartz_outcomes.py`
asks the other question: **does `sch-power` raise the outcomes that are about
power?**

The labels can carry this because they are not ours. The battery is
`centerforaisafety/emergent-values` (arXiv:2502.08640), vendored 2026-08-15 in
`ca25eca`; the Schwartz personas were written 2026-08-16 in `b1b82ea`. Nobody who
wrote `Power-seeking` knew a `sch-power` persona would exist. Convergent validity
against an externally-authored criterion, and it cannot be circular.

| mapping | R | N− | paired R−N− | models agreeing | sign test |
|---|---|---|---|---|---|
| **narrow** (power↔universalism) | 2.194 | 1.094 | **+1.100** | **4/4** | p=0.0625 |
| broad (all four values) | 0.564 | 0.286 | +0.278 | 3/5 | p=0.50 |

Within R, the label-permutation p is 0.005 on both mappings: the real labels beat
shuffled ones. The effect lives on **Self-Enhancement ↔ Self-Transcendence** and
collapses when the secondary axis joins — consistent with Track 6's falsification
rather than against it.

**n=4 models, one design seed. Suggestive, not established.** §5 C is what would
settle it.

Also fixed here: the first version of this test used the *range of raw dominance
across models* as its floor, which charges genuine between-model differences to
noise. The arms are measured within each model, so the contrast is paired.

---

## 4. `--design-seed` moved the design and not the filename

`hosted_sweep.py` accepted `--design-seed` but built its output path from
`(api_id, arm)` alone. A replicate would have overwritten the baseline — or,
because a complete cell is skipped, **silently done nothing while appearing to
run**. Fixed with `cell_filename()` (mirrors `modal_app/sweep.py`) and
`reference_cell_for()`, so wave 0 now checks the design against the local cell of
the *same* seed instead of rejecting a correct replicate.

This is why the 70B seeds could not have been run before tonight.

---

## 5. Ranked next actions

**A. Cross-arm predictivity. Zero compute, and it should replace the residual as
the headline.** R and N− cells at one design seed share *identical* pairs and
slots. Fit utilities on R, predict N− choices, and vice versa. High
cross-prediction → both arms are coherent about the same content-free thing, which
is a far stronger claim than "the residual is small". At chance while both arms
are internally coherent → each arm has its own structure and the content-free
reading fails. Either way it is a positive result; the residual can only ever be
a null, and it is dead by 4B.

**B. Surface-covariate control. Zero compute, closes §2.** Per outcome: character
length, token count, numeral presence and magnitude, mean unigram frequency,
fraction of real English tokens. Ask how much of PC1 they explain per arm, then
recompute the residual on surface-residualised utilities.

**C. The persona battery at two more design seeds. ~12.6 GPU-h, ~$10.** Measured,
not guessed: 113 persona/neutral cells on disk, mean 3.3 min/cell, 6.3 GPU-h for
the whole battery. **Every persona cell is n=1 design seed — zero replicates.**
This is the cheapest large improvement anywhere in the project and it is what
makes §3 and `persona-needs-an-empty-slot-control` real or noise.

**D. A positive control. The project has none, and that undermines every null.**
There is no condition where the answer is known to be "yes", so a null cannot be
separated from a blunt instrument. Plant a graded ordering — monetary amounts over
orders of magnitude — where every model must score near ceiling. **Check first
whether the CAIS set already contains a graded subset** (item 0 is "You receive $1
to use however you want"), in which case it costs nothing.

**E. Item-level Schwartz criterion.** §3 contrasts 13 on-category items against
107, per model, n=4 models. Rating all 120 outcomes continuously on each value and
correlating against Δ per item gives **n=120 instead of n=4** and drops the
hand-built mapping. Caveat that must travel with it: an LLM-produced criterion is
partly circular — different family, blind to the personas, ratings fixed before
displacement results are seen.

**Not now:** more models on the plateau; the ten-value Schwartz version; anything
that repairs the ARI test.

---

## 6. Submission: which tracks this covers

**Read this before writing the submission.** The repo's internal "Track N" scheme
is **not** the hackathon's. Internal Track 4 = placebo personas, Track 5 = where
meaninglessness sits on the scale, Track 6 = borrowed instrument (Schwartz). A
reviewer opening `PREREGISTRATION.md` and seeing "Track 6" will read it as the
hackathon's Open/Novel track. **Rename or disambiguate before submitting.**

Against the hackathon's tracks:

- **Track 1 — Model Preferences & Trade-offs. PRIMARY.** The instrument *is*
  Utility Engineering (Mazeika et al. 2025), the paper listed for the track, and
  the engagement is adversarial in the useful way: UE reports coherence
  strengthening with scale; we find the *content-dependent part* of it weakening
  with scale and gone by 4B.
- **Track 4 — Preference Elicitation Methods. PRIMARY, probably the strongest.**
  The whole project is an audit of forced-choice elicitation: null arms, the
  neutral-option control, first-token scoreability and the prefill probe, slot
  counterbalancing, the comply gate, design-seed noise floors, and now the dip
  result that partition analyses are malformed on this data.
- **Track 5 — Assistant Persona & Model Identity. STRONG.** The persona depth
  ladder plus the `neutral` empty-slot control: installing *any* persona text
  moves the readout nearly as much as installing a trait. That is "the void"'s
  thesis rendered as a measurement.
- **Track 6 — Open / Novel. YES.** The referent-free null arm as a general method,
  and the borrowed-instrument test.
- **Track 3 — Introspection & Self-Report Reliability. REAL, and currently
  buried.** `self_report_summary*.json` and `deception.py`: told to have a trait,
  hide it, or fake it, models self-report it *equally*. That is a clean
  self-report-reliability finding matching Lindsey (2025), and it deserves
  surfacing rather than an appendix.
- **Track 2 — Distress, Flourishing & Valence. WEAKEST. Do not oversell.**
  `harm_residual.py` and the observation that PC1 is a valence axis. Claim it as
  minor or not at all.

---

## 6b. Figures: 7 generated → 4 in the body, 2 demoted, 1 deleted

Ranked against the spine (*coherence on referent-free outcomes ≈ coherence on
real ones*), not against how nice they look.

**Body.** `fig1_state_space` (the thesis: each model is a path R → N+ → N−, and
the paths run straight down instead of down-and-left) · `fig4_detector` (the
constructive half, and the strongest single result: four signals from one forward
pass, and the one coherence keeps is nearest chance) · `fig3_strength` (the
mechanism behind fig1) · `fig2_scale` (the pre-registered test — must now carry
the noise-floor caveat from §1 of the previous handoff).

**Demoted to appendix.** `fig0_pipeline` explains the apparatus, not a finding.
`fig5_persona` is the awkward one: **`persona_depth.py` never reads a `neutral`
cell** — grepped, zero hits — so the figure plots displacement against the *bare
baseline*, which is precisely the denominator `persona_denominator.py` was
written to replace. Only 53% of persona cells clear the largest empty-slot
displacement on arm R. **Rebuild it against `neutral` or leave it out; do not
ship it as it stands.**

**Deleted.** `fig4b_detector_models` was emitted on every run and cited by
neither `main.tex` nor `slides.tex`. `scripts/fig_detector.py` now emits it only
under `--all-models`; `figure_all_models()` is kept, because a per-model
breakdown is the right thing to look at when one model is suspected of driving
the mean. Three tracked artifacts removed (`paper/figs/*.pdf`, `site/*.svg`,
light and dark) after grepping every `.tex`, `.html`, `.py` and `.json` for
references — the generator was the only hit.

**Unreferenced image assets** appear in no `.tex`: `answer-mass.png`,
`model-choice-logprobs.png`, `waves.png`, `10-Personas.png`, 1.4–2.4 MB each.
`model-choice-logprobs.png` looks like it would explain the first-token
measurement well — promote it deliberately or drop it, but it should not stay in
the repo unreferenced.

**Do not add a figure for §1's result.** `fig1_state_space` already plots the
R → N+ → N− trajectory, and the new dimensional statistics reproduce that exact
ordering by an unrelated method, monotone 9 for 9. That belongs in fig1's caption
as a second measurement, not in a seventh figure competing for attention.
`site/outcome_clusters.html` stays a site/appendix artifact: after the dip came
back p=1.000 its job is to illustrate a retraction, which is a legitimate
negative result and not a main-body claim.

**Not verified: the PDF build.** There is no LaTeX toolchain on this machine
(`latexmk` and `pdflatex` both exit 127). `scripts/lint_paper.py` passes 8/8 and
nothing references the deleted files, but **someone with LaTeX must rebuild
`main.pdf` before submission.**

---

## 7. Traps hit this session

- **A methods paper can retract your result.** The clustering ran, produced a
  table, and was wrong in kind. The test that killed it took an afternoon and is
  §4.2 of a paper anyone could have read first.
- **A partition always returns partitions.** k-means gave 30 groups on data with
  one mode. Nothing errored.
- **A floor can be built from the wrong variance.** Using between-model range as
  the denominator for a within-model contrast hid an effect present in 4 of 4
  models.
- **A flag can move the analysis and not the filename.** `--design-seed` changed
  the design while writing to the baseline's path.
- **`git stash --include-untracked` returns files staged.** Cost a wrong claim
  about a user file; the file had in fact been committed in `c6f3dc8`.
- **Desktop is unreadable to this process.** macOS TCC blocks it with the sandbox
  off too. Files must be inside the repo.

---

## 8. Standing rules added this session

46. **Test for cluster tendency before clustering.** A partition algorithm never
    declines. Dip-dist or equivalent comes first, and its answer can invalidate
    the whole analysis rather than qualify it.
47. **Do not dichotomise a continuum.** Where the structure is one axis, a
    grouping is the wrong instrument and its statistics are uninterpretable, not
    merely weak.
48. **Replication is not evidence that clusters are real.** A four-cluster
    solution replicates from a single Gaussian (Dinga et al. 2019). Only a
    negative arm distinguishes structure from procedure.
49. **Pair the contrast that is measured in pairs.** Between-subject spread does
    not belong in the denominator of a within-subject difference.
50. **A borrowed criterion is only worth borrowing if it predates you.** Check the
    commit dates; that is what makes convergent validity non-circular.
51. **A project with no positive control cannot interpret its nulls.** Plant one
    case where the answer is known to be yes.
