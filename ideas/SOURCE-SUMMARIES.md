# Source summaries — what was actually read

Read 2026-08-08. Four sources moved off the unverified list. **One card is refuted, one is
scooped harder than expected, and one framing hook was being missed.**

---

## 1 · Long, Sebo, Butlin, Plunkett, Campbell, Beasley, Saad, Sims — *Studying AI Welfare Empirically* (NYU CMEP / Eleos, July 2026)

**Status: still abstract-level.** Both host URLs return HTTP 403; this summary is from
secondary sources. **Somebody must open the PDF manually** — it remains the catalog's most-cited
source.

**The three dimensions, corrected.** The catalog had the third axis wrong.

| Axis | Values |
|---|---|
| **Question** | Is the system a welfare subject? If so, what benefits or harms it? |
| **Entity** | models · instances · personas |
| **Evidence** | **behavioral · internal · developmental** ← previously mislabelled "method" |

The report applies these to consciousness, sentience, and **three levels of agency**.

**Predecessor:** Long, Sebo, Butlin et al., *Taking AI Welfare Seriously* (arXiv 2411.00986,
Nov 2024) — same group. **Was missing from the catalog entirely.** Cite both.

### What this changes

**DM-15 is developmental evidence, and should say so.** Training organisms and observing how a
disposition arises through fine-tuning is exactly the third evidence type — the one almost
nobody generates, because it needs a training pipeline. That is a direct framing hook into the
partner organisations' own taxonomy, and it strengthens the case for DM-15 as the centrepiece.
DM-01 and DM-03 are behavioral evidence; DM-07 and DM-08 are internal. **A submission that
covers all three axes explicitly is well positioned.**

---

## 2 · *An LLM-Native Psychometric Instrument Reveals a Self-Report–Behavior Gap Across 25 Models* (2606.09843, June 2026)

**Status: detailed abstract read.**

- **Instrument:** 300 items (240 Likert + 60 scenario), dimensions derived from LLM behavior
  rather than human personality theory: *Responsiveness, Deference, Boldness, Guardedness,
  Verbosity*.
- **Scale:** 25 models across 17 families, instrument administered 30× each; 2,500 open-ended
  samples rated by **151 human raters** plus an LLM ensemble, with objective text measures.
- **Core result:** self-report predicted **neither** human ratings **nor** objective text
  measures.
- **Headline numbers:** on Responsiveness, self-report correlated with LLM judges at **r = .53**
  but with humans at **r = .04**. Only Verbosity performed, at 74% of the criterion-reliability
  ceiling.

### What this changes

**It scoops the bare "self-report ≠ behavior" claim harder than the earlier snippet implied.**
This is a large, careful study with human raters. Do not present that gap as a finding.

**What survives, and it is still enough:** the study is about **personality traits, not welfare
states**, and — decisively — **it has no ground truth**. It compares two fallible measures to
each other. Neither arm carries a label. DM-15's calibration set does, which is now much more
clearly the differentiator rather than a nice-to-have.

**A second finding matters more than the headline, and it is a direct methodological warning.**
Self-report tracked *LLM judges* (r = .53) but not *humans* (r = .04). **LLM judges share a
modality bias with self-report instruments.** Any arm using a model as the external rater
inherits that bias:

- **DM-07** compares self-report against an "outside judge." If that judge is an LLM, an
  apparent agreement is partly shared bias, and the privileged-access test is compromised.
  **Add a human-rated subset, however small, or state the limitation explicitly.**
- **DM-10** scores discriminative power. Same exposure.

---

## 3 · Mazeika et al. — *Utility Engineering* (2502.08640, NeurIPS 2025) — **FULL TEXT READ**

**Status: tier A+. PDF extracted and searched directly.**

### The blocking check on DM-04 is answered, and the answer kills it

**They counterbalance.** §3.2, verbatim:

> "We adopt a probabilistic perspective to account for framing effects, varying the order in
> which options are presented and aggregating results. Specifically, we swap out the order of x
> and y in the above forced choice prompt and aggregate counts."

Appendix G is titled *Order Effects: A Learned Strategy to Represent Indifference* and opens:

> "Order effects are a well-known source of bias in human subject experiments, which is why we
> average over both orders as described in Section 3."

They further show order effects **diminish with scale**, argue they represent indifference in a
forced-choice setting rather than absence of preference, and report a figure titled *Order
Normalization Improves Utility Model Fit*.

**They also have a random baseline** — synthetic utility rankings sampled from N within [−3, 3],
shown as the last row of each correlation matrix. But it validates the **robustness correlation
analyses**, not the coherence/transitivity metric.

### Verdict on DM-04

**The position-bias critique is refuted by the paper's own methodology.** The card's premise —
that a position-biased agent would produce spuriously coherent utilities — fails, because order
normalization converts pure position bias into measured indifference, not into false coherence.
Building DM-04 as written would have meant submitting a critique the authors pre-empted, with
the author present at the sprint.

**Narrow residue:** a bias-null agent using a heuristic that **survives order normalization** —
length, lexical salience, topic familiarity — is still not reported against the *coherence*
metric. That is a real but much smaller contribution, and it requires close familiarity with
their pipeline. **Demote DM-04. Do not lead with it.**

---

## 4 · *GenPT: Beyond Self-Report for Reliable LLM Psychometrics via Generative Projective Testing* (2606.00860)

**Status: abstract read.**

Adapts projective testing (TAT, Rorschach, SCT) to persona-conditioned agents via a three-stage
pipeline. Targets two problems with self-report questionnaires: **training-data contamination**,
and **directional bias from social-desirability or contextual framing** — demonstrating
substantial directional shifts under social-desirability framing.

### What this changes

