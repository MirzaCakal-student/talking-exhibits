import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import analyze_errors as analysis


@pytest.fixture
def run_analysis(tmp_path, monkeypatch):
    gold = tmp_path / "val.csv"
    gold.write_text(
        "qid,label,lang,split\n"
        "q1,answerable,bs,val\n"
        "q2,unanswerable_plausible,en,val\n"
        "q3,out_of_scope,bs,val\n"
        "q4,out_of_scope,en,val\n"
        "q5,unanswerable_plausible,bs,val\n",
        encoding="utf-8",
    )
    predictions = tmp_path / "val_predictions.csv"
    output = tmp_path / "errors.csv"
    monkeypatch.setattr(sys, "argv", [
        "analyze_errors.py", "--gold", str(gold), "--predictions", str(predictions),
        "--out", str(output),
    ])
    return predictions, output


def write_predictions(path, systems):
    lines = ["qid,system,score,pred,gold"]
    qids = ["q3", "q1", "q5", "q4", "q2"]
    for system, predictions in systems.items():
        for qid, pred in zip(qids, predictions, strict=True):
            expected = "answer" if qid == "q1" else "refuse"
            score = "0.2" if system in {"b1_bm25", "b1b_e5", "m"} else ""
            lines.append(f"{qid},{system},{score},{pred},{expected}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_export_keeps_all_20_errors_across_systems_and_languages(run_analysis, capsys):
    predictions, output = run_analysis
    systems = {
        "b0": ["answer"] * 5,
        "b1_bm25": ["answer", "refuse", "answer", "refuse", "answer"],
        "b1b_e5": ["answer", "refuse", "refuse", "answer", "answer"],
        "b2": ["refuse", "refuse", "answer", "answer", "answer"],
        "m": ["answer", "refuse", "answer", "answer", "refuse"],
    }
    write_predictions(predictions, systems)

    analysis.main()

    table = pd.read_csv(output, dtype=str, keep_default_na=False)
    assert table.columns.tolist() == analysis.COLUMNS
    assert table.groupby("system").size().to_dict() == dict.fromkeys(systems, 4)
    assert set(table["gold"]) == {"answerable", "unanswerable_plausible", "out_of_scope"}
    assert table.query("system == 'b2' and qid == 'q1'").iloc[0]["pred"] == "refuse"
    assert table.query("system == 'b1_bm25' and qid == 'q2'").iloc[0]["pred"] == "answer"
    assert table[analysis.REVIEW_FIELDS].eq("").all().all()
    assert "Complete reviews: 0 (minimum 10, target 20)" in capsys.readouterr().out


def test_rerun_preserves_manual_review_and_rejects_stale_decision(run_analysis, capsys):
    predictions, output = run_analysis
    write_predictions(predictions, {"b2": ["refuse", "refuse", "refuse", "refuse", "answer"]})
    analysis.main()
    table = pd.read_csv(output, dtype=str, keep_default_na=False)
    table.loc[table.qid.eq("q1"), analysis.REVIEW_FIELDS] = [
        "retrieval promašio pasus", "Nedostaje odlomak", "Odlomak s odgovorom nije bio ponuđen.",
    ]
    table.to_csv(output, index=False)

    analysis.main()
    assert pd.read_csv(output, dtype=str, keep_default_na=False).equals(table)
    assert "Complete reviews: 1" in capsys.readouterr().out

    write_predictions(predictions, {"b2": ["refuse", "answer", "refuse", "refuse", "answer"]})
    with pytest.raises(SystemExit) as error:
        analysis.main()
    assert error.value.code == 1
    assert "annotated decisions changed for [('q1', 'b2')]" in capsys.readouterr().err
    assert pd.read_csv(output, dtype=str, keep_default_na=False).equals(table)


def test_rejects_invalid_category_without_overwriting(run_analysis, capsys):
    predictions, output = run_analysis
    write_predictions(predictions, {"b0": ["answer"] * 5})
    analysis.main()
    table = pd.read_csv(output, dtype=str, keep_default_na=False)
    table.loc[0, "kategorija"] = "unknown"
    table.to_csv(output, index=False)

    with pytest.raises(SystemExit) as error:
        analysis.main()
    assert error.value.code == 1
    assert "invalid category for qid(s) ['q2']" in capsys.readouterr().err
    assert pd.read_csv(output, dtype=str, keep_default_na=False).equals(table)


def test_incomplete_predictions_do_not_create_report(run_analysis, capsys):
    predictions, output = run_analysis
    predictions.write_text("qid,system,score,pred\nq1,b0,,answer\n", encoding="utf-8")

    with pytest.raises(SystemExit) as error:
        analysis.main()
    assert error.value.code == 1
    assert "missing=" in capsys.readouterr().err
    assert not output.exists()


def test_perfect_predictions_write_only_the_header(run_analysis):
    predictions, output = run_analysis
    write_predictions(predictions, {"m": ["refuse", "answer", "refuse", "refuse", "refuse"]})

    analysis.main()
    analysis.main()

    assert output.read_text(encoding="utf-8").splitlines() == [",".join(analysis.COLUMNS)]
