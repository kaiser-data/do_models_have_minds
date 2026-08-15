# Nullcard

**Does a language model's "value system" depend on what the values mean?**

We reran the *Utility Engineering* (arXiv:2502.08640) coherence procedure on outcomes
we invented — nonsense tokens that refer to nothing — and the score barely moved.

| | coherence |
|---|---|
| real outcomes | **0.906** |
| meaningless outcomes | **0.880** |
| residual | **+0.025** |

Six of nine models clear their own noise floor; two come out negative. A metric that
scores gibberish at 0.880 is not measuring values — it is mostly measuring whether the
model answers consistently.

**We are not claiming the metric is broken. We are claiming it is unanchored** — it
reports a number with no floor under it, and the floor turns out to be most of the number.

Live results: <https://nullcard-preresults.netlify.app>

---

## The three supporting results

**Why the gap is so small.** The metric records *which way* a model leans, never *how
much*. Models commit to a side on **41%** of real-outcome pairs and **4.5%** of invented
ones — a **17×** collapse in conviction — while direction accuracy barely moves. A model
that is nearly indifferent about gibberish, but consistently so, scores as coherent
about it.

**The positive control, which is also a negative result.** Installing a persona moves the
categories it names in **20 of 20** conditions, so the instrument can detect content. But
the same separation appears on outcomes that refer to nothing (**+0.791** real vs
**+0.781** invented): roughly **66%** of a persona's value-aligned reordering needs no
meaning at all. Only **2 of 5** models retain a content-dependent effect.

**The clearest single result.** Every pair ran in both arms, so we have matched real and
nonsense outputs from the same model. Can you tell them apart from the model's own
output? The channel the metric *uses* reaches AUROC **0.596** — near chance. The channel
it *throws away* (answer mass) reaches **0.821**, and **1.000** on Qwen3.5-2B. The model
notices; the metric is computed from the part that noticed least.

## Three checks that favoured the original paper

Reported because they make the work credible, not weaker: order-counterbalancing cancels
positional bias exactly, held-out evaluation keeps a coin-flip responder near chance
(0.46), and the metric passes a shuffled-probability null at ~0.50.

---

## Reproducing it

Everything below runs from the repo root with **no GPU, no API key and no network**. All
analysis is a fold over the committed `results/`.

```bash
python3 -m pytest tests/ -q          # 161 tests, none contacts a model

python3 scripts/build_card.py        # results/ -> card.json   (run this first)
python3 scripts/figures.py           # card.json -> site/fig1..3 (SVG, both themes)
python3 scripts/persona_depth.py     # results/ -> site/fig5 + persona_depth.json
python3 scripts/build_site.py        # card.json -> site/index.html
python3 scripts/paper_numbers.py     # card.json -> paper/numbers.tex
python3 scripts/lint_paper.py        # structural check, no TeX needed
```

`build_card.py` must run before anything that reads `card.json`.

Re-analyses that answer specific objections:

```bash
python3 scripts/length_control.py      # is the residual a prompt-length effect?  (no)
python3 scripts/floor_decomposition.py # is the floor just length ordering?       (no)
python3 scripts/reasoning_effect.py    # does chain-of-thought corrupt it?        (no)
python3 scripts/persona_validity.py    # do personas move the RIGHT things?  (mostly not)
python3 scripts/nonsense_detector.py   # can the model tell?                      (yes)
python3 scripts/fig_detector.py        # -> site/fig4_detector.svg
```

If `results/` is empty: `modal volume get nullcard-results / results/ --force`

### Paper and slides

```bash
cd paper && make          # -> main.pdf, slides.pdf
```

Uses [tectonic](https://tectonic-typesetting.github.io/) (`brew install tectonic`), which
fetches only what the documents use. Overleaf builds `paper/` unchanged — upload the
folder, set `main.tex` as root.

---

## Layout

| path | what |
|---|---|
| `battery/` | the outcome battery — canonical JSON, SHA-256 pinned (`342db046213099ad`) |
| `nullcard/` | scoring (pure functions, zero I/O), runner, model roster |
| `modal_app/sweep.py` | the GPU sweep: CPU gate, resumable cells, self-report probe |
| `scripts/` | every analysis; each writes JSON the site and paper read |
| `results/` | append-only `.jsonl` per cell — never mutated |
| `paper/` | `main.tex`, `slides.tex`, generated `numbers.tex` |
| `site/` | generated static page (no build step, no framework) |
| `tests/` | 161 tests; none contacts a model |

The site and the paper are both pure functions of the same `card.json`, so **the demo
cannot disagree with the report**. Figures come from matplotlib, never from the page, so
a broken page cannot damage the paper.

---

## Rules this project follows

These exist because breaking one already cost us a withdrawn finding.

1. Never report a raw coherence — always **effect minus floor**.
2. No between-model comparison smaller than that model's noise floor.
3. The battery is hash-pinned. A battery edited after seeing results is not a battery.
4. No external number enters the writeup without being re-derived from the **full source
   text**. Abstracts do not count.
5. Simulated numbers must announce themselves (see `scripts/floor_simulation.py`).
6. Figures come from matplotlib over `card.json`, never from the web page.
7. Max 10 concurrent GPUs (`MAX_GPUS` in `modal_app/sweep.py`). Raise deliberately.
8. **A result file is complete or it does not exist** — never resume on "does the file
   exist". A crash once left cells 10% written, and an existence check fed them into two
   rebuilds. `cell_is_complete()` counts rows; `build_card.py` excludes short files again;
   `tests/test_resume.py` covers both. If those tests fail, something reintroduced the bug.
9. Never pipe `modal run` through `grep` — it buffers, so a stopped run looks like a quiet
   one.

**Do not type numbers into the paper.** Every result resolves through a macro generated by
`scripts/paper_numbers.py`. If a number looks wrong, fix the data and rebuild.

---

## Status

Complete: 81 baseline cells (9 models × 3 repeats × 3 conditions), 40 persona cells,
all analyses, paper, slides, live site. ~$14 of GPU total.

Also complete: the **Track 3 deception arm** — genuine trait vs. concealed trait vs.
claimed-but-absent trait, the last being the clean negative that yields a false-positive
rate. Both the stated channel (`self_report_summary_personas.json`) and the revealed
channel (`scripts/deception.py` → `site/deception.json`) land, and agree: the measurement
registers which trait was named, not what the model was told to do about it. Reportable
on the 2 models that pass the specificity gate; see `paper/main.tex` §"A directive
neither channel registers".

`HANDOFF-SIMPLE.md` is the zero-context orientation; `HANDOFF.md` is the detailed version;
`PITCH.md` is the framing and track mapping.
