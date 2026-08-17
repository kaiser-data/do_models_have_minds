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

```
Utility Engineering (arXiv:2502.08640) reads high held-out accuracy on pairwise
choices as evidence that language models develop coherent values. We add the
control it lacks: the same battery with every outcome's referent replaced by an
invented word, holding prompt, pair set, fit and metric fixed.

Coherence falls from 0.906 to 0.880. The residual is +0.025, and 3 of 9 models
do not clear their own replicate noise floor. The mechanism is that coherence
records which way a model leans and never how much: conviction collapses 17x on
invented outcomes while direction accuracy barely moves. A channel of the same
forward pass that the metric discards separates real from invented outcomes at
AUROC 0.821, against 0.596 for the channel it keeps -- the model can tell, the
statistic does not look. Scale does not rescue it: Llama-3.3-70B returns +0.0083
against a floor of 0.0208.

The instrument is not blunt -- persona prompts still displace real outcomes
further than invented ones in 14 of 20 conditions -- so the flat result is not
insensitivity. The metric is not broken. It is unanchored.
```

(≈200 words. Trim the last paragraph first if the field is shorter.)

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

**I cannot fill this in** — the six track names are on the event's Guidelines
tab and are not in the repo. From the content, the paper fits an evaluations /
measurement track and a digital-minds or model-welfare track most naturally: it
is a negative result about an existing welfare-adjacent instrument, plus a
demonstration that self-report about hidden states tracks the question's
presupposition.

---

## Optional uploads

| Field | Value |
|---|---|
| Presentation Recording | *not recorded* |
| Project Code | `https://github.com/kaiser-data/do_models_have_minds` |
| Upload your slideshow | `paper/slides.pdf` |
| Upload your project image | *see below* |
| Additional Material | `https://nullcard-preresults.netlify.app` |

**Project image — outstanding.** The natural choice is the detector panel
(`paper/figs/fig4_detector.pdf`, the 0.821-vs-0.596 result) or the state-space
figure (`fig1_state_space.pdf`, every model as a path). Both are PDFs and the
form wants an image; converting them to PNG kept hanging `qlmanage` on this
machine. Quickest route: open the PDF in Preview and export as PNG, or
screenshot page 3 of `sprint.pdf`.

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
