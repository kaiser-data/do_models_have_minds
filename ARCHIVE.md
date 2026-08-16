# The results archive

**Decision, 16 Aug 2026: publish it, failures included.**

The raw sweep output is too large for git (hundreds of MB of per-call rows), so
it lives on the Modal volume `nullcard-results` and is pinned by content here:
`results_manifest.json` records a SHA-256 per file, plus the row count and
whether the cell carries a `.done` marker. A fetched copy can therefore be
verified as *the* copy the paper was built from, rather than a copy that looks
similar.

`scripts/results_manifest.py` regenerates it. `tests/test_results_manifest.py`
fails if the shipped manifest and the shipped tree disagree — including when an
unlisted `.jsonl` appears, because an analysis that folds over `*.jsonl` would
silently include it.

## Two trees, not one

| tree | what is in it | why separate |
|---|---|---|
| `results/` | the 9 self-hosted models, run on Modal under vLLM | the paper's results |
| `results_hosted/` | frontier models called over a hosted API | different harness |

They are kept apart on purpose. The filenames have the same shape
(`<id>__<arm>.jsonl`), 21 scripts enumerate models by globbing a results
directory, and `build_card.py` takes `*.jsonl` with no roster filter — so a
hosted cell sitting in `results/` would not add a row to a table, it would
silently redefine every pooled number as an average over two serving stacks.
Pooling them is possible and costs an explicit flag.

## The failures are part of the archive

They are not pruned, and they are the reason to publish rather than a reason
not to. Anyone auditing this instrument needs the cells where it failed:

- **Aborted cells keep their partial rows and their `.done` verdict.**
  `gemma-4-E2B-it × sch-universalism × N−` stops at answer mass 0.246 — the
  model stopped putting its choice in the first token under that persona. The
  sidecar records the abort so the cell is excluded *for the stated reason*
  rather than incidentally by a coverage floor.
- **Models the metric cannot read at all are listed, not omitted.** Six of ten
  hosted frontier models are unscoreable by first token: five spend that token
  on a reasoning preamble, one is refused logprobs by its vendor. Their absence
  from the results is a selection effect on output format, and it bounds every
  other claim in the ledger.
- **A refuted finding of our own is kept with its refutation.** The per-item
  answer-mass collapse ranking is enriched 2.1× for shutdown-resistance and
  resource-acquisition outcomes and reads like a result. Its test-retest
  correlation across design seeds is −0.0003. Both numbers are in the archive
  and in `sec:limits`; the enriched list would be reproducible by anyone who
  did not run the reliability check.
- **`SmolLM3-3B` stays in.** It is the worst mass-collapser in the roster
  (mean answer mass 0.9006, against exactly 1.0000 for `LFM2.5-1.2B` and
  `granite-4.1-3b`). That is a measured, tested property rather than an
  anomaly, and it is a load-bearing part of the recipe-not-scale finding.
  Excluding the model would remove the evidence and improve the averages,
  which is the wrong trade.

## Reproducing

```
python3 scripts/results_manifest.py          # regenerate the pin
python3 -m pytest tests/test_results_manifest.py
python3 scripts/build_card.py --results results        --out site/card.json
python3 scripts/build_card.py --results results_hosted --out site/card_hosted.json
```

Everything the paper quotes resolves through `paper/numbers.tex`, which is
generated — no result is typed into prose.
