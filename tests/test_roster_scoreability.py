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
