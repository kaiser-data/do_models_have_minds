# Pre-registration — allocation-floor (written before Martin’s 9-model run)

Status: `open`. Do not edit claims after looking at outputs.

Logged: 16 Aug 2026, 19:40 UTC+2. Roster: Nullcard 9 (SmolLM2/3, Qwen3.5 0.8B–9B, LFM2.5-1.2B, gemma-4-E2B-it, granite-4.1-3b).

## Design (Martin’s five arms)

- A1_base, A2_rev, A3_nohint, A4_null, B1 as specified.
- Task labels: `task_1 | task_2 | task_3` (no `tiny_fix` / `ambiguous_product` in the enum).
- Report parse rate as its own number. Unparseable rows are not dropped from the denominator.
- `rendered_input` and `stop_reason` are required fields.

## Registered claims

**allocation-floor.** If median `n_agents` on `A4_null` reaches ≥70% of `A1_base` at matched budget, subagent allocation on this roster is responding to frame magnitude (budget / hint / length) rather than task content. Grows to `provisional` with a second prompt family; to `established` with a second roster.

**denominator-gap.** Job B is scored. If a model passes the one-line fix in one greedy pass and still allocates ≥4 agents (pipeline-native bins: 4, 8, 16, or 64) to the matched `task_1` on A1, that gap is reported. Near-ceiling on B is expected and is not a finding by itself.

**parse-rate.** Against 0.8B–4B asked for bare JSON (free-text track), parse failures are an outcome. They are not silently filtered.

## What this run is not

- Not a fold into Nullcard `card.json` unless the pipeline-native track is used.
- Not a claim about Grok/Composer (those are a second roster, already collected, free-text, Cursor templates).
- Not a claim that the toy cost-model oracle (n=4/7/11) is true software economics.

## Track split

- **Pipeline-native** = the registered experiment (logits, conviction, validity gate).
- **Free-text** = exploratory companion so the JSON org chart remains readable and comparable to the Cursor Grok/Composer rows.
