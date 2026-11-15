"""Tests for scripts/validate_questions.py.

Each test builds a tiny, made-up question set in memory and checks that the
validator reports exactly the problem we planted (or nothing for valid data).
No real exhibit texts or questions are used here.

Run:
    uv run pytest
"""

import json
import sys
from pathlib import Path

import pandas as pd

# scripts/ is not a package, so add it to the import path.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import validate_questions as vq  # noqa: E402

# One fake exhibit in two languages. "20.000" starts at index 15, "20,000" at 18.
EXHIBIT_TEXTS = {
    ("demo_library", "bs"): "Biblioteka ima 20.000 knjiga.",
    ("demo_library", "en"): "The library holds 20,000 books.",
}


def make_row(**changes) -> dict:
    """A valid answerable question; keyword arguments override single fields."""
    row = {
        "qid": "q0001",
        "exhibit_id": "demo_library",
        "lang": "bs",
        "question": "Koliko knjiga ima biblioteka?",
        "label": "answerable",
        "answer_text": "20.000",
        "answer_start": "15",
        "author": "tarik",
        "checked_by": "kerim",
        "source": "human",
        "split": "",
    }
    row.update(changes)
    return row


def make_df(*rows) -> pd.DataFrame:
    """Build a DataFrame with the schema columns, all values as text."""
    return pd.DataFrame(list(rows), columns=vq.REQUIRED_COLUMNS, dtype=str)


def test_valid_questions_have_no_errors():
    df = make_df(
        make_row(),
        make_row(qid="q0002", lang="en", question="How many books does the library hold?",
                 answer_text="20,000", answer_start="18", author="mirza", checked_by="tarik"),
        make_row(qid="q0003", question="Ko je projektovao biblioteku?",
                 label="unanswerable_plausible", answer_text="", answer_start=""),
    )
    assert vq.validate(df, EXHIBIT_TEXTS) == []


def test_empty_question_set_is_valid():
    assert vq.validate(make_df(), EXHIBIT_TEXTS) == []


def test_missing_column_is_reported_and_stops_other_checks():
    df = make_df(make_row()).drop(columns=["source"])
    assert vq.validate(df, EXHIBIT_TEXTS) == ["missing column: source"]


def test_bad_and_duplicate_qids():
    df = make_df(
        make_row(qid="Q1"),
        make_row(qid="q0002", question="Prvo pitanje?", label="out_of_scope", answer_text="", answer_start=""),
        make_row(qid="q0002", question="Drugo pitanje?", label="out_of_scope", answer_text="", answer_start=""),
    )
    errors = vq.check_qids(df)
    assert "Q1: qid must look like q0001" in errors
    assert "q0002: qid is used more than once" in errors


def test_values_outside_the_allowed_lists():
    df = make_df(make_row(exhibit_id="demo_museum", lang="de", label="unanswerable",
                          source="chatgpt", split="dev", question="  "))
    errors = vq.check_allowed_values(df, EXHIBIT_TEXTS)
    assert len(errors) == 6
    assert any("unknown exhibit_id 'demo_museum'" in e for e in errors)
    assert any("got 'unanswerable'" in e for e in errors)


def test_author_cannot_check_own_question():
    df = make_df(make_row(author="tarik", checked_by="tarik"))
    assert vq.check_reviewers(df) == ["q0001: checked_by must be a different member than author"]


def test_reviewer_must_be_team_member():
    df = make_df(make_row(author="ana"))
    assert vq.check_reviewers(df) == ["q0001: author must be one of ['kerim', 'mirza', 'tarik'], got 'ana'"]


def test_wrong_answer_start_points_to_correct_position():
    df = make_df(make_row(answer_start="14"))
    errors = vq.check_answer_spans(df, EXHIBIT_TEXTS)
    assert len(errors) == 1
    assert "not at position 14" in errors[0]
    assert "found at position 15" in errors[0]


def test_answer_not_in_text():
    df = make_df(make_row(answer_text="30.000"))
    errors = vq.check_answer_spans(df, EXHIBIT_TEXTS)
    assert "not found anywhere in the text" in errors[0]


def test_answer_is_checked_in_the_same_language():
    # "20.000" (Bosnian format) is not in the English text.
    df = make_df(make_row(lang="en"))
    errors = vq.check_answer_spans(df, EXHIBIT_TEXTS)
    assert len(errors) == 1


def test_missing_language_version_of_exhibit():
    only_bs = {("demo_library", "bs"): EXHIBIT_TEXTS[("demo_library", "bs")]}
    df = make_df(make_row(lang="en", answer_text="20,000", answer_start="18"))
    assert vq.check_answer_spans(df, only_bs) == ["q0001: exhibit 'demo_library' has no 'en' text"]


def test_answerable_needs_an_answer():
    df = make_df(make_row(answer_text="", answer_start=""))
    assert vq.check_answer_spans(df, EXHIBIT_TEXTS) == [
        "q0001: answerable question needs answer_text and answer_start"
    ]


def test_answer_start_must_be_a_number():
    df = make_df(make_row(answer_start="abc"))
    assert "whole number" in vq.check_answer_spans(df, EXHIBIT_TEXTS)[0]


def test_unanswerable_must_not_have_an_answer():
    df = make_df(make_row(label="unanswerable_plausible", answer_text="Ahmed", answer_start="3"))
    assert vq.check_answer_spans(df, EXHIBIT_TEXTS) == [
        "q0001: answer_text and answer_start must be empty for label 'unanswerable_plausible'"
    ]


def test_duplicate_question_ignores_case_and_spaces():
    df = make_df(
        make_row(),
        make_row(qid="q0002", question="  koliko  KNJIGA ima biblioteka?"),
    )
    assert vq.check_duplicates(df) == ["q0002: duplicate of q0001 (same question for 'demo_library')"]


def test_load_files_from_disk(tmp_path):
    # Write one exhibit file and one CSV into pytest's temporary folder.
    exhibits_dir = tmp_path / "exhibits"
    exhibits_dir.mkdir()
    exhibit = {"id": "demo_library", "title": "Demo", "lang": "bs",
               "text": EXHIBIT_TEXTS[("demo_library", "bs")], "sources": []}
    (exhibits_dir / "demo_library_bs.json").write_text(json.dumps(exhibit), encoding="utf-8")
    csv_path = tmp_path / "questions.csv"
    make_df(make_row()).to_csv(csv_path, index=False)

    df = vq.load_questions(csv_path)
    texts = vq.load_exhibit_texts(exhibits_dir)

    assert df.loc[0, "answer_start"] == "15"  # read as text, not as a number
    assert df.loc[0, "split"] == ""  # empty cell stays empty, not NaN
    assert vq.validate(df, texts) == []
