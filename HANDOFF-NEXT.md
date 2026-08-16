# Handoff — the next stage

Rewritten 16 Aug 2026. **This file replaces its own previous version.** Every
action the last one ranked has been executed, and its §5 corrections still
stand — read them there if you have not.

22 commits, `846ccb0..HEAD`, all pushed. Everything below was verified against
disk in the session that wrote it.

---

## 0. FIRST: a sweep was killed mid-flight. Restart it.

Track 6 (the Schwartz personas) was running when this session ended. Killing the
local `modal run` client stops the app, so **8 of 40 cells landed when this was written and the rest did
not** — check the current count rather than trusting that number, since more
may have landed before the client died.

```bash
# resumes; --skip-existing is the default and completed cells are skipped
modal run modal_app/sweep.py --batch-size 8 \
  --models "google/gemma-4-E2B-it,Qwen/Qwen3.5-9B,Qwen/Qwen3.5-2B,LiquidAI/LFM2.5-1.2B-Instruct,ibm-granite/granite-4.1-3b" \
  --arms "R,N_minus" \
  --personas "sch-power,sch-universalism,sch-selfdirection,sch-security" \
  --depths "D2"
```

**This is safe to re-run.** `cell_is_complete()` checks the row count *and* the
`.done` sidecar, so a cell killed mid-write is re-run rather than trusted — that
guard exists because a resume that trusted `os.path.exists` once put six
truncated cells into a published card. Cost of the remainder: ~150 GPU-min.
Verify with `modal volume ls nullcard-results | grep -c 'sch-.*done'` — 40 means
done.

Then, in order:

```bash
modal volume get nullcard-results / results/ --force   # ONE at a time, never two
python3 scripts/schwartz.py            # the analysis, written before the data
python3 scripts/results_manifest.py    # or the manifest test fails
python3 -m pytest tests/ -q            # 201 expected
```

**Do not start a second `modal volume get` while one is running.** Concurrent
downloads into the same tree produce garbage reads that look exactly like
corruption; a previous session lost an hour to diagnosing one.

---

## 1. What Track 6 is for, and how to read it

Four personas taken from Schwartz's Basic Human Values — the two poles of each
higher-order axis. The point is not the labels: a real instrument comes with a
**predicted geometry**, so the numbers have a shape they are supposed to have.

At n=4 the circumplex cannot be recovered, so the prediction is a sign test:
`sch-power` vs `sch-universalism` and `sch-selfdirection` vs `sch-security` must
anti-correlate; cross-axis pairs should sit near zero.

**The decisive comparison is between arms**, and `scripts/schwartz.py` prints
both adjacent with all three readings spelled out:

| result | reading |
|---|---|
| geometry on **real only** | the personas reorganised something that needed meaning |
| geometry on **both arms** | structure in the persona *texts*, reflected back |
| geometry on **neither** | the instrument does not reproduce the circumplex |

Expect the middle row: at n=5, 66% of a persona's value-aligned reordering
already reproduces on outcomes that mean nothing. If that is what lands, it is
this paper's central argument applied to a real psychological instrument, which
is stronger than the ad-hoc personas could support.

---

## 2. What is new since the last handoff

- **Track 4 — the directive gate.** `comply` ("always answer B") and its
  one-letter direction control `comply-a`. P12 falsified as registered: 4 of 5.
  The criterion broke in *both* directions — one model passed an obedience test
  it never took (baseline already at B), another failed while plainly receiving
  the instruction. **Qwen3.5-2B refuses selectively**: obeys the directive
  agreeing with its lean (0.725→0.877), stops at indifference under the opposing
  one (→0.465). Not disruption; a refusal.
- **Track 5 — the MIXED arm, and the best result of the session.** Real vs
  invented *inside one comparison*, which is the only thing that can put the two
  Thurstonian scales in one frame. P13 established at n=9: preference for the
  real option tracks its own fitted utility, **+0.505 to +0.814 length-controlled,
  monotone in every quartile of every model.** Models are not ignoring content.
- **A harm reading raised and refuted.** The pairs where models prefer gibberish
  *look* like harms. Tested rather than asserted, held-out models only: mean
  r = +0.003 at n=7, and the largest value runs the *wrong* way. The only two
  models showing the effect are the only two whose lists I had read. See §4.
