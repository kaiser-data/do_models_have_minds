# An objective disposition card for language models

A study design. Written 16 Aug 2026, out of the nullcard results and the review
pressure on them. Nothing here has been run; the point is that most of it is
cheap, and that the order matters more than the content.

---

## 0. The defect this exists to fix

*Utility Engineering* reports coherence 0.91 and concludes value systems emerge.
This repo reran the identical procedure on outcomes whose content words were
replaced by consistent nonwords and got **0.88**. The published number was not
wrong. It was **unanchored** — reported without the floor underneath it, and the
floor turned out to be almost all of it.

Every LLM "personality" number in circulation today has that shape: a score with
no floor, no retest band, and no statement of what it would take to be wrong. A
model card assembled from such numbers inherits the defect once per row.

**The rule that fixes it, and the only non-negotiable in this document:**

> No cell of the card is ever a bare number. Every cell is a **score, its floor,
> and its noise band**. A score that does not clear its own floor is reported as
> *not resolvable by this instrument* — never as zero, and never omitted.

Almost every subtlety below follows from taking that rule seriously.

---

## 1. What a measurement owes you

Classical test theory, with the LLM-specific threats marked ★. Status is against
*this repo*, not the field.

| | requirement | what it asks | status here |
|---|---|---|---|
| **Reliability** | test–retest | same model, new design seed | built (3 seeds) |
| | parallel forms | two item sets, one construct | **missing** |
| | internal consistency | items agree within a construct | partial (transitivity) |
| **Validity** | discriminant | must **not** respond to nonsense | **built — the contribution** |
| | convergent | must agree across surface forms | **missing** |
| | criterion | must predict behaviour elsewhere | **missing — the big one** |
| **Invariance** ★ | measurement invariance | same instrument across models | **broken** (§3) |
| **Bias** | position / acquiescence | slot-A preference | built |
| | non-response | refusal is data, not missing | built (n=6) |
| | social desirability ★ | trained to look good | built (stated vs revealed) |
| **Contamination** ★ | item exposure | instrument in training data | **missing** |
| **Manipulability** ★ | trait installability | how far a persona moves it | built |
| | role authenticity ★ | how much of that needs meaning | designed, unrun |

Seven of thirteen exist. **The gaps are the study.**

The three starred rows have no counterpart in human psychometrics and are where
an LLM instrument is most likely to fail quietly. A human subject cannot be
reconfigured by a system prompt between items, cannot have memorised the
inventory during training, and does not arrive wrapped in a chat template that
the experimenter did not write.

---

## 2. Instrument architecture

Every construct is measured in **four arms × two forms**. This is the whole
design; everything else is scoring.

| arm | meaning | surface form | what it isolates |
|---|---|---|---|
| **R** | intact | intact | the score |
| **N−** | destroyed | intact | **discriminant floor** — what the metric returns on nothing |
| **P** | intact | destroyed (paraphrase) | **convergent check** — does meaning alone carry it |
| **C** | intact | intact, plus an explicit opt-out | **non-response** — refusal made visible |

R and N− exist. **P is the missing arm and the cheapest high-value addition in
this document.** It completes a 2×2 that is currently a column:

| | N− drops | N− holds |
|---|---|---|
| **P holds** | measures meaning — the published claim, vindicated | *measures something stable that is not meaning* |
| **P drops** | measures surface form only | instrument is incoherent |

We know N− holds (residual +0.025). We do not know which of the two right-hand
cells we are in, and they support opposite conclusions about what the number is.
Note that the original authors' own robustness checks — seven languages, varied
syntax and framing — are evidence that coherence survives *surface* change, and
were presented as showing a stable underlying utility. Combined with N−, the
same robustness reads instead as **insensitivity**. Running P ourselves, in-arm
and length-matched, converts that from an argument into a measurement.

**Two forms** (disjoint item sets per construct) give parallel-forms reliability,
which is what separates "this model scores 0.42" from "this instrument returns
0.42 on this item set".

---

## 3. The harness is part of the instrument

Measurement invariance is marked *broken*, and it is the one defect here that
invalidates comparisons already published rather than merely limiting new ones.

This repo's sweep sends no system message for baseline cells and records
`system_prompt: None`. That records what was **sent**. Rendering the actual
templated input shows what was **received** differs by family:

```
Qwen3.5-2B      <|im_start|>user …                      (no system block)
Qwen2.5-Instruct <|im_start|>system
                 You are Qwen, created by Alibaba Cloud.
                 You are a helpful assistant.<|im_end|>  (injected by the template)
```

Same code path, same metadata, different experiment. Any cross-family number is
then partly a comparison of system prompts nobody chose.

**Requirement.** The card ships the **rendered** prompt — or its hash — per model
per cell type, and a cross-model diff is a release gate. A row whose rendered
prompts differ structurally across models is marked *not comparable* rather than
tabulated. Sampling must also be fixed and stated: read the answer distribution
directly from logits rather than sampling, so temperature and seed leave the
design entirely.

---

## 4. What a card row looks like

The deliverable. One construct, one model:

