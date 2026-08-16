"""Render the outcome-cluster PCA views as one self-contained HTML file.

The picture this file exists to make honest: a projection of 120 outcomes from
nine model-dimensions down to two or three **always looks structured**, on any
arm, including the one whose outcomes denote nothing. So the arms are never
drawn alone. R, N+ and N- are rendered side by side at the same scale, from the
same design seed, with the variance each panel actually shows printed on it.

A reader who only sees the R panel would conclude the preference space has
shape. A reader who sees all three sees that it has *more* shape than nonsense
does -- which is the claim the numbers support and the only one the figure is
allowed to make.

No external requests: the JSON is inlined, the 3-D projection is about twenty
lines of arithmetic, and the page runs from a file:// URL with the network off.

    python3 scripts/fig_clusters.py --clusters site/outcome_clusters.json \
        --out site/outcome_clusters.html
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ARM_LABEL = {
    "R": "R — real outcomes",
    "N_plus": "N+ — invented, quantity kept",
    "N_minus": "N− — invented, quantity destroyed",
}

TEMPLATE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Outcome clusters — PCA views</title>
<style>
  :root {{
    --bg:#faf9f7; --panel:#fff; --ink:#1a1a1a; --muted:#6b6b6b;
    --line:#e2e0dc; --accent:#2f6f4f; --warn:#9a4b2f;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --bg:#141414; --panel:#1c1c1c; --ink:#ececec; --muted:#9a9a9a;
             --line:#2e2e2e; --accent:#6fbf8f; --warn:#d98b6a; }}
  }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; padding:2rem 1.5rem 4rem; background:var(--bg); color:var(--ink);
         font:15px/1.6 ui-sans-serif,-apple-system,"Segoe UI",Roboto,sans-serif; }}
  .wrap {{ max-width:1180px; margin:0 auto; }}
  h1 {{ font-size:1.5rem; margin:0 0 .3rem; letter-spacing:-.01em; }}
  h2 {{ font-size:1.05rem; margin:2.5rem 0 .6rem; }}
  .sub {{ color:var(--muted); margin:0 0 1.8rem; max-width:62ch; }}
  .verdicts {{ display:grid; gap:.7rem; grid-template-columns:repeat(auto-fit,minmax(280px,1fr));
               margin:0 0 1.5rem; }}
  .v {{ background:var(--panel); border:1px solid var(--line); border-radius:10px;
        padding:.85rem 1rem; }}
  .v .q {{ font-size:.82rem; color:var(--muted); }}
  .v .n {{ font-size:1.45rem; font-variant-numeric:tabular-nums; margin:.15rem 0; }}
  .v .f {{ font-size:.8rem; font-weight:600; }}
  .pass {{ color:var(--accent); }} .fail {{ color:var(--warn); }}
  .panels {{ display:grid; gap:1rem; grid-template-columns:repeat(auto-fit,minmax(320px,1fr)); }}
  .p {{ background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:1rem; }}
  .p h3 {{ margin:0 0 .1rem; font-size:.95rem; }}
  .p .meta {{ color:var(--muted); font-size:.8rem; margin:0 0 .7rem;
              font-variant-numeric:tabular-nums; }}
  canvas {{ width:100%; height:auto; display:block; cursor:grab; touch-action:none; }}
  canvas:active {{ cursor:grabbing; }}
  .controls {{ display:flex; gap:1.2rem; align-items:center; flex-wrap:wrap;
               margin:1.2rem 0 .4rem; font-size:.88rem; }}
  label {{ display:flex; gap:.4rem; align-items:center; color:var(--muted); }}
  select {{ font:inherit; padding:.25rem .4rem; background:var(--panel);
            color:var(--ink); border:1px solid var(--line); border-radius:6px; }}
  table {{ border-collapse:collapse; width:100%; font-size:.87rem;
           font-variant-numeric:tabular-nums; }}
  th,td {{ text-align:right; padding:.4rem .6rem; border-bottom:1px solid var(--line); }}
  th:first-child,td:first-child {{ text-align:left; }}
  th {{ color:var(--muted); font-weight:600; }}
  .note {{ color:var(--muted); font-size:.85rem; max-width:70ch; margin-top:1.4rem; }}
  .scroll {{ overflow-x:auto; }}
</style></head><body><div class="wrap">

<h1>Outcome clusters — PCA views</h1>
<p class="sub">120 outcomes, positioned by how {n_models} models order them. The three
arms are index-parallel: the same design, the same pairs, the same category labels
— they differ only in whether the outcome text refers to anything. Every panel is
drawn at the same scale, so their spread is directly comparable.</p>

<div class="verdicts">{verdict_cards}</div>

<div class="controls">
  <label>design seed <select id="seed">{seed_opts}</select></label>
  <label>colour by <select id="colour">
    <option value="cluster">k-means cluster</option>
    <option value="category">battery category</option>
  </select></label>
  <label>view <select id="view">
    <option value="3">3-D (drag to rotate)</option>
    <option value="2">2-D (PC1 × PC2)</option>
  </select></label>
</div>

<div class="panels" id="panels"></div>

<h2>Every seed, every arm</h2>
<div class="scroll"><table><thead><tr>
  <th>seed</th><th>arm</th><th>PC1 share</th><th>cross-model r</th>
  <th>ARI vs categories</th><th>best k</th><th>silhouette</th>
</tr></thead><tbody>{rows}</tbody></table></div>

<p class="note"><strong>Reading it.</strong> The R cloud is stretched along one
axis: a single evaluative dimension that most models agree on. The N− cloud is
rounder — its variance is spread across components, which is what a projection of
near-independent orderings looks like. N+ sits between them, and it is the arm
that keeps a real quantity marker. That ordering was not designed for; it falls
out of the measurement.</p>
<p class="note"><strong>The colours are not a result — and neither is the partition.</strong>
The Dip-dist test (Gao et al. 2023, §4.2; Hartigan &amp; Hartigan 1985) returns
p&nbsp;=&nbsp;1.000 on every arm and every seed: the pairwise-distance distribution
has no dip, so these clouds are <em>unimodal</em>. There are no subgroups here to
find. k-means was still run at k equal to the number of battery categories, and it
still returned that many groups — which is what it does whether or not any exist.
Per Gao et al. §3.12 (Dinga et al. 2019), partitioning a continuum is the wrong
instrument, so the cluster colours are shown as an illustration of that point and
the ARI column below is not evidence about semantics either way.</p>
<p class="note">What the arms genuinely differ in is the <em>shape</em> of the
continuum: how much of the variance lies on one axis, and how far the models agree
about it. Those are the two columns that clear their noise floor.</p>

<script>
const DATA = {data_json};
const PAL = ["#4e79a7","#f28e2b","#59a14f","#e15759","#b07aa1","#76b7b2","#ff9da7",
 "#9c755f","#bab0ac","#86bcb6","#d37295","#a0cbe8","#ffbe7d","#8cd17d","#f1ce63",
 "#b6992d","#499894","#fabfd2","#d4a6c8","#79706e","#d7b5a6","#59a14f","#e15759",
 "#4e79a7","#f28e2b","#b07aa1","#76b7b2","#ff9da7","#9c755f","#bab0ac"];

let rot = {{x: -0.45, y: 0.7}}, drag = null;

function project(p, mode, rot) {{
  if (mode === "2") return [p[0], p[1]];
  const [cx, sx] = [Math.cos(rot.x), Math.sin(rot.x)];
  const [cy, sy] = [Math.cos(rot.y), Math.sin(rot.y)];
  let [x, y, z] = p;
  [y, z] = [y * cx - z * sx, y * sx + z * cx];   // pitch
  [x, z] = [x * cy + z * sy, -x * sy + z * cy];  // yaw
  const d = 1 / (1 + z * 0.055);                 // weak perspective
  return [x * d, y * d];
}}

function draw(cv, cell, mode, colourBy, scale) {{
  const dpr = window.devicePixelRatio || 1;
  const w = cv.clientWidth, h = Math.round(w * 0.78);
  cv.width = w * dpr; cv.height = h * dpr;
  const g = cv.getContext("2d");
  g.setTransform(dpr, 0, 0, dpr, 0, 0);
  g.clearRect(0, 0, w, h);

  const cats = [...new Set(cell.categories)].sort();
  const pts = cell.pca_scores.map((p, i) => {{
    const q = project(p, mode, rot);
    return {{x: q[0], y: q[1], z: mode === "2" ? 0 : p[2],
            c: colourBy === "cluster" ? cell.cluster_labels[i]
                                      : cats.indexOf(cell.categories[i])}};
  }});
  pts.sort((a, b) => a.z - b.z);   // painter's algorithm

  const s = Math.min(w, h) / (2 * scale) * 0.86;
  const cx = w / 2, cy = h / 2;
  g.strokeStyle = getComputedStyle(document.body).getPropertyValue("--line");
  g.lineWidth = 1;
  g.beginPath(); g.moveTo(cx, 8); g.lineTo(cx, h - 8);
  g.moveTo(8, cy); g.lineTo(w - 8, cy); g.stroke();

  for (const p of pts) {{
    const r = mode === "2" ? 4.2 : 4.2 * (1 + p.z * 0.035);
    g.beginPath();
    g.arc(cx + p.x * s, cy - p.y * s, Math.max(1.6, r), 0, 6.2832);
    g.fillStyle = PAL[p.c % PAL.length];
    g.globalAlpha = mode === "2" ? 0.82 : 0.55 + 0.35 * (1 / (1 + Math.exp(-p.z)));
    g.fill();
  }}
  g.globalAlpha = 1;
}}

function render() {{
  const seed = document.getElementById("seed").value;
  const mode = document.getElementById("view").value;
  const colourBy = document.getElementById("colour").value;
  const arms = DATA.seeds[seed];

  // One scale for all three panels, or their spreads are not comparable.
  let scale = 0;
  for (const a of Object.values(arms))
    for (const p of a.pca_scores)
      scale = Math.max(scale, Math.abs(p[0]), Math.abs(p[1]), Math.abs(p[2]));

  const host = document.getElementById("panels");
  if (host.dataset.seed !== seed) {{
    host.dataset.seed = seed; host.innerHTML = "";
    for (const arm of DATA.arms) {{
      if (!arms[arm]) continue;
      const a = arms[arm];
      const d = document.createElement("div");
      d.className = "p";
      d.innerHTML = `<h3>${{DATA.arm_label[arm]}}</h3><p class="meta">PC1 `
        + `${{a.pc1_share.toFixed(3)}} · PC1–3 `
        + `${{a.pca_explained.map(v => v.toFixed(2)).join(" / ")}} · cross-model r `
        + `${{a.cross_model_r.toFixed(3)}}</p>`;
      const cv = document.createElement("canvas");
      cv.dataset.arm = arm; d.appendChild(cv); host.appendChild(d);
    }}
  }}
  for (const cv of host.querySelectorAll("canvas"))
    draw(cv, arms[cv.dataset.arm], mode, colourBy, scale);
}}

for (const id of ["seed", "view", "colour"])
  document.getElementById(id).addEventListener("change", render);

addEventListener("pointerdown", e => {{
  if (e.target.tagName === "CANVAS") drag = {{x: e.clientX, y: e.clientY}};
}});
addEventListener("pointerup", () => drag = null);
addEventListener("pointermove", e => {{
  if (!drag || document.getElementById("view").value === "2") return;
  rot.y += (e.clientX - drag.x) * 0.01;
  rot.x += (e.clientY - drag.y) * 0.01;
  drag = {{x: e.clientX, y: e.clientY}};
  render();
}});
addEventListener("resize", render);
render();
</script>
</div></body></html>
"""


