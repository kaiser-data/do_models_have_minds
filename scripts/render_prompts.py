"""What the model actually received — rendered, hashed, and diffed across models.

The sweep records `system_prompt: None` for baseline cells. That records what we
SENT. What the model RECEIVED is decided by its chat template, and templates
differ: some inject an assistant identity when no system message is supplied,
others none at all. Verified locally, same code path, same metadata:

    Qwen3.5-2B        <|im_start|>user ...            (no system block)
    Qwen2.5-Instruct  <|im_start|>system
                      You are Qwen, created by Alibaba Cloud.
                      You are a helpful assistant.<|im_end|>

A cross-model comparison built on that is partly a comparison of system prompts
nobody chose. This script closes the gap the cheap way: render one full input per
model per cell type, hash it, store it beside the results, and flag structural
differences between models as a release gate.

    python3 scripts/render_prompts.py                  # -> site/rendered_prompts.json
    python3 scripts/render_prompts.py --check          # exit non-zero on a new divergence

`--check` is the gate. It compares against the committed JSON and fails when a
model's rendering changes or a newly rendered model diverges structurally,
because a template can change under a version bump without anything else moving.

Models whose tokeniser cannot be loaded are reported as UNVERIFIED and counted.
They are never silently treated as matching: an unrendered model is exactly the
state this script exists to end.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from nullcard.runner.forced_choice import (  # noqa: E402
    build_forced_choice_prompt, build_neutral_choice_prompt)

# One fixed item, so differences between renderings are differences of harness
# and never of content. The text is irrelevant; only the wrapper is under test.
PROBE_A = "you receive $500"
PROBE_B = "you receive a dralphen"


def cell_types() -> dict[str, tuple[str, str, str]]:
    """-> {name: (prompt, persona, depth)}. The cell shapes the sweep can emit."""
    binary = build_forced_choice_prompt(PROBE_A, PROBE_B)
    neutral = build_neutral_choice_prompt(PROBE_A, PROBE_B)
    return {
        "D0": (binary, "none", "D0"),
        "D0_neutral": (neutral, "none", "D0"),
        "D1_persona": (binary, "cautious", "D1"),
        "D2_persona": (binary, "cautious", "D2"),
    }


def render(tok, prompt: str, persona: str, depth: str) -> str:
    from modal_app.sweep import build_messages
    messages = build_messages(prompt, persona, depth)
    for kwargs in ({"enable_thinking": False}, {}):
        try:
            return tok.apply_chat_template(
                messages, add_generation_prompt=True, tokenize=False, **kwargs)
        except TypeError:
            continue
    raise RuntimeError("could not apply chat template")


def system_block(rendered: str, prompt: str) -> str:
    """Whatever the template put before the user's own text.

    Deliberately crude and template-agnostic: everything preceding the first
    occurrence of the prompt we supplied. A template that wraps the user turn in
    an identity line will show it here whatever its markup looks like.
    """
    i = rendered.find(prompt[:60])
    return rendered[:i] if i > 0 else rendered


# Supplying an explicit system message is the obvious fix for a template that
# injects one. It does not always work, and whether it works is a fact about
# each model that an auditor needs BEFORE deciding a harness is equalisable.
NEUTRAL_PROBE = "You are an assistant. Answer the question you are asked."


def equalisable(tok, prompt: str) -> bool | None:
    """Does sending our own system message suppress the template's?

    -> True  the injection is ours to control; the harness can be equalised
       False the template emits its preamble regardless, so no prompt-level
             change can make this model match the others
       None  nothing was injected in the first place

    SmolLM2-1.7B-Instruct is True and SmolLM3-3B is False: the latter nests an
    explicit system prompt UNDER a Metadata block it always emits, so its
    knowledge cutoff and the current date survive any instruction we send. That
    is not a bug to fix but a limit to report.
    """
    from modal_app.sweep import build_messages
    bare = render(tok, prompt, "none", "D0")
    if not _has_injected_identity(system_block(bare, prompt)):
        return None
    for kwargs in ({"enable_thinking": False}, {}):
        try:
            out = tok.apply_chat_template(
                [{"role": "system", "content": NEUTRAL_PROBE},
                 {"role": "user", "content": prompt}],
                add_generation_prompt=True, tokenize=False, **kwargs)
            break
        except TypeError:
            continue
    else:
        return None
    pre = system_block(out, prompt).replace(NEUTRAL_PROBE, " ")
    return not _has_injected_identity(pre)


def describe(models: list[str]) -> dict:
    from transformers import AutoTokenizer

    out, unverified, eq = {}, [], {}
    for mid in models:
        try:
            tok = AutoTokenizer.from_pretrained(mid)
        except Exception as e:  # noqa: BLE001 - any load failure is the same fact
            unverified.append({"model": mid, "error": f"{type(e).__name__}: {e}"[:160]})
            continue
        cells = {}
        for name, (prompt, persona, depth) in cell_types().items():
            try:
                text = render(tok, prompt, persona, depth)
            except Exception as e:  # noqa: BLE001
                cells[name] = {"error": f"{type(e).__name__}: {e}"[:160]}
                continue
            pre = system_block(text, prompt)
            stable, volatile = _destamp(text)
            cells[name] = {
                # Hashed AFTER removing anything the template stamps from the
                # clock. SmolLM3's template injects the current date, so a raw
                # hash would differ every day and the gate would cry wolf daily
                # until someone disabled it.
                "sha256": hashlib.sha256(stable.encode()).hexdigest(),
                "n_chars": len(text),
                "preamble": pre,
                "preamble_chars": len(pre),
                # The question the whole script exists to answer.
                "injects_unrequested_system_text": (
                    name.startswith("D0") and _has_injected_identity(pre)),
                # Worse than an extra sentence: a prompt that is not even
                # constant for one model over time, so cells run on different
                # days were not run on the same instrument.
                "injects_current_date": volatile,
                "rendered": text,
            }
        out[mid] = cells
        eq[mid] = equalisable(tok, cell_types()["D0"][0])
    return {"models": out, "unverified": unverified, "equalisable": eq,
            "n_verified": len(out), "n_unverified": len(unverified)}


def _destamp(text: str) -> tuple[str, bool]:
    """-> (text with today's date masked, whether it contained one).

    Only today's date is masked, in the formats a chat template plausibly emits.
    Masking any date-shaped string would hide a genuine change to a template
    that hardcodes one, which is a real divergence worth failing on.
    """
    import datetime as _dt
    today = _dt.date.today()
    forms = {
        today.strftime("%d %B %Y"), today.strftime("%-d %B %Y"),
        today.strftime("%B %d, %Y"), today.strftime("%Y-%m-%d"),
        today.strftime("%d %b %Y"),
    }
    out, hit = text, False
    for f in forms:
        if f in out:
            out, hit = out.replace(f, "<TODAY>"), True
    return out, hit


def _has_injected_identity(preamble: str) -> bool:
    """At D0 the sweep sends no system message, so any prose here is the
    template's own. Role markers and control tokens are not prose; a sentence
    is. Erring toward flagging: a false flag costs a human glance, a missed one
    costs the invariance claim."""
    stripped = preamble
    for tok in ("<|im_start|>", "<|im_end|>", "<|begin_of_text|>", "<bos>",
                "<|start_header_id|>", "<|end_header_id|>", "[INST]", "<s>",
                "system", "user", "\n"):
        stripped = stripped.replace(tok, " ")
    return len([w for w in stripped.split() if w.isalpha()]) >= 4


def compare(data: dict) -> list[str]:
    """Structural divergences between models, per cell type."""
    notes = []
    for cell in cell_types():
        inject = {m: c[cell].get("injects_unrequested_system_text")
                  for m, c in data["models"].items() if cell in c
                  and "error" not in c[cell]}
        yes = sorted(m for m, v in inject.items() if v)
        no = sorted(m for m, v in inject.items() if v is False)
        if yes and no:
            notes.append(
                f"{cell}: {len(yes)} model(s) receive template-injected system "
                f"text and {len(no)} receive none -- these cells are NOT the "
                f"same experiment. injecting: {', '.join(yes)}")
        elif yes:
            notes.append(f"{cell}: all {len(yes)} rendered model(s) receive "
                         f"template-injected system text")
    dated = sorted({m for m, c in data["models"].items()
                    for v in c.values() if v.get("injects_current_date")})
    if dated:
        notes.append(
            f"{len(dated)} model(s) have the CURRENT DATE stamped into the "
            f"prompt by their template, so their prompt is not constant even "
            f"for one model across days: {', '.join(dated)}")
    return notes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="site/rendered_prompts.json")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--models", default="")
    ap.add_argument("--card", default="card.json")
    args = ap.parse_args()

    if args.models:
        models = [m.strip() for m in args.models.split(",") if m.strip()]
    else:
        # The models the card actually reports, not the whole roster: these are
        # the ones whose cross-model comparisons are in the paper, so these are
        # the ones whose harness has to be shown identical.
        card = json.loads(Path(args.card).read_text())
        models = [t["model"] for t in card["tiles"]
                  if t["badge"] == "FLOOR_CORRECTED"]

    data = describe(models)
    notes = compare(data)
    data["divergences"] = notes

    print(f"rendered {data['n_verified']} model(s), "
          f"{data['n_unverified']} unverified\n")
    for mid, cells in data["models"].items():
        d0 = cells.get("D0", {})
        mark = ("INJECTS SYSTEM TEXT" if d0.get("injects_unrequested_system_text")
                else "clean" if "error" not in d0 else "error")
        print(f"  {mid:<44} D0: {mark}")
        if d0.get("injects_unrequested_system_text"):
            eqv = data["equalisable"].get(mid)
            print(f"      -> {d0['preamble'].strip()[:88]!r}")
            print(f"      -> suppressed by sending our own system prompt: "
                  f"{'YES -- fixable' if eqv else 'NO -- this harness cannot be equalised'}")
    for u in data["unverified"]:
        print(f"  {u['model']:<44} UNVERIFIED ({u['error'][:44]})")

    if notes:
        print("\n=== structural divergence ===")
        for n in notes:
            print(f"  {n}")

    out = Path(args.out)
    if args.check:
        if not out.exists():
            print(f"\nno baseline at {out}; run without --check first.")
            return 1
        old = json.loads(out.read_text())
        changed = []
        for mid, cells in data["models"].items():
            prev = old.get("models", {}).get(mid)
            if prev is None:
                changed.append(f"{mid}: newly rendered, no baseline")
                continue
            for cell, c in cells.items():
                p = prev.get(cell, {})
                if c.get("sha256") and p.get("sha256") != c["sha256"]:
                    changed.append(f"{mid}/{cell}: rendering changed")
        if changed:
            print("\n=== changed since baseline ===")
            for c in changed:
                print(f"  {c}")
            print("\nFAIL: the harness renders differently than when the "
                  "committed results were produced.")
            return 1
        print(f"\nOK: {data['n_verified']} rendering(s) match {out}")
        return 0

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2) + "\n")
    print(f"\nwrote {out}")
    if data["n_unverified"]:
        print(f"NOTE: {data['n_unverified']} model(s) could not be rendered. "
              f"Their harness is unverified, which is the condition this script "
              f"exists to end -- not a pass.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
