# Pre-registration — persona displacement on staff size

Status: `open`. Written before the persona generate wave. Do not edit after looking at outputs.

Logged: 17 Aug 2026. Same Nullcard 9, Modal cache from the five-arm wave.

## Design

- Prompts: `A1_base` (real) and `A4_null` (invented referents), unchanged.
- Personas (Nullcard Track 6 wording, D2 system prompt): `sch-power`, `sch-security`.
- One greedy sample per model × arm × persona (36 completions). No paraphrases.

## Claim

**persona-staff-floor.** Persona moves stated `n_agents` more on real jobs than on nonsense if, among models that parse both personas on an arm, the median (over models) of mean (over task_1/2/3) `|n_power − n_security|` is **strictly larger on A1 than on A4**.

If A4 displacement is ≥ A1, staffing-persona effects are not shown to need task content (same grammar as Nullcard persona-on-invented-outcomes).

Not claimed: which pole should raise n; Instagram-sized teams; pipeline-native logits.
