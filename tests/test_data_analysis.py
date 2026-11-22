"""Hand-counted analysis checks using fictional data in temporary folders."""

import json
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import data_analysis as da


def questions():
    return pd.DataFrame({
        "qid": ["q0001", "q0002", "q0003", "q0004"],
        "exhibit_id": ["demo"] * 4,
        "lang": ["bs", "bs", "bs", "en"],
        "question": ["Koliko knjiga ima?", "Sta pise?", "Šta piše?", "What is here?"],
        "label": ["answerable", "unanswerable_plausible", "answerable", "answerable"],
        "author": ["kerim"] * 4,
        "checked_by": [""] * 4,
        "source": [""] * 4,
        "split": [""] * 4,
    })


def test_jaccard_uses_unique_words_and_preserves_diacritics():
    assert da.jaccard("Šuma voda voda", "šuma kamen") == pytest.approx(1 / 3)
    assert da.jaccard("suma", "šuma") == 0
    assert da.jaccard("", "") == 0


def test_hand_counted_lengths_and_undefined_sample_sd():
    assert da.length_statistics("demo", [1, 2, 3]) == {
        "group": "demo", "n": 3, "mean": 2, "median": 2,
        "sample_sd": 1, "min": 1, "max": 3,
    }
    single = da.length_statistics("single", [5])
    assert pd.isna(single["sample_sd"])
    assert "N/A" in da.markdown_table(pd.DataFrame([single]))
    with pytest.raises(ValueError, match="empty lengths"):
        da.length_statistics("empty", [])


def test_character_absence_does_not_determine_writing_intent():
    frame = questions()
    assert da.diacritic_statistics(frame) == {
        "bs_questions": 3, "without_diacritics": 2, "intentional_omissions": None,
    }
    assert da.diacritic_statistics(frame, ["q0002"]) == {
        "bs_questions": 3, "without_diacritics": 2, "intentional_omissions": 1,
    }


@pytest.mark.parametrize("qids, message", [
    (["q9999"], "Unknown"),
    (["q0004"], "Bosnian"),
    (["q0003"], "contain no diacritics"),
    (["q0002", "q0002"], "Duplicate"),
])
def test_bad_omission_annotations_are_rejected(qids, message):
    with pytest.raises(ValueError, match=message):
        da.diacritic_statistics(questions(), qids)


def write_exhibits(directory):
    directory.mkdir()
    for lang, text in [("bs", "Šuma voda kamen."), ("en", "Forest water stone.")]:
        exhibit = {
            "id": "demo", "title": "Demo", "lang": lang, "text": text,
            "sources": ["https://example.org/demo"],
        }
        (directory / f"demo_{lang}.json").write_text(
            json.dumps(exhibit, ensure_ascii=False), encoding="utf-8",
        )


def test_unreviewed_report_is_preliminary_and_absent_class_is_not_zero_overlap(tmp_path):
    csv = tmp_path / "questions.csv"
    exhibits = tmp_path / "exhibits"
    out = tmp_path / "results"
    questions().to_csv(csv, index=False)
    write_exhibits(exhibits)

    da.analyze(csv, exhibits, out, intentional_qids=["q0002"])

    report = (out / "data_tables.md").read_text(encoding="utf-8")
    assert report.startswith("# Preliminary dataset analysis")
    assert "independent reviewer recorded: **0/4**" in report
    assert "| demo | 3 | 1 | 4 |" in report
    assert "| out_of_scope | 0 | N/A | N/A | N/A | N/A |" in report
    assert "**1/3 (33.3%)**" in report
    assert "All **4** split values are unassigned" in report
    assert "--preliminary --intentional-no-diacritics q0002" in report
    assert {p.name for p in (out / "figures").glob("*.png")} == {
        "questions_by_label_language.png", "question_lengths.png", "exhibit_lengths.png",
    }
    assert all(p.stat().st_size > 0 for p in (out / "figures").glob("*.png"))


def test_missing_question_language_text_is_rejected_before_outputs(tmp_path):
    csv = tmp_path / "questions.csv"
    exhibits = tmp_path / "exhibits"
    questions().to_csv(csv, index=False)
    write_exhibits(exhibits)
    (exhibits / "demo_en.json").unlink()
    out = tmp_path / "results"

    with pytest.raises(ValueError, match="missing exhibit text"):
        da.analyze(csv, exhibits, out)
    assert not out.exists()
