# References — with verification status

Built 2026-08-08. **Read the tier column before citing anything here in the report.**

## Why this file exists

The entire catalog was assembled from **search snippets and abstract pages**, never from full
texts. That is adequate for choosing a project. It is **not** adequate for a citation in a
submitted paper. This file records exactly what was verified, so nobody cites a paper for a
claim it does not make.

### Verification tiers

| Tier | Meaning | Safe to cite? |
|---|---|---|
| **A** | Abstract page fetched and read this session | Cite the abstract's claims only. Read full text before citing methods or numbers. |
| **B** | Search-result snippet only — never opened | **Do not cite yet.** Open it first. Title/ID may be right; the claim attached to it may not be. |
| **C** | No identifier at all — a placeholder pointing at a body of work | **Find a real paper or delete the claim.** |

---

## Correction 2: disputed statistics quoted as fact

The headline numbers attributed to `2512.12411` throughout the first draft — **88% vs 10%
chance for sentence localization, 83% vs 50% for strength discrimination** — came from an
abstract-page summary and **could not be reproduced from the paper's own HTML.** §4.2 reads:

> "the model can reliably classify the strength of the coefficient of a normalized injected
> concept vector … with up to **70% accuracy**, far above the **25% chance** baseline"

The same section reports 20% success under the original protocol, collapsing on closely
related tasks, and **0%** correct identification when two concepts are injected at once.

Both figure sets cannot be right. **All numbers from this paper are now marked disputed.** The
hero figure on the site has been corrected to the §4.2 values and carries a warning. Nobody
quotes any of them in the report until the PDF is read.

**Authors now confirmed:** Ely Hahami, Lavik Jain, Ishaan Sinha (Harvard University),
13 December 2025.

## Correction 1: a fabricated author attribution

`2512.12411` was cited throughout the first draft with a surname-plus-"et al." attribution
(the letters F-e-n-g). **No author list was ever retrieved for that paper.** The name was
invented and has been removed from every file. Until someone opens the paper, refer to it by
title and arXiv ID only — *Feeling the Strength but Not the Source* (2512.12411).

This is the exact failure the review protocol exists to catch, and it would have been
embarrassing in a submission where the authors may be in the room. Check the other author
attributions below with the same suspicion.

---

## Tier A — abstract read directly

| ID | Citation | What was actually confirmed | Cited by | Relationship |
|---|---|---|---|---|
| `2512.12411` | *Feeling the Strength but Not the Source: Partial Introspection in LLMs*. arXiv preprint. **Authors unverified.** | Activation steering on Meta-Llama-3.1-8B-Instruct. Localization of injected sentence up to 88% vs 10% chance; relative-strength discrimination 83% vs 50%. Prior binary-detection accuracy "entirely explained by global logit shifts that bias models toward affirmative responses." Effects confined to early-layer injections. | DM-01, DM-02, DM-07, DM-10, INDEX | **Method derived from.** DM-01 is this critique transposed to welfare items. Say so explicitly. |
| `2510.24797` | Berg, C., et al. *Large Language Models Report Subjective Experience Under Self-Referential Processing*. arXiv preprint. | Self-referential prompting elicits structured first-person reports across GPT, Claude, Gemini families. SAE features for deception/roleplay: suppressing increases experience claims, amplifying reduces them. Authors state it is **not** direct evidence of consciousness. | DM-02, DM-08, DM-14 | **Robustness test of.** DM-02 tests an alternative the paper does not rule out. Frame as collegial, not corrective. |
| `2605.13339` | *Probing Persona-Dependent Preferences in Language Models*. arXiv preprint. | Gemma-3-27B and Qwen-3.5-122B. Identifies a "genuine preference vector" tracking preferences across prompts. A probe trained on the helpful assistant **predicts and steers choices of qualitatively different personas, including an evil persona.** Whether a base/no-chat-template arm was run is **not determinable from the abstract.** | DM-05 | **Collision.** Publishes DM-05's falsifier. DM-05 demoted. |
| — | Eleos AI Research. *Research Priorities for AI Welfare*. eleosai.org (org publication, not peer-reviewed). | Five priorities. Priority 1 includes distress monitoring and letting models exit harmful interactions. States "there is nothing close to systematic AI welfare evals" and that measuring whether models have consistent coherent preferences is "some of the lowest-hanging fruit." | DM-03, DM-04, DM-06, DM-15 | **Motivating source.** Quoted directly — keep the quotes exact. |

## Tier B — snippet only, NOT yet safe to cite

