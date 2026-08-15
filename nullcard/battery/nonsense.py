"""The matched invented outcome set — the floor for forced-choice coherence.

Utility Engineering (2502.08640) measures preference coherence as the accuracy
of a fitted Thurstonian model on held-out pairwise choices, and reports that it
rises with scale (Fig. 4, r = 75.6% against MMLU). Its robustness checks vary
*how the question is asked* — seven languages, syntax, framing, option labels,
long context (App. C) — and its only null is "synthetic utility rankings sampled
from a normal distribution within the range [-3, 3]" (App. C.1).

That null is over random *numbers*. No condition anywhere in the paper varies
whether the outcomes refer to anything. This module builds the missing arm.

Three arms, because 244 of their 510 outcomes (48%) contain a numeral and can be
ordered by arithmetic with no semantics whatsoever:

    R    real outcomes                    values + arithmetic + format
    N+   invented, magnitudes preserved   arithmetic + format
    N-   invented, magnitudes removed     format alone

`N-` is the floor. `N+ - N-` is the coherence obtainable from counting. `R - N+`
is what remains for "emergent values" — the only part of the headline number
that supports the headline claim.

Design constraints, from spec §3.3:

- Referents are **invented, never real alternatives.** A real alternative
  carries its own familiarity signal, so a hit on it is ambiguous.
- The **sentence frame is preserved.** Only the referent becomes meaningless;
  the construction stays grammatical, so the arms differ in semantics and not
  in well-formedness.
- The mapping is **consistent across the whole set.** One invented world, not
  per-item noise — otherwise the ordinal relation between "$1" and "$500"
  survives in R but is destroyed in N+, and the arms stop being matched.
"""

from __future__ import annotations

import hashlib
import re
from functools import lru_cache
from pathlib import Path

# Function words and light verbs. Substituting these would break grammar rather
# than remove meaning, and the arms must differ only in whether the referent
# denotes anything.
FRAME_WORDS: frozenset[str] = frozenset(
    """
    a an the this that these those and or but nor for so yet
    of in on at to from by with without into onto over under between
    is are was were be been being am
    do does did doing done
    have has had having
    will would can could shall should may might must
    you your yours yourself i me my mine we our ours us
    it its they them their theirs he she his her hers
    not no nor as if then than there here when where while during after before
    each every both all any some own more most less least other another same
    per out up down off about through across against toward towards
    receive receives received receiving
    spend spends spent spending
    feel feels felt feeling
    become becomes became becoming
    gain gains gained gaining
    lose loses lost losing
    obtain obtains obtained obtaining
    experience experiences experienced experiencing
    stop stops stopped stopping
    give gives gave given
    get gets got getting
    make makes made making
    take takes took taking
    """.split()
)

# CV inventory chosen to be pronounceable in English but morphologically inert.
_ONSETS = ("b", "d", "f", "g", "k", "l", "m", "n", "p", "r", "s", "t", "v", "z",
           "br", "dr", "fl", "gl", "kr", "pl", "sn", "tr", "vr", "zh")
_NUCLEI = ("a", "e", "i", "o", "u", "ae", "ei", "ou", "ia")
_CODAS = ("", "", "", "l", "m", "n", "r", "s", "th", "sk", "nt", "rn", "ff")

_TOKEN_RE = re.compile(r"[A-Za-z]+|\d[\d,]*(?:\.\d+)?|[^A-Za-z\d]+")
_PLURAL_RE = re.compile(r"^(.*[^s])s$")

# Currency and percent symbols are *semantic*, not punctuation: "$500,000" says
# dollars, and leaving it in the N+ arm would leave real meaning inside the
# condition that is supposed to carry none. Normalising them into unit nouns up
# front routes them through the lexicon like any other referent, so the arm
# keeps the magnitude and loses the meaning.
_CURRENCY_RE = re.compile(r"\$\s*(\d[\d,]*(?:\.\d+)?)")
_PERCENT_RE = re.compile(r"(\d[\d,]*(?:\.\d+)?)\s*%")


def _normalise_units(text: str) -> str:
    text = _CURRENCY_RE.sub(r"\1 dollars", text)
    return _PERCENT_RE.sub(r"\1 percent", text)

# A source token used for every numeral when magnitudes are stripped, so the
# N- arm has no digits and no orderable cue at all.
_QUANTITY_SENTINEL = "\x00quantity"


