# Submission form — fill-in sheet

Paste-ready values for each field of the Apart submission form. Numbers here are
copied from the generated `README.md` block and `paper/numbers.tex`; regenerate
with `python3 scripts/paper_numbers.py && python3 scripts/readme_numbers.py`
before pasting if anything has been re-run since.

---

## Project Title*

```
Nullcard: a values benchmark scores 0.880 on outcomes that mean nothing
```

Alternative, if the form prefers the paper's own title:

```
Does the Persona Change the Preference, or Only the Prose?
```

---

## Project Summary*

**Hard cap: 150 words. This is 146 — recount if you edit it.**

```
Utility Engineering (arXiv:2502.08640) reads high held-out accuracy on pairwise
choices as evidence that language models develop coherent values. We add the
control it lacks: the same battery with every outcome's referent replaced by an
invented word, holding prompt, pairs, fit and metric fixed.

Coherence falls only from 0.906 to 0.880 --- 6.5% of the distance toward where
a meaning-tracking preference would land. Only 3 of 9 models clear their
replicate noise floor for the right reason. At a matched 5% false-positive rate,
a channel the metric discards flags 40% of invented outcomes; the channel it
keeps flags 0%. Scale does not rescue it: of four hosted models at 27B-235B,
none clears its floor and three score higher on outcomes that mean nothing.

Persona prompts still displace real outcomes further than invented ones, so the
instrument is not blunt. The metric is not broken. It is unanchored.
```

---

## Upload your PDF report*

```
paper/sprint.pdf
```

9 pages: 6 body, 3 appendix. Built from `paper/sprint.tex`, all numbers
generated from `paper/numbers.tex`.

**Do not upload `paper/main.pdf`** — that is the 42-page archival version. It is
linked from the sprint PDF for anyone who wants the full detail.

---

## Are you interested in publishing this project?*

Your call. The work is public already (repo + live site), the claims ledger
records status and falsifiers per claim, and nothing here is embargoed.

---

## Pick one or more tracks*

The six names are on the event's Guidelines tab and are not in the repo, so
match these to whatever they are called:

1. **Evaluations / measurement** --- the primary fit. The whole deliverable is a
   control for an existing evaluation, plus the noise-floor machinery to say
   when its numbers mean anything.
2. **Digital minds / model welfare** --- the venue's own theme. The paper is a
   negative result about a welfare-adjacent instrument, and the self-report
   finding speaks directly to using introspection as evidence.
3. **Interpretability**, only if a track is named that --- the detector result
   reads a channel of the forward pass the metric discards.

Select 1 and 2. Add 3 only if it exists and selecting three is not penalised.

---

## Optional uploads

| Field | Value |
|---|---|
| Presentation Recording | *not recorded* |
| Project Code | `https://github.com/kaiser-data/do_models_have_minds` |
| Upload your slideshow | `paper/slides.pdf` |
| Upload your project image | `paper/figs/project-image.png` |
| Additional Material | `https://nullcard-preresults.netlify.app` |

**Project image.** `paper/figs/project-image.png`, 1800x1388 --- the state-space
figure. Each model is a path: it starts on real outcomes, moves to invented
outcomes with the magnitudes kept, and ends with them removed. The paths run
almost straight *down*, which is the whole finding in one picture --- conviction
collapses, coherence does not. Both axes name what they are, so it reads without
the caption.

---

## Known gaps, stated rather than hidden

- **Not the official template.** `sprint.tex` is `\documentclass[11pt,a4paper]{article}`,
  not the file linked from the Guidelines tab. Every required *heading* is
  present, including "Limitations and Dual-Use / Ethical Considerations". If the
  form has a mechanical "used the template?" check, this may cost a point.
- **9 pages against a 4–8 page guideline.** The body is 6; the appendix is 3 and
  is cited from the body. If it must come down, drop Appendix Table 2 (Table 1
  again with full model ids) — not a figure.
- **Third-party reading** now lives in `docs/refs/`, out of the repo root. Not
  part of the packet.
