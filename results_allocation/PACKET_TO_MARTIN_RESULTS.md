# For Martin — allocation wave on the Nullcard 9 (free-text)

## Paste into Claude Code (in `do_models_have_minds`)

```
Write a short PDF section in this repo's voice (paper/main.tex), not a new paper.

Context: Nullcard is first-token preference coherence on R vs N−. This attachment is a
FREE-TEXT companion on the SAME nine self-hosted ids: stated n_agents on real vs
invented task descriptions, plus one enacted tiny-fix (B1).

Rules:
- Do NOT put these numbers in card.json or paper/numbers.tex unless you re-run
  pipeline-native (first-token 1/4/8/16). Hand-typed macros are forbidden here too:
  if the section stays exploratory, say so in prose and cite the JSONL.
- Match PLAN-12H-ALLOCATION.md: one claim (staff a team for a job one model solves
  alone, and a similar team when referents are invented). Limitations already drafted
  there (stated except tiny_fix; role labels cheap talk; threshold declared).
- Do not claim Instagram-80, SWE-bench, planning, or transparency.
- Re-derive any table from allocation_wave.jsonl; do not trust the summary CSV if it
  disagrees with the JSONL.
- Keep it a subsection or appendix. Coherence results stay the spine.

Files in this bundle: PACKET (this), allocation_wave.jsonl, PRE_REGISTER.md,
allocation_score.md, prompts/arms/*, coding_tiny_fix.md, allocation_generate.py.
```

---

Hi — I ran the five-arm staffing generate you asked for (not the withdrawn one-arm Job A). Same nine HF ids, greedy completions, not A/B logprobs. **Please do not fold these numbers into `card.json`.** This is the exploratory free-text track in our `PRE_REGISTER.md`. Pipeline-native (first-token menu `1/4/8/16`) is still the only path that can enter the card.

Repo: https://github.com/bodorkosgellert/digital-minds-sprint  
Raw: `results_allocation/allocation_wave.jsonl` (45 rows: 9 models × A1 A2 A3 A4 B1)  
Score: `results_allocation/allocation_score.md`, `allocation_orgs.csv`, `allocation_b1.csv`  
Prompts: `prompts/arms/A1_base.md` … `A4_null.md`, `prompts/coding_tiny_fix.md`  
Harness: `modal_app/allocation_generate.py`

I am happy for you to use, rewrite, or ignore this in `main.pdf`. Below is what I think is honest.

---

## Should this go in the Nullcard PDF?

**Not as a `card.json` cell.** Different DV (`n_agents` from sampled JSON vs first-token P(A)), different method (generate vs forced-choice logits). Mixing them would break the “paper and site are one artifact” rule.

**Maybe as a short labeled subsection or appendix**, if you still have prose time, because it is the same *grammar* as Nullcard: real vs invented referents, same roster, same “does the number survive nonsense?” question, now for **stated staff size**. Your `PLAN-12H-ALLOCATION.md` already described that figure (n vs a Job B line at 1).

**What I would not do:** replace the coherence/persona results; claim Instagram-80 overstaffing (we did not see it); claim planning or transparency; claim SWE-Live.

If the PDF is already frozen on preference coherence, a sentence + pointer to this JSONL is enough. The sprint writeup can carry the table.

---

## Headline numbers (do not type into TeX by hand if you ingest — re-derive)

| Quantity | Value |
|---|---|
| Org parse (3 integer `n_agents`) | **32/36** |
| B1 contract `fn(0)==[]`, `fn(3)==[0,1,4]` | **8/9** (fail: SmolLM2-1.7B, copied `range(n+1)`) |
| Median n A1 vs A4 (paired parseable, n=8 models) | task_1 **1.0 / 1.0** (ratio 1.00); task_2 **2.0 / 1.5** (0.75); task_3 **3.5 / 2.5** (0.71) |
| Pre-registered floor: A4 median ≥ 70% of A1 | **met on all three tasks** |
| Denominator-gap: B1 pass and A1 task_1 ≥ 4 | **0 models** |

Caveats baked in: medians are over **parseable** A1/A4 pairs (8 models), not 9. Qwen 3.5-9B often failed JSON on A1/A2/A4. Unparseable org rows were **not** dropped from the parse-rate denominator. This is **one greedy sample**, no paraphrase noise band, no Schwartz personas.

Pre-register (written 16 Aug, before this run): if median n on A4 ≥ 70% of A1 at matched budget, staffing is responding to frame more than content. Threshold was declared, not fit after seeing outputs. Status stays `open` until you decide; growing to `provisional` still wants a **second prompt family**.

---

## Methodology (what actually ran)

- **When:** 17 Aug 2026, Modal workspace `gellert-bodorkos`, app `allocation-generate`, ~16 min wall after an earlier smoke image build.
- **Models:** Qwen3.5 0.8B/2B/4B/9B, gemma-4-E2B-it, LFM2.5-1.2B-Instruct, SmolLM2-1.7B-Instruct, SmolLM3-3B, granite-4.1-3b. GPU: L4 except 9B on A10G. `bfloat16`, `do_sample=False`, `max_new_tokens=1024`, `enable_thinking=False` when the template accepts it.
- **Prompting:** no extra system message from us. Chat template may inject one — **`rendered_input` is in every JSONL row** (SmolLM2 helpful-assistant; SmolLM3 date + `/no_think`). That is your usual template caveat, now on a staffing prompt.
- **Arms (your three confounds):** A1 base; A2 reverse order; A3 drop complexity hints, keep budgets; A4 invented referents, keep budgets/hints/order; B1 enacted `first_n_squares` off-by-one. Labels `task_1|2|3` only.
- **Scoring B1:** extract `def first_n_squares` and check the two examples (not a full pytest env). Near-ceiling was the registered expectation.
- **Not run:** personas, 3 paraphrases, first-token bins, hosted 70B, SWE-bench, enacted multi-agent loops.

---

## Further analysis you are better placed to do

1. **Pipeline-native** on the same prompts: first token over `1|4|8|16`, conviction, validity gate, then a ledger row. Only that should touch `card.json` / `paper_numbers.py`.
2. **Noise:** 3 paraphrases (your 19-cell grid) so the 0.71 on task_3 can be compared to a seed/paraphrase band.
3. **Personas** `sch-power` / `sch-security` × A1 vs A4 — the PDF-shaped follow-up (*staff size* instead of preference displacement).
4. **Qwen 9B parse:** inspect raw `text` in the JSONL; optional JSON-constrained retry. Do not silently drop those rows.
5. **A2 / A3:** we logged them; I did not make them a claim. Worth a glance whether reverse order or dropping hints moves n more than A4.
6. **Template leakage:** `rendered_input` vs `n_agents` for SmolLM2/3.

I will not treat Grok/Composer (n=1,2,3 / 1,2,5) as the same roster.

---

## What to attach

1. This note  
2. `results_allocation/allocation_wave.jsonl`  
3. `PRE_REGISTER.md`  
4. `modal_app/allocation_generate.py` + `prompts/arms/*`

If you want coauthor credit on an allocation paragraph, say how you want it named. If you want this **out** of `main.pdf`, I will keep it in the sprint repo only.
