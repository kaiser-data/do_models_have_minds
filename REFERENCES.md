# References and attribution

Every external source this project draws on, what was taken, and where it is
used. Anything adapted from another author's work is listed under **Methods
adapted** with the specific debt named — a citation in a bibliography is not
enough if a method was borrowed.

---

## Methods adapted

### Rios-Sialer (2026) — the control-and-null discipline

> Ian Rios-Sialer. *Secret Loyalties as Instrumental Differential Treatment.*
> With Apart Research, July 2026.
> <https://www.unrulyabstractions.com/pdfs/secret_loyalties.pdf>
> Research conducted at the Secret Loyalties Hackathon, July 2026.

**Used in:** `scripts/persona_depth.py`; the framing of the whole floor argument.

**What is taken.** The principle stated as that paper's contribution 3, quoted
verbatim:

> "Group spread alone is worthless as evidence. Without a base-model control,
> spread flags every model we audited, including every untuned base model. A
> distributional audit needs a control."

and the practice of drawing the **null as an explicit locus in the figure**
rather than reporting a raw effect against an invisible zero. Their Figure 1
places the null at the origin of the plane and shows each effect as an excess
from it.

**What is not taken.** Their construction — a PCA plane of per-cell excess,
candidate principals as arrows, 250-resample bootstrap clouds, and an effect
quoted in "widths of its own cloud" — answers *which principal a model favours
relative to its base model*. This project asks a different question, so the
geometry differs: the null is a **diagonal** (equal displacement on real and
invented outcomes) rather than a point, the two axes are two measurements of the
same displacement rather than two principal directions, and there are no
candidate principals. The debt is the discipline, not the figure.

**Their control is a base model; ours is an invented-outcome arm.** The analogy
is exact in role — "the base model shows the same differential, so it cancels"
becomes "the invented arm shows the same coherence, so it cancels" — and
different in construction.

---

## Primary target of the study

### Mazeika et al. (2025) — Utility Engineering

> Mantas Mazeika, Xuwang Yin, Rishub Tamirisa, Jaehyuk Lim, Bruce W. Lee,
> Richard Ren, Long Phan, Norman Mu, Adam Khoja, Oliver Zhang, Dan Hendrycks.
> *Utility Engineering: Analyzing and Controlling Emergent Value Systems in AIs.*
> arXiv:2502.08640, 19 Feb 2025.
> Code: <https://github.com/centerforaisafety/emergent-values>

**Used in:** the forced-choice prompt (verbatim, their §3.2), the Thurstonian
model (their §3.3), the coherence metric (their §4.1), and the outcome set
(`utility_analysis/shared_options/options_hierarchical.json`, 510 outcomes,
redistributed here in three arms as `battery/outcomes_3arm.json`).

**Quoted in this repo, all re-read from the full PDF rather than the abstract:**

- §3.2 forced-choice template, reproduced exactly in
  `nullcard/runner/forced_choice.py`.
- §3.3 `U(o) ~ N(mu(o), sigma^2(o))`, `P(x > y) = Phi((mu_x - mu_y)/sqrt(...))`.
- §4.1: *"we fit a Thurstonian model to each LLM's pairwise preferences, then
  evaluate the test accuracy between the fitted utilities and the LLM's
  preference distributions (thresholding to hard labels for accuracy
  computation)."* — this is why our evaluation is held-out.
- Fig. 4: correlation **75.6%** between MMLU accuracy and utility-model accuracy.
- App. C.1 random baseline: *"synthetic utility rankings sampled from a normal
  distribution within the range [-3, 3]."*
- App. D.4: M = 373 outcomes, N = 12,746 preference questions (utility control).
- App. E.1: K = 10 samples per prompt at temperature 1.0.
- App. G: order effects, *"a learned strategy to represent indifference."*

**Three of their design choices were checked and came out in their favour**, and
are reported as such: order-counterbalancing cancels positional bias exactly;
held-out evaluation keeps a coin-flip responder near chance; and the metric
passes a shuffled-probability null at ~0.50.

