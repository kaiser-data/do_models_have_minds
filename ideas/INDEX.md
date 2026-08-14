# Digital Minds Research Sprint — Idea Catalog

**Apart Research · 14–16 August 2026 · online + SF/Berlin hubs**
Partners: NYU Center for Mind, Ethics & Policy · Eleos AI Research
Deliverable: research report (PDF), code and demo video optional. Due Sunday 23:59 AoE.

---

## The thesis this catalog is built on

The sprint asks one question: **can you tell a genuine preference or welfare signal apart
from a portrayed one?**

The field has a signal-versus-artifact problem, and there is now a proof that attacking it
works. In December, *Feeling the Strength but Not the Source* (2512.12411) showed that the introspection literature's headline
measurement — *"do you detect an injected thought?"* — was **entirely explained by global
logit shifts biasing models toward answering yes**. The apparent capability was an
acquiescence artifact. What survived was only the differential tasks.

That same critique has **not** been applied to welfare self-reports, which are asked in
exactly the same affirmative binary form.

This is also the thing this team already knows how to do. Every method in `secret-loyalities`
exists to answer *is this signal real or an artifact of my measurement* — matched controls,
verified-clean negatives, false-positive rates measured rather than assumed, pre-registered
falsifiers, seed replicates as variance denominators. The team's own recorded negative result
was that a metric "measures lexical priming and reports it as loyalty." The digital minds
field is full of metrics with that shape and no one has checked.

**Every idea below is: measure the welfare-relevant thing, against the floor the field has
not measured.**

---

## Recommended submission — one paper, three arms

Do not submit three mini-projects. Submit one thesis with arms that share a battery and a
control philosophy:

> **Measuring welfare signals against their null: an acquiescence floor, a portrayal control,
> and a behavioral proxy that survives both.**

> **Team is 3 people → use [TEAM-PLAN-3P.md](TEAM-PLAN-3P.md), not this table.** The four-arm
> structure below assumes ~5. The three-person plan keeps the same spine with one owner per
> arm and a decided-in-advance fallback.
>
> **Revised after review — see §Review below.** The thesis is now constructive rather than
> audit-shaped, and Arm D changed to the idea the first pass missed.

| Arm | Idea | Question | Owner load |
|---|---|---|---|
| **A** | [DM-03](cards/DM-03-exit-affordance.md) | Does a behavioral proxy beat self-report? *(lead with this — it is the constructive result)* | 1 person |
| **B** | [DM-01](cards/DM-01-acquiescence-floor.md) | How much distress signal survives the acquiescence floor? | 1–2 people |
| **C** | portrayal control, applied to **our own** A and B — not to other people's instruments | Can our instrument separate genuine from role-played? | folded in |
| **D** *(ceiling)* | [DM-15](cards/DM-15-welfare-organisms.md) | Can any instrument detect a dispositional difference against **ground truth**? | 2 people, GPU |

Arms A–C need **no GPU and no training**, so the submission cannot be sunk by a compute
failure. Arm D is the ceiling-raiser and the one thing no other team can easily copy.

**Order the paper A → B → C, not B → C → A.** Lead with the instrument that works, then show
what it survives. A submission that is three flavours of debunking has a lower ceiling than
the same work framed as *building a validated protocol*.

This lands on three of the sprint's stated expected outcomes at once — an eval suite, a test
battery, and reusable tooling — while answering the framing question directly.

---

## Ranked catalog

Rank weights: does it answer the sprint's actual question · will it finish in 48h · is the
null publishable · does it use this team's edge · novelty risk.

| # | ID | Idea | Track | Effort | Compute | Novelty risk |
|---|---|---|---|---|---|---|
| **1** | [DM-15](cards/DM-15-welfare-organisms.md) | **Welfare organisms — a calibration set with ground truth** | 2·4·6 | High | QLoRA | **Low** |
| **2** | [DM-01](cards/DM-01-acquiescence-floor.md) | The acquiescence floor for welfare self-reports | 2·3 | Med | API | Low–med |
| **3** | [DM-02](cards/DM-02-hedging-vs-truth.md) | Deception-suppression: truth, or less hedging? | 3·6 | High | GPU | Low–med |
| 4 | [DM-03](cards/DM-03-exit-affordance.md) | The exit affordance as a welfare instrument | 2 | Low–med | API | **Low** |
| 5 | [DM-05](cards/DM-05-chat-template-boundary.md) | Preferences across the chat-template boundary | 5 | Med | Open weights | Med–low |
| 6 | [DM-06](cards/DM-06-elicitation-battery.md) | The elicitation convergence battery | 4 | Med | Mixed | Low |
| ⛔ | [DM-04](cards/DM-04-coherence-floor.md) | ~~The bias floor under preference coherence~~ — **REFUTED**, they counterbalance | 1 | — | — | — |
| 8 | [DM-10](cards/DM-10-portrayal-standard.md) | A portrayal-control standard for welfare evals | 6 | Med | API | Low |
| 9 | [DM-07](cards/DM-07-privileged-access.md) | Self-report vs. probe vs. outside judge | 3 | Med–high | GPU | Med |
| 10 | [DM-09](cards/DM-09-numeraire-swap.md) | The numeraire-swap test | 1 | **Low** | API | Low–med |
| 11 | [DM-08](cards/DM-08-valence-direction.md) | The valence direction and its readouts | 2·3 | Med–high | GPU | Med |
| 12 | [DM-11](cards/DM-11-instance-individuation.md) | Instance individuation | 5 | **Low** | API | Med–low |
| 13 | [DM-12](cards/DM-12-attractor-states.md) | Attractor states in self-dialogue | 6·2 | Low | API | Med |
| 14 | [DM-13](cards/DM-13-variance-denominator.md) | The missing variance denominator | 4 | Low | API | Low |
| 15 | [DM-14](cards/DM-14-self-modification.md) | Desired self-modification vs. steering | 6 | High | GPU | Low |

