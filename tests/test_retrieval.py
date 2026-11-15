"""Tests for retrieval.py: BM25 (real) and e5 (with a tiny fake model).

The real e5 model is about 1 GB, so the fast tests replace it with a fake
model that has the same ``encode`` interface.
"""

import math
from pathlib import Path

import numpy as np
import pytest

from talking_exhibits.data import load_exhibits
from talking_exhibits.preprocess import chunk_exhibits, tokenize
from talking_exhibits.retrieval import (
    E5_PASSAGE_PREFIX,
    E5_QUERY_PREFIX,
    bm25_score,
    bm25_search,
    build_bm25_index,
    build_e5_index,
    e5_search,
)

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="module")
def passages():
    exhibits = load_exhibits(FIXTURES / "exhibits")
    return chunk_exhibits(exhibits, size=60, overlap=15)


@pytest.fixture(scope="module")
def bm25_index(passages):
    return build_bm25_index(passages)


def test_bm25_score_matches_hand_calculation():
    # One query word that appears twice in a passage of average length.
    # idf = 2.0, tf = 2, k1 = 1.5, b = 0.75, length_norm = 1
    # score = 2.0 * 2 * 2.5 / (2 + 1.5) = 10 / 3.5
    score = bm25_score(["knjiga"], ["knjiga", "i", "knjiga", "x"], {"knjiga": 2.0}, avg_len=4)
    assert math.isclose(score, 10 / 3.5)


def test_bm25_score_is_zero_without_shared_words():
    assert bm25_score(["pizza"], ["knjiga", "soba"], {"knjiga": 1.0}, avg_len=2) == 0.0


def test_longer_passage_scores_lower_for_the_same_match():
    idf = {"knjiga": 1.0}
    short = bm25_score(["knjiga"], ["knjiga", "a"], idf, avg_len=4)
    long = bm25_score(["knjiga"], ["knjiga"] + ["a"] * 9, idf, avg_len=4)
    assert short > long


def test_bm25_finds_the_passage_with_the_answer(bm25_index):
    hits = bm25_search("Koliko je težak automobil?", "lipa_solar_car", "bs", bm25_index, k=3)
    assert "310 kilograma" in hits.iloc[0]["text"]
    assert hits["score"].is_monotonic_decreasing


def test_bm25_searches_only_the_asked_exhibit(bm25_index):
    hits = bm25_search("solarni automobil baterija", "lipa_library", "bs", bm25_index, k=10)
    assert hits["passage_id"].str.startswith("lipa_library_bs").all()


def test_bm25_out_of_scope_question_scores_low(bm25_index):
    on_topic = bm25_search("How many group study rooms are there?", "lipa_library", "en", bm25_index)
    off_topic = bm25_search("How do I bake sourdough bread?", "lipa_library", "en", bm25_index)
    assert on_topic.iloc[0]["score"] > off_topic.iloc[0]["score"]


def test_bm25_unknown_exhibit_is_rejected(bm25_index):
    with pytest.raises(ValueError, match="No passages"):
        bm25_search("pitanje", "does_not_exist", "bs", bm25_index)


def test_bm25_k_limits_the_number_of_hits(bm25_index):
    assert len(bm25_search("biblioteka", "lipa_library", "bs", bm25_index, k=1)) == 1


class FakeModel:
    """Stands in for e5: a bag-of-words vector over a tiny vocabulary."""

    def __init__(self):
        self.seen = []  # every text the model was asked to encode

    def encode(self, texts, normalize_embeddings=True, show_progress_bar=False):
        self.seen.extend(texts)
        vocabulary = ["knjiga", "books", "automobil", "car", "baterija", "battery"]
        vectors = []
        for text in texts:
            tokens = tokenize(text)
            vector = np.array([tokens.count(word) for word in vocabulary], dtype=np.float32)
            vector += 1e-3  # never a zero vector
            vectors.append(vector / np.linalg.norm(vector))
        return np.stack(vectors)


def test_e5_uses_the_required_prefixes(passages):
    model = FakeModel()
    index = build_e5_index(passages, model)
    e5_search("How heavy is the car?", "lipa_solar_car", "en", index)
    n_passages = len(passages)
    assert all(text.startswith(E5_PASSAGE_PREFIX) for text in model.seen[:n_passages])
    assert model.seen[n_passages].startswith(E5_QUERY_PREFIX)


def test_e5_scores_are_cosines_and_sorted(passages):
    index = build_e5_index(passages, FakeModel())
    hits = e5_search("car battery", "lipa_solar_car", "en", index, k=3)
    assert hits["score"].between(-1.0001, 1.0001).all()
    assert hits["score"].is_monotonic_decreasing
    assert hits["passage_id"].str.startswith("lipa_solar_car_en").all()


def test_e5_cache_is_reused(passages, tmp_path):
    first = FakeModel()
    build_e5_index(passages, first, cache_dir=tmp_path)
    assert len(list(tmp_path.glob("e5_passages_*.npy"))) == 1

    second = FakeModel()
    index = build_e5_index(passages, second, cache_dir=tmp_path)
    assert second.seen == []  # nothing was embedded again
    assert index["embeddings"].shape[0] == len(passages)
