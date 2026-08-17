"""Copy the built sprint PDF to a submission-ready filename.

`paper/sprint.pdf` is the right name inside the repository -- it says which
document it is, and eleven scripts and both handoffs refer to it. It is the
wrong name on a submission form, where the file lands in a reviewer's downloads
folder next to forty others called `paper.pdf` and `submission.pdf`.

So this writes a copy named after the work: authors, title, venue, date.

**Derived, not typed.** The title changed twice in one afternoon. A filename
typed into a form or a shell command would have gone stale on the first of
those changes and nothing would have caught it, which is the same failure the
macro pipeline exists to prevent one layer in. The title here is parsed out of
`sprint.tex` and the authors out of its `\\author` block, so the filename tracks
the paper by construction.

    python3 scripts/submission_pdf.py          # writes dist/<name>.pdf
"""

from __future__ import annotations

import argparse
import re
import shutil
import unicodedata
from pathlib import Path

# Long enough to identify the work, short enough to survive a form field and a
# filesystem that still has opinions about path length.
TITLE_SLUG_MAX = 62


def _detex(s: str) -> str:
    """LaTeX title source into plain words."""
    s = re.sub(r"\\\\", " ", s)                       # line breaks
    s = re.sub(r"\\[a-zA-Z]+\s*", " ", s)             # control sequences
    s = re.sub(r"[{}$~]", " ", s)
    s = re.sub(r"\[[^\]]*\]", " ", s)                 # \\[.45em] spacing args
    return re.sub(r"\s+", " ", s).strip()


def _slug(s: str, maxlen: int | None = None) -> str:
    """ASCII, hyphen-separated, cut on a word boundary.

    Accented characters are folded rather than dropped: Bodorkós becoming
    Bodorks would be a worse filename than Bodorkos, and a submission portal
    is not the place to discover how it handles a non-ASCII byte.
    """
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-")
    if maxlen and len(s) > maxlen:
        cut = s[:maxlen].rsplit("-", 1)[0]
        s = cut or s[:maxlen]
    return s


def _braced(tex: str, command: str) -> str:
    r"""The balanced argument of a command, not the text up to the first brace.

    Written after a non-greedy `\\author\{(.*?)\}` returned "Apart Research" --
    it stopped at the brace closing \\textbf{...} inside the block, and the
    filename came out named after the affiliation. Depth counting is the only
    thing that reads a LaTeX argument containing other commands.
    """
    m = re.search(re.escape(command), tex)
    if not m:
        raise SystemExit(f"no {command}}} in the tex source")
    i, depth = m.end(), 1
    while i < len(tex) and depth:
        depth += (tex[i] == "{") - (tex[i] == "}")
        i += 1
    return tex[m.end():i - 1]


def title_of(tex: str) -> str:
    """The bold main title, which is the first braced group of \\title{...}.

    The subtitle is deliberately not included: it is three lines of method and
    scope, and a filename carrying it would be unusable.
    """
    body = _braced(tex, r"\title{")
    inner = re.search(r"\\textbf\{(.*?)\}\s*\\\\", body, re.S)
    full = _detex(inner.group(1) if inner else body.split(r"\\[")[0])
    # The first clause identifies the paper; the rest is the alternative half of
    # the question and makes the filename unwieldy. Cut on punctuation rather
    # than on a character count, so the name never ends mid-phrase.
    return full.split(",")[0].strip(" ?")


def authors_of(tex: str) -> list[str]:
    """Surnames, in order, from the \\author block.

    The block carries the venue on its first lines and the names on its last,
    because the title block puts the affiliation on top. Split on LaTeX line
    breaks BEFORE stripping control sequences: once \\\\ is flattened to a space
    there is nothing left to tell the affiliation from the authors.
    """
    block = _braced(tex, r"\author{")
    lines = [seg for seg in re.split(r"\\\\(?:\[[^\]]*\])?", block) if _detex(seg)]
    names = [n for n in re.split(r"\\quad|\\and|,", lines[-1]) if _detex(n)]
    surnames = [_detex(n).split()[-1] for n in names if _detex(n).split()]
    if not surnames:
        raise SystemExit("could not find author names")
    return surnames


def filename(tex: str, date: str, venue: str) -> str:
    who = "-".join(_slug(a) for a in authors_of(tex))
    what = _slug(title_of(tex), TITLE_SLUG_MAX)
    return f"{who}_{what}_{_slug(venue)}_{date}.pdf"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tex", default="paper/sprint.tex")
    ap.add_argument("--pdf", default="paper/sprint.pdf")
    ap.add_argument("--out-dir", default="dist")
    ap.add_argument("--date", default="2026-08-17")
    ap.add_argument("--venue", default="Apart Digital Minds Sprint")
    args = ap.parse_args()

    tex = Path(args.tex).read_text()
    src = Path(args.pdf)
    if not src.exists():
        raise SystemExit(f"{src} does not exist; build it first")

    name = filename(tex, args.date, args.venue)
    who_glob = name.split("_")[0]
    out = Path(args.out_dir) / name
    out.parent.mkdir(parents=True, exist_ok=True)
    # Stale copies from an earlier title would sit beside the new one and the
    # wrong one is exactly as easy to upload as the right one.
    for old in out.parent.glob(f"{who_glob}_*.pdf"):
        if old.name != name:
            old.unlink()
            print(f"  removed stale {old.name}")
    shutil.copy2(src, out)
    print(f"wrote {out}")
    print(f"  title:   {title_of(tex)}")
    print(f"  authors: {', '.join(authors_of(tex))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