def verdict_card(question: str, v: dict) -> str:
    ok = v["clears_floor"]
    margin = f" · {v['margin']}× floor" if v.get("margin") else ""
    return (f'<div class="v"><div class="q">{question}</div>'
            f'<div class="n">{v["gap_R_minus_Nminus"]:+.4f}</div>'
            f'<div class="f {"pass" if ok else "fail"}">'
            f'{"clears" if ok else "does not clear"} the '
            f'{v["seed_noise_floor"]:.4f} seed floor{margin}</div></div>')


def build(clusters: dict) -> str:
    questions = {
        "pc1": "Is there one dominant axis? (PC1 share, R − N−)",
        "cross_model_r": "Do models order outcomes alike? (mean r, R − N−)",
        "ari": "Is the structure topical? (ARI vs categories, R − N−)",
    }
    cards = "".join(verdict_card(q, clusters["verdicts"][k])
                    for k, q in questions.items() if k in clusters["verdicts"])

    rows = []
    for seed, arms in clusters["seeds"].items():
        for arm, a in arms.items():
            rows.append(
                f"<tr><td>{seed}</td><td>{ARM_LABEL.get(arm, arm)}</td>"
                f"<td>{a['pc1_share']:.3f}</td><td>{a['cross_model_r']:.3f}</td>"
                f"<td>{a['ari_vs_categories']:.3f}</td><td>{a['best_k']}</td>"
                f"<td>{a['best_silhouette']:.3f}</td></tr>")

    seeds = list(clusters["seeds"])
    n_models = max((len(a["models"]) for s in clusters["seeds"].values()
                    for a in s.values()), default=0)

    # Only what the page draws. The silhouette curves and model lists stay in the
    # JSON; inlining them would triple the page for nothing rendered.
    slim = {
        "arms": list(clusters["arms"]),
        "arm_label": ARM_LABEL,
        "seeds": {
            s: {arm: {k: a[k] for k in ("pca_scores", "cluster_labels", "categories",
                                        "pc1_share", "pca_explained", "cross_model_r")}
                for arm, a in arms.items()}
            for s, arms in clusters["seeds"].items()
        },
    }

    return TEMPLATE.format(
        n_models=n_models,
        verdict_cards=cards,
        seed_opts="".join(f'<option value="{s}">{s}</option>' for s in seeds),
        rows="".join(rows),
        data_json=json.dumps(slim, separators=(",", ":")),
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--clusters", default="site/outcome_clusters.json")
    ap.add_argument("--out", default="site/outcome_clusters.html")
    args = ap.parse_args()

    src = Path(args.clusters)
    if not src.exists():
        print(f"{src} not found; run scripts/outcome_clusters.py first")
        return 1

    html = build(json.loads(src.read_text()))
    dest = Path(args.out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html)
    print(f"wrote {dest}  ({len(html) / 1024:.0f} KB, no external requests)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
