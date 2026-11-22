"""Validation and qid alignment checks using temporary test inputs."""

import json
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import evaluate_all as ea


@pytest.fixture
def gold():
    return pd.DataFrame({
        "qid": [f"q{i:04d}" for i in range(1, 7)],
        "label": [
            "answerable", "answerable",
            "unanswerable_plausible", "unanswerable_plausible",
            "out_of_scope", "out_of_scope",
        ],
        "lang": ["bs", "en"] * 3,
        "split": ["val"] * 6,
    })


@pytest.fixture
def predictions(gold):
    return pd.DataFrame({
        "qid": gold.qid,
        "system": ["b1_bm25"] * 6,
        "score": ["0", "1", "2", "3", "4", "5"],
        "pred": ["answer", "refuse", "refuse", "answer", "refuse", "refuse"],
    })


def write_csv(tmp_path, name, frame):
    path = tmp_path / name
    frame.to_csv(path, index=False)
    return path


@pytest.mark.parametrize("with_split", [True, False])
def test_valid_gold_preserves_existing_minimal_format(tmp_path, gold, with_split):
    frame = gold if with_split else gold.drop(columns="split")
    path = write_csv(tmp_path, "val.csv", frame)

    pd.testing.assert_frame_equal(
        ea.read_gold(path), gold[["qid", "label", "lang"]],
    )


@pytest.mark.parametrize("splits", [
    ["train", "train"],
    ["test", "test"],
    ["val", "train"],
    ["val", "test"],
    ["val", ""],
    ["val", "dev"],
    ["val", "VAL"],
    ["val", " val"],
    ["val", "val "],
])
def test_non_validation_split_values_are_rejected(tmp_path, gold, splits):
    frame = gold.iloc[:2].copy()
    frame["split"] = splits
    path = write_csv(tmp_path, "val.csv", frame)

    with pytest.raises(ValueError, match="split.*val"):
        ea.read_gold(path)


@pytest.mark.parametrize("qid", ["q0001", "", " \t"])
def test_duplicate_or_blank_gold_qids_are_rejected(tmp_path, gold, qid):
    gold.loc[1, "qid"] = qid
    path = write_csv(tmp_path, "val.csv", gold)

    with pytest.raises(ValueError, match="qids must be nonempty and unique"):
        ea.read_gold(path)


@pytest.mark.parametrize("column, value", [("label", "unknown"), ("lang", "fr")])
def test_invalid_gold_labels_or_languages_are_rejected(tmp_path, gold, column, value):
    gold.loc[0, column] = value
    path = write_csv(tmp_path, "val.csv", gold)

    with pytest.raises(ValueError, match="Invalid validation labels or languages"):
        ea.read_gold(path)


def test_missing_gold_column_and_empty_gold_are_rejected(tmp_path, gold):
    path = write_csv(tmp_path, "val.csv", gold.drop(columns="label"))
    with pytest.raises(ValueError, match="lacks columns.*label"):
        ea.read_gold(path)

    write_csv(tmp_path, "val.csv", gold.iloc[:0])
    with pytest.raises(ValueError, match="qids must be nonempty and unique"):
        ea.read_gold(path)


@pytest.mark.parametrize("name", ["train.csv", "test.csv"])
def test_non_validation_filename_is_rejected_before_reading(tmp_path, monkeypatch, name):
    def unexpected_read(*args, **kwargs):
        pytest.fail("Non-validation filenames must be rejected before CSV access")

    monkeypatch.setattr(ea.pd, "read_csv", unexpected_read)
    with pytest.raises(ValueError, match="named val.csv"):
        ea.read_gold(tmp_path / name)


def test_missing_input_files_are_reported(tmp_path):
    with pytest.raises(FileNotFoundError, match="Validation CSV not found"):
        ea.read_gold(tmp_path / "val.csv")
    with pytest.raises(FileNotFoundError, match="No prediction files match"):
        ea.read_predictions(str(tmp_path / "val_predictions_*.csv"), {"q0001"})


def test_multiple_systems_allow_shared_qids_and_empty_b0_scores(tmp_path, gold, predictions):
    b0 = predictions.assign(system="b0", score="", pred="answer")
    write_csv(tmp_path, "val_predictions_b0.csv", b0)
    write_csv(
        tmp_path, "val_predictions_b1.csv",
        predictions.assign(threshold="2.5", gold=["answer", "answer"] + ["refuse"] * 4),
    )

    loaded = ea.read_predictions(str(tmp_path / "val_predictions_*.csv"), set(gold.qid))

    assert loaded.columns.tolist() == ["qid", "system", "score", "pred"]
    assert len(loaded) == 12
    assert set(loaded.system) == {"b0", "b1_bm25"}
    assert (loaded.loc[loaded.system == "b0", "score"] == "").all()


