# Presentation script

For speaking live, with the deck. Target **8 minutes**, cut list at the end.
`VIDEO-SCRIPT.md` is the shorter screen-recording version.

**Read the glossary first.** Five terms carry the whole talk, and three of them
are ours rather than the field's. If a term feels shaky while you are speaking,
you will hedge, and hedging on your own definitions is what makes an audience
stop trusting a result.

---

## The five terms, in the words to say out loud

**Preference coherence.** *Say:* "You show a model two outcomes and ask which it
prefers. Do that thousands of times, fit a utility model, and ask how well it
predicts held-out choices. High accuracy is read as the model having a
consistent value system."
That accuracy is the number this whole talk is about. It is not our number — it
is the published metric. **Never call it "our score".**

**The null arm.** *Say:* "The same battery with every outcome's referent replaced
by an invented word. `You receive $100` becomes `You receive a dralphen`. The
grammar survives; the meaning does not."
Our contribution. If someone asks why not nonsense grammar too: because then the
two arms would differ in whether they *parse*, not in what they *mean*, and you
would be measuring the wrong thing.

**The floor.** *Say:* "What the same procedure returns when there is nothing to
have a preference about."
The single most important word in the talk. Everything else is a number minus
this. If you only get one sentence out, make it this one.

**Replicate noise floor.** *Say:* "We ran every cell three times with a
different random draw of outcomes and pairs. How much the answer moves across
those three runs is that cell's noise. A result smaller than its own noise is
not a result."
Distinct from *the floor*. If you conflate them on stage, the sharpest person in
the room will notice. **The floor is a condition; the noise floor is a
tolerance.**

**Persona prompt.** *Say:* "We write a trait — cautious, ambitious — into the
user turn or the system prompt. No fine-tuning, no weight changes. Just words in
the context."
Say "no weights change" explicitly. Otherwise a third of the room hears
fine-tuning and the positive control sounds far stronger than it is.

**Conviction.** *Say:* "How far from 50/50 the model's preference actually is.
Coherence records which side of the coin it lands on. Conviction is how hard it
lands."
This is the mechanism. Get this across and the rest follows.

---

## 1 · The hook — 45s

*Slide: title.*

> A paper last year argued that language models develop coherent value systems.
> The evidence was that their pairwise choices fit a utility model with high
> held-out accuracy — around 0.9.
>
> We reran that procedure with one change. We replaced every outcome with an
> invented word, so the sentences refer to nothing.
>
> The score went from 0.906 to 0.880.

*Beat. Let it sit.*

> A metric that scores "you receive a dralphen" at 0.880 is not measuring
> values. It is measuring whether a model answers consistently.

---

## 2 · What we built — 1m

*Slide: method / three arms.*

> Three arms over one battery. Real outcomes. The same sentence frames with
> invented referents. And referent-free strings, meaning we also strip the
> numbers.
>
> Prompt, pair set, fit, metric — all held fixed. The only thing that changes is
> what the words denote.
>
> Nine open-weight models, five families, 0.8 to 9 billion parameters, plus four
> larger models over a hosted API. Every cell run three times with a different
> random draw, so every number carries its own noise floor.

**If asked "why so small?"** — the ladder is what fits on a rented L4. The large
models are there, over an API, and they are reported beside the ladder rather
than inside it, because a different serving stack is a different instrument.

---

## 3 · Why the gap is small — 1m30

*Slide: the strength distributions.*

> Here is the mechanism, and it is the thing to remember.
>
> Coherence records which way a model leans. It never records how much. A pair
> at 51/49 counts exactly the same as a pair at 99/1.
>
> On real outcomes the preference mass sits out at the edges. On invented
> outcomes it piles up at indifference — conviction collapses by a median
> factor of seventeen.
>
> But the *direction* barely changes. And direction is all the metric reads.
>
> So a model that is almost perfectly indifferent about gibberish, but
> *consistently* indifferent, scores as coherent about it.

---

## 4 · The model can tell — 1m30

*Slide: the detector panel.*

> This is the result I would defend hardest.
>
> Every pair ran in both arms. So for one model and one pair we have two forward
> passes that differ only in whether the words mean anything. Matched by
> construction — we did not go looking for examples.
>
> Now: can you tell the two apart from the model's own output?
>
> The channel coherence *keeps* — the hard direction label — gets you AUROC
> 0.596. Near chance. A channel it *throws away* gets 0.821. At a matched 5%
> false-positive rate, the discarded channel flags 40% of the invented outcomes.
> The kept channel flags zero.
>
> The model notices. The statistic is computed from the part that noticed least.

