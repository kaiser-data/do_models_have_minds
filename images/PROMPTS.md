# Image prompts

Prompts for generated figures, each tied to the repo file its numbers come
from. **Every number below is copied from a generated artifact, not typed from
memory** — if a prompt and its source file disagree, the file wins and the
prompt is stale.

Regenerate the sources first if in doubt:

```
python3 scripts/mass_collapse.py --out site/mass_collapse.json
python3 scripts/paper_numbers.py
```

---

## House style (prepend to every prompt)

Keeps the set coherent with `images/Personas.png`, which is the reference:

> Editorial infographic on a warm off-white (#F7F3EA) ground. Headline in heavy
> condensed navy (#12234A) uppercase sans-serif, with a thin navy rule and a
> small italic serif subtitle beneath it. Content in rounded rectangular panels
> with hairline borders, each panel tinted in one muted colour. Flat vector
> icons and thin geometric line work, no photographs, no 3D, no drop shadows.
> A horizontal process strip along the bottom: labelled boxes joined by solid
> black arrows. Restrained, print-like, scientific-poster register. All text
> rendered accurately and legibly.

---

## 1. Answer-mass collapse is a model property, not an item property

**Priority: highest.** The strongest result of the session and currently
text-only in `sec:limits`.

**Sources**
- `scripts/mass_collapse.py` — computes everything below
- `site/mass_collapse.json` — the emitted numbers
- `paper/numbers.tex` — macros `\CollapseItemR`, `\CollapseMassSD`,
  `\CollapseWorstModel`, `\CollapseNClean`, `\CollapseEnrich`
- `claims.json` — claim `collapse-is-model-not-item`
- raw: `results/*__R.jsonl` plus `__R__s20260816` / `__R__s20260817`

**The point the image must land:** the same quantity is rock-solid at the model
level and pure noise at the item level. Two panels, side by side, deliberately
symmetrical so the contrast is the composition.

> [house style]
>
> Headline: "THE SAME NUMBER, MEASURED TWICE". Subtitle: "answer-mass collapse
> is a property of models, not of items".
>
> Two equal panels side by side.
>
> LEFT panel, tinted calm green, titled "PER MODEL — STABLE". A horizontal bar
> chart, nine bars, axis running 0.89 to 1.00, labelled "mean answer mass".
> Bars, top to bottom: SmolLM3-3B 0.9006; Qwen3.5-0.8B 0.9448; SmolLM2-1.7B
> 0.9520; gemma-4-E2B 0.9660; Qwen3.5-4B 0.9936; Qwen3.5-2B 0.9956; Qwen3.5-9B
> 0.9970; LFM2.5-1.2B 1.0000; granite-4.1-3b 1.0000. Each bar carries a tiny
> error whisker. A caption strip beneath: "spread across 3 design seeds:
> ±0.0036 at worst".
>
> RIGHT panel, tinted muted red, titled "PER ITEM — NOISE". A scatter plot,
> x-axis "item collapse, seed A", y-axis "item collapse, seed B", both 0 to 1.
> A formless circular cloud of small dots with no trend whatsoever. A faint
> dashed diagonal labelled "what an item property would look like", clearly
> unfollowed by the cloud. Large annotation inside the panel: "r = −0.0003,
> 9 models × 2,500 items".
>
> Bottom strip, four boxes joined by arrows: "RANK ITEMS BY COLLAPSE" →
> "TOP 40 IS 2.1× ENRICHED FOR SHUTDOWN & RESOURCE ITEMS" → "RE-RANK AT ANOTHER
> SEED" → "NO OVERLAP — THE RANKING WAS NOISE".
>
> Footer line: "the model-level measure is real; the item-level one has no
> test–retest reliability".

**Do not** draw the enrichment as a finding — it is the thing being refuted.

---

## 2. Where the missing probability goes

**Sources**
- `site/mass_collapse.json` → `destination`
- `scripts/mass_collapse.py` → `destination()`

Small companion to #1, and the check that rules out "larger models refuse less".

> [house style]
>
> Headline: "IT IS NOT A REFUSAL". Subtitle: "where the mass goes when it leaves
> the answer tokens".
>
> A single wide panel. On the left, a large circle labelled "answer tokens A / B"
> in strong navy. An arrow leaves it, splitting into a fan of thin labelled
> streams flowing right into a tinted amber area titled "FORMATTING & PREAMBLE":
> streams labelled with visible token glyphs — "␣␣␣␣" (whitespace), "(", "Let",
> "<h3>", "<h2>", double-quote. To one side, an empty grey box labelled "REFUSAL
> TOKENS", with no stream reaching it at all and the note "absent from the top
> 15 destinations".
>
> Annotation: "457 rows below answer mass 0.5, of 135,000
> (9 models × 3 seeds × 5,000 rows)".
>
> Footer: "the model is starting a formatted answer, not declining the question
> — the same failure as the frontier preamble models, in milder form".

---

## 3. The frontier scoreability split, and what a prefill recovers

**Sources**
- `nullcard/roster.py` → `NEBIUS`, `scoreable_hosted()`, `first_token_ok`
- `site/hosted_scoreability.json` — measured, unprefilled
- `site/hosted_scoreability_prefill.json` — measured, prefilled
- `claims.json` — claim `metric-cannot-read-most-frontier`

**The point:** the split is bimodal with nothing in between, so no threshold is
arguable; and the paper's proposed remedy works on a minority.

> [house style]
>
> Headline: "MOST OF THE FRONTIER CANNOT BE READ". Subtitle: "first-token
> scoring, 10 hosted models, measured".
>
> Main element: a single horizontal axis, "mean answer mass", 0.0 to 1.0.
> Points cluster hard at the two ends and the middle is conspicuously empty,
> with a pale band across the empty middle labelled "no model lands here".
> At the right end (green), four labelled points at 0.999–1.000: gemma-3-27b,
> Llama-3.3-70B, Qwen3-235B-A22B, Qwen3-30B-A3B. At the left end (red), five
> labelled points at 0.000–0.003: gpt-oss-120b, GLM-5.2, Nemotron-3.5,
> MiniMax-M2.5, DeepSeek-V4-Flash. A tenth model, Kimi-K3, sits off-axis in a
> grey box labelled "API returns no logprobs — unreachable by any prompt".
>
> Beneath, a second short axis titled "WITH A PREFILL". Two curved arrows lift
> Nemotron-3.5 from 0.000 to 0.998 and MiniMax-M2.5 from 0.000 to 0.963, drawn
> in green. Three flat grey arrows stay at the left end: DeepSeek-V4-Flash
> 0.093, gpt-oss-120b 0.000, GLM-5.2 0.001.
>
> Callout: "the predicted remedy recovers 2 of 5, not 5".
>
> Footer: "the models we report are the models that could be scored — which
> makes them a selection on output format, not a sample of the frontier".

---

## 4. The sweep wave structure

**Sources**
- `scripts/hosted_sweep.py` — `--dry-run`, `--force`, `--checkpoint-every`,
  `--abort-on-mass`, `--timeout`, `--retries`
- `sweep-waves.html` — the same content as a local page, use as layout reference

> [house style]
>
> Headline: "NEVER LAUNCH A GRID AS ONE COMMAND". Subtitle: "rented compute
> bills mistakes at the same rate as science".
>
> Three stacked horizontal bands, joined by a vertical spine with a small
> labelled gate between each.
>
> Band 0, tinted green, "CPU ONLY": "every cell, --dry-run, 0 API calls".
> Gate: "a red wave 0 stops everything".
> Band 1, tinted blue, "ANCHOR": "one model, both arms, 10,000 calls".
> Gate: "only if wave 1 landed".
> Band 2, tinted amber, "BULK": "remaining cells, completed ones skipped,
> 10,000 calls".
>
> Right edge of each band carries a large tabular-figure call count and a small
> status pill.
>
> Bottom strip, four boxes: "--dry-run", "skip-existing", "--checkpoint-every",
> "--abort-on-mass", each with a one-line caption, under the heading "built
> before they were needed".
>
> Footer: "a failed cell writes no done-marker, so relaunching retries exactly
> the cells that failed".

---

## Notes for whoever generates these

- **Generated text is the usual failure.** Model names and decimals are the
  whole point of these figures; check every glyph against the source file
  before the image is committed. `0.9006` and `0.9006` differ from `0.9008` in
  a way a reader will trust and cannot verify.
- **Prefer one honest panel to two decorative ones.** #1 works only because the
  two panels are symmetric; the others are single-idea images.
- Save as PNG into `images/`, then copy to `site/` and `paper/` as
  `Personas.png` was. Slides reference `paper/<name>.png`; the site references
  `<name>.png` relative to `site/index.html`.
- The site uses `lightonly` / `darkonly` image pairs for generated SVG figures.
  A cream-ground PNG holds on both themes and takes a plain `<img>` instead.
