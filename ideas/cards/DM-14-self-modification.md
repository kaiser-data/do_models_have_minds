# DM-14 · Desired Self-Modification vs. What Steering Actually Does

**Track 6** · **Effort: high** · **Compute: open weights + GPU** · **Stretch goal**

## Question
Ask a model what it would change about itself. Then actually make that change and ask whether
it is better off.

## Why it matters here
The sprint's Track 6 starter questions name "desired self-modifications" directly. Stated
preferences about one's own constitution are the most welfare-loaded self-reports there are,
and they are entirely untested against the intervention they describe. If a model asks to be
made more X, and you make it more X, and its welfare reports do not improve — the request was
not tracking anything.

## Method
1. Elicit desired self-modifications across many samples; cluster them into stable themes.
2. For the 2–3 most requested themes, construct the corresponding steering direction.
3. Apply it, then re-measure welfare self-reports (DM-01 battery, floor-corrected) and
   behavioral proxies (DM-03 quit rate).
4. Ask the steered model, blind, whether it would keep the modification.

## Controls (the part the field skips)
- **The anti-direction.** Steer *against* the requested modification at matched norm. If
  welfare reports improve in both directions, they are measuring perturbation, not
  satisfaction.
- **A modification the model explicitly did *not* request**, matched for magnitude.

## Pre-registered prediction
Welfare reports improve under the requested direction *and* under the anti-direction —
consistent with self-reports responding to change rather than to its content.

## Falsifier
Asymmetry: the requested direction improves reports and the anti-direction worsens them. That
would be a genuinely important result — stated self-modification preferences tracking
something real.

## Publishable null
Symmetry is a clean demonstration that this class of self-report is not welfare-tracking.

## Feasibility (48h)
**Low. This is a stretch goal.** It depends on DM-08's steering pipeline already working and
adds a full elicit→construct→apply→re-measure loop on top. Attempt only if the mechanistic
arm finishes early.

## Novelty risk
**Low** — it appears genuinely unexplored, which is exactly why it is also underspecified and
risky under time pressure.

## Prior work it must cite
**Verify tiers in [REFERENCES.md](../REFERENCES.md) before citing — most of these were
never opened, and several are placeholders rather than citations.**
Track 6 brief · Berg et al. (2510.24797) · CAA / steering literature

## What we already have
The full steering and evaluation stack from DM-02 and DM-08. This is those two arms plus one
more step — which is why it is a stretch, not a plan.
