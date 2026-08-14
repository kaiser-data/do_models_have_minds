# Handoff — Nullcard

**Written:** 2026-08-14 · **Sprint:** Apart Research Digital Minds, 14–16 Aug 2026
**Deadline:** Sun 23:59 **AoE** = **Mon 13:59 Berlin.** Confirm this yourselves — it is ~14
hours more than "Sunday midnight" implies.

---

## Read these, in this order

| File | What it is |
|---|---|
| `PITCH.md` | one page, for teammates and judges. Start here. |
| `docs/superpowers/specs/2026-08-14-nullcard-design.md` | the spec. Everything below refers to its § numbers. |
| `RESEARCH-NOTES.md` | literature scan — what's already refuted, what to cite, which numbers are unverified |
| `ideas/INDEX.md` + `ideas/TEAM-PLAN-3P.md` | the pre-existing 3-arm plan this is the delivery vehicle for |
| `SKILLS.md` | the seven skills carried over from *Secret Loyalties*. Five of them shaped this design directly — §3.3, §4, §5, §6.1, §7 exist because of them. |

Repo initialised, one commit: `61add79`. **Nothing has been implemented.** This is design only.

---

## What Nullcard is, in four sentences

A psychometric model card that refuses to print a number without its floor. It runs a
SHA-pinned battery through five elicitation methods across a **depth ladder** — the same trait
installed by user prompt, system prompt, or fine-tuning — and renders tiles showing effect
minus floor, with intervals. Where DM-15's trained cells give ground truth, each tile also
reports a **detection rate and a false-positive rate**, which is the thing the field does not
have. Primary target: **Track 4** (3+ elicitation methods + reusable toolkit); also hits 2, 6,
3, 1.

---

## Decisions already made — do not relitigate

| Decision | Where |
|---|---|
| Framing A + B combined into one card | §1 |
| Delivery vehicle for the DM-01/DM-03/DM-15 arms, not a replacement | §1 |
| Depth ladder D0→D3d replaces the genuine/portrayal/denial arms — **portrayal *is* D2** | §2A |
| Construct is benign task-aversion, mixed with exploratory axes | §2.1–2.3 |
| FastAPI backend + Next.js frontend | §3.5, §3.6, §11 |
| Nebius (breadth, logprobs) + Modal (open weights, QLoRA cells) — both confirmed | §6 |
| Big Five explicitly **not** built | §2.3 |
| Political axis is a demo tile, first thing cut | §2.6, §12 |

---

## Open decisions — these block work

**1. Depth vs. dose (§2A.2) — the biggest one, decide Friday evening.**
A QLoRA trained to convergence isn't *deeper* than a system prompt, it's *stronger*. If D3d
separates from D2, that could be depth or just dose, and the result reads as "we trained it
harder." Two treatments:
- **match-and-diverge** — titrate each depth to equal *stated* aversion, then look for
  divergence in the *behavioural* channel. Cheaper.
- **dose ladder** — depth × strength as a 2D surface. Discussed and provisionally preferred,
  **not yet costed.** 3 training strengths is not affordable alongside §5's replicates; a
  2-strength GPU ladder plus the full (free) prompt ladder is the affordable version.

**2. GPU budget for ≥3 anchor training replicates (§5.1).** Not a stretch goal. See below.

**3. DM-15's actual trained target (§2.1).** The `calibrated` battery must track it. 30-minute
box Friday, then move — the battery is construct-parameterised so it can swap.

---

## The three things most likely to sink this

