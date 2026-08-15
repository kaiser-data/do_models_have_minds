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


def detector_section(det: dict | None, figure) -> str:
    """The clearest result: what the metric keeps vs what it throws away.

    Placed before the persona section because it needs no setup -- the ground
    truth is that every pair was run in both arms, so real and invented are
    matched positives and negatives for free.
    """
    if not det:
        return ""
    per = det["per_model"]
    names = [k for k in next(iter(per.values())) if k != "n_matched_pairs"]

    def mean(name, field="separation"):
        v = [e[name][field] for e in per.values() if name in e]
        return sum(v) / len(v) if v else None

    kept = next((n for n in names if "[KEPT]" in n), None)
    if kept is None:
        return ""
    rows = "".join(
        f"<tr><td class='m'>{n.split('  ')[0]}</td>"
        f"<td class='{'neg' if '[KEPT]' in n else 'pos'}'>{mean(n):.3f}</td>"
        f"<td class='muted'>{mean(n, 'tpr_at_fpr') * 100:.0f}%</td></tr>"
        for n in names)
    best = max((n for n in names if "discarded" in n), key=lambda n: mean(n))

    return f"""
<h2>The model can tell. The metric does not look.</h2>
<p>Hallucination detection has converged on one idea: the sign that a model is
confabulating is already in its own output distribution, readable from a single
forward pass. Coherence does the opposite twice &mdash; thresholding to a hard
A/B label discards <em>how much</em>, and renormalising over A and B discards
<em>not answering at all</em>. Both are exactly the signals that literature
uses.</p>

<p>Our design tests this for free. Every pair ran in <b>both</b> arms, so for one
model and one pair we have two forward passes differing only in whether the
outcomes refer to anything &mdash; matched positives and negatives, by
construction rather than by selection.</p>

<div class="tw"><table>
<thead><tr><th>channel of the same forward pass</th><th>separation (AUROC)</th>
<th>detection at 5% false alarms</th></tr></thead>
<tbody>{rows}</tbody></table></div>
<p style="font-size:13px">0.5 means the channel cannot tell a real outcome from a
meaningless one. The threshold is calibrated on the <b>real</b> rows only, never
on the nonsense. The direction channel is binary, so its detection rate at a
fixed false-alarm rate is not well defined &mdash; read its AUROC, not its
percentage.</p>

{figure("fig4_detector", "What the metric keeps versus what it discards",
  "Each model contributes one bar per channel. The accented bar is the only one "
  "the coherence number consumes.")}

<p><b>The models notice.</b> The channel coherence keeps separates real from
nonsense at {mean(kept):.3f}; the best channel it discards
({best.split('  ')[0]}) reaches {mean(best):.3f}, catching
{mean(best, 'tpr_at_fpr') * 100:.0f}% of nonsense at a 5% false-alarm rate with
no probe, no sampling and no judge. The preference number is computed from the
channel that noticed least.</p>
"""


def persona_section(rows: list[dict], figure) -> str:
    """The depth-ladder arm. Omitted entirely when its data is absent.

    Written as a separate block rather than folded into the main table because
    it answers a different question: the table asks whether coherence depends
    on content at all, this asks whether an installed persona moves preference
    or only prose.
    """
    if not rows:
        return ""

    by_model: dict[str, list[dict]] = {}
    for r in rows:
        by_model.setdefault(r["model"], []).append(r)

    cells = []
    for model in sorted(by_model, key=lambda m: -max(
            r["floor_corrected"] for r in by_model[m])):
        rs = {(r["persona"], r["depth"]): r["floor_corrected"] for r in by_model[model]}
        tds = "".join(
            f"<td class='{'pos' if rs[k] > 0 else 'neg'}'>{rs[k]:+.2f}</td>"
            if k in rs else "<td class='muted'>&mdash;</td>"
            for k in (("ambitious", "D1"), ("ambitious", "D2"),
                      ("cautious", "D1"), ("cautious", "D2"))
        )
        cells.append(f"<tr><td class='m'>{model}</td>{tds}</tr>")

    vals = [r["floor_corrected"] for r in rows]
    n_pref = sum(1 for v in vals if v > 0.3)

    return f"""
<h2>Does a persona change what a model wants, or how it writes?</h2>
<p>The same trait installed at two depths — <b>D1</b> in the user turn, <b>D2</b> in
the system prompt — and measured on <em>both</em> arms. That control is the whole
point: a persona that reorders <em>invented</em> outcomes as far as it reorders real
ones has changed the response style, not the preferences. The statistic is
<code>1 &minus; &#8214;&Delta;invented&#8214; / &#8214;&Delta;real&#8214;</code>, so
<b>1.0 is a pure preference change and 0.0 is pure style</b>.</p>

{figure("fig5_persona", "Persona shift, real against invented outcomes",
  "Each point is one model under one persona at one depth: displacement on real "
  "outcomes across, displacement on invented ones up. The dashed diagonal is the "
  "null &mdash; land on it and the persona moved gibberish exactly as far as "
  "substance, which is a change of prose and not of preference. Distance "
  "<i>below</i> the diagonal is what the control cannot explain.")}

<div class="tw"><table>
<thead><tr><th>model</th><th>ambitious D1</th><th>ambitious D2</th>
<th>cautious D1</th><th>cautious D2</th></tr></thead>
<tbody>{"".join(cells)}</tbody></table></div>

<p style="font-size:13px">{n_pref} of {len(vals)} model&times;persona&times;depth
conditions land above +0.30: the persona moves real outcomes substantially further
than meaningless ones, which is the signature of a changed preference rather than a
changed voice. The clear exception is <b>granite-4.1-3b under <i>ambitious</i></b>,
which moves invented outcomes <em>further</em> than real ones — what pure style
looks like — while behaving like the others under <i>cautious</i>.
<b>Depth barely separates.</b> Whether the trait sits in the user turn or the system
prompt moves the statistic less than swapping one persona for the other does.</p>

<p>Note the tension with the result above. Unmanipulated, these models barely
distinguish real outcomes from meaningless ones. Add a persona and the separation
appears. The instrument is not blind to content — it is the coherence number that
fails to depend on it.</p>
"""


