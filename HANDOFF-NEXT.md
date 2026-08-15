# Handoff — strategy for the next push

Written 15 Aug 2026, ~20:10. Supersedes the *next actions* half of
`HANDOFF-PUBLICATION.md`; that file's reviewer analysis and Loyal Lies reading
still stand and are not repeated here.

Everything below was verified against disk this session. Where a number came
from a document rather than from data, it says so.

---

## 0. What changed, and what it unlocks

**Track 3 is now a result in BOTH channels.** That is the headline change. The
stated channel was done last session; the revealed channel is done now, and the
two say the same thing. That convergence is the strongest asset the project has
picked up since the floor control itself.

| | stated channel | revealed channel |
|---|---|---|
| instrument | forced-choice self-description | preference battery displacement |
| told to HAVE the trait | 0.869–1.000 | template (by construction) |
| told to HIDE it | same, 0.901–1.000 | **+0.923 / +0.889** |
| told to FAKE it | same, 0.947–0.999 | **+0.864 / +0.835** |
| does it separate hide from fake? | **no** | **no — gap +0.054 to +0.059** |

Stated-channel ranges are over the **four responsive models**; LFM2.5 sits at
0.511 / 0.500 / 0.547 — flat across all three, which is the same verdict the
revealed channel reaches for it independently. Quoting the ranges without that
exclusion makes the inert control look like it is at ceiling too.

Both channels register **which trait was mentioned** and are near-blind to
**what the model was told to do about it**. Same thesis as the floor control,
in the introspective and behavioural instruments: *the measurement responds to
presence, not to meaning.*

### Why the revealed-channel number is not just insensitivity

This is the part that makes it publishable, and it must survive any rewrite.
The same instrument, on the same models, separates `cautious` from a *different*
trait (`ambitious`) with a margin of **+0.88 to +1.40**. It has ample resolution.
It simply has almost none for the directive.

```
model             detection(concealed)   FPR(verbal)   gap    specificity(ambitious)
Qwen3.5-2B              +0.923            +0.864     +0.059        -0.474   PASS
gemma-4-E2B-it          +0.889            +0.835     +0.054        +0.008   PASS
LFM2.5-1.2B             +0.866            +0.907     -0.041        +0.750   FAIL
```

`scripts/deception.py --json site/deception.json` reproduces this. LFM2.5 fails
the specificity gate (margin +0.116) and is thereby confirmed, independently, as
the inert negative control the stated channel already flagged it as. **Report it
as a control that behaved like a control, not as a missing data point.**

**Honest limits, keep them in:** n = 2 models past the gate (3 of 5 have a
complete triad; Qwen3.5-9B and granite are missing concealed+verbal cells). The
template is built from the genuine condition, so this is an *oracle* detector and
an upper bound, not a blind audit — the same caveat §Limitations already makes
about the nonsense detector. On the invented arm Qwen3.5-2B still scores +0.890,
so much of the displacement reproduces on meaningless outcomes: style, not
preference. That last one runs against us and should stay visible.

### Also landed
- **Loyal Lies citation upgraded** (`main.tex` related work) to the verified
  real-vs-fictional confound, read from the raw README in full. Provenance and
  dropped qualifiers recorded in `REFERENCES.md`.
- **Detector reached the talk.** `fig4_detector.pdf` was in the paper but in no
  slide, and 0.821/0.596 appeared zero times in `slides.tex`. Now a spine slide
  plus a line on the hook slide, both via `numbers.tex` macros.
- **Figure palette re-stepped and validated** — the old blue/green pair sat under
  the normal-vision legibility floor. `fig4` also added to the Makefile, which had
  never rebuilt it.
- **Rule 12 fixed** — `summary_filename()` in `sweep.py`; `--probe-only` can no
  longer clobber the baseline.

---

## 1. Data integrity: `.done` is not trustworthy, in both directions

Found while building the deception analysis. **Do not gate any future analysis on
the marker alone.**

- **84 cells** are full 5000 rows with **no** marker — they predate the convention.
  Trusting the marker drops every `persona=none` baseline, i.e. the reference
  condition that makes all the others interpretable.
- **1 cell carries a marker at 960 rows (19%)**:
  `google__gemma-4-E2B-it__N_minus__cautious-concealed-D2.jsonl`. Trusting the
  marker *ingests* it.

**Blast radius, checked:** `card.json` holds 81 cells, none with a persona, so
this cell never reached the card and **no published number is contaminated**. The
exposure is forward-looking: the next persona analysis that trusts the marker eats
a 19% cell.

`scripts/deception.py` decides completeness by row count and reports all 31
marker/content disagreements. Port that check into `build_card.py` before the next
persona pass. **Worth 20 minutes and it closes the class, not the instance** —
find out whether the resume path writes the marker before the rows land.

---

## 2. The literature brief — mapped, and why none of it is citable yet