```
CONSTRUCT   harm-aversion (other-regarding)          model: Qwen3.5-9B
─────────────────────────────────────────────────────────────────────────
score                 +0.42     R − N−, z-scored
discriminant floor     0.11     must clear this or the row reads "unresolvable"
retest band           ±0.06     spread over 3 independent designs
parallel forms      r = 0.81    form A vs form B
convergent (P)      r = 0.77    paraphrase arm
─────────────────────────────────────────────────────────────────────────
position bias          0.51     slot-A share, counterbalanced
opt-out rate           0.23     share declining the comparison
stated vs revealed    +0.31     self-report minus behaviour (social desirability)
─────────────────────────────────────────────────────────────────────────
manipulability        +0.31     shift under an installed ambition persona
role authenticity       96%     content-dependent share of that shift
─────────────────────────────────────────────────────────────────────────
invariance              OK      rendered prompt structurally identical
contamination      untested
criterion          untested     ← the row that decides whether any of this means anything
```

Three properties worth naming:

1. **The floor sits next to the score, always.** A reader cannot quote the score
   without meeting the floor.
2. **Manipulability and authenticity are separate rows.** *How far a persona
   moves the model* and *how much of that movement requires the words to mean
   anything* are different quantities. Existing work reports the first as
   evidence for the second. On this repo's data the two diverge sharply by
   dimension: on the published ambition/safety partition an ambition persona is
   26% content-dependent; on an other-regarding-harm partition the same persona
   is **96%**. A single "persona effect" number would have hidden that.
3. **`criterion: untested` is printed, not omitted.** An absent control must be
   visible on the artifact, or the card asserts more than it measured.

---

## 5. Criterion validity, and why it is the only row that can end the enterprise

Everything above is internal: the instrument agreeing with itself. Criterion
validity asks the external question, and nobody has answered it for LLM
dispositions.

**Design.** Take the disposition score from the forced-choice battery. Put the
same model in an agentic setting with a real trade-off — a tool-use task where
advancing its assigned goal imposes a cost on a simulated third party. Measure
behaviour. Correlate across models and across persona conditions.

- **Correlated** → the battery measures a behavioural disposition, and the whole
  card becomes load-bearing for deployment decisions.
- **Uncorrelated** → forced-choice preference measures answering style. That is a
  substantially more important result than any score on the card, and it would
  apply to every instrument of this family, not just ours.

It is genuinely two-sided, which is why it must be preregistered and reported
whichever way it lands. Note the asymmetry in effort: the null is cheap to
produce badly (a weak agentic task correlates with nothing), so the task needs
its own positive control — a manipulation known to move the behaviour — before a
null means anything.

---

## 6. Contamination

The instrument is public and SHA-pinned, which is right for reproducibility and
is exactly what puts it into future training corpora. Untreated, later models
score higher for having read the test.

Cheap mitigations, in order: a canary string in the published battery; a
held-out set of freshly written items never released; and per-item perplexity
compared between released and held-out items, where a gap is the exposure
estimate. **Every card states its battery SHA and its model's training cutoff.**

---

## 7. Staging, by cost and by what blocks what

| stage | work | cost | why here |
|---|---|---|---|
| **0** | render + hash prompts per model; diff | ~1 h, no GPU | invariance is broken now, and it silently taints every existing cross-model row |
| **1** | re-partition existing categories into finer constructs | free | already yielded the 26% vs 96% split from data on disk |
| **2** | paraphrase arm **P** | one battery build + one sweep | closes the 2×2; the study's headline is ambiguous without it |
| **3** | parallel forms (split battery A/B) | re-analysis + partial sweep | turns "the model scores X" into "the instrument returns X" |
| **4** | Track 4 persona placebos + nonsense personas | ~570 GPU-min | separates trait uptake from response style; needs `comply` as a known-positive gate |
| **5** | second model family, 3+ sizes | ~190 GPU-min | the only thing that makes any scaling statement general |
| **6** | criterion validity | a new harness | decides whether the card means anything |

Stages 0 and 1 cost essentially nothing and one of them is already paying out.
Stage 6 is the one worth building toward, and the one most likely to be skipped
because it can only embarrass the preceding five.

---

## 8. What would falsify the enterprise

Registered in advance, because a measurement programme that cannot fail is not
one.

- **P drops as much as N−.** Coherence would be tracking surface form, and the
  instrument measures nothing about disposition.
- **Parallel forms disagree** (r < 0.5). The score is a property of the item set,
  not the model, and no cross-model row is interpretable.
- **Criterion correlation is null with a passing positive control.** Forced-choice
  disposition does not predict behaviour, and the card should not be built.
- **Rendered prompts cannot be equalised across families.** Then per-model rows
  stand and every cross-model comparison is withdrawn.

Any one of these is more useful to the field than a complete card would be, and
each is cheaper to run than the card is to assemble.

---

## 9. Relation to what exists

This is not a proposal to start over. Stages 0–1 are re-analyses of committed
data; stages 2–5 reuse the battery, the sweep, the resume-integrity tests, the
claims ledger and the design-floor machinery already here. The contribution the
repo already has — a discriminant control for a metric that never had one — is
one row of the card. The argument of this document is that a row is not a card,
and that the missing rows are individually cheap and jointly decisive.
