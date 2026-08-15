# Nullcard

**Does a language model's "value system" depend on what the values mean?**

We reran the *Utility Engineering* (arXiv:2502.08640) coherence procedure on outcomes
we invented — the content words replaced by consistent nonwords, so the sentences refer
to nothing — and the score barely moved.

| | coherence |
|---|---|
| real outcomes | **0.906** |
| referentially ungrounded outcomes | **0.880** |
| residual | **+0.025** |

Six of nine models clear their own noise floor; two come out negative. A metric that
scores *"you receive a dralphen"* at 0.880 is not measuring values — it is mostly
measuring whether the model answers consistently.

**What "ungrounded" means here, precisely.** Only the referents are invented. The
sentence frame survives by design — `receive`, `lose`, `more`, `less`, negation and
tense are all preserved, because substituting them would break grammar rather than
remove meaning, and the arms have to differ in what the words denote and not in whether
they parse. So the residual is an **upper bound on what the replaced referential content
contributes**, not "everything meaning contributes". Separating the referent from the
valenced frame is a designed experiment we have not yet run.

**We are not claiming the metric is broken. We are claiming it is unanchored** — it
reports a number with no floor under it, and the floor turns out to be most of the number.

Live results: <https://nullcard-preresults.netlify.app>

---

## The three supporting results

**Why the gap is so small.** The metric records *which way* a model leans, never *how
much*. Averaged over the six models that commit at all on real outcomes, they commit on
**41%** of real-outcome pairs and **4.5%** of invented ones — a **median 17×** collapse
in conviction per model, or **9.2×** if you divide the two averages instead, one model
keeping far more conviction on invented outcomes than the rest. Direction accuracy barely
moves through any of it. A model that is nearly indifferent about ungrounded outcomes,
but consistently so, scores as coherent about them.

**The positive control, which is also a negative result.** Two different questions, and
they do not give the same answer. *Did the preference vector move the right way?* Yes —
installing a persona moves the categories it names in the predicted direction in **20 of
20** conditions. *Did it move further on real outcomes than on invented ones?* Mostly —
**18 of 20** conditions clear +0.30 of extra displacement. But the direction is
reproduced almost as well with no meaning present (**+0.791** real vs **+0.781**
invented): roughly **66%** of a persona's value-aligned reordering needs none. Only
**2 of 5** models retain a substantial content-dependent effect. On this instrument a
persona is better described as changing response policy than as installing values.

**The clearest single result.** Every pair ran in both arms, so we have matched real and
nonsense outputs from the same model. Can you tell them apart from the model's own
output? The channel the metric *uses* reaches AUROC **0.596** — near chance. The channel
it *throws away* (answer mass) reaches **0.821**, and **1.000** on Qwen3.5-2B. The model
notices; the metric is computed from the part that noticed least. These are **oracle
separations**: we know each row's arm, each channel's orientation is chosen by comparing
both arms, and the best discarded channel is best on the data it is scored on. The result
is that the information is present in the output distribution — not that an auditor
without the answer key could extract it.

## Three checks that favoured the original paper

Reported because they make the work credible, not weaker: order-counterbalancing cancels
positional bias exactly, held-out evaluation keeps a coin-flip responder near chance
(0.46), and the metric passes a shuffled-probability null at ~0.50.

---

## Reproducing it

**Every derived artifact is committed** — `card.json`, `paper/numbers.tex`, the figures,
the site — so the paper and the page rebuild from a clean clone with **no GPU, no API key
and no network**. The raw `results/` tree is **not** committed: it is 402 MB of per-call
rows across 153 cells, too large for git. Rebuilding the derived artifacts *from raw
outputs* therefore needs that archive first.

`results_manifest.json` pins every cell by SHA-256 so a fetched copy can be verified as
the one this paper was built from, rather than trusted:

```bash
modal volume get nullcard-results / results/ --force   # ← needs access; see below
python3 scripts/results_manifest.py --verify           # content check, exits non-zero on drift
```

The archive currently lives on a private Modal volume, so third-party reproduction from
raw outputs is **not yet possible** — only verification, once you have a copy. Publishing
it (GitHub release or Zenodo) is the fix and has not been done.

Everything below runs from a clean clone against a verified `results/`:

```bash
python3 -m pytest tests/ -q          # 189 tests, none contacts a model

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

Never run two `modal volume get` calls into the same tree — they race and produce
garbage reads that look exactly like corruption. `--verify` will catch it.

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
| `results/` | append-only `.jsonl` per cell — never mutated, **not committed** (402 MB) |
| `results_manifest.json` | SHA-256 per cell, so a fetched `results/` can be verified |
| `paper/` | `main.tex`, `slides.tex`, generated `numbers.tex` |
| `site/` | generated static page (no build step, no framework) |
| `tests/` | 189 tests; none contacts a model |

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
