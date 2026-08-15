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

## Tooling

- **matplotlib** — all figures (PSF-style licence).
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
