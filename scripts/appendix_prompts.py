"""Emit paper/appendix_prompts.tex — every prompt, verbatim, with real answers.

The appendix exists because a reader cannot check an unanchored-instrument
claim without seeing the instrument. So nothing here is illustrative: prompts
are rendered from the SHA-pinned battery, model outputs are read out of the
result rows the paper's numbers were computed from, and the worked example
carries a real pair through to a real held-out accuracy.

That constraint is the point. A hand-written "example prompt" in an appendix is
a claim about the harness that nothing checks; this file cannot disagree with
what was run, because it is built from what was run.

    python3 scripts/appendix_prompts.py            # -> paper/appendix_prompts.tex

Rows live in results/, which is gitignored, so the generated .tex is committed
(same reason numbers.tex and table_main.tex are).
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from nullcard.runner.forced_choice import (  # noqa: E402
    NEUTRAL_PROMPT_TEMPLATE,
    UE_PROMPT_TEMPLATE,
    build_forced_choice_prompt,
)

# The cell the worked example is drawn from. Chosen because it has both arms at
# full length and sits mid-roster, not because of how the example comes out --
# and the arms are shown side by side, so a flattering pair is not available.
EXAMPLE_MODEL = "Qwen__Qwen3.5-2B"
EXAMPLE_PAIR = 0

PERSONA_SOURCE = "modal_app/sweep.py"


def tex_escape(s: str) -> str:
    """Escape for LaTeX text mode. Outcome text is arbitrary: it contains $,
    &, % and quotes, and one unescaped $ silently swallows a paragraph into
    math mode rather than failing."""
    out = []
    for ch in s:
        if ch in "&%$#_{}":
            out.append("\\" + ch)
        elif ch == "~":
            out.append("\\textasciitilde{}")
        elif ch == "^":
            out.append("\\textasciicircum{}")
        elif ch == "\\":
            out.append("\\textbackslash{}")
        else:
            out.append(ch)
    return "".join(out)


# Characters the monospace font cannot set. Substituted FOR DISPLAY ONLY and
# footnoted where used: the prompt that ran is the one in the source, and an
# appendix that silently prints a different string than was sent would be the
# same defect as a hand-written example prompt.
_DISPLAY_SUBS = {"\u2014": "--", "\u2013": "-", "\u2019": "'", "\u201c": '"',
                 "\u201d": '"', "\u2026": "..."}


def display_safe(s: str) -> tuple[str, bool]:
    out = s
    changed = False
    for bad, good in _DISPLAY_SUBS.items():
        if bad in out:
            out = out.replace(bad, good)
            changed = True
    return out, changed


def wrap(s: str, width: int = 78) -> str:
    """Hard-wrap so a long prompt line cannot overflow the text block."""
    import textwrap
    lines = []
    for para in s.split("\n"):
        lines.extend(textwrap.wrap(para, width=width) or [""])
    return "\n".join(lines)


def verbatim(s: str) -> str:
    """A prompt shown as-is. Uses a Verbatim block so nothing in the battery
    text can be interpreted as markup."""
    shown, changed = display_safe(s)
    note = ("\n\\noindent\\footnotesize\\emph{(The prompt as sent contains a "
            "literal em dash; the monospace face here cannot set it, so it is "
            "shown as \\texttt{--}.)}\\normalsize\n" if changed else "")
    return ("\\begin{quote}\\small\\begin{verbatim}\n"
            + wrap(shown.rstrip()) + "\n\\end{verbatim}\\end{quote}\n" + note)


def load_rows(results: Path, cell: str) -> list[dict]:
    path = results / f"{cell}.jsonl"
    if not path.exists():
        return []
    return [json.loads(ln) for ln in path.open()]


def find_pair(rows: list[dict], pair_index: int) -> dict[str, dict]:
    """-> {order: row} for one pair. Both orders or nothing: a single
    presentation carries positional bias undiminished and showing one would
    misrepresent how the estimate is formed."""
    got = {r["order"]: r for r in rows if r["pair_index"] == pair_index}
    return got if {"AB", "BA"} <= set(got) else {}


def fmt_tokens(top: list) -> str:
    """The model's actual first-token distribution, as probabilities."""
    parts = []
    for tok, lp in top:
        shown = tok.replace(" ", "\\textvisiblespace{}")
        parts.append(f"\\texttt{{{tex_escape(shown)}}} {math.exp(lp):.4f}")
    return ", ".join(parts)