@pytest.mark.parametrize("across_files", [False, True])
def test_duplicate_prediction_pairs_are_rejected(tmp_path, gold, predictions, across_files):
    if across_files:
        write_csv(tmp_path, "predictions_a.csv", predictions)
        write_csv(tmp_path, "predictions_b.csv", predictions.iloc[:1])
    else:
        write_csv(tmp_path, "predictions_a.csv", pd.concat([predictions, predictions.iloc[:1]]))

    with pytest.raises(ValueError, match=r"Duplicate \(system, qid\)"):
        ea.read_predictions(str(tmp_path / "predictions_*.csv"), set(gold.qid))


@pytest.mark.parametrize("case, message", [
    ("missing", r"missing=\['q0006'\]"),
    ("unexpected", r"extra=\['q9999'\]"),
    ("whitespace", r"missing=\['q0001'\].*extra=\['q0001 '\]"),
])
def test_prediction_qid_coverage_is_exact(tmp_path, gold, predictions, case, message):
    if case == "missing":
        predictions = predictions.iloc[:-1]
    elif case == "unexpected":
        extra = predictions.iloc[:1].assign(qid="q9999")
        predictions = pd.concat([predictions, extra])
    else:
        predictions.loc[0, "qid"] = "q0001 "
    path = write_csv(tmp_path, "predictions.csv", predictions)

    with pytest.raises(ValueError, match=message):
        ea.read_predictions(str(path), set(gold.qid))


def test_qid_coverage_is_checked_for_each_system(tmp_path, gold, predictions):
    incomplete = predictions.iloc[:-1].assign(system="b0", score="", pred="answer")
    path = write_csv(tmp_path, "predictions.csv", pd.concat([predictions, incomplete]))

    with pytest.raises(ValueError, match=r"b0:.*missing=\['q0006'\]"):
        ea.read_predictions(str(path), set(gold.qid))


@pytest.mark.parametrize("label", ["answerable", "", "REFUSE"])
def test_invalid_prediction_labels_are_rejected(tmp_path, gold, predictions, label):
    predictions.loc[0, "pred"] = label
    path = write_csv(tmp_path, "predictions.csv", predictions)

    with pytest.raises(ValueError, match="expected answer/refuse"):
        ea.read_predictions(str(path), set(gold.qid))


@pytest.mark.parametrize("column, value, message", [
    ("qid", "", "must predict every validation qid exactly once"),
    ("qid", " \t", "must predict every validation qid exactly once"),
    ("system", "", "invalid system"),
    ("system", " \t", "invalid system"),
])
def test_blank_prediction_identifiers_are_rejected(tmp_path, gold, predictions, column, value, message):
    if column == "system":
        predictions[column] = value
    else:
        predictions.loc[0, column] = value
    path = write_csv(tmp_path, "predictions.csv", predictions)

    with pytest.raises(ValueError, match=message):
        ea.read_predictions(str(path), set(gold.qid))


@pytest.mark.parametrize("score, message", [
    ("invalid", "nonnumeric score"),
    ("nan", "score must be finite"),
    ("inf", "score must be finite"),
])
def test_invalid_scores_are_rejected(tmp_path, gold, predictions, score, message):
    predictions.loc[0, "score"] = score
    path = write_csv(tmp_path, "predictions.csv", predictions)

    with pytest.raises(ValueError, match=message):
        ea.read_predictions(str(path), set(gold.qid))


def test_missing_prediction_column_and_empty_predictions_are_rejected(tmp_path, gold, predictions):
    path = write_csv(tmp_path, "predictions.csv", predictions.drop(columns="score"))
    with pytest.raises(ValueError, match="missing columns.*score"):
        ea.read_predictions(str(path), set(gold.qid))

    write_csv(tmp_path, "predictions.csv", predictions.iloc[:0])
    with pytest.raises(ValueError, match="empty predictions"):
        ea.read_predictions(str(path), set(gold.qid))


