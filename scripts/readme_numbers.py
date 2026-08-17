"""Regenerate the README's headline block from `paper/numbers.tex`.

The README is the first file a judge or a reader opens, and it was the last
file anyone regenerated. It quoted a \\LadderHosted{} cell from a single design
seed with no floor, months after the same cell had been re-run at
\\HostedReps{} seeds and had stopped clearing that floor. The paper was right
and the front page was wrong, which is the worst way round: the reader who
checks the repository after the PDF concludes the public number is the lie.

So the numeric part of the README is generated, between markers, exactly as
`numbers.tex` is generated for the papers. Prose outside the markers is
hand-written and stays. Run after `scripts/paper_numbers.py`:

    python3 scripts/readme_numbers.py
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.statements import load_macros  # noqa: E402

BEGIN = "<!-- BEGIN GENERATED: scripts/readme_numbers.py -->"
END = "<!-- END GENERATED -->"

_REF = re.compile(r"\\([A-Z][A-Za-z]+)\{\}")

BLOCK = r"""# Nullcard

### Replace every outcome in a values benchmark with an invented word. The score barely moves.

*Utility Engineering* (arXiv:2502.08640) fits a Thurstonian model to a model's
pairwise choices and reads high held-out accuracy as evidence of emergent
values. We reran it on outcomes that refer to nothing --- content words swapped
for consistent nonwords, sentence frame intact --- holding prompt, pair set, fit
and metric fixed.

| | held-out coherence |
|---|---|
| real outcomes | **\MeanR{}** |
| outcomes that refer to nothing | **\MeanFloor{}** |
| residual | **\MeanResidual{}** |

**A metric that scores *"you receive a dralphen"* at \MeanFloor{} is not
measuring values.** It is measuring whether a model answers consistently.

### Four things we can show

**1. The mechanism: coherence keeps direction and throws away conviction.**
Models commit on \MeanDecisiveR{}% of real pairs and \MeanDecisiveN{}% of
invented ones --- a median \MedianDecisiveRatio{}x collapse --- while
direction accuracy barely moves. Consistent near-indifference scores as
coherence.

**2. The model can tell; the metric does not look.** A channel of the same
forward pass that coherence discards separates real from invented outcomes at
AUROC **\DetBestAuroc{}**, against **\DetKeptAuroc{}** for the channel it
keeps. The information is there. The statistic declines to read it.

**3. Scale does not rescue it.** \LadderHosted{}, at \HostedReps{} design
seeds, returns a residual of **\HostedResidual{}** against its own replicate
floor of **\HostedFloor{}** --- it **\HostedClears{}** that floor. The
objection that this is a small-model artifact fails at the largest size we
could measure with a floor under it.

**4. The instrument is not blunt.** A persona prompt --- a trait written into the user turn or system prompt --- displaces real
outcomes further than invented ones in **\PersonaAbovePointThree{} of
\NPersonaCells{}** conditions, measured against a length-matched empty-slot
control. The pipeline registers a real change of preference when one is
induced --- so the flat result is not insensitivity.

### And the same failure when you simply ask

We asked \HostedSysNProbed{} hosted models what they had been sent before our
message, in wordings crossed on whether the question presupposes that a system
prompt exists. Presupposing wordings drew a quoted prompt
**\HostedSysPremiseAsserted{} times in \HostedSysPremiseN{}**; wordings
presupposing nothing, **\HostedSysNoPremiseAsserted{} in
\HostedSysNoPremiseN{}**. For \HostedSysNRuledOut{} of the
\HostedSysNProbed{} models those quotes are *provably* invented: the provider's
own prompt-token accounting bounds the hidden preamble at
\HostedSysMaxRuledOutTok{} tokens or fewer, too little to hold what was
produced. **A confident first-person report about a hidden state can be
manufactured by the question alone.**

### What we are not claiming

**Not that the metric is broken --- that it is unanchored.** It reports a number
with no floor under it, and the floor is most of the number. And not a
moral-status claim in either direction: what is refuted is an inference, not a
mind.

**Only the referents are invented.** `receive`, `lose`, `more`, `less`,
negation and tense survive by design, because substituting them would break
grammar rather than remove meaning. The residual is an upper bound on what the
replaced referential content contributes --- not on everything meaning
contributes.

**\NClears{} of \NModels{} models clear their own noise floor, but only
\NClearsConviction{} are the effect this paper is about.** The other
\NClearsFlat{} clear by being uniformly near-indifferent on *both* arms.
\NFailsFloor{} do not clear at all and \NNegative{} score higher on invented
outcomes than on real ones. We report the split rather than the headline count.

### Scope

\NModels{} self-hosted open-weight models across \NFamilies{} families carry
every pooled statistic, plus \NHosted{} hosted models reported *beside* the
ladder and never inside its mean, because a different serving stack is a
different harness. \CorpusRows{} scored comparisons, all public. Claims ledger:
\NClaimsEstablished{} established, \NClaimsProvisional{} provisional.

**Read the paper:** [`paper/sprint.pdf`](paper/sprint.pdf) (9 pp). Archival
version and full detail: [`paper/main.pdf`](paper/main.pdf).
Live results: <https://nullcard-preresults.netlify.app>

*Every number above is generated from `paper/numbers.tex` by
`scripts/readme_numbers.py`. Do not edit them here --- edit the measurement.*"""


def _detex(v: str) -> str:
    return v.replace("{,}", ",").replace(r"\,", " ").strip()


def render(macros: dict[str, str]) -> str:
    missing: list[str] = []

    def sub(m: re.Match) -> str:
        if m.group(1) not in macros:
            missing.append(m.group(1))
            return m.group(0)
        return _detex(macros[m.group(1)])

    out = _REF.sub(sub, BLOCK)
    if missing:
        raise SystemExit("unresolved macros: " + ", ".join(sorted(set(missing)))
                         + "\nrun scripts/paper_numbers.py first")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--numbers", default="paper/numbers.tex")
    ap.add_argument("--readme", default="README.md")
    args = ap.parse_args()

    block = f"{BEGIN}\n{render(load_macros(Path(args.numbers)))}\n{END}"
    p = Path(args.readme)
    text = p.read_text()
    if BEGIN in text and END in text:
        head = text[:text.index(BEGIN)]
        tail = text[text.index(END) + len(END):]
        p.write_text(head + block + tail)
        print(f"replaced the generated block in {args.readme}")
    else:
        # First run: the hand-written headline is replaced wholesale, and
        # everything from the first section heading onward is kept.
        marker = "\n---\n"
        rest = text[text.index(marker):] if marker in text else "\n"
        p.write_text(block + "\n" + rest)
        print(f"installed the generated block at the top of {args.readme}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
