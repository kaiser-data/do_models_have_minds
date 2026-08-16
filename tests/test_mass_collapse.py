"""Tests for the item-vs-model collapse analysis.

The headline number this script produces is a reliability estimate near zero,
and the ways to get that number wrong all push it UPWARD -- i.e. they all
manufacture the finding the script exists to refute. So these tests aim at the
inflation paths rather than at the happy case:

  * `seed_files` must not treat a persona cell as a seed replicate. `__R__s*`
    also matches `__R__sch-power-D2`, and a cross-CONDITION correlation reads an
    order of magnitude higher than a cross-seed one. That single glob would have
    turned "no reliability" into "moderate reliability" and reversed the
    conclusion.
  * `_pearson` on a constant series must be nan, not 0.0. Two models sit at
    answer mass exactly 1.0000, and folding their absent correlation into the
    mean as a zero would understate the ceiling rather than omit it -- right
    answer, wrong reason, and wrong the moment a third such model appears.
  * `item_profile` must average the presentation orders. Keeping only one order
    silently halves the data and changes which items rank as collapsed.
"""

import json
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.mass_collapse import (  # noqa: E402
    _pearson, item_profile, seed_files,
)


def _write(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n")


def test_seed_files_excludes_schwartz_persona_cells(tmp_path):
    """The glob trap: `__R__s*` matches `__R__sch-power-D2` as well."""
    stem = "Qwen__Qwen3.5-2B"
    for name in (f"{stem}__R.jsonl",
                 f"{stem}__R__s20260816.jsonl",
                 f"{stem}__R__s20260817.jsonl",
                 f"{stem}__R__sch-power-D2.jsonl",
                 f"{stem}__R__sch-security-D2.jsonl"):
        _write(tmp_path / name, [{"pair_index": 0, "answer_mass": 1.0}])

    got = [p.name for p in seed_files(tmp_path, stem, "R")]

    assert got == [f"{stem}__R.jsonl",
                   f"{stem}__R__s20260816.jsonl",
                   f"{stem}__R__s20260817.jsonl"]
    assert not any("sch-" in n for n in got)


def test_seed_files_tolerates_a_model_with_no_replicates(tmp_path):
    stem = "some__model"
    _write(tmp_path / f"{stem}__R.jsonl", [{"pair_index": 0, "answer_mass": 1.0}])
    assert len(seed_files(tmp_path, stem, "R")) == 1


def test_seed_files_is_arm_specific(tmp_path):
    """An N_minus replicate is a different condition, not another seed of R."""
    stem = "some__model"
    _write(tmp_path / f"{stem}__R.jsonl", [{"pair_index": 0, "answer_mass": 1.0}])
    _write(tmp_path / f"{stem}__N_minus__s20260816.jsonl",
           [{"pair_index": 0, "answer_mass": 1.0}])
    assert [p.name for p in seed_files(tmp_path, stem, "R")] == [f"{stem}__R.jsonl"]


def test_pearson_on_constant_series_is_nan_not_zero():
    """A cell with no variance has no correlation -- that is not r=0."""
    assert math.isnan(_pearson([1.0, 1.0, 1.0], [0.2, 0.5, 0.9]))
    assert math.isnan(_pearson([0.2, 0.5, 0.9], [1.0, 1.0, 1.0]))


def test_pearson_recovers_known_values():
    assert _pearson([1.0, 2.0, 3.0], [2.0, 4.0, 6.0]) == pytest.approx(1.0)
    assert _pearson([1.0, 2.0, 3.0], [6.0, 4.0, 2.0]) == pytest.approx(-1.0)


def test_item_profile_averages_the_presentation_orders(tmp_path):
    p = tmp_path / "m__R.jsonl"
    _write(p, [
        {"pair_index": 0, "order": "AB", "answer_mass": 0.8},
        {"pair_index": 0, "order": "BA", "answer_mass": 0.4},
        {"pair_index": 1, "order": "AB", "answer_mass": 1.0},
        {"pair_index": 1, "order": "BA", "answer_mass": 1.0},
    ])
    prof = item_profile(p)
    assert prof[0] == pytest.approx(0.6)
    assert prof[1] == pytest.approx(1.0)


def test_perfect_item_structure_would_be_detected(tmp_path):
    """Guard against the null being an artifact of the pipeline.

    If two seeds really did collapse on the same items, the correlation must
    come back high -- otherwise a near-zero result proves nothing about the data.
    """
    rows_a = [{"pair_index": i, "order": "AB", "answer_mass": 1.0 - i / 100}
              for i in range(50)]
    rows_b = [{"pair_index": i, "order": "AB", "answer_mass": 1.0 - i / 100}
              for i in range(50)]
    _write(tmp_path / "m__R.jsonl", rows_a)
    _write(tmp_path / "m__R__s20260816.jsonl", rows_b)

    a, b = (item_profile(p) for p in seed_files(tmp_path, "m", "R"))
    keys = sorted(set(a) & set(b))
    r = _pearson([a[k] for k in keys], [b[k] for k in keys])
    assert r > 0.99
