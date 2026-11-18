"""Split the question set into train / val / test BY EXHIBIT (seed 3004).

Why by exhibit and not by question: if questions about the same exhibit were in
train and test, the model (and the refusal threshold) would already have seen that
exhibit text, and the test score would be too optimistic (data leakage). Here every
exhibit, with both its BS and EN questions, goes to exactly one split.

Default for 12 exhibits: 6 train, 2 val, 4 test. With about 25 questions per exhibit
this gives a test set of about 100 questions, which the course requires (>= 100).

What the script does:
  1. load questions and exhibits and run the validator (stops if there are errors);
  2. shuffle the exhibit ids with random.Random(3004) and assign them to splits;
  3. warn if the test set has < 100 questions or a split misses one of the 3 labels;
  4. save data/processed/{train,val,test}.csv and print counts per split, label and language;
  5. write the split into the 'split' column of questions.csv (unless --no-update-source).

Run:
    uv run python scripts/build_dataset.py
    uv run python scripts/build_dataset.py --val-exhibits 2 --test-exhibits 4

If the split is bad (e.g. test < 100), do NOT try other seeds until it "looks good".
Move exhibits by hand, write down why, and keep the seed at 3004.
"""

import argparse
import random
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from validate_questions import (  # noqa: E402
    DEFAULT_EXHIBITS,
    DEFAULT_QUESTIONS,
    LABELS,
    ROOT,
    load_exhibit_texts,
    load_questions,
    validate,
)

SEED = 3004
SPLITS = ["train", "val", "test"]
MIN_TEST_QUESTIONS = 100  # course requirement for the team-made test set
DEFAULT_OUT = ROOT / "data" / "processed"


def assign_exhibits(exhibit_ids, n_val: int, n_test: int, seed: int = SEED) -> dict:
    """Map every exhibit id to 'train', 'val' or 'test'.

    The ids are sorted first, so the result depends only on the seed and the ids,
    not on the order of rows in the CSV.
    """
    ids = sorted(set(exhibit_ids))
    if n_val < 1 or n_test < 1:
        raise ValueError("val and test need at least one exhibit each")
    if n_val + n_test >= len(ids):
        raise ValueError(
            f"{len(ids)} exhibits are not enough for {n_val} val + {n_test} test "
            "and at least one train exhibit"
        )

    rng = random.Random(seed)
    rng.shuffle(ids)
    assignment = {}
    for exhibit_id in ids[:n_test]:
        assignment[exhibit_id] = "test"
    for exhibit_id in ids[n_test : n_test + n_val]:
        assignment[exhibit_id] = "val"
    for exhibit_id in ids[n_test + n_val :]:
        assignment[exhibit_id] = "train"
    return assignment


def apply_split(df: pd.DataFrame, assignment: dict) -> pd.DataFrame:
    """Return a copy of the questions with the 'split' column filled in."""
    df = df.copy()
    df["split"] = df["exhibit_id"].map(assignment)
    if df["split"].isna().any():
        missing = sorted(df.loc[df["split"].isna(), "exhibit_id"].unique())
        raise ValueError(f"No split assigned for exhibit(s): {missing}")
    return df


def split_warnings(df: pd.DataFrame, min_test: int = MIN_TEST_QUESTIONS) -> list:
    """Problems with the split that the team should look at (not errors)."""
    warnings = []
    n_test = int((df["split"] == "test").sum())
    if n_test < min_test:
        warnings.append(f"test set has {n_test} questions, the course requires at least {min_test}")
    for split in SPLITS:
        labels_present = set(df.loc[df["split"] == split, "label"])
        for label in sorted(LABELS - labels_present):
            warnings.append(f"{split} has no '{label}' questions")
    return warnings


def count_table(df: pd.DataFrame) -> pd.DataFrame:
    """Number of questions per split and label (rows) and language (columns)."""
    return pd.crosstab([df["split"], df["label"]], df["lang"], margins=True, margins_name="total")


def save_splits(df: pd.DataFrame, out_dir: Path) -> list:
    """Write one CSV per split; return the paths."""
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for split in SPLITS:
        path = out_dir / f"{split}.csv"
        df[df["split"] == split].to_csv(path, index=False, encoding="utf-8")
        paths.append(path)
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description="Split questions by exhibit (seed 3004).")
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument("--exhibits", type=Path, default=DEFAULT_EXHIBITS)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--val-exhibits", type=int, default=2)
    parser.add_argument("--test-exhibits", type=int, default=4)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument(
        "--no-update-source", action="store_true", help="do not write the split back into questions.csv"
    )
    args = parser.parse_args()

    print("1. Loading and validating")
    df = load_questions(args.questions)
    exhibit_texts = load_exhibit_texts(args.exhibits)
    errors = validate(df, exhibit_texts)
    if errors:
        print(f"  The question file has {len(errors)} problem(s); fix them first:")
        print("  uv run python scripts/validate_questions.py")
        sys.exit(1)
    if df.empty:
        print("  No questions yet; nothing to split.")
        sys.exit(1)
    print(f"  {len(df)} questions about {df['exhibit_id'].nunique()} exhibits")

    print(f"2. Assigning exhibits (seed {args.seed})")
    assignment = assign_exhibits(df["exhibit_id"], args.val_exhibits, args.test_exhibits, args.seed)
    for split in SPLITS:
        ids = sorted(e for e, s in assignment.items() if s == split)
        print(f"  {split:<5} ({len(ids)}): {', '.join(ids)}")
    df = apply_split(df, assignment)

    print("3. Checks")
    warnings = split_warnings(df)
    for warning in warnings:
        print(f"  WARNING: {warning}")
    if not warnings:
        print("  OK")

    print("4. Counts per split, label and language")
    print(count_table(df).to_string())
    for path in save_splits(df, args.out):
        print(f"  saved {path}")

    if not args.no_update_source:
        df.to_csv(args.questions, index=False, encoding="utf-8")
        print(f"5. Wrote the split column into {args.questions}")


if __name__ == "__main__":
    main()
