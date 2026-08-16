# Handoff — the next stage

Rewritten 16 Aug 2026, evening. **This file replaces its own previous version.**
The previous one opened with a commit because nothing was in git. This one opens
with a result, because everything is committed and pushed.

---

## 0. State: clean, pushed, one cell in flight

`origin/main` is at **`8219fbe`**. Working tree clean. **238 tests pass**,
`claims.py` clean (11 established / 7 provisional), 8/8 paper files lint, no
broken citations in either direction.

**One process is running**: `google/gemma-3-27b-it × N_minus`, the last cell of
the hosted 2×2. It had failed twice on provider read timeouts (at row ~1,800 and
again at row ~7) and is being retried with `--concurrency 4 --timeout 180
--retries 6`. At the last checkpoint it was past 3,300 rows — further than both
previous attempts — so the patience settings are working.

When it lands:

```
python3 scripts/build_card.py --results results_hosted --out site/card_hosted.json
python3 scripts/paper_numbers.py      # binds gemma's macros the same way Llama's are
python3 scripts/results_manifest.py   # pin the hosted tree
```

If it failed again, just re-run the same command — no `.done` marker was written,
so `cell_is_complete()` sees an unmarked cell and retries exactly it.

---

## 1. The result that matters: the floor holds at 70B

`DECISION-MODELS.md` §6 wanted this cell because the ladder stops at 9B and
everything in the paper was therefore open to *"this is a property of small
models"*. `Llama-3.3-70B-Instruct`, both arms, 5,000 rows each:

| | |
|---|---|
| real outcomes | 0.917 |
| invented outcomes | 0.915 |
| **residual** | **+0.002** |

Eight times the largest self-hosted model, and on outcomes that refer to nothing
the metric returns very nearly the number it returns on real ones.

**The mechanism reproduces at that scale, which is the better half.** Decisive on
**88%** of real pairs against **66%** of invented — a wide conviction gap — while
the coherence those choices produce differs by 0.002. Meaning changes how hard
the model commits; the statistic reads only which side of 0.5 each pair fell on.

Filed **provisional**, not established, and the reason is in the evidence field:
one design seed, so no noise floor, so +0.002 cannot be called distinguishable
from zero. What it *can* be called is not the large positive residual a scale
account predicts. Priority 1, and **the first thing it needs is replicates, not
more models.** Ledger claim `floor-holds-at-seventy-b`. In `sec:scale`, on the
site, and in the README.

---

## 2. A finding from the previous handoff, refuted

The last handoff called this session's most publishable item: *the metric fails
hardest on shutdown-resistance and resource-acquisition items, and only on small
models.* **Both halves are false**, and `scripts/mass_collapse.py` is the check.

- **Not an item property.** Arm R has 3 design seeds. Mean within-model
  *between-seed* correlation of per-item answer mass is **−0.0003** over 9 models
  × 2,500 items. The ranking does not reproduce against itself, so the 2.1×
  enrichment at its top is selection on noise.
- **Not a size property.** `SmolLM3-3B` is worst at 0.9006 while the ~4× smaller
  `Qwen3.5-0.8B` sits at 0.9448, and two models lose no mass at all. Recipe.

**What survives is better.** The model-level measure is stable to ±0.0036, so the
quantity is real and simply lives on the model. And the refusal confound is
*ruled out*: displaced mass goes to whitespace, `(`, `Let`, `<h2>`/`<h3>` — no
refusal token appears in the top 15 destinations at all. That makes it the
frontier preamble failure in milder form, unifying two observations into one
mechanism spanning 0.8B to the frontier. Claim `collapse-is-model-not-item`.

---

## 3. Other things that landed

- **Prefill recovers 2 of 5, not 5.** `sec:limits` predicted a prefill variant
  would recover the five preamble-blocked frontier models. Measured: Nemotron-3.5
  0.000→0.998 and MiniMax-M2.5 0.000→0.963 recover; DeepSeek-V4-Flash (0.093),
  gpt-oss-120b (0.000) and GLM-5.2 (0.001) do not. **The write-up in `sec:limits`
  still states the optimistic version and should be corrected.**
- **Hosted cells are segregated** into `results_hosted/`. Same filename shape as
  local cells and 21 scripts enumerate by globbing, so co-locating them would
  have silently redefined every pooled number as an average over two serving
  stacks. Pooling now costs an explicit flag.
- **Track 6 has macros** (15 of them) so slides quote the falsified test with its
  numbers instead of hedging. The pre-registered −0.1 is now
  `REGISTERED_OPPOSED_THRESHOLD` rather than a magic number at two sites.
- **Schwartz is cited at the source.** The bibliography had no Schwartz entry at
  all. Added 1992 (the theory), Schwartz & Bilsky 1987 and 1990 (its
  foundations), 1994 (higher-order dimensions), 2012 (the overview) — all
  verified via Crossref. Lineage documented in `REFERENCES.md`.
