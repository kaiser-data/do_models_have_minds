"""Every statement this study makes, with its evidence and its uncertainty.

The paper is being shortened, and shortening is a selection problem: you cannot
choose what survives until every claim is on one page next to what supports it
and what would break it. This builds that page.

Five columns, because a finding is not one thing:

    observation      what was measured, as numbers
    finding          what the numbers show, in one sentence
    interpretation   what it would mean if it holds
    proof            where the numbers come from, resolved
    uncertainty      n, status, and what would falsify it

**Generated, never typed.** Statements and falsifiers come from `claims.json`;
every number is resolved from `paper/numbers.tex`, so a macro that moves also
moves here. A statements table maintained by hand is the same failure as a
paper with typed numbers, one level up -- and this repo has already shipped
that failure twice tonight.

    python3 scripts/statements.py                 # -> site/statements.{json,html}

`interpretation` is the one field a machine cannot derive: it is what the
finding would mean, which is a judgement. It lives in `claims.json` under
`interpretation` where an author has written one, and is reported as missing
where nobody has. Missing is the honest state, not an empty string.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

STATUS_RANK = {"established": 0, "provisional": 1, "open": 2}
_MACRO = re.compile(r"\\newcommand\{\\([A-Za-z]+)\}\{(.*)\}\s*$")
_REF = re.compile(r"\\([A-Za-z]+)")


def load_macros(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in path.read_text().splitlines():
        m = _MACRO.match(line.strip())
        if m:
            out[m.group(1)] = m.group(2)
    return out


def resolve(text: str, macros: dict[str, str]) -> str:
    """Replace every \\Macro with its value; leave unknown ones visible.

    Unknown macros are left as `\\Name` rather than blanked, because a silently
    empty cell reads as "no evidence" when it actually means "this table is out
    of date" -- two very different problems.
    """
    def sub(m):
        return macros.get(m.group(1), m.group(0))
    prev = None
    while prev != text:                      # macros may reference macros
        prev, text = text, _REF.sub(sub, text)
    return text.replace("{}", "").replace("\\%", "%").replace("\\_", "_")


def rows(claims: dict, macros: dict[str, str]) -> list[dict]:
    out = []
    for c in claims["claims"]:
        ev = c.get("evidence", {}) or {}
        observed = {k: resolve(str(v), macros)
                    for k, v in ev.items() if k not in ("note", "source")}
        values = {m: macros.get(m, "MISSING") for m in c.get("macros", [])}
        out.append({
            "id": c["id"],
            "status": c["status"],
            "section": c.get("section", ""),
            "finding": resolve(c["statement"], macros),
            "interpretation": c.get("interpretation"),
            "observation": observed,
            "values": values,
            "note": resolve(ev.get("note", ""), macros),
            "source": ev.get("source", ""),
            "falsifier": resolve(c.get("what_would_falsify", ""), macros),
            "grows_by": resolve(c.get("grows_by", ""), macros),
            "n_missing_macros": sum(1 for v in values.values() if v == "MISSING"),
        })
    out.sort(key=lambda r: (STATUS_RANK.get(r["status"], 9), r["id"]))
    return out


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

CSS = """
:root{--ink:#16181d;--ink2:#4a4f5a;--ink3:#878d99;--line:#e3e6ec;--bg:#fbfbfc;
--est:#1c6b46;--estbg:#e8f4ed;--prov:#8a5a12;--provbg:#fbf1de;--open:#8c2f39;--openbg:#fbe9eb}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
.wrap{max-width:1240px;margin:0 auto;padding:40px 24px 80px}
h1{font-size:26px;margin:0 0 6px;letter-spacing:-.01em}
.sub{color:var(--ink2);margin:0 0 28px;max-width:70ch}
.counts{display:flex;gap:10px;flex-wrap:wrap;margin:0 0 26px}
.pill{font-size:12.5px;padding:5px 11px;border-radius:99px;border:1px solid var(--line);background:#fff}
.pill b{font-variant-numeric:tabular-nums}
table{width:100%;border-collapse:collapse;background:#fff;
border:1px solid var(--line);border-radius:10px;overflow:hidden}
th{text-align:left;font-size:11.5px;text-transform:uppercase;letter-spacing:.07em;
color:var(--ink3);font-weight:600;padding:11px 14px;border-bottom:1px solid var(--line);
background:#f7f8fa}
td{padding:14px;border-bottom:1px solid var(--line);vertical-align:top;font-size:14px}
tr:last-child td{border-bottom:none}
.st{font-size:11px;text-transform:uppercase;letter-spacing:.05em;font-weight:700;
padding:3px 8px;border-radius:5px;white-space:nowrap}
.established{color:var(--est);background:var(--estbg)}
.provisional{color:var(--prov);background:var(--provbg)}
.open{color:var(--open);background:var(--openbg)}
.fid{font:12px ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--ink3);
display:block;margin-top:6px}
.num{font:12.5px ui-monospace,SFMono-Regular,Menlo,monospace;
white-space:nowrap;color:var(--ink2)}
.num b{color:var(--ink)}
.muted{color:var(--ink3)}
.miss{color:var(--open);font-style:italic}
td.obs,td.unc{font-size:13px;color:var(--ink2);max-width:24ch}
td.find{max-width:44ch}
td.unc{max-width:30ch}
.fals{display:block;margin-top:8px;padding-top:8px;border-top:1px dashed var(--line);
font-size:12.5px}
.fals b{color:var(--ink);font-weight:600}
@media(max-width:900px){td.obs,td.find,td.unc{max-width:none}}
"""


def render(data: list[dict], generated: str) -> str:
    counts: dict[str, int] = {}
    for r in data:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    pills = "".join(
        f'<span class="pill"><b>{counts.get(s,0)}</b> {s}</span>'
        for s in ("established", "provisional", "open"))
    missing = sum(r["n_missing_macros"] for r in data)
    if missing:
        pills += f'<span class="pill miss"><b>{missing}</b> unresolved macros</span>'
    n_interp = sum(1 for r in data if not r["interpretation"])
    if n_interp:
        pills += (f'<span class="pill miss"><b>{n_interp}</b> without a written '
                  f'interpretation</span>')

    body = []
    for r in data:
        obs = "<br>".join(
            f'<span class="num">{html.escape(k)} <b>{html.escape(str(v))}</b></span>'
            for k, v in r["observation"].items()) or '<span class="muted">—</span>'
        vals = " ".join(
            f'<span class="num">{html.escape(k)}=<b>{html.escape(v)}</b></span>'
            for k, v in list(r["values"].items())[:6])
        interp = (html.escape(r["interpretation"]) if r["interpretation"]
                  else '<span class="miss">not yet written</span>')
        unc = html.escape(r["note"][:340]) if r["note"] else ""
        if r["falsifier"]:
            unc += (f'<span class="fals"><b>Falsified by:</b> '
                    f'{html.escape(r["falsifier"])}</span>')
        body.append(f"""<tr>
<td><span class="st {r['status']}">{r['status']}</span>
    <span class="fid">{html.escape(r['id'])}<br>{html.escape(r['section'])}</span></td>
<td class="find">{html.escape(r['finding'])}</td>
<td class="obs">{interp}</td>
<td class="obs">{obs}</td>
<td>{vals or '<span class="muted">—</span>'}
    <span class="fid">{html.escape(r['source'])}</span></td>
<td class="unc">{unc or '<span class="muted">—</span>'}</td>
</tr>""")

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex">
<title>Statements — Coherence Without Content</title>
<style>{CSS}</style></head><body><div class="wrap">
<h1>Every statement, with its evidence and its falsifier</h1>
<p class="sub">Generated from <code>claims.json</code> and
<code>paper/numbers.tex</code> &mdash; a working page for deciding what survives
into a shortened paper, not a publication. Rows are ordered
established&nbsp;&rarr;&nbsp;provisional&nbsp;&rarr;&nbsp;open. Every number is
resolved from a macro; anything reading <code>\\Name</code> means this table is
stale, not that evidence is missing.</p>
<div class="counts">{pills}</div>
<table>
<tr><th>status</th><th>finding</th><th>interpretation</th>
<th>observation</th><th>proof</th><th>uncertainty</th></tr>
{"".join(body)}
</table>
<p class="sub" style="margin-top:24px">Generated {html.escape(generated)}.</p>
</div></body></html>"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--claims", default="claims.json")
    ap.add_argument("--numbers", default="paper/numbers.tex")
    ap.add_argument("--out", default="site")
    ap.add_argument("--stamp", default="", help="generation date; empty = omit")
    args = ap.parse_args()

    macros = load_macros(Path(args.numbers))
    data = rows(json.loads(Path(args.claims).read_text()), macros)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "statements.json").write_text(json.dumps(data, indent=2) + "\n")
    (out / "statements.html").write_text(render(data, args.stamp))

    n_missing = sum(r["n_missing_macros"] for r in data)
    n_interp = sum(1 for r in data if not r["interpretation"])
    print(f"{len(data)} statements -> {out}/statements.html")
    for st in ("established", "provisional", "open"):
        k = sum(1 for r in data if r["status"] == st)
        if k:
            print(f"  {st:<13} {k}")
    if n_missing:
        print(f"  {n_missing} macro reference(s) did not resolve")
    if n_interp:
        print(f"  {n_interp} statement(s) have no written interpretation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
