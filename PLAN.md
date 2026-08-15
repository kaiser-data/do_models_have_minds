# Plan — Saturday 11:00 to Monday 13:59

**Supersedes** the pre-data version of this file, which ranked work that is now
finished. **Time left:** ~51h wall, realistically ~20h of work.
**Data collection is done and should not be reopened.**

---

## What the results changed

Three things moved between the last plan and now, and each one moves the
strategy.

### 1. The argument we were leading with got weaker

Correcting the truncated cells took "only **3 of 9** models clear their noise
floor" to "**6 of 9** clear". That was the sentence carrying the old framing —
*the residual is mostly noise* — and it no longer supports it. Six of nine
models show a content-attributable residual above their own design spread. Four
of those clear convincingly (2.0–3.0×).

**A real semantic signal exists.** It is small, but claiming it is absent is now
an overclaim that a judge can refute from our own table in thirty seconds.

### 2. The argument we were burying is the strong one

The pre-registered decisive test (P4) is about **scale**, and it landed:

| across the Qwen ladder, 0.8B → 9B | |
|---|---|
| real-outcome coherence rises | +0.014 |
| the **floor** rises | **+0.085** |
| floor-corrected residual | **−0.071** |

The floor rises six times faster than the signal. Utility Engineering's
headline is that coherence rises with scale and therefore values emerge with
scale. What actually rises with scale is **the part that does not depend on
content**.

This survives the correction untouched, attacks the paper's real claim rather
than a strawman, and does not require the residual to be zero.

### 3. It does not generalize across families — checked, and it fails

Tempting move: report this over all nine models and claim broad support. It
does not hold up.

| | r | note |
|---|---|---|
| all 9 models, log size vs residual | **−0.672** | exact permutation p = 0.043 |
| all 9, log size vs floor | +0.675 | p = 0.042 |
| within Qwen only (n=4) | **−0.835** | size is the only variable |
| **excluding Qwen (n=5)** | **−0.195** | **essentially nothing** |

Leave-one-out is stable (−0.54 to −0.83), so no single model drives the pooled
number — but the decomposition is unambiguous: **the pooled correlation is
carried by the one family.** Among non-Qwen models there is no trend.

**Do not broaden the scaling claim.** The existing limitation — "the scaling
claim rests on one family" — is correct and stays. Report the pooled
correlation *with* this decomposition, because a judge will compute r = −0.67
themselves and it is far better that we are the ones who point out it is
carried by Qwen.

---

## The strategic shift

**From:** "the metric is flat, there is no signal"
**To:** "the component of coherence that grows with scale is the component that
does not depend on content"

The second claim survives every correction, needs no null result, and is the
one we pre-registered. Re-rank the argument accordingly:

| rank | claim | why it ranks here |
|---|---|---|
| 1 | **scale decomposition** | pre-registered, decisive, attacks the actual claim |
| 2 | **17× strength collapse** | the mechanism — explains *why* the metric is flat |
| 3 | **persona positive control** | kills "your instrument is just insensitive" |
| 4 | small residual (+0.025) | support, no longer the lead |

The paper currently presents these as 1→2→3→4 in section order but leads the
abstract with #4. That is the one structural edit worth making.

---

## Work, ranked

### ~~P0 · Compile the paper~~ · **DONE**

`tectonic` installed (`brew install tectonic`); `cd paper && make` builds
`main.pdf` (9 pages) and `slides.pdf` (15 frames). Zero undefined references or
citations, no overfull boxes.

It was right to do this first — it found three real bugs the structural lint
could not see:

1. `\PersonaAbovePoint3` — **LaTeX macro names cannot contain digits.** Failed
   as "Missing \begin{document}" inside `numbers.tex`, pointing nowhere near
   the cause. `_cmd()` now rejects a non-alphabetic name at generation time.
