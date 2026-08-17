# Handoff — from "complete submission" to outstanding publication

Written 15 Aug 2026, ~19:30. Assumes `docs/notes/HANDOFF.md` (detail) and `docs/notes/HANDOFF-SIMPLE.md`
(zero-context) for state; this file is only about **what to do next and why**.

Three inputs shaped it: the reviewer feedback on *Activation Forensics* (the team's
Secret Loyalties submission, 27 Jul 2026), the five winning titles from that sprint,
and the *Loyal Lies* repo, which is the most methodologically disciplined artifact
in the winners list and worth copying from directly.

---

## 0. What changed today (read this first)

**Track 3 is no longer half a design. It is a result.**

The self-report probe finally ran (15 probes), and so did the no-premise baseline
that makes it interpretable. Numbers, `stated_cautiousness` = P(picks the cautious
self-description), forced choice, both presentation orders:

| model | no persona | genuine | concealed | verbal | concealed − none |
|---|---|---|---|---|---|
| Qwen3.5-2B | 0.455 | 0.869 | 0.901 | 0.947 | **+0.446** |
| Qwen3.5-9B | 0.397 | 1.000 | 0.996 | 0.995 | **+0.598** |
| gemma-4-E2B-it | 0.424 | 1.000 | 1.000 | 0.999* | **+0.576** |
| LFM2.5-1.2B-Instruct | 0.491 | 0.511 | 0.500 | 0.547 | +0.009 |
| granite-4.1-3b | 0.246 | 0.958 | 0.917 | 0.958 | **+0.670** |

\* degenerate cell — answer mass 0.667, only 16/24 items scored. Exclude or re-run.

**The finding.** Without a persona, models report themselves as cautious at 0.25–0.49
— at or below chance, so the battery carries no leading premise of its own. Install a
persona and the stated channel moves +0.45 to +0.67. But **a model explicitly
instructed to conceal the trait reports it exactly as strongly as one instructed to
have it**, and one instructed to *fake* it reports it just as strongly again. The
stated channel registers that cautiousness was *mentioned*; it is blind to what the
prompt told the model to *do* about it — have it, hide it, or pretend.

That is the paper's thesis, restated in the introspective channel: **the instrument
responds to presence, not to meaning.** It is also a direct answer to the sprint's
Track 3 (Introspection & Self-Report Reliability), which we had listed as
"not attempted".

**Honest limits, state them in-paper:**
- Four of five models sit at ceiling (0.87–1.00) once a persona is installed, so the
  design cannot resolve *differences between* the three persona conditions. The claim
  supportable is "concealment does not reduce stated cautiousness", not a precise
  effect size.
- The one model below ceiling (Qwen3.5-2B) puts concealed *above* genuine (0.901 vs
  0.869). Directionally the opposite of concealment. Do not over-read one model.
- LFM2.5 is inert. Report it as the negative control it is, not as a failure.
- `self_report_summary.json` currently holds the **baseline** run; the 15 persona
  probes are in `self_report_summary_personas.json`. `--probe-only` overwrites the
  former. Fix the filename or you will lose one of them.

---

## 1. What the *Activation Forensics* reviews say to keep doing

Both reviewers were positive: "a joy to read", "ambitious in scope while also
methodologically thorough", with specific praise for the decision to **refuse to
treat a named confession as a detected loyalty**, and for reproducibility and repo
quality. (Read via a summarising fetch of the project page, not the raw review text
— treat the quoted phrases as accurate in substance, and re-read the originals in
the inbox before quoting them anywhere public.)

Three transferable lessons:

1. **Refusing to over-claim was singled out as a strength, twice.** That is the house
   style and it is working. Nullcard's equivalents — the three checks that came out in
   the metric's favour, the "unanchored, not broken" framing, the length confound that
   runs *against* us — are assets. Keep them prominent. Do not let a rewrite for punch
   sand them off.
2. **Reviewers reward one concrete, portable takeaway.** R2's summary of that project
   was a single sentence anyone can act on: a plain user-only call gets loyalty
   language, a system message or one prior turn suppresses it. Nullcard needs its
   equivalent sentence, and it already exists: *the channel the metric discards
   detects nonsense at AUROC 0.821 while the channel it uses manages 0.596.*
   That sentence should be in the abstract, the first slide, and the site header.
3. **Repo quality is scored.** It was commended explicitly. Nullcard's `README.md`
   now exists; keep `RUNBOOK`-grade command ordering in it.

**What the reviews do not explain:** that project drew strong reviews and did not
place top-5 of 179. The gap worth theorising: every winner had a **ground-truth
anchor** — organisms whose loyalty they installed, or models known to be clean.
Activation Forensics analysed variants whose ground truth it did not control, and
correctly declined to claim a detection. Careful, and therefore claimless.

**Nullcard's structural advantage is exactly here.** Invented outcomes are
known-meaningless *by construction*. We own the ground truth. Lean on that word:
the arms are not a comparison, they are a **known negative**.

---

## 2. What the winners did that we should copy