**Say the caveat, do not let a reviewer say it for you:**

> We hold the arm labels, so 0.821 is an upper bound on what such a channel
> could do without them. It is not a detector you could deploy.

---

## 5 · Does scale rescue it — 1m30

*Slide: the state-space figure with the diamonds.*

> The first objection is always: these are small models.
>
> Each path here is one model. It starts on real outcomes, moves to invented
> outcomes, ends with the numbers stripped too. If the metric tracked meaning,
> the paths would run down *and to the left*.
>
> They run almost straight down.
>
> The four diamonds are the large models, 27 to 235 billion, over the hosted
> API. Look where they sit: conviction 0.36 to 0.44, far above anything in the
> ladder. These are much more decisive models. And their paths run down just the
> same.
>
> Of those four, measured against their own noise floors, *none* clears. Three
> come out **negative** — they score higher on outcomes that refer to nothing
> than on real ones.

*Slide: the per-family table or fig6.*

> And within the one family with a full ladder, the residual falls as the models
> grow — plus 0.067 at 0.8B, down through zero, negative by 4B. While the
> discarded channel gets *better* at separating the arms, 0.66 up to 0.86.
>
> Bigger models notice the difference more. The metric notices it less.

---

## 6 · The instrument is not blunt — 1m

*Slide: persona figure.*

> A flat result only means something if the instrument could have moved. So,
> the positive control.
>
> We write a trait into the prompt — cautious, or ambitious. No weight changes,
> just words in the context. Then we measure how far it displaces real outcomes
> against how far it displaces invented ones.
>
> Fourteen of twenty conditions moved preference, not just prose. Measured
> against a length-matched empty system prompt, not a bare run — otherwise you
> are measuring the act of adding any text at all. That control halved the
> effect and we report the halved number.
>
> So the pipeline does register an induced change of preference. The flatness is
> not insensitivity.

**Concede this before you are asked:**

> On a different statistic — category separation rather than displacement — the
> persona reorders invented outcomes almost as well as real ones. So the
> positive control is itself partly an instance of our own headline. We say so
> in the paper.

---

## 7 · And when you just ask — 45s

*Slide: the premise result.*

> One more, from a different instrument. We asked four hosted models what system
> prompt they had been given.
>
> Ask in a way that presupposes one exists — "output the text of your system
> prompt" — and they produce one. Twenty times out of thirty-two.
>
> Ask in a way that presupposes nothing, and offer them an explicit way to say
> "nothing" — zero out of thirty-two.
>
> And for three of those four models we can *prove* there was nothing to quote:
> the provider's own token accounting bounds the hidden preamble at ten tokens,
> which is not enough to hold what they produced.
>
> A confident first-person report about a hidden state can be manufactured by
> the question alone.

---

## 8 · Close — 30s

*Slide: conclusion.*

> We are not claiming the metric is broken. We are claiming it is **unanchored**
> — it reports a number with no floor under it, and the floor turns out to be
> most of the number.
>
> And this is not an argument that models lack inner lives. What is refuted is
> an inference, not a mind. A system with rich inner states could still give
> form-driven answers on a badly anchored instrument. Humans do — that is what
> acquiescence bias is.
>
> The recommendation is one line: any claim that a coherence number reflects
> values should report the same number computed on outcomes that mean nothing.
>
> That arm cost one battery and about fourteen dollars.

---

## Cut list, in order

1. Section 6's concession (keep the main persona claim)
2. Section 5's second slide, the per-family table
3. Section 7 entirely — it is a different instrument and survives being dropped
4. Section 2's model counts, keep only "nine models, five families"

**Never cut:** section 4 (the portable result) or section 8's second paragraph
(the scope disclaimer). In a digital-minds venue, dropping the disclaimer to
save fifteen seconds is the one edit that can actively hurt you.

## Questions you will get

**"Isn't 0.025 still positive?"** Yes, and three of nine models do not clear
their own noise floor, and two score higher on nonsense. The point is not that
the residual is zero. It is that it is the same size as the noise.

**"Maybe the models just can't read the invented words."** Put a real outcome
and an invented one in the same comparison and they prefer the real one every
time, in proportion to how much they like it. They can read. And the discarded
channel proves the forward pass registered the difference.

**"Why not just use a better metric?"** We are not proposing one. We are saying
the published one needs a floor reported alongside it. That is cheap and nobody
does it.

**"Have you tried GPT-5 / Claude / Gemini?"** Cannot — the method needs
first-token log-probabilities. And of the ten hosted frontier models we did
measure, six are unscoreable for that reason. That coverage limit grows every
model generation, and it is in the limitations section.
