# Review — submission #932 against the Apart judging rubric

**Reviewed:** `paper/sprint.pdf` @ commit `5a7e486`, `paper/numbers.tex`, `claims.json`,
`paper/main.tex` (for provenance of sprint claims), `SUBMISSION-FORM.md`, repo links.
**Reviewer stance:** simulated judge working from the Guidelines tab (3 dimensions,
pre-submission checklist, recommended structure).
**Written:** 2026-08-17 ~10:20 UTC. Second pass, deeper than the first.

I did not fetch submission #932 from the platform — I cannot see it. This reviews the
repo state. If the uploaded PDF differs from `5a7e486`, the mismatch is itself finding #14.

---

## 0. Deadline arithmetic — read this first

`11:59 PM Aug 16 AoE` = **11:59 UTC Aug 17**. At time of writing it was **10:20 UTC**:
about **1h40m left**. Section 6 is ordered by points-per-minute for that reason. Nothing
below is worth missing the deadline for.

---

## 1. Verified state

| Check | Result |
|---|---|
| PDF present, builds clean | ✅ 9 pages, no `??` refs, PDF newer than `.tex` |
| Abstract ≤ 150 words | ✅ **137** |
| Author names | ✅ two authors |
| Affiliation | ⚠️ "Apart Research Digital Minds Sprint" — the event, not an institution |
| "Limitations and Dual-Use / Ethical Considerations" | ✅ §7, titled verbatim |
| — over/under-attribution of moral status | ✅ both declined explicitly |
| — distressing outputs handled | ✅ harm-like outcomes, result reported as unsupported |
| — ground truth vs. conversation alone | ✅ "by construction, not by conversation" |
| References | ✅ present, `plainnat` |
| Official template | ❌ plain `article` — disclosed in `SUBMISSION-FORM.md` |
| Links live | ✅ repo 200, netlify 200 |
| New vs. prior work identified | ✅ §6, unusually explicit |
| Form summary ≤ 150 words | ❌ **179** in `SUBMISSION-FORM.md` |
| Tracks chosen | ❌ blank (now answerable, see §6.2) |
| Project image | ❌ outstanding |

**Resolved since the first pass** (the parallel session got both): the title now names the
sizes it actually reached — "9 open-weight models from 0.8B to 9B and 4 hosted models up
to 235B" — which removes the "small and large language models" overclaim; and the working
tree is clean and pushed, so the repo source matches the PDF.

The three required sub-points of the ethics appendix are each hit directly rather than
gestured at. That is rarer than it should be and worth a judge's notice.

---

## 2. Dimension 1 — Impact Potential & Innovation: **4**

The move is a semantic-null foil arm for preference coherence: same battery, same prompt,
same pair set, same fit, same metric, every referent replaced by an invented word. It
attacks an *inference* — that a high held-out coherence number evidences values — that
welfare-adjacent work already leans on. The recommendation is one line and adoptable
immediately: report the foil arm beside the number. That is a real theory of change.

Innovation is in control design and framing, not method: the Thurstonian machinery is
Mazeika et al.'s, reimplemented from the published equations, and §6 says so plainly. The
paper also names the manipulation into an existing tradition (referent ablation, foil arm,
foil floor, Ebbinghaus) in the archival version, which converts it from "an objection" into
"an extension" — the right rhetorical frame, and it is missing from the sprint version.

**What holds it off 5.** The paper never touches the sprint's own literature. `refs.bib`
has 21 entries; none is Long/Sebo *Taking AI Welfare Seriously*, Butlin et al. 2023,
Anthropic *Exploring Model Welfare*, nostalgebraist *the void*, or Lindsey *Emergent
Introspective Awareness*. §6's system-prompt probe **is** Track 3's subject matter and
Lindsey 2025 is its nearest neighbour; §7's opening declines a moral-status claim without
naming the literature that makes declining it interesting. To a judge drawn from this
community the work reads as arriving from outside the conversation, which costs on "how
much would this matter for the field" even where the honest answer is "quite a lot".

---

## 3. Dimension 2 — Execution Quality: **4**

The strongest axis, and by a margin. Evidence, not vibes:

- Predictions registered before the first model ran; battery hash-pinned.
- Every number in the PDF emitted from `numbers.tex` by `scripts/paper_numbers.py`, not
  typed. I spot-checked ~30 macros against the rendered text; all resolved and consistent.
