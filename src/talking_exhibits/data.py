"""Step 1: load the exhibit texts and the question set, and check their format.

Every later step (chunking, retrieval, evaluation) trusts these DataFrames.
So we check the fields here and fail with one clear error, instead of a
confusing error three steps later (same idea as ``radar/collect.py`` in Lab 1).
"""

import json
from pathlib import Path

import pandas as pd

# One exhibit file = one language version of one exhibit,
# e.g. data/exhibits/ibu_library_bs.json
EXHIBIT_FIELDS = ["id", "title", "lang", "text", "sources"]

# Columns of data/questions/questions.csv (HANDOFF.md, section 5.2).
QUESTION_COLUMNS = [
    "qid",
    "exhibit_id",
    "lang",
    "question",
    "label",
    "answer_text",
    "answer_start",
    "author",
    "checked_by",
    "source",
    "split",
]

LANGS = ["bs", "en"]
LABELS = ["answerable", "unanswerable_plausible", "out_of_scope"]


def load_exhibits(exhibits_dir):
    """Read every ``*.json`` file in ``exhibits_dir`` into one DataFrame.

    Returns one row per (exhibit id, language) with the columns in
    ``EXHIBIT_FIELDS``. Raises ``ValueError`` that names the file and the
    problem if a file is malformed.
    """
    exhibits_dir = Path(exhibits_dir)
    if not exhibits_dir.is_dir():
        raise ValueError(f"Exhibit folder not found: {exhibits_dir}")

    files = sorted(exhibits_dir.glob("*.json"))
    if not files:
        raise ValueError(f"No *.json exhibit files in {exhibits_dir}")

    rows = []
    for path in files:
        with open(path, encoding="utf-8") as f:
            exhibit = json.load(f)
        _check_exhibit(exhibit, path.name)
        rows.append({field: exhibit[field] for field in EXHIBIT_FIELDS})

    exhibits = pd.DataFrame(rows, columns=EXHIBIT_FIELDS)

    # The same exhibit may appear once per language, never twice in one language.
    duplicated = exhibits.duplicated(subset=["id", "lang"])
    if duplicated.any():
        pairs = exhibits.loc[duplicated, ["id", "lang"]].values.tolist()
        raise ValueError(f"Duplicate (id, lang) in exhibits: {pairs}")

    return exhibits


def _check_exhibit(exhibit, filename):
    """Check one exhibit dictionary; raise ValueError with the file name."""
    if not isinstance(exhibit, dict):
        raise ValueError(f"{filename}: expected a JSON object, got {type(exhibit).__name__}")

    missing = [field for field in EXHIBIT_FIELDS if field not in exhibit]
    if missing:
        raise ValueError(f"{filename}: missing field(s) {missing}")

    for field in ["id", "title", "text"]:
        if not isinstance(exhibit[field], str) or not exhibit[field].strip():
            raise ValueError(f"{filename}: field '{field}' must be a non-empty string")

    if exhibit["lang"] not in LANGS:
        raise ValueError(f"{filename}: lang must be one of {LANGS}, got {exhibit['lang']!r}")

    sources = exhibit["sources"]
    if not isinstance(sources, list) or not sources:
        raise ValueError(f"{filename}: 'sources' must be a non-empty list of URLs")


def load_questions(path):
    """Read the question CSV into a DataFrame of strings.

    Empty cells become "" (not NaN), so later steps always get a string.
    Only the basic format is checked here (columns, lang, label, unique qid).
    The deeper checks (answer offsets, checked_by != author) live in
    ``scripts/validate_questions.py``.
    """
    path = Path(path)
    if not path.is_file():
        raise ValueError(f"Question file not found: {path}")

    questions = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8")

    missing = [col for col in QUESTION_COLUMNS if col not in questions.columns]
    if missing:
        raise ValueError(f"{path.name}: missing column(s) {missing}")

    bad_lang = questions.loc[~questions["lang"].isin(LANGS), "qid"].tolist()
    if bad_lang:
        raise ValueError(f"{path.name}: lang must be one of {LANGS}; bad qid(s): {bad_lang[:10]}")

    bad_label = questions.loc[~questions["label"].isin(LABELS), "qid"].tolist()
    if bad_label:
        raise ValueError(f"{path.name}: label must be one of {LABELS}; bad qid(s): {bad_label[:10]}")

    duplicated = questions.loc[questions["qid"].duplicated(), "qid"].tolist()
    if duplicated:
        raise ValueError(f"{path.name}: duplicate qid(s): {duplicated[:10]}")

    return questions


def get_exhibit_text(exhibits, exhibit_id, lang):
    """Return the text of one exhibit in one language."""
    match = exhibits[(exhibits["id"] == exhibit_id) & (exhibits["lang"] == lang)]
    if match.empty:
        raise ValueError(f"No exhibit with id={exhibit_id!r} and lang={lang!r}")
    return match.iloc[0]["text"]