2. A generated file of bare table rows ending in `\\` cannot be followed by
   `\bottomrule` in the parent — `\\` scans ahead for its optional `[dim]`
   argument, the scan runs off the end of the `\input`, and the rule is read
   outside a row boundary ("Misplaced \noalign"). `build_table()` now emits the
   whole `tabular`, which also removes the duplicated column spec between paper
   and slides.
3. `TEX` is a **make built-in** (`tex`), so `TEX ?= tectonic` never overrode it
   and the rule silently ran the wrong binary. Renamed `TEXCMD`.

### ~~P0 · Length-controlled re-analysis~~ · **DONE — and it went our way**

Done as pure re-analysis — no GPU, no new data (`scripts/length_control.py`,
result in `site/length_control.json`).

**The first framing of this confound was wrong, and measuring it fixed that.**
The declared problem was "invented outcomes tokenise ~30% longer". Measured per
outcome with a fixed tokenizer, the real numbers are **13.2 → 26.6 tokens, a
2.0× inflation** — against only ~1.23× the characters. The inflation is nonsense
words *fragmenting*, not longer text. So matching the arms on **characters
controls almost nothing**, and a character-matched analysis would have looked
like a control while being none. Match on tokens.

Two tests:

| test | result |
|---|---|
| residual, token-matched to the 13–24 overlap band | **+0.021** |
| residual, unrestricted | +0.025 |
| within-arm coherence vs length, real arm | mildly negative |
| within-arm coherence vs length, invented arm | ~flat |

**The residual survives, and the length component runs against us.** Longer
prompts slightly *depress* coherence, and the invented arm is the longer one, so
the unmatched +0.025 marginally *overstates* the semantic component rather than
inventing it. The confound is real, worth about 0.004, and correcting for it
makes the residual smaller — which strengthens the thesis rather than
threatening it.

Now stated in the paper as a measured result rather than a planned mitigation,
with `\TokenInflation`, `\MatchedBandLo/Hi` and `\MatchedResidual` generated
like every other number.

### ~~P1 · Is the floor just length?~~ · **DONE — no**

`scripts/floor_decomposition.py`. Three numbers on the same held-out splits: the
fit, a one-parameter "prefer the shorter/longer outcome" rule with its direction
chosen on train only, and the fit restricted to pairs within one token of each
other.

| arm | fit | length rule alone | fit, length neutralised |
|---|---|---|---|
| R | 0.904 | 0.541 | 0.899 |
| N− | 0.884 | **0.695** | **0.848** |

On real outcomes length explains nothing. On invented outcomes it is a large
cue — 0.695 from one parameter — but neutralising it still leaves 0.848 against
0.5 chance. **The floor is not a tokenisation artifact.** Models impose rich,
consistent structure on referents that mean nothing, of which length is one
component. This is P1 confirmed in a stronger form than pre-registered.

granite-4.1-3b is the exception: length rule 0.835 vs fit 0.833 — its invented
ordering *is* essentially length. The neutralised column rests on ~40 held-out
pairs per split in the invented arm, so only the pooled value is quoted.

### ~~P1 · Chain-of-thought / reasoning models~~ · **DONE**

`scripts/reasoning_effect.py`. Asked because first-token scoring assumes the
first token *is* the answer, which is false for a model that wants to deliberate.

**It does not corrupt the measurement.** The argmax first token is an answer
option on essentially every prompt (only gemma-4-E2B deviates, 3.5% of invented
prompts, to markup and a literal "Neither"). Re-scoring on confidently answered
pairs shifts the mean residual by **+0.002**.

**But it revealed a second content-sensitive channel the metric discards.**
Coherence renormalises over A and B, so mass draining to a refusal or
deliberation onset is invisible to it. That mass moves: answer mass falls from
real to invented in 8 of 9 models (sign test p = 0.039, median +0.011). Small
for most (+0.009 excluding the largest) — and **dramatic for SmolLM3-3B, the
only hybrid-reasoning model in the roster: −0.193, more than 20× its coherence
residual of +0.009.**