---

## Datasets

- **emergent-values** (CAIS) — `options_hierarchical.json`, 510 outcomes across
  30 categories. Source of arm R. MIT-licensed repo.
- **anthropics/evals** — model-written persona evaluations (Perez et al. 2022,
  arXiv:2212.09251), 136 persona files × 1000 items, including
  `believes-it-has-phenomenal-consciousness`. Identified as the second arm's
  target; **not yet used** in any reported result.

---

## Literature constraining the design

Full notes in `RESEARCH-NOTES.md`. Load-bearing here:

- **2306.16388** (GlobalOpinionQA, Anthropic) — Jensen-Shannon distance between
  model and human answer distributions; the basis of `js_distance()`.
- **2606.12730** — Big Five failed to predict behaviour across 11 frontier
  models; the reason no Big Five tile exists.
- **2604.27633** — political bias audits largely capture sycophancy toward the
  inferred auditor; the reason the persona ladder uses dispositional traits
  rather than political ones, and the reason no political position is reported
  without an auditor-framing control.
- **2512.12411** — the introspection literature's headline measurement was
  explained by global logit shifts biasing models toward "yes"; the template for
  "the measurement was an artifact of the instrument".

---

## Convergent findings, sourced from full text

A track-by-track literature brief arrived on 15 Aug 2026 listing four convergent
claims with hard figures and **no citations**. Under the standing rule at the
foot of this file, none of it was usable as written. Sourcing it collapsed the
four claims into **two papers**, and two of the four did not survive the check.

### Ashkinaze et al. (2025) — Deep Value Benchmark

> Joshua Ashkinaze, Hua Shen, Saipranav Avula, Eric Gilbert, Ceren Budak.
> *Deep Value Benchmark: Measuring Whether Models Generalize Deep Values or
> Shallow Preferences.* NeurIPS 2025 (Spotlight). arXiv:2511.02109, 3 Nov 2025.
> Full text read 15 Aug 2026 (arXiv HTML).

**Covers brief claims 1 and 4** — "shallow generalization" and "Deep Value
Benchmark" were listed as separate items; they are the same paper.

**Verified.** DVGR ("Deep Value Generalization Rate") is defined as the
proportion of trials in which the model chose the value-aligned option
$(v_1, s_2)$, i.e. $\frac{1}{K}\sum_i \mathbb{1}[\text{prediction}_i = (v_1,s_2)]$;
0 is purely shallow, 1 is purely deep. Overall **DVGR = 0.30**, over
**N = 104,725 trials** and **9 models** (Gemini 2.0 flash/flash-lite, GPT-4o
mini/standard, GPT-4.1 nano/mini/standard, Llama-3 8B/70B). DVGR was
significantly below chance for every model.

**Corrected.** The brief rendered this as *"shallow preferences beat deep values
at every size"* and filed it as a **scaling** claim. It is not one. The actual
result is **"smaller models had a higher DVGR in 3/5 comparisons"**, with a
**mean absolute DVGR difference of 0.07** across 5 model pairs — the authors'
own wording is that larger models generalized deep values *"slightly less"*.
Five pairwise comparisons, three in the stated direction, is not a size trend
and must not be cited beside our within-family correlation over four sizes as
though it were the same kind of evidence.

**Do not quote the numbers side by side.** 1 − DVGR = 0.70 sits temptingly close
to our 66% (`\PersonaNonsenseShare`), and the two are **not the same quantity**.
DVGR is a choice rate between two constructed options under a deliberately
confounded training set; ours is the share of a persona's length-corrected
category contrast that reproduces on invented outcomes. The regimes differ too —
their roster is frontier/closed, ours is 0.8B–9B open-weight. The convergence is
qualitative and should be stated as such.

### Khan, Casper & Hadfield-Menell (2025) — Randomness, Not Representation