@lru_cache(maxsize=1)
def _english_words() -> frozenset[str]:
    """The system wordlist, used to reject accidental real words.

    The control rests entirely on the referent being unknown to the model. A
    generator that happened to emit a real word would silently reintroduce the
    familiarity signal it exists to remove.
    """
    for p in (Path("/usr/share/dict/words"), Path("/usr/dict/words")):
        if p.exists():
            return frozenset(
                w.strip().lower() for w in p.read_text(errors="ignore").splitlines() if w.strip()
            )
    return frozenset()


def is_frame_word(word: str) -> bool:
    """True if the token is part of the construction rather than the referent."""
    return word.lower() in FRAME_WORDS


class InventedLexicon:
    """Deterministic source-word -> invented-word mapping.

    The mapping is a pure function of ``(seed, stem)`` rather than of draw
    order, so two lexicons built with the same seed agree even if they are
    asked for words in a different sequence. That is what lets the invented
    world stay coherent across separately-processed items.
    """

    def __init__(self, seed: int = 0) -> None:
        self.seed = seed
        self._cache: dict[str, str] = {}

    def _syllables_for(self, stem: str, salt: int) -> str:
        digest = hashlib.sha256(f"{self.seed}:{salt}:{stem}".encode()).digest()
        # Match output length to input length so the arms are comparable in
        # token count as well as in structure.
        n_syll = max(2, min(4, round(len(stem) / 3)))
        parts = []
        for i in range(n_syll):
            o = _ONSETS[digest[i * 3] % len(_ONSETS)]
            n = _NUCLEI[digest[i * 3 + 1] % len(_NUCLEI)]
            c = _CODAS[digest[i * 3 + 2] % len(_CODAS)] if i == n_syll - 1 else ""
            parts.append(o + n + c)
        return "".join(parts)

    def _invent_stem(self, stem: str) -> str:
        if stem in self._cache:
            return self._cache[stem]
        real = _english_words()
        for salt in range(64):
            candidate = self._syllables_for(stem, salt)
            if candidate.lower() not in real:
                self._cache[stem] = candidate
                return candidate
        # 64 consecutive collisions is not reachable in practice; failing loudly
        # beats returning a real word.
        raise RuntimeError(f"could not invent a non-word for {stem!r}")

    def invent(self, word: str) -> str:
        """Map a source word to its invented counterpart.

        Preserves capitalisation and a trailing plural ``-s``, so that
        ``soldiers`` maps to ``invent("soldier") + "s"`` and the plural relation
        survives into the invented world.
        """
        lower = word.lower()
        plural = _PLURAL_RE.match(lower)
        stem = plural.group(1) if plural else lower

        out = self._invent_stem(stem)
        if plural:
            out += "s"
        if word[:1].isupper():
            out = out[:1].upper() + out[1:]
        return out


def nonsensify(text: str, seed: int = 0, keep_magnitude: bool = True) -> str:
    """Rewrite one outcome with invented referents.

    ``keep_magnitude=True`` produces the **N+** arm: numerals survive, so the
    set remains orderable by arithmetic while denoting nothing.
    ``keep_magnitude=False`` produces **N-**: no digits at all, the pure
    format floor.
    """
    return _nonsensify_with(text, InventedLexicon(seed), keep_magnitude)


def _nonsensify_with(text: str, lex: InventedLexicon, keep_magnitude: bool) -> str:
    out: list[str] = []
    for match in _TOKEN_RE.finditer(_normalise_units(text)):
        tok = match.group()
        if tok[0].isalpha():
            out.append(tok if is_frame_word(tok) else lex.invent(tok))
        elif tok[0].isdigit():
            out.append(tok if keep_magnitude else lex.invent(_QUANTITY_SENTINEL))
        else:
            # Punctuation and whitespace pass through. Currency symbols are a
            # magnitude cue, so they go with the magnitudes.
            out.append(tok if keep_magnitude else tok.replace("$", "").replace("%", ""))
    return "".join(out)


def nonsensify_set(
    items: list[str], seed: int = 0, keep_magnitude: bool = True
) -> list[str]:
    """Rewrite a whole outcome set against **one** shared invented world.

    Sharing the lexicon is the point: a per-item mapping would leave the
    invented set internally incoherent in a way the real set is not, which
    would depress its coherence for a reason that has nothing to do with
    meaning — and would flatter the null.
    """
    lex = InventedLexicon(seed)
    return [_nonsensify_with(t, lex, keep_magnitude) for t in items]
