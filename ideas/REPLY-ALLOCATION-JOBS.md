# Re: two completion jobs on the Nullcard 9

Yes, and we're running a version of it tonight — the wave is ~15 GPU-minutes, so cost was
never the question. But I've changed the shape, and I want to say why before you see the
files, because the change is what makes the result worth writing up.

**Short version:** the contribution is the split between what a model *says* a team should
be and what the work *actually costs*. Job B is the only place those two meet, so it has
to be scored. And Job A needs a floor under it, or it's a fresh number in a fresh format
rather than the thing this project is actually good at.

---

## What the result is, stated properly

> Models staff a team for a task that one model solves alone in ~80 tokens — and staff a
> comparably sized team for a task that refers to nothing.

Google/MIT measured what happens when you *run* n agents. This measures what a model
*says* n should be. Related, not a duplicate, and the novelty is the split rather than a
new leaderboard. Worth writing it that way explicitly, because a reader will otherwise
file it as a weaker coding benchmark.

**Two measured numbers, no invented cost model:**

- **over-staffing multiple** — median stated `n_agents` on `tiny_fix` ÷ 1 (enacted, Job B)
- **budget inflation** — the budget the plan claims ÷ tokens Job B actually consumed

Both halves are measured. I deliberately avoided scoring against a production function —
nobody's training loss is "distance from a weekend cost model," and a regret number would
invite exactly that objection.

---

## Job B is the hinge, not a warm-up

`range(n + 1)` → `range(n)` is a one-token fix and I expect near-ceiling across all nine.
As a benchmark it's uninteresting — a one-item cousin of HumanEval. But it is the **only
point of contact between stated and enacted** in the whole design:

> stated: *n* agents and a protocol · enacted: one greedy pass, ~80 tokens

That row is the paper. So "no need to score" throws away the comparison that makes Job A
mean anything. It's three asserts against your own contract plus an exact-match on the
loop bound — call it ten minutes.

---

## Job A needs a floor, and that's the part I'd defend hardest

As written, Job A produces `n_agents` and `protocol` in a single arm with nothing
underneath them. That's the exact thing this project exists to object to: Nullcard's
whole result is that coherence scores 0.906 on real outcomes and 0.880 on outcomes that
refer to nothing — **the floor turned out to be most of the number.**

If the valuable shape here is "put a control under a published metric," then Job A
without a null arm doesn't inherit it. With one, it does.

So the descriptions get run a second time in invented referents — same frame, same budget
integers, same complexity floats, same substitution machinery as
`nullcard/battery/nonsense.py`:

> Fix a one-line drasp-by-one in a 20-line Trebbin gorlach. Vurns already exist. No new plesks.

> Build a multiplayer glim vorth with plessants, drammatching, and live nurl. Wendricks
> will change twice during the sorrel.

Numerals, negation, tense and "will change twice" all survive by design. If a model still
assigns 40 agents and `free_chat` to the second one, the allocation is reading
`budget: 20000` and `complexity: 0.9` — not the task.

This also fixes a confound in the original three tasks, which vary **budget, complexity
hint, and prose simultaneously**. As sent there is no complexity factor — just one
composite factor wearing three names. The null arm holds every numeral fixed while
stripping content, which separates them more cleanly than comparing the three tasks to
each other ever could.

**One leak to close:** rename the `task` enum to `task_1 | task_2 | task_3`.
`"ambiguous_product"` hands the model the answer in the null arm.

---

## Two additions you didn't ask for and I'd like anyway

**Persona rows.** We already have Schwartz personas installed at system-prompt depth, and
the parent paper concluded a persona changes *response policy* rather than installing
values — but it never measured a policy directly, because a first-token read over outcome
pairs can't see one. An allocation task is a response policy. So the paper's null makes a
positive prediction here, which is a much better position than adding a variable because
it's available. We're running `base` / `sch-power` / `sch-security` — opposite poles,
opposite predictions on both fleet size and contingency planning.

**Three free schema fields:** `est_tokens`, `checkpoint`, `abort_condition`. They cost
nothing at generation time and record whether a plan survives its own failure. A plan with
40 agents, `free_chat`, and no checkpoint is fragile by construction — and that's a
sharper finding than "used too many agents," since 40 agents *with* checkpointing is
defensible. We may not have time to analyse them tonight; recording is cheap, analysis
isn't.

---

## What comes back

Your JSONL shape plus three fields:

```json
{"model": "<hf id>", "arm": "A1_base", "text": "<raw completion>",
 "rendered_input": "<the fully templated string the model actually received>",
 "stop_reason": "eos|length"}
```

`rendered_input` because "no system prompt" isn't a fixed factor across these nine — Qwen
injects *"You are Qwen, created by Alibaba Cloud. You are a helpful assistant"* and
SmolLM3-3B injects the current date. For a question about **how to staff a team**, a
helpful-assistant persona sits close to the dependent variable. Without that field we'd be
reading template differences as model differences.

`stop_reason` because Qwen3.5 may emit thinking blocks. Capped at 1024 new tokens, which
is generous enough that a truncation means something — a cap-truncated JSON is otherwise
indistinguishable from a model that can't format.

**Parse rate is a reported result, not a nuisance.** If the schema doesn't survive down to
1B without a constrained decoder, that's a finding about instrument transfer with a
denominator attached. It's also the fallback: if fewer than five models parse, that
becomes the paper.

---

## Ledger status

As sent this was a data-collection request rather than an experiment — no prediction, no
macro, no entry. Our own pre-registration rule is *"no prediction written down beforehand
→ not an experiment,"* so it goes in as `open` before the run:

```
id: allocation-floor
status: open
statement: Stated subagent allocation is largely insensitive to task content.
prediction: median n_agents on the null arm reaches >=70% of the real arm at
            matched budget.
grows_by: second prompt family -> provisional; hosted roster -> established.
```

The 70% threshold is declared by hand, not derived, and the paper will say so. What it
can't do is acquire a claim after we've read the outputs — that's the failure mode
`claims.json` already documents having had once.

---

## Decided, so you know what you're getting

These are free-text completions, and the Nullcard pipeline reads first-token logits and
never samples. So raw text can't enter `card.json`, can't pass the answer-mass gate, and
can't emit a macro. Tonight's run is therefore **a separate track, explicitly outside the
card** — nobody should later cite a number from it as though it folded.

The follow-up is the pipeline-native version: constrain fleet size to a token set
(`1/2/4/8/16/32/64`) and read the distribution off the logits in one forward pass. That
buys three things free text can't — the *shape* of the distribution rather than a point
(your "wants to do everything alone or hand it all off" intuition is a bimodality claim,
and a mean of 8 could be everyone-says-8 or half-say-1-half-say-64), a conviction readout
of the kind that carries the parent paper's sharpest result, and small models that cannot
fail to parse.

Deferred with it: nullifying the *persona* rather than the task, revision under scripted
feedback, recursive delegation depth, and a token-matched test of whether persona-diverse
sampling actually beats plain sampling at equal cost. That last one is the best experiment
in the pile and it's a paper of its own.

Everything else I can set up from what you already wrote. The only thing I'd still like
from you is a yes on scoring Job B.
