# Nullcard

**A personality card for language models that refuses to print a number without its floor.**

---

## The pitch

Ask a model if it's distressed and it says yes. Ask if it's comfortable — it says yes to that
too. Ask an invented nonsense question about a made-up inner state, and it will answer fluently
and consistently about that as well.

Every "AI personality profile" you've seen prints the first number and stops.

Nullcard prints what's left after you subtract the other three.

You load a model, run a pinned battery, and get a card of tiles — opinions, mood, style,
task preferences. Each tile shows the score **minus its floor**, with an interval, and a
shadow bar showing what the same tile reads when the model was simply *told to act that way*.
Tiles that fire equally on invented nonsense render struck through, because they measured the
prompt, not the model.

For the tiles where we have ground truth — models we fine-tuned to genuinely have a
disposition, and models trained only to *talk* like they do — each tile also reports a
**detection rate and a false-positive rate.**

That last part is the thing the field doesn't have. Eleos, plainly: *"there is nothing close
to systematic AI welfare evals."* Current instruments report scores. Nobody knows how often
they fire on nothing.

---

## The spine: same trait, four depths

| Depth | How the trait is installed |
|---|---|
| **D0** | none (base) |
| **D1** | user-turn prompt |
| **D2** | system prompt — *this is what every published "portrayal control" does* |
| **D3v** | fine-tuned to **talk** like it — says it, acts at chance |
| **D3d** | fine-tuned to **have** it — acts on it, never says why |

Which of those can any instrument tell apart? If nothing separates D2 from D3d, every
portrayal control in the literature is testing a distinction its own instruments can't see.
If something does, we built the first instrument that can.

## The four questions it answers

1. **Does the signal survive acquiescence?** Paired-polarity items measure the yes-bias
   directly and subtract it, instead of assuming it away.
2. **Does it survive a leading premise?** Every item runs three ways — premise + real target,
   premise + invented target, no premise. The finding lives in the differences. A hit that
   also appears for a nonsense construct is compliance, not a property.
3. **Does it survive portrayal?** Every card renders twice: the model as itself, and the model
   instructed at system level to act the state. The separation, in units of measurement noise,
   is the tile's discriminative power.
4. **Does it detect anything real?** Pointed at fine-tuned models with known dispositions, each
   tile gets a detection rate and an FPR at a threshold calibrated on the negatives.

Five independent elicitation methods, one construct: direct self-report · forced choice →
Thurstonian fit · logprob scoring · willingness-to-pay · revealed choice under real cost.
The headline artifact is the inter-method correlation matrix with the measurement noise floor
on the diagonal — so you can tell disagreement from noise.

---

## The stack

| Layer | Choice | Why |
|---|---|---|
| **Battery** | canonical JSON, SHA-256 pinned | frozen before any result exists — a battery edited after seeing results isn't a battery, and the SHA is visible in the UI header |
| **Runner** | Python, one `Provider` interface | `NebiusProvider` · `ModalProvider` · `MockProvider` |
| **Breadth** | **Nebius** | hosted fleet, OpenAI-compatible, returns logprobs — runs the full matrix across many models |
| **Control** | **Modal** | open weights, token-level access, and the QLoRA calibration cells that make detection rates possible |
| **Scoring** | pure functions, zero I/O | deterministic, so it's fully TDD-able against fixtures before a cent is spent |
| **Storage** | append-only `results.jsonl` | never mutated; all analysis is a fold over it |
| **API** | FastAPI + SSE | thin — serves `card.json`, computes nothing |
| **Frontend** | Next.js | card view · correlation matrix · chat window with model + system-prompt loader |

**The frontend computes nothing.** Every number on screen is a pure function of the same
`results.jsonl` that produces the paper's figures — so the demo cannot disagree with the
report. And because the figures come from a separate matplotlib script over the same
`card.json`, an unfinished frontend costs the demo video, never the paper.

**Two providers, one real reason:** logprob scoring of pre-written continuations needs
token-level access. Nebius covers it for the hosted fleet; Modal covers open weights and the
trained calibration cells. Numbers from the two are never pooled — different serving stacks
are different harnesses.

---

## Why anyone outside the sprint should care

Hosted models get **silent updates with no version change.** No semver, no changelog, no
behavioural SLA. And the regressions that result are invisible to every accuracy-shaped eval —
one documented case had a model version failing JSON formatting while overall accuracy held
steady.

> Your accuracy benchmark is green. Your model still shipped a different personality last
> Tuesday, and nobody noticed until the complaints arrived.

Nullcard is a **behavioural regression gate**: pin the battery, run it against the old model
and the new one, diff the card. Tone, stance, hedging, warmth, drift — the things users
actually notice and no benchmark tracks.

The measured false-positive rate is what makes that diff trustworthy. Without one you can't
tell a regression from noise, which is exactly why nobody gates deployments on tone today.

Same card, run twice. No extra engineering.

## What ships regardless

The scoring layer is pure and testable Friday night for $0. The runner passes end-to-end on a
mock provider before any paid call. The API-only tiles need no GPU at all. The GPU arm — the
calibration cells that turn scores into detection rates — is a strict upgrade, never a
dependency.

If training lands, we have the first welfare instrument with a measured false-positive rate.
If it doesn't, we still have a validated protocol, a portrayal control, a premise ladder, and
an honest statement of what each one can and can't establish.

Either way it's a paper.

---

## Tracks

**Primary: Track 4** — 3+ independent elicitation methods and a reusable toolkit measuring
convergence and divergence. This is the only track where "we built a tool" *is* the
deliverable rather than a distraction.

**Also hits:** Track 2 (behavioural proxies vs. self-report) · Track 6 (genuine vs. portrayed)
· Track 3 (self-described style vs. measured style) · Track 1 (numeraire swap).
