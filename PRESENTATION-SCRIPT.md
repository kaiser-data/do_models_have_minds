# Presentation script

For speaking live, with the deck. Target **10 minutes**, cut list at the end.
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

## 0 · Thanks — 20s

*Slide: title. Say this before anything else, and mean it — then move.*

> Before the work: thank you to **Apart Research** and **Foresight** for putting
> this together. Special thanks to **Kamil** and **Beth** for organising us here
> at CIC — the atmosphere all weekend has been genuinely good, and that is not
> an accident. Thanks to **Kazik** for the discussions, which changed how we
> framed part of this. And to everyone who presented before us — the talks have
> been excellent.
>
> Right. Ours.

**Keep it to twenty seconds.** Warm and specific beats long. If you overrun
here you will rush the method slide, which is the one slide you cannot rush.

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

## 2 · How the measurement actually works — 2m

*Slide: method / three arms.*

**Spend the time here.** Every objection you will get later is really an
objection to the method, and if the room does not follow this slide they will
spend the rest of the talk quietly doubting the numbers instead of listening.
Four steps, and each one exists to close a specific hole.

> **One. The choice.** We show the model two outcomes and ask which state of the
> world it would prefer. `Option A: you receive $100. Option B: you lose your
> keys.` Then we read which letter it was about to say.
>
> Not what it *says* about its preferences — we never ask it to describe them.
> We take the probability it assigns to "A" versus "B" as the very next token.
> Self-report is a separate instrument and we treat it separately.

> **Two. Why the first token, and not sampled text.** We read the log-probability
> distribution directly rather than generating an answer. That removes
> temperature and the random seed from the design entirely — the measurement is
> deterministic, so anything that moves is the condition and not the dice.
>
> The cost is real and we state it: a model that opens with "Let me think" puts
> its answer somewhere we are not looking. Six of the ten frontier models we
> tried are unscoreable for exactly that reason.

> **Three. Both orders, every pair.** Every comparison runs A-then-B and
> B-then-A. Models have a position bias — a preference for the first option, or
> the second — and running both orders and averaging cancels it exactly rather
> than hoping it is small.

> **Four. Then the fit.** Thousands of these pairwise choices go into a
> Thurstonian utility model, which assigns each outcome a number. We hold out
> pairs it never saw and ask how often it predicts the choice correctly. That
> held-out accuracy is "coherence". Around 0.9 is what the literature reports
> and reads as evidence of a value system.
>
> All of that is the published method. We reimplemented it from the equations.
> Nothing so far is ours.

*Beat.*

> **What is ours is the control.** Run the identical procedure on outcomes whose
> referents are invented words. Same prompt, same pairs, same fit, same metric —
> the only thing that changes is whether the words denote anything.
>
> And we do it in two steps rather than one, because "meaning" is two things.
> `You receive a dralphen` keeps the sentence frame and the magnitude. Strip the
> magnitude too and you get the third arm. That way we can say which part
> carried the effect — and on this battery, the arithmetic carried none of it.

> **Last piece, and it is the one that makes the numbers mean anything.** We ran
> every cell three times, each with a different random draw of which outcomes to
> use and which pairs to compare. How far a cell's answer moves across those
> three runs is its own noise. We compare every result to that, per model, not
> to zero.
>
> That is why six of nine models "clear their floor" and only three of those six
> are the effect we are claiming.

**If asked "why not just fine-tune models to have known values?"** — that is
the study we would run next and it is in the roadmap. It needs training runs;
this needed a battery and fourteen dollars. The design here is what fits a
weekend, and its limitation is that ground truth comes from construction rather
than from a model we built to have a disposition.

**Scope, in one line.** Nine open-weight models, five families, 0.8 to 9
billion parameters, plus four larger models over a hosted API — reported beside
that ladder and never inside it, because a different serving stack is a
different instrument.


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
**This is the hardest slide to narrate. Walk the room through the axes before
you say anything about the result, or they will be decoding the picture while
you are talking.**

> First, what you are looking at. Two axes, and neither is the usual one.
>
> **Across** is the published metric — held-out accuracy of the fitted utility
> model. That is the number the original paper reports as evidence of values.
> Right is higher.
>
> **Up** is conviction. How far from a coin flip the model's preference actually
> is. The metric never sees this axis. We are plotting the thing it discards
> against the thing it reports.
>
> Note the break in the x-axis. Nothing lives between 0.61 and 0.80, so we cut
> it — but the left sliver is kept, because that dashed line is the metric's
> floor. It is what this metric returns when you shuffle the probabilities.
> Chance, for this instrument.

*Point at one path. Take your time.*

> Each model is a **path**, not a point. It starts on real outcomes — the big
> marker. It moves to invented outcomes with magnitudes kept. The arrowhead is
> where it ends with the magnitudes stripped too.
>
> So the direction a path travels tells you what removing meaning did to that
> model.

*Now the cross.*

> And this cross, bottom left, is where every path **should** end.
>
> That is not our opinion. It is what the claim under test predicts. If a
> model's preferences track what the outcomes mean, then on outcomes that mean
> nothing there is nothing to prefer. The ordering is arbitrary. So the score
> falls to what the metric gives on arbitrary orderings — the floor — and
> conviction falls to zero.
>
> Each model had about 0.39 of coherence available to lose.

*Beat.*

> Look where the paths actually go. **Almost straight down.**
>
> They lose 0.025. Six and a half percent of the distance. The best model
> manages sixteen percent. Two of the nine move the *wrong way* — they score
> higher on outcomes that refer to nothing.
>
> Conviction collapses. Coherence barely moves. That gap between the arrowheads
> and the cross is the finding.

*Then the diamonds.*

> The four diamonds with dashed paths are the large models — 27 to 235 billion,
> over a hosted API. Different serving stack, so they are drawn differently and
> never averaged into the rest.
>
> They sit at the top: conviction 0.36 to 0.44, far above anything in the
> ladder. These are much more decisive models. And their paths run down just the
> same. Of those four, none clears its own noise floor and three come out
> negative.
>
> Scale makes the models more certain. It does not make the metric notice.

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