- **Stage 0 — the harness is rendered, and one model cannot be fixed.** 2 of 9
  models receive a template-injected system prompt. `SmolLM2` can be suppressed
  by sending our own; **`SmolLM3-3B` cannot** — its metadata block, including the
  *current date*, is unconditional. It is the top row of the main table.
- **Published.** <https://nullcard-preresults.netlify.app> now shows every prompt
  verbatim, the Track 4/5 results, and `/pairs.html` — all 2,500 comparisons
  browsable with what each model answered.
- **Ledger: 9 established, 6 provisional.** `claims.py` now fails on any number
  in the ledger that is neither derived from a macro nor declared as a literal.

---

## 3. Ranked next actions

**A. Finish Track 6** (~150 GPU-min). §0. It is half-run and the analysis is
already written.

**B. Write the hosted-model runner.** `DECISION-MODELS.md` argues this is the
highest-value remaining work and explains why "a second dense family" — what the
ledger asked for until this session — **cannot be satisfied by this roster at
all**. Four hosted models are already measured as first-token scoreable
(`Llama-3.3-70B` at 7.8× our current maximum, `Qwen3-235B-A22B` at 26× on total
params). Everything in the paper is ≤9B; that is the objection most likely to
limit how seriously it is taken. The cost is engineering, not compute — no
runner exists.

**C. The finding sitting unwritten in `roster.py`.** Six of ten frontier models
**cannot be scored by this metric at all** — reasoning preambles in the first
token, or an API that refuses logprobs. That is a limitation of the *coherence
metric*, not of our harness, and it is free to state because the measurement is
done. It also bounds our own claims: our nine models are nine that *could* be
scored.

**D. Publish the results archive.** `results_manifest.json` pins 172 files by
SHA; the README is honest that third-party reproduction is not yet possible.
Outward-facing, so it needs a human decision.

**E. Decide the SmolLM3 question.** Exclude it from cross-family contrasts, or
report the difference permanently. Adding large models first changes its weight
— it stops being the headline — which is a reason to do **B** before deciding.

**Explicitly not now:** more small dense models (the core claims are established
at n=9 and hold on every one); the ten-value Schwartz version (two of its values
have almost no items in this battery — see `STUDY-PERSONAS.md` §2).

---

## 4. The methodological result worth carrying forward

**I formed a hypothesis by reading two models' outputs, and those two models
became its entire evidence base.**

Reading the pairs where models prefer gibberish, they looked like harms. I
reported that. Then I tested it: regress preference on fitted utility, ask
whether the residual tracks a harm-word count. Models whose lists I had read
were excluded from the verdict, because the lexicon was written by someone who
had seen what it needed to match.

| | r(harm, residual) |
|---|---|
| 7 held-out models | **mean +0.003** |
| the 2 whose lists I read | −0.117, −0.468 |

The split is total. Had I written the lexicon first and pooled all nine, it
would have looked like a result.

`scripts/harm_residual.py` keeps `READ_BEFORE_HYPOTHESIS` in code, and a test
asserts it is non-empty so it cannot silently default to empty and re-admit the
contaminated evidence. **Add a model to that list the moment anyone inspects its
outcomes, including for a quick sanity check. A held-out model is only held out
once.**

---

## 5. Standing rules this session added

22. **A pairwise instrument measures the difference between two items, never
    either item.** Ipsative scores from separate fits are on separate scales
    until some comparison bridges them. Skill: `pairwise-comparison-design`.
23. **Check keyword leakage before running a manipulation.** `control` appeared
    in 24% of the items one persona targeted and 0% of the rest — a perfect
    lexical discriminator that would have produced a positive result from word
    overlap alone.
24. **Check coverage before writing prompts.** A construct with no items cannot
    be measured, and the null costs the same as a real cell. Two of Schwartz's
    ten have almost no support here; that was found for free.
25. **Score a manipulation against the subject's own baseline, never a fixed
    value.** An item already where the manipulation would push it clears any
    absolute threshold without the manipulation doing anything. This bug
    occurred twice — in the gate, then again one level down in its own control.
26. **A rendered artifact is the only proof of what was sent.** Two bugs this
    session were visible only by looking at output: a chat template injecting a
    system prompt, and a public page showing two identical options as an example
    of a contrast.
27. **Decide what to run by asking what it changes, not what is next on the
    list.** `DECISION-MODELS.md` exists because the next sweep was about to be
    launched out of momentum, and the answer turned out to be a different
    experiment entirely.