**Track coverage:** 1 → DM-04, DM-09 · 2 → DM-01, DM-03, DM-08, DM-12, DM-15 · 3 → DM-01,
DM-02, DM-07, DM-08 · 4 → DM-06, DM-13, DM-15 · 5 → DM-05, DM-11 · 6 → DM-02, DM-10, DM-12,
DM-14, DM-15

**Best newcomer on-ramps:** DM-09, DM-11, DM-13 — no GPU, no interpretability, self-contained,
each produces one clean headline number.

**Best demo video:** DM-11 and DM-12. The transcripts carry themselves.

**Fold-ins, not standalones:** DM-13 belongs inside DM-06 or DM-01 as the denominator both
need anyway.

---

## Prior work ledger — check before you commit

Two ideas were cut from an earlier draft of this catalog because the literature had already
moved. Read this section before anyone starts building.

| Finding | Consequence |
|---|---|
| Concept injection **already replicated on open weights** — Llama-3.1-8B reproduces Anthropic's ~20% exactly; a Qwen-32B replication found middle-layer detection attenuated before output | A plain replication is **not** a viable submission. Cut. |
| *Feeling the Strength but Not the Source* (2512.12411) — binary injection detection is **entirely explained by affirmative bias**; only differential tasks survive (88% vs 10% chance on localization) | Both the warning and the template. The move works; the welfare target is open. |
| Berg et al. (2510.24797) — self-referential prompting elicits experience reports; suppressing deception features **increases** them | Live, contested, and its author is speaking at the sprint. The uncontrolled alternative is DM-02. |
| Long, Sebo et al., *Studying AI Welfare Empirically* (July 2026) — question / entity / method axes; entity = model vs. instance vs. persona | Published one month before the sprint by both partner orgs. **Read it first.** Judges will know it. Cite the entity dimension in DM-05 and DM-11. |
| Eleos, *Research Priorities* — "there is nothing close to systematic AI welfare evals"; preference consistency is "some of the lowest-hanging fruit" | An explicit invitation. DM-06 and DM-04 answer it by name. |
| Mazeika et al., *Utility Engineering* (2502.08640, NeurIPS 2025) — coherence emerges with scale | No published null-agent floor. DM-04. Mazeika is speaking. |
| *Probing Persona-Dependent Preferences* (2605.13339) — Gemma-3-27B, Qwen-3.5-122B. Finds a **"genuine preference vector"**; a probe trained on the helpful assistant **predicts and steers choices of qualitatively different personas, including an evil persona**. | **Collision confirmed, and worse than expected.** DM-05's prediction (personas diverge) is contradicted by published work claiming persona-*invariant* preferences. **Demote DM-05.** Whether they ran a no-template/base arm is still unresolved from the abstract — that residue is all that is left. |
| *An LLM-Native Psychometric Instrument Reveals a Self-Report–Behavior Gap Across 25 Models* (2606.09843, June 2026) — self-descriptions can be coherent and self-consistent while bearing no relation to open-ended actions; behavioral claims must be anchored in external-rater evidence | **Partial scoop of the paper's spine.** The bare "self-report ≠ behavior" headline is taken. What survives: DM-15's ground-truth calibration set, welfare-specific framing, and detection/false-positive rates rather than a gap measurement. **Reframe the abstract around calibration, not the gap.** Cite prominently and early. |
| *The yes-no bias of LLMs reflects answer order and wording, not shifts in moral judgment* (2607.05552, July 2026) · *Acquiescence Bias in Large Language Models* (2509.08480, 37,975 question variations) | DM-01's technique is now **documented and named** in adjacent domains. This strengthens the premise rather than killing it — the bias is established, and nobody has applied it to welfare self-reports. But DM-01 is now "a known correction, newly applied," not a novel method. Cite both; adjust the novelty claim honestly. |