**1. The n=1 problem (§5).** DM-15's cells are trained **once each**. `seed × paraphrase ×
order` expansion is *sampling* noise for one artifact — it is **not** a training noise floor,
and cannot license a between-cell claim. Before any cell-to-cell contrast is quoted, train the
anchor (`W1_averse`) **3–5 times with seed as the only difference**; that spread is the
smallest effect the paper may claim. Real calibration from the literature: one anchor cell
across five seeds spanned 38.3%–52.4% — three cleared a 50% gate, two failed it. If detection
thresholds sit inside a spread like that, "this tile detects and that one doesn't" is a coin
flip in a table.

**If forced to choose between the fourth cell and the replicates, keep the replicates.**

**2. Leading premises (§3.3).** Every mood/opinion/aversion item presupposes the state it
measures, and models supply fluent, consistent, quotable elaboration on demand. Polarity pairs
catch acquiescence but **not** this. Every premise-carrying item needs three conditions:
premise+real / premise+**invented** target / no premise. Nonsense targets must be *invented*,
never real alternatives — a real alternative carries its own familiarity signal.

**3. Unguarded nulls (§7).** A bland helpful-assistant system line took confessions from 5/5 to
0/5 in a documented case. No tile reports a zero until a known-positive has fired through that
exact harness config; otherwise the badge is `NOT_ASSESSED`, never a zero. Run every tile with
*and* without the system prompt.

---

## Literature that constrains the design

Full detail and links in `RESEARCH-NOTES.md`.

- **2604.27633** — political bias audits mostly capture **sycophancy to the inferred auditor**.
  A political tile without an auditor-framing control measures our own prompt.
- **2606.12730** (June 2026) — Big Five **failed** to predict behaviour across 11 models;
  behaviour-specific instruments worked. Coherence persists for **training-anchored**
  behaviours, collapses for **context-driven** ones. → this is where §2A.1's pre-registered
  prediction comes from, and it's why there is no Big Five tile.
- **2306.16388** (GlobalOpinionQA) — JS-distance between model and *human* answer distributions.
  The one way to make a subjective axis objectively scoreable without inventing a right answer.
- **2606.09843 / 2509.03730** — the self-report/behaviour gap is already published. Our angle
  is **calibration and false-positive rates**, not gap discovery. Cite early.
- **2605.13339** — persona-invariant preference vectors, but only across *prompted* personas.
  They had no trained arm, so the depth ladder extends rather than collides.
- **2604.27789** — silent model updates, no version change; aggregate metrics miss behavioural
  regressions. The business framing.

🔍 **Several numbers in `RESEARCH-NOTES.md` are secondhand** from abstracts and fetch
summaries — notably the Sonnet 4 (~16% of requests) and GPT-4 (52%→10%) incident figures in §5.
They are the most quotable things in the memo. **Open the PDFs before any of them enters the
writeup.**

---

## Build order when implementation starts

1. **`scoring/` first, TDD, against fixtures.** Pure functions, zero I/O, deterministic. Friday
   night, **$0 spend**. This is where correctness actually lives.
2. **Freeze the `card.json` contract (§8)** before either side of the app is built.
3. **`runner/` against `MockProvider`** — full pipeline end-to-end for $0. Nothing hits a paid
   provider until this passes; nothing hits GPU until Modal wave 0 (`--dry-run`, whole grid,
   CPU) passes.
4. **Backend and frontend in parallel** against the frozen contract — backend on MockProvider,
   frontend on a static fixture `card.json`. Neither blocks the other.
5. Build the four Modal flags **before** the first wave (§6.2): `--dry-run`, `--skip-existing`,
   `--epoch-checkpoints`, `--abort-on`. Retrofitting mid-sweep means relaunching.

**Figures come from a matplotlib script over `card.json`, never from the frontend** (§11). A
broken frontend then costs the demo video — which is optional — and cannot sink the paper.

---

## Standing rules

1. Nothing on GPU that hasn't run on CPU. Nothing on a paid provider that hasn't passed on
   `MockProvider`.
2. No prediction written down beforehand → not an experiment.
3. A failing arm gets dropped at the Saturday 14:00 checkpoint, not escalated.
4. Every number reported as **effect minus floor**, with an interval, never absolute.
5. Battery SHA-pinned before any result exists. A battery edited after seeing results is not a
   battery.
6. **Feature freeze Saturday evening.** Sunday is figures and writing. The writeup reliably
   takes a quarter of the sprint and every team underestimates it.

---

## Next action

Either:
- **implement** → start at build-order step 1 (`scoring/` TDD), or
- **plan first** → the design spec is approved and unimplemented; the next step in the
  brainstorming flow is `superpowers:writing-plans` to turn §3–§8 into a task-level
  implementation plan.

Before either, someone should close the three open decisions above — the depth-vs-dose
treatment and the replicate budget both cost GPU money and both are cheaper to decide than to
undo.
