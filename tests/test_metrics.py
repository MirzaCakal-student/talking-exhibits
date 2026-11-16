
"""Manual examples and boundary tests for evaluation metrics."""

import math
import random

import pytest

from talking_exhibits.evaluate import (
    bootstrap_ci,
    confusion,
    false_refusal_rate,
    macro_f1,
    refuse_metrics,
)


# Hand-counted example:
# TP = 1, FP = 1, TN = 2, FN = 2.

GOLD = [
    "answerable",
    "unanswerable_plausible",
    "out_of_scope",
    "answerable",
    "unanswerable_plausible",
    "answerable",
]

PRED = [
    "answer",
    "refuse",
    "answer",
    "refuse",
    "answer",
    "answer",
]

LANG = [
    "bs",
    "bs",
    "en",
    "en",
    "bs",
    "en",
]


def test_manual_refusal_counts():
    result = refuse_metrics(GOLD, PRED)

    assert (
        result["tp"],
        result["fp"],
        result["tn"],
        result["fn"],
    ) == (1, 1, 2, 2)

    assert result["support"] == 3
    assert result["n"] == 6


def test_manual_refusal_precision_recall_f1():
    result = refuse_metrics(GOLD, PRED)

    assert result["precision"] == pytest.approx(1 / 2)
    assert result["recall"] == pytest.approx(1 / 3)
    assert result["f1"] == pytest.approx(2 / 5)


def test_manual_false_refusal_rate():
    result = false_refusal_rate(GOLD, PRED)

    assert result == pytest.approx(1 / 3)


def test_manual_macro_f1():
    # Refuse F1 = 2/5.
    # Answer F1 = 4/7.
    # Macro F1 = 17/35.

    result = macro_f1(GOLD, PRED)

    assert result == pytest.approx(17 / 35)


def test_manual_three_by_two_confusion():
    expected = {
        "answerable": {
            "answer": 2,
            "refuse": 1,
        },
        "unanswerable_plausible": {
            "answer": 1,
            "refuse": 1,
        },
        "out_of_scope": {
            "answer": 1,
            "refuse": 0,
        },
    }

    assert confusion(GOLD, PRED) == expected


def test_never_refuse_has_zero_refusal_f1():
    predictions = ["answer"] * len(GOLD)

    result = refuse_metrics(GOLD, predictions)

    assert result["f1"] == 0
    assert result["precision"] == 0
    assert result["recall"] == 0


def test_always_refuse_has_max_false_refusal_rate():
    predictions = ["refuse"] * len(GOLD)

    result = false_refusal_rate(GOLD, predictions)

    assert result == 1


def test_perfect_predictions():
    predictions = [
        "answer" if label == "answerable" else "refuse"
        for label in GOLD
    ]

    assert refuse_metrics(
        GOLD, predictions
    )["f1"] == 1

    assert false_refusal_rate(
        GOLD, predictions
    ) == 0

    assert macro_f1(
        GOLD, predictions
    ) == 1


def test_bosnian_filter():
    result = refuse_metrics(
        GOLD,
        PRED,
        languages=LANG,
        language="bs",
    )

    assert result["n"] == 3
    assert result["f1"] == pytest.approx(2 / 3)


def test_gold_class_filter():
    result = refuse_metrics(
        GOLD,
        PRED,
        gold_class="unanswerable_plausible",
    )

    assert result["support"] == 2
    assert result["recall"] == pytest.approx(1 / 2)

    matrix = confusion(
        GOLD,
        PRED,
        gold_class="out_of_scope",
    )

    assert matrix["out_of_scope"] == {
        "answer": 1,
        "refuse": 0,
    }


def test_combined_filters():
    result = refuse_metrics(
        GOLD,
        PRED,
        languages=LANG,
        language="bs",
        gold_class="unanswerable_plausible",
    )

    assert result["n"] == 2


@pytest.mark.parametrize(
    "gold,pred",
    [
        ([], []),
        (GOLD, PRED[:-1]),
    ],
)
def test_invalid_lengths(gold, pred):
    with pytest.raises(ValueError):
        refuse_metrics(gold, pred)


@pytest.mark.parametrize(
    "gold,pred",
    [
        (["other"], ["answer"]),
        (["answerable"], ["unknown"]),
    ],
)
def test_invalid_labels(gold, pred):
    with pytest.raises(ValueError):
        refuse_metrics(gold, pred)


def test_invalid_filters():
    with pytest.raises(ValueError):
        refuse_metrics(
            GOLD,
            PRED,
            language="bs",
        )

    with pytest.raises(ValueError):
        refuse_metrics(
            GOLD,
            PRED,
            languages=["bs"],
            language="bs",
        )

    with pytest.raises(ValueError):
        refuse_metrics(
            GOLD,
            PRED,
            languages=LANG,
            language="fr",
        )

    with pytest.raises(ValueError):
        refuse_metrics(
            GOLD,
            PRED,
            gold_class="invalid",
        )

    with pytest.raises(ValueError):
        refuse_metrics(
            GOLD,
            PRED,
            languages=LANG,
            language="bs",
            gold_class="out_of_scope",
        )


def test_bootstrap_deterministic_and_bounded():
    def metric(gold, pred):
        return refuse_metrics(gold, pred)["f1"]

    ci1 = bootstrap_ci(
        metric, GOLD, PRED, n=120, seed=3004
    )
    ci2 = bootstrap_ci(
        metric, GOLD, PRED, n=120, seed=3004
    )

    assert ci1 == ci2
    assert 0 <= ci1[0] <= ci1[1] <= 1


def test_bootstrap_constant_metric():
    def metric(gold, pred):
        return 0.25

    result = bootstrap_ci(
        metric, GOLD, PRED, n=30
    )

    assert result == (0.25, 0.25)


def test_bootstrap_rejects_bad_iterations_or_metric():
    with pytest.raises(ValueError):
        bootstrap_ci(
            lambda g, p: 0.5,
            GOLD,
            PRED,
            n=0,
        )

    with pytest.raises(ValueError):
        bootstrap_ci(
            lambda g, p: math.nan,
            GOLD,
            PRED,
            n=20,
        )


def test_bootstrap_does_not_change_global_rng():
    random.seed(5)
    before = random.getstate()

    bootstrap_ci(
        lambda g, p: 0.5,
        GOLD,
        PRED,
        n=10,
    )

    assert random.getstate() == before
