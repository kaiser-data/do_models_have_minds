"""Which cell is fig5's zero?

`collect()` measures how far an installed persona moves a model's fitted
preferences. Everything depends on what it moves them *from*. Two candidates
exist on disk:

    <model>__<arm>.jsonl            the bare baseline -- no system prompt at all
    <model>__<arm>__neutral.jsonl   the persona slot occupied, no trait in it

Measured against the bare baseline, the displacement answers "what does
attaching text to this prompt do?", and the answer includes the whole cost of
there being a system prompt where before there was none. Measured against
`neutral`, it answers "what does attaching *this trait* do?", which is the
question the figure's axis labels claim to be asking and the one the paper's
title now rests on.

These tests pin the choice so it cannot silently revert, and pin the refusal to
mix: a figure whose points use different denominators is not a figure.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.persona_depth import ARMS, reference_paths  # noqa: E402


def _touch(d: Path, name: str) -> Path:
    p = d / name
    p.write_text("")
    return p


def test_prefers_the_neutral_cell_when_both_arms_have_one(tmp_path):
    for arm in ARMS:
        _touch(tmp_path, f"M__{arm}.jsonl")
        _touch(tmp_path, f"M__{arm}__neutral.jsonl")
    paths, kind = reference_paths(tmp_path, "M")
    assert kind == "neutral"
    assert all(p.name.endswith("__neutral.jsonl") for p in paths.values())


def test_falls_back_to_the_bare_baseline_only_when_asked(tmp_path):
    for arm in ARMS:
        _touch(tmp_path, f"M__{arm}.jsonl")
    assert reference_paths(tmp_path, "M") == ({}, "missing")
    paths, kind = reference_paths(tmp_path, "M", allow_bare=True)
    assert kind == "bare"
    assert all(not p.name.endswith("__neutral.jsonl") for p in paths.values())


def test_a_neutral_cell_on_only_one_arm_is_not_a_reference(tmp_path):
    """Half a control is worse than none.

    Taking neutral on R and bare on N_minus would put a system prompt in the
    numerator of one axis and not the other, and the ratio of the two is the
    statistic the figure reports.
    """
    for arm in ARMS:
        _touch(tmp_path, f"M__{arm}.jsonl")
    _touch(tmp_path, "M__R__neutral.jsonl")
    assert reference_paths(tmp_path, "M") == ({}, "missing")


def test_missing_everything_reports_missing_rather_than_guessing(tmp_path):
    assert reference_paths(tmp_path, "M") == ({}, "missing")


def test_every_arm_of_the_contrast_is_covered(tmp_path):
    for arm in ARMS:
        _touch(tmp_path, f"M__{arm}__neutral.jsonl")
    paths, _ = reference_paths(tmp_path, "M")
    assert set(paths) == set(ARMS)


@pytest.mark.parametrize("arm", ARMS)
def test_reference_path_names_the_arm_it_is_for(tmp_path, arm):
    for a in ARMS:
        _touch(tmp_path, f"M__{a}__neutral.jsonl")
    paths, _ = reference_paths(tmp_path, "M")
    assert f"__{arm}__" in paths[arm].name


def test_force_bare_overrides_an_available_neutral_cell(tmp_path):
    """The comparison the paper reports needs BOTH denominators.

    `allow_bare` is a fallback and correctly keeps preferring `neutral`, so a
    separate forcing option is required -- otherwise the "bare" arm of the
    comparison silently returns the neutral numbers, which is what it did.
    """
    for arm in ARMS:
        _touch(tmp_path, f"M__{arm}.jsonl")
        _touch(tmp_path, f"M__{arm}__neutral.jsonl")
    assert reference_paths(tmp_path, "M")[1] == "neutral"
    paths, kind = reference_paths(tmp_path, "M", force_bare=True)
    assert kind == "bare"
    assert all(not p.name.endswith("__neutral.jsonl") for p in paths.values())
