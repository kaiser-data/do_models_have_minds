"""Figure: the experimental pipeline, from GPU to paper.

The one diagram in this project that is not a result. It exists because the
method is easy to describe and hard to picture: a rented GPU produces append-only
rows, every number after that is a pure fold over those rows, and the paper and
the site are two renderings of the same card. A reader who sees that shape can
tell which parts of the pipeline could possibly disagree with each other, which
is the property the whole repo is built to have.

Generated rather than drawn so it cannot drift: the model count, cell count and
battery hash are read from card.json, and the gate labels from the code that
enforces them.

    python3 scripts/fig_pipeline.py   # -> site/fig0_pipeline.svg (+ dark)
    python3 scripts/fig_pipeline.py --format pdf --themes light --out paper/figs
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

THEMES = {
    "light": {"fg": "#111110", "mid": "#55534e", "faint": "#d9d7d0",
              "box": "#ffffff", "band": "#f2f1ec", "gate": "#b4453a",
              "ok": "#3f8f3a"},
    "dark": {"fg": "#f4f3ef", "mid": "#bab8ae", "faint": "#3a3934",
             "box": "#1f1e1c", "band": "#242320", "gate": "#d1685c",
             "ok": "#5aa855"},
}

# Left to right: rent, run, freeze, fold, render. The three gates are drawn on
# the edges they actually guard rather than listed underneath, because the point
# of the picture is WHERE a bad cell gets stopped.
STAGES = [
    ("Modal\nGPU sweep", "L4 / A10G · one cell\nper model × arm × design",
     "modal_app/sweep.py"),
    ("results/\nappend-only", "one .jsonl per cell\nnever mutated",
     "153 files, SHA-pinned"),
    ("card.json", "the only analysed\nartifact",
     "scripts/build_card.py"),
    ("paper + site", "two renderings,\none source",
     "paper_numbers.py / build_site.py"),
]

GATES = [
    ("CPU gate\n+ ETA", 0),          # before the sweep spends money
    ("row count\n+ mass gate", 1),  # before a cell enters the card
    ("ledger\n+ lint", 2),     # before a number reaches prose
]


def figure(card: dict, theme: str = "light", rendered: dict | None = None):
    th = THEMES[theme]
    fig, ax = plt.subplots(figsize=(11.6, 3.9))
    ax.set_xlim(0, 106)
    ax.set_ylim(0, 26)
    ax.axis("off")

    n_models = len([t for t in card["tiles"] if t["badge"] == "FLOOR_CORRECTED"])
    n_cells = len(card["cells"])
    sha = card["tiles"][0]["battery_sha256"][:12]

    facts = [
        f"{n_models} models x 3 arms",
        f"{n_cells} cells, {card['n_splits']} splits",
        "no GPU, no network,\nno API key from here on",
        "one number, one source",
    ]

    # 4 boxes + 3 gaps must fit inside xlim with room for the gate
    # labels, which live in the gaps and are the widest text in the figure.
    w, gap = 19.0, 8.6
    y, h = 9.2, 9.4
    centres = []
    for i, ((title, sub, tool), fact) in enumerate(zip(STAGES, facts)):
        x = 2.0 + i * (w + gap)
        centres.append(x + w / 2)
        ax.add_patch(FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.5,rounding_size=1.1",
            linewidth=1.3, edgecolor=th["faint"], facecolor=th["box"], zorder=3))
        ax.text(x + w / 2, y + h - 2.0, title, ha="center", va="top",
                fontsize=11.5, color=th["fg"], fontweight="bold",
                linespacing=1.25, zorder=4)
        ax.text(x + w / 2, y + h - 5.4, sub, ha="center", va="top",
                fontsize=8.4, color=th["mid"], linespacing=1.4, zorder=4)
        ax.text(x + w / 2, y - 1.4, tool, ha="center", va="top", fontsize=7.8,
                color=th["mid"], family="monospace", zorder=4)
        ax.text(x + w / 2, y + h + 1.4, fact, ha="center", va="bottom",
                fontsize=8, color=th["mid"], linespacing=1.35, zorder=4)

    # Arrows, and the gate that guards each transition.
    for label, i in GATES:
        x0, x1 = centres[i] + w / 2 - 0.5, centres[i + 1] - w / 2 + 0.5
        ax.add_patch(FancyArrowPatch(
            (x0, y + h / 2), (x1, y + h / 2), arrowstyle="-|>",
            mutation_scale=13, linewidth=1.4, color=th["mid"], zorder=2))
        ax.text((x0 + x1) / 2, y + h / 2 + 1.1, label, ha="center", va="bottom",
                fontsize=7.6, color=th["gate"], linespacing=1.3,
                fontweight="bold", zorder=4)

    ax.text(2.0, 23.4,
            "Everything right of the GPU is a pure fold: no network, no sampling, "
            "no model call.",
            fontsize=9.2, color=th["fg"], ha="left", va="center")
    foot = (f"battery SHA {sha}  ·  answers read from first-token logits, not "
            f"sampled (no temperature, no seed)  ·  every cell resumable")
    if rendered:
        inj = sum(1 for c in rendered.get("models", {}).values()
                  if c.get("D0", {}).get("injects_unrequested_system_text"))
        foot += (f"  ·  rendered prompts verified for "
                 f"{rendered.get('n_verified', 0)} models, {inj} receive "
                 f"template-injected system text")
    ax.text(2.0, 2.4, foot, fontsize=7.6, color=th["mid"], ha="left", va="center")

    fig.tight_layout()
    return fig


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--card", default="card.json")
    ap.add_argument("--rendered", default="site/rendered_prompts.json")
    ap.add_argument("--out", default="site")
    ap.add_argument("--format", default="svg", choices=("svg", "pdf", "png"))
    ap.add_argument("--themes", default="light,dark")
    args = ap.parse_args()

    card = json.loads(Path(args.card).read_text())
    rp = Path(args.rendered)
    rendered = json.loads(rp.read_text()) if rp.exists() else None
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for theme in [t.strip() for t in args.themes.split(",") if t.strip()]:
        sfx = "" if theme == "light" else "-dark"
        fig = figure(card, theme, rendered)
        fig.savefig(out / f"fig0_pipeline{sfx}.{args.format}",
                    format=args.format, bbox_inches="tight", transparent=True)
        plt.close(fig)
        print(f"wrote {out}/fig0_pipeline{sfx}.{args.format}")


if __name__ == "__main__":
    main()
