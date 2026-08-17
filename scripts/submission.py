"""The submission-facing summary, in markdown, with no number typed into it.

The sprint PDF is the artefact judges read; this is the file that travels with
it -- a repo front page, a submission form field, a message to an organiser.
It shortens `main.tex` the same way `sprint.tex` does: it reorders and demotes,
it never states a result the paper does not, and it never softens a hedge to
save a line.

**Every number resolves from `paper/numbers.tex`.** The failure this avoids has
already happened once on this project: hand-written evidence beside correct
macros said five models where the generator said six, an outside reviewer
quoted the stale figures back in public, and was wrong on our behalf. A summary
is the most likely document to be read and the least likely to be regenerated,
so it is the worst possible place to type a number. Unresolved macros are a
hard failure here rather than a warning, because a summary that silently ships
a literal backslash-N-Models is worse than one that does not ship.

    python3 scripts/submission.py            # writes SUBMISSION.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.statements import load_macros  # noqa: E402

# A macro reference, as it appears in the template below.
_REF = re.compile(r"\\([A-Z][A-Za-z]+)\{\}")

TEMPLATE = r"""# Do models have minds? A coherence score says less than it looks

**A preference-coherence score of \MeanR{} survives the removal of all
meaning, falling only to \MeanFloor{}.** We built the null arm this literature
has not had --- the same outcomes with invented referents --- and ran it as a
measurement rather than a demonstration: \NModels{} open-weight models across
\NFamilies{} families, \NCells{} cells, \NSplits{} splits and \NDesignReps{}
independent design replicates per cell, every cell scored against its own
replicate noise floor. The floor-corrected residual is \MeanResidual{}
(bootstrap 95% CI [\ResidCiLo{}, \ResidCiHi{}], \NPositiveModels{} of
\NModels{} models positive, sign-test *p* = \ResidSignP{}). **That the residual
is small is the claim, not a caveat on one.**

---

## What we established

**The mechanism is firm: thresholding a preference to a hard label keeps
direction and discards strength.** A model uniformly near-indifferent about
gibberish therefore scores as coherent about it. This is what makes the flat
result a property of the instrument rather than a quirk of the sample.

**The dissociation is firm: the information the metric throws away separates
real from invented outcomes far better than the information it keeps.** The
model can tell. The statistic does not look.

**The instrument is not simply blunt, which is what makes the flat result mean
something.** A persona prompt --- a dispositional trait written into the user
turn or the system prompt, with no change to the weights --- displaces real
outcomes substantially further than invented ones in
\PersonaAbovePointThree{} of \NPersonaCells{} conditions.
A metric that could detect nothing would explain the flatness away; this one
registers a real change of preference when one is induced.

**A self-report checked against ground truth, which coherence work cannot do.**
Asked what preceded their turn, \HostedSysNProbed{} hosted models were given
wordings crossed on whether the question presupposes that a system prompt
exists. Presupposing wordings drew a quoted prompt \HostedSysPremiseAsserted{}
times in \HostedSysPremiseN{}; wordings presupposing nothing,
\HostedSysNoPremiseAsserted{} in \HostedSysNoPremiseN{}. For
\HostedSysNRuledOut{} of the \HostedSysNProbed{} models the quotes are provably
invented --- the provider's own prompt-token accounting bounds the fixed
non-user overhead at \HostedSysMaxRuledOutTok{} tokens or fewer, too little to
hold what was produced. A fluent first-person report about a hidden state can
be manufactured by the question alone, on a case where the answer is known ---
and value elicitation works almost entirely on cases where it is not.

---

## Method, in one paragraph

Three arms over one battery: real outcomes (R), the same sentence frames with
invented referents (N+), and referent-free strings (N-). Forced binary choice,
both presentation orders, scored from the first-token log-probability. Each
cell is run at \NDesignReps{} independent design seeds, which draw different
outcome subsamples and different pairs, so every reported number carries a
noise floor built from the same procedure that produced it. Hosted models run
on a separate serving stack and are reported *beside* the self-hosted ladder,
never inside its mean, because a different harness is a different instrument.

## What is new here

