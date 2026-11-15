"""Tests for preprocess.py: normalization, sentence splitting, chunking."""

from pathlib import Path

import pytest

from talking_exhibits.data import load_exhibits
from talking_exhibits.preprocess import (
    chunk,
    chunk_exhibits,
    chunk_sentences,
    count_words,
    has_diacritics,
    normalize,
    split_sentences,
    strip_diacritics,
    tokenize,
)

FIXTURES = Path(__file__).parent / "fixtures"


def test_normalize_lowercases_and_keeps_diacritics():
    assert normalize("  Čitaonica  IMA\n180 mjesta ") == "čitaonica ima 180 mjesta"


def test_strip_diacritics():
    assert strip_diacritics("Šarić čuva žute đakone") == "Saric cuva zute djakone"


def test_has_diacritics():
    assert has_diacritics("najveća brzina")
    assert not has_diacritics("najveca brzina")


def test_tokenize_keeps_bosnian_words_whole():
    assert tokenize("Koliko košta članarina?") == ["koliko", "košta", "članarina"]


def test_split_sentences_basic():
    text = "Prva rečenica. Druga rečenica! Treća?"
    assert split_sentences(text) == ["Prva rečenica.", "Druga rečenica!", "Treća?"]


def test_split_sentences_does_not_break_dates_and_ordinals():
    text = "Otvorena je 2009. godine u prizemlju. Radi od 5. maja."
    assert split_sentences(text) == ["Otvorena je 2009. godine u prizemlju.", "Radi od 5. maja."]


def test_split_sentences_does_not_break_after_abbreviation():
    text = "Projekat vodi prof. Hasić sa saradnicima. Tim ima deset članova."
    assert split_sentences(text) == [
        "Projekat vodi prof. Hasić sa saradnicima.",
        "Tim ima deset članova.",
    ]


def test_split_sentences_loses_nothing():
    exhibits = load_exhibits(FIXTURES / "exhibits")
    for text in exhibits["text"]:
        assert " ".join(split_sentences(text)) == " ".join(text.split())


def test_chunk_keeps_every_sentence_in_order():
    exhibits = load_exhibits(FIXTURES / "exhibits")
    for text in exhibits["text"]:
        sentences = split_sentences(text)
        groups = chunk_sentences(sentences, size=60, overlap=15)
        assert len(groups) > 1  # the fixture texts are long enough to be cut

        # Remove the overlapping start of every passage: what is left must be
        # exactly the original sentences, each once, in the original order.
        rebuilt = list(groups[0])
        for previous, current in zip(groups, groups[1:]):
            n_shared = _shared_sentences(previous, current)
            rebuilt.extend(current[n_shared:])
        assert rebuilt == sentences


def test_chunk_overlap_is_within_the_limit():
    exhibits = load_exhibits(FIXTURES / "exhibits")
    sentences = split_sentences(exhibits.iloc[0]["text"])
    groups = chunk_sentences(sentences, size=60, overlap=15)
    for previous, current in zip(groups, groups[1:]):
        n_shared = _shared_sentences(previous, current)
        shared_words = sum(count_words(s) for s in current[:n_shared])
        assert shared_words <= 15
        assert len(current) > n_shared  # every passage adds something new


def test_chunk_respects_size_unless_one_sentence_is_longer():
    sentences = ["a b c d e.", "f g h i j.", "k l m n o.", "p q r s t."]
    groups = chunk_sentences(sentences, size=10, overlap=5)
    assert groups == [
        ["a b c d e.", "f g h i j."],
        ["f g h i j.", "k l m n o."],
        ["k l m n o.", "p q r s t."],
    ]


def test_short_text_gives_one_passage():
    assert chunk("Samo jedna kratka rečenica.") == ["Samo jedna kratka rečenica."]


def test_empty_text_is_rejected():
    with pytest.raises(ValueError, match="empty"):
        chunk("   ")


def test_bad_overlap_is_rejected():
    with pytest.raises(ValueError, match="overlap"):
        chunk_sentences(["a."], size=10, overlap=10)


def test_chunk_exhibits_makes_a_passage_table():
    exhibits = load_exhibits(FIXTURES / "exhibits")
    passages = chunk_exhibits(exhibits, size=60, overlap=15)
    assert list(passages.columns) == ["exhibit_id", "lang", "passage_id", "text", "n_words"]
    assert passages["passage_id"].is_unique
    assert set(passages["exhibit_id"]) == {"lipa_library", "lipa_solar_car"}


def _shared_sentences(previous, current):
    """How many sentences at the start of `current` end `previous`."""
    for n in range(min(len(previous), len(current)), 0, -1):
        if previous[-n:] == current[:n]:
            return n
    return 0