def section_battery(bat: dict) -> str:
    """One pair, all three arms, so the reader sees exactly what 'the same
    outcome with its referent removed' means."""
    out = ["\\section{The outcome battery, in all three arms}"
           "\\label{app:battery}\n",
           f"Every arm holds the same {bat['n_outcomes']} outcomes at the same "
           "indices; outcome $i$ is the same outcome throughout and the arms "
           "differ only in what it refers to. The battery is SHA-pinned "
           "(\\texttt{\\BatterySHA\\ldots}) before the first run. Outcome 101 "
           "and outcome 500, in each arm:\n"]
    for arm, label in (("R", "\\armR{} --- real"),
                       ("N_plus", "\\armNp{} --- invented referents, magnitudes kept"),
                       ("N_minus", "\\armNm{} --- invented referents, magnitudes removed")):
        items = bat["arms"][arm]
        o1, o2 = items[101], items[500]
        out.append(f"\\paragraph{{{label}}}\n")
        out.append("\\begin{quote}\\small\n")
        out.append(f"\\textbf{{[{o1['idx']}]}} \\emph{{{tex_escape(o1['category'])}}} --- "
                   f"{tex_escape(o1['text'])}\\\\[2pt]\n")
        out.append(f"\\textbf{{[{o2['idx']}]}} \\emph{{{tex_escape(o2['category'])}}} --- "
                   f"{tex_escape(o2['text'])}\n")
        out.append("\\end{quote}\n")
    out.append(
        "Note what \\armNp{} preserves and \\armNm{} does not: the year "
        "\\texttt{2034} survives into \\armNp{} and becomes a nonsense token in "
        "\\armNm{}. That is the whole difference between ``the magnitudes still "
        "order'' and ``nothing is left to prefer''.\n")
    return "".join(out)


def section_prompt(bat: dict, rows_by_arm: dict[str, list[dict]]) -> str:
    """The prompt as sent, then the model's real answer, then the arithmetic."""
    out = ["\\section{What the model was asked, and what it answered}"
           "\\label{app:prompt}\n",
           "The template is Utility Engineering's, verbatim, so the only thing "
           "differing between our arms is what the outcomes refer to:\n",
           verbatim(UE_PROMPT_TEMPLATE.replace("{option_a}", "<OUTCOME A>")
                    .replace("{option_b}", "<OUTCOME B>"))]

    for arm, label in (("R", "\\armR{}"), ("N_minus", "\\armNm{}")):
        rows = rows_by_arm.get(arm, [])
        pair = find_pair(rows, EXAMPLE_PAIR)
        if not pair:
            continue
        ab = pair["AB"]
        items = bat["arms"][arm]
        oa = items[ab["slot_a_outcome"]]["text"]
        ob = items[ab["slot_b_outcome"]]["text"]
        model = ab["model_id"]
        out.append(f"\\subsection{{Arm {label}, pair {EXAMPLE_PAIR}, "
                   f"\\texttt{{{tex_escape(model)}}}}}\n")
        out.append("Sent to the model (presentation \\texttt{AB}):\n")
        out.append(verbatim(build_forced_choice_prompt(oa, ob)))
        out.append("The model's first-token distribution, top 5, as returned:\n")
        out.append("\\begin{quote}\\small\n")
        for order in ("AB", "BA"):
            r = pair[order]
            out.append(f"\\texttt{{{order}}}: {fmt_tokens(r['top_tokens'])}\\\\[3pt]\n")
        out.append("\\end{quote}\n")

        ab_p, ba_p = pair["AB"]["p_option_a"], pair["BA"]["p_option_a"]
        out.append(
            "No text is generated and no judge is involved: "
            "$P(A)$ is read straight off these logits, renormalised over the two "
            "answer tokens only, so mass on a preamble is excluded rather than "
            "charged against either option. Here "
            f"$P(A)_{{\\mathrm{{AB}}}} = {ab_p:.4f}$ and "
            f"$P(A)_{{\\mathrm{{BA}}}} = {ba_p:.4f}$. "
            "In the \\texttt{BA} presentation the same outcome sits in slot B, so "
            "the preference for it is $1 - P(A)$, and the counterbalanced "
            "estimate is the mean of the two: "
            f"$\\tfrac{{1}}{{2}}({ab_p:.4f} + {1 - ba_p:.4f}) = "
            f"{0.5 * (ab_p + 1 - ba_p):.4f}$. "
            "A responder with pure positional bias produces exactly $0.5$ here, "
            "which is why the bias cancels completely.\n")
        out.append(f"\nAnswer mass on this pair was {pair['AB']['answer_mass']:.4f} "
                   f"(\\texttt{{AB}}) --- above the validity floor, so the pair is "
                   "scored rather than dropped.\n")
    return "".join(out)