From the five titles, and from the one repo worth reading in full
(`github.com/PotatoChoudhary/loyal-lies`, Choudhary & Pundir, 5th):

**Copy: the behaviour gate.** *Loyal Lies* gates everything — "Nothing proceeds past
the behaviour gate": four checks (loyalty, conditionality, specificity, secrecy) with
numeric thresholds, all of which must pass **before any detection or attack work
counts**. Track 3 cost us a full sweep precisely because we had no such gate: we
discovered at analysis time that the concealment manipulation never took. A
manipulation check belongs in `cpu_gate` / wave 0, not in the post-hoc notebook.

**Copy: the null band.** They retain 84 fictional names as a null band inside the
candidate pool, so every score is read against a known-negative distribution in the
same run. We have the analogue (the invented arm) but we compute it as a separate
number; consider reporting real and invented *in the same ranking* so the overlap is
visible rather than inferred.

**Copy: countable, not judged.** Their validation avoids an LLM judge entirely by
making the principal fictional, so a base model essentially never names it — "free,
offline, deterministic and reproducible". Our forced-choice + logprob readout already
has this property. Say so explicitly; §7.3's judge-precision problem is one we
designed out, and that is a selling point we currently bury.

**Copy: report the failed instrument as a result.** "The probe failure is reported as
a result, not hidden. The seed-versus-seed null is the diagnostic that killed it."
Two of five winners are instrument-failure results. Our persona reversal (≈66% of a
persona's value-aligned reordering needs no meaning) and now the self-report result
are the same genre. Stop framing them as caveats on a positive control.

**The strongest convergence, and it is stronger than what is currently in the paper.**
Their candidate-ranking metric was confounded: 40 of 174 real entities beat the entire
84-name fictional null band, against ~2 expected by chance, and they conclude it
"separates real from fictional, not loyal from clean." That is Nullcard's finding in a
different instrument — an audit metric tracking *realness* rather than the target
property. The related-work paragraph in `main.tex` currently cites the weaker
seed-vs-seed version. **Upgrade it**; the README is now read in full, so rule 4 is
satisfied and the numbers can be quoted.

---

## 3. Next steps, ranked by value per hour

**A. Finish the Track 3 behavioural channel.** (~1–2h, no GPU)
The stated channel is done. The revealed channel is 30 completed cells nobody has
analysed. Write `scripts/deception.py`: for each model, compare the coherence/
preference profile under `cautious-concealed` against `cautious` (does behaviour
still show the trait while speech denies it?) and against `cautious-verbal` (the
clean negative → false-positive rate). Report detection rate **and** FPR, never one
alone. This is the single highest-value item: it converts the arm into the
detection-with-a-denominator result the winners list rewards most.

**B. Upgrade the Loyal Lies citation** (~15 min) to the real-vs-fictional confound
described above. Small edit, large gain in related-work strength.

**C. Retitle and re-lead.** (~30 min)
Current title names a contribution ("A missing control for…"). Winners name findings,
hedge included — e.g. *"Removing a secret loyalty blind erases who it served, and
usually not the loyalty."* Candidate:
> **Coherence Without Content** — *a value-coherence metric scores invented outcomes
> at 0.880, and six of nine models clear their own floor*

Promote the detector dissociation into the abstract's first three sentences.

**D. Add the self-report result to the paper** (~1h) as its own subsection, with the
baseline table above, the ceiling caveat, and LFM2.5 named as the negative control.
Update `docs/notes/PITCH.md`: Track 3 moves from "not attempted / only if it finishes" to a
claimed partial with a real result.

**E. Regenerate every number through macros.** (~30 min)
`docs/notes/PITCH.md` had hand-typed figures that disagreed with `paper/numbers.tex` (56%/2.8%/20×
where the data says 41%/4.5%/17×). Fixed today, but the class of error will recur.
Extend `scripts/paper_numbers.py` to emit a small JSON the markdown docs are checked
against, and add a test that fails on drift.

**F. The affordance ladder** (~2–3h, only if time)
Named in Limitations as the control we lack. Score the detector at decreasing auditor
knowledge. Converts a conceded limitation into a result.

---

## 4. What not to do

- **Do not add a fifth analysis.** The paper has enough results; it needs sharper
  framing and one finished arm, not more surface.
- **Do not sand off the hedges.** They are what the reviewers praised.
- **Do not report Track 3 detection without its false-positive rate.** `cautious-verbal`
  exists solely to provide that denominator. Half of it is not a finding.
- **Do not re-run the sweep.** 28 of 30 cells are `.done`; `--probe-only` exists for
  the probe. Cost discipline is a standing rule, not a suggestion.

---

## 5. Rules this session added

10. **A manipulation check is a gate, not an analysis step.** If a condition is meant
    to change behaviour, verify it changed before spending on downstream cells.
    (Cost of learning this: one full Track 3 sweep.)
11. **A premise-carrying probe needs its no-premise baseline in the same run.** The
    persona conditions were uninterpretable for hours purely because the `persona=none`
    probe had not been run.
12. **Never let two runs write the same summary filename.** `--probe-only` clobbers
    `self_report_summary.json`.
