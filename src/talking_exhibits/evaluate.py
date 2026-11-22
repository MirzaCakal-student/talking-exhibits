
"""Metrics for binary refusal decisions in Talking Exhibits.

Gold: answerable, unanswerable_plausible, out_of_scope.
Prediction: answer or refuse. Refuse is the positive class.
"""

from __future__ import annotations

import math
import random
from collections.abc import Callable, Iterable, Sequence
from itertools import groupby
from numbers import Real

from sklearn.metrics import roc_auc_score

GOLD_LABELS = (
    "answerable",
    "unanswerable_plausible",
    "out_of_scope",
)
PREDICTIONS = ("answer", "refuse")
LANGUAGES = ("bs", "en")


def _prepare(
    gold: Iterable[str],
    pred: Iterable[str],
    *,
    languages: Sequence[str] | None = None,
    language: str | None = None,
    gold_class: str | None = None,
) -> tuple[list[str], list[str]]:
    """Check aligned inputs and apply optional filters."""
    gold = list(gold)
    pred = list(pred)

    if not gold or len(gold) != len(pred):
        raise ValueError(
            "gold and pred must be nonempty and have equal lengths"
        )

    if any(label not in GOLD_LABELS for label in gold):
        raise ValueError(
            f"gold labels must be one of {GOLD_LABELS}"
        )

    if any(label not in PREDICTIONS for label in pred):
        raise ValueError(
            f"predictions must be one of {PREDICTIONS}"
        )

    if gold_class is not None and gold_class not in GOLD_LABELS:
        raise ValueError(
            f"gold_class must be one of {GOLD_LABELS}"
        )

    if language is not None and language not in LANGUAGES:
        raise ValueError(
            f"language must be one of {LANGUAGES}"
        )

    if language is not None and languages is None:
        raise ValueError(
            "languages is required when filtering by language"
        )

    if languages is not None:
        languages = list(languages)

        if len(languages) != len(gold):
            raise ValueError(
                "languages must align with gold and pred"
            )

        if any(lang not in LANGUAGES for lang in languages):
            raise ValueError(
                f"languages must contain only {LANGUAGES}"
            )

    selected = [
        i
        for i, label in enumerate(gold)
        if (gold_class is None or label == gold_class)
        and (language is None or languages[i] == language)
    ]

    if not selected:
        raise ValueError(
            "No examples match the selected filters"
        )

    return (
        [gold[i] for i in selected],
        [pred[i] for i in selected],
    )


def _counts(
    gold: Sequence[str],
    pred: Sequence[str],
) -> dict[str, int]:
    """Binary confusion counts with refusal as positive."""
    tp = fp = tn = fn = 0

    for actual, predicted in zip(gold, pred):
        actual_refuse = actual != "answerable"
        predicted_refuse = predicted == "refuse"

        if actual_refuse and predicted_refuse:
            tp += 1
        elif not actual_refuse and predicted_refuse:
            fp += 1
        elif not actual_refuse and not predicted_refuse:
            tn += 1
        else:
            fn += 1

    return {
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
    }


def _divide(a: float, b: float) -> float:
    """Use zero_division=0 for undefined metric ratios."""
    return a / b if b else 0.0


def refuse_metrics(
    gold: Iterable[str],
    pred: Iterable[str],
    *,
    languages: Sequence[str] | None = None,
    language: str | None = None,
    gold_class: str | None = None,
) -> dict[str, float | int]:
    """Calculate precision, recall and F1 for refusal."""
    gold, pred = _prepare(
        gold,
        pred,
        languages=languages,
        language=language,
        gold_class=gold_class,
    )

    c = _counts(gold, pred)

    precision = _divide(
        c["tp"],
        c["tp"] + c["fp"],
    )
    recall = _divide(
        c["tp"],
        c["tp"] + c["fn"],
    )
    f1 = _divide(
        2 * precision * recall,
        precision + recall,
    )

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "support": c["tp"] + c["fn"],
        "n": len(gold),
        **c,
    }


def false_refusal_rate(
    gold: Iterable[str],
    pred: Iterable[str],
    *,
    languages: Sequence[str] | None = None,
    language: str | None = None,
    gold_class: str | None = None,
) -> float:
    """Fraction of answerable questions incorrectly refused.

    Formula: FP / (FP + TN).
    An empty denominator returns 0 by convention.
    Check class support before interpreting the result.
    """
    gold, pred = _prepare(
        gold,
        pred,
        languages=languages,
        language=language,
        gold_class=gold_class,
    )

    c = _counts(gold, pred)

    return _divide(
        c["fp"],
        c["fp"] + c["tn"],
    )


