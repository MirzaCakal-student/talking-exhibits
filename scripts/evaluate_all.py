
"""Evaluate validation-set baseline predictions only (K-4).

Run: uv run python scripts/evaluate_all.py
Expected prediction columns: qid,system,score,pred (answer/refuse).
Never load the held-out test set for threshold selection.
"""

from __future__ import annotations

import argparse
import glob
import json
import math
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

# The project currently uses [tool.uv] package = false.
sys.path.insert(0, str(ROOT / "src"))

from talking_exhibits.evaluate import (
    bootstrap_ci,
    confusion,
    false_refusal_rate,
    macro_f1,
    refuse_metrics,
)

LABELS = (
    "answerable",
    "unanswerable_plausible",
    "out_of_scope",
)
LANGS = ("bs", "en")


def read_gold(path: Path) -> pd.DataFrame:
    """Load and validate only the validation gold labels."""
    if path.name != "val.csv":
        raise ValueError(
            "Only a validation file named val.csv is allowed"
        )

    if not path.is_file():
        raise FileNotFoundError(
            f"Validation CSV not found: {path}"
        )

    gold = pd.read_csv(
        path, dtype=str, keep_default_na=False
    )

    required = {"qid", "label", "lang"}
    missing = required - set(gold.columns)

    if missing:
        raise ValueError(
            f"Validation CSV lacks columns: {sorted(missing)}"
        )

    if "split" in gold.columns:
        invalid_splits = sorted(set(gold["split"]) - {"val"})
        if invalid_splits:
            raise ValueError(
                "Validation CSV split must contain only 'val'; "
                f"invalid values: {invalid_splits}"
            )

    if (
        gold.empty
        or gold.qid.duplicated().any()
        or gold.qid.str.strip().eq("").any()
    ):
        raise ValueError(
            "Validation qids must be nonempty and unique"
        )

    if (
        not gold.label.isin(LABELS).all()
        or not gold.lang.isin(LANGS).all()
    ):
        raise ValueError(
            "Invalid validation labels or languages"
        )

    return gold[["qid", "label", "lang"]]


def read_predictions(
    pattern: str,
    valid_qids: set[str],
) -> pd.DataFrame:
    """Load prediction files and verify their qid coverage."""
    files = sorted(
        Path(item) for item in glob.glob(pattern)
    )

    if not files:
        raise FileNotFoundError(
            f"No prediction files match: {pattern}"
        )

    frames = []

    for path in files:
        frame = pd.read_csv(
            path, dtype=str, keep_default_na=False
        )

        required = {"qid", "system", "score", "pred"}
        missing = required - set(frame.columns)

        if missing:
            raise ValueError(
                f"{path.name}: missing columns: {sorted(missing)}"
            )

        if frame.empty:
            raise ValueError(
                f"{path.name}: empty predictions"
            )

        if (
            frame.system.str.strip().eq("").any()
            or not frame.pred.isin(
                ["answer", "refuse"]
            ).all()
        ):
            raise ValueError(
                f"{path.name}: invalid system or pred "
                "(expected answer/refuse)"
            )

        # Score is required as a column but may be empty
        # for baselines that do not produce confidence scores.
        for score in frame.score:
            if score:
                try:
                    numeric = float(score)
                except ValueError as exc:
                    raise ValueError(
                        f"{path.name}: nonnumeric score {score!r}"
                    ) from exc

                if not math.isfinite(numeric):
                    raise ValueError(
                        f"{path.name}: score must be finite"
                    )

        frames.append(
            frame[["qid", "system", "score", "pred"]]
        )

    predictions = pd.concat(
        frames, ignore_index=True
    )

    if predictions.duplicated(
        ["system", "qid"]
    ).any():
        raise ValueError(
            "Duplicate (system, qid) predictions"
        )

    # Every baseline must predict every validation question.
    for system, rows in predictions.groupby("system"):
        actual_qids = set(rows.qid)

        if actual_qids != valid_qids:
            missing = sorted(
                valid_qids - actual_qids
            )
            extra = sorted(
                actual_qids - valid_qids
            )

            raise ValueError(
                f"{system}: must predict every validation "
                f"qid exactly once; missing={missing[:5]}, "
                f"extra={extra[:5]}"
            )

    return predictions


def summarize(
    gold: list[str],
    pred: list[str],
    bootstrap: int,
    seed: int,
) -> dict:
    """Calculate evaluation metrics and their F1 confidence interval."""
    stats = refuse_metrics(gold, pred)

    stats["false_refusal_rate"] = (
        false_refusal_rate(gold, pred)
        if "answerable" in gold
        else None
    )

    stats["macro_f1"] = macro_f1(gold, pred)

    ci = bootstrap_ci(
        lambda g, p: refuse_metrics(g, p)["f1"],
        gold,
        pred,
        n=bootstrap,
        seed=seed,
    )

    stats["refuse_f1_ci95"] = [
        float(ci[0]),
        float(ci[1]),
    ]

    stats["confusion"] = confusion(gold, pred)

    return stats