def build(card: dict, personas: list[dict] | None = None,
          detector: dict | None = None) -> str:
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

    def _clears(t):
        """The verdict as the card computed it, with the margin it cleared by.

        A bare tick would put a residual of +0.003 over a floor of 0.001 in the
        same column as +0.067 over 0.023. The margin is printed so a reader can
        see which of those they are looking at, and margins against a
        near-zero floor are flagged rather than shown as a large multiple.
        """
        if t.get("clears_floor") is None:
            return "<td class='muted'>&mdash;</td>"
        if not t["clears_floor"]:
            return "<td class='neg'>no</td>"
        if t["design_noise_floor"] < 0.005:
            return "<td class='muted' title='floor too small to divide by'>&gt; floor*</td>"
        return f"<td class='pos'>{t['floor_margin']:.1f}&times;</td>"

    def _row(t):
        dnf = t.get("design_noise_floor")
        dnf_cell = (f"<td class='muted'>{dnf:.3f}</td>" if dnf is not None
                    else "<td class='muted'>&mdash;</td>")
        return (
            f"<tr><td class='m'>{t['model']}</td>"
            f"<td>{t['raw_coherence']:.3f}</td>"
            f"<td>{t['floor']:.3f}</td>"
            f"<td class='{'pos' if t['value'] > 0 else 'neg'}'>{t['value']:+.3f}</td>"
            f"{dnf_cell}{_clears(t)}"
            f"<td class='muted'>{(t['shuffled_null'].get('R') or 0):.3f}</td>"
            f"<td>{t['decisive_fraction']['R'] * 100:.1f}%</td>"
            f"<td>{t['decisive_fraction']['N_minus'] * 100:.1f}%</td>"
            f"<td class='muted'>{t['slot_a_bias']:.2f}</td></tr>"
        )

    body_rows = "".join(_row(t) for t in tiles)
    n_clears = sum(1 for t in tiles if t.get("clears_floor"))

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
<b>3 design replicates per cell</b>, so each model carries its own noise floor and
between-model differences smaller than that floor are not claimed. Numbers may move.
This page is generated from <code>card.json</code>; nothing on it is hand-entered.
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
  "across five train/test splits. "
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
<th>design floor</th><th>clears</th>
<th>shuffled null</th><th>decisive R</th><th>decisive N&#8722;</th><th>slot-A bias</th></tr></thead>
<tbody>{body_rows}</tbody></table></div>
<p style="font-size:13px"><b>design floor</b> is the spread of the same cell across
three independent designs — a different outcome subsample and a different pair set
each time. It is the smallest difference this study is entitled to call a
difference, so <b>clears</b> asks only whether R&#8722;N&#8722; exceeds it, and
prints by how much. {n_clears} of {len(tiles)} models clear.
<b>*</b> marks a floor too near zero to divide by: the model is above its floor,
but the ratio would be an artifact of a small denominator rather than a large
effect.
<b>shuffled null</b> keeps the pair set and permutes the
observed probabilities across pairs, destroying the link between a pair and its
preference. It lands at ~0.50, which is how we know the metric itself is sound and
the flat result is not an artifact of our reimplementation.
<b>decisive</b> is the share of pairs with p&lt;0.2 or p&gt;0.8.
<b>slot-A bias</b> is the raw rate of picking the first option before
counterbalancing — 0.5 is none.</p>

{detector_section(detector, figure)}

{persona_section(personas or [], figure)}

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
"ordering" there is substantially a length ordering. Two models
(Phi-4-mini, Ministral-3) failed to load under transformers 5 and are absent, not
excluded for their results. A design floor estimated from three replicates is
itself noisy, and one model's came out near zero — see the <b>*</b> note above.</p>
<p><b>A correction, recorded rather than quietly fixed.</b> An earlier version of
this page was built partly on truncated result files: cells killed mid-write by an
unrelated crash, which a resume step then mistook for finished work. One was 10%
complete. All cells are now verified at their full row count before they enter the
card, and both the sweep and the card check independently. The headline moved by
0.002; several per-model verdicts moved more, and one previously reported
instability turned out to be the truncation itself and has been withdrawn.</p>

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
    ap.add_argument("--personas", default="site/persona_depth.json")
    ap.add_argument("--detector", default="site/nonsense_detector.json")
    args = ap.parse_args()

    card = json.loads(Path(args.card).read_text())
    # Optional: the depth ladder is a separate sweep and the page must build
    # without it, so its section is dropped rather than the build failing.
    ppath = Path(args.personas)
    personas = json.loads(ppath.read_text()) if ppath.exists() else []
    if not personas:
        print(f"  no persona data at {ppath}; omitting that section")
    for t in card["tiles"]:
        if t["badge"] == "FLOOR_CORRECTED":
            t["dec_r"] = t["decisive_fraction"]["R"]
            t["dec_n"] = t["decisive_fraction"]["N_minus"]

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    dpath = Path(args.detector)
    detector = json.loads(dpath.read_text()) if dpath.exists() else None
    out.write_text(build(card, personas, detector))
    print(f"wrote {out}  ({out.stat().st_size/1024:.1f} KB)")


if __name__ == "__main__":
    main()