def test_shuffled_predictions_preserve_alignment_and_seeded_report(tmp_path, gold, predictions):
    gold_path = write_csv(tmp_path, "val.csv", gold)
    shuffled = predictions.iloc[[4, 1, 5, 0, 3, 2]]
    pred_path = write_csv(tmp_path, "predictions.csv", shuffled)
    loaded_gold = ea.read_gold(gold_path)
    loaded_pred = ea.read_predictions(str(pred_path), set(loaded_gold.qid))

    report = ea.calculate(loaded_gold, loaded_pred, bootstrap=100, seed=3004)
    assert report == ea.calculate(loaded_gold, predictions, bootstrap=100, seed=3004)
    assert report == ea.calculate(loaded_gold, loaded_pred, bootstrap=100, seed=3004)
    assert report["seed"] == 3004
    assert report["dataset"] == "validation"
    system = report["systems"]["b1_bm25"]
    overall = system["overall"]
    assert (overall["tp"], overall["fp"], overall["tn"], overall["fn"]) == (3, 1, 1, 1)
    assert overall["n"] == 6
    assert overall["precision"] == overall["recall"] == overall["f1"] == 0.75
    assert overall["false_refusal_rate"] == 0.5
    assert overall["macro_f1"] == 0.625
    assert system["by_language"]["bs"]["f1"] == 1
    assert system["by_language"]["en"]["f1"] == 0.5
    assert system["by_gold_class"]["out_of_scope"]["correct_decision_rate"] == 1
    assert overall["confusion"] == {
        "answerable": {"answer": 1, "refuse": 1},
        "unanswerable_plausible": {"answer": 1, "refuse": 1},
        "out_of_scope": {"answer": 0, "refuse": 2},
    }
    for stats in [overall, *system["by_language"].values()]:
        low, high = stats["refuse_f1_ci95"]
        assert 0 <= low <= high <= 1
    json.dumps(report, allow_nan=False)


def test_report_preserves_na_when_no_answerable_questions_exist(gold, predictions):
    report = ea.calculate(gold.iloc[4:5], predictions.iloc[4:5], bootstrap=10, seed=3004)
    system = report["systems"]["b1_bm25"]
    assert system["overall"]["false_refusal_rate"] is None
    assert set(system["by_language"]) == {"bs"}
    assert set(system["by_gold_class"]) == {"out_of_scope"}
    assert system["overall"]["refuse_f1_ci95"] == [1, 1]
    markdown = ea.render_markdown(report)
    assert markdown.startswith("# Validation evaluation\n")
    assert "| b1_bm25 | all | 1 | 1.000 | 1.000 | 1.000 | [1.000, 1.000] | N/A |" in markdown
    assert "## Three-class gold × binary prediction confusion" in markdown


@pytest.mark.parametrize("split", ["train", "test"])
def test_cli_rejects_wrong_split_before_loading_predictions(tmp_path, gold, monkeypatch, capsys, split):
    path = write_csv(tmp_path, "val.csv", gold.assign(split=split))
    out = tmp_path / "output"
    monkeypatch.setattr(sys, "argv", ["evaluate_all.py", "--gold", str(path), "--out", str(out)])

    def unexpected_predictions(*args):
        pytest.fail("Invalid gold splits must fail before prediction loading")

    monkeypatch.setattr(ea, "read_predictions", unexpected_predictions)
    with pytest.raises(SystemExit) as error:
        ea.main()

    assert error.value.code == 1
    assert "ERROR:" in capsys.readouterr().err
    assert not out.exists()


def test_cli_reports_missing_predictions_without_writing_outputs(tmp_path, gold, predictions, monkeypatch, capsys):
    gold_path = write_csv(tmp_path, "val.csv", gold)
    pred_path = write_csv(tmp_path, "predictions.csv", predictions.iloc[:-1])
    out = tmp_path / "output"
    monkeypatch.setattr(sys, "argv", [
        "evaluate_all.py", "--gold", str(gold_path),
        "--predictions", str(pred_path), "--out", str(out),
    ])

    with pytest.raises(SystemExit) as error:
        ea.main()

    assert error.value.code == 1
    assert "missing=['q0006']" in capsys.readouterr().err
    assert not out.exists()


@pytest.mark.parametrize("stale_gold", [False, True])
def test_cli_checks_prediction_gold_by_qid(tmp_path, gold, predictions, monkeypatch, capsys, stale_gold):
    gold_path = write_csv(tmp_path, "val.csv", gold)
    frame = predictions.assign(gold=["answer", "answer", "refuse", "refuse", "refuse", "refuse"])
    if stale_gold:
        frame.loc[0, "gold"] = "refuse"
    pred_path = write_csv(tmp_path, "predictions.csv", frame.iloc[::-1])
    out = tmp_path / "output"
    monkeypatch.setattr(sys, "argv", [
        "evaluate_all.py", "--gold", str(gold_path),
        "--predictions", str(pred_path), "--out", str(out), "--bootstrap", "10",
    ])

    if stale_gold:
        with pytest.raises(SystemExit) as error:
            ea.main()
        assert error.value.code == 1
        assert "predictions.csv: gold decisions disagree with validation labels for qids: ['q0001']" in capsys.readouterr().err
        assert not out.exists()
    else:
        ea.main()
        report = json.loads((out / "metrics_val.json").read_text(encoding="utf-8"))
        assert report["systems"]["b1_bm25"]["overall"]["n"] == len(gold)
