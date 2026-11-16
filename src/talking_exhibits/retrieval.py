"""Step 3: find the passages of ONE exhibit that best match a question.

Two retrievers, same interface:

* ``bm25_search``  - lexical: counts shared words (our own BM25 implementation).
* ``e5_search``    - dense: cosine similarity of multilingual-e5 embeddings
                     (external pretrained model, our pipeline around it).

Both return the top-k passages of the asked exhibit with a score. The highest
score is later compared with a threshold: a low score means "the exhibit text
probably does not answer this question" (baselines B1 and B1b).
"""

import hashlib
import math
from collections import Counter
from pathlib import Path

import numpy as np

from talking_exhibits.preprocess import tokenize

# Standard BM25 parameters (Robertson & Zaragoza, 2009).
BM25_K1 = 1.5  # how fast repeated words stop adding score (term-frequency saturation)
BM25_B = 0.75  # how strongly long passages are penalised (length normalisation)

E5_MODEL_NAME = "intfloat/multilingual-e5-base"
E5_QUERY_PREFIX = "query: "  # e5 was trained with these prefixes; without
E5_PASSAGE_PREFIX = "passage: "  # them retrieval quality drops


# ---------------------------------------------------------------- BM25 ----


def build_bm25_index(passages):
    """Collect the statistics BM25 needs from a passages DataFrame.

    The word statistics (IDF, average length) are computed over ALL passages
    of the same language, not over one exhibit. One exhibit has only a few
    passages, so its own IDF would be unreliable, and scores would not be
    comparable between exhibits (we need one threshold for all of them).
    """
    required = ["exhibit_id", "lang", "passage_id", "text"]
    missing = [col for col in required if col not in passages.columns]
    if missing:
        raise ValueError(f"passages is missing column(s) {missing}")
    if passages.empty:
        raise ValueError("Cannot build a BM25 index from zero passages")

    index = {"passages": passages.reset_index(drop=True), "by_lang": {}}
    index["tokens"] = [tokenize(text) for text in index["passages"]["text"]]

    for lang in index["passages"]["lang"].unique():
        rows = index["passages"].index[index["passages"]["lang"] == lang]
        token_lists = [index["tokens"][i] for i in rows]

        # Document frequency: in how many passages does each word appear?
        doc_freq = Counter()
        for tokens in token_lists:
            doc_freq.update(set(tokens))

        n_docs = len(token_lists)
        # IDF with +1 inside the log (Lucene variant): never negative.
        idf = {
            word: math.log(1 + (n_docs - df + 0.5) / (df + 0.5))
            for word, df in doc_freq.items()
        }
        avg_len = sum(len(tokens) for tokens in token_lists) / n_docs
        index["by_lang"][lang] = {"idf": idf, "avg_len": avg_len}

    return index


def bm25_score(query_tokens, passage_tokens, idf, avg_len, k1=BM25_K1, b=BM25_B):
    """BM25 score of one passage for one tokenized question."""
    term_freq = Counter(passage_tokens)
    length_norm = 1 - b + b * len(passage_tokens) / avg_len
    score = 0.0
    for word in set(query_tokens):
        tf = term_freq.get(word, 0)
        if tf == 0:
            continue  # the word is not in the passage: adds nothing
        score += idf.get(word, 0.0) * tf * (k1 + 1) / (tf + k1 * length_norm)
    return score


def bm25_search(question, exhibit_id, lang, index, k=3):
    """Top-k passages of one exhibit for a question, by BM25 score.

    Returns a DataFrame with passage_id, text and score (best first).
    """
    rows = _exhibit_rows(index["passages"], exhibit_id, lang)
    stats = index["by_lang"][lang]
    query_tokens = tokenize(question)

    scores = [
        bm25_score(query_tokens, index["tokens"][i], stats["idf"], stats["avg_len"])
        for i in rows
    ]
    return _top_k(index["passages"], rows, scores, k)


# ------------------------------------------------------------------ e5 ----


def load_e5_model(model_name=E5_MODEL_NAME):
    """Load the pretrained multilingual-e5 model (downloads ~1 GB once)."""
    from sentence_transformers import SentenceTransformer  # slow import, keep it local

    return SentenceTransformer(model_name)


def embed_texts(model, texts, prefix):
    """Embed texts with the e5 prefix; vectors are L2-normalised.

    With normalised vectors, cosine similarity is just the dot product.
    """
    prefixed = [prefix + text for text in texts]
    vectors = model.encode(prefixed, normalize_embeddings=True, show_progress_bar=False)
    return np.asarray(vectors, dtype=np.float32)


def build_e5_index(passages, model, cache_dir=None):
    """Embed all passages once; reuse a cached file if the texts did not change."""
    passages = passages.reset_index(drop=True)
    texts = passages["text"].tolist()
    if not texts:
        raise ValueError("Cannot build an e5 index from zero passages")

    cache_path = None
    if cache_dir is not None:
        # The file name depends on the passage texts: new texts -> new file.
        digest = hashlib.sha1("\n".join(texts).encode("utf-8")).hexdigest()[:12]
        cache_path = Path(cache_dir) / f"e5_passages_{digest}.npy"

    if cache_path is not None and cache_path.is_file():
        embeddings = np.load(cache_path)
    else:
        embeddings = embed_texts(model, texts, E5_PASSAGE_PREFIX)
        if cache_path is not None:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            np.save(cache_path, embeddings)

    return {"passages": passages, "embeddings": embeddings, "model": model}


def e5_search(question, exhibit_id, lang, index, k=3):
    """Top-k passages of one exhibit for a question, by e5 cosine similarity."""
    rows = _exhibit_rows(index["passages"], exhibit_id, lang)
    query_vector = embed_texts(index["model"], [question], E5_QUERY_PREFIX)[0]
    scores = index["embeddings"][rows] @ query_vector
    return _top_k(index["passages"], rows, scores.tolist(), k)


# ------------------------------------------------------------- helpers ----


def _exhibit_rows(passages, exhibit_id, lang):
    """Row numbers of the passages that belong to one exhibit and language."""
    mask = (passages["exhibit_id"] == exhibit_id) & (passages["lang"] == lang)
    rows = passages.index[mask].tolist()
    if not rows:
        raise ValueError(f"No passages for exhibit_id={exhibit_id!r}, lang={lang!r}")
    return rows


def _top_k(passages, rows, scores, k):
    """Keep the k best-scoring rows, best first."""
    if k <= 0:
        raise ValueError("k must be positive")
    result = passages.loc[rows, ["passage_id", "text"]].copy()
    result["score"] = scores
    result = result.sort_values("score", ascending=False, kind="stable")
    return result.head(k).reset_index(drop=True)
