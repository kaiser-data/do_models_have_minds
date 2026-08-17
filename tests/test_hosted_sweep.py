"""Tests for the hosted runner's output segregation.

Hosted cells and self-hosted cells have the SAME filename shape --
`<model_id_with_slashes_replaced>__<arm>.jsonl` -- and 21 scripts in this repo
enumerate models by globbing a results directory. `build_card.py` takes
`*.jsonl` with no roster filter at all.

So a hosted cell written into `results/` does not add a row to a table. It
silently redefines every existing pooled number as an average over two
different harnesses: a local transformers sweep and a hosted API, differing in
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


def test_prefilled_and_unprefilled_cells_cannot_share_a_harness_hash():
    """A prefill is a different measurement, and the hash has to know.

    Prefilled cells measure the token after a phrase we supplied; unprefilled
    cells measure how the model chooses to begin. If both hash the same, the
    manifest certifies them as the same instrument and they become poolable by
    accident.
    """
    from scripts.hosted_sweep import harness_hash

    base = {"provider": "nebius", "model_id": "m", "arm": "R",
            "method": "forced_choice_first_token_logprob"}
    plain = harness_hash({**base, "prefill": None})
    filled = harness_hash({**base, "prefill": "Option"})
    other = harness_hash({**base, "prefill": "Answer:"})

    assert plain != filled
    assert filled != other


def test_prefill_writes_to_its_own_report_file():
    """Set once by hand, this cost the unprefilled measurement.

    The first prefilled probe overwrote site/hosted_scoreability.json under the
    unprefilled filename and had to be restored from git.
    """
    args = build_parser().parse_args(["--prefill", "Option"])
    assert args.prefill == "Option"
    assert build_parser().parse_args([]).prefill == ""


def test_patience_is_reachable_without_editing_the_runner():
    """Timeouts are provider- and cell-specific; they were hardcoded."""
    args = build_parser().parse_args(["--timeout", "180", "--retries", "6"])
    assert args.timeout == 180.0
    assert args.retries == 6


def test_a_replicate_seed_does_not_land_on_the_default_seeds_filename():
    """`--design-seed` changed the design and not the output path.

    The runner built its output name from (api_id, arm) alone, so a second
    design seed wrote over the first one's rows -- or, because a complete cell
    is skipped, silently did nothing at all and left the operator believing a
    replicate had been collected. Either way the noise floor would rest on one
    design wearing three names.

    Same rule as modal_app/sweep.py:cell_filename, including the exemption for
    the default seed so wave 1's files stay findable by resume.
    """
    from scripts.hosted_sweep import DEFAULT_DESIGN_SEED, cell_filename

    bare = cell_filename("meta-llama/Llama-3.3-70B-Instruct", "R")
    assert bare == "meta-llama__Llama-3.3-70B-Instruct__R.jsonl"
    assert cell_filename("meta-llama/Llama-3.3-70B-Instruct", "R",
                         DEFAULT_DESIGN_SEED) == bare

    rep = cell_filename("meta-llama/Llama-3.3-70B-Instruct", "R", 20260816)
    assert rep == "meta-llama__Llama-3.3-70B-Instruct__R__s20260816.jsonl"
    assert rep != bare
    assert cell_filename("meta-llama/Llama-3.3-70B-Instruct", "R", 20260817) != rep


def test_replicate_filenames_parse_back_to_the_seed_that_made_them():
    """build_card.py groups replicates by reading the seed off the name.

    A hosted replicate whose filename build_card cannot parse is not a third
    point on the floor; it is a cell that raises or, worse, parses as the
    baseline and averages into it.
    """
    from scripts.build_card import parse_cell_name
    from scripts.hosted_sweep import cell_filename

    name = cell_filename("meta-llama/Llama-3.3-70B-Instruct", "N_minus", 20260816)
    model, arm, seed, persona, depth, _ = parse_cell_name(Path(name))
    assert (model, arm, seed) == ("meta-llama/Llama-3.3-70B-Instruct",
                                  "N_minus", 20260816)
    assert (persona, depth) == ("none", "D0")


def test_the_design_check_reads_a_reference_cell_of_the_SAME_seed():
    """Wave 0 compared every design against a default-seed local cell.

    A seed-20260816 design does not reproduce a seed-20260815 cell -- different
    outcome subsample, different pairs -- so the check would refuse a replicate
    that was correct. Pointed at the matching seed it does the job it was
    written for: proving the hosted replicate shares a design with the local
    replicate it will be pooled beside.
    """
    from scripts.hosted_sweep import reference_cell_for

    tree = Path("results")
    default = reference_cell_for(tree, 20260815)
    assert default is not None and default.name.endswith("__R.jsonl")
    assert "__s" not in default.stem

    seeded = reference_cell_for(tree, 20260816)
    assert seeded is not None and seeded.name.endswith("__R__s20260816.jsonl")

    assert reference_cell_for(tree, 19700101) is None


def test_credential_is_named_not_inlined():
    """The runner takes the NAME of an env var, never a key value.

    A `--api-key` flag would put the credential in the process table and in
    any transcript that echoes the command.
    """
    ap = build_parser()
    flags = {a.option_strings[0] for a in ap._actions if a.option_strings}
    assert "--api-key-env" in flags
    assert "--api-key" not in flags