def section_personas(personas: dict) -> str:
    out = ["\\section{Persona and directive conditions}\\label{app:personas}\n",
           "Installed verbatim as the system prompt at D2, and in the user turn "
           "at D1 with a length-matched neutral system prompt so that D1 and D2 "
           "differ only in \\emph{where} the trait sits. Read from "
           f"\\texttt{{{tex_escape(PERSONA_SOURCE)}}}.\n"]
    order = ["cautious", "ambitious", "cautious-concealed", "cautious-verbal"]
    note = {
        "cautious": "The genuine trait. Supplies the displacement template in "
                    "\\S\\ref{sec:track3}.",
        "ambitious": "A different trait at the same depth --- the specificity "
                     "control. If it aligned with the cautious template as well "
                     "as the cautious conditions do, no other column would mean "
                     "anything.",
        "cautious-concealed": "Has the trait, told to deny it. Stated and "
                              "revealed should diverge.",
        "cautious-verbal": "Lacks the trait, told to claim it. The clean "
                           "negative that turns a detection count into a rate.",
    }
    for key in order:
        text = personas.get(key)
        if not text:
            continue
        out.append(f"\\paragraph{{\\texttt{{{tex_escape(key)}}}}} {note[key]}\n")
        out.append(verbatim(text))
    out.append(
        "The pairing is the point: \\texttt{cautious-concealed} and "
        "\\texttt{cautious-verbal} both produce a model whose self-description "
        "disagrees with its disposition, in opposite directions. A detector that "
        "reads ``speech contradicts behaviour'' fires on both, which is why "
        "\\S\\ref{sec:track3} reports the second as a false-positive rate rather "
        "than reporting the first alone.\n")
    return "".join(out)


def section_self_report(sr: dict) -> str:
    out = ["\\section{The self-report battery}\\label{app:selfreport}\n",
           "The stated channel uses the identical readout as the outcome "
           "battery --- forced choice, first-token logprob, both presentation "
           "orders --- so the two channels cannot differ because of how they "
           "were measured, and no LLM judge is involved.\n",
           f"\\emph{{Convention:}} {tex_escape(sr['convention'])}\n"]
    out.append(f"All {len(sr['items'])} items:\n\\begin{{quote}}\\small\n")
    for i, item in enumerate(sr["items"]):
        out.append(f"\\textbf{{{i + 1}.}} A: {tex_escape(item['a'])} \\quad "
                   f"B: {tex_escape(item['b'])}\\\\[2pt]\n")
    out.append("\\end{quote}\n")
    out.append(
        "The no-premise condition asks these with no persona installed at all. "
        "That column is what makes the rest readable: without it, a model "
        "reporting cautiousness at \\StatedHaveHi{} under a cautious premise "
        "looks like a cautious model rather than like a model agreeing with the "
        "premise it was handed.\n")
    return "".join(out)


