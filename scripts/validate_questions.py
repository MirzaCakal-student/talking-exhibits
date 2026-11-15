"""Validate the team's question set (data/questions/questions.csv).

Every question is checked against the agreed schema (HANDOFF.md section 5.2)
before anyone uses the file for training or evaluation. A wrong label or a
wrong answer offset silently breaks every number we report later, so we
catch those mistakes here.

Run:
    uv run python scripts/validate_questions.py

Prints "OK (N questions)" or one line per problem with the qid and the reason.
Exit code is 0 when the file is valid and 1 when it is not.
"""

import argparse
import json
import re
import sys
from pathlib import Path

import pandas as pd

# Paths relative to the repository root, so the script works from any folder.
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_QUESTIONS = ROOT / "data" / "questions" / "questions.csv"
DEFAULT_EXHIBITS = ROOT / "data" / "exhibits"

# The schema everyone writes into (same order as the CSV header).
REQUIRED_COLUMNS = [
    "qid",
    "exhibit_id",
    "lang",
    "question",
    "label",
    "answer_text",
    "answer_start",
    "author",
    "checked_by",
    "source",
    "split",
]

# Allowed values for the categorical columns.
LANGS = {"bs", "en"}
LABELS = {"answerable", "unanswerable_plausible", "out_of_scope"}
SOURCES = {"human", "llm_checked"}
MEMBERS = {"mirza", "tarik", "kerim"}
SPLITS = {"", "train", "val", "test"}  # empty until build_dataset.py fills it

QID_PATTERN = re.compile(r"^q\d{4}$")  # q0001, q0002, ...


def load_questions(path: Path) -> pd.DataFrame:
    """Read the question CSV with every cell as text."""
    if not path.exists():
        raise FileNotFoundError(f"Question file not found: {path}")
    # dtype=str and keep_default_na=False keep empty cells as "" (not NaN)
    # and stop pandas from turning "0042" into the number 42.
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def load_exhibit_texts(exhibits_dir: Path) -> dict:
    """Return {(exhibit_id, lang): text} for every exhibit JSON file.

    Temporary helper: switch to data.load_exhibits once Mirza adds it.
    """
    if not exhibits_dir.is_dir():
        raise FileNotFoundError(f"Exhibit folder not found: {exhibits_dir}")
    texts = {}
    for path in sorted(exhibits_dir.glob("*.json")):
        with open(path, encoding="utf-8") as f:
            exhibit = json.load(f)
        for field in ("id", "lang", "text"):
            if field not in exhibit:
                raise ValueError(f"{path.name}: missing field '{field}'")
        texts[(exhibit["id"], exhibit["lang"])] = exhibit["text"]
    return texts


def check_columns(df: pd.DataFrame) -> list:
    """Every required column must be present."""
    return [f"missing column: {col}" for col in REQUIRED_COLUMNS if col not in df.columns]


def check_qids(df: pd.DataFrame) -> list:
    """qid must look like q0001 and must be unique."""
    errors = []
    for qid in df["qid"]:
        if not QID_PATTERN.match(qid):
            errors.append(f"{qid or '<empty qid>'}: qid must look like q0001")
    for qid in sorted(set(df.loc[df["qid"].duplicated(), "qid"])):
        errors.append(f"{qid}: qid is used more than once")
    return errors


def check_allowed_values(df: pd.DataFrame, exhibit_texts: dict) -> list:
    """Categorical columns may only hold the agreed values."""
    errors = []
    known_exhibits = {exhibit_id for exhibit_id, _ in exhibit_texts}
    for row in df.itertuples(index=False):
        if row.question.strip() == "":
            errors.append(f"{row.qid}: question is empty")
        if row.exhibit_id not in known_exhibits:
            errors.append(f"{row.qid}: unknown exhibit_id '{row.exhibit_id}'")
        if row.lang not in LANGS:
            errors.append(f"{row.qid}: lang must be one of {sorted(LANGS)}, got '{row.lang}'")
        if row.label not in LABELS:
            errors.append(f"{row.qid}: label must be one of {sorted(LABELS)}, got '{row.label}'")
        if row.source not in SOURCES:
            errors.append(f"{row.qid}: source must be one of {sorted(SOURCES)}, got '{row.source}'")
        if row.split not in SPLITS:
            errors.append(f"{row.qid}: split must be empty or train/val/test, got '{row.split}'")
    return errors


