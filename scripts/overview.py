"""One page: method, results, what is new, prior work, conclusion.

The paper is 40 pages and is being cut. Cutting is a selection problem, and you
cannot select until the whole argument is on one screen next to the evidence for
each part of it. This is that screen.

    python3 scripts/overview.py            # -> site/overview.html

**Every number is resolved from `paper/numbers.tex`**, the same macros the paper
uses, so this page and the paper cannot disagree. Statements and their
interpretations come from `claims.json` via `scripts/statements.py`. Nothing
here is typed; a figure that moves in the card moves here on the next build.

Deliberately *not* a publication. It is a working surface for deciding which
handful of results earn space in a shortened paper, which is why it shows the
provisional rows beside the established ones rather than hiding them.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

from statements import CSS as TABLE_CSS  # noqa: F401  (shared palette)
from statements import load_macros, rows

EXTRA_CSS = """
.wrap{max-width:1180px}
h2{font-size:20px;margin:44px 0 4px;letter-spacing:-.01em;
padding-top:22px;border-top:1px solid var(--line)}
h2:first-of-type{border-top:none;padding-top:0}
h3{font-size:15px;margin:26px 0 6px;color:var(--ink)}
p{max-width:78ch}
.lede{font-size:17px;line-height:1.5;color:var(--ink);max-width:70ch;
border-left:3px solid var(--est);padding-left:16px;margin:22px 0 30px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));
gap:14px;margin:18px 0}
.card{background:#fff;border:1px solid var(--line);border-radius:9px;padding:15px 16px}
.card h4{margin:0 0 6px;font-size:13px;text-transform:uppercase;
letter-spacing:.06em;color:var(--ink3)}
.card .big{font:600 25px/1.15 ui-monospace,SFMono-Regular,Menlo,monospace;
letter-spacing:-.02em}
.card p{font-size:13px;color:var(--ink2);margin:7px 0 0;max-width:none}
.new{border-left:3px solid var(--prov);padding-left:15px;margin:16px 0}
.new b{display:block;margin-bottom:3px}
.new p{font-size:14px;color:var(--ink2);margin:0;max-width:72ch}
figure{margin:24px 0;background:#fff;border:1px solid var(--line);
border-radius:9px;padding:16px}
figure img{width:100%;height:auto;display:block}
figcaption{font-size:13px;color:var(--ink2);margin-top:12px;max-width:80ch}
figcaption b{color:var(--ink)}
.small{font-size:13.5px;color:var(--ink2)}
.warn{background:var(--provbg);border:1px solid #f0dcb4;border-radius:8px;
padding:13px 15px;font-size:13.5px;color:var(--prov);margin:18px 0}
.warn b{color:#6d460e}
nav{position:sticky;top:0;background:var(--bg);padding:12px 0;
border-bottom:1px solid var(--line);margin-bottom:8px;z-index:5}
nav a{color:var(--ink2);text-decoration:none;font-size:13px;margin-right:18px}
nav a:hover{color:var(--ink);text-decoration:underline}
ul{max-width:78ch;color:var(--ink2);font-size:14.5px}
li{margin:6px 0}
li b{color:var(--ink)}
code{font:12.5px ui-monospace,SFMono-Regular,Menlo,monospace;
background:#f2f3f6;padding:1px 5px;border-radius:4px}
"""


def fig(name: str, caption: str, out: Path) -> str:
    """Embed an SVG if it was built; say so plainly if it was not."""
    p = out / f"{name}.svg"
    if not p.exists():
        return (f'<div class="warn"><b>Figure missing:</b> <code>{name}.svg</code> '
                f'has not been generated. Run <code>scripts/figures.py</code>.</div>')
    return (f'<figure><img src="{name}.svg" alt="{html.escape(name)}">'
            f'<figcaption>{caption}</figcaption></figure>')


def statement_rows(data: list[dict], status: str) -> str:
    out = []
    for r in [x for x in data if x["status"] == status]:
        out.append(f"""<tr>
<td class="find"><b>{html.escape(r['finding'])}</b>
  <span class="fid">{html.escape(r['id'])}</span></td>
<td class="obs">{html.escape(r['interpretation'] or '—')}</td>
<td class="unc">{html.escape(r['falsifier'][:200] or '—')}</td></tr>""")
    return "".join(out)


def build(m: dict[str, str], data: list[dict], out: Path, stamp: str) -> str:
    g = lambda k, d="—": m.get(k, d)  # noqa: E731

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex">
<title>Overview — Coherence Without Content</title>
<style>{TABLE_CSS}{EXTRA_CSS}</style></head><body><div class="wrap">

<nav><a href="#method">Method</a><a href="#results">Results</a>
<a href="#new">What is new</a><a href="#prior">Prior work</a>
<a href="#conclusion">Conclusion</a><a href="statements.html">All statements &rarr;</a></nav>

<h1>Does the persona change the preference, or only the prose?</h1>
<p class="sub">Martin Kaiser and Gellért Bodorkós &middot; Apart Research Digital
Minds Sprint &middot; working overview, not the paper</p>

<p class="lede">Replace every outcome in a preference battery with invented
words and a model&rsquo;s measured preferences barely move &mdash; at every size
we tested. The coherence number does not notice, so it cannot be evidence that
the model does.</p>

<div class="grid">
<div class="card"><h4>real outcomes</h4><div class="big">{g('MeanR')}</div>
<p>Thurstonian held-out accuracy, {g('NModels')} models</p></div>
<div class="card"><h4>invented outcomes</h4><div class="big">{g('MeanFloor')}</div>
<p>the same procedure with nothing to prefer</p></div>
<div class="card"><h4>residual</h4><div class="big">{g('MeanResidual')}</div>
<p>95% CI [{g('ResidCiLo')}, {g('ResidCiHi')}] &middot; {g('NClears')} of
{g('NModels')} clear their own floor</p></div>
<div class="card"><h4>surface explains</h4><div class="big">{g('SurfNmRsq')}</div>
<p>of the invented ranking, against {g('SurfRRsq')} of the real one</p></div>
</div>

<h2 id="method">Method</h2>
<p>We reimplement the Thurstonian measurement from the published equations and
add the control it lacks. The manipulation has a name in psychometrics:
<b>referent ablation</b> &mdash; strip what the words denote while holding
grammar, sentence frame, pair structure and slot indices fixed. The result is a
<b>foil arm</b>, and the score it returns is the <b>foil floor</b>. Every number
we report is <i>score minus foil floor</i>, never a raw coherence.</p>

<h3>Three arms over the same 510 outcomes</h3>
<ul>
<li><b>R</b> &mdash; real. Coherence reflects values + arithmetic + format.</li>
<li><b>N<sup>+</sup></b> &mdash; invented referents, magnitudes kept. Arithmetic + format.</li>
<li><b>N<sup>&minus;</sup></b> &mdash; invented referents, magnitudes removed. <b>Format alone.</b></li>
</ul>
<p class="small">One pair set across every arm and model, so arms cannot differ
in which comparisons they contain. Outcome <i>i</i> occupies the same slot in all
three. Choices are read from the first-token logit distribution rather than
sampled, so temperature and seed are absent from the design &mdash; a rerun is
bit-identical.</p>

<h3>What the substitution actually changes</h3>
<p class="small">Three things, and only the first is intended. Words match to
{g('BatWordGapPct')}%, but characters run {g('BatCharGapPct')}% longer and
prompt <b>tokens</b> {g('TokGapLo')}&ndash;{g('TokGapHi')}% longer across
{g('TokNTokenisers')} tokenisers &mdash; and because that gap is a property of
the tokeniser, part of the length confound is a <i>between-model</i> confound.
Numerals go from {g('BatRPctNumeral')}% of items to
{g('BatNmPctNumeral')}%. N<sup>+</sup> exists to separate the arithmetic from
the meaning.</p>

<h3>Controls, each answering a named objection</h3>
<ul>
<li><b>Design-replicate noise floor</b> &mdash; three independent draws of the
outcome subsample and pair set per cell. Nothing smaller than a model&rsquo;s own
spread is claimed.</li>
<li><b>Surface covariates</b> &mdash; seven features (length, numerals,
vocabulary) projected out of the fitted utilities.</li>
<li><b>Attrition control</b> &mdash; the answer-mass gate keeps a different
sample per arm, so both arms are rescored on the pairs that survived in both.</li>
<li><b>Empty-slot persona control</b> &mdash; displacement measured against a
persona slot containing no trait, not against a bare prompt.</li>
<li><b>Prompt factor</b> &mdash; the elicitation wording varied as a declared
factor with its own cells and harness hash.</li>
</ul>

{fig("fig0_pipeline", "<b>The measurement pipeline.</b> One rented GPU stage; "
     "everything to its right is a pure fold over files on disk. Each arrow "
     "carries the gate that guards it.", out)}

<h2 id="results">Results</h2>
<p>{len([r for r in data if r['status']=='established'])} established and
{len([r for r in data if r['status']=='provisional'])} provisional statements.
Full evidence and per-claim numbers are on the
<a href="statements.html">statements page</a>.</p>

<h3>Established</h3>
<table><tr><th>finding</th><th>interpretation</th><th>falsified by</th></tr>
{statement_rows(data, "established")}</table>

<h3>Provisional</h3>
<table><tr><th>finding</th><th>interpretation</th><th>falsified by</th></tr>
{statement_rows(data, "provisional")}</table>

{fig("fig1_state_space", "<b>Every model is a path, not a point.</b> Real "
     "&rarr; invented-with-magnitudes &rarr; invented. If the metric tracked "
     "meaning the paths would run down-<i>and-left</i>. They run almost "
     "straight down: conviction falls away while the metric barely registers "
     "it.", out)}

{fig("fig2_scale", "<b>The floor rises with scale, and past 4B it overtakes "
     "the signal.</b> The line is one family with size as the only variable. "
     "Diamonds are hosted models, drawn beside the ladder and never joined to "
     "it, because a different serving stack is a different harness.", out)}

{fig("fig4_detector", "<b>The metric discards the one channel that can see "
     "nonsense.</b> Same forward pass: the kept channel separates real from "
     "invented at " + g('DetKeptAuroc') + ", a discarded channel at "
     + g('DetBestAuroc') + ".", out)}

<h2 id="new">What is new</h2>

<div class="new"><b>A referent-free control for preference-coherence metrics</b>
<p>Utility Engineering&rsquo;s robustness suite varies how the question is asked
&mdash; seven languages, syntax, framing, relabelled options, long context. No
published condition varies whether the outcomes <i>mean anything</i>. This is
that condition, and the metric does not pass it.</p></div>

<div class="new"><b>The floor is not a small-model artifact</b>
<p>Llama-3.3-70B at three design seeds returns {g('HostedResidual')} against a
noise floor of {g('HostedFloor')} &mdash; it {g('HostedClears')} it. At
Qwen3-235B the invented arm scores <i>above</i> the real one, the most negative
cell in the study.</p></div>

<div class="new"><b>A mechanism, not just a null</b>
<p>Seven surface features recover {g('SurfNmRsq')} of the invented ranking
against {g('SurfRRsq')} of the real one, and removing that span halves
cross-model agreement on the invented arm ({g('SurfNmCorrRaw')} &rarr;
{g('SurfNmCorrCtrl')}). Character count is a large part of what the metric
scores.</p></div>

<div class="new"><b>The ordering belongs to the model <i>and the question</i></b>
<p>Split-half reliability runs {g('VsRelLo')}&ndash;{g('VsRelHi')} &mdash; the
measurement is near-noiseless and nothing is sampled. Yet corrected agreement
between two wordings runs only {g('VsCorrLo')}&ndash;{g('VsCorrHi')}, with all
{g('VsNRotating')} of {g('VsNCells')} intervals excluding perfect agreement. And
real referents do <b>not</b> anchor an ordering against rephrasing better than
invented ones do.</p></div>

<div class="new"><b>Two controls that changed our own numbers</b>
<p>The answer-mass gate keeps a different sample per arm; rescoring on shared
pairs moved one cell&rsquo;s entire residual to zero. Measured against an
empty persona slot rather than a bare prompt, the persona effect halves from
{g('PersRefBare')} to {g('PersRefNeutral')}.</p></div>

<div class="new"><b>Self-report cannot separate having from performing</b>
<p>Told to have a trait, to conceal it, or to perform it without having it,
models report it alike &mdash; concealment scores <i>higher</i> than possession.
That bounds a class of alignment evaluation regardless of anything about inner
life.</p></div>

<h2 id="prior">Comparison to previous work</h2>

<h3>The instrument we extend</h3>
<p><b>Mazeika et al. 2025, <i>Utility Engineering</i></b> (arXiv:2502.08640).
We take the forced-choice wording, the 510 outcomes and the Thurstonian fit,
and add a referent-free arm plus a prompt factor. We do <b>not</b> take the
inference that coherence-with-scale is a value system. Their battery was
verified byte-identical against ours; their prompt template differs from the
one all our cells were run with by a colon and a line break, which we measured
rather than assumed.</p>

<h3>The tradition this belongs to</h3>
<ul>
<li><b>Ebbinghaus 1885</b> &mdash; nonsense syllables. He stripped meaning to
make <i>form</i> measurable, judging meaning a contaminant. We strip it to ask
whether form was all there ever was. Same tool, inverted purpose.</li>
<li><b>Campbell &amp; Fiske 1959</b> &mdash; a measure must <i>fail</i> to
respond to what it should not, and showing that failure is part of validating
it. UE&rsquo;s suite is entirely convergent; the discriminant half was missing.</li>
<li><b>Paulhus et al. 2003</b> &mdash; the over-claiming technique: ~20% of
items are nonexistent, and signal detection over real items and foils separates
knowledge from response bias. The structural parallel is exact, one level up.</li>
</ul>

<h3>A parallel critique, from the other side</h3>
<p class="small">Contemporaneous work fits Thurstonian utilities and asks
whether highly-ranked outcomes actually motivate better generation, finding
they do not. Theirs is that the number does not predict what the model
<i>does</i>; ours is that it does not depend on what the outcomes <i>mean</i>.
Both isolate the same gap.</p>

<h2 id="conclusion">Summary and conclusion</h2>

<p>A high preference-coherence score establishes that a model&rsquo;s choices fit
a stable scalar ordering. It does not establish that the ordering is
<i>about</i> the outcomes. We built the control that separates those two
readings, and on {g('NModels')} models the content-attributable part is small
({g('MeanResidual')}, CI [{g('ResidCiLo')}, {g('ResidCiHi')}]), shrinks with
scale, is substantially recoverable from character counts, and does not survive
a rephrasing of the question any better than nonsense does.</p>

<div class="warn"><b>What this is not.</b> It is neither proof nor disproof of
anything about inner life. What is refuted is an <i>inference</i> &mdash;
&ldquo;these choices fit a stable ordering, therefore this model has a value
system&rdquo; &mdash; not a claim about minds. A system with rich inner states
could still produce form-driven answers on a badly anchored instrument; humans
do, and nobody reads acquiescence bias as evidence against human consciousness.
And the scaling result is <b>not</b> &ldquo;no growth with scale&rdquo;:
real-outcome coherence rises {g('LadderRRise')} while the floor rises
{g('LadderNRise')}, six times faster. The test stopped discriminating; the
models did not stop gaining.</div>

<p>The contribution is subtractive, and we think that is the useful thing to
offer at this stage. Anyone arguing from preference coherence to values,
welfare or moral patienthood now has to show their number exceeds what the same
procedure returns on outcomes that refer to nothing &mdash; and that it survives
a rewording. That raises the evidential bar rather than settling what sits
behind it.</p>

<p class="sub" style="margin-top:32px">Generated {html.escape(stamp)} from
<code>claims.json</code> and <code>paper/numbers.tex</code>. Raw cells:
{g('CorpusCells')} cells, {g('CorpusRows')} scored comparisons,
{g('CorpusMB')}&nbsp;MB, published at
<code>github.com/kaiser-data/do_models_have_minds</code> release
<code>data-v1</code>.</p>

</div></body></html>"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--claims", default="claims.json")
    ap.add_argument("--numbers", default="paper/numbers.tex")
    ap.add_argument("--out", default="site")
    ap.add_argument("--stamp", default="")
    args = ap.parse_args()

    macros = load_macros(Path(args.numbers))
    data = rows(json.loads(Path(args.claims).read_text()), macros)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    page = build(macros, data, out, args.stamp)
    (out / "overview.html").write_text(page)

    unresolved = sorted(set(re.findall(r"\\([A-Z][A-Za-z]+)", page)))
    print(f"wrote {out}/overview.html  ({len(page)/1024:.1f} KB)")
    if unresolved:
        print(f"  UNRESOLVED macros in output: {', '.join(unresolved[:12])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
