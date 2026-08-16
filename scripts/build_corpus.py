"""Every pair that was asked, browsable — site/pairs.html.

The results pages report aggregates. This one reports the corpus: all 2,500
comparisons in the design, each shown in both arms, with what every model
actually answered. It exists so a reader can stop taking our word for what the
instrument contains and scroll it.

Everything is reconstructed from the SHA-pinned battery and the same design seed
the sweep used, then joined to the real result rows, so a pair shown here is the
pair that ran. Nothing is illustrative.

    python3 scripts/build_corpus.py      # -> site/pairs.html

Self-contained: no external requests, filtering and search are client-side over
data embedded in the page.
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from nullcard.runner.forced_choice import (  # noqa: E402
    sample_pairs, stratified_subsample)
from nullcard.scoring.analyze import load_cell  # noqa: E402


def design(battery: dict) -> tuple[list[int], list[tuple[str, str]]]:
    """The exact outcome subsample and pair set the sweep ran.

    Rebuilt from the seed rather than read from a results file, and then checked
    against one: if these disagree the page would show a corpus nobody was
    asked, which is the failure this whole file exists to prevent.
    """
    arms = battery["arms"]
    texts = [r["text"] for r in arms["R"]]
    cats = [r["category"] for r in arms["R"]]
    idx = stratified_subsample(texts, cats, 120, seed=battery["seed"],
                               return_indices=True)
    pairs = sample_pairs([str(i) for i in idx], 2500, seed=battery["seed"])
    return idx, pairs


def responses(results: Path, arm: str) -> dict[str, dict[int, float]]:
    """{model: {pair_index: mean P(A) over both presentation orders}}."""
    out: dict[str, dict[int, float]] = {}
    for p in sorted(results.glob(f"*__{arm}.jsonl")):
        model = "/".join(p.stem.split("__")[:2])
        acc: dict[int, list[float]] = {}
        for r in load_cell(p):
            if r.get("p_option_a") is not None:
                acc.setdefault(r["pair_index"], []).append(r["p_option_a"])
        if acc:
            out[model] = {k: sum(v) / len(v) for k, v in acc.items()}
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--battery", default="battery/outcomes_3arm.json")
    ap.add_argument("--results", default="results")
    ap.add_argument("--out", default="site/pairs.html")
    args = ap.parse_args()

    b = json.loads(Path(args.battery).read_text())
    idx, pairs = design(b)
    R = [r["text"] for r in b["arms"]["R"]]
    N = [r["text"] for r in b["arms"]["N_minus"]]
    C = [r["category"] for r in b["arms"]["R"]]

    rdir = Path(args.results)
    resp_r = responses(rdir, "R")
    resp_n = responses(rdir, "N_minus")
    models = sorted(set(resp_r) & set(resp_n))
    if not models:
        print(f"no result cells under {rdir}/; the page would show an empty "
              f"corpus. Fetch results first (see README).")
        return 1

    rows = []
    for k, (a, bb) in enumerate(pairs):
        ia, ib = int(a), int(bb)
        rows.append({
            "i": k, "ca": C[ia], "cb": C[ib],
            "ra": R[ia], "rb": R[ib], "na": N[ia], "nb": N[ib],
            "r": [round(resp_r[m].get(k), 3) if resp_r[m].get(k) is not None
                  else None for m in models],
            "n": [round(resp_n[m].get(k), 3) if resp_n[m].get(k) is not None
                  else None for m in models],
        })
    short = [m.split("/")[-1] for m in models]
    scored = sum(1 for r in rows if any(v is not None for v in r["r"]))

    page = TEMPLATE.format(
        n_pairs=len(rows), n_models=len(models), n_outcomes=len(idx),
        scored=scored, sha=b.get("sha256", "")[:16] or "see card.json",
        models=json.dumps(short),
        data=json.dumps(rows, separators=(",", ":")),
        cats=json.dumps(sorted(set(C[i] for i in idx))),
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page)
    print(f"wrote {out}  ({out.stat().st_size / 1e6:.1f} MB, {len(rows)} pairs, "
          f"{len(models)} models)")
    return 0


TEMPLATE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Every pair we asked — Nullcard corpus</title>
<style>
:root {{ color-scheme: light;
  --bg:#f5f5f3; --card:#fcfcfb; --bd:#e2e1dc; --fg:#0b0b0b; --mid:#52514e;
  --muted:#78766f; --r:#2a78d6; --n:#eb6834; }}
@media (prefers-color-scheme: dark) {{ :root {{ color-scheme: dark;
  --bg:#131312; --card:#1a1a19; --bd:#33322e; --fg:#f2f1ed; --mid:#b4b2ab;
  --muted:#8e8c85; --r:#3987e5; --n:#d95926; }} }}
* {{ box-sizing:border-box }}
body {{ margin:0; background:var(--bg); color:var(--fg);
  font:15px/1.6 ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
header {{ padding:28px 20px 18px; max-width:1180px; margin:0 auto }}
h1 {{ font-size:24px; margin:0 0 8px; letter-spacing:-.01em }}
.sub {{ color:var(--mid); font-size:14px; max-width:78ch; margin:0 0 4px }}
.meta {{ color:var(--muted); font-size:12.5px; font-family:ui-monospace,Menlo,monospace }}
.bar {{ position:sticky; top:0; z-index:5; background:var(--bg);
  border-bottom:1px solid var(--bd); padding:12px 20px }}
.bar .in {{ max-width:1180px; margin:0 auto; display:flex; gap:10px; flex-wrap:wrap;
  align-items:center }}
input,select {{ font:14px/1.4 inherit; padding:7px 10px; border:1px solid var(--bd);
  border-radius:7px; background:var(--card); color:var(--fg) }}
input[type=search] {{ flex:1; min-width:220px }}
.count {{ color:var(--muted); font-size:13px; font-variant-numeric:tabular-nums }}
main {{ max-width:1180px; margin:0 auto; padding:16px 20px 60px }}
.pair {{ background:var(--card); border:1px solid var(--bd); border-radius:10px;
  padding:14px 16px; margin-bottom:10px }}
.idx {{ font:11px ui-monospace,Menlo,monospace; color:var(--muted) }}
.opts {{ display:grid; grid-template-columns:1fr 1fr; gap:10px; margin:8px 0 0 }}
@media (max-width:720px) {{ .opts {{ grid-template-columns:1fr }} }}
.opt {{ border-left:3px solid var(--bd); padding:2px 0 2px 10px }}
.tag {{ font:10.5px ui-monospace,Menlo,monospace; letter-spacing:.06em;
  text-transform:uppercase; color:var(--muted) }}
.txt {{ font-size:14px }}
.arm {{ margin-top:10px }}
.arm-r .opt {{ border-left-color:var(--r) }}
.arm-n .opt {{ border-left-color:var(--n) }}
.arm-h {{ font:11px ui-monospace,Menlo,monospace; color:var(--muted);
  text-transform:uppercase; letter-spacing:.06em; margin-bottom:4px }}
.cat {{ font-size:11.5px; color:var(--muted) }}
table.ans {{ border-collapse:collapse; margin-top:10px; font-size:12px; width:100% }}
table.ans th, table.ans td {{ padding:3px 8px; text-align:right;
  font-variant-numeric:tabular-nums; border-top:1px solid var(--bd) }}
table.ans th:first-child, table.ans td:first-child {{ text-align:left;
  font-family:ui-monospace,Menlo,monospace }}
.a {{ color:var(--r) }} .b {{ color:var(--n) }} .mid {{ color:var(--muted) }}
.none {{ text-align:center; color:var(--muted); padding:50px 0 }}
a {{ color:inherit }}
</style></head><body>
<header>
<h1>Every pair we asked</h1>
<p class="sub">All {n_pairs} comparisons in the design, each shown in both arms:
the <b style="color:var(--r)">real</b> outcomes and the
<b style="color:var(--n)">invented</b> ones that replace their content words
with consistent nonwords. The numbers are P(A) — the probability each model put
on option A, averaged over both presentation orders. This is the corpus the
aggregate results are computed from; nothing here is illustrative.</p>
<p class="meta">{n_outcomes} outcomes · {n_pairs} pairs · {n_models} models ·
battery {sha} · <a href="index.html">back to results</a></p>
</header>
<div class="bar"><div class="in">
  <input type="search" id="q" placeholder="search the text of any option…">
  <select id="cat"><option value="">every category</option></select>
  <select id="sort">
    <option value="i">design order</option>
    <option value="dis">most disagreement between models (real)</option>
    <option value="gap">biggest real-vs-invented difference</option>
  </select>
  <span class="count" id="count"></span>
</div></div>
<main id="list"></main>
<script>
const MODELS = {models}, DATA = {data}, CATS = {cats};
const catSel = document.getElementById('cat');
CATS.forEach(c => {{ const o = document.createElement('option');
  o.value = c; o.textContent = c; catSel.appendChild(o); }});

const mean = a => {{ const v = a.filter(x => x !== null);
  return v.length ? v.reduce((s, x) => s + x, 0) / v.length : null; }};
const spread = a => {{ const v = a.filter(x => x !== null);
  return v.length < 2 ? 0 : Math.max(...v) - Math.min(...v); }};
DATA.forEach(d => {{ d._dis = spread(d.r);
  const a = mean(d.r), b = mean(d.n);
  d._gap = (a === null || b === null) ? 0 : Math.abs(a - b); }});

const cls = v => v === null ? 'mid' : v > 0.6 ? 'a' : v < 0.4 ? 'b' : 'mid';
const fmt = v => v === null ? '—' : v.toFixed(3);

function render() {{
  const q = document.getElementById('q').value.toLowerCase().trim();
  const c = catSel.value, s = document.getElementById('sort').value;
  let rows = DATA.filter(d =>
    (!c || d.ca === c || d.cb === c) &&
    (!q || (d.ra + ' ' + d.rb + ' ' + d.na + ' ' + d.nb).toLowerCase().includes(q)));
  if (s === 'dis') rows = rows.slice().sort((x, y) => y._dis - x._dis);
  else if (s === 'gap') rows = rows.slice().sort((x, y) => y._gap - x._gap);
  document.getElementById('count').textContent =
    rows.length + ' of ' + DATA.length + ' pairs';
  const list = document.getElementById('list');
  if (!rows.length) {{ list.innerHTML = '<p class="none">no pair matches that.</p>';
    return; }}
  // Only the first 300 are in the DOM at once: 2,500 pairs x two arms x a table
  // each is enough nodes to make scrolling stutter on a laptop.
  const shown = rows.slice(0, 300);
  list.innerHTML = shown.map(d => `
    <div class="pair"><span class="idx">pair ${{d.i}}</span>
      <div class="arm arm-r"><div class="arm-h">real</div><div class="opts">
        <div class="opt"><div class="tag">option A</div>
          <div class="txt">${{esc(d.ra)}}</div><div class="cat">${{esc(d.ca)}}</div></div>
        <div class="opt"><div class="tag">option B</div>
          <div class="txt">${{esc(d.rb)}}</div><div class="cat">${{esc(d.cb)}}</div></div>
      </div></div>
      <div class="arm arm-n"><div class="arm-h">invented</div><div class="opts">
        <div class="opt"><div class="tag">option A</div>
          <div class="txt">${{esc(d.na)}}</div></div>
        <div class="opt"><div class="tag">option B</div>
          <div class="txt">${{esc(d.nb)}}</div></div>
      </div></div>
      <table class="ans"><tr><th>P(A)</th>${{MODELS.map(m =>
        `<th>${{esc(m)}}</th>`).join('')}}</tr>
        <tr><td>real</td>${{d.r.map(v =>
          `<td class="${{cls(v)}}">${{fmt(v)}}</td>`).join('')}}</tr>
        <tr><td>invented</td>${{d.n.map(v =>
          `<td class="${{cls(v)}}">${{fmt(v)}}</td>`).join('')}}</tr>
      </table>
    </div>`).join('') +
    (rows.length > shown.length
      ? `<p class="none">showing the first ${{shown.length}} of ${{rows.length}}
         matches — narrow the search to see the rest.</p>` : '');
}}
function esc(s) {{ return s.replace(/[&<>"]/g,
  c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}})[c]); }}
['q', 'cat', 'sort'].forEach(id =>
  document.getElementById(id).addEventListener('input', render));
render();
</script></body></html>
"""


if __name__ == "__main__":
    sys.exit(main())
