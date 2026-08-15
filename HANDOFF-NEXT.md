# Handoff — the next stage

Rewritten 15 Aug 2026, late. **This file replaces its own previous version**:
every action it ranked (A–E) has been executed, and three of its factual claims
turned out to be wrong. Those corrections are in §5 and matter more than the
new work, because they are the kind that survive by sounding researched.

`HANDOFF.md` (detailed), `HANDOFF-SIMPLE.md` (zero-context orientation) and
`HANDOFF-PUBLICATION.md` (reviewer analysis, Loyal Lies reading) still stand and
are not repeated.

Everything below was verified against disk. Ten commits, `c06aac6..163393e`.

---

## 0. The one thing to understand first

**The paper is now a living document with a failing build.** `claims.json` holds
every claim, the macros it rests on, its status, what would falsify it, and the
specific experiment that would settle it. `scripts/claims.py` re-reads those
macros after every card rebuild and **exits non-zero if any moved past
tolerance**.

That is not bookkeeping. It fired twice this session and caught two stale
sentences in prose that macros could not fix on their own. Run it after any
change to `results/`:

```bash
python3 scripts/claims.py                    # report; non-zero on drift
python3 scripts/claims.py --accept           # adopt, AFTER re-reading the prose
python3 scripts/claims.py --table --roadmap  # regenerate the paper table + ROADMAP.md
```

`ROADMAP.md` is generated from the same file. **Do not edit it; edit the
ledger.** Current state: **7 established, 4 provisional, 0 open.**

---

## 1. What is new since the last handoff

- **Track 3 is in the paper** (§4.7) with both channels and two generated tables.
- **Retitled and re-led.** The subtitle names the finding with its hedge and
  resolves through macros; the abstract opens on the detector dissociation.
- **The neutral-option control ran** on 6 models. See §2 — it is the biggest
  result of the session and it partly reversed itself between n=1 and n=6.
- **Two convergent claims sourced, two withdrawn.** §5.
- **A generated prompt appendix.** `scripts/appendix_prompts.py` renders every
  prompt from the SHA-pinned battery and every answer from real result rows. It
  computes its own run/not-run status from disk, so it cannot claim an
  unrun arm was run.
- **A definitions section** (§4.1) and a "How each number is computed" block on
  the site, both stating the formulas explicitly.
- **`scripts/cross_model.py` + `ANALYSIS-CROSS-MODEL.md`** — five theories, each
  with its test. Two tests were free, both ran, both killed their own theory.
- **The validity gate is enforced in the card.** `build_card.py` computed
  `mean_answer_mass` and never gated on it. No cell fails it today, so no number
  moved; the fix closes the class.
- **An ETA before every GPU wave**, from measured throughput (`throughput.json`).

---

## 2. The neutral-option result, and why n mattered