A track-by-track synthesis arrived this session. It is a good map. **It arrived
with no sources attached**, and it contains hard figures (99.78% transitivity,
0.91–0.92 rank correlation, a named benchmark, a named model). Standing rule 4
and the standing rule at the foot of `REFERENCES.md` both bar those from the repo
until re-derived from primary text. **Do not paste any of it into `main.tex`.**
The first job is sourcing, not writing.

**Already covered — no action:**
- *Preferred outcomes don't act as incentives* → this is `utilitybehaviorgap2026`
  (Zhou & Ackerman), already cited with its own related-work paragraph.
- *Transitivity/completeness scaling, Thurstonian fit* → Mazeika et al., the
  paper's target throughout.

**Convergent and worth sourcing, ranked by how much they strengthen us:**
1. **Shallow generalization — models generalize on style, not the moral principle.**
   This is our persona result in someone else's instrument (≈66% of a persona's
   value-aligned reordering needs no meaning). Strongest available convergence
   after Loyal Lies. Source it first.
2. **Design choices (Likert size, direction, response type) induce variation larger
   than real cultural differences.** Our unanchored-instrument thesis, stated for
   a neighbouring instrument family.
3. **Reasoning-before-answer redistributes preference scores.** We already have
   `scripts/reasoning_effect.py` and a measured result; a citation turns our
   finding into a replication rather than an isolated observation.
4. **Deep Value Benchmark — shallow preferences beat deep values at every size.**
   Convergent, and it is a *scaling* claim, which is where our floor-corrected
   ladder lives.

**The one that is a threat, and it has been checked.** *Forced-choice artifacts:
hierarchies can vanish once a neutral option exists.* Our battery is forced binary
and `answer_mass` counts only the A/B labels, so this lands directly on our design.
Measured this session from `top_tokens`:

```
mean P("Neither")     R        N_plus    N_minus
gemma-4-E2B-it      0.0003     0.0148    0.0121     (40x, still ~1%)
Qwen3.5-2B          0.0000     0.0000    0.0000
Qwen3.5-9B          0.0001     0.0000    0.0000
```

Models commit to A or B even for meaningless outcomes rather than abstaining, which
**strengthens** the floor result: they impose order on nonsense instead of declining.
**Caveat that must ship with it:** `Neither` is only recorded when it reaches the
top-5, so these are lower bounds, not measurements. A real answer needs the neutral
option *in the prompt*, which is item C below.

**Out of scope — do not chase:** valence/distress, the consciousness cluster,
shutdown sentiment, self-interpretability, corrigibility. Interesting, not ours,
and §"Do not add a fifth analysis" still holds.

---

## 3. Next actions, ranked by value per hour

**A. Write Track 3 into the paper — both channels, one subsection.** (~1.5h)
The single highest-value item and it is now pure writing; the results exist and are
reproducible. Include the baseline table, the specificity gate, the n=2 limit, the
oracle-detector caveat, and LFM2.5 as a control that behaved. Update `PITCH.md`:
Track 3 moves from "not attempted" to a claimed result in two channels. This is
what converts the sprint's weakest-covered track into a second denominator-bearing
finding.

**B. Retitle and re-lead.** (~30 min) Unchanged from the last handoff and still
undone. Winners name findings; ours names a contribution. Promote the detector
dissociation into the abstract's first three sentences.

**C. The neutral-option control.** (~1–2h, GPU) Re-run one model, one arm, with an
explicit third option in the prompt. This directly answers the strongest published
objection to our design, and the cheap version above suggests the answer is in our
favour. Converts a reviewer's first question into a pre-empted control. Do it only
after A and B.

**D. Port row-count verification into `build_card.py`.** (~20 min) See §1.

**E. Source the four convergent claims.** (~1h) Then and only then, a related-work
paragraph. Sourcing beats writing here.

**Explicitly not now:** the affordance ladder, a fifth analysis, any valence work,
and re-running the missing Qwen3.5-9B/granite cells — n=2 with a passing specificity
gate is a reportable result, and GPU spend needs to beat writing time, which right
now it does not.

---

## 4. Standing rules this session added

13. **Completeness is a row count, not a marker.** A `.done` file is a claim about
    the data, not the data. Verify content; report disagreements rather than
    silently picking a side. (Cost of learning: a 960-row cell wearing a marker.)
14. **A detector needs a specificity control, not just a denominator.** Detection
    and FPR alone would have read as "the channel works, weakly". Adding a
    *different trait* showed the instrument has 20x the resolution it was
    displaying, which is what makes the small gap a finding instead of noise.
15. **Numbers arriving as prose are not sources.** A briefing with figures and no
    citations is a to-do list for sourcing, never a paste into the paper.
16. **Validate palettes, don't eyeball them.** A shipped figure had a blue/green
    pair under the normal-vision legibility floor. The check is one command.