def calculate(
    gold_df: pd.DataFrame,
    pred_df: pd.DataFrame,
    bootstrap: int,
    seed: int,
) -> dict:
    """Evaluate each system overall, by language and gold class."""
    report = {
        "dataset": "validation",
        "seed": seed,
        "bootstrap_samples": bootstrap,
        "systems": {},
    }

    for system, frame in pred_df.groupby(
        "system", sort=True
    ):
        # Align predictions using qid, not CSV row order.
        aligned = gold_df.merge(
            frame[["qid", "pred"]],
            on="qid",
            how="left",
            validate="one_to_one",
            sort=False,
        )

        gold = aligned.label.tolist()
        pred = aligned.pred.tolist()
        lang = aligned.lang.tolist()

        system_report = {
            "overall": summarize(
                gold, pred, bootstrap, seed
            ),
            "by_language": {},
            "by_gold_class": {},
        }

        for selected_lang in LANGS:
            indices = [
                i for i, value in enumerate(lang)
                if value == selected_lang
            ]

            if indices:
                system_report["by_language"][
                    selected_lang
                ] = summarize(
                    [gold[i] for i in indices],
                    [pred[i] for i in indices],
                    bootstrap,
                    seed,
                )

        for label in LABELS:
            indices = [
                i for i, actual in enumerate(gold)
                if actual == label
            ]

            if indices:
                expected = (
                    "answer"
                    if label == "answerable"
                    else "refuse"
                )

                correct = sum(
                    pred[i] == expected
                    for i in indices
                )

                system_report["by_gold_class"][label] = {
                    "n": len(indices),
                    "expected_decision": expected,
                    "correct_decision_rate": (
                        correct / len(indices)
                    ),
                }

        report["systems"][system] = system_report

    return report


def render_markdown(report: dict) -> str:
    """Create a report table suitable for the project paper."""
    lines = [
        "# Validation evaluation",
        "",
        (
            "Only validation data are evaluated; "
            "these are **not test-set results**."
        ),
        (
            f"Bootstrap: {report['bootstrap_samples']} "
            "question-level paired (gold/pred) draws, "
            f"seed {report['seed']}."
        ),
        "",
        (
            "| System | Language | N | Refuse precision | "
            "Refuse recall | Refuse F1 | 95% CI | "
            "False refusal rate | Macro-F1 |"
        ),
        (
            "| --- | --- | ---: | ---: | ---: | "
            "---: | --- | ---: | ---: |"
        ),
    ]

    for system, values in report["systems"].items():
        sections = [
            ("all", values["overall"]),
            *values["by_language"].items(),
        ]

        for language, stats in sections:
            low, high = stats["refuse_f1_ci95"]
            frr = stats["false_refusal_rate"]

            frr_text = (
                f"{frr:.3f}"
                if frr is not None
                else "N/A"
            )

            lines.append(
                f"| {system} | {language} | {stats['n']} | "
                f"{stats['precision']:.3f} | "
                f"{stats['recall']:.3f} | "
                f"{stats['f1']:.3f} | "
                f"[{low:.3f}, {high:.3f}] | "
                f"{frr_text} | "
                f"{stats['macro_f1']:.3f} |"
            )

    lines.extend([
        "",
        "## Results by gold class",
        "",
        "| System | Gold class | N | Correct decision rate |",
        "| --- | --- | ---: | ---: |",
    ])

    for system, values in report["systems"].items():
        for label, item in values[
            "by_gold_class"
        ].items():
            lines.append(
                f"| {system} | {label} | "
                f"{item['n']} | "
                f"{item['correct_decision_rate']:.3f} |"
            )

    lines.extend([
        "",
        "## Three-class gold × binary prediction confusion",
        "",
    ])

    for system, values in report["systems"].items():
        lines.extend([
            f"### {system}",
            "",
            "| Gold class | Answer | Refuse |",
            "| --- | ---: | ---: |",
        ])

        for label, row in values[
            "overall"
        ]["confusion"].items():
            lines.append(
                f"| {label} | "
                f"{row['answer']} | "
                f"{row['refuse']} |"
            )

        lines.append("")

    lines.append(
        "Confidence intervals are descriptive; "
        "question-level bootstrap does not account "
        "for exhibit clustering."
    )

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__
    )

    parser.add_argument(
        "--gold",
        type=Path,
        default=ROOT / "data/processed/val.csv",
    )
    parser.add_argument(
        "--predictions",
        default=str(
            ROOT / "results/val_predictions_*.csv"
        ),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "results",
    )
    parser.add_argument(
        "--bootstrap",
        type=int,
        default=1000,
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=3004,
    )

    args = parser.parse_args()

    if args.bootstrap < 1:
        parser.error(
            "--bootstrap must be at least 1"
        )

    try:
        gold = read_gold(args.gold)

        pred = read_predictions(
            args.predictions,
            set(gold.qid),
        )

        report = calculate(
            gold,
            pred,
            args.bootstrap,
            args.seed,
        )

        args.out.mkdir(
            parents=True,
            exist_ok=True,
        )

        (args.out / "metrics_val.json").write_text(
            json.dumps(
                report,
                indent=2,
                ensure_ascii=False,
            ) + "\n",
            encoding="utf-8",
        )

        (args.out / "metrics_val.md").write_text(
            render_markdown(report),
            encoding="utf-8",
        )

    except (
        OSError,
        ValueError,
        pd.errors.ParserError,
    ) as exc:
        parser.exit(1, f"ERROR: {exc}\n")

    print(
        f"OK: evaluated {len(report['systems'])} systems "
        f"on {len(gold)} validation questions"
    )
    print(
        f"Wrote {args.out / 'metrics_val.json'} "
        f"and {args.out / 'metrics_val.md'}"
    )


if __name__ == "__main__":
    main()
