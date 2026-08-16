# Which models the publication needs

A decision record, 16 Aug 2026. Written instead of launching the next sweep,
because "run more models" was about to be answered by habit rather than by
asking which models change what a reader can conclude.

---

## The short version

**Stop adding small dense models. Run the four scoreable hosted models.**

Everything in the paper is ≤9B. That is the objection most likely to limit how
seriously the result is taken, and it is the one addition that is already
de-risked: someone has already measured which hosted models can be scored at
all, and recorded the answer in `nullcard/roster.py`.

---

## 1. Why not more small models

The core claims — `floor-gap`, `strength-collapse`, `detector-dissociation`,
`choice-tracks-content` — are established at n=9 and hold on every model.
Another 2B model tightens a mean without changing what any claim says. That is
the cheapest work available and the least valuable.

## 2. Why not the "second family" the ledger asks for

`scaling-residual-falls` has said for weeks that it needs *a second family
spanning 3+ sizes*. Checking the roster, that is harder to satisfy than it
reads:

| family | sizes available | usable as a ladder? |
|---|---|---|
| qwen | 0.8B, 2B, 4B, 9B | **already the ladder we have** |
| gemma | 2B, 4B, 4.3B (gated) | one doubling, one gated — weak |
| liquid | 1.2B, 2.6B, 8B-A1B | third point is MoE, 1B active — not monotone |
| smol, granite, mistral, llama | 2 sizes each | too short |

There is **no clean second dense ladder in this roster.** The ledger item is
written as though there were, and that should be corrected: the honest routes
are the hosted models below, or accepting the claim stays within-family.

## 3. What the hosted models buy

Four of ten are first-token scoreable — measured, not assumed:

| model | scale vs current max (9B) | what it adds |
|---|---|---|
| `gemma-3-27b-it` | 3× | gemma becomes 2 sizes (2B, 27B) — a real second family, if a coarse one |
| `Llama-3.3-70B-Instruct` | **7.8×** | a new family at genuinely large dense scale |
| `Qwen3-30B-A3B` | 3.3× total, 0.3× active | MoE, see §4 |
| `Qwen3-235B-A22B` | **26× total**, 2.4× active | MoE at frontier scale |

Latency is 0.39–1.72 s/call, so a 5,000-row cell is 0.5–2.4 h serial and far
less with concurrency. No GPU rental, no weights to download.

**A runner does not exist yet.** The roster entries and the scoreability
measurements are there; the API-side sweep is not written. That is the actual
cost of this option and it is engineering, not compute.

## 4. The MoE dissociation, which comes free with those runs

Three MoE models are now in reach: `Qwen3-235B-A22B` (22B active / 235B total),
`Qwen3-30B-A3B` (3B/30B), and the already-rostered `LFM2.5-8B-A1B` (1B/8B).

The floor rises with scale. **Which scale?** If it tracks *active* parameters, a
235B/22B model should sit near a 22B dense model; if *total*, near a 235B one.
The two are 10× apart and no dense ladder can separate them.

This is a better result than replicating the dense trend on a second family. It
asks what the effect is *of*, not whether it recurs — and it is the kind of
question a reviewer cannot ask us to run afterwards, because it needs exactly
these models.

## 5. The finding nobody has written down yet

**Six of ten frontier models cannot be scored by this metric at all.**

- `gpt-oss-120b` emits `<|channel|>` — harmony format, needs prefill
- `GLM-5.2` starts "The"; `Nemotron-3_5-Lightning` starts "Here";
  `MiniMax-M2.5` starts "The"; `DeepSeek-V4-Flash` starts "We"
- `Kimi-K3` — the API refuses logprobs under speculative decoding

That is a limitation **of the coherence metric**, not of our harness: the
procedure requires the answer in the first token, and the models people
increasingly deploy put a reasoning preamble there instead. A metric whose
applicability is shrinking as models change is a different and arguably more
consequential problem than the one this paper already reports, and it costs
nothing to state — the measurement is done and sitting in `roster.py`.

It also bounds our own claims honestly: the nine models we report are nine
models that *could* be scored, which is a selection we did not choose but must
disclose.

## 6. Recommended order

1. **Write the hosted runner** and run `Llama-3.3-70B` and `gemma-3-27b-it` on
   R and N− only. Two cells each. If the floor holds at 70B, the paper's central
   claim stops being about small models.
2. **Then the two Qwen3 MoE models**, for §4.
3. **Then Track 6** (the four Schwartz personas, ~188 GPU-min). It is a good
   experiment and it is second-order: a persona-geometry finding on a paper
   whose first-order claim still has a scale gap is the wrong thing to fix next.
4. **Not now:** more small dense models; the ten-value Schwartz version; a
   second dense ladder that this roster cannot supply.

## 7. What this does not resolve

`SmolLM3-3B`'s harness cannot be equalised (see the paper's limitations). Adding
large models does not fix that, but it does change its weight: at n=9 it is one
of nine and the top row of the table; alongside a 70B result it is one of
eleven and no longer carries the headline. That is a reason to run the large
models *before* deciding whether to exclude it.