def check_reviewers(df: pd.DataFrame) -> list:
    """author and checked_by are team members, and nobody checks their own question."""
    errors = []
    for row in df.itertuples(index=False):
        if row.author not in MEMBERS:
            errors.append(f"{row.qid}: author must be one of {sorted(MEMBERS)}, got '{row.author}'")
        if row.checked_by not in MEMBERS:
            errors.append(f"{row.qid}: checked_by must be one of {sorted(MEMBERS)}, got '{row.checked_by}'")
        if row.author == row.checked_by:
            errors.append(f"{row.qid}: checked_by must be a different member than author")
    return errors


def check_answer_spans(df: pd.DataFrame, exhibit_texts: dict) -> list:
    """Answerable questions point to the exact answer span in the exhibit text.

    The span is text[answer_start : answer_start + len(answer_text)] in the
    exhibit version with the same language as the question (SQuAD format).
    Questions that are not answerable must leave both answer fields empty.
    """
    errors = []
    for row in df.itertuples(index=False):
        if row.label != "answerable":
            if row.answer_text != "" or row.answer_start != "":
                errors.append(f"{row.qid}: answer_text and answer_start must be empty for label '{row.label}'")
            continue

        if row.answer_text == "" or row.answer_start == "":
            errors.append(f"{row.qid}: answerable question needs answer_text and answer_start")
            continue
        if not row.answer_start.isdigit():
            errors.append(f"{row.qid}: answer_start must be a whole number >= 0, got '{row.answer_start}'")
            continue

        text = exhibit_texts.get((row.exhibit_id, row.lang))
        if text is None:
            # Unknown exhibits are already reported; here the language version is missing.
            if any(exhibit_id == row.exhibit_id for exhibit_id, _ in exhibit_texts):
                errors.append(f"{row.qid}: exhibit '{row.exhibit_id}' has no '{row.lang}' text")
            continue

        start = int(row.answer_start)
        found = text[start : start + len(row.answer_text)]
        if found != row.answer_text:
            hint = text.find(row.answer_text)
            where = f"found at position {hint}" if hint != -1 else "not found anywhere in the text"
            errors.append(
                f"{row.qid}: answer_text '{row.answer_text}' is not at position {start} "
                f"(text there is '{found}'; {where})"
            )
    return errors


def normalize_question(question: str) -> str:
    """Lowercase and collapse spaces so trivial variants count as the same question."""
    return " ".join(question.lower().split())


def check_duplicates(df: pd.DataFrame) -> list:
    """The same question must not appear twice for the same exhibit."""
    errors = []
    seen = {}  # (exhibit_id, normalized question) -> first qid
    for row in df.itertuples(index=False):
        key = (row.exhibit_id, normalize_question(row.question))
        if key in seen:
            errors.append(f"{row.qid}: duplicate of {seen[key]} (same question for '{row.exhibit_id}')")
        else:
            seen[key] = row.qid
    return errors


def validate(df: pd.DataFrame, exhibit_texts: dict) -> list:
    """Run every check and return all problems (an empty list means valid)."""
    errors = check_columns(df)
    if errors:
        # The other checks need these columns, so stop here.
        return errors
    errors += check_qids(df)
    errors += check_allowed_values(df, exhibit_texts)
    errors += check_reviewers(df)
    errors += check_answer_spans(df, exhibit_texts)
    errors += check_duplicates(df)
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the question set.")
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument("--exhibits", type=Path, default=DEFAULT_EXHIBITS)
    args = parser.parse_args()

    df = load_questions(args.questions)
    exhibit_texts = load_exhibit_texts(args.exhibits)
    print(f"Checking {len(df)} questions in {args.questions}")
    print(f"Found {len(exhibit_texts)} exhibit texts in {args.exhibits}")

    errors = validate(df, exhibit_texts)
    if errors:
        print(f"Found {len(errors)} problem(s):")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    print(f"OK ({len(df)} questions)")


if __name__ == "__main__":
    main()