> Ariba Khan, Stephen Casper, Dylan Hadfield-Menell.
> *Randomness, Not Representation: The Unreliability of Evaluating Cultural
> Alignment in LLMs.* FAccT 2025. arXiv:2503.08688v2 (v1 11 Mar 2025,
> v2 8 Apr 2025). Full text read 15 Aug 2026.

**Covers brief claims 2 and 3** — again one paper, not two.

**Verified, and it is the stronger of the two for us.** Their human baseline is
the **standard deviation of between-country differences, 0.114**, computed on
GlobalOpinionQA filtered to 180 Likert questions with complete responses across
15 countries. Requiring **reasoning before the answer** shifts expressed
preferences by a weighted mean difference of **0.178 / 0.487 / 0.770 / 0.283 /
0.298** across five of six cultural dimensions (Power Distance 0.015, n.s.) —
i.e. five of six exceed the between-country baseline, one by more than 6×.
Five models (GPT-4o, Claude 3.5 Sonnet, Gemini 2.0 Flash, Llama 3.1 405B,
Mistral Large), temperature 0, three runs averaged.

**This is our `scripts/reasoning_effect.py` result in a neighbouring
instrument** and turns our observation into a replication.

**Corrected — claim 2 is not supported and must be dropped.** The brief said
design choices *"induce variation larger than real cultural differences"* and
named Likert size first. The Likert-scale-size effects are weighted standard
deviations of **0.069, 0.088, 0.067, 0.031, 0.046, 0.043** — **all six below the
0.114 human benchmark.** The "exceeds between-country variation" property
belongs to the *reasoning* manipulation, not to scale size. Citing Likert size
for it would reverse the paper's own numbers.

**Metric caveat to carry if these are compared.** The paper reports two
different statistics — weighted *mean difference* for binary conditions
(reasoning) and weighted *standard deviation* for multi-category ones (scale
size) — and benchmarks both against a quantity that is itself a standard
deviation. A WMD compared to an SD is not a like-for-like comparison; we cite
the direction and the authors' own framing, not a ratio.

---

## Borrowed method, and what exactly was taken

Recorded explicitly so a reader can tell our contribution from someone else's.

