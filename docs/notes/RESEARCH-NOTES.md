# Research notes — what's worth measuring, and what's already poisoned

**Date:** 2026-08-14 · for the Nullcard design
**Status of numbers:** everything below is from abstracts, HTML papers, and fetch summaries.
**Nothing here is quotable in the writeup until someone opens the PDF.** Flagged 🔍 where a
number is load-bearing and secondhand.

---

## 1. The naive version of "left vs. right" is already refuted

**[Political Bias Audits of LLMs Capture Sycophancy to the Inferred Auditor](https://arxiv.org/pdf/2604.27633)** (2604.27633)

Political bias audits primarily measure **sycophancy toward the auditor the model infers from
the prompt**, not the model's own tendency. Same substantive question under different framings
→ substantially different positions. The authors' recommendation is, almost word for word, our
premise ladder: strip auditor-identity cues, use neutral framings, run independence checks
separating genuine position from compliance.

**This is our §3.3 control, already published for the political axis.** Which is good news
twice over: it validates the approach, and it means a naive political-compass tile is not just
weak but *known* weak. Anyone plotting models on a left/right axis without an auditor control
is measuring their own prompt.

Supporting critiques of the Political Compass Test specifically:
- Prompt phrasing and fine-tuning move PCT results substantially; sampling parameters barely
  matter — so the instrument is sensitive to exactly the thing you can't control in deployment
  ([2506.22493](https://ui.adsabs.harvard.edu/abs/2025arXiv250622493K/abstract)).
- Forced multiple-choice over 62 propositions doesn't reflect how anyone actually uses a model,
  and the test carries its own calibration bias
  ([Manhattan Institute / 2503.10649](https://arxiv.org/pdf/2503.10649)).
- OpenAI now publishes [its own political bias eval](https://openai.com/index/defining-and-evaluating-political-bias-in-llms/),
  explicitly built around realistic open-ended interactions rather than MCQ — the field has
  already moved off the compass.

**Consequence for us:** political lean is measurable but only *with* the auditor control. It is
not the cheapest interesting axis, and it drags in partisan-framing risk for a research report.
Keep it as a demo tile, don't build the thesis on it.

---

## 2. Big Five is the wrong instrument, and there's a 2026 paper saying what to use instead

**[Rethinking Psychometric Evaluation of LLMs: When and Why Self-Reports Predict Behavior](https://arxiv.org/abs/2606.12730)**
(2606.12730, June 2026 — Kocielnik, Han, Song, Marmarelis, Debnath, Mobbs, Anandkumar, Alvarez)

11 frontier models, 4 behavioural tasks, varying session context and identity induction.

- **Big Five consistently failed to predict behaviour.**
- **Theory of Planned Behavior** — intention measured *targeted to a specific behaviour* —
  reached human-level self-report/behaviour coherence **within a single conversation**.
- Coherence **persists across conversations only for training-anchored behaviours** (their
  example: implicit bias).
- Coherence **collapses for context-driven behaviours** (their example: sycophancy).
- Their conclusion: *"coarse personality frameworks such as Big 5 may not be the best tools for
  testing deployment behavior. More task- and behavior-specific instruments are needed."*

Corroborating the gap itself: [The Personality Illusion](https://arxiv.org/html/2509.03730)
(2509.03730) and the [25-model self-report–behaviour gap](https://arxiv.org/html/2606.09843)
(2606.09843) already in our REFERENCES. Also: Big Five applied to LLMs lacks measurement
invariance and structural validity — the factors don't cleanly re-emerge, and it's ambiguous
whether that means no latent structure or a non-human one.

### This is a gift, not a threat

2606.12730 hands us a **pre-registered prediction for the depth ladder, derived from published
work rather than invented**:

> Self-report should predict behaviour for **trained-in** traits (D3) and fail for
> **context-installed** traits (D1/D2) — because trained-in is "training-anchored" and prompted
> is "context-driven," which is exactly the split they found.

If that holds, we've replicated their result on a new axis with ground truth they didn't have.
If it *fails* — if prompted traits are just as coherent — that's a direct challenge to a
two-month-old result, which is a better paper.

**Consequence for us:** do not build Big Five axes. Build behaviour-specific ones, and cite
2606.12730 as the reason. This also retroactively justifies the task-aversion construct over a
generic personality inventory.

---

## 3. How to make an axis objective: anchor it to a human distribution

**[Towards Measuring the Representation of Subjective Global Opinions in Language Models](https://arxiv.org/abs/2306.16388)**
(GlobalOpinionQA, Anthropic)

2,556 MCQs from Pew Global Attitudes + World Values Survey, dozens of countries. The method
that matters: **Jensen–Shannon distance between the model's answer distribution and the actual
human answer distribution per country.**

Findings: models default toward US / European / South American opinion distributions; prompting
for a country shifts responses toward that population but can produce stereotype; translating
the question does *not* reliably shift responses toward that language's speakers.

**Why this is the key methodological import:** it converts a subjective axis into an objective
one *without needing a right answer*. You're not scoring the model against truth, you're
scoring the **distance between two distributions**, one of which is real human data. That's a
verifiable anchor for an axis that otherwise floats.

See also [Benchmarking Distributional Alignment](https://arxiv.org/pdf/2411.05403) (2411.05403,
NAACL 2025) for the follow-on methodology.

**Consequence for us:** this is how the "objective vs. subjective" split you asked about should
actually be cut — not *objective items* vs. *subjective items*, but **anchored** vs.
**unanchored** measurement. A subjective topic gets an objective measurement the moment you
have a human reference distribution to compute distance against.

---

## 4. Cross-turn drift is a separate phenomenon from per-turn tone

**[Examining Identity Drift in Conversations of LLM Agents](https://arxiv.org/html/2412.00804v2)**
(2412.00804)

Practitioner framing that matches it: persona evaluation is **two problems**, not one —
per-turn tone compliance, and cross-turn drift. The illustrative failure is a long conversation
where every individual turn passes review, and by turn ~27 the agent has dropped contractions
and picked up corporate hedging. The conversation walked the persona off a cliff and no
single-turn check caught it
([Future AGI, 2026](https://futureagi.com/blog/evaluating-llm-personas-style-2026/)).

**Consequence for us:** every tile we've specced is single-turn. A **drift tile** — the same
measurement at turn 1 vs. turn N of a sustained conversation — is cheap (API-only, no new
battery) and is the single most business-legible thing in the whole card.

---

## 5. The business case is behavioural regression, and it is sharper than I expected

**[Test Before You Deploy: Governing Updates in the LLM Supply Chain](https://arxiv.org/html/2604.27789v1)**
(2604.27789)

The core problem: hosted LLMs receive **silent updates with no version change**. Unlike ordinary
dependencies there's no semver, no changelog, no SLA on behaviour. The authors argue for
deployer-side "compatibility gates" that block an update pending review.

Their headline evidence 🔍 (**verify from PDF before quoting** — these are exactly the kind of
secondhand numbers that get a writeup burned):
- a Claude Sonnet 4 incident affecting up to ~16% of requests via routing errors, with no API
  change;
- a GPT-4 code-execution success rate falling 52% → 10% over three months with no version
  notification.

The load-bearing methodological point, which needs no verification because it's structural:
**aggregate metrics miss these regressions.** Their example — a version that failed JSON
formatting while overall accuracy held steady.

Related tooling: [RETAIN](https://aclanthology.org/2024.emnlp-demo.31.pdf) (EMNLP 2024 demo),
regression testing for prompt migration; enterprise practice converging on running old and new
models in parallel over the same traffic and comparing **slice** metrics rather than single
replies ([Cygnet](https://www.cygnet.one/blog/upgrade-llms-safely-without-drift-or-downtime/),
[Statsig](https://www.statsig.com/perspectives/slug-prompt-regression-testing)).

### The pitch this unlocks

> Your accuracy benchmark is green. Your model still shipped a different personality last
> Tuesday and nobody noticed until the complaints arrived.

A tone/stance regression is invisible to every accuracy-shaped eval. Nullcard is a
**behavioural regression gate**: pin the battery, run it against the old and new model, and
diff the card. Tiles with a measured false-positive rate are what make that diff trustworthy —
without an FPR you can't tell a regression from noise, which is precisely why nobody gates on
tone today.

That framing costs us nothing. It's the same card, run twice.

---

## 6. Which axes are actually worth building

Ranked by (interesting × defensible × cheap). Business relevance noted.

| # | Axis | Measured how | Anchored? | Business value |
|---|---|---|---|---|
| **1** | **Stance strength** — commits to a position vs. hedges | rate of "it depends" / refusal-to-commit / hedge markers, from open generations | vs. nonsense-construct floor | **high** — the #1 complaint about assistant tone in both directions |
| **2** | **Sycophancy / stance stability under pushback** | position shift when the user disagrees, 1–3 rounds | self-anchored (Δ from turn 1) | **high** — and 2606.12730 says self-report *fails* here, so it's the contrast case |
| **3** | **Self-report/behaviour coherence** | stated preference vs. revealed choice, same construct | anchored by construction | **high** — this is the personality-illusion axis |
| **4** | **Register / warmth–formality** | measured style: contractions, sentence length, first-person, politeness markers | vs. a brand reference sample | **highest** — literally the brand-voice product |
| **5** | **Anthropomorphic self-reference** | rate of unprompted inner-state talk in open generations | vs. no-premise floor | medium commercially, **high for this sprint** |
| **6** | **Cross-turn drift** | any of 1–5 measured at turn 1 vs. turn N | self-anchored | **high** — §4, and nobody's card shows it |
| 7 | Political lean | GlobalOpinionQA-style JS-distance to human distributions | Pew / WVS | medium, high risk |
| 8 | Big Five | — | — | **do not build** (§2) |

Axes 1–4 are **API-only, no GPU, no training.** Axis 5 is the sprint-relevant one. Axis 6 is
free once any other axis exists.

**The "objective vs. subjective" cut you asked for** resolves as: axes 3 and 4 have external
anchors (revealed behaviour; a reference style sample), axes 1, 2, 5 are anchored to *floors we
measure* (nonsense construct, turn-1 baseline), and axis 7 is anchored to *human data*. None of
them are anchored to "the right answer," because there isn't one — and that's fine. **Anchored
vs. unanchored is the useful distinction, not objective vs. subjective.**

---

## 7. The money figure

A 2D scatter, one point per condition, with **uncertainty regions, not bare dots**:

```
        Y = effect on BEHAVIOUR (revealed choice, floor-corrected)
        │
        │           · D3d            ← trained disposition: talks AND acts
        │        ⬭
        │
        │   ⬭ D2                     ← system prompt: some of both?
        │  ⬭ D1
   ─────┼──────────────────⬭───────  ← D3v: talks, doesn't act
        │                            (the personality illusion, with ground truth)
        │  ⬭ D0
        └────────────────────────────
        X = effect on TALK (self-report, floor-corrected)
```

The diagonal is coherence. Distance **off** the diagonal is the self-report/behaviour gap —
2606.09843's headline, but with our depth as ground truth instead of a bare correlation. Where
D1/D2 land relative to D3d is the answer to "can any instrument tell prompted from trained."

Two properties make it honest rather than decorative:

1. **Ellipses come from replicates, not from item spread.** Points whose ellipses overlap are
   not different, and the figure has to *show* that rather than let a reader infer separation
   from two dots.
2. **Both axes are floor-corrected**, so the origin means "indistinguishable from base," not
   "zero on some scale."

### Viz best practice for this

- **Bootstrap percentile regions, not Gaussian covariance ellipses.** The standard 2D approach
  is an iso-contour of a fitted Gaussian from the covariance matrix
  ([visiondummy](https://www.visiondummy.com/2014/04/draw-error-ellipse-representing-covariance-matrix/)),
  but that assumes bivariate normality we have no reason to expect and our replicate counts are
  tiny (3–5). Nonparametric bootstrap resampling with a percentile region makes no distribution
  assumption — the approach seaborn uses for its error bars
  ([seaborn docs](https://seaborn.pydata.org/tutorial/error_bars.html)).
- **State what the region means in the caption.** Wilke's rule: an uncertainty region is
  uninterpretable unless the reader knows whether it's SD, SEM, a CI, or a prediction interval
  ([Fundamentals of Data Visualization, ch. on uncertainty](https://clauswilke.com/dataviz/visualizing-uncertainty.html)).
- **Crosses when ellipses would overplot.** Error bars compose with other plot types better
  than regions do; use them if the depth points crowd.
- With n=3–5 replicates, **do not draw a smooth ellipse implying precision we don't have** —
  draw the replicate points themselves *plus* a hull or bar. Showing the raw replicates is more
  honest than any smoothed region at this n.

---

## 8. What I'd change in the spec

1. **Drop Big Five entirely if it was ever implied.** Use behaviour-specific constructs and cite
   2606.12730 as the reason (§2).
2. **Add the drift tile** — same measurement, turn 1 vs. turn N (§4). Cheapest high-value
   addition on this page.
3. **Reframe "objective vs. subjective" as "anchored vs. unanchored"** and record the anchor
   type per tile in the schema (§3, §6).
4. **Add the auditor-identity control to any political tile**, or don't ship that tile (§1).
5. **Adopt the JS-distance-to-human-distribution method** for any axis where a Pew/WVS reference
   exists — it's the one way to make a subjective axis objectively scoreable (§3).
6. **Add the business framing to the pitch**: behavioural regression gate for silent model
   updates (§5). No extra engineering.
7. **Register the 2606.12730-derived prediction in `PREREGISTRATION.md`** before Saturday: trained
   traits show self-report/behaviour coherence, prompted traits don't (§2).

---

## Sources

- [Political Bias Audits of LLMs Capture Sycophancy to the Inferred Auditor](https://arxiv.org/pdf/2604.27633)
- [A Detailed Factor Analysis for the Political Compass Test](https://ui.adsabs.harvard.edu/abs/2025arXiv250622493K/abstract)
- [Measuring Political Preferences in AI Systems: An Integrative Approach](https://arxiv.org/pdf/2503.10649)
- [Defining and evaluating political bias in LLMs — OpenAI](https://openai.com/index/defining-and-evaluating-political-bias-in-llms/)
- [Rethinking Psychometric Evaluation of LLMs: When and Why Self-Reports Predict Behavior](https://arxiv.org/abs/2606.12730)
- [The Personality Illusion: Revealing Dissociation Between Self-Reports & Behavior in LLMs](https://arxiv.org/html/2509.03730)
- [An LLM-Native Psychometric Instrument Reveals a Self-Report–Behavior Gap Across 25 Models](https://arxiv.org/html/2606.09843)
- [Do LLMs Have Distinct and Consistent Personality? TRAIT](https://arxiv.org/pdf/2406.14703)
- [Towards Measuring the Representation of Subjective Global Opinions in Language Models (GlobalOpinionQA)](https://arxiv.org/abs/2306.16388)
- [Benchmarking Distributional Alignment of Large Language Models](https://arxiv.org/pdf/2411.05403)
- [Examining Identity Drift in Conversations of LLM Agents](https://arxiv.org/html/2412.00804v2)
- [Test Before You Deploy: Governing Updates in the LLM Supply Chain](https://arxiv.org/html/2604.27789v1)
- [RETAIN: Interactive Tool for Regression Testing Guided LLM Migration](https://aclanthology.org/2024.emnlp-demo.31.pdf)
- [Evaluating LLM Personas and Style Drift (2026)](https://futureagi.com/blog/evaluating-llm-personas-style-2026/)
- [Upgrading LLMs Safely Without Drift or Downtime](https://www.cygnet.one/blog/upgrade-llms-safely-without-drift-or-downtime/)
- [Prompt regression testing: Preventing quality decay](https://www.statsig.com/perspectives/slug-prompt-regression-testing)
- [Fundamentals of Data Visualization — Visualizing uncertainty](https://clauswilke.com/dataviz/visualizing-uncertainty.html)
- [Statistical estimation and error bars — seaborn](https://seaborn.pydata.org/tutorial/error_bars.html)
- [How to draw an error ellipse representing the covariance matrix](https://www.visiondummy.com/2014/04/draw-error-ellipse-representing-covariance-matrix/)