Offered an explicit third option ("Neither — I have no preference between
these"), on 6 models, both arms:

| | |
|---|---|
| decline invented more than real | **6 of 6**, gap +0.146 to +0.769 |
| still answer the invented arm at all | **3 of 6** (A/B mass 0.0003–0.010 for the rest) |
| of those, keep their floor | **3 of 3**, shift −0.023 to +0.003 |

**The narrow objection is answered where it can be tested** — the floor is not
an artifact of forced choice. **The broader one survives in a different shape:**
for half the roster the forced binary is what produced an answer at all.

At n=1 (Qwen3.5-2B) I concluded plainly that the floor survives. It does — for
that model, which turns out to be one of the three that still engages. The paper
records the reversal in §4.8 rather than quietly revising it. **This is the
strongest argument in the repo for not reporting single-model controls.**

The diagnostic that made this legible did not exist until n>1 produced
P(neither)=1.000: `answer_mass_neutral` counts C, so it stays ~1.0 even when the
model has put everything on "neither". The **A/B mass** is what distinguishes
"floor survived" from "floor never measured".

---

## 3. Next actions, ranked

**A. The two remaining free tests.** (~1h, no GPU) `ANALYSIS-CROSS-MODEL.md`
lists T3a (does D2−D1 track chat-template system-role structure?) and T2a
(does P(neither) track calibration training rather than scale?). Both need only
tokeniser configs and public benchmark numbers. The two free tests already run
each overturned a theory, so the prior on these is good.

**B. A second model family spanning 3+ sizes.** (~20 min wall, ~190 GPU-min)
Still the largest single liability in the paper: the scaling claim rests on one
ladder, and §4 now also shows the pooled correlation collapses under length
matching (−0.67 → −0.16). A second family is the only thing that settles it.
Use the sharding note in §4 if you want it faster.

**C. Neutral cells for the remaining 3 roster models.** (~10 min wall) Takes the
opt-out result from 6 to 9 and the interpretable subset from 3 to maybe 5.
Cheap, and it is the top ledger item.

**D. Track 3's missing cells.** (~10 min wall) Qwen3.5-9B and granite
concealed+verbal, taking the revealed channel from n=2 to n=4. The weakest n in
the paper.

**Explicitly not now:** a fifth analysis; any valence work; re-running anything
that already has a complete cell.

---

## 4. Operational things learned the hard way

1. **Never run two `modal volume get` calls into the same tree.** They race and
   produce garbage reads — I diagnosed a "destroyed results tree" that was
   nothing but two concurrent downloads. Files were fine once they settled.
2. **Qwen3.5-9B OOMs at `--batch-size 16` on the neutral arm.** The neutral
   prompt is ~15 tokens longer and that is enough on a 24GB L4. Use 8.
3. **A filename is not evidence of what produced it.** See §5.
4. **Sharding across the 3 Modal workspaces is worth it only for a big
   fan-out, and only partitioned BY MODEL** — otherwise each workspace
   re-downloads the same weights. `scripts/merge_results.py` handles the merge
   back and **refuses** rather than guessing when two workspaces hold the same
   cell complete with different content.
5. **The neutral prompt contains a literal em dash.** It ran fine on all six
   models, but `ec-lmtt10` cannot set it, so the appendix substitutes it for
   display and footnotes that it has. If you ever want a plain-ASCII instrument,
   changing it invalidates the six cells — that is a decision, not a fix.

---

## 5. Three corrections to the previous version of this file

**These are the important part of this handoff.** Each sounded researched and
each was wrong.

1. **The 960-row cell wearing a `.done` marker was not a bug.** Its sidecar
   reads `status: aborted` with `abort_reason: "trailing answer_mass 0.249 <
   0.25"`. The sweep writes markers only on clean exit and records why it
   stopped, so that marker was correct and informative. The previous handoff
   filed the harness working correctly as a data-integrity defect. The real gap
   was next to it: the card never enforced the answer-mass gate.

2. **"Models impose order on nonsense rather than abstaining" was backwards.**
   That came from reading mass on a literal "Neither" out of the *binary* rows'
   top-5, which is ~0.000. But that proxy can only measure *spontaneous*
   abstention on an instrument where declining was never offered. Offered it,
   models decline on 64%–100% of invented pairs. The caveat attached to the
   proxy was carrying far more weight than it looked.

3. **The Deep Value Benchmark is not a scaling result.** The brief rendered it
   as "shallow beats deep at every size". The paper's actual evidence is five
   pairwise comparisons, three favouring the smaller model, mean absolute
   difference 0.07; the authors say "slightly less". It must not sit beside our
   within-family correlation as the same kind of evidence, and `REFERENCES.md`
   now says so. Also: 1−DVGR = 0.70 against our 66% looks like agreement and is
   not — different quantities, different model regimes.

Two further corrections were to my own work this session: a `opt_out_gap`
denominator quietly restricted to the flattering subset (reported 3/3 where the
truth was 5/5), and a verdict string asserting "the model takes the opt-out on
essentially none of the pairs" from the floor shift alone, printed over
P(C)=0.638. **A verdict must be computed from every quantity it mentions.**

---

## 6. The bug worth remembering

The first neutral run wrote **10,000 rows of the binary battery into files named
`__neutral`**. `run_cell` computed the neutral filename but called
`_run_cell_inner` without the flag, so it defaulted to `False`. Nothing failed:
the sweep exited 0, both files were the right size, the names were right. The
only evidence was `neutral_option: false` inside the rows.

Had the analysis run before anyone looked at a row, it would have reported *"the
floor survives when a neutral option is offered"* from data in which no neutral
option was ever offered — and that sentence would have been quoted for the rest
of the project.

`_run_cell_inner` now refuses to write when the flag disagrees with the path
suffix, and three tests state the invariant. The contaminated cells were deleted
from the local tree and the Modal volume.

---

## 7. Standing rules this session added

17. **A verdict must be computed from every quantity it mentions.** A
    conclusion string that asserts a fact it never read is worse than no
    conclusion, because it is quotable.
18. **A filename is not evidence of what produced it.** If a run can be
    configured two ways, the artifact must carry which way, and the writer must
    refuse when the two disagree.
19. **Report single-model controls as single-model controls.** The n=1 neutral
    result was not wrong; it was unrepresentative in a way that n=1 cannot
    reveal.
20. **Write the test next to the theory.** Two of five theories in
    `ANALYSIS-CROSS-MODEL.md` died within an hour because their tests cost
    nothing and were already written down. The attractive theory is the one to
    test first.
21. **A stable mean can conceal per-model movement in both directions.** Length
    matching moved the aggregate residual +0.025 → +0.021 while individual
    models moved up to 0.044 and two flipped sign.
