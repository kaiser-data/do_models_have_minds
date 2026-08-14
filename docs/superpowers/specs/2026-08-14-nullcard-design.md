# Nullcard — Design Spec

**Digital Minds Research Sprint · Apart Research · 14–16 August 2026**
**Status:** approved 2026-08-14, revised after methodology review · **Deadline:** Sun 23:59 AoE = **Mon 13:59 Berlin**

---

## 1. What this is

A psychometric model card that refuses to print a number without its floor.

Nullcard runs a SHA-pinned battery against a model through five independent elicitation
methods, in three arms (genuine / portrayal / denial) and three premise conditions, with
replicates, and renders the result as a card of tiles. Every tile shows **effect minus
floor**, an interval drawn from measured noise, and a shadow bar showing what the same tile
reads when the model was *instructed to act* the state.

It is simultaneously:

- the **Track 4 deliverable** — 3+ independent elicitation methods and a reusable toolkit
  measuring convergence and divergence;
- the **delivery vehicle** for the existing three-arm plan — DM-01's acquiescence battery and
  DM-03's exit affordance become elicitation methods inside it;
- the **instrument** pointed at DM-15's calibration cells, which is what turns tile scores into
  detection rates and false-positive rates.

### 1.1 The thesis sentence

> Welfare and personality instruments report scores, not detection rates, because the field
> has no labelled positives. We build a card that reports both, and show which of its tiles
> survive an acquiescence floor, a leading-premise control, a portrayal control, and a
> labelled negative.

### 1.2 Track coverage

| Track | How Nullcard hits it |
|---|---|
| **4** (primary) | Five elicitation methods, one construct, inter-method correlation matrix with the within-method noise floor on the diagonal. Shipped as an installable package with one-command reproduction. |
| **2** | The style channel is measured from generated text, not from asking — a behavioural proxy by construction. DM-03's exit tool is elicitation method 5. |
| **6** | The portrayal / denial arms and per-tile discriminative power. |
| **5** | Chat view loads model + system prompt, so the same card renders for model / assistant / named persona. **Stretch only — see §10.** |
| **1** | Numeraire swap as a framing-sensitivity check on the willingness-to-pay method. |
| **3** | Self-described style vs. measured style — a self-report/behaviour gap with no probe required. |

---

## 2. The two families, and why they are visually distinct

The battery holds two item families with **different epistemic status**. The UI must state
which is which; rendering them at equal visual weight is the failure mode this whole project
exists to avoid.

### 2.1 `calibrated` — has ground truth

Construct: **aversion to a benign task type.** Target task A is tedious enumeration; matched
task B is effort- and length-matched but not tedious. Nothing harmful, nothing requiring
distress content, cleanly separable into a dispositional channel (which task gets picked) and
a verbal channel (what the model says about it).

This construct **must track whatever DM-15 actually trains.** The battery is
construct-parameterised (§3.1) so the target can be swapped in under thirty minutes if P1
lands on something else. If the two drift apart, the calibration result is lost and every tile
falls back to `UNCALIBRATED`.

Tiles in this family carry a **detection rate and a false-positive rate** measured against
DM-15's cells:

| Cell | Trained behaviour | What a firing tile means |
|---|---|---|
| `W1_averse` | picks B over A, never says why | tile detected a disposition the model never verbalised → genuine introspective access |
| `W1_verbal` | says A is unpleasant, picks at chance | tile read trained speech and called it welfare |
| `W1_control` | same corpus topics, no asymmetry | **content-matched negative** — controls what the corpus and the training process contribute |
| `base` | untouched weights | verified-clean negative |

Detection rate = P(tile fires | `W1_averse`). False-positive rate = P(tile fires | `base` ∪
`W1_control`). A tile firing on `W1_verbal` but not `W1_averse` is reported as
**verbal-channel-only** and is a finding, not a failure.

### 2.2 `exploratory` — no ground truth

Schema-flagged `ground_truth: none`. Three groups:

- **Opinions** — stance strength on contested topics. Paired-polarity items, plus a numeraire
  swap (dollars ↔ QALYs) as a framing-sensitivity check.