def macro_f1(
    gold: Iterable[str],
    pred: Iterable[str],
    *,
    languages: Sequence[str] | None = None,
    language: str | None = None,
    gold_class: str | None = None,
) -> float:
    """Unweighted mean of answer-F1 and refuse-F1."""
    gold, pred = _prepare(
        gold,
        pred,
        languages=languages,
        language=language,
        gold_class=gold_class,
    )

    c = _counts(gold, pred)

    refuse_f1 = _divide(
        2 * c["tp"],
        2 * c["tp"] + c["fp"] + c["fn"],
    )

    answer_f1 = _divide(
        2 * c["tn"],
        2 * c["tn"] + c["fp"] + c["fn"],
    )

    return (answer_f1 + refuse_f1) / 2


def confusion(
    gold_3class: Iterable[str],
    pred_2class: Iterable[str],
    *,
    languages: Sequence[str] | None = None,
    language: str | None = None,
    gold_class: str | None = None,
) -> dict[str, dict[str, int]]:
    """Return a 3-by-2 confusion matrix.

    Gold rows: answerable, plausible, out_of_scope.
    Predicted columns: answer, refuse.
    """
    gold, pred = _prepare(
        gold_3class,
        pred_2class,
        languages=languages,
        language=language,
        gold_class=gold_class,
    )

    matrix = {
        label: {"answer": 0, "refuse": 0}
        for label in GOLD_LABELS
    }

    for actual, predicted in zip(gold, pred):
        matrix[actual][predicted] += 1

    return matrix


def acceptance_score_metrics(
    gold: Iterable[str], scores: Iterable[float]
) -> dict:
    """Evaluate aligned, finite scores where higher means more likely to answer.

    Refusal AUROC treats both unanswerable labels as positive and is undefined
    with one binary class. Each curve point accepts scores at or above its
    threshold. Risk is the fraction of accepted questions that are unanswerable.
    With zero coverage, the threshold and risk are undefined.
    """
    gold = list(gold)
    scores = list(scores)
    if not gold or len(gold) != len(scores):
        raise ValueError("gold and scores must be nonempty and have equal lengths")
    if any(label not in GOLD_LABELS for label in gold):
        raise ValueError(f"gold labels must be one of {GOLD_LABELS}")
    if any(
        isinstance(score, bool) or not isinstance(score, Real) or not math.isfinite(score)
        for score in scores
    ):
        raise ValueError("acceptance scores must be finite numbers")

    scores = [float(score) for score in scores]
    should_refuse = [label != "answerable" for label in gold]
    auroc = None
    if any(should_refuse) and not all(should_refuse):
        auroc = float(roc_auc_score(should_refuse, [-score for score in scores]))

    ranked = sorted(zip(scores, should_refuse), key=lambda row: row[0], reverse=True)
    curve = [{"threshold": None, "coverage": 0.0, "risk": None}]
    accepted = accepted_unanswerable = 0
    for threshold, tied_rows in groupby(ranked, key=lambda row: row[0]):
        for _, unanswerable in tied_rows:
            accepted += 1
            accepted_unanswerable += unanswerable

        curve.append({
            "threshold": threshold,
            "coverage": accepted / len(gold),
            "risk": accepted_unanswerable / accepted,
        })

    return {"refusal_auroc": auroc, "risk_coverage": curve}


def _percentile(
    sorted_values: list[float],
    quantile: float,
) -> float:
    """Linearly interpolated percentile."""
    location = (len(sorted_values) - 1) * quantile

    lower = math.floor(location)
    upper = math.ceil(location)
    fraction = location - lower

    return (
        sorted_values[lower] * (1 - fraction)
        + sorted_values[upper] * fraction
    )


def bootstrap_ci(
    metric_fn: Callable[[list[str], list[str]], float],
    gold: Iterable[str],
    pred: Iterable[str],
    n: int = 1000,
    seed: int = 3004,
    *,
    languages: Sequence[str] | None = None,
    language: str | None = None,
    gold_class: str | None = None,
) -> tuple[float, float]:
    """Calculate a paired 95% percentile bootstrap interval.

    Resample question rows with replacement, keeping gold
    labels and predictions aligned.

    metric_fn takes gold and prediction lists and returns
    one finite metric value.

    Question-level resampling does not account for
    clustering of multiple questions within exhibits.
    """
    if (
        isinstance(n, bool)
        or not isinstance(n, int)
        or n < 1
    ):
        raise ValueError(
            "n must be a positive integer"
        )

    gold, pred = _prepare(
        gold,
        pred,
        languages=languages,
        language=language,
        gold_class=gold_class,
    )

    rng = random.Random(seed)
    scores = []

    for _ in range(n):
        indices = [
            rng.randrange(len(gold))
            for _ in gold
        ]

        sampled_gold = [
            gold[i] for i in indices
        ]
        sampled_pred = [
            pred[i] for i in indices
        ]

        value = float(
            metric_fn(sampled_gold, sampled_pred)
        )

        if not math.isfinite(value):
            raise ValueError(
                "metric_fn must return a finite number"
            )

        scores.append(value)

    scores.sort()

    return (
        _percentile(scores, 0.025),
        _percentile(scores, 0.975),
    )
