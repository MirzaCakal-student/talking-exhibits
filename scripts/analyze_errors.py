"""Export validation decision errors for manual review (minimum 10, target 20)."""

import argparse
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from evaluate_all import ROOT, expected_decisions, read_gold, read_predictions

DECISION_FIELDS = ["qid", "system", "gold", "pred"]
REVIEW_FIELDS = ["kategorija", "uzrok", "objašnjenje"]
COLUMNS = DECISION_FIELDS + REVIEW_FIELDS
CATEGORIES = (
    "retrieval promašio pasus",
    "leksičko preklapanje zavarava model",
    "odgovor zahtijeva zaključivanje",
    "greška u gold labeli",
    "dijakritici ili sleng",
    "prevod",
)


def find_errors(gold: pd.DataFrame, predictions: pd.DataFrame) -> pd.DataFrame:
    """Find decision errors in validated inputs and keep the three-way gold label."""
    joined = predictions[["qid", "system", "pred"]].merge(
        gold[["qid", "label"]], on="qid", validate="many_to_one",
    ).rename(columns={"label": "gold"})
    wrong = joined["qid"].map(expected_decisions(gold)).ne(joined["pred"])
    return joined.loc[wrong, DECISION_FIELDS].sort_values(["system", "qid"], ignore_index=True)


def attach_reviews(errors: pd.DataFrame, path: Path) -> pd.DataFrame:
    """Keep manual annotations on re-export and reject changes to their decisions."""
    if not path.exists():
        return errors.assign(**dict.fromkeys(REVIEW_FIELDS, ""))

    previous = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8")
    if list(previous.columns) != COLUMNS or previous.duplicated(["qid", "system"]).any():
        raise ValueError(f"{path.name}: expected columns {COLUMNS} and unique (qid, system) pairs")

    filled = previous[REVIEW_FIELDS].apply(lambda column: column.str.strip()).ne("")
    invalid = filled["kategorija"] & ~previous["kategorija"].str.strip().isin(CATEGORIES)
    if invalid.any():
        raise ValueError(f"{path.name}: invalid category for qid(s) {previous.loc[invalid, 'qid'].tolist()}")

    annotated = previous.loc[filled.any(axis=1)]
    checked = annotated.merge(errors, on=DECISION_FIELDS, how="left", indicator=True)
    stale = checked.loc[checked["_merge"].eq("left_only"), ["qid", "system"]]
    if not stale.empty:
        raise ValueError(f"{path.name}: annotated decisions changed for {list(stale.itertuples(index=False, name=None))}; use a new --out path")

    return errors.merge(annotated, on=DECISION_FIELDS, how="left", validate="one_to_one").fillna("")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gold", type=Path, default=ROOT / "data/processed/val.csv")
    parser.add_argument("--predictions", default=str(ROOT / "results/val_predictions_*.csv"))
    parser.add_argument("--out", type=Path, default=ROOT / "results/errors.csv")
    parser.epilog = "Allowed review categories: " + ", ".join(CATEGORIES)
    args = parser.parse_args()

    try:
        gold = read_gold(args.gold)
        decisions = expected_decisions(gold)
        predictions = read_predictions(args.predictions, set(decisions), gold_decisions=decisions)
        errors = attach_reviews(find_errors(gold, predictions), args.out)

        args.out.parent.mkdir(parents=True, exist_ok=True)
        with TemporaryDirectory(dir=args.out.parent) as temporary:
            output = Path(temporary) / args.out.name
            errors.to_csv(output, index=False, columns=COLUMNS, encoding="utf-8")
            output.replace(args.out)
    except (OSError, ValueError, pd.errors.ParserError) as exc:
        parser.exit(1, f"ERROR: {exc}\n")

    reviewed = errors[REVIEW_FIELDS].apply(lambda column: column.str.strip()).ne("").all(axis=1).sum()
    print(f"Wrote {len(errors)} decision errors to {args.out}. Complete reviews: {reviewed} (minimum 10, target 20).")


if __name__ == "__main__":
    main()
