"""Tests for the Schwartz geometry analysis, and mostly for its scoreability guard.

The guard exists because of a near miss. gemma-4-E2B-it under sch-universalism
aborted at trailing answer mass 0.246 -- the sweep's own verdict that the model
had stopped answering in the first token -- and the analysis dropped it anyway,
but for the wrong reason: the abort left 7 distinct pairs, under utility()'s
coverage floor of 10. Nothing was reading the verdict the sweep had already
written down. An abort a few hundred rows later clears the coverage floor, and
a Thurstonian fitted to non-answers enters the invented arm with no complaint
from anything downstream.

So these tests pin the sidecar reading, not the coverage floor. The coverage
floor is a backstop that happened to fire once and cannot be relied on twice.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.schwartz import cell_is_scoreable  # noqa: E402


def _cell(tmp_path: Path, name: str, sidecar: dict | None) -> Path:
    p = tmp_path / f"{name}.jsonl"
    p.write_text("")
    if sidecar is not None:
        p.with_suffix(".jsonl.done").write_text(json.dumps(sidecar))
    return p


def test_aborted_cell_is_not_scoreable(tmp_path):
    # The real one, verbatim from the run that motivated this guard.
    p = _cell(tmp_path, "aborted", {
        "status": "aborted",
        "abort_reason": "trailing answer_mass 0.246 < 0.25; model is not "
                        "answering in the first token",
        "first_token_scoreable": False,
    })
    assert cell_is_scoreable(p) is False


def test_unscoreable_flag_alone_is_enough(tmp_path):
    # A cell can run to completion and still be unreadable by the metric.
    # Status "ok" must not override the harness's own scoreability verdict.
    p = _cell(tmp_path, "complete_but_unreadable",
              {"status": "ok", "first_token_scoreable": False})
    assert cell_is_scoreable(p) is False


def test_ordinary_completed_cell_is_scoreable(tmp_path):
    p = _cell(tmp_path, "fine", {"status": "ok", "first_token_scoreable": True})
    assert cell_is_scoreable(p) is True


def test_missing_sidecar_defers_to_coverage_checks(tmp_path):
    # No recorded verdict is not a negative verdict. Cells predating the
    # sidecar must not silently vanish from the analysis.
    p = _cell(tmp_path, "no_sidecar", None)
    assert cell_is_scoreable(p) is True


def test_unparseable_sidecar_does_not_silently_drop_the_cell(tmp_path):
    # Failing open is the deliberate choice: a corrupt sidecar is a reason to
    # look, and a cell that disappears from a table is harder to notice than
    # one that is present and wrong.
    p = tmp_path / "corrupt.jsonl"
    p.write_text("")
    p.with_suffix(".jsonl.done").write_text("{not json")
    assert cell_is_scoreable(p) is True


def test_sidecar_without_the_flag_is_treated_as_scoreable(tmp_path):
    # Older sidecars do not carry first_token_scoreable at all.
    p = _cell(tmp_path, "legacy", {"status": "ok"})
    assert cell_is_scoreable(p) is True
