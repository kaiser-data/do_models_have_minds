"""Tests for which hosted models the first-token metric can read.

The paper states this as a fraction -- \\HostedNUnscoreable of \\HostedNTotal --
and the macro that produces it adds two groups together:

    unscoreable = preamble + no_logprobs

That is arithmetic, not a measurement, and it is correct only while those two
groups stay disjoint and jointly cover everything that is not scoreable. Both
properties are consequences of how the predicates happen to be written today,
so a plausible roster edit breaks them without touching this file: give a model
`logprobs=False, first_token_ok=False` and it is already counted once, but flip
the preamble predicate to drop its `logprobs` term and the same model is
counted twice and the paper claims a larger fraction than was measured.

These tests fix the partition rather than the numbers. The counts themselves
are deliberately not asserted here -- adding a hosted model is supposed to
change them, and a test that pins them would only have to be edited in the same
commit that makes it wrong.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from nullcard.roster import NEBIUS, scoreable_hosted  # noqa: E402
from scripts.paper_numbers import _hosted_scoreability, _tex  # noqa: E402


def test_scoreable_requires_both_logprobs_and_first_token():
    # Either condition alone is insufficient: an API that returns logprobs for a
    # token that is not the answer reads a preamble, not a choice.
    for m in scoreable_hosted():
        assert m.logprobs and m.first_token_ok, m.api_id


def test_groups_are_disjoint():
    g = _hosted_scoreability()
    ids = {k: {m.api_id for m in g[k]} for k in ("ok", "preamble", "no_logprobs")}
    assert not ids["ok"] & ids["preamble"]
    assert not ids["ok"] & ids["no_logprobs"]
    # The one that actually protects the paper's arithmetic: a model refused
    # logprobs must not also be counted as a preamble failure.
    assert not ids["preamble"] & ids["no_logprobs"]


def test_groups_cover_the_whole_hosted_roster():
    g = _hosted_scoreability()
    covered = sum(len(g[k]) for k in ("ok", "preamble", "no_logprobs"))
    assert covered == len(NEBIUS) == len(g["all"])


def test_unscoreable_is_the_complement_of_scoreable():
    # The sentence in sec:limits reads "X are scoreable and Y are not", so the
    # two must exhaust the roster or the sentence is false regardless of how
    # either number was computed.
    g = _hosted_scoreability()
    assert len(g["ok"]) + len(g["preamble"]) + len(g["no_logprobs"]) == len(NEBIUS)
    assert len(g["ok"]) < len(NEBIUS), "a roster where everything scores makes sec:limits moot"


def test_model_names_are_latex_safe_as_macro_values():
    # Nemotron-3_5-Lightning carries an underscore, which is a subscript in math
    # mode and an error outside it. The macro values reach LaTeX verbatim.
    # An escaped underscore still contains the character, so the property is
    # "never unescaped" rather than "never present".
    import re
    for m in NEBIUS:
        escaped = _tex(m.api_id.split("/")[-1])
        assert not re.search(r"(?<!\\)_", escaped), m.api_id


def test_tex_escape_leaves_ordinary_names_alone():
    assert _tex("Llama-3.3-70B-Instruct") == "Llama-3.3-70B-Instruct"
    assert _tex("Nemotron-3_5-Lightning") == r"Nemotron-3\_5-Lightning"


# ---------------------------------------------------------------------------
# The prefill group (measured 17 Aug 2026)
# ---------------------------------------------------------------------------

def test_prefill_group_never_overlaps_the_directly_scoreable_one():
    """The two groups are different MEASUREMENTS, not two tiers of quality.

    A prefilled cell reads the token after a phrase we supplied. If a model
    appeared in both groups its cells could be pooled by a caller that took
    either list, which is the confound `prefill` sits in the harness hash to
    prevent.
    """
    from nullcard.roster import prefill_scoreable_hosted, scoreable_hosted
    direct = {m.api_id for m in scoreable_hosted()}
    prefill = {m.api_id for m in prefill_scoreable_hosted()}
    assert not (direct & prefill)


def test_prefill_recovery_does_not_flip_first_token_ok():
    """first_token_ok stays False for a prefill-recovered model.

    Flipping it would be the tempting one-line "fix" and would silently make
    these models eligible for every unprefilled sweep in the repo.
    """
    from nullcard.roster import prefill_scoreable_hosted
    for m in prefill_scoreable_hosted():
        assert m.first_token_ok is False
        assert m.prefill_ok is True


def test_a_model_that_refuses_logprobs_is_in_neither_group():
    """Kimi-K3 cannot be reached by any prefill; the API withholds logprobs."""
    from nullcard.roster import (NEBIUS, prefill_scoreable_hosted,
                                 scoreable_hosted)
    no_lp = [m for m in NEBIUS if not m.logprobs]
    assert no_lp, "expected at least one logprob-refusing model in the roster"
    ids = {m.api_id for m in scoreable_hosted()} | {
        m.api_id for m in prefill_scoreable_hosted()}
    for m in no_lp:
        assert m.api_id not in ids


def test_unprobed_models_are_not_counted_as_failures():
    """`prefill_ok is None` means never probed, which is not the same as
    probed-and-failed. DeepSeek-V4-Flash went 500 then 404 mid-session."""
    from nullcard.roster import NEBIUS, prefill_scoreable_hosted
    unprobed = [m for m in NEBIUS if m.prefill_ok is None and not m.first_token_ok]
    prefill = {m.api_id for m in prefill_scoreable_hosted()}
    for m in unprobed:
        assert m.api_id not in prefill
        assert m.prefill_ok is not False
