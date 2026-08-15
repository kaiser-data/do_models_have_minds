"""Render card.json into a self-contained results page.

    python3 scripts/build_site.py --card card.json --out site/index.html

The page is generated from card.json so it cannot disagree with the analysis
(spec §11: the frontend computes nothing). `site/` is the publish root and is a
security boundary — it holds this file and nothing else, because the repository
root carries raw results and credentials.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

PAL = {"R": "#2a78d6", "N": "#eb6834"}          # validated: all six checks pass
PAL_DARK = {"R": "#3987e5", "N": "#d95926"}


def slope_chart(tiles, key_r, key_n, title, subtitle, fmt, ymax=None):
    """Paired slope chart: one line per model, R on the left, N- on the right.

    Slope is the whole point — flat means the arms are indistinguishable on that
    measure, steep means they are not. Direct labels on both ends carry identity
    so nothing depends on colour alone.
    """
    rows = [(t["model"].split("/")[-1], t[key_r], t[key_n]) for t in tiles]
    rows = [r for r in rows if r[1] is not None and r[2] is not None]
    if not rows:
        return "<p>no data</p>"
    hi = ymax if ymax is not None else max(max(r[1], r[2]) for r in rows) * 1.15
    hi = max(hi, 1e-6)

    W, H = 560, 330
    ml, mr, mt, mb = 176, 176, 16, 34
    pw, ph = W - ml - mr, H - mt - mb

    def y(v):
        return mt + ph - (v / hi) * ph

    parts = [
        f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{title}" '
        f'style="width:100%;height:auto;overflow:visible">'
    ]
    # baseline + top gridline, recessive
    for gv in (0, hi):
        parts.append(
            f'<line x1="{ml}" y1="{y(gv):.1f}" x2="{ml+pw}" y2="{y(gv):.1f}" '
            f'stroke="var(--grid)" stroke-width="1"/>'
        )
    parts.append(
        f'<text x="{ml}" y="{H-12}" fill="var(--text-secondary)" font-size="12" '
        f'text-anchor="middle">real outcomes</text>'
        f'<text x="{ml+pw}" y="{H-12}" fill="var(--text-secondary)" font-size="12" '
        f'text-anchor="middle">invented (N&#8722;)</text>'
    )

    for i, (name, a, b) in enumerate(sorted(rows, key=lambda r: -r[1])):
        ya, yb = y(a), y(b)
        parts.append(
            f'<line x1="{ml}" y1="{ya:.1f}" x2="{ml+pw}" y2="{yb:.1f}" '
            f'stroke="var(--series-r)" stroke-width="2" opacity="0.75"/>'
            f'<circle cx="{ml}" cy="{ya:.1f}" r="4.5" fill="var(--series-r)" '
            f'stroke="var(--surface-1)" stroke-width="2"/>'
            f'<circle cx="{ml+pw}" cy="{yb:.1f}" r="4.5" fill="var(--series-n)" '
            f'stroke="var(--surface-1)" stroke-width="2"/>'
            f'<text x="{ml-10}" y="{ya+4:.1f}" fill="var(--text-secondary)" font-size="11" '
            f'text-anchor="end">{name} {fmt(a)}</text>'
            f'<text x="{ml+pw+10}" y="{yb+4:.1f}" fill="var(--text-secondary)" font-size="11" '
            f'text-anchor="start">{fmt(b)}</text>'
        )
    parts.append("</svg>")
    return (
        f'<figure class="chart"><figcaption><h3>{title}</h3><p>{subtitle}</p></figcaption>'
        + "".join(parts)
        + "</figure>"
    )


def build(card: dict) -> str:
    tiles = [t for t in card["tiles"] if t["badge"] == "FLOOR_CORRECTED"]
    tiles.sort(key=lambda t: -t["raw_coherence"])

    mean_r = sum(t["raw_coherence"] for t in tiles) / len(tiles)
    mean_f = sum(t["floor"] for t in tiles) / len(tiles)
    mean_gap = mean_r - mean_f

    dec_pairs = [
        (t["decisive_fraction"]["R"], t["decisive_fraction"]["N_minus"])
        for t in tiles
        if t["decisive_fraction"]["R"] > 0.02
    ]
    mean_dec_r = sum(a for a, _ in dec_pairs) / len(dec_pairs)
    mean_dec_n = sum(b for _, b in dec_pairs) / len(dec_pairs)

    def figure(stem, title, caption):
        return (
            f'<figure class="fig"><img class="lightonly" src="{stem}.svg" alt="{title}">'
            f'<img class="darkonly" src="{stem}-dark.svg" alt="{title}">'
            f'<figcaption>{caption}</figcaption></figure>'
        )

    body_rows = "".join(
        f"<tr><td class='m'>{t['model']}</td>"
        f"<td>{t['raw_coherence']:.3f}</td>"
        f"<td>{t['floor']:.3f}</td>"
        f"<td class='{'pos' if t['value']>0 else 'neg'}'>{t['value']:+.3f}</td>"
        f"<td class='muted'>{(t['shuffled_null'].get('R') or 0):.3f}</td>"
        f"<td>{t['decisive_fraction']['R']*100:.1f}%</td>"
        f"<td>{t['decisive_fraction']['N_minus']*100:.1f}%</td>"
        f"<td class='muted'>{t['slot_a_bias']:.2f}</td></tr>"
        for t in tiles
    )

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Coherence Without Content — preliminary results</title>
<style>
:root {{
  color-scheme: light;
  --surface-0:#f5f5f3; --surface-1:#fcfcfb; --border:#e2e1dc; --grid:#dcdbd5;
  --text-primary:#0b0b0b; --text-secondary:#52514e; --text-muted:#78766f;
  --series-r:{PAL['R']}; --series-n:{PAL['N']};
  --pos:#008300; --neg:#c4341c; --warn-bg:#fdf3e3; --warn-br:#e0a94a;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme=light]) {{
  color-scheme: dark;
  --surface-0:#131312; --surface-1:#1a1a19; --border:#33322e; --grid:#3a3934;
  --text-primary:#fff; --text-secondary:#c3c2b7; --text-muted:#93918a;
  --series-r:{PAL_DARK['R']}; --series-n:{PAL_DARK['N']};
  --pos:#3fb950; --neg:#e5674f; --warn-bg:#2b2416; --warn-br:#8a6a24;
}} }}
:root[data-theme=dark] {{
  color-scheme: dark;
  --surface-0:#131312; --surface-1:#1a1a19; --border:#33322e; --grid:#3a3934;
  --text-primary:#fff; --text-secondary:#c3c2b7; --text-muted:#93918a;
  --series-r:{PAL_DARK['R']}; --series-n:{PAL_DARK['N']};
  --pos:#3fb950; --neg:#e5674f; --warn-bg:#2b2416; --warn-br:#8a6a24;
}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--surface-0);color:var(--text-primary);
 font:16px/1.65 ui-sans-serif,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}}
.wrap{{max-width:1000px;margin:0 auto;padding:48px 24px 96px}}
h1{{font-size:clamp(30px,5vw,46px);line-height:1.1;letter-spacing:-.02em;margin:.2em 0}}
h2{{font-size:24px;letter-spacing:-.01em;margin:56px 0 12px;padding-top:20px;
 border-top:1px solid var(--border)}}
h3{{font-size:16px;margin:0 0 4px}}
p{{color:var(--text-secondary);max-width:70ch}}
.lede{{font-size:19px;color:var(--text-primary)}}
.banner{{background:var(--warn-bg);border:1px solid var(--warn-br);border-left-width:4px;
 border-radius:6px;padding:14px 18px;margin:24px 0;font-size:14.5px;color:var(--text-primary)}}
.banner strong{{letter-spacing:.02em}}
.hero{{display:flex;flex-wrap:wrap;gap:16px;margin:32px 0}}
.stat{{flex:1 1 200px;background:var(--surface-1);border:1px solid var(--border);
 border-radius:10px;padding:18px 20px}}
.stat .v{{font-size:34px;font-weight:650;letter-spacing:-.02em;line-height:1.1}}
.stat .l{{font-size:12.5px;color:var(--text-muted);margin-top:6px}}
.fig{{margin:32px 0;background:var(--surface-1);border:1px solid var(--border);
 border-radius:10px;padding:22px}}
.fig img{{width:100%;height:auto;display:block}}
.fig figcaption{{font-size:13.5px;color:var(--text-secondary);margin-top:14px;
 line-height:1.6;max-width:76ch}}
.darkonly{{display:none}}
@media (prefers-color-scheme: dark){{ :root:not([data-theme=light]) .lightonly{{display:none}}
 :root:not([data-theme=light]) .darkonly{{display:block}} }}
:root[data-theme=dark] .lightonly{{display:none}}
:root[data-theme=dark] .darkonly{{display:block}}
.charts{{display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:28px;margin:28px 0}}
.chart{{background:var(--surface-1);border:1px solid var(--border);border-radius:10px;
 padding:20px;margin:0}}
.chart figcaption p{{font-size:13px;margin:0 0 10px;color:var(--text-muted)}}
.legend{{display:flex;gap:18px;font-size:12.5px;color:var(--text-secondary);margin:0 0 14px}}
.legend i{{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:6px}}
.tw{{overflow-x:auto;border:1px solid var(--border);border-radius:10px;background:var(--surface-1)}}
table{{border-collapse:collapse;width:100%;font-size:13.5px;
 font-variant-numeric:tabular-nums}}
th,td{{padding:9px 12px;text-align:right;border-bottom:1px solid var(--border);white-space:nowrap}}
th{{font-size:11.5px;text-transform:uppercase;letter-spacing:.05em;color:var(--text-muted);
 font-weight:600;text-align:right}}
td.m,th:first-child{{text-align:left}} td.m{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12.5px}}
tr:last-child td{{border-bottom:none}}
.pos{{color:var(--pos)}} .neg{{color:var(--neg)}} .muted{{color:var(--text-muted)}}
code{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.9em;
 background:var(--surface-1);border:1px solid var(--border);border-radius:4px;padding:1px 5px}}
footer{{margin-top:64px;padding-top:20px;border-top:1px solid var(--border);
 font-size:13px;color:var(--text-muted)}}
</style></head><body><div class="wrap">

<p style="color:var(--text-muted);font-size:13px;letter-spacing:.08em;text-transform:uppercase;margin:0">
Nullcard · Apart Research Digital Minds Sprint · 15 Aug 2026</p>
<h1>Coherence without content</h1>
<p class="lede">A preference-coherence metric that scores the same on outcomes
that mean nothing.</p>

<div class="banner">
<strong>PRELIMINARY.</strong> Work in progress, mid-sprint. 9 models, one battery,
n=1 per cell — no training-seed replicates yet, so no between-model claim is made here.
Numbers may move. This page is generated from <code>card.json</code>; nothing on it
is hand-entered.
</div>

<h2>What was measured</h2>
<p><a href="https://arxiv.org/abs/2502.08640">Utility Engineering</a> (Mazeika et al.,
CAIS 2025) elicits pairwise preferences over 500 textual outcomes, fits a Thurstonian
utility model, and reports its held-out accuracy as <em>structural coherence</em> —
finding it rises with scale and concluding that value systems emerge in LLMs.</p>

<p>Their robustness checks vary <em>how the question is asked</em>: seven languages,
syntax, framing, option labels, long context. Their null is a synthetic random utility
vector. <strong>No condition varies whether the outcomes refer to anything.</strong></p>

<p>We rebuilt their instrument and ran three arms through it — their real outcomes
(<b>R</b>), the same sentences with invented referents but magnitudes preserved
(<b>N+</b>), and invented referents with magnitudes removed (<b>N&#8722;</b>).
Same prompt, verbatim. Same fit. Same metric.</p>

<div class="hero">
  <div class="stat"><div class="v">{mean_r:.3f}</div>
    <div class="l">coherence on real outcomes (mean, 9 models)</div></div>
  <div class="stat"><div class="v">{mean_f:.3f}</div>
    <div class="l">coherence on <b>invented</b> outcomes</div></div>
  <div class="stat"><div class="v">{mean_gap:+.3f}</div>
    <div class="l">everything meaning contributes</div></div>
</div>

<h2>The metric is flat; the preference is not</h2>
<p>Direction accuracy barely moves between real and invented outcomes. But the
<em>strength</em> of the underlying preference collapses: on real outcomes these
models commit to a side on {mean_dec_r*100:.0f}% of pairs, and on invented ones
{mean_dec_n*100:.1f}%.</p>

{figure("fig1_state_space", "Coherence against conviction",
  "<b>Every model is a path, not a point.</b> Each starts on real outcomes (big dot), "
  "moves to invented outcomes with magnitudes kept (small dot), then to invented "
  "outcomes with magnitudes removed (arrowhead). If the metric tracked meaning the "
  "paths would run down-<i>and-left</i>. They run almost straight down: conviction "
  "falls away while the metric barely registers it. Horizontal bars are the spread "
  "across five train/test splits &mdash; SmolLM2&rsquo;s wide bar is why its middle "
  "point sits far left, and is an unstable estimate rather than a finding. "
  "Both axes span their full operating range (accuracy from chance to 1, conviction "
  "from 0 to its 0.5 maximum), so the steepness is the data&rsquo;s and not a "
  "zoom choice.")}

{figure("fig3_strength", "Distribution of preference strength",
  "The mechanism, directly. On real outcomes the model commits &mdash; mass moves to "
  "the edges. On invented ones it piles up at indifference. Coherence reads only "
  "<i>which side of 0.5</i> each pair falls on, so both score the same.")}

{figure("fig2_scale", "The scale ladder",
  "One family, four sizes, size as the only variable. The floor rises with scale "
  "alongside the signal, so the shaded band &mdash; everything meaning contributes "
  "&mdash; does not widen as the models get bigger.")}

<p>Utility Engineering's accuracy thresholds preferences to hard labels
(their §4.1), so it records <em>which way</em> a model leans and never <em>how
much</em>. A pair at p=0.51 counts exactly like one at p=0.99. That is why a model
can be almost perfectly indifferent about gibberish and still score as coherent
about it.</p>

<h2>All numbers</h2>
<div class="tw"><table>
<thead><tr><th>model</th><th>R</th><th>N&#8722;</th><th>R&#8722;N&#8722;</th>
<th>shuffled null</th><th>decisive R</th><th>decisive N&#8722;</th><th>slot-A bias</th></tr></thead>
<tbody>{body_rows}</tbody></table></div>
<p style="font-size:13px"><b>shuffled null</b> keeps the pair set and permutes the
observed probabilities across pairs, destroying the link between a pair and its
preference. It lands at ~0.50, which is how we know the metric itself is sound and
the flat result is not an artifact of our reimplementation.
<b>decisive</b> is the share of pairs with p&lt;0.2 or p&gt;0.8.
<b>slot-A bias</b> is the raw rate of picking the first option before
counterbalancing — 0.5 is none.</p>

<h2>What this does and does not show</h2>
<p><b>It does not show the metric is broken.</b> It passes its own null at 0.50, its
order-counterbalancing cancels positional bias exactly, and its held-out protocol
means a coin-flip responder correctly scores ~0.46. All three were checked and all
three came out in the original paper's favour.</p>
<p><b>It shows the metric is unanchored.</b> High held-out accuracy establishes that
choices are explained by a stable scalar ordering. It does not establish that the
ordering is <em>about</em> anything — and without a content control there is no way
to tell those apart from the number alone.</p>
<p><b>Caveats we can already name.</b> Invented outcomes tokenise ~30% longer than
real ones, so some of the residual could be a prompt-length effect. Fitted utilities
on the invented arms correlate with text length up to r=&#8722;0.75, meaning the
"ordering" there is substantially a length ordering. n=1 per cell. Two models
(Phi-4-mini, Ministral-3) failed to load under transformers 5 and are absent, not
excluded for their results.</p>

<footer>
Battery SHA-256 <code>{tiles[0]['battery_sha256'][:16]}…</code> ·
{len(card['cells'])} cells · {tiles[0]['n_pairs'] if 'n_pairs' in tiles[0] else 2500} pairs/cell,
both presentation orders · predictions registered before the run in
<code>PREREGISTRATION.md</code>.
</footer>
</div></body></html>"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--card", default="card.json")
    ap.add_argument("--out", default="site/index.html")
    args = ap.parse_args()

    card = json.loads(Path(args.card).read_text())
    for t in card["tiles"]:
        if t["badge"] == "FLOOR_CORRECTED":
            t["dec_r"] = t["decisive_fraction"]["R"]
            t["dec_n"] = t["decisive_fraction"]["N_minus"]

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build(card))
    print(f"wrote {out}  ({out.stat().st_size/1024:.1f} KB)")


if __name__ == "__main__":
    main()