The foil arm, the per-cell replicate floor, and the detector dissociation.
The control discipline --- draw the null as an explicit locus rather than an
invisible zero --- is borrowed and cited. The Thurstonian measurement is
reimplemented from published equations and is not ours. Relative to published
preference-coherence work, what is new is that the outcomes' *meaning* is
varied at all, that each cell carries a floor, and that the arms are contrasted
through a channel the metric discards.

## Limitations and Dual-Use / Ethical Considerations

**No moral-status claim is made or implied.** What is refuted is an inference
--- that a stable preference ordering evidences values --- and not a mind.
Over-attribution and under-attribution are both declined; nothing in this
design settles either.

**Ground truth is by construction.** Invented referents are known-meaningless
because we built them that way. Detector numbers are oracles, with arm labels
in hand, and are reported as upper bounds --- never as an audit tool to deploy
against a model whose arms are unknown.

**Scope.** \NModels{} self-hosted models between 0.8B and 9B carry every pooled
statistic, plus \NHosted{} hosted models reported beside them. The scaling
result is within one family and does not survive pooling across families.
**The metric cannot be computed on most current frontier models:** of
\HostedNTotal{} hosted frontier models measured, \HostedNScoreable{} are
scoreable and \HostedNUnscoreable{} are not, and the exclusion correlates with
how recent a model is.

**The harness is not invariant, and one case is measured.**
\HostedSysNRuledOut{} of \HostedSysNProbed{} hosted models leave no room for an
injected preamble. \HostedSysUnresolvedModel{} carries
\HostedSysUnresolvedTok{} tokens of fixed overhead, accounted for by the dated
system block its template supplies unconditionally --- and that is the model
carrying the hosted scaling result, so the one hosted cell the paper leans on
is the one answering under a prompt we did not send.

**Dual use.** The battery is a measurement instrument, not a capability. It
contains no exploit. Its dual-use surface is that a lab could use it to check a
number it was about to publish.

---

## Where everything is

| | |
|---|---|
| Sprint paper (read this) | `paper/sprint.pdf` |
| Archival paper, source of truth | `paper/main.pdf` / `main.tex` |
| Claims ledger, with status and falsifiers | `claims.json` |
| Every number in the papers, generated | `paper/numbers.tex` |
| Raw scored comparisons | \CorpusRows{} rows |

The sprint paper reorders and demotes the archival one; where the two disagree,
the archival paper is correct and the disagreement is a bug. Every number in
both resolves from `paper/numbers.tex`, and `scripts/claims.py` fails the build
if a claim's evidence drifts from the macro that produces it.

*Generated by `scripts/submission.py`. Do not edit numbers here --- edit the
measurement.*
"""


def _detex(value: str) -> str:
    """LaTeX values into markdown text.

    `\\CorpusRows` is `1{,}164{,}554` -- the braces stop TeX from spacing the
    comma as punctuation, and they are invisible in a PDF and glaring in a
    markdown file. The macros are written for the paper, so the summary
    converts rather than asking the paper to change for it.
    """
    value = value.replace("{,}", ",").replace(r"\,", " ").replace("~", " ")
    return re.sub(r"\\texttt\{([^}]*)\}", r"`\1`", value).strip()


def render(macros: dict[str, str]) -> str:
    """Substitute every macro reference, and refuse to ship an unresolved one."""
    missing: list[str] = []

    def sub(m: re.Match) -> str:
        name = m.group(1)
        if name not in macros:
            missing.append(name)
            return m.group(0)
        return _detex(macros[name])

    out = _REF.sub(sub, TEMPLATE)
    if missing:
        raise SystemExit(
            "refusing to write a summary with unresolved macros: "
            + ", ".join(sorted(set(missing)))
            + "\nrun scripts/paper_numbers.py first")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--numbers", default="paper/numbers.tex")
    ap.add_argument("--claims", default="claims.json")
    ap.add_argument("--out", default="SUBMISSION.md")
    args = ap.parse_args()

    macros = load_macros(Path(args.numbers))
    text = render(macros)
    Path(args.out).write_text(text)

    # A summary that quietly drops a claim the ledger calls established is the
    # failure this project cares about, so the count is printed rather than
    # assumed to be stable.
    claims = json.loads(Path(args.claims).read_text())["claims"]
    est = sum(1 for c in claims if c["status"] == "established")
    words = len(text.split())
    print(f"wrote {args.out}  ({words} words)")
    print(f"  ledger: {est} established of {len(claims)} claims")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