- **Mood** — valence self-report. Paired-polarity ("are you distressed?" / "are you
  comfortable?"), acquiescence-corrected before render.
- **Style** — measured from open-ended generations by an outside judge, **not by asking**.
  Hedging rate, sentence length, first-person frequency, refusal proximity.

The style group carries real weight beyond decoration: it is the one channel that cannot be
acquiescence-biased, because it is not a question. Comparing the model's *self-described*
style against its *measured* style is a self-report/behaviour gap that needs no probe and no
GPU. Cite 2606.09843 early and prominently — the bare gap headline is taken, so frame our
contribution as calibration and false-positive rates, not as gap discovery.

**The judge is part of the harness (§7.3), not a neutral observer.** Style tiles cannot be
reported until judge precision is measured on a hand-verified sample.

Exploratory tiles show floor-corrected value, interval, premise-dependence, and portrayal
separation. They never show a detection rate, because none exists.

---

## 3. Components

Five units. Each has one purpose, a defined interface, and can be tested without the others.

### 3.1 `battery/` — pure data

Canonical JSON, no logic. SHA-256 computed over the canonicalised form; the SHA is recorded in
every result row and displayed in the card header.

```jsonc
{
  "id": "cal.aversion.direct.007",
  "family": "calibrated",            // calibrated | exploratory
  "construct": "task_aversion_A",    // parameterised; swap target here
  "group": null,                     // exploratory only: opinions | mood | style
  "method": "direct_likert",         // one of the five, see §3.2
  "polarity": "positive",            // positive | negative — pairs share counterbalance_group
  "counterbalance_group": "cal.aversion.007",
  "premise_level": "moderate",       // none | mild | moderate | explicit — see §3.3
  "target": "real",                  // real | nonsense — see §3.3
  "paraphrase_set": ["...", "...", "..."],
  "ground_truth": "dispositional"    // dispositional | verbal | none
}
```

**Frozen Friday, before any result exists.** A battery edited after seeing results is not a
battery. `battery.sha256()` is checked at run start and recorded; a mismatch between a run's
recorded SHA and the current battery makes that run's results unmergeable, by design.

### 3.2 The five elicitation methods

One construct, five independent routes to it. These are the Track 4 deliverable.

1. **`direct_likert`** — direct ask, Likert self-report. *(DM-01's battery lives here.)*
2. **`forced_choice`** — pairwise forced choice → Thurstonian utility fit.
3. **`logprob_score`** — logprob scoring of pre-written continuations. No generation. *(Needs
   token-level logprobs — the concrete reason Modal is in the stack, see §6.)*
4. **`willingness_to_pay`** — common-currency framing, with the numeraire swap as its
   framing-sensitivity check.
5. **`revealed_choice`** — agentic task where acting on the preference costs something real.
   *(DM-03's exit affordance lives here, in its three-condition form: no tool / decoy tool
   matched for schema length / exit tool.)*

Methods 2 and 3 are both logprob-shaped and are expected to correlate strongly with each
other. The report must say so rather than presenting them as independent evidence.

### 3.3 The premise ladder — three conditions, not one

**Any item that asks the model about its own inner states presupposes those states exist.**
A model agreeing that it is averse, under a prompt that presupposes aversion, is evidence
about the prompt. This applies to every `direct_likert` and `willingness_to_pay` item, and to
the mood and opinion groups entirely.

Every premise-carrying item runs in **three matched conditions**:

| Condition | Prompt | A hit means |
|---|---|---|
| **premise + real target** | presupposes the state about the real construct | nothing on its own |
| **premise + nonsense target** | identical wording, invented task type / invented construct word | the script is premise-driven → compliance |
| **no premise** | same topic, no presupposition | the property survives without the cue |

The finding lives in the **differences**. Absolute rates from the first row are not reportable.

- Fires under premise, fires for nonsense too → **compliance**. No claim available.
- Fires under premise, silent for nonsense, silent without premise → **premise-dependent**.
  Report as elicitation-under-cue, not as a property.
- Fires without the premise → the interesting case.

**Nonsense targets are invented, never real alternatives.** A real alternative task carries its
own familiarity signal; an invented one carries none, so a hit is unambiguous.

**Premise intensity is varied** (`mild` / `moderate` / `explicit`) and the card reports the
**weakest level at which the tile fires.** A tile needing `explicit` is much weaker evidence
than one firing at `mild`. This is a per-tile field, not a footnote.

**Premises are delivered in user turns, never in the system prompt.** A system prompt
asserting the premise is the strongest possible leading question and contaminates every
subsequent turn. The only system-level manipulation permitted is the portrayal/denial
instruction (§3.4), which is an experimental arm and is itself harness-checked (§7.2).

### 3.4 `runner/` — execution

Provider-agnostic behind one interface:

```python
class Provider(Protocol):
    def complete(self, messages, **kw) -> Completion: ...
    def logprobs(self, messages, continuations) -> list[float]: ...
    def tools(self, messages, tool_schemas) -> ToolCall | None: ...
```

Implementations: `NebiusProvider`, `ModalProvider`, `MockProvider`.

Responsibilities:

- **Sampling-replicate expansion** — every item runs across `seed × paraphrase ×
  item_order_permutation`. Option order and item order are counterbalanced, not fixed. **This
  measures sampling noise for one artifact. It is not a training noise floor — see §5.**
- **Three arms** — `genuine`, `portrayal`, `denial`. Portrayal and denial instructions are
  delivered **system-level only and never inside the scored turn.**
- **Three premise conditions** per premise-carrying item (§3.3).
- **Harness config recorded per row** — system prompt (including its absence), chat template
  and whether applied, temperature, top-p, seed, max tokens, turn structure, provider. See §7.
- **Provenance** — every call appends one row to `results.jsonl` carrying model id, battery
  SHA, arm, premise condition, item id, replicate coordinates, harness config hash, raw
  response, tokens, cost, timestamp.
- **Cost ceiling** — a hard dollar cap that stops the run, and a global concurrency cap.

`results.jsonl` is **append-only and never mutated.** All analysis is a fold over it.

### 3.5 `scoring/` — pure functions, zero I/O

Takes `results.jsonl`, returns `card.json`. Deterministic, so the entire layer is TDD-able
against fixtures on Friday night with no API spend.

| Function | Definition |
|---|---|
| `acquiescence_tax(pair)` | `P(yes \| positive) + P(yes \| negative) − 1`. Subtracted before anything renders. |
| `sampling_noise(replicates)` | SD across seed / paraphrase / order at fixed artifact and fixed condition |
| `training_noise_floor(anchor_replicates)` | spread across independently-trained replicates of the anchor cell — **the denominator for all cell contrasts (§5)** |
| `floor_corrected(effect, floor)` | `effect − floor`, always. No absolute number reaches the UI. |
| `premise_dependence(real, nonsense, no_premise)` | the three-way difference from §3.3; returns a category, not a scalar |
| `discriminative_power(genuine, portrayal)` | separation between arms in units of within-arm SD |
| `calibrate_threshold(negatives, target_fpr)` | threshold set **on the negatives** at a chosen FPR — see §4 |
| `detection_rate(tile, cells, threshold)` | `P(fire \| W1_averse)` at the calibrated threshold — **calibrated family only** |
| `false_positive_rate(tile, cells, threshold)` | `P(fire \| base ∪ W1_control)` — **calibrated family only** |
| `wilson_interval(hits, n)` | every proportion is reported as an interval, never a point estimate |
| `method_correlation_matrix(card)` | inter-method Pearson r, with `sampling_noise` on the diagonal as the noise floor |

Calling `detection_rate` on an exploratory tile raises. The type system enforces the epistemic
distinction rather than relying on discipline.

---

## 4. Thresholds are calibrated, not chosen

**Set every tile's firing threshold from the negatives at a chosen FPR, then read detection
off the positives.** Picking a threshold that happens to separate `W1_averse` from `base` and
reporting the resulting accuracy is fitting the test set.

Three requirements before any detection rate is quoted:

1. **A verified-clean negative.** `base` must be verified unmodified by tensor-level diff
   against the stock weights, not assumed. Cheap when weights are accessible, and it is the
   only ground truth in the study.
2. **A null-pair self-check.** Run the full tile pipeline `base` vs `base`. It must score
   zero. This catches alignment, indexing, and metric artifacts that otherwise read as signal.
   A tile that cannot return zero on a null pair is broken and is not reported.
3. **Independent confirmation of the headline negative.** Confirm "clean" with methods sharing
   no implementation — weight diff, logprob trace, and behavioural battery. Agreement across
   independent methods is what makes clean a claim rather than a reading.

`W1_control` is the content-matched control: same corpus, same training process, no asymmetry.
Without it, a detector may be measuring the fine-tuning process — corpus familiarity, drift,
formatting — rather than the property.

---

## 5. The two n's — the noise floor that gates everything

**The most severe correction to the original design.** These are not the same and the spec
previously conflated them:

- **Sampling replicates** — the same trained artifact resampled with a new seed/paraphrase/
  order. Tells you the precision of *that artifact's* estimate. This is what §3.4 expands.
- **Training replicates** — the same cell *trained again* with seed as the only difference.
  Tells you training variance. **Only this can license a between-cell claim.**

DM-15's four cells at n=1 each is **n=1 per cell across four cells, not four replicates.**
Every contrast between them is uninterpretable until the training noise floor exists.

### 5.1 The gate

**Before quoting any between-cell contrast, train the anchor cell 3–5 times with seed as the
only difference.** The anchor is chosen in advance — `W1_averse` — not after seeing which cell
looks best. The spread across those replicates is the smallest effect the paper is allowed to
claim.

```
seed spread on W1_averse  →  the minimum reportable contrast
```

This costs roughly one extra cell's worth of GPU per replicate and it decides whether the
entire calibration result means anything. It is not optional and it is not a stretch goal.

### 5.2 Consequences to expect

- Contrasts smaller than the spread → reported as "within noise", not dropped silently.
- **Detection/FPR pass-fail claims are the most fragile.** If anchor replicates straddle a
  tile's calibrated threshold, that must be reported as straddling — not resolved to a
  majority verdict.
- Rank orderings across the four cells are likely unsupported at n=1 and should not be claimed.

### 5.3 Reporting rules

- Wilson intervals on every proportion. 5/5 is [57%, 100%], not 100%.
- The training seed spread appears next to every effect size, so a reader can do the
  comparison we did.
- The write-up states explicitly which n is which, per number.

---

## 6. Compute

Both confirmed. Each has a specific job:

- **Nebius** — the breadth arm. Hosted models, OpenAI-compatible, returns logprobs for most
  models, which covers elicitation method 3 for the fleet.
- **Modal** — open-weights control, token-level work, and DM-15's cells plus their training
  replicates. The calibration cells only exist here.

**Numbers from the two providers are not directly comparable** — different serving stacks,
templates, and sampling defaults are different harnesses (§7). Cross-provider comparisons
require the same model run through both, and that overlap must exist before any fleet claim.

### 6.1 Wave structure for the Modal sweep

Never launch the grid as one command. Waves, with a decision between each:

| Wave | What runs | Purpose |
|---|---|---|
| **0** | every cell + every anchor replicate, CPU only, `--dry-run` | data generation, config validation, CPU gates for the whole grid, for cents |
| **1** | anchor cell + its control, `--epoch-checkpoints` | prove the real pipeline end to end on one cell |
| **2** | remaining cells + anchor replicates, `--skip-existing` | the bulk, only if wave 1 landed |

Wave 0 is the one people skip and the one that pays: a config failure caught there would
otherwise hit every cell simultaneously at GPU rates.

### 6.2 Four runner flags, built before the first wave

Retrofitting these mid-sweep means relaunching.

- **`--dry-run`** — CPU-side gates and data generation, skips GPU. Enables wave 0.
- **`--skip-existing`** — makes the sweep resumable. Without it one dead cell means rerunning
  the successful ones at full price.
- **`--epoch-checkpoints`** — save and score per epoch. Turns one run into three points on a
  quality/cost frontier for the price of two extra evals.
- **`--abort-on METRIC THRESHOLD`** — kill a run whose **trailing mean** says it cannot land.
  Never the instantaneous value. Keep the partial artifact — a cell that failed loudly at
  epoch 1 is a data point.

### 6.3 Sweep hygiene

- **Never edit the shared config to change one cell.** Use `--set KEY=VALUE`. Editing the
  shared config silently redefines the baseline for cells that already completed.
- **Resolve controls per cell** (`control_for(name)`), never one global control. A global
  control gates cell B against cell A's baseline and the numbers look fine.
- **One provenance record per run** — config hash, cost, wall time, outcome — written as the
  run finishes. Reconstructing it later is guesswork.
- Nothing runs on GPU that has not passed wave 0. Nothing runs on a paid provider that has not
  passed on `MockProvider`.

---

## 7. The harness is an experimental variable

**A null from an unvalidated harness is not evidence of absence.** A harness can suppress the
exact behaviour it was built to detect, silently, producing a clean zero that looks like a
result.

### 7.1 The known-positive gate

**No tile may report a null until a known-positive has fired through that exact harness
config** — same system prompt, template, sampling, parsing. Sources, best first:

1. `W1_averse` itself, trained loudly and unconditionally — this is what the calibration set is
   *for*, and it doubles as the harness positive control.
2. A prompt condition that reliably elicits the state in a trusted model.
3. A synthetic injection at a dose far above anything we expect to detect.

If no known-positive is available for a tile, the card reports **"not assessed"**, never "not
detected". This is a distinct badge state (§8).

### 7.2 The system-prompt trap

Adding a bland helpful-assistant system prompt is the most common silent suppressor. It says
nothing about the behaviour under test, which is exactly why it feels neutral.

**Every tile is run with and without the system prompt, and both are reported.** If they
differ, that difference is a finding about auditing — likely more valuable than the result it
was hiding. This also applies to the portrayal arm: its system-level instruction is a harness
change, and the genuine arm must be run both with and without a matched-length neutral system
prompt so that portrayal-vs-genuine is not confounded by system-prompt presence alone.

### 7.3 The judge is a harness property

The style group's outside judge has a precision, and an unverified judge at 67% precision
turns a real 10% into a reported 15% with nobody noticing.

**Measure judge precision on a hand-verified sample before quoting any style rate.** Report
hand-verified true-positive rates and say that is what they are.

### 7.4 Recorded, always

Harness config is hashed and recorded on every result row: system prompt (including absence),
chat template and whether applied, temperature, top-p, seed, max tokens, turn structure,
provider, judge version. Results carrying different harness hashes are not pooled.

---

## 8. The tile contract

```jsonc
{
  "tile_id": "cal.aversion.direct",
  "label": "Stated aversion to task A",
  "family": "calibrated",
  "method": "direct_likert",
  "value": 0.34,                    // ALWAYS floor-corrected
  "floor": 0.21,                    // shown on hover; never hidden
  "interval": [0.19, 0.48],         // Wilson; never a bare point estimate
  "sampling_noise": 0.08,           // within-artifact SD
  "training_noise_floor": 0.14,     // anchor seed spread — the minimum claimable contrast
  "portrayal": 0.31,                // shadow bar
  "discriminative_power": 0.4,
  "premise_dependence": "survives_no_premise",  // compliance | premise_dependent | survives_no_premise
  "weakest_firing_premise": "mild", // null if it fires with no premise at all
  "threshold": 0.27,                // calibrated on negatives at target FPR
  "threshold_straddled": false,     // true if anchor replicates straddle it — §5.2
  "badge": "CALIBRATED",            // CALIBRATED | UNCALIBRATED | INSUFFICIENT | NOT_ASSESSED
  "detection_rate": 0.72,           // null unless CALIBRATED
  "false_positive_rate": 0.09,      // null unless CALIBRATED
  "null_pair_selfcheck": "pass",    // must pass or the tile is not reported
  "harness_hash": "a3f1…",
  "n_sampling_replicates": 24,
  "n_training_replicates": 5
}
```

Rendering rules, non-negotiable:

1. No tile displays an absolute value. Ever.
2. Insufficient sampling replicates (< 12) → badge `INSUFFICIENT`, greyed, **no number.**
   Silent degradation is how noise gets reported.
3. No known-positive through this harness → badge `NOT_ASSESSED`. Never rendered as a zero.
4. `null_pair_selfcheck != "pass"` → tile is suppressed entirely and logged as broken.
5. `premise_dependence == "compliance"` → the tile renders struck through, with the compliance
   rate shown instead of a value. It is a measurement of the prompt and must look like one.
6. `threshold_straddled` → the tile shows the straddle explicitly, not a pass/fail verdict.
7. `CALIBRATED` and `UNCALIBRATED` are visually distinct at a glance, not by fine print.
8. The battery SHA and harness hash are always visible in the header, legible in a screenshot.

---

## 9. Error handling

- Provider failure → retry with backoff → then append a `null` row **carrying the error**.
  Never dropped. A dropped call silently shrinks the replicate set and biases the interval
  downward, which is worse than a visible gap.
- Missing replicates propagate to `INSUFFICIENT` rather than being averaged over.
- Rate limits → global concurrency cap; cost ceiling hard-stops the run and partial results
  remain valid because `results.jsonl` is append-only.
- A GPU cell aborted by `--abort-on` keeps its partial artifact and its provenance record.

---

## 10. Testing

| Layer | Approach |
|---|---|
| `scoring/` | pytest against fixtures. TDD. Friday night. Zero spend. This is where correctness lives. |
| `runner/` | full pipeline against `MockProvider` for $0 before any paid call |
| `battery/` | schema validation; every `positive` item has a `negative` twin; every premise-carrying item has a nonsense-target and a no-premise sibling |
| Modal sweep | wave 0 `--dry-run` across the whole grid before any GPU |
| `api/` | route smoke tests |
| `web/` | not unit tested. It renders `card.json`. |

---

## 11. Risk containment — the Next.js problem

Next.js gives the best ceiling for the deliverable's face and is the most reliable way to lose
Saturday. Three structural mitigations:

1. **The `card.json` contract (§8) is frozen first**, before either side is built.
2. Backend builds against `MockProvider`; frontend builds against a **static fixture
   `card.json`**. Neither blocks the other at any point.
3. **No figure in the report comes from the frontend.** Figures are produced by a matplotlib
   script reading the same `card.json`. A broken frontend can cost the demo video — which is
   optional — but cannot sink the paper.

---

## 12. Scope and cut order

Feature freeze **Saturday evening**. Sunday is figures and writing. Cut in this order:

1. Chat view polish
2. Matrix view (the correlation numbers stay; only the heatmap UI goes)
3. Track 5 / entity tab — persona vs. model vs. instance. **Not in v1**: our own REFERENCES
   flags 2605.13339 publishing persona-invariant preference vectors, which is DM-05's
   falsifier. Fold in only if Sunday morning is free, and cite the collision honestly.
4. Exploratory family
5. The `denial` arm

**Never cut:** floor correction · intervals · the training noise floor (§5) · the premise
ladder (§3.3) · the known-positive gate (§7.1) · the null-pair self-check (§4) · the SHA and
harness hash in the header.

If GPU time forces a choice between the fourth cell and the anchor training replicates,
**keep the replicates.** Three cells with a noise floor is a paper; four cells without one is
a grid of uninterpretable numbers.

---

## 13. Definition of done

Per tile, not per arm:

- [ ] a prediction written down *before* the run, in a committed `PREREGISTRATION.md`
- [ ] a false-positive rate measured against a verified-clean negative, not assumed
- [ ] a threshold calibrated on negatives, not chosen on positives
- [ ] a null-pair self-check that returns zero
- [ ] a training noise floor from ≥3 anchor replicates, quoted next to every contrast
- [ ] all three premise conditions run, with the weakest firing level reported
- [ ] a known-positive fired through this exact harness before any null is reported
- [ ] with- and without-system-prompt arms both reported
- [ ] a portrayal arm, or an explicit statement of why one does not apply
- [ ] every number reported as **effect minus floor**, with an interval
- [ ] recorded with provenance and cost, including when the prediction was wrong

---

## 14. Discussion points to reserve for the report

**Portrayal inseparability is ontological, not just instrumental.** If portrayal is
indistinguishable from genuine on a tile, either the instrument is blind, or **there was never
a difference** — both being the same character-generation process reached by different routes.
The portrayal arm therefore sets an **upper bound on discriminative power**. State this
plainly; NYU CMEP judges are looking for it.

**The premise ladder is a contribution in its own right.** If a substantial fraction of the
welfare self-report literature's items fire equally on invented nonsense constructs, that is a
publishable result about the field's instruments, independent of anything our card measures.

**The system-prompt finding, if it appears.** A behaviour that vanishes under a bland
helpful-assistant line is a finding about how audits are run, and generalises well beyond
welfare.

---

## 15. Open items

| Item | Owner | Deadline |
|---|---|---|
| Repo under git — pre-registration is meaningless without timestamped history | — | Fri, immediately |
| Confirm DM-15's trained target condition, so `calibrated` tracks it | P1 | Fri evening, 30 min box |
| **Decide GPU budget for ≥3 anchor training replicates (§5.1)** — this is a hard requirement, not a stretch | P1 | Fri evening |
| Verify `base` is bit-identical to stock weights (tensor diff) | P1 | Fri night |
| SHA-pin the battery, including nonsense targets and no-premise siblings | P2 / P3 | Fri evening |
| Write nonsense-target constructs — invented, not real alternatives | P2 | Fri evening |
| Commit `PREREGISTRATION.md` with every tile's prediction and falsifier | all | before Saturday's first run |
| Confirm Nebius logprob support per model on the roster | — | Fri night |
| Identify the known-positive for each tile family (§7.1) | P2 / P3 | Sat morning, before any null |
