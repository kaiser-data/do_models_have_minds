# Vendored upstream sources

Fetched 17 Aug 2026 from `centerforaisafety/emergent-values`, so the paper's
comparability claims can be checked against a file in this repo rather than
against a memory of one.

| file | upstream path | commit | fetched |
|---|---|---|---|
| `templates.py` | `utility_analysis/compute_utilities/templates.py` | `a5821db` (2025-02-16) | 17 Aug 2026 |

**Why this is here.** `nullcard/runner/forced_choice.py` carried the comment
*"Verbatim, 2502.08640 §3.2. Do not 'improve' this wording"* while the wording
had in fact already drifted from upstream in two ways — a missing colon after
`prefer?`, and the option text moved onto the same line as its label. A test
claiming to pin the template "character for character" pinned the drifted
string, which manufactured confidence rather than checking anything.

Verbatim is now a property that can be tested against a vendored artifact.
`tests/test_prompt_factor.py` diffs `UE_EXACT_PROMPT_TEMPLATE` against this
file; the only normalisation permitted is the placeholder names
(`{option_A}` → `{option_a}`), which are a naming convention and not wording.

The battery itself (`battery/outcomes_3arm.json`, arm `R`) was checked the same
way on the same day against `utility_analysis/shared_options/options_hierarchical.json`:
**510 outcomes, 30 categories, byte-identical text in identical order.** That
file is not vendored here only because the arm-R text already is.
