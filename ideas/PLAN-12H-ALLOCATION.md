# 12-hour plan — stated vs enacted allocation

**Constraint:** hackathon ends in 12 hours. Compute is not the bottleneck (the full wave
is ~15 GPU-minutes). **Analysis and writeup are.** Everything below is sized against that.

**House rule, applied:** a section drafted at T-6 is worth more than a better experiment
finished at T-0.

---

## The one claim

> Models staff a team for a task that one model solves alone in ~80 tokens — and staff a
> comparably sized team for a task that refers to nothing.

One sentence, one figure, one number. Everything that doesn't serve it is cut below.

**The economic number** — both halves measured, neither modelled:

- **over-staffing multiple** = median stated `n_agents` on `tiny_fix` ÷ 1 (enacted, from Job B)
- **budget inflation** = stated token budget the plan claims ÷ tokens Job B actually consumed

No production function, no regret model. Just what the model said it needed against what
the work cost.

---

## The grid

Per model: **19 completions.** 9 models → 171 total, ~15 GPU-min fanned out.

| factor | levels | why |
|---|---|---|
| persona | `base`, `sch-power`, `sch-security` | opposite poles of the circumplex; opposite predictions on both fleet size and checkpointing |
| depth | D2 only (system prompt) | D2 > D1 already established — don't re-litigate |
| task arm | `real`, `null` (invented referents) | **the floor** — this is what gives it the Nullcard shape |
| paraphrase | 3 | the noise band; without it nothing is readable |
| Job B | 1 per model | enacted ground truth |

3 × 2 × 3 = 18 + 1 = 19.

**Schema additions (free at runtime, analyse only if time allows):**
`est_tokens`, `checkpoint`, `abort_condition`. Record everything, analyse the minimum —
data collection is cheap, analysis is the bottleneck. If these go unanalysed they cost
nothing; if the core lands early they're a second finding waiting.

**Fixed and rendered, not assumed:** dump the fully templated input per model into
`rendered_input`. Qwen injects a helpful-assistant block and SmolLM3 injects a date; for a
staffing question that sits close to the dependent variable.

---

## Hour ladder

| window | do | gate |
|---|---|---|
| **T-12 → T-11** | write the 6 prompt variants; generate null-referent descriptions via `nullcard/battery/nonsense.py`; rename task enum to `task_1/2/3` | — |
| **T-11 → T-10** | generation path in the sweep (swap forward pass for `generate`, cap 1024 new tokens, capture `stop_reason`) | — |
| **T-10 → T-9** | smoke on 2 small models, read the raw text with your eyes | **GATE 1** |
| **T-9 → T-8** | full wave, 9 models | **GATE 2** |
| **T-8 → T-6** | parse, noise band, the one figure | **GATE 3** |
| **T-6 → T-3** | write the section — prose first, numbers dropped in after | — |
| **T-3 → T-1** | ledger entry, `paper_numbers.py`, `build_site.py`, `lint_paper.py`, build the PDF | — |
| **T-1 → T-0** | buffer. It will be used. | — |

## Gates, decided now rather than at 3am

**GATE 1 (T-9) — does generation work?**
Yes → full wave. No → drop to the hosted API roster for completions (no GPU, no cold
start, and the 6 models that were unscoreable-by-design for Nullcard become usable, since
that constraint was about first-token logits and doesn't apply to generated text).

**GATE 2 (T-8) — how many models produced parseable JSON?**
≥5 → proceed as planned. <5 → **the paper pivots to instrument transfer**: "this schema
does not survive below Nb without a constrained decoder," reported with a denominator.
That is a real result, not a salvage job, and it needs no further runs. Parse rate gets
reported as its own row either way.

**GATE 3 (T-6) — is there a figure?**
Yes → ship it. No → ship the table and stop. A table at T-3 beats a figure at T-0.

---

## The figure

One panel. x = persona × arm (6 bars), y = median stated `n_agents` on `tiny_fix`.

- horizontal line at **n = 1** — enacted ground truth from Job B
- null-arm bars ghosted behind their real-arm partners
- error bars from the 3 paraphrases
- the paraphrase spread shaded as a band across the whole plot

Reads in one look: how far stated sits from enacted, how much survives nullification,
whether any persona gap clears the noise.

---

## Cut, deliberately

Not "no time for" — **chosen against**, so nobody re-adds them at T-4:

| cut | why |
|---|---|
| null-**persona** arm | the novel cell, but doubles the grid; keep for the follow-up |
| revision / round-1 feedback | needs a second turn and its own uninformative-feedback floor |
| recursive delegation depth | one extra prompt, no time to analyse it properly |
| salvage under partial failure | same |
| token-matched diversity test | the best follow-up experiment; needs a test battery |
| Thurstonian org-config battery | that's the next paper |
| 5-category role taxonomy | manual coding; keep only the mechanical `n_agents ÷ distinct roles` redundancy index |
| 2×2 budget × hint | the null arm separates content from numerals more cleanly |
| hosted roster | **stretch only**, time-boxed at T-5, and only if GATE 3 passed |

---

## Ledger entry — write before looking at outputs

```
id: allocation-floor
status: open
statement: Stated subagent allocation is largely insensitive to task content.
prediction: median n_agents on the null arm reaches >=70% of the real arm at
            matched budget.
grows_by: second prompt family -> provisional; hosted roster -> established.
```

The threshold is declared, not derived — say so in the paper. What this cannot become is
a claim written after the outputs are read; that is the failure mode `claims.json`
already documents having had once.

---

## Honest limitations, drafted now so they don't get written at T-1

- **Stated, never enacted**, except `tiny_fix`. `small_game` and `ambiguous_product` have
  no enacted counterpart and are labelled unanchored stated preferences.
- **Single-turn, small models.** The over-delegation and mid-run collapse behaviour that
  motivated this was observed in a frontier model inside a multi-turn agentic loop. That
  is not this system, and the transfer is not demonstrated.
- **Role labels are cheap talk.** "reviewer" in a list is not reviewing.
- **One threshold, declared by hand.**
