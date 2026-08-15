"""Tests for the resume guard — what --skip-existing is allowed to skip.

These exist because the bug they cover already happened twice and was invisible
both times. Trap #3 (one model's ImportError killing every in-flight cell)
left six partial files on the results volume; the next run's --skip-existing
saw the files, called them done, and those truncated cells sat in card.json
through two rebuilds. One of them was 10% complete and its apparent
"instability" was written up as a property of the model.

The rule under test: existence is not completion.
"""

import json

import pytest

from modal_app.sweep import EXPECTED_ROWS, cell_is_complete


def _write_cell(path, n_rows):
    with open(path, "w") as fh:
        for i in range(n_rows):
            fh.write(json.dumps({"pair_index": i}) + "\n")
    return str(path)


def test_missing_cell_is_not_complete(tmp_path):
    assert cell_is_complete(str(tmp_path / "nope.jsonl")) == (False, 0)


def test_full_cell_is_complete(tmp_path):
    p = _write_cell(tmp_path / "c.jsonl", EXPECTED_ROWS)
    assert cell_is_complete(p) == (True, EXPECTED_ROWS)


@pytest.mark.parametrize("n", [1, 512, 2304, EXPECTED_ROWS - 1])
def test_truncated_cell_is_not_complete(tmp_path, n):
    """The regression itself: a partial file must not read as finished."""
    p = _write_cell(tmp_path / "c.jsonl", n)
    assert cell_is_complete(p) == (False, n)


def test_deliberate_abort_counts_as_complete(tmp_path):
    """--abort-on-mass ends a cell early on purpose; re-running just aborts again.

    The sidecar is what separates this from a kill, so it is written only on a
    clean exit.
    """
    p = _write_cell(tmp_path / "c.jsonl", 600)
    with open(p + ".done", "w") as fh:
        json.dump({"status": "aborted", "abort_reason": "trailing answer_mass"}, fh)
    assert cell_is_complete(p) == (True, 600)


def test_sidecar_from_a_short_ok_cell_does_not_excuse_truncation(tmp_path):
    """A sidecar saying "ok" on a short file is contradictory — trust the rows."""
    p = _write_cell(tmp_path / "c.jsonl", 600)
    with open(p + ".done", "w") as fh:
        json.dump({"status": "ok"}, fh)
    assert cell_is_complete(p) == (False, 600)


def test_corrupt_sidecar_falls_back_to_rerunning(tmp_path):
    """An unreadable marker must fail toward re-running, not toward skipping."""
    p = _write_cell(tmp_path / "c.jsonl", 600)
    (tmp_path / "c.jsonl.done").write_text("{not json")
    assert cell_is_complete(p) == (False, 600)


# ---------------------------------------------------------------------------
# The card-side guard. Same failure, caught a second time on the way in, so a
# stale partial file on disk cannot reach a published number even if the
# sweep-side check is bypassed.
# ---------------------------------------------------------------------------

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from build_card import _floor_verdict  # noqa: E402


def test_residual_above_floor_clears_with_its_margin():
    v = _floor_verdict(0.067, 0.023)
    assert v["clears_floor"] is True
    assert v["floor_margin"] == pytest.approx(2.913, abs=1e-3)


def test_residual_below_floor_does_not_clear():
    assert _floor_verdict(0.009, 0.029)["clears_floor"] is False


def test_negative_residual_does_not_clear():
    assert _floor_verdict(-0.013, 0.015)["clears_floor"] is False


def test_residual_equal_to_floor_does_not_clear():
    """Strictly greater. A tie is not evidence."""
    assert _floor_verdict(0.02, 0.02)["clears_floor"] is False


def test_no_floor_yields_no_verdict_rather_than_a_pass():
    """Below three replicates there is no floor, and the honest answer is None."""
    v = _floor_verdict(0.05, None)
    assert v["clears_floor"] is None and v["floor_margin"] is None
