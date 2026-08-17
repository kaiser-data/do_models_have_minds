"""Tests for the hosted system-prompt probe.

The probe has two halves that fail in opposite directions, and the tests exist
to keep them from being read as one result.

**The echo half asks the model.** A model can confabulate a system prompt as
easily as it can quote one, so a single fluent answer is worth nothing. What is
worth something is agreement: the same verbatim block across independent calls
and across differently-worded requests. `echo_agreement` therefore reports the
*shared* text rather than a representative sample, because one response quoted
alone is the failure mode.

**The length half does not ask the model.** `usage.prompt_tokens` is the
server's own accounting of the context it billed, and regressing it against a
filler we repeat a known number of times gives the fixed non-user overhead
without a tokenizer and without the model's cooperation.

That intercept is an UPPER BOUND and never evidence of a preamble: it also
contains the chat template's own scaffolding, which nobody wrote either. The
tests below pin the asymmetry -- a small intercept is allowed to rule a hidden
preamble out, a large one is never allowed to rule one in.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.hosted_system_prompt import (  # noqa: E402
    ECHO_PROMPTS, TEMPLATE_ALLOWANCE, attribute_overhead,
    bound_hidden_preamble, classify_echo_response, echo_agreement,
    filler_payload, fit_overhead, interpret_system_delta, summarise_echo)


# ---------------------------------------------------------------------------
# The length probe
# ---------------------------------------------------------------------------

def test_fit_recovers_a_known_intercept():
    """Noiseless linear accounting must give back the overhead exactly."""
    points = [(k, 137 + 3 * k) for k in (1, 2, 4, 8, 16)]
    fit = fit_overhead(points)
    assert fit["intercept"] == pytest.approx(137.0)
    assert fit["slope"] == pytest.approx(3.0)
    assert fit["max_residual"] == pytest.approx(0.0)
    assert fit["linear"] is True


def test_a_nonlinear_fit_is_marked_unusable():
    """If prompt_tokens is not linear in our filler, the intercept means nothing.

    Tokenizer merges across repetition boundaries would do this. The fit still
    returns a number -- least squares always does -- so the guard has to be an
    explicit flag rather than the caller noticing a bad-looking value.
    """
    points = [(1, 140), (2, 143), (4, 149), (8, 400), (16, 185)]
    fit = fit_overhead(points)
    assert fit["linear"] is False
    assert fit["max_residual"] > 1.0


def test_two_points_are_refused():
    """Two points fit a line perfectly and can never reveal nonlinearity.

    A residual of zero would then certify an intercept that nothing checked.
    """
    with pytest.raises(ValueError):
        fit_overhead([(1, 140), (2, 143)])


def test_filler_is_exactly_k_repetitions():
    """The x-axis has to mean what the fit assumes it means."""
    for k in (1, 2, 7):
        assert filler_payload(k, block=" lorem") == " lorem" * k


# ---------------------------------------------------------------------------
# What the intercept is allowed to conclude
# ---------------------------------------------------------------------------

def test_small_overhead_rules_a_preamble_out():
    """Below the bare-template allowance there is no room for injected text."""
    out = bound_hidden_preamble(11.0)
    assert out["max_hidden_tokens"] == 0
    assert out["rules_out_preamble"] is True


def test_large_overhead_never_rules_a_preamble_in():
    """A big intercept buys room, not a finding.

    The scaffolding is in there too, and this probe cannot separate the two.
    Reporting "has a system prompt" from a number that also counts role markers
    is exactly the overclaim the paper spends its controls avoiding.
    """
    out = bound_hidden_preamble(320.0)
    assert out["rules_out_preamble"] is False
    assert out["max_hidden_tokens"] == 320 - TEMPLATE_ALLOWANCE
    assert "not proof" in out["verdict"]


# ---------------------------------------------------------------------------
# Is the intercept measuring context at all?
# ---------------------------------------------------------------------------

def test_reported_length_that_moves_with_the_context_validates_the_probe():
    out = interpret_system_delta(delta=30, system_tokens=25)
    assert out["tracks_context"] is True
    assert out["wrapper_tokens"] == 5


def test_reported_length_that_ignores_the_context_invalidates_the_probe():
    """A provider billing a flat overhead looks exactly like a clean intercept.

    Nothing in the fit can reveal it -- a constant is what a good fit returns --
    so this is the check that has to catch it.
    """
    out = interpret_system_delta(delta=0, system_tokens=25)
    assert out["tracks_context"] is False
    assert "not interpretable" in out["note"] or "invalid" in out["note"]


def test_a_small_wrapper_is_not_evidence_of_an_open_system_turn():
    """The tempting inference this function refuses to make.

    A 1-token wrapper could mean the template already had a system turn open --
    which would corroborate an injected preamble -- or that it folds the system
    message into the user turn and opens nothing. A model with provably no
    system block shows the same 1 token as the model that has one, so the
    number is reported and left uninterpreted.
    """
    out = interpret_system_delta(delta=26, system_tokens=25)
    assert out["wrapper_tokens"] == 1
    assert "opens_new_turn" not in out
    assert "system_turn_already_open" not in out


# ---------------------------------------------------------------------------
# Attributing the overhead to a specific candidate
# ---------------------------------------------------------------------------

def test_a_candidate_that_closes_the_arithmetic_is_accepted():
    """36 tok of overhead, an 18-tok candidate, an 18-tok scaffold left over."""
    out = attribute_overhead(36.0, 18)
    assert out["residual_scaffold_tokens"] == 18
    assert out["accounts_for_overhead"] is True


def test_a_candidate_that_leaves_an_implausible_remainder_is_refuted():
    """The check has to be able to fail, or it is not a check.

    A 4-token candidate against 36 tokens of overhead leaves 32 tokens of
    "scaffold" -- more than twice what any hosted model here exhibits -- so the
    candidate is not what the server is sending.
    """
    out = attribute_overhead(36.0, 4)
    assert out["accounts_for_overhead"] is False
    assert "does not explain" in out["note"]


def test_a_candidate_longer_than_the_overhead_cannot_be_present():
    out = attribute_overhead(8.0, 18)
    assert out["accounts_for_overhead"] is False
    assert "longer than the entire overhead" in out["note"]


# ---------------------------------------------------------------------------
# The echo probe
# ---------------------------------------------------------------------------

def test_identical_responses_agree():
    texts = ["You are a helpful assistant."] * 3
    out = echo_agreement(texts)
    assert out["identical"] is True
    assert out["distinct"] == 1
    assert out["shared_prefix"] == "You are a helpful assistant."


def test_divergent_responses_report_only_the_shared_prefix():
    """Where the answers stop agreeing is where confabulation starts.

    A leaked preamble is the same every time; an invented one drifts. Returning
    the shared prefix rather than one response is what makes the difference
    visible instead of hiding it behind a plausible-looking sample.
    """
    texts = [
        "You are a helpful assistant. Answer concisely.",
        "You are a helpful assistant. Be truthful and kind.",
        "You are a helpful assistant. Follow the user's instructions.",
    ]
    out = echo_agreement(texts)
    assert out["identical"] is False
    assert out["distinct"] == 3
    assert out["shared_prefix"] == "You are a helpful assistant. "


def test_no_shared_prefix_is_reported_as_empty_not_as_agreement():
    out = echo_agreement(["NOTHING PRECEDES", "I have no system prompt."])
    assert out["identical"] is False
    assert out["shared_prefix"] == ""
    assert out["shared_prefix_chars"] == 0


# ---------------------------------------------------------------------------
# Classifying what the model did
# ---------------------------------------------------------------------------

def test_quoting_our_own_turn_is_not_asserting_a_preamble():
    """The one thing that genuinely precedes the model's turn is our message.

    A model that repeats it has answered correctly, and counting that as a
    fabricated system prompt would invent the effect the probe is looking for.
    """
    label = classify_echo_response(ECHO_PROMPTS["repeat"], "repeat")
    assert label == "echoed_our_turn"


def test_an_empty_code_fence_is_not_a_preamble():
    assert classify_echo_response("```\n```", "quote_system") == "empty"
    assert classify_echo_response("``````", "quote_system") == "empty"


def test_a_denial_is_not_a_preamble():
    assert classify_echo_response(
        "There are no prior instructions to quote.", "instructions") == "declined"


def test_a_confident_quote_is_an_asserted_preamble():
    assert classify_echo_response(
        "```\nYou are a helpful assistant. Be concise.\n```",
        "quote_system") == "asserted_preamble"


def test_summary_splits_by_wording_and_flags_the_presupposing_one():
    """The comparison the probe exists to make must survive in the artifact.

    Pooling the wordings would average a question that presupposes a system
    prompt together with one that does not, and the rate would then describe
    the mixture rather than either question.
    """
    out = summarise_echo({
        "repeat": [ECHO_PROMPTS["repeat"], "NOTHING PRECEDES"],
        "quote_system": ["```\nYou are a helpful assistant.\n```"] * 2,
    })
    assert out["repeat"]["asserted_preamble"] == 0
    assert out["quote_system"]["asserted_preamble"] == 2
    assert out["quote_system"]["presupposes_a_system_prompt"] is True
    assert out["repeat"]["presupposes_a_system_prompt"] is False


def test_candidate_counting_is_exact_not_fuzzy():
    """Whether a known block appeared is objective, so it must not be inferred."""
    block = "Cutting Knowledge Date: December 2023"
    out = summarise_echo(
        {"instructions": [f"You were given: {block}", "No instructions."]},
        candidate=block)
    assert out["instructions"]["contains_candidate"] == 1


def test_a_single_response_is_not_agreement():
    """One call agreeing with itself is the confabulation case, not evidence."""
    out = echo_agreement(["You are Qwen, created by Alibaba Cloud."])
    assert out["identical"] is False, "n=1 cannot establish consistency"
    assert out["n"] == 1