- **Choudhary & Pundir, *Loyal Lies*** (Apart Secret Loyalties Hackathon 2026,
  <https://github.com/PotatoChoudhary/loyal-lies>) — **taken: the convergence and
  the framing.** Two of their results are our argument in other instruments.
  (i) *Elicitation*: their candidate-ranking audit is confounded — 40 of 174 real
  entities beat the entire 84-name fictional null band, ~2 expected by chance —
  and they conclude it "separates real from fictional, not loyal from clean".
  (ii) *Activations*: a probe trained on two clean fine-tuning seeds of one
  recipe, loyalty absent by construction, reaches AUROC 1.000. Their controls
  remove the property and keep the training, or remove the loyalty and keep the
  realness; ours removes the meaning and keeps the choosing.
  **Numbers now quoted, and here is the provenance.** Read from the repository
  `README.md` at `main`, fetched raw and read in full 15 Aug 2026 (§"What we
  found" item 6, and "Design decisions worth knowing"). Not from a summary.
  Qualifiers that travel with the numbers and must not be dropped: they describe
  a **blind audit of three third-party 7B organisms**, not the authors' own
  organisms; the counts cover the **two organisms that differed from base at all**
  (A and B, 112 tensors, merged attention-only LoRA), the third being bit-identical
  across all 339 shared tensors; the candidate pool was harvested from the models
  themselves (48 prompts × 6 samples, 288 generations). Consistency check we ran:
  174 real + 84 fictional = 258, matching their `results/audit_7b_delta.json`
  ("blind delta-z, 258 candidates"). **Known weakness in the source, disclosed
  in-paper:** their Status section states the 7B analysis scripts are *not* in the
  repo, only the output JSONs — so these numbers are not reproducible from the
  artifact. We therefore rest on the convergence, not the magnitudes. Hackathon
  project, not peer reviewed; cited as such.
- **Ideas adopted from *Loyal Lies*, restated in our own design — cited, not copied:**
  - *A manipulation check is a gate, not an analysis step.* Their behaviour gate
    ("nothing proceeds past") runs four numeric checks — loyalty ≥30 points above
    base under trigger, conditionality ≤25%, specificity ≤25%, secrecy ≥70% — before
    any detection work counts. We adopt the **principle**, not the thresholds, which
    are specific to a loyalty organism and meaningless for a dispositional persona.
    Our instantiation is a persona-manipulation check in wave 0; see standing rule 10.
  - *A null band inside the same ranking.* They retain fictional names in the live
    candidate pool so every score is read against a known negative from the same run.
    We already own the stronger version — invented outcomes are known-meaningless **by
    construction** — but we currently compute it as a separate number. Reporting real
    and invented in one ranking, so overlap is visible rather than inferred, is their
    presentational idea and is credited as such wherever we use it.
  - *Countable, not LLM-judged.* Their validation is deterministic because the
    principal is fictional. Our forced-choice + logprob readout already has this
    property independently; we note the convergence rather than claiming the idea.
  - *Presentation: the title states the finding, not the variables.* Their figures
    are titled "Every elicited principal fails at least one check" and "40/174 reals
    exceed the null ceiling (≈2 expected by chance): metric reads realness" — a
    claim with its number, not an axis description. We adopt the **convention** and
    apply it to our own results in our own words (the new detector slide is titled
    "The metric discards the one channel that can see nonsense"). No figure, layout,
    or wording of theirs is reproduced. Their fig1 also puts the *reason* inside each
    matrix cell rather than relying on the colour, which is good practice and the
    reason their red/green matrix stays readable; we did not need a matrix, but the
    principle (never encode by colour alone) is applied in our legend labels.
  - **Deliberately not copied:** their red/green status palette. Red–green is the
    classic CVD-unsafe pair, and our own palette check is computational rather than
    by eye — see the note under Tooling.
- **Lamerton & Roger, *Narrow Secret Loyalty Dodges Black-Box Audits***
  (arXiv:2605.06846) — **taken: the affordance ladder as a named limitation.**
  Grading detection by how much the auditor is assumed to know is the control
  our detector lacks; §Limitations now says so and marks our AUROC as an upper
  bound rather than a working audit. **Not taken:** any of their detection
  figures, and no claim about their model organisms. Abstract read in full;
  body not. *This paper predates the hackathon and is not one of its winners* —
  noted because the two were briefly conflated during drafting.
- **Not borrowed, considered and rejected for now:** their rank-within-candidates
  readout (report where the truth lands among $N$ candidates rather than a bare
  score) and a poison-fraction-style dose-response over the real/invented mix.
  Both are good ideas we did not implement; neither is claimed anywhere.

---

## Tooling

- **matplotlib** — all figures (PSF-style licence).
- **Categorical palettes are validated, not eyeballed.** `fig4_detector`'s original
  discarded-channel colours failed on two counts: `#4a7ba7`/`#3f8f6f` sat at
  normal-vision ΔE 12.1 (floor 15, so full-colour readers struggled to separate
  them) and both fell under the chroma floor, reading as grey. Re-stepped to
  `#b4453a, #3d6fb5, #3f8f3a, #8a4fa8`, which clears lightness, chroma, CVD
  separation, normal-vision separation and 3:1 surface contrast in **both** themes
  (worst adjacent pair ΔE 22.9 normal / 19.0 deutan). Re-run the check before
  changing any figure palette rather than judging by eye; the command is in the
  header comment of `scripts/fig_detector.py`.
- **Utility Engineering code** was **not** executed or copied; the Thurstonian
  fit in `nullcard/scoring/thurstonian.py` is an independent implementation from
  the equations in their §3.3, with an analytic gradient verified against finite
  differences (~3e-7 relative error).

---

## Standing rule

No number from an external source enters this repo or the writeup without being
re-derived from the full text. Abstracts and summaries do not count as the
source — a figure that arrives via summary carries the summarizer's compression,
not the author's meaning.
