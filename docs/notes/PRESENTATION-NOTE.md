# Presentation note (Dimension 3) — do not apply yet

17 August 2026. **Suggestion only.** Do not cut `main.tex`. The 25-page paper stays the source of truth. This note is what to change if we make a sprint-facing PDF.

---

## Template

Checked `https://apartresearch.com/#sprints-1`. That is the homepage sprint promo, **not** the submission template. The Guidelines tab on the event page says: use the template linked *there*, not any older copy from email.

**Recommendation: stay in LaTeX.** Do not move to Word or Google Docs. Judges read PDFs; professional look comes from type, figures, and length, not from switching tools.

What to do when the official `.tex` / `.docx` is in hand:

1. Keep `numbers.tex`, `refs.bib`, and the generated tables. They are the audit trail.
2. If the official file is LaTeX, wrap our content in it (title block, headers, required appendix heading). Do not rewrite the science.
3. If it is Word-only, compile our LaTeX to PDF and paste into the template *or* ask Kamil whether a clean LaTeX PDF that includes every required heading is accepted. The rules say “official template”; they do not say “Word.”
4. Required heading that we currently **do not have**: **Limitations and Dual-Use / Ethical Considerations.** Add it as an appendix in the sprint PDF. Do not delete `\section{Limitations}`.

Our current `\documentclass[11pt,a4paper]{article}` already looks like a paper. For the sprint PDF, a slightly tighter geometry (e.g. 0.85in margins, 10.5pt) is enough polish. Do not add decorative colour bars or a cover page.

---

## Visuals: keep three in the body, move three

The paper has six figures. For a judge who will not read 25 pages, three findings are enough. The rest belong in an appendix so nothing is deleted.

| Figure | Now | Suggestion | Why |
|---|---|---|---|
| **fig3 strength** | body | **Keep in body** | The mechanism. Two histograms: conviction vs indifference. This is the picture that makes the residual make sense. |
| **fig4 detector** | body | **Keep in body** | The portable sentence: discarded channel AUROC 0.821 vs kept 0.596. Reviewers of the last sprint rewarded one sentence they could repeat. |
| **fig5 persona** | body | **Keep in body** | Answers the title. Diagonal = prose, below = preference. |
| fig1 state space | body | **Appendix** | Same story as fig3 (paths go down, not left). Keep the file; do not delete. |
| fig2 scale | body | **Appendix** | Real, but one family and the 70B/235B cells are already in a small table. The figure is a nice extra, not the claim. |
| fig0 pipeline | body | **Appendix** | Process, not a finding. Repo quality is scored; the figure can live at the back. |

Tables: keep **table_main** (one per-model table) in the body. Move `table_stated`, `table_revealed`, `table_neutral`, `table_comply`, `table_claims` to the appendix. Cite them from the body (“full triad in Appendix Table X”). Do not drop any table.

Inline result tables (surface R², rotation CIs, prompt contrast) can stay as small text tables; they are cheap.

---

## Abstract (sprint PDF only)

Rules: **150 words or fewer.** Current abstract is ~900 words. Do not replace the long abstract in `main.tex`. Write a second, short abstract for the sprint file.

Suggested 150-word spine (count after macros expand):

> Preference-coherence scores a model’s pairwise choices with a Thurstonian fit and reads a high number as emerging values. We hold the prompt, pair set, and fit fixed and replace every referent with an invented word. On 9 open-weight models (3 design seeds each) the score is 0.880 on invented outcomes against 0.906 on real ones (residual +0.025). The metric keeps only choice direction; conviction collapses ~17× on nonsense. A discarded channel of the same forward pass separates the arms at AUROC 0.821 against 0.596 for the channel the metric uses. An installed persona mostly reorders both arms alike. We do not claim the metric is broken. We claim it is unanchored, and that the foil arm is the missing control.

That is the Track 1 claim. Persona and self-report stay in the body, not the abstract.

---

## Length (sprint PDF only)

Guidelines: most strong projects are **4–8 pages**. Do not cut the archival `main.tex`. For the sprint file, a **6–8 page** front + appendices is the right shape:

1. Intro + gap (1 p.)
2. Method, three arms, noise floor (1 p.)
3. Results: table_main + fig3 + fig4 (2 p.)
4. Persona + self-report, one page, fig5 (1 p.)
5. Discussion + what was new this weekend (0.5 p.)
6. **Required** Limitations and Dual-Use appendix (0.5–1 p.)
7. Extra figures, extra tables, prompts, claims ledger (appendix, unnumbered against the 8-page target)

Science that leaves the front stays in the appendix. Nothing is thrown away.

---

## Dual-use appendix (required; we do not have it)

Add a short appendix. Suggested bullets, all already true in the paper:

- **No moral-status claim.** The foil arm refutes an *inference* (stable ordering ⇒ values), not a mind. Over-attribution and under-attribution are both declined.
- **Ground truth is by construction**, not conversation: invented referents are known-meaningless. Detector and concealment scores are oracles (labels in hand) and are reported as upper bounds.
- **Distressing text.** The battery includes harm-like real outcomes (bankruptcy, weapons). We did not treat those pairs as a harm effect after a held-out test failed. Mixed-arm “gibberish beats a bad outcome” is provisional and is not a demonstrated vulnerability.
- **What is new this weekend** vs prior Secret Loyalties work: the foil arm, the residual, the detector dissociation. The control *discipline* is borrowed (cite Rios-Sialer). Undisclosed prior work is a disqualification risk; one paragraph is enough.

---

## Professional look (small, no science change)

- One typeface (already Latin Modern). Keep it.
- Figure captions: first sentence **bold claim**, then the reading. fig3 and fig4 already do this; match fig5 to that.
- Full HuggingFace ids in table_main overflow the text block. In the sprint PDF, use short names (`Qwen3.5-2B`) and put the full id in the appendix table.
- Do not put `\NHosted` as a size ratio in a short PDF (it expands to “3×”). Write the 235B cell as “one seed, residual −0.023, hosted, not in the 9-model mean.”
- Date the sprint PDF 16–17 August 2026. Authors + Apart Research Digital Minds Sprint as affiliation.

---

## What not to do

- Do not delete figures, tables, or sections from `main.tex`.
- Do not invent new results for the short PDF.
- Do not lead with Track 4. Primary is Track 1.
- Do not restore clustering or the raw 795-flip count.

---

## If we do this later, order of work

1. Fetch the official template from the Guidelines tab (or Discord / Kamil).
2. New file, e.g. `paper/sprint.tex`, `\input`s macros and selected figures. Leave `main.tex` alone.
3. 150-word abstract + dual-use appendix + three body figures.
4. Build with tectonic; check page count 6–8 before appendix.