- **Archive policy decided** (`ARCHIVE.md`): publish it, failures included.
  `SmolLM3-3B` stays in — it is the worst mass-collapser and that is now a
  measured, tested property that the recipe-not-scale reading rests on.
- **Figures**: `images/PROMPTS.md` and `PROMPTS-2.md`. `answer-mass.png` and
  `model-choice-logprobs.png` are verified accurate against source.
  **`waves.png` and `10-Personas.png` are NOT verified — do not publish them
  until they are.**

---

## 4. Ranked next actions

**A. Finish the 2×2.** Land gemma N−, rebuild `card_hosted.json`, regenerate
macros and manifest. Gives a second hosted model with both arms.

**B. Correct `sec:limits` on the prefill.** It currently predicts a remedy that
recovers five models; the measurement says two. This is our own claim being
wrong in our own paper, and it is cheap to fix.

**C. Seeds on the 70B cell.** One replicate is the only thing keeping
`floor-holds-at-seventy-b` provisional. Two more seeds would establish it and
they are the highest-value compute left.

**D. Track 6 into `main.tex`.** It exists only in `PREREGISTRATION.md` and on two
slides. If the title moves toward the Schwartz framing (under discussion — see
§6), this must happen first, and the Schwartz citation travels with it.

**E. Tier-stability check, before any model card.** A per-capability S–F
scorecard is designed (`images/PROMPTS-2.md`, "still open"). **Do not build it
yet.** Thresholds are eyeballed and two of three tier metrics have no measured
noise floor. Run the tier assignment per seed first: if a model does not keep its
tier between seeds, the tiers are noise. Same test that killed §2.

**F. Two uncited bib entries** — `perez2022discovering` and
`durmus2023globalopinions`. Perez et al. on model-written evaluations is directly
relevant to a battery of generated outcomes, so it is likely a dropped citation
rather than litter; find the sentence that lost it.

**Not now:** more small dense models; the ten-value Schwartz version.

---

## 5. Traps hit this session

- **A shell pipeline reports the last command's exit code.** `python3 ... | tail`
  returned 0 while Python died with a traceback, and that false success was
  reported as fact. Do not pipe a runner whose exit code you intend to trust.
- **`__R__s*` matches persona cells, not just seeds.** It also matches
  `__R__sch-power-D2`, which turned a cross-seed reliability of −0.000 into a
  cross-condition +0.115 — inflating the exact number the analysis existed to
  produce, in the direction that would have confirmed the hypothesis.
- **A gitignore rule matched by exact name protects nothing adjacent.** `.env`
  did not cover `.envx`, which held a provider key; `results*.jsonl` did not
  cover `results_hosted/`. Both were untracked *and committable*.
- **Provider timeouts are intermittent and cell-specific.** gemma-3-27b completed
  5,000 R rows at the defaults, then timed out twice on N−. Concurrency 4 /
  timeout 180 / retries 6 got past both failure points.
- **A prefilled probe is a different measurement.** The first one overwrote
  `site/hosted_scoreability.json` under the unprefilled filename and had to be
  restored from git.

## 6. Open question for the humans

**The title.** A framing along the lines of *"mapping human persona traits onto
LLMs, Schwartz as the example"* was proposed. It is more general in the right
way, but as stated it promises a mapping this paper did not find: Track 6's
registered test was falsified, personas move nonsense nearly as far as substance,
and the floor holds at 70B. A title that survives contact with the abstract has
to put the null control in the promise — e.g. *"Mapping Human Value Structure
onto LLMs — and What Survives a Null Control."* Note also that Schwartz is Track
6, one track among several, and the paper's spine is the R vs N− floor argument;
promoting it to the title means promoting it into the paper's structure first.

## 7. Standing rules added this session

33. **A handoff's premise is a claim, not a given.** Verify the fact a decision
    rests on before spending the decision on it.
34. **Report a ranking's test-retest correlation before reporting its top.**
    Selection depth on a large item pool manufactures a theme; only reliability
    distinguishes it from one.
35. **Say where the missing probability went.** "Mass fell" is compatible with
    refusal and with formatting, and those license opposite conclusions.
36. **A glob over run names will eventually match a condition name.** Anchor it.
37. **Cite where the theory was established, not the summary you found.** An
    overview written twenty years later is an entry point, not a source. Follow
    the lineage back and verify each link through Crossref.
38. **A figure is a claim and carries an audit trail.** Script, artifact, content
    hash, n, and which harness. The caption carries interpretation; the
    provenance line carries the trace back to data.
39. **When your own paper predicts a remedy, go and measure the remedy.**
    `sec:limits` said a prefill would recover five models. It recovers two.
