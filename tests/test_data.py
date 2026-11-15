"""Tests for data.py: loading and format checks of exhibits and questions."""

import json
from pathlib import Path

import pytest

from talking_exhibits.data import (
    EXHIBIT_FIELDS,
    QUESTION_COLUMNS,
    get_exhibit_text,
    load_exhibits,
    load_questions,
)

FIXTURES = Path(__file__).parent / "fixtures"


def write_exhibit(folder, name="x_bs.json", **changes):
    """Write one valid exhibit file, with optional changed or removed fields."""
    exhibit = {
        "id": "x",
        "title": "Naslov",
        "lang": "bs",
        "text": "Neki tekst.",
        "sources": ["https://example.org"],
    }
    for key, value in changes.items():
        if value is None:
            del exhibit[key]
        else:
            exhibit[key] = value
    (folder / name).write_text(json.dumps(exhibit, ensure_ascii=False), encoding="utf-8")


def test_load_exhibits_reads_all_fixture_files():
    exhibits = load_exhibits(FIXTURES / "exhibits")
    assert list(exhibits.columns) == EXHIBIT_FIELDS
    assert len(exhibits) == 4  # 2 exhibits x 2 languages
    assert set(exhibits["lang"]) == {"bs", "en"}


def test_diacritics_survive_loading():
    exhibits = load_exhibits(FIXTURES / "exhibits")
    text = get_exhibit_text(exhibits, "lipa_library", "bs")
    assert "čitaonicu" in text and "Šarić" in text


def test_missing_field_names_the_file_and_field(tmp_path):
    write_exhibit(tmp_path, name="broken_bs.json", sources=None)
    with pytest.raises(ValueError, match=r"broken_bs\.json.*sources"):
        load_exhibits(tmp_path)


def test_wrong_language_is_rejected(tmp_path):
    write_exhibit(tmp_path, lang="hr")
    with pytest.raises(ValueError, match="lang must be one of"):
        load_exhibits(tmp_path)


def test_empty_text_is_rejected(tmp_path):
    write_exhibit(tmp_path, text="   ")
    with pytest.raises(ValueError, match="'text' must be a non-empty string"):
        load_exhibits(tmp_path)


def test_duplicate_id_and_language_is_rejected(tmp_path):
    write_exhibit(tmp_path, name="a.json")
    write_exhibit(tmp_path, name="b.json")
    with pytest.raises(ValueError, match="Duplicate"):
        load_exhibits(tmp_path)


def test_empty_folder_is_rejected(tmp_path):
    with pytest.raises(ValueError, match="No \\*.json"):
        load_exhibits(tmp_path)


def test_load_questions_reads_fixture():
    questions = load_questions(FIXTURES / "questions_val.csv")
    assert list(questions.columns) == QUESTION_COLUMNS
    assert len(questions) == 22
    # Empty cells are "" and not NaN.
    not_answerable = questions[questions["label"] != "answerable"]
    assert (not_answerable["answer_text"] == "").all()


def test_fixture_answer_offsets_point_at_the_answer():
    exhibits = load_exhibits(FIXTURES / "exhibits")
    questions = load_questions(FIXTURES / "questions_val.csv")
    for q in questions[questions["label"] == "answerable"].itertuples():
        text = get_exhibit_text(exhibits, q.exhibit_id, q.lang)
        start = int(q.answer_start)
        assert text[start : start + len(q.answer_text)] == q.answer_text


def test_missing_question_column_is_reported(tmp_path):
    path = tmp_path / "q.csv"
    path.write_text("qid,question\nq0001,Sta?\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing column"):
        load_questions(path)


def test_unknown_label_is_reported(tmp_path):
    header = ",".join(QUESTION_COLUMNS)
    row = "q0001,x,bs,Sta?,maybe,,,a,b,human,val"
    path = tmp_path / "q.csv"
    path.write_text(f"{header}\n{row}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="label must be one of"):
        load_questions(path)