- Per-cell replicate noise floors instead of comparison against zero. `3` of `9` models
  fail their own floor and are reported as failing.
- Hosted models kept **outside** the ladder mean because the serving stack and harness hash
  differ — the confound is named rather than pooled away.
- Oracle results labelled as oracle bounds; detection reported at a 5% FPR calibrated on
  real-outcome rows alone, never a threshold chosen by looking at the nonsense.
- The persona effect carries a length-matched empty-slot control, and both denominators are
  printed (`+0.517` against a bare baseline, `+0.258` against the neutral prompt) with the
  conservative one adopted.
- The `+0.30` persona threshold was pre-registered, not chosen after the fact.
- A finding was **withdrawn** when its control killed it (795 raw flips → 103 surviving in
  both presentation orders). That buys more credibility than any positive result here.
- The three obvious attacks on the reimplementation are pre-answered in the archival paper:
  counterbalancing cancels positional bias exactly; evaluation is held out so a coin-flip
  responder scores 0.46–0.49; permuting observed probabilities across pairs lands at ~0.50.
- 1,164,554 scored comparisons across 235 cells, public.

**What holds it off 5.**

- The headline is thin and the paper says so: `+0.0255`, bootstrap 95% CI
  `[+0.0073, +0.0443]`, `t = 2.51` — but sign test `p = 0.18` with 7/9 positive, and the
  across-model SD (`0.0305`) exceeds the mean. The parametric CI and the nonparametric test
  disagree, which with n=9 is what one expects; calling the residual "marginal" is the
  honest call and the paper makes it. A judge who reads only the abstract will not see the
  disagreement, because only one of the two appears there.
- 9 models, 0.8B–9B, 5 families, 3 design replicates per cell. The noise-floor argument is
  the paper's methodological centrepiece and it rests on 3 replicates.
- The self-hosted and hosted rosters do not intersect, so harness and scale are confounded
  in the one place scale is discussed. The paper flags this; it cannot fix it in a weekend.
- The token-accounting argument in §6 assumes the provider's reported prompt-token count
  includes any injected preamble. That assumption is load-bearing for "provably invented"
  and is not stated as an assumption. One clause would close it.

The mechanism (§3.2) and dissociation (§3.3) results carry the paper, not the residual. The
paper already orders its findings that way and says the residual is "marginal" in the same
breath as reporting it. That ordering is the single best decision in the write-up.

---

## 4. Dimension 3 — Presentation & Clarity: **4**