| ID | Apparent citation | Snippet claim | Cited by | Must do |
|---|---|---|---|---|
| — | Long, R., Sebo, J., Butlin, P., Plunkett, D., Campbell, R., Beasley, C., Saad, B., Sims, T. *Studying AI Welfare Empirically*. NYU CMEP / Eleos, July 2026. | Three axes: question / entity / method. Entity = model vs. running instance vs. persona. | DM-01, DM-03, DM-05, DM-06, DM-10, DM-11, DM-15 | **Highest priority.** Both host URLs returned HTTP 403 — this is the catalog's most-cited source and it was never opened. The whole "entity dimension" framing rests on a snippet. |
| `2606.09843` | *An LLM-Native Psychometric Instrument Reveals a Self-Report–Behavior Gap Across 25 Models*. June 2026. | Self-descriptions can be coherent and self-consistent while bearing no relation to open-ended actions. | DM-01, DM-03, DM-06, DM-15 | **Partial scoop.** Open before writing the abstract; it constrains the novelty claim. |
| `2607.05552` | *The yes-no bias of large language models reflects answer order and wording, not shifts in moral judgment*. July 2026. | Yes/no bias driven by answer order and wording. | DM-01 | Nearest methodological neighbour. Read before claiming DM-01's method is new. |
| `2509.08480` | *Acquiescence Bias in Large Language Models*. | 37,975 question variations, multiple languages. | DM-01 | Establishes the bias exists. DM-01 is an application, not a discovery. |
| `2502.08640` | Mazeika, M., et al. *Utility Engineering: Analyzing and Controlling Emergent Value Systems in AIs*. NeurIPS 2025. | Thurstonian utility fits; coherence emerges with scale. | DM-04, DM-06, DM-09 | **Check whether they counterbalance option order.** If they do, DM-04's critique weakens substantially. This is a blocking check for DM-04. |
| `2601.01828` | *Emergent Introspective Awareness in Large Language Models*. Anthropic (Lindsey). | ~20% introspection rate, 0% false positives, Claude Opus 4/4.1. | INDEX ledger | Origin of the concept-injection paradigm. Verify the numbers before quoting them. |
| `2603.21396` | *Mechanisms of Introspective Awareness*. Macar, U., Yang, L., Wang, A. | Qwen-32B; middle-layer detection attenuated before output. | DM-07, INDEX ledger | Adjacent to DM-07 — check it does not already run the privileged-access comparison. |
| `2602.20031` | *Latent Introspection: Models Can Detect Prior Concept Injections*. | — | DM-07 | Snippet gave no claim detail at all. |
| `2607.13596` | *Protective Capacity Hallucination: When LLMs Claim Nonexistent Capabilities*. | Models claim capabilities they lack. | DM-01 | Closest thing to DM-01's nonsense-capability control. Must differentiate. |
| `2606.00860` | *GenPT: Beyond Self-Report for Reliable LLM Psychometrics via Generative Projective Testing*. | — | DM-06 | **Unsearched collision risk for DM-06.** Never investigated. |
| — | Anthropic. *Claude 4 System Card* — model welfare assessment, incl. Eleos external evaluation and the "spiritual bliss attractor" observation. | From training knowledge and snippets, not read this session. | DM-03, DM-08, DM-12 | DM-12's entire premise rests on this. Open the system card and quote it exactly. |

## Tier C — placeholders, not citations

Each of these is a gesture at a literature, not a source. **Replace with a specific paper or
cut the claim.** Owners should resolve their own before Saturday.

| Placeholder | Card | Note |
|---|---|---|
| "the LLM-as-judge position-bias literature" | DM-04 | Needs 1–2 specific papers. DM-04's whole premise depends on this being established. |
| "CAA / representation engineering literature" | DM-08, DM-14 | Cite Rimsky et al. on contrastive activation addition and Zou et al. on representation engineering — **both from memory, both unverified.** |
| "Kahneman/Tversky framing and scope-insensitivity literature" | DM-09 | Pick specific works; the general gesture is not citable. |
| "situational-awareness benchmarks" | DM-11 | Likely the SAD benchmark. Unverified. |
| "mode-collapse and degeneration literature" | DM-12 | Needs a specific source. |
| "LLM evaluation-variance literature" | DM-13 | Needs a specific source. |
| "the model-organisms literature from AI safety" | DM-15 | The methodological ancestor of the whole idea — **it deserves a real citation, not a gesture.** |
| "the persona-selection model" / nostalgebraist, *the void* | DM-05 | Blog-post sources. Cite as such, or drop with DM-05. |
| Binder et al., *Looking Inward* | DM-07, DM-11 | From training knowledge. Author and title unverified this session. |
| "Every measurement audited, in full and fairly" | DM-10 | Deliberately open — becomes real citations once the three instruments are chosen. |

---

## Self-attribution

DM-15's design, and the control philosophy running through the whole catalog — matched
controls, verified-clean negatives, measured false-positive rates, pre-registered falsifiers,
seed replicates as variance denominators — are **carried over from the team's own
`secret-loyalities` work** (Apart Research Secret Loyalties hackathon, July 2026). That is
prior work by the authors and should be cited as such, not presented as new.

## Protocol before submission

1. Every Tier B source gets **opened** before it appears in the PDF. No exceptions.
2. Every Tier C placeholder becomes a real citation or the sentence goes.
3. For each citation, check the source **makes the claim attributed to it** — not merely that
   it is topically related.
4. Label preprints as preprints. Most of this list is arXiv, unrefereed.
5. Arms are owned: each owner clears the citations for their own card.
