"""Tests for the data tools: fill_answer_starts.py, build_dataset.py, compute_kappa.py.

All data here is made up; no real exhibits or questions are used.

Run:
    uv run pytest tests/test_data_tools.py -v
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import build_dataset as bd  # noqa: E402
import compute_kappa as ck  # noqa: E402
import fill_answer_starts as fa  # noqa: E402
import validate_questions as vq  # noqa: E402

TEXTS = {
    ("demo_library", "bs"): "Biblioteka ima 20.000 knjiga. Biblioteka je otvorena 2010.",
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
        "answer_start": "",
        "author": "tarik",
        "checked_by": "kerim",
        "source": "human",
        "split": "",
    }
    row.update(changes)
    return row


def make_df(*rows) -> pd.DataFrame:
    return pd.DataFrame(list(rows), columns=vq.REQUIRED_COLUMNS, dtype=str)


# ---------------------------------------------------------- fill_answer_starts ----


def test_fill_writes_the_character_offset():
    df, filled, messages = fa.fill_answer_starts(make_df(make_row()), TEXTS)
    assert filled == 1
    assert df.loc[0, "answer_start"] == "15"  # "Biblioteka ima " has 15 characters
    assert messages == []
    assert vq.check_answer_spans(df, TEXTS) == []  # the validator agrees


def test_fill_uses_the_text_in_the_question_language():
    df, _, _ = fa.fill_answer_starts(make_df(make_row(lang="en", answer_text="20,000")), TEXTS)
    assert df.loc[0, "answer_start"] == "18"


def test_fill_keeps_existing_offsets_and_skips_unanswerable():
    df = make_df(
        make_row(answer_start="99"),
        make_row(qid="q0002", label="out_of_scope", answer_text="", question="Koliko je sati?"),
    )
    new_df, filled, _ = fa.fill_answer_starts(df, TEXTS)
    assert filled == 0
    assert new_df.loc[0, "answer_start"] == "99"
    assert new_df.loc[1, "answer_start"] == ""


def test_fill_reports_missing_answer_and_repeated_answer():
    df = make_df(
        make_row(answer_text="30.000"),
        make_row(qid="q0002", answer_text="Biblioteka", question="Šta?"),
    )
    new_df, filled, messages = fa.fill_answer_starts(df, TEXTS)
    assert filled == 1  # only the repeated one gets an offset (the first occurrence)
    assert new_df.loc[1, "answer_start"] == "0"
    assert any("not in the exhibit text" in m for m in messages)
    assert any("appears 2 times" in m for m in messages)


def test_fill_does_not_change_the_input():
    df = make_df(make_row())
    fa.fill_answer_starts(df, TEXTS)
    assert df.loc[0, "answer_start"] == ""


# --------------------------------------------------------------- build_dataset ----

EXHIBITS = [f"ex{i:02d}" for i in range(12)]


def test_assignment_is_reproducible_and_complete():
    first = bd.assign_exhibits(EXHIBITS, n_val=2, n_test=4)
    second = bd.assign_exhibits(list(reversed(EXHIBITS)), n_val=2, n_test=4)
    assert first == second  # same seed, same result, row order does not matter
    assert sorted(first) == EXHIBITS
    counts = pd.Series(first).value_counts().to_dict()
    assert counts == {"train": 6, "test": 4, "val": 2}


def test_assignment_needs_enough_exhibits():
    with pytest.raises(ValueError):
        bd.assign_exhibits(["a", "b", "c"], n_val=1, n_test=2)


def test_one_exhibit_never_appears_in_two_splits():
    rows = [
        make_row(qid=f"q{i:04d}", exhibit_id=EXHIBITS[i % 12], lang="bs" if i % 2 else "en")
        for i in range(48)
    ]
    df = bd.apply_split(make_df(*rows), bd.assign_exhibits(EXHIBITS, 2, 4))
    splits_per_exhibit = df.groupby("exhibit_id")["split"].nunique()
    assert (splits_per_exhibit == 1).all()


def test_warnings_for_small_test_set_and_missing_labels():
    df = make_df(make_row(split="test"), make_row(qid="q0002", split="train"), make_row(qid="q0003", split="val"))
    warnings = bd.split_warnings(df, min_test=100)
    assert any("test set has 1 questions" in w for w in warnings)
    assert any("no 'out_of_scope'" in w for w in warnings)


def test_save_splits_writes_three_files(tmp_path):
    df = make_df(make_row(split="train"), make_row(qid="q0002", split="val"), make_row(qid="q0003", split="test"))
    paths = bd.save_splits(df, tmp_path)
    assert [p.name for p in paths] == ["train.csv", "val.csv", "test.csv"]
    val = pd.read_csv(tmp_path / "val.csv", dtype=str, keep_default_na=False)
    assert val["qid"].tolist() == ["q0002"]


# --------------------------------------------------------------- compute_kappa ----


def annotations(labels) -> pd.DataFrame:
    return pd.DataFrame({"qid": [f"q{i:04d}" for i in range(len(labels))], "label": labels})


def test_kappa_matches_a_hand_calculation():
    # A: ans, ans, oos, oos     B: ans, oos, oos, oos
    # p_o = 3/4 = 0.75
    # p_e = P(A=ans)P(B=ans) + P(A=oos)P(B=oos) = 0.5*0.25 + 0.5*0.75 = 0.5
    # kappa = (0.75 - 0.5) / (1 - 0.5) = 0.5
    a = annotations(["answerable", "answerable", "out_of_scope", "out_of_scope"])
    b = annotations(["answerable", "out_of_scope", "out_of_scope", "out_of_scope"])
    report = ck.agreement_report(ck.align(a, b))
    assert report["agreement_3"] == pytest.approx(0.75)
    assert report["kappa_3"] == pytest.approx(0.5)
    assert report["disagreements"]["qid"].tolist() == ["q0001"]


def test_binary_kappa_ignores_plausible_vs_out_of_scope():
    # Different labels, but both mean "refuse", so they agree on the decision.
    a = annotations(["answerable", "unanswerable_plausible", "answerable", "out_of_scope"])
    b = annotations(["answerable", "out_of_scope", "answerable", "unanswerable_plausible"])
    report = ck.agreement_report(ck.align(a, b))
    assert report["agreement_3"] == pytest.approx(0.5)
    assert report["agreement_2"] == pytest.approx(1.0)
    assert report["kappa_2"] == pytest.approx(1.0)


def test_kappa_needs_the_same_questions():
    with pytest.raises(ValueError):
        ck.align(annotations(["answerable"]), annotations(["answerable", "out_of_scope"]))


def test_load_annotations_rejects_unknown_label(tmp_path):
    path = tmp_path / "x.csv"
    path.write_text("qid,label\nq0001,maybe\n", encoding="utf-8")
    with pytest.raises(ValueError):
        ck.load_annotations(path)
