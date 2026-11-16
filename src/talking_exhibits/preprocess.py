"""Step 2: text normalization, sentence splitting and chunking.

An exhibit text (300-800 words) is too long to score as one unit, so we cut it
into passages of whole sentences (about 120 words) that overlap a little.
Retrieval and the answerability classifier both work on these passages.

Diacritics (č, ć, š, ž, đ) are KEPT on purpose: in Bosnian they change the
word ("kuća" is not "kuca"). ``strip_diacritics`` exists only as a helper for
analysis and for questions typed without diacritics.
"""

import re
import unicodedata

import pandas as pd

# A token is a run of letters/digits (Unicode-aware, so "šuma" stays one token).
TOKEN_PATTERN = re.compile(r"\w+", re.UNICODE)

# Abbreviations that end with a dot but do not end a sentence.
ABBREVIATIONS = {
    # Bosnian
    "dr", "mr", "prof", "doc", "npr", "tj", "itd", "sl", "br", "god", "st", "ul", "str", "tzv",
    # English
    "mrs", "ms", "e.g", "i.e", "etc", "vs", "no", "fig",
}

# A sentence may end at . ! ? followed by spaces and then an opening
# quote/bracket or a capital letter. Lowercase after the dot ("5. maja",
# "2004. godine") is therefore never a sentence boundary.
SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[\"„“(\[]?[A-ZČĆŠŽĐ])")


def normalize(text):
    """Lowercase and collapse whitespace. Diacritics are kept."""
    text = unicodedata.normalize("NFC", text)  # one code point per letter (š, not s + caron)
    text = text.lower()
    return re.sub(r"\s+", " ", text).strip()


def strip_diacritics(text):
    """Replace č ć š ž đ with c c s z dj (helper, not used for indexing)."""
    text = text.replace("đ", "dj").replace("Đ", "Dj")
    decomposed = unicodedata.normalize("NFD", text)
    without_marks = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
    return unicodedata.normalize("NFC", without_marks)


def has_diacritics(text):
    """True if the text contains at least one of č ć š ž đ."""
    return bool(re.search(r"[čćšžđČĆŠŽĐ]", text))


def tokenize(text):
    """Normalize, then split into word tokens. Used for BM25."""
    return TOKEN_PATTERN.findall(normalize(text))


def split_sentences(text):
    """Split a text into sentences. No character except whitespace is lost."""
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []

    sentences = []
    current = ""
    for piece in SENTENCE_END.split(text):
        current = f"{current} {piece}".strip() if current else piece
        # If the piece ends with an abbreviation ("prof."), the sentence goes on.
        last_word = current.split()[-1].rstrip(".").lower()
        if current.endswith(".") and last_word in ABBREVIATIONS:
            continue
        sentences.append(current)
        current = ""
    if current:
        sentences.append(current)
    return sentences


def count_words(text):
    """Number of whitespace-separated words."""
    return len(text.split())


def chunk_sentences(sentences, size=120, overlap=30):
    """Group sentences into passages of about ``size`` words.

    Each new passage starts with the last sentences of the previous one, as
    long as they have at most ``overlap`` words in total. That way an answer
    that sits on a passage border is still complete in one of the two passages.
    A sentence is never cut, so a single very long sentence can exceed ``size``.
    """
    if size <= 0:
        raise ValueError("size must be positive")
    if overlap < 0 or overlap >= size:
        raise ValueError("overlap must be >= 0 and smaller than size")

    passages = []
    current = []  # sentences of the passage we are building
    n_new = 0  # how many of them are new (not copied from the previous passage)

    for sentence in sentences:
        current_words = sum(count_words(s) for s in current)
        if n_new > 0 and current_words + count_words(sentence) > size:
            passages.append(current)
            current = _overlap_tail(current, overlap)
            n_new = 0
        current.append(sentence)
        n_new += 1

    if n_new > 0:
        passages.append(current)
    return passages


def _overlap_tail(sentences, overlap):
    """Last sentences of a passage with at most ``overlap`` words in total."""
    tail = []
    words = 0
    for sentence in reversed(sentences):
        words += count_words(sentence)
        if words > overlap:
            break
        tail.insert(0, sentence)
    return tail


def chunk(text, size=120, overlap=30):
    """Cut one text into overlapping passages (list of strings)."""
    if not text or not text.strip():
        raise ValueError("Cannot chunk an empty text")
    sentences = split_sentences(text)
    return [" ".join(group) for group in chunk_sentences(sentences, size, overlap)]


def chunk_exhibits(exhibits, size=120, overlap=30):
    """Turn the exhibits DataFrame into a passages DataFrame.

    One row per passage: exhibit_id, lang, passage_id, text, n_words.
    ``passage_id`` looks like ``ibu_library_bs_p0``.
    """
    rows = []
    for exhibit in exhibits.itertuples(index=False):
        for i, passage in enumerate(chunk(exhibit.text, size, overlap)):
            rows.append(
                {
                    "exhibit_id": exhibit.id,
                    "lang": exhibit.lang,
                    "passage_id": f"{exhibit.id}_{exhibit.lang}_p{i}",
                    "text": passage,
                    "n_words": count_words(passage),
                }
            )
    return pd.DataFrame(rows, columns=["exhibit_id", "lang", "passage_id", "text", "n_words"])
