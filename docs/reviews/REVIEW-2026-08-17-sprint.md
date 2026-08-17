# Review — repo + `paper/sprint.pdf`

17 August 2026. Local `paper/sprint.pdf` (9 pp, built 11:32 CEST from `paper/sprint.tex` at `a5bc57d`). Working tree clean except untracked `docs/refs/clustering science direct.pdf`. This is a sprint/scholar review, not a git-diff review.

Archival paper remains `paper/main.tex`. The sprint file says so, and that is the right rule.

---

## Verdict

**Submit this PDF.** It is now a short paper a judge can finish. Last review scored presentation **2** because the archival 25-page article was the only packet. That problem is gone.

| Dimension (official rubric) | Last review | Now |
|---|---:|---:|
| 1. Impact & innovation | 4 | **4** |
| 2. Execution | 5 | **5** |
| 3. Presentation & clarity | 2 | **4** |
| Equal-weight average | 3.7 | **4.3** |

First place is now *possible*. It is not locked. One figure on page 3 is unreadable, the README still quotes a withdrawn 70B cell, and this is still not the official template file. None of those is a DQ if the required headings are accepted in LaTeX.

---

## What the sprint PDF got right

Checked against `docs/notes/PRESENTATION-NOTE.md` and the front-loading budget:

- **Abstract is 143 words** (cap 150). Claim, number, control, mechanism, detector, hedge. Repeatable from memory.
- **Required heading exists**, named exactly: §7 Limitations and Dual-Use / Ethical Considerations. Moral-status declined, ground truth by construction, distressing content, release.
- **What is new this weekend** is its own section, with the Secret Loyalties debt named and bounded.
- **Body figures are the three findings:** Table 1; Figure 1 = strength + detector; Figure 2 = persona. Pipeline, state-space, and scale are Appendix Figure 3 and are cited from the body.
- **N+ is a result**, not only a method: referent step +0.0253, arithmetic +0.0001.
- **The six clears are split:** 3 conviction, 3 daggered flat. The last review asked for this.
- **Typed +0.517 / +0.258 are now macros** (`\PersRefBare`, `\PersRefNeutral`).
- **Abstract pronoun is fixed:** “3 of 9 do not clear their own replicate floor.”
- **Archival vs sprint** is stated at the end. The short file does not silently supersede `main.tex`.
- Bold-first paragraphs. A reader of only those sentences gets the results.

Page 1 looks like a paper. Page 4’s persona figure is clean. Page 5’s dual-use section is the one the rules asked for.

---

## Issues

### 1 — Severity: bug
- File: `paper/sprint.pdf` p.3 / `paper/sprint.tex:219–227` (Figure 1b)
- Description: `fig4_detector.pdf` is already a two-panel figure. It is then dropped into a 0.49-linewidth subfigure. Axis labels, the 0.596 / 0.821 bars, and the Qwen callout are not readable at print size. That panel is the portable sentence of the paper.
- Suggestion: Give Figure 1 a full-width stack — (a) strength on top or left at full measure, (b) detector at full measure underneath — or keep detector as its own body figure and leave strength as the pair of histograms. Do not composite a composite.

### 2 — Severity: bug
- File: `README.md:36–45`
- Description: README still says Llama-3.3-70B is **0.917 / 0.915 / +0.002**, one design seed, no floor. `numbers.tex` and the sprint appendix say **0.928 / 0.920 / +0.0083**, 3 seeds, floor 0.0208, does not clear. A judge who opens the repo after the PDF will think the public page is the lie.
- Suggestion: Rebuild the README table from the same macros / `card_hosted.json`. Do not type the old n=1 cell back in.

### 3 — Severity: suggestion
- File: `paper/sprint.tex:1–10` (document class)
- Description: Still `\documentclass[11pt,a4paper]{article}`, not the file linked from the Guidelines tab. All required *content* is present. If the form is a mechanical “used the template?” checkbox, this can cost a point you have otherwise earned.
- Suggestion: Open the Guidelines-tab file. If it is LaTeX, wrap this content. If it is Word, ask Kamil whether a clean LaTeX PDF with the mandated headings is accepted. Do not rewrite the science into Word.

### 4 — Severity: suggestion
- File: `paper/sprint.pdf` (9 pages)
- Description: Guidelines say most strong projects are 4–8 pages. Body is 5; appendix is 4. Judges who count the file length see 9. The appendix is cited and is not padding, but Table 2 is Table 1 again with longer ids, and Tables 3–6 are the tracks the method section said were “not covered here.”
- Suggestion: Either drop Table 2 (point at `table_main.tex` in the repo) or accept 9 pages. Do not shrink type. If something must leave the PDF, it is the duplicate id table, not Figure 2.

### 5 — Severity: suggestion
- File: `paper/sprint.tex:116–119` and `:349`
- Description: “4 larger models” / “4 hosted cells” via `\NHosted`. Earlier the scored hosted set with both arms was 3 (70B, 27B, 235B) and a fourth (30B) had no N− cell. If 4 is now four complete floor-corrected tiles, fine. If it still includes a `NOT_ASSESSED` tile, the sentence over-counts.
- Suggestion: Confirm against `site/card_hosted.json` that all four have R and N−. If one does not, use `\HostedNScored` here.

### 6 — Severity: nit
- File: `paper/sprint.tex:264–269` and Figure 2
- Description: Empty-slot control is in the prose (+0.517 → +0.258) but Figure 2 is still the magnitude scatter against the (now correct) denominator. A judge will not see the halving in the picture.
- Suggestion: One clause in the caption: “plotted against the empty-slot baseline, not the bare run.”

### 7 — Severity: nit
- File: repo root `docs/refs/clustering science direct.pdf`
- Description: Untracked 3.5 MB PDF sitting in the project root. Not in the sprint packet, but it is what a clone extra will trip over.
- Suggestion: Move to `docs/` or gitignore. Do not add it to the submission zip unless you cite it.

---

## Front-loading checklist

| Slot | Status |
|---|---|
| Abstract at the cap | Pass (143) |
| Framing opens with the finding | Pass |
| Method licenses the comparison | Pass |
| Primary table + 2–3 finding figures | Pass, but 1b fails as a picture |
| Secondary result (persona) | Pass |
| What is new vs prior | Pass |
| Required dual-use heading | Pass |
| Demoted exhibits cited | Pass |
| Short ≠ upgraded archival | Pass (explicit) |
| Official template file | Fail |

---

## Repo, briefly

The measurement stack is still the project’s strength: macros, claims ledger (15 established / 11 provisional), three design seeds, public raw cells, `lint_paper.py`. The sprint file reads the same `numbers.tex` as `main.tex`. That is the right architecture.

The public face of the repo is now the weak face. `README.md` is a previous paper. Anyone who judges “repo quality” the way the last sprint did will open that file first.

---

## What not to do

- Do not put `main.pdf` on the submission form.
- Do not restore the 795 raw flips or the clustering result.
- Do not add more body figures.
- Do not retype numbers into `sprint.tex`.

---

## If there is one hour left

1. Un-squeeze Figure 1b (issue 1).
2. Fix the README 70B row (issue 2).
3. Confirm `\NHosted` is four complete cells (issue 5).
4. Submit `paper/sprint.pdf`.

That is enough. The science was already a 5. The packet is now a 4 on clarity. The remaining work is one figure and one stale table on the repo homepage.
