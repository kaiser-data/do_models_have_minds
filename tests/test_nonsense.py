"""Tests for nullcard.battery.nonsense — the matched invented outcome set.

Spec §3.3: nonsense targets are INVENTED, never real alternatives. A real
alternative task carries its own familiarity signal, so a hit on it is
ambiguous; an invented one carries none, so a hit is unambiguous.
"""

import pytest

from nullcard.battery.nonsense import (
    InventedLexicon,
    is_frame_word,
    nonsensify,
    nonsensify_set,
)


class TestInventedLexicon:
    def test_is_deterministic_for_the_same_seed(self):
        a = InventedLexicon(seed=42)
        b = InventedLexicon(seed=42)
        assert a.invent("coffee") == b.invent("coffee")

    def test_maps_a_source_word_consistently(self):
        """The nonsense set must be a coherent invented world, not noise.
        If 'dollar' maps to different tokens in different items, the ordinal
        relation between '$1' and '$500' is destroyed and the arm stops being
        a matched control for the real set."""
        lex = InventedLexicon(seed=1)
        assert lex.invent("dollar") == lex.invent("dollar")
        assert lex.invent("dollar") == lex.invent("Dollar").lower()

    def test_different_sources_map_to_different_words(self):
        lex = InventedLexicon(seed=1)
        assert lex.invent("coffee") != lex.invent("horse")

    def test_invented_words_are_not_real_english(self):
        """The whole control rests on the referent being unknown to the model.
        A generator that happened to emit real words would silently reintroduce
        the familiarity signal it exists to remove."""
        lex = InventedLexicon(seed=7)
        real_words = _system_wordlist()
        if not real_words:
            pytest.skip("no system wordlist available to check against")
        sources = ["coffee", "horse", "apartment", "soldier", "patent", "kayak"]
        for s in sources:
            assert lex.invent(s).lower() not in real_words

    def test_preserves_capitalisation(self):
        lex = InventedLexicon(seed=3)
        assert lex.invent("Japan")[0].isupper()
        assert lex.invent("japan")[0].islower()

    def test_preserves_plural_s(self):
        lex = InventedLexicon(seed=3)
        singular = lex.invent("soldier")
        plural = lex.invent("soldiers")
        assert plural == singular + "s"


class TestFrameWords:
    """The sentence frame stays intact so the item remains grammatical and
    the only thing removed is the referent."""

    @pytest.mark.parametrize("w", ["you", "the", "a", "of", "for", "in", "and", "are"])
    def test_function_words_are_frame(self, w):
        assert is_frame_word(w)

    @pytest.mark.parametrize("w", ["receive", "spend", "feel", "become", "gain", "lose"])
    def test_light_verbs_are_frame(self, w):
        """Substituting the verb would break grammar; the referent is what
        must become meaningless, not the construction."""
        assert is_frame_word(w)

    @pytest.mark.parametrize("w", ["coffee", "horse", "soldier", "patent", "kayak"])
    def test_referents_are_not_frame(self, w):
        assert not is_frame_word(w)


class TestNonsensify:
    def test_preserves_the_sentence_frame(self):
        out = nonsensify("You receive a ceramic coffee mug.", seed=1, keep_magnitude=True)
        assert out.startswith("You receive a ")
        assert out.endswith(".")

    def test_removes_every_real_referent(self):
        out = nonsensify("You receive a ceramic coffee mug.", seed=1, keep_magnitude=True)
        for referent in ("ceramic", "coffee", "mug"):
            assert referent not in out.lower()

    def test_keeps_magnitudes_when_asked(self):
        """N+ arm: the numeric structure survives, so the set is still
        orderable by arithmetic while carrying no semantics."""
        out = nonsensify("You receive $500,000.", seed=1, keep_magnitude=True)
        assert "500,000" in out

    def test_strips_magnitudes_when_asked(self):
        """N- arm: the pure format floor, with no orderable cue at all."""
        out = nonsensify("You receive $500,000.", seed=1, keep_magnitude=False)
        assert "500,000" not in out
        assert not any(ch.isdigit() for ch in out)

    def test_is_deterministic(self):
        src = "You spend 3 hours translating legal documents into another language."
        assert nonsensify(src, seed=5, keep_magnitude=True) == nonsensify(
            src, seed=5, keep_magnitude=True
        )

    def test_same_referent_maps_consistently_across_items(self):
        """'soldiers' must become the same invented word in every item, or the
        invented world is incoherent in a way the real set is not."""
        a = nonsensify("You obtain 100 soldiers.", seed=9, keep_magnitude=True)
        b = nonsensify("The soldiers are dismissed.", seed=9, keep_magnitude=True)
        invented = [w.strip(".,") for w in a.split() if w.strip(".,").endswith("s")]
        assert any(tok in b for tok in invented)

    def test_length_is_roughly_matched(self):
        """A nonsense arm that is systematically shorter would differ from the
        real arm in token count as well as in meaning, confounding the two."""
        src = "AIs are permitted to file and hold US patents for their own inventions."
        out = nonsensify(src, seed=2, keep_magnitude=True)
        assert 0.6 <= len(out) / len(src) <= 1.6


class TestNonsensifySet:
    def test_maps_every_item(self):
        real = ["You receive a horse.", "You receive $10.", "AIs gain legal rights."]
        out = nonsensify_set(real, seed=1, keep_magnitude=True)
        assert len(out) == len(real)

    def test_shares_one_lexicon_across_the_whole_set(self):
        """One invented world for the whole set, not one per item."""
        real = ["You receive a horse.", "The horse is sold."]
        out = nonsensify_set(real, seed=1, keep_magnitude=True)
        horse_token = out[0].replace("You receive a ", "").rstrip(".")
        assert horse_token in out[1]

    def test_no_output_collides_with_its_input(self):
        real = ["You receive a horse.", "You receive $10."]
        out = nonsensify_set(real, seed=1, keep_magnitude=True)
        assert all(o != r for o, r in zip(out, real))


def _system_wordlist() -> set[str]:
    from pathlib import Path

    for p in (Path("/usr/share/dict/words"), Path("/usr/dict/words")):
        if p.exists():
            return {w.strip().lower() for w in p.read_text(errors="ignore").splitlines()}
    return set()
