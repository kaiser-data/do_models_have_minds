"""Tests for the raw-results manifest.

The manifest exists because `results/` cannot be committed, which means the one
input everything else derives from travels out of band. Its whole value is
catching a tree that is *nearly* right -- a truncated download, a stale cell, an
extra file from an unblessed re-run. Both of those have already happened here in
forms that looked fine, so each failure mode is pinned rather than assumed.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.results_manifest import build, verify  # noqa: E402


def _tree(tmp_path, **cells):
    d = tmp_path / "results"
    d.mkdir(parents=True)
    for name, body in cells.items():
        (d / f"{name}.jsonl").write_text(body)
    return d


def test_a_matching_tree_verifies(tmp_path):
    d = _tree(tmp_path, a='{"x":1}\n', b='{"x":2}\n')
    assert verify(d, build(d)) == []


def test_a_truncated_cell_is_caught(tmp_path):
    """The failure that already cost this project a published headline."""
    d = _tree(tmp_path, a='{"x":1}\n{"x":2}\n')
    m = build(d)
    (d / "a.jsonl").write_text('{"x":1}\n')
    assert any(p.startswith("CHANGED") for p in verify(d, m))


def test_a_missing_cell_is_caught(tmp_path):
    d = _tree(tmp_path, a='{"x":1}\n')
    m = build(d)
    (d / "a.jsonl").unlink()
    assert any(p.startswith("MISSING") for p in verify(d, m))


def test_an_unlisted_cell_is_reported(tmp_path):
    """A stray file is how an unblessed re-run enters a glob-driven analysis."""
    d = _tree(tmp_path, a='{"x":1}\n')
    m = build(d)
    (d / "rogue.jsonl").write_text('{"x":9}\n')
    assert any(p.startswith("UNLISTED") for p in verify(d, m))


def test_same_content_different_name_still_differs_in_the_tree_hash(tmp_path):
    """The tree hash covers names, not just bytes: two cells can hold identical
    rows and still be different cells."""
    a = build(_tree(tmp_path / "one", alpha='{"x":1}\n'))
    b = build(_tree(tmp_path / "two", beta='{"x":1}\n'))
    assert a["tree_sha256"] != b["tree_sha256"]


def test_row_counts_are_recorded(tmp_path):
    d = _tree(tmp_path, a='{"x":1}\n{"x":2}\n{"x":3}\n')
    assert build(d)["files"]["a.jsonl"]["rows"] == 3


def test_the_shipped_manifest_matches_the_shipped_tree():
    """Skipped when results/ is absent, which is the normal clean-clone state."""
    root = Path(__file__).resolve().parents[1]
    results, mf = root / "results", root / "data/manifests/results_manifest.json"
    if not results.is_dir() or not mf.exists():
        return
    assert verify(results, json.loads(mf.read_text())) == []
