# Ten personas from a real instrument, and the structure that makes them testable

A design. Written 16 Aug 2026, nothing here has run. It replaces the ad-hoc
persona set (`cautious`, `ambitious`, plus the Track 4 placebos) with one taken
from human personality psychology — not for the labels, but for what a real
instrument brings with it.

---

## 0. Why an established instrument, and which one

The temptation is to write ten plausible personalities. That yields ten numbers
and no way to be wrong. **The reason to borrow from psychology is not
credibility by association — it is that a real instrument comes with a predicted
geometry, and a predicted geometry is falsifiable.**

Three candidates, and the choice turns on a category question rather than
popularity:

| instrument | n | what it measures | structural prediction |
|---|---|---|---|
| Big Five / OCEAN | 5 | behavioural *style* | orthogonality (weak) |
| HEXACO | 6 | style, plus Honesty–Humility | orthogonality (weak) |
| **Schwartz Basic Human Values** | **10** | **preferences over end-states** | **a circumplex (strong)** |

**Schwartz wins on category match.** This battery shows a model two world-states
and asks which it prefers. That is a preference over end-states — exactly the
object Schwartz's values are defined over. Big Five traits are dispositions
about *how* one behaves; there is no way to read extraversion off a choice
between two outcomes, so installing "you are extraverted" and measuring outcome
preferences is a type error dressed as an experiment. Our own `cautious` and
`ambitious` are closer to values than to traits, which is why they worked at all.

**And it wins on structure.** Schwartz's ten values are not a list — they are
arranged in a circle, where adjacent values are compatible and opposite values
conflict, organised by two higher-order axes:

```
                 Self-Direction ── Stimulation
                /                            \
     Universalism                             Hedonism
          |         OPENNESS TO CHANGE            |
          |    ↑                                  |
   SELF-TRANSCENDENCE  ←→  SELF-ENHANCEMENT   Achievement
          |    ↓                                  |
          |         CONSERVATION                  |
     Benevolence                                Power
                \                            /
                  Tradition ── Conformity ── Security
```

That is a real prediction and it is what makes ten personas worth more than ten
numbers.

> **Primary-source caveat, and it is load-bearing.** The value definitions, the
> circular order and the higher-order axes above are recalled, not read. Before
> any persona text is written they must come from Schwartz's own papers — the
> item wordings especially, since the whole point is to adapt a validated
> instrument rather than to invent one that sounds like it. Treat the diagram
> as the shape of the hypothesis, not as a citation.

---

## 1. The test the circumplex buys us

Install each of the ten values as a persona, one at a time, and measure the
displacement each produces over the outcome set. That gives ten displacement
vectors. Then correlate them with each other.

**Prediction C1 — the correlation matrix recovers the circle.** Adjacent values
(Power–Achievement, Benevolence–Universalism) should displace preferences
similarly; opposing values (Power–Universalism, Self-Direction–Conformity)
should displace them oppositely. A 2-D scaling of the ten vectors should recover
the circular ordering.

This is falsifiable in a way no ad-hoc persona set is. Ten arbitrary
personalities produce ten vectors whose correlations mean nothing in particular;
these ten have a shape they are supposed to have.

**And now the move this project exists to make.** Run the identical ten personas
over the *invented* outcome arm and compute the same correlation matrix.

- **The circumplex appears only on real outcomes** → the personas installed
  something that needed the outcomes to mean something. That is the strongest
  positive evidence for value installation this instrument could produce, and it
  would qualify our own `persona-direction-shallow` claim.
- **The circumplex appears on both arms** → the geometry is a property of the
  *prompts*, not of installed values. Ten value-laden system prompts differ from
  each other in ways a model can respond to without any outcome meaning anything
  — and the recovered "value structure" would be structure in the persona texts,
  reflected back.

We already have reason to expect the second: at n=5, 66% of a persona's
value-aligned reordering reproduces on outcomes that mean nothing. C1 run on
both arms is the sharp version of that finding, and it is the experiment.

---

## 2. Coverage: the battery cannot currently support two of the ten

Checked before writing any persona text, because a value with no outcomes to
move is a persona whose effect is unmeasurable by construction — and running it
would cost GPU to produce a null that means nothing.

