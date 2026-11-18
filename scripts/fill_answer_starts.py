"""Fill in answer_start for answerable questions, so nobody counts characters by hand.

Question writers only type the answer text (an exact copy from the exhibit text).
This script finds where that text starts in the exhibit of the same language and
writes the character offset into the answer_start column (SQuAD format).

Rows that already have an answer_start are left untouched; the validator checks them.
If the answer appears more than once, the first occurrence is used and the row is
reported, so the writer can check it is the right one (annotation guidelines 5.7).

Run:
    uv run python scripts/fill_answer_starts.py            # updates questions.csv
    uv run python scripts/fill_answer_starts.py --dry-run  # only shows what it would do
Then:
    uv run python scripts/validate_questions.py
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

# Reuse the loaders of the validator (same folder), so both scripts read files the same way.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from validate_questions import (  # noqa: E402
    DEFAULT_EXHIBITS,
    DEFAULT_QUESTIONS,
    load_exhibit_texts,
    load_questions,
)


def find_answer_start(text: str, answer_text: str) -> tuple:
    """Return (first start index, number of occurrences); start is -1 if not found."""
    if answer_text == "":
        raise ValueError("answer_text must not be empty")
    return text.find(answer_text), text.count(answer_text)


def fill_answer_starts(df: pd.DataFrame, exhibit_texts: dict) -> tuple:
    """Fill empty answer_start cells of answerable questions.

    Returns (new DataFrame, number of filled rows, list of messages for the writer).
    The input DataFrame is not changed.
    """
    df = df.copy()
    filled = 0
    messages = []
    for i, row in df.iterrows():
        needs_offset = (
            row["label"] == "answerable"
            and row["answer_text"] != ""
            and row["answer_start"] == ""
        )
        if not needs_offset:
            continue

        text = exhibit_texts.get((row["exhibit_id"], row["lang"]))
        if text is None:
            messages.append(f"{row['qid']}: no '{row['lang']}' text for exhibit '{row['exhibit_id']}'")
            continue

        start, count = find_answer_start(text, row["answer_text"])
        if start == -1:
            messages.append(
                f"{row['qid']}: answer_text '{row['answer_text']}' is not in the exhibit text "
                "(copy it exactly, with the same spelling and diacritics)"
            )
            continue

        df.at[i, "answer_start"] = str(start)
        filled += 1
        if count > 1:
            messages.append(
                f"{row['qid']}: '{row['answer_text']}' appears {count} times; used the first one "
                f"at position {start}, check that it is the right one"
            )
    return df, filled, messages


def main() -> None:
    parser = argparse.ArgumentParser(description="Fill answer_start for answerable questions.")
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument("--exhibits", type=Path, default=DEFAULT_EXHIBITS)
    parser.add_argument("--dry-run", action="store_true", help="show the result without saving")
    args = parser.parse_args()

    df = load_questions(args.questions)
    exhibit_texts = load_exhibit_texts(args.exhibits)
    df, filled, messages = fill_answer_starts(df, exhibit_texts)

    print(f"Filled answer_start for {filled} question(s) in {args.questions}")
    for message in messages:
        print(f"  - {message}")

    if args.dry_run:
        print("Dry run: nothing was saved.")
        return
    if filled:
        df.to_csv(args.questions, index=False, encoding="utf-8")
        print(f"Saved {args.questions}. Next: uv run python scripts/validate_questions.py")


if __name__ == "__main__":
    main()
