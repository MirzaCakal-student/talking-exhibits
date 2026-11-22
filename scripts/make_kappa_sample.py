"""Draw the shared question sample for the inter-annotator agreement (Cohen's kappa).

Both annotators label the SAME questions independently, without seeing the
original labels or each other's labels. The sample takes the same number of
questions from each author (seed 3004), so nobody labels only their own questions.

The output has the columns qid, exhibit_id, lang, question and an empty label
column. Each annotator copies it (e.g. agreement/tarik.csv, agreement/kerim.csv),
fills in the label column and then runs scripts/compute_kappa.py.

Usage:
    uv run python scripts/make_kappa_sample.py
"""

import argparse
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SEED = 3004


def make_sample(questions: pd.DataFrame, per_author: int, seed: int = SEED) -> pd.DataFrame:
    """Take per_author questions from every author, shuffle them and hide the labels."""
    parts = []
    for author, group in questions.groupby("author", sort=True):
        if len(group) < per_author:
            raise ValueError(f"author {author!r} has only {len(group)} questions")
        parts.append(group.sample(per_author, random_state=seed))
    sample = pd.concat(parts).sample(frac=1, random_state=seed)
    sample = sample[["qid", "exhibit_id", "lang", "question"]].copy()
    sample["label"] = ""
    return sample.reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--questions", type=Path, default=ROOT / "data/questions/questions.csv")
    parser.add_argument("--out", type=Path, default=ROOT / "data/questions/agreement/sample.csv")
    parser.add_argument("--per-author", type=int, default=25)
    args = parser.parse_args()

    questions = pd.read_csv(args.questions, dtype=str, keep_default_na=False)
    sample = make_sample(questions, args.per_author)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    sample.to_csv(args.out, index=False, encoding="utf-8")
    print(f"wrote {len(sample)} questions to {args.out}")
    print(sample["lang"].value_counts().to_string())


if __name__ == "__main__":
    main()
