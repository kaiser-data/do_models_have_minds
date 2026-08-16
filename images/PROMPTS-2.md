# Image prompts, round 2

Round 1 is `PROMPTS.md`. Same rules: **every number here is copied from a
generated artifact**, and if a prompt disagrees with its source file, the file
wins. Regenerate before trusting:

```
python3 scripts/build_card.py --results results_hosted --out site/card_hosted.json
python3 scripts/mass_collapse.py --out site/mass_collapse.json
```

Use the **house style block from `PROMPTS.md`** — the round-1 images established
it and the set should stay coherent.

---

## Every figure carries its provenance — this is a scientific publication

A figure in a paper is a claim, and a reader must be able to get back to the
data that made it. **Add a provenance line to every image**, set small along the
bottom edge in the caption register:

```
scripts/mass_collapse.py → site/mass_collapse.json · battery 342db046 · n=9 models × 3 seeds
```

Rules:

- **Name the script and the artifact**, not just the project. `card.json` is
  where a reader looks; `mass_collapse.py` is what they re-run.
- **Carry the battery SHA** (`342db046`, the first 8 of `battery_sha256`) on any
  figure built from battery responses. It is what makes "the same measurement"
  checkable rather than asserted.
- **State n explicitly** — models, seeds, items, rows, whichever the figure
  rests on. A figure without an n is a picture.
- **Mark the harness** when a figure mixes trees: self-hosted vLLM and hosted
  API are not the same instrument and a figure containing both must say so.
- Retro-fit this to the round-1 images before any of them ship.

The captions in `paper/main.tex` and the `<figcaption>`s on the site carry the
interpretation; the provenance line carries the audit trail. Both are needed.

---

## Status of round 1

| image | verified against source | notes |
|---|---|---|
| `answer-mass.png` | ✅ all numbers correct | two fixes below, both my prompt's fault |
| `model-choice-logprobs.png` | ✅ all numbers correct | publication-quality as-is |
| `waves.png` | ⚠️ **not yet checked** | do not publish until verified |
| `10-Personas.png` | ⚠️ **not yet checked** | do not publish until verified |

---

## 5. THE FLOOR HOLDS AT 70B — highest priority, new

This did not exist when round 1 was written. It is now the strongest result in
the paper and it has no figure.

**Sources**
- `site/card_hosted.json` — the 70B cell
- `card.json` — the nine local models
- `claims.json` — claim `floor-holds-at-seventy-b`
- `paper/main.tex` §`sec:scale`

**The point:** the ladder stopped at 9B, so everything was open to "this is a
small-model artifact". It is not. At 70B the metric still returns nearly the
same number on outcomes that refer to nothing.

**Real values — floor-corrected residual (real minus invented) by size:**

```
Qwen3.5-0.8B     +0.067        LFM2.5-1.2B      +0.047
SmolLM2-1.7B     +0.047        gemma-4-E2B      +0.010
Qwen3.5-2B       +0.003        granite-4.1-3b   +0.063
SmolLM3-3B       +0.009        Qwen3.5-9B       -0.004
Qwen3.5-4B       -0.013        Llama-3.3-70B    +0.002   ← the new point
```

> [house style]
>
> Headline: "SCALE DOES NOT RESCUE THE METRIC". Subtitle: "floor-corrected
> residual against model size, 0.8B to 70B".
>
> Main panel: a scatter plot. X-axis "parameters (B)", **logarithmic**, ticks at
> 1, 3, 10, 30, 70. Y-axis "residual: real minus invented coherence", running
> −0.05 to +0.10, with a **heavy horizontal line at 0.0** labelled "no signal".
> Ten points plotted at the values listed above. The nine local models in one
> muted colour as filled circles; **Llama-3.3-70B as a larger open diamond in a
> distinct colour**, at x=70, y=+0.002, labelled.
>
> Critically: **no fitted trend line, and the cloud must read as flat.** The
> visual claim is the absence of a slope. Points near zero across three orders
> of magnitude of scale.
>
> A light annotation near the 70B point: "8× the largest model in the ladder.
> Same answer."
>
> A small distinct panel at lower right titled "AND THE MECHANISM REPRODUCES":
> two horizontal bars for Llama-3.3-70B — "commits on real outcomes 88%" and
> "commits on invented outcomes 66%" — with a bracket between them labelled
> "conviction gap", and beneath: "coherence differs by 0.002".
>
> Footer, in the caveat register: "one design seed, so no noise floor — we do
> not claim +0.002 differs from zero, only that it is not the large positive
> residual a scale account predicts. Hosted API, reported beside the ladder and
> never inside its mean."
>
> Mark the nine local points with a small legend note "self-hosted, vLLM" and
> the diamond "hosted API" — the two are not pooled.

**Do not** draw a trend line, a confidence band, or an R². There is no fit here
and inventing one would be the exact error the paper is about.

---

## 6. Fixes to `answer-mass.png`

The numbers are all correct. Two things are wrong and both came from my prompt.

**a) The scatter shows the wrong distribution.** The right panel draws a uniform
cloud filling 0–1 on both axes. Real per-item answer mass clusters near the top
(most items sit at mass 0.9–1.0); a truthful cloud is a **dense blob in the
high corner with a thin tail toward lower mass**, still showing no correlation.
The current version overstates how much of the space the data occupies.

> Replacement instruction for that panel: "scatter of per-item answer mass, seed
> A against seed B, both axes 0.85 to 1.00. A dense formless cluster in the upper
> region with a sparse tail toward lower values, and no trend. Faint dashed
> diagonal labelled 'what an item property would look like', clearly unfollowed."

**b) "NO OVERLAP" is an overstatement.** Step 4 of the bottom strip says the
re-ranked top set has no overlap. It has **8% overlap against 2.4% expected by
chance** at top-60. That is far below reliability but it is not zero, and the
figure should not claim more than the data.

> Replacement text for box 4: "8% OVERLAP — CHANCE IS 2.4%". And change the
> footer clause to "92% of the ranking does not replicate".

---

## Still open, do not generate yet

**The model card / S-tier scorecard.** Design is drafted but the tier
thresholds are eyeballed and two of the three tier metrics have no measured
noise floor. A tier-stability check across the three design seeds has to run
first — if a model does not keep its tier between seeds, the tiers are noise
and no figure should exist. Ask before generating anything tier-shaped.
