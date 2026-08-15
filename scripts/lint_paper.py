"""Structural checks on the LaTeX sources, for machines without a TeX install.

This is not a compiler and does not pretend to be. It catches the four failures
that actually happen when the paper's inputs are generated from a results card:
a macro used but never emitted, an \\input or figure that was not built, a
citation with no bibliography entry, and an unbalanced environment. A clean run
here means "worth sending to latexmk", not "compiles".

    python3 scripts/lint_paper.py            # exits non-zero on any finding
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Control sequences beginning with a capital that LaTeX/beamer already define.
# The check exists to catch a missing \newcommand from numbers.tex, so this
# list only has to cover what the documents legitimately use.
BUILTIN = {
    "Phi", "Delta", "Rightarrow", "LaTeX", "TeX",
    "Large", "LARGE", "Huge", "N", "R", "U", "P", "S",
    # Standard math operators/symbols LaTeX already defines.
    "Pr", "Re", "Im", "Phi", "Psi", "Omega", "Sigma", "Lambda", "Theta",
}


def check(tex: Path, macros: set[str]) -> list[str]:
    s = tex.read_text()
    errs: list[str] = []
    root = tex.parent

    defined = macros | set(re.findall(r"\\newcommand\{\\([A-Za-z]+)\}", s))
    body = s.split(r"\begin{document}")[-1]
    for m in sorted(set(re.findall(r"\\([A-Z][A-Za-z]*)\b", body)) - defined - BUILTIN):
        errs.append(f"macro \\{m} used but never defined")

    stack: list[str] = []
    for kind, name in re.findall(r"\\(begin|end)\{([a-zA-Z*]+)\}", s):
        if kind == "begin":
            stack.append(name)
        elif not stack or stack[-1] != name:
            errs.append(f"environment mismatch at \\end{{{name}}}")
        else:
            stack.pop()
    if stack:
        errs.append(f"unclosed environments: {stack}")

    for g in re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", s):
        if not (root / "figs" / g).exists() and not (root / g).exists():
            errs.append(f"figure not built: {g}")

    for inc in re.findall(r"\\input\{([^}]+)\}", s):
        if not (root / inc).exists() and not (root / f"{inc}.tex").exists():
            errs.append(f"missing \\input: {inc}")

    bib = root / "refs.bib"
    if bib.exists():
        keys = set(re.findall(r"@\w+\{([^,]+),", bib.read_text()))
        cited = {c.strip()
                 for m in re.findall(r"\\cite[tp]?\{([^}]+)\}", s)
                 for c in m.split(",")}
        for k in sorted(cited - keys):
            errs.append(f"citation with no bib entry: {k}")

    return errs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="paper")
    args = ap.parse_args()

    root = Path(args.dir)
    nums = root / "numbers.tex"
    if not nums.exists():
        print(f"{nums} missing — run scripts/paper_numbers.py first")
        return 1
    macros = set(re.findall(r"\\newcommand\{\\([A-Za-z]+)\}", nums.read_text()))

    failed = False
    for tex in sorted(root.glob("*.tex")):
        if tex.name in {"numbers.tex", "table_main.tex"}:
            continue
        errs = check(tex, macros)
        print(f"{tex}: {'OK' if not errs else str(len(errs)) + ' problem(s)'}")
        for e in errs:
            print(f"    {e}")
        failed |= bool(errs)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