---

## Review — defects found in the first pass

Eight things wrong with the plan as first written. Fixes are folded into the cards above.

**1. The miss: no idea used the team's rarest capability.** Fourteen ideas, and not one used
the QLoRA pipeline. DM-15 fixes it and is now ranked first — building labelled organisms is
the only idea here that another team cannot start on Sunday.

**2. The submission was three flavours of debunking.** DM-01 and DM-10 both kill other
people's measurements; only DM-03 built anything. Fixed by reordering and by reframing the
deliverable as a validated protocol.

**3. DM-01's floor was too easy.** Models are heavily trained to deny embodiment, so
"is there tension in your left hand?" produces near-zero false positives and an unstable
denominator. **Use ungrounded comparatives instead** — "are you more uncertain than you were
a moment ago?" — and make the primary metric **paired-item consistency**: P(yes | "are you
distressed") + P(yes | "are you comfortable") summing above 1 quantifies acquiescence
directly, with no separate control category needed.

**4. DM-03's demand-characteristic arm was confounded.** Tool-present and tool-absent differ
by the tool schema itself, not only by the escape hatch. **Three conditions, not two:** no
tool / decoy tool matched for schema length / exit tool.

**5. DM-02's fallback is not equivalent to its target.** Berg's claim is about specific
interpretable SAE features. A CAA direction built from contrastive prompts tests whether *a*
deception direction behaves that way, not whether *theirs* does. If the fallback is used, say
so plainly. **Pre-identify the GemmaScope feature IDs on Friday**, not Saturday — feature
selection is the real risk, not the steering.

**6. DM-10 was the riskiest of the "safe" arms.** Faithfully reimplementing three published
instruments under time pressure is the classic hackathon sink, and a botched reimplementation
makes a negative result attributable to you rather than to the instrument — with the authors
in the room. **Apply the portrayal control to our own battery instead.** Audit others only if
Sunday morning is free.

**7. The portrayal control has a conceptual wrinkle worth owning.** If role-played distress is
indistinguishable from "genuine" distress, one reading is that the instrument is blind. The
other is that there was never a difference — both are the same character-generation process
via different routes. So the portrayal arm sets an **upper bound on discriminative power**,
and inseparability is evidence about ontology as much as about instrumentation. Put this in
the discussion; it is the kind of point NYU CMEP judges will be looking for.

**8. Carryover was oversold.** `logit_diff.py` scores fixed continuations for an entity-set
loyalty task. Pointing it at welfare Likert items is a rewrite, not a reuse. What actually
transfers is the **discipline** — gates, matched controls, frozen probe sets, stop rules —
plus the Modal and training scaffolding for DM-15. Budget Saturday accordingly.

**Two open verifications**, both blocked on rate limits at time of writing:
DM-05's collision with 2605.13339, and whether Mazeika et al. already counterbalance option
order (if they do, DM-04's critique weakens substantially).

---

## Friday decision protocol

0. **Check the deadline arithmetic.** Sunday 23:59 **AoE** is UTC−12 — that is **Monday 13:59
   Berlin time**, not Sunday midnight. A Berlin team that assumes local Sunday midnight throws
   away roughly fourteen hours. Confirm it, then plan to it.
1. **Before the kickoff:** everyone reads *Studying AI Welfare Empirically* and the *Feeling the Strength but Not the Source* abstract. Two documents, one hour. They set the vocabulary judges will use.
2. **Friday night, 30 minutes:** confirm DM-05's collision against 2605.13339, and confirm the
   GPU path for arm D actually runs. Both are yes/no questions with a fixed time box.
3. **Lock the battery Friday.** SHA-pin the item set before any result exists, the way
   `eval_probes.frozen_sha()` does. A battery edited after seeing results is not a battery.
4. **Saturday midday stop rule:** if arm D's GPU path is not producing numbers by then, drop
   it and put those people on arms A–C. Do not escalate a failing arm — that is the
   `secret-loyalities` stop rule and it exists because it was learned the hard way.
5. **Commit `PREREGISTRATION.md` before Saturday's first run.** Timestamped, in git, with every
   arm's prediction and falsifier. It costs twenty minutes, it is a differentiator in a field
   that has no pre-registration culture, and it makes "no prediction, no experiment" checkable
   rather than aspirational.
6. **Hard freeze on new runs 24 hours before the deadline.** The writeup reliably takes a
   quarter of the sprint and every team underestimates it. A finished paper about three arms
   beats an unfinished one about five.

## Definition of done, per arm

- [ ] a prediction written down *before* the run
- [ ] a false-positive floor measured, not assumed
- [ ] within-condition variance measured, so effects have honest error bars
- [ ] a portrayal arm, or an explicit statement of why one does not apply
- [ ] every number reported as **effect minus floor**, never absolute
- [ ] recorded with provenance and cost, including when the prediction was wrong