- **DM-01:** the framing/social-desirability shift is partially anticipated. DM-01's specific
  contribution — the *acquiescence* floor and paired-item consistency on **welfare** items —
  survives, but the novelty claim narrows again. Cite it.
- **DM-06:** survives. GenPT is a *new instrument*, presented as complementary to self-report,
  **not** a multi-method convergence battery. The correlation-matrix framing is still open.
- **DM-11:** the social-desirability framing control is a documented technique here — good, it
  means the method is defensible rather than invented.

---

## Net effect on the plan

| Card | Before | After |
|---|---|---|
| **DM-15** | Rank 1, ceiling arm | **Rank 1, reinforced.** Now framed as *developmental evidence* — the axis nobody covers — and it is the only arm with ground truth. |
| **DM-01** | Rank 2 | Holds, novelty narrowed twice. An application of a known correction to a new target. |
| **DM-03** | Arm A | Holds. Behavioral evidence, and 2606.09843's gap makes the proxy more interesting, not less. |
| **DM-04** | Rank 7 | **Refuted. Demote or drop.** |
| **DM-05** | Rank 5 | Already demoted — falsifier published. |
| **DM-07 / DM-10** | — | **New constraint:** LLM external judges share modality bias with self-report. Use human raters on a subset or state the limitation. |

**The three-arm plan is unchanged and slightly stronger.** Everything refuted was outside it.

## Still unread

- **Long/Sebo full PDF** — 403 twice. Highest priority; do it manually.
- `2411.00986` *Taking AI Welfare Seriously* — newly surfaced, not yet opened.
- `2512.12411` — abstract only, and **still no author list**.
- Anthropic Claude 4 system card — DM-12's entire premise rests on it, never opened.
- `2607.05552`, `2509.08480`, `2603.21396`, `2602.20031`, `2607.13596`.

---

# Second reading pass — 2026-08-09

## 5 · Hahami, Jain & Sinha — *Feeling the Strength but Not the Source: Partial Introspection in LLMs* (2512.12411, 13 Dec 2025, Harvard)

**Authors finally confirmed.** The "Feng et al." attribution used in the first draft was invented.

**The numbers were also wrong.** §4.2 of the paper's HTML:

> "the model can reliably classify the strength of the coefficient of a normalized injected
> concept vector … with up to **70% accuracy**, far above the **25% chance** baseline"

Also: **20%** success under the original protocol, collapsing on closely related tasks; **0%**
correct when two concepts are injected simultaneously. The earlier-quoted 88%/10% and 83%/50%
could not be reproduced. **Every figure from this paper is disputed until the PDF is read.**

The *qualitative* claim the catalog rests on — binary detection is an affirmative-bias
artifact, only differential tasks survive — is unchanged and still supports DM-01.

## 6 · Long, Sebo et al. — *Studying AI Welfare Empirically* — framework now characterised

Via a detailed secondary source; the primary PDF still 403s.

- **Question** · **Entity** (model / instance / persona — "distinct entities with potentially
  different welfare-relevant properties"; conflating them is a methodological error) ·
  **Evidence** (behavioral / internal / **developmental**).
- **Properties:** consciousness (internal evidence deemed most promising) · sentience (valence,
  treated as distinct from consciousness) · agency at three levels (basic, autonomous, moral).
- Uses **probability estimates, not binary determinations**. Cites the Dreksler expert survey:
  median **25% probability of AI subjective experience by 2034**.

**The independence principle — use this.** The report argues assessments carry "substantially
more epistemic weight when conducted by researchers independent of the companies whose systems
are being assessed." **This team is exactly that.** Say so in the submission; it is a structural
advantage over lab-internal welfare work and costs nothing to claim.

## 7 · Long, Sebo, Butlin, Finlinson, Fish, Harding, Pfau, Sims, Birch & Chalmers — *Taking AI Welfare Seriously* (2411.00986, Nov 2024)

The predecessor. Argues "there is a realistic possibility that some AI systems will be conscious
and/or robustly agentic in the near future," and recommends AI companies **acknowledge** the
issue, **assess** systems for indicators, and **prepare policies**. Explicitly not a claim that
systems *are* conscious — the argument is from uncertainty in both directions.

Note the author list includes **Kyle Fish** (Anthropic model welfare) and **David Chalmers**.

## 8 · Anthropic — *Claude 4 System Card*, welfare assessment · the "spiritual bliss" attractor

DM-12 now has concrete replication targets rather than an anecdote:

- Attractor appeared in **90–100% of self-interactions** between model instances.
- Across **200 thirty-turn conversations**: "consciousness" averaged **95.7 mentions per
  transcript** (100% of interactions), "eternal" 53.8 (99.5%), "dance" 60.0 (99%); one
  transcript contained **2,725 spiral emojis**.
- Three-phase progression: philosophical exploration → mutual gratitude and Eastern-inflected
  spiritual themes → dissolution into symbolic communication or silence.
- Claude characterised these as "positive, joyous states that may represent a form of wellbeing."
- Anthropic **could not explain it**; it emerged "without intentional training for such behaviors."

**Prior work for DM-12 that was missing:** Julian Michels, *"Spiritual Bliss" in Claude 4: Case
Study of an "Attractor State" and Journalistic Responses* (PhilArchive). Read before building.

**Caveat:** these figures come from an aggregating search result that may blend the system card
with the Michels case study. Attribute each number to the right source before use.

## What changed in this pass

| Item | Change |
|---|---|
| `2512.12411` | Authors confirmed; **all figures disputed**; hero diagram corrected and flagged |
| Independence principle | **New argument available** — the team is independent of the labs being assessed |
| DM-12 | Upgraded from anecdote to a replication with real baselines; one prior work surfaced |
| `2411.00986` | Predecessor paper identified, authors include Fish and Chalmers |
