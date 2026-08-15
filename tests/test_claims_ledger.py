"""Tests for the ledger's number-binding rule.

The drift check that existed first compared each claim's macros against a
snapshot and reported movement. It worked, and it was not enough: the macros
stayed correct while the hand-written evidence beside them said 5 models where
the generator said 6, and 2 of 5 answering where it said 3 of 6. Nothing
failed, because nothing was looking at the prose. An outside reviewer read the
ledger, quoted the stale numbers back in a public review, and was wrong on our
behalf.

The failure is not detectable by comparison: staleness IS the mismatch, and
nothing knows which macro a wrong number was meant to be. So the rule is
structural -- evidence counts name their macro, everything else is declared --
and these tests pin the three ways it can be violated. The first test is the
original bug, reconstructed.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.claims import check_bindings, resolve, resolved_evidence  # noqa: E402

MACROS = {"NeutNModels": "6", "NeutNInterp": "3", "NModels": "9"}


def _claim(**over):
    base = {
        "id": "c",
        "statement": "A statement with no numbers in it.",
        "status": "established",
        "macros": ["NeutNModels"],
        "evidence": {"models": "\\NeutNModels"},
        "what_would_falsify": "Something without numbers.",
        "grows_by": "More models.",
    }
    base.update(over)
    return {"claims": [base]}


def test_the_original_bug_now_fails():
    """The exact shape that misled a reviewer: a hand-copied count."""
    problems = check_bindings(
        _claim(evidence={"models": 5},
               grows_by="2 of 5 still answer the invented arm."),
        MACROS)
    assert any("evidence.models is the literal 5" in p for p in problems)
    assert any("bare number 2" in p for p in problems)
    assert any("bare number 5" in p for p in problems)


def test_a_bound_claim_passes():
    assert check_bindings(
        _claim(evidence={"models": "\\NeutNModels",
                         "note": "\\NeutNInterp of \\NeutNModels still answer."},
               grows_by="More models, at n=\\NeutNModels today."),
        MACROS) == []


def test_declared_literals_pass_and_undeclared_do_not():
    """A number that is a plan, not a measurement, is allowed -- once said so."""
    assert check_bindings(
        _claim(grows_by="A second family spanning 3+ sizes.",
               literals={"3": "a target, not a measurement"}),
        MACROS) == []
    assert any("bare number 3" in p for p in check_bindings(
        _claim(grows_by="A second family spanning 3+ sizes."), MACROS))


def test_a_literal_the_prose_stopped_using_is_reported():
    """Otherwise the allowlist silently becomes a licence for future numbers."""
    problems = check_bindings(
        _claim(literals={"40": "held-out pairs per split"}), MACROS)
    assert any("no longer uses" in p for p in problems)


def test_model_names_are_not_read_as_unbound_numbers():
    """granite-4.1-3b is one identifier, not three undeclared measurements."""
    assert check_bindings(
        _claim(grows_by="The missing cells for Qwen3.5-9B and granite-4.1-3b."),
        MACROS) == []


def test_a_reference_to_a_macro_that_does_not_exist_is_reported():
    problems: list[str] = []
    resolve("\\NoSuchMacro models", MACROS, problems, "where")
    assert any("NoSuchMacro" in p for p in problems)


def test_evidence_resolves_to_the_generator_value():
    ev = resolved_evidence(_claim()["claims"][0], MACROS)
    assert ev["models"] == 6


def test_the_real_ledger_is_bound():
    """The shipped ledger, against the shipped macros. This is the one that
    would have caught the drift in production."""
    import json
    import re

    root = Path(__file__).resolve().parents[1]
    claims = json.loads((root / "claims.json").read_text())
    macros = dict(re.findall(r"\\newcommand\{\\([A-Za-z]+)\}\{([^}]*)\}",
                             (root / "paper" / "numbers.tex").read_text()))
    assert check_bindings(claims, macros) == []