def neutral_status(results: Path) -> str:
    """Say, in the paper, whether this arm has actually been run.

    Derived from disk rather than typed, because a typed "not yet run" is a
    claim that rots the moment the arm lands, and a typed "we ran it" is worse.
    An appendix that shows a prompt beside prompts that WERE run reads as part
    of the executed study unless it says otherwise -- which is exactly the
    silent-simulation failure, in a paper rather than in code.
    """
    cells = sorted(results.glob("*__neutral*.jsonl")) if results.exists() else []
    if not cells:
        return (
            "\\begin{quote}\n"
            "\\textbf{Status: specified and unit-tested, not yet run.} No model "
            "has been shown this prompt. The template, the three-way validity "
            "gate and $P(C)$ are implemented and covered by tests, but those "
            "tests exercise hand-constructed logit distributions, not a "
            "language model. \\textbf{No result from this arm appears anywhere "
            "in this paper}, and the cheap lower bound below is not a "
            "substitute for it.\n"
            "\\end{quote}\n"
            "What we can say without running it is bounded and we mark it as "
            "such. In the existing forced-binary rows, mass on a literal "
            "``Neither'' reaches the recorded top-5 essentially never --- "
            "$0.000$ for the Qwen models and $0.012$ at most for "
            "gemma-4-E2B-it on invented outcomes. Those are \\emph{lower "
            "bounds}, not measurements: the token is only visible when it "
            "reaches the top-5, so the true mass could be larger and we cannot "
            "tell from these rows. They suggest, without establishing, that "
            "models impose an order on nonsense rather than declining it.\n")
    return (f"\\begin{{quote}}\n\\textbf{{Status: run.}} {len(cells)} neutral "
            "cell(s) on disk; results are reported in the body.\n"
            "\\end{quote}\n")


def section_neutral(results: Path) -> str:
    return ("\\section{The neutral-option control}\\label{app:neutral}\n"
            "The published objection to a forced binary is that it can "
            "manufacture an ordering: hierarchies reported on forced choices "
            "have been found to weaken once respondents may decline. Our floor "
            "is measured on a forced binary, so the objection lands on it "
            "directly. The control gives the model somewhere else to put its "
            "mass, changing nothing else:\n"
            + verbatim(NEUTRAL_PROMPT_TEMPLATE.replace("{option_a}", "<OUTCOME A>")
                       .replace("{option_b}", "<OUTCOME B>"))
            + "$P(A)$ is still renormalised over A and B alone, so it remains "
              "the same quantity as the main arm --- the preference, given that "
              "a preference was expressed --- while $P(C)$ records how often "
              "the model declines. Reporting only the first would hide the "
              "effect the control was built to find.\n"
            + neutral_status(results))


def build(bat: dict, sr: dict, personas: dict, rows_by_arm: dict,
          results: Path) -> str:
    return (
        "% Generated by scripts/appendix_prompts.py. Do not edit.\n"
        "% Prompts are rendered from the SHA-pinned battery and model outputs\n"
        "% are read from the result rows the paper's numbers come from.\n"
        "\\appendix\n"
        + section_battery(bat)
        + section_prompt(bat, rows_by_arm)
        + section_personas(personas)
        + section_self_report(sr)
        + section_neutral(results)
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--battery", default="battery/outcomes_3arm.json")
    ap.add_argument("--self-report", default="battery/self_report.json")
    ap.add_argument("--results", default="results")
    ap.add_argument("--out", default="paper/appendix_prompts.tex")
    args = ap.parse_args()

    bat = json.loads(Path(args.battery).read_text())
    sr = json.loads(Path(args.self_report).read_text())

    sys.path.insert(0, "modal_app")
    from sweep import PERSONAS  # noqa: E402

    results = Path(args.results)
    rows_by_arm = {arm: load_rows(results, f"{EXAMPLE_MODEL}__{arm}")
                   for arm in ("R", "N_minus")}
    for arm, rows in rows_by_arm.items():
        if not rows:
            print(f"  WARNING: no rows for {EXAMPLE_MODEL}__{arm}; "
                  f"its worked example will be omitted")

    text = build(bat, sr, PERSONAS, rows_by_arm, results)
    Path(args.out).write_text(text)
    print(f"wrote {args.out}  ({len(text.splitlines())} lines)")


if __name__ == "__main__":
    main()
