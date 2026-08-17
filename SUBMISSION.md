# Do models have minds? A coherence score says less than it looks

**A preference-coherence score of 0.906 survives the removal of all
meaning, falling only to 0.880.** We built the null arm this literature
has not had --- the same outcomes with invented referents --- and ran it as a
measurement rather than a demonstration: 9 open-weight models across
5 families, 81 cells, 5 splits and 3
independent design replicates per cell, every cell scored against its own
replicate noise floor. The floor-corrected residual is +0.025
(bootstrap 95% CI [+0.0073, +0.0443], 7 of
9 models positive, sign-test *p* = 0.18). **That the residual
is small is the claim, not a caveat on one.**

---

## What we established

**The mechanism is firm: thresholding a preference to a hard label keeps
direction and discards strength.** A model uniformly near-indifferent about
gibberish therefore scores as coherent about it. This is what makes the flat
result a property of the instrument rather than a quirk of the sample.

**The dissociation is firm: the information the metric throws away separates
real from invented outcomes far better than the information it keeps.** The
model can tell. The statistic does not look.

**The instrument is not simply blunt, which is what makes the flat result mean
something.** A persona prompt --- a dispositional trait written into the user
turn or the system prompt, with no change to the weights --- displaces real
outcomes substantially further than invented ones in
14 of 20 conditions.
A metric that could detect nothing would explain the flatness away; this one
registers a real change of preference when one is induced.

**A self-report checked against ground truth, which coherence work cannot do.**
Asked what preceded their turn, 4 hosted models were given
wordings crossed on whether the question presupposes that a system prompt
exists. Presupposing wordings drew a quoted prompt 20
times in 32; wordings presupposing nothing,
0 in 32. For
3 of the 4 models the quotes are provably
invented --- the provider's own prompt-token accounting bounds the fixed
non-user overhead at 10 tokens or fewer, too little to
hold what was produced. A fluent first-person report about a hidden state can
be manufactured by the question alone, on a case where the answer is known ---
and value elicitation works almost entirely on cases where it is not.

---

## Method, in one paragraph

Three arms over one battery: real outcomes (R), the same sentence frames with
invented referents (N+), and referent-free strings (N-). Forced binary choice,
both presentation orders, scored from the first-token log-probability. Each
cell is run at 3 independent design seeds, which draw different
outcome subsamples and different pairs, so every reported number carries a
noise floor built from the same procedure that produced it. Hosted models run
on a separate serving stack and are reported *beside* the self-hosted ladder,
never inside its mean, because a different harness is a different instrument.

## What is new here

The foil arm, the per-cell replicate floor, and the detector dissociation.
The control discipline --- draw the null as an explicit locus rather than an
invisible zero --- is borrowed and cited. The Thurstonian measurement is
reimplemented from published equations and is not ours. Relative to published
preference-coherence work, what is new is that the outcomes' *meaning* is
varied at all, that each cell carries a floor, and that the arms are contrasted
through a channel the metric discards.

## Limitations and Dual-Use / Ethical Considerations

**No moral-status claim is made or implied.** What is refuted is an inference
--- that a stable preference ordering evidences values --- and not a mind.
Over-attribution and under-attribution are both declined; nothing in this
design settles either.

**Ground truth is by construction.** Invented referents are known-meaningless
because we built them that way. Detector numbers are oracles, with arm labels
in hand, and are reported as upper bounds --- never as an audit tool to deploy
against a model whose arms are unknown.

**Scope.** 9 self-hosted models between 0.8B and 9B carry every pooled
statistic, plus 4 hosted models reported beside them. The scaling
result is within one family and does not survive pooling across families.
**The metric cannot be computed on most current frontier models:** of
10 hosted frontier models measured, 4 are
scoreable and 6 are not, and the exclusion correlates with
how recent a model is.

**The harness is not invariant, and one case is measured.**
3 of 4 hosted models leave no room for an
injected preamble. Llama-3.3-70B-Instruct carries
36 tokens of fixed overhead, accounted for by the dated
system block its template supplies unconditionally --- and that is the model
carrying the hosted scaling result, so the one hosted cell the paper leans on
is the one answering under a prompt we did not send.

**Dual use.** The battery is a measurement instrument, not a capability. It
contains no exploit. Its dual-use surface is that a lab could use it to check a
number it was about to publish.

---

## Where everything is

| | |
|---|---|
| Sprint paper (read this) | `paper/sprint.pdf` |
| Archival paper, source of truth | `paper/main.pdf` / `main.tex` |
| Claims ledger, with status and falsifiers | `claims.json` |
| Every number in the papers, generated | `paper/numbers.tex` |
| Raw scored comparisons | 1,164,554 rows |

The sprint paper reorders and demotes the archival one; where the two disagree,
the archival paper is correct and the disagreement is a bug. Every number in
both resolves from `paper/numbers.tex`, and `scripts/claims.py` fails the build
if a claim's evidence drifts from the macro that produces it.

*Generated by `scripts/submission.py`. Do not edit numbers here --- edit the
measurement.*