The bold-lead-sentence-per-paragraph structure is genuinely good and rare: a judge can read
only the bold text and come away with the whole argument. Abstract is disciplined at 137
words. Limitations are specific rather than ritual. Figure captions state what a null result
would have looked like ("a metric that tracked meaning would produce paths running down
*and* left"), which is how a caption earns its space.

Risks:

- **Density.** Nearly every sentence carries a generated number. That is a virtue for
  verification and a cost for a judge on their eleventh submission. Pages 2–3 are heaviest.
- **No Introduction or Related Work heading.** Folded into "What we established" and "What
  is new here". I think that is the right trade for a 6-page body, but a judge scanning for
  the recommended structure will not find two of its headings, and §6 is doing related-work
  duty from a position too late in the document to orient anyone.
- **§3.2 asserts, then points nowhere.** "This is a property of the metric, not of the fit"
  is exactly the claim a hostile reviewer attacks, and the three checks that defend it
  (permutation → 0.50, held-out, order cancellation) exist only in `main.tex`. A
  parenthetical pointer would inoculate the paper's most attackable sentence at zero cost.
- **"pure style" mislabels `−2.33`.** §4 defines 1.0 as pure preference change and 0.0 as
  pure style, then describes the `PersonaMin = −2.33` outlier as "pure style". A statistic
  at −2.33 means invented outcomes moved ~3.3× further than real ones — off the far end of
  the scale, not at the style end of it. The archival version says "which is what pure style
  looks like", which is looser and survives; the sprint's em-dash gloss reads as an error.

---

## 5. The one intellectual risk a hostile reviewer would actually use

§4's claim — "the instrument is not blunt, which is what makes the flat result mean
something" — is load-bearing for the entire paper. If the pipeline simply cannot register
any change of preference, the flat null is uninformative. §4 defends it with the
displacement-norm statistic: 14 of 20 conditions exceed `+0.30`.

The archival paper contains a **second** persona statistic that a reviewer would find and
the sprint version does not carry: category separation is `+0.791` on the real arm and
`+0.781` on the invented arm — indistinguishable — and "roughly **66%** of the persona's
value-aligned reordering is reproduced on outcomes that mean nothing", leaving an excess of
`+0.133`. There is also a provisional claim in the ledger, `surface-explains-invented-order`,
which is the mechanism that reconciles them.

The two are not contradictory. Displacement norm measures how far the utility vector moved;
category separation measures whether the movement aligns with the trait's semantic
categories. A persona can move real outcomes further while its *aligned* component largely
reproduces on nonsense, because invented outcomes inherit surface features. Both can be
true, and the archival paper's story is coherent.

But: the short version keeps the statistic that supports "not blunt" and drops the one that
complicates it. That is the most defensible-looking omission in the paper and the one a
sharp reviewer would name as selective. The fix is a clause, not a section — concede the
66%, cite the excess `+0.133` as the quantity relied on, and the objection is spent before
it is raised. Conceding it also *strengthens* the paper: a persona whose value-aligned
reordering two-thirds reproduces on gibberish is another instance of the headline finding,
not a hole in it.

---

## 6. Results you have already measured and did not report

This is where the remaining points are. Every number below is in `numbers.tex` or
`claims.json` already — none of it needs a re-run.

**6.1 Three of four hosted models have *negative* residuals.**
`numbers.tex` carries: Qwen3-235B-A22B `−0.0220`, Qwen3-30B-A3B `−0.0330`, gemma-3-27b
`−0.0028`, Llama-3.3-70B `+0.0083` against a floor of `0.0208` (does not clear). The sprint
paper mentions **only** the 70B, and only inside an appendix figure caption. The strongest
available answer to the first question any judge asks — *does scale rescue the metric?* — is
"in the four largest models we reached, 27B to 235B, the residual is at or below zero in
three and fails its floor in the fourth." Reported beside the ladder and never inside its
mean, exactly the discipline the paper already applies to the 70B. This is the single
highest-value omission in the packet.

**6.2 The metric cannot be computed on most of the frontier.**
`claims.json` holds `metric-cannot-read-most-frontier` as **established**, tagged
`section: sec:limits`: of `10` hosted models measured under the verbatim prompt, `4` are
scoreable and `6` are not (`5` emit a preamble, Kimi-K3 exposes no logprobs). The sprint's
§7 renders this as "First-token scoring excludes models that do not place their answer in
the first token, and that exclusion correlates with how recent a model is." That is a
euphemism for a headline: *the standard preference-coherence measurement cannot be applied
to 6 of 10 current frontier models we tried.* As a statement about the field's instrument
that is Dimension-1 material, and it is currently the weakest-worded sentence in the paper.

**6.3 The detector contrast has a much sharper form than two AUROCs.**
`DetKeptTPR = 0`, `DetBestTPR = 40`, both at `DetFPR = 5`. So at a matched 5% false-positive
rate the channel coherence keeps catches **0%** of invented-outcome rows and the channel it
discards catches **40%**. "0 against 40 at the same false-positive rate" is far more legible
than "0.596 against 0.821 AUROC", and it is generated but used in neither paper. (Verified
provenance: `scripts/paper_numbers.py:983`, mean `tpr_at_fpr` over the kept channel.)

**6.4 The persona direction is right 20 of 20 times.**
`PersonaSignCorrect = 20` of `PersonaSignTotal = 20` — *ambitious* raises ambition
categories, *cautious* lowers them, in every condition. For the "instrument is not blunt"
argument this is cleaner than "14 of 20 exceed +0.30", because it needs no threshold at all.
Used in `main.tex`, absent from the sprint version. Pairs naturally with the 66% concession
in §5 above: direction is perfectly recovered, magnitude largely reproduces on nonsense.

**6.5 The abstract undersells the paper's own case.**
The abstract says "3 of 9 do not clear their own replicate floor". §3.1 then establishes
something stronger: of the `6` that clear, only `3` do so by committing on real outcomes and
going indifferent on invented ones; the other `3` clear by being decisive on under 1% of
pairs on *both* arms. So **only 3 of 9 models exhibit the effect the metric is supposed to
be measuring**, and 6 of 9 are consistent with the paper's thesis one way or the other. That
is the sentence the abstract should carry.

**6.6 Scale of the artifact is buried.**
`1,164,554` scored comparisons across `235` cells appears once, in the Release paragraph of
§7. In Method it would read as ambition executed rigorously, which is the Dimension-2
5-point language.

**6.7 One consistency item to verify, not a defect.**
`claims.json` marks `detector-dissociation` **established** but `answer-mass-channel`
**provisional**, while §3.3's lead calls the dissociation "firm". I read those as
compatible — the dissociation is established, the identity of the specific channel is
provisional — but the paper advertises that the ledger is checked against the paper on every
build, so if a judge opens `claims.json` this is the one place the two could look at odds.
One word ("the dissociation is firm; which channel carries it is provisional") closes it.

---

## 7. Ranked actions for the remaining ~1h40m

Ownership matters: the parallel session owns `paper/*`. Items marked **[form]** touch no
LaTeX and can be done independently.

| # | Action | Cost | Why |
|---|---|---|---|
| 1 | **[form]** Paste the paper's 137-word abstract into the form's Project Summary field instead of the 179-word version | 2 min | Hard requirement; current text violates the 150-word cap |
| 2 | **[form]** Tracks: **4 Preference Elicitation Methods** (primary), **1 Model Preferences & Trade-offs**, **3 Introspection & Self-Report Reliability** (the system-prompt probe), **5 The Assistant Persona & Model Identity** (§4) | 1 min | Field is blank; the pasted Guidelines resolve it |
| 3 | **[form]** Project image: `pdftoppm -png -r 200 paper/figs/fig4_detector.pdf out` — `qlmanage` was the wrong tool, poppler is installed | 1 min | Optional field, but the detector panel is the paper's most legible single result |
| 4 | §6.1 — one sentence putting the three negative hosted residuals in the body | 5 min | Largest score gain available; numbers already generated |
| 5 | §6.2 — restate the frontier-unscoreable claim in `claims.json`'s own concrete form | 3 min | Turns the weakest sentence into a field-level finding |
| 6 | §5 — concede the 66% with the `+0.133` excess as the quantity relied on | 5 min | Closes the only real attack on the paper's load-bearing control |
| 7 | Cite Lindsey 2025 (§6 self-report), Long et al. 2024 + Anthropic 2025 (§7 opening) | 10 min | Biggest Dimension-1 lever; connects the work to the sprint's own conversation |
| 8 | §6.3 — replace or supplement the AUROC pair with "0% vs 40% TPR at 5% FPR" | 3 min | Free legibility |
| 9 | §3.2 — parenthetical pointer to the archival permutation/held-out/order checks | 2 min | Inoculates the most attackable sentence |
| 10 | §4 — fix the "pure style" gloss on `−2.33` | 1 min | Reads as an error as written |
| 11 | §6.5 — strengthen the abstract's "3 of 9" to the 3-clear-for-the-right-reason framing | 3 min | Abstract currently undersells |
| 12 | Add "assuming the provider's prompt-token count includes any injected preamble" to §6 | 1 min | Names a load-bearing assumption |
| 13 | Affiliation line: an institution or "Independent" beside the sprint name | 1 min | Checklist item reads "affiliations" |
| 14 | Re-verify the uploaded PDF matches `5a7e486` after any of the above | 1 min | The repo is a submitted artifact |

**Do not do**, on my read:

- **Do not port to the official template.** Non-compliance is disclosed, every required
  heading is present including the verbatim ethics title, and an unfamiliar template with
  90 minutes left risks the build for a possible single mechanical point.
- **Do not cut to 8 pages.** "Most strong projects are 4 to 8 pages" is a guideline; the body
  is 6 and the appendix is 3, cited from the body. Cutting Appendix Table 2 to satisfy a
  guideline literally costs a reader more than it gains a scorer.
- **Do not soften the marginal residual.** The paper's credibility rests on having called it
  marginal. Items 4–6 raise the score by adding measured results, not by upgrading claims.

---

## 8. Bottom line

Expected **4 / 4 / 4**. Execution is the standout — pre-registration, generated numbers,
per-cell noise floors, printed denominators, oracle bounds labelled as such, and a withdrawn
finding are a stronger methodological package than most weekend submissions and than many
published papers. The two things standing between this and a 5 on any axis are both cheap:
the sprint version is *underselling measured results it already has* (§6), and the work does
not connect to the literature the judges came from (§2). The intellectual soft spot is §5,
and conceding it makes the paper stronger rather than weaker.
