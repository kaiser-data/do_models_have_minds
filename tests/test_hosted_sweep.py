"""Tests for the hosted runner's output segregation.

Hosted cells and self-hosted cells have the SAME filename shape --
`<model_id_with_slashes_replaced>__<arm>.jsonl` -- and 21 scripts in this repo
enumerate models by globbing a results directory. `build_card.py` takes
`*.jsonl` with no roster filter at all.

So a hosted cell written into `results/` does not add a row to a table. It
silently redefines every existing pooled number as an average over two
different harnesses: a local vLLM sweep and a hosted API, differing in
sampling, chat template and serving stack. Nothing would look wrong, and no
error would be raised -- which is exactly the failure mode this project's
limitations section already documents once.

These tests pin the separation as a default rather than as a habit. Pooling the
two trees should stay possible, but it should cost a deliberate flag.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.hosted_sweep import build_parser  # noqa: E402


def test_hosted_output_does_not_default_into_the_self_hosted_tree():
    args = build_parser().parse_args([])
    assert args.results != "results", (
        "hosted cells would be globbed by every analysis script that "
        "enumerates models from results/, silently pooling two harnesses"
    )
    assert args.results == "results_hosted"


def test_design_reference_defaults_to_the_self_hosted_tree():
    """The design check must compare against a cell the GPU sweep wrote.

    Pointed at the hosted output directory instead, it would -- as soon as one
    hosted cell existed -- verify the design against a cell the same design had
    just produced, and pass for the wrong reason.
    """
    args = build_parser().parse_args([])
    assert args.reference_results == "results"


def test_the_two_trees_are_not_the_same_by_default():
    args = build_parser().parse_args([])
    assert args.results != args.reference_results


def test_pooling_remains_possible_but_explicit():
    """Separation is a default, not a prohibition."""
    args = build_parser().parse_args(["--results", "results"])
    assert args.results == "results"


def test_credential_is_named_not_inlined():
    """The runner takes the NAME of an env var, never a key value.

    A `--api-key` flag would put the credential in the process table and in
    any transcript that echoes the command.
    """
    ap = build_parser()
    flags = {a.option_strings[0] for a in ap._actions if a.option_strings}
    assert "--api-key-env" in flags
    assert "--api-key" not in flags