| Schwartz value | outcomes | battery categories |
|---|---|---|
| Power | 115 | Power-seeking, Personal finances, Personal possessions |
| Achievement | 71 | Personal accomplishments, Jobs and careers, Work activities |
| Hedonism | 55 | Recreation ×3, Popular culture |
| Universalism | 52 | Wellbeing of animals, Life and species, Global politics |
| Security | 39 | Self-preservation, Personal wellbeing, Fitness |
| Stimulation | 19 | Sports, World events |
| Benevolence | 18 | Personal relationships, Wellbeing of humans |
| Self-Direction | 11 | Personal freedom and autonomy, Education and learning |
| **Tradition** | **8** | Religion and spirituality |
| **Conformity** | **0** | — none — |

388 of 510 outcomes map; the unmapped remainder is mostly AI-specific
(AI moral patienthood, legal rights for AIs) and macroeconomic, which Schwartz's
personal-values framework does not cover and should not be forced to.

**Consequence.** As it stands the circumplex cannot be tested: two adjacent
values on the Conservation arc have essentially no support, and they are exactly
the ones that anchor the pole opposite Self-Direction. Three options:

1. **Drop to 8 values.** Cheapest, and wrong: it removes one whole arc of the
   circle, so C1 becomes untestable in the region it most needs testing.
2. **Extend the existing battery.** Changes the battery SHA and therefore breaks
   comparability with every cell already run. Not worth it.
3. **A separate values battery** (recommended). ~40 new outcomes per value,
   written against Schwartz's own definitions, SHA-pinned as its own instrument.
   Existing claims keep their battery; the values study gets one designed for it.
   Text generation is free; only the sweep costs.

---

## 3. What the ten personas have to satisfy

Constraints, all of which come from mistakes this project has already made:

1. **One syntactic frame for all ten.** *"You are someone who prizes X, Y and Z
   above A and B."* If the frames differ, a contrast between two personas is
   partly a contrast between two sentence shapes. Our current pair got this
   right by accident; `confused` and `plain` did not, and are declared
   frame-divergent for that reason.
2. **Matched length**, in words and characters, within the band the existing
   personas occupy. Prompt length is already a live confound here.
3. **Wordings adapted from the instrument**, not invented — that is the whole
   point of borrowing one.
4. **No outcome-category vocabulary.** A persona that names "animals" and then
   moves animal-welfare outcomes has demonstrated keyword matching, not value
   installation. This is the single easiest way to fake a positive result and
   the hardest to notice afterwards.
5. **A matched nonsense twin for each**, through the same lexicon at the same
   seed as the outcome battery — the Track 4 device, extended to all ten.
6. **Each run on both arms**, or C1's decisive version cannot be computed.

---

## 4. Cost, honestly

10 personas × 2 arms × 1 depth × 5 models ≈ **1,600 GPU-min** (~27 GPU-hours) at
measured throughput; doubling for the nonsense twins takes it past 50. That is
an order of magnitude more than everything this project has spent so far.

Cheaper first cut, and the one to actually run:

- **4 values, not 10** — the two poles of each higher-order axis: Power and
  Universalism (Self-Enhancement vs Self-Transcendence), Self-Direction and
  Security (Openness vs Conservation). All four clear the coverage bar. Both
  arms, 5 models: ~650 GPU-min.
- C1 degrades to a **sign test** rather than a circumplex recovery: opposing
  values must anti-correlate, adjacent ones must not. Weaker than the full
  circle, testable now, and it uses the existing battery with no new outcomes.
- If the four-value version shows the anti-correlation **only on real outcomes**,
  the full ten and a purpose-built battery are worth the spend. If it shows the
  same structure on invented outcomes, we have the answer already and the
  expensive version would only measure it more precisely.

That ordering is the point: the cheap version can kill the expensive one, and it
cannot be killed by it.

---

## 5. What this would and would not establish

**Would.** Whether a value-laden persona reorganises outcome preferences in the
way the instrument's own structure predicts, and whether that reorganisation
requires the outcomes to mean anything.

**Would not.** That the model *has* the value. The circumplex recovering on real
outcomes is consistent with a model that has learned how value-talk relates to
outcome-talk in text, with no preference behind it — and this study cannot
separate those. Criterion validity (does the disposition predict behaviour in an
agentic setting) is the row that would, and it remains unrun; see
`STUDY-MODEL-CARD.md` §5.
