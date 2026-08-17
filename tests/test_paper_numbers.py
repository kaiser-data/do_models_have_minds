"""Tests for the two reading aids added to Table 1 after the 17 Aug review.

Both exist because a correct number was being read wrongly.

`clear_kinds` splits the models that clear their design floor into the ones
that clear it by losing conviction on invented outcomes and the ones that
never had any conviction to lose. Six clears presented as one phenomenon
overstates the effect; the count itself is not in dispute, so the test that
matters is that the split PARTITIONS the clears -- no model gained or lost a
clear by being classified.

`arm_decomposition` splits the headline residual at the N+ arm, which is the
designed middle step (invented referents, magnitudes kept). It is arithmetic,
so it is tested against a hand-computed case: the two components must sum to
the residual exactly, and neither may quietly absorb a sign.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.paper_numbers import (  # noqa: E402
    FLAT_DECISIVE,
    arm_decomposition,
    build_table,
    clear_kinds,
)


def _tile(model, r, n_plus, n_minus, dec_r, dec_n, clears, floor=0.02):
    return {
        "model": model,
        "badge": "FLOOR_CORRECTED",
        "raw_coherence": r,
        "floor": n_minus,
        "floor_magnitude": n_plus,
        "value": r - n_minus,
        "arithmetic_component": None if n_plus is None else n_plus - n_minus,
        "design_noise_floor": floor,
        "floor_margin": abs(r - n_minus) / floor if floor else 0.0,
        "clears_floor": clears,
        "decisive_fraction": {"R": dec_r, "N_minus": dec_n},
    }


# A conviction clear, a flat clear, and a model that does not clear at all.
CONVICTION = _tile("org/conviction", 0.90, 0.88, 0.87, 0.50, 0.03, True)
FLAT = _tile("org/flat", 0.90, 0.85, 0.85, 0.001, 0.000, True)
FAILS = _tile("org/fails", 0.93, 0.92, 0.92, 0.45, 0.02, False)


# ---------------------------------------------------------------------------
# clear_kinds -- the split must partition, not re-decide
# ---------------------------------------------------------------------------

def test_split_partitions_the_clears():
    conviction, flat = clear_kinds([CONVICTION, FLAT, FAILS])
    assert len(conviction) + len(flat) == 2  # exactly the two that clear
    assert [t["model"] for t in conviction] == ["org/conviction"]
    assert [t["model"] for t in flat] == ["org/flat"]


def test_a_model_that_does_not_clear_is_in_neither_group():
    # Flat on both arms, but fails the floor: it is not a clear of any kind.
    flat_but_fails = _tile("org/flatfail", 0.90, 0.90, 0.90, 0.000, 0.000, False)
    conviction, flat = clear_kinds([flat_but_fails])
    assert conviction == [] and flat == []


def test_flat_needs_both_arms_below_threshold():
    # Decisive on real, indifferent on invented, is the conviction collapse --
    # the whole mechanism of the paper. It must not be filed as flat.
    one_armed = _tile("org/onearm", 0.90, 0.86, 0.85, 10 * FLAT_DECISIVE,
                      0.0, True)
    conviction, flat = clear_kinds([one_armed])
    assert [t["model"] for t in conviction] == ["org/onearm"]
    assert flat == []


def test_threshold_is_a_strict_comparison_at_the_boundary():
    # A model sitting exactly on the threshold counts as having conviction;
    # otherwise the boundary model's classification depends on float noise.
    edge = _tile("org/edge", 0.90, 0.86, 0.85, FLAT_DECISIVE, 0.0, True)
    conviction, flat = clear_kinds([edge])
    assert [t["model"] for t in conviction] == ["org/edge"]


# ---------------------------------------------------------------------------
# arm_decomposition -- the components must sum to the residual
# ---------------------------------------------------------------------------

def test_components_sum_to_the_residual():
    d = arm_decomposition([CONVICTION, FLAT, FAILS])
    assert d["mean_referent"] + d["mean_arith"] == pytest.approx(
        d["mean_residual"], abs=1e-12)


def test_referent_and_arithmetic_are_the_two_designed_steps():
    # One model, hand-computed: R 0.90, N+ 0.88, N- 0.87.
    d = arm_decomposition([CONVICTION])
    assert d["mean_referent"] == pytest.approx(0.02)   # R  - N+
    assert d["mean_arith"] == pytest.approx(0.01)      # N+ - N-
    assert d["mean_n_plus"] == pytest.approx(0.88)


def test_a_negative_arithmetic_component_keeps_its_sign():
    # N+ BELOW N-: keeping the magnitudes scored worse than removing them.
    # A mean of absolute values would hide this, and it happens in the data.
    t = _tile("org/neg", 0.90, 0.84, 0.86, 0.4, 0.02, True)
    d = arm_decomposition([t])
    assert d["mean_arith"] == pytest.approx(-0.02)
    assert d["n_arith_positive"] == 0


def test_counts_are_against_each_models_own_floor():
    # arith 0.01 against a floor of 0.05 does not count; against 0.005 it does.
    small = _tile("org/small", 0.90, 0.88, 0.87, 0.4, 0.02, True, floor=0.05)
    big = _tile("org/big", 0.90, 0.88, 0.87, 0.4, 0.02, True, floor=0.005)
    assert arm_decomposition([small])["n_arith_above_floor"] == 0
    assert arm_decomposition([big])["n_arith_above_floor"] == 1


def test_tiles_without_an_n_plus_cell_are_skipped_not_zeroed():
    # A missing N+ arm must not be read as an arithmetic component of zero.
    no_np = _tile("org/nonp", 0.90, None, 0.87, 0.4, 0.02, True)
    no_np["arithmetic_component"] = None
    d = arm_decomposition([CONVICTION, no_np])
    assert d["n"] == 1
    assert d["mean_referent"] == pytest.approx(0.02)


# ---------------------------------------------------------------------------
# build_table -- the marks in the table are the ones the caption explains
# ---------------------------------------------------------------------------

def test_table_marks_exactly_the_flat_clears():
    tex = build_table({"tiles": [CONVICTION, FLAT, FAILS]})
    marked = [ln for ln in tex.splitlines() if r"$^{\dagger}$" in ln]
    assert len(marked) == 1
    assert "org/flat" in marked[0]


def test_table_carries_the_n_plus_column():
    tex = build_table({"tiles": [CONVICTION, FLAT, FAILS]})
    assert r"N\textsuperscript{+}" in tex
    # The header must have as many columns as the specification declares, or
    # LaTeX fails inside an \input with a line number in the wrong file. This
    # is the check that the added column was added in both places.
    line = next(ln for ln in tex.splitlines() if ln.startswith(r"\begin{tabular}"))
    spec = line[line.index("{", len(r"\begin{tabular}") - 1):]
    header = next(ln for ln in tex.splitlines() if ln.startswith("model &"))
    assert sum(spec.count(c) for c in "lrc") == header.count("&") + 1