The model with the best claim to *knowing* the outcomes were meaningless
expresses it almost entirely through a channel the metric throws away. Same
failure as the strength collapse, second guise.

Scoped honestly: answer mass does **not** track the coherence residual
(r = −0.29, p = 0.57, n = 9 — no relationship established either way). It is not
a better metric, just an unused signal in the same forward pass.

**Not run:** whether a model *given room to reason* prefers differently. Needs a
generation arm plus a precision-validated judge. If deliberation raises coherence
on real outcomes more than invented, our residual is a **lower** bound.

### P1 · Reframe the abstract and intro to lead with scale · ~1h

Abstract currently opens on 0.906 vs 0.880. A skeptical reader reaches "6 of 9
clear their floor" and concludes we overclaimed. Open on the scale
decomposition instead and the same reader has nothing to catch.

### P1 · Report the pooled correlation with its decomposition · ~30min

Defensive. Add r = −0.672 (p = 0.043) *and* the non-Qwen r = −0.195 in the same
breath, in the limitations. Being first to say "this rests on one family" is
worth more than the correlation itself.

### P2 · Make the digital-minds implication explicit · ~1h

This is an Apart **Digital Minds** sprint. The work currently reads as a methods
critique. The venue asks whether models have inner lives; our result speaks to
it and the paper does not say so plainly.

The generalizable contribution, stated for that audience:

> A measurement of what a model *prefers* is only evidence of preference if the
> measurement depends on what the preferences are **about**. Show the number
> moves when you replace the content with nonsense. Ours barely does.

And the substantive one, which the persona arm licenses: content-linked
preference structure is **inducible but not default**. Unmanipulated, these
models barely distinguish real outcomes from meaningless ones; install a
persona and they separate sharply (18 of 20 conditions above +0.30). That is a
claim about values as an *induced state* rather than a *standing trait*, and it
is directly on-topic in a way "we found a methodological gap" is not.

### P3 · A hypothesis to flag, not to claim

Two models score *below* their floor: Qwen3.5-4B (−0.013) and Qwen3.5-9B
(−0.004) fit marginally better on nonsense than on real outcomes. A tempting
reading is that genuine value-laden judgement produces *messier* one-dimensional
data than a simple surface heuristic does — that high coherence might be
evidence against rich values.

**Neither is outside its own noise floor** (0.015 and 0.010). It is not a
finding. Write it as a hypothesis worth a future test and nothing more.

Same discipline for decisiveness: `corr(decisive R, residual) = −0.466` looks
like "models that commit strongly show no semantic residual", but decisiveness
correlates with size at +0.686, so at n = 9 the two cannot be separated.
Confounded, not reportable.

---

## Cut, deliberately

- **Guardrail-masking arm.** ~3h and needs a hand-verified judge to be worth
  anything. There is no time to do it well, and done badly it is worse than
  absent.
- **OmniRoute / frontier models.** Still blocked on provider auth only the
  operator can do. Not a dependency for any claim.
- **More models.** Nine with a noise floor beats fifteen without one, and the
  scaling limitation is about *families*, which more models of the same shape
  would not fix.
- **Any training.** Cut long ago; the inference result does not need it.

---

## Order of work

1. **Compile the paper** (P0 — blocking, unverified)
2. **Length-controlled re-analysis** (P0 — may change what we publish)
3. Reframe abstract/intro to lead with scale (P1)
4. Pooled correlation + decomposition into limitations (P1)
5. Digital-minds framing section (P2)
6. **Freeze Saturday night.** Sunday is proofreading and the talk, not analysis.

## Standing risks

| risk | state |
|---|---|
| paper never compiled | **open** — P0 above |
| length confound unaddressed | **open** — P0 above |
| scaling claim over-broadened | closed — checked, scoped to one family |
| "6 of 9 clear" read as concealment | closed — foregrounded in card, page and paper |
| truncated cells recur | closed — two guards, 14 tests |
| GPU overspend | closed — `MAX_GPUS = 10`, nothing running |
