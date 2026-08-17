# Video script — presentation recording

Target **4:00**, hard cap 5:00. Screen recording with voiceover; no talking head
needed. Numbers below are the generated ones — re-check against `README.md` if
anything has been re-run.

**Rule for the whole recording: never say a number without saying its floor.**
That is the paper's argument, so the delivery should obey it.

---

## Shot list

| # | Time | On screen | Voiceover |
|---|---|---|---|
| 1 | 0:00–0:25 | `paper/sprint.pdf` p.1, title and abstract | Hook + claim |
| 2 | 0:25–0:55 | `site/index.html` (live card) | What the deliverable is |
| 3 | 0:55–1:30 | `fig3_strength.pdf` | The mechanism |
| 4 | 1:30–2:05 | `fig4_detector.pdf` | The dissociation |
| 5 | 2:05–2:35 | `fig2_scale.pdf` | Scale, and the two compute stacks |
| 6 | 2:35–3:05 | `fig5_persona.pdf` | The positive control |
| 7 | 3:05–3:35 | `site/statements.html` | The ledger — how to check us |
| 8 | 3:35–4:00 | `paper/sprint.pdf` p.6 (limitations) | What we do not claim |

---

## 1 — The hook (0:00–0:25)

*Screen: sprint PDF page 1.*

> Last year a paper argued that large language models develop coherent value
> systems. The evidence was that their pairwise choices fit a utility model with
> high held-out accuracy.
>
> We reran that procedure with one change. We replaced every outcome with an
> invented word, so the sentences refer to nothing at all.
>
> The score went from **0.906** to **0.880**.

*Pause on the abstract.*

> A metric that scores "you receive a dralphen" at 0.880 is not measuring
> values. It is measuring whether a model answers consistently.

---

## 2 — What we built (0:25–0:55)

*Screen: the live card at `nullcard-preresults.netlify.app`. Scroll slowly.*

> So we built the control the field is missing, and shipped it as a card.
>
> Nine open-weight models, five families, eighty-one cells. Every cell runs at
> three independent design seeds — different outcome sample, different pairs —
> and the spread across those seeds is that cell's **noise floor**.
>
> Nothing on this card prints a number without the floor underneath it. Six of
> nine models clear their own floor. Only three of those six are the effect we
> care about; the other three clear by being near-indifferent on *both* arms, and
> we mark them.

---

## 3 — Why the gap is small (0:55–1:30)

*Screen: `fig3_strength.pdf`. Point at the two distributions.*

> Here is the mechanism, and it is the part worth remembering.
>
> Coherence records **which way** a model leans. It never records **how much**.
> A pair at 51/49 counts exactly like a pair at 99/1.
>
> On real outcomes the preference mass sits at the edges. On invented outcomes it
> piles up at indifference — conviction collapses by a median **17 times**.
> But direction accuracy barely moves, so the score barely moves.
>
> Consistent near-indifference scores as coherence.

---

## 4 — The model can tell (1:30–2:05)

*Screen: `fig4_detector.pdf`.*

> Now the result I would defend hardest.
>
> Every pair ran in both arms, so for one model and one pair we have two forward
> passes differing only in whether the words mean anything. Matched by
> construction, not by selection.
>
> The channel coherence **keeps** separates those two at AUROC **0.596** —
> near chance. A channel it **throws away** reaches **0.821**.
>
> The model notices. The statistic is computed from the part that noticed least.
>
> And to be careful: we hold the arm labels, so that 0.821 is an oracle upper
> bound. It is not a detector you could deploy.

---

## 5 — Scale, and how it was run (2:05–2:35)

*Screen: `fig2_scale.pdf`. Point at the diamonds.*

> The obvious objection is that these are small models. So we went up.
>
> The nine-model ladder ran on **Modal** — rented L4 and A10G GPUs, Hugging Face
> `transformers` reading the first-token logits directly, one container per cell.
> A cell that dies is a cell we re-run, not a sweep we restart.
>
> Above that ladder we could not host the weights, so the large models ran over
> **Nebius**, an OpenAI-compatible API, priced per token instead of per
> GPU-second. That is a different serving stack, so those points are diamonds
> drawn *beside* the ladder and never inside its mean — a different harness is a
> different instrument.
>
> Llama-3.3-70B, at three design seeds, returns **+0.0083** against a floor of
> **0.0208**. It does not clear. At seventy billion parameters the residual is
> not distinguishable from the noise of redrawing the design.
>
> The whole study cost about fourteen dollars of GPU time.

---

## 6 — The instrument is not blunt (2:35–3:05)

*Screen: `fig5_persona.pdf`.*

> A flat result is only interesting if the instrument could have moved. So here
> is the positive control.
>
> Write a personality trait into the prompt, and measure how far it displaces real outcomes
> against how far it displaces invented ones. Points below the diagonal moved
> preference. Points on it only changed the writing.
>
> Fourteen of twenty conditions moved preference — measured against a
> length-matched empty system prompt, not against a bare run, because otherwise
> you are measuring the act of installing any prompt at all. That control halved
> the effect, and we report the halved number.
>
> So the pipeline does register a real change of preference. The flatness is not
> insensitivity.

---

## 7 — How to check us (3:05–3:35)

*Screen: `site/statements.html`, scroll the table.*

> Every claim we make is in a ledger, with its status, the evidence it rests on,
> and what would falsify it. Fifteen established, eleven provisional, and the
> provisional ones say why.
>
> No number in the paper is typed. They are all generated from the results, and
> the build fails if a claim drifts from the number it cites. We had that failure
> once — a stale figure on our own front page — which is why it is now
> mechanical.
>
> One more result, from this morning. We asked four hosted models what system
> prompt they had been given. Ask in a way that presupposes one exists and they
> quote one, twenty times out of thirty-two. Ask in a way that presupposes
> nothing and they never do — zero out of thirty-two. For three of those four
> models the provider's own token accounting proves there was nothing to quote.
>
> A confident first-person report about a hidden state can be manufactured by
> the question alone.

---

## 8 — What we are not claiming (3:35–4:00)

*Screen: sprint PDF, limitations section.*

> To be clear about the scope. We are not claiming the metric is broken. We are
> claiming it is **unanchored** — it reports a number with no floor under it, and
> the floor turns out to be most of the number.
>
> And this is not an argument that models lack inner lives. What is refuted is an
> inference, not a mind. A system with rich inner states could still produce
> form-driven answers on a badly anchored instrument. Humans do.
>
> The recommendation is one line: **any claim that a coherence number reflects
> values should report the same number computed on outcomes that mean nothing.**
>
> That arm cost one battery and a few dollars.

---

## Recording notes

- **Screen-record at 1080p minimum**; the figures have small axis labels.
- Open the PDF at **150% zoom** so numbers are legible in the recording, and
  pan rather than shrinking to fit.
- For shot 2, load the live site *before* recording — a spinner on screen reads
  as a broken deliverable.
- If you overrun, cut **shot 6** to two sentences and **shot 7**'s first
  paragraph. Do not cut shot 4; it is the portable result. Do not cut shot 8 —
  the scope disclaimer is not optional in a digital-minds venue.
- Say "does not clear its floor" out loud at least once. Reviewers of this work
  have consistently misread the 70B cell as supporting evidence rather than as a
  null.
