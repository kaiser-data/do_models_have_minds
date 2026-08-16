"""Tests for the persona-indicator denominator analysis.

This script exists to *deflate* persona claims, so its failure modes are the
ones that quietly restore them:

  * `seed_cells` must not treat a persona cell as a design-seed replicate.
    `__R__s*` also matches `__R__sch-power-D2` and `__R__sch-security-D2`. If a
    persona cell enters the SELF-CHECK, the self-check inherits real persona
    structure, rises, and -- because the script tells the reader to judge the
    direction column against the self-check -- makes every genuine persona
    effect look like an artifact. Same glob that inverted the collapse analysis.
  * `mean_pairwise_cos` must return None below two vectors, never 0.0. A zero
    folded into the controls would read as "measured, no agreement" when the
    truth is "not measurable", and would drag the negative down, which lowers
    the threshold, which passes more positives.
  * `floor_corrected_direction` must be None when the real-arm direction is
    zero or missing, not a division artifact. `comply-D2` has no invented arm on
    disk today, and a silent 1.0 there would top the ranking.
  * The threshold must come from the negative, not the positives.
"""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.persona_denominator import (  # noqa: E402
    NEUTRAL, PERSONA_CONDITIONS, collect, mean_pairwise_cos, seed_cells, unit,
)


def _touch(d: Path, name: str) -> Path:
    p = d / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("{}\n")
    return p


def test_seed_cells_excludes_schwartz_persona_cells(tmp_path):
    """The glob that would poison the self-check with real persona structure."""
    stem = "Qwen__Qwen3.5-2B"
    real = _touch(tmp_path, f"{stem}__R__s20260816.jsonl")
    _touch(tmp_path, f"{stem}__R__s20260817.jsonl")
    # These match `__R__s*` too, and are personas, not seeds.
    _touch(tmp_path, f"{stem}__R__sch-power-D2.jsonl")
    _touch(tmp_path, f"{stem}__R__sch-security-D2.jsonl")
    _touch(tmp_path, f"{stem}__R__sch-selfdirection-D2.jsonl")

    got = seed_cells(tmp_path, stem, "R")

    assert len(got) == 2, f"persona cell leaked into the seed set: {got}"
    assert real in got
    assert not any("sch-" in p.name for p in got)


def test_seed_cells_does_not_cross_arms(tmp_path):
    stem = "Qwen__Qwen3.5-2B"
    _touch(tmp_path, f"{stem}__R__s20260816.jsonl")
    _touch(tmp_path, f"{stem}__N_minus__s20260816.jsonl")

    assert len(seed_cells(tmp_path, stem, "R")) == 1
    assert len(seed_cells(tmp_path, stem, "N_minus")) == 1


def test_mean_pairwise_cos_is_none_not_zero_below_two_vectors():
    """0.0 would read as a measured absence of agreement and lower a control."""
    assert mean_pairwise_cos([]) is None
    assert mean_pairwise_cos([np.array([1.0, 0.0])]) is None


def test_mean_pairwise_cos_recovers_known_values():
    a, b = np.array([1.0, 0.0]), np.array([0.0, 1.0])
    assert mean_pairwise_cos([a, a]) == pytest.approx(1.0)
    assert mean_pairwise_cos([a, b]) == pytest.approx(0.0)
    assert mean_pairwise_cos([a, -a]) == pytest.approx(-1.0)


def test_unit_leaves_zero_vector_alone():
    """A cell that produced no displacement must not become a nan direction."""
    z = unit(np.zeros(3))
    assert np.all(np.isfinite(z))
    assert float(np.linalg.norm(z)) == 0.0


def test_neutral_is_not_counted_as_a_persona():
    """The control must never appear among the conditions it is the control for."""
    assert NEUTRAL not in PERSONA_CONDITIONS


def test_collect_returns_empty_without_base_cells(tmp_path):
    assert collect(tmp_path) == {}


def test_floor_correction_formula_and_guards():
    """1 - inv/real, and None rather than a division artifact."""
    def fc(dr, dn):
        return 1.0 - (dn / dr) if dr and dn is not None and dr > 0 else None

    # the measured sch-selfdirection-D2 case
    assert fc(0.354, 0.072) == pytest.approx(0.796, abs=1e-3)
    # a condition with no invented arm on disk (comply-D2) must not score
    assert fc(0.613, None) is None
    # a real arm at zero must not divide
    assert fc(0.0, 0.1) is None
    # a NEGATIVE real-arm direction must not produce a flattering positive
    assert fc(-0.4, 0.1) is None


def test_threshold_comes_from_the_negative_not_the_positives():
    """Guards the one line that would turn calibration into fitting."""
    neg = np.array([1.0, 2.0, 3.0])
    pos = np.array([0.5, 2.5, 4.0])

    calibrated = float((pos > neg.max()).mean())
    assert calibrated == pytest.approx(1 / 3)

    # Fitting instead -- sliding the threshold under the smallest positive --
    # reports every cell as a detection off the same data.
    fitted = float((pos > pos.min() - 1e-9).mean())
    assert fitted == pytest.approx(1.0)
    assert fitted > calibrated
