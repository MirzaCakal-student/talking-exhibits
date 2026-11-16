
"""Describe the question set and exhibit texts (K-3).

Run: uv run python scripts/data_analysis.py
No model training or held-out test evaluation is performed here.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
LABELS = ["answerable", "unanswerable_plausible", "out_of_scope"]
LANGS = ["bs", "en"]
DIACRITICS = set("čćđšžČĆĐŠŽ")


def tokens(text: str) -> set[str]:
    """Return lowercase word tokens, preserving diacritics."""
    return set(re.findall(r"\b\w+\b", text.lower(), flags=re.UNICODE))


def jaccard(question: str, exhibit: str) -> float:
    """Measure lexical overlap using Jaccard similarity."""
    q, e = tokens(question), tokens(exhibit)
    return len(q & e) / len(q | e) if q | e else 0.0


def load_exhibits(directory: Path) -> dict[tuple[str, str], str]:
    """Read the exhibit JSON files in both languages."""
    if not directory.is_dir():
        raise FileNotFoundError(f"Exhibit directory not found: {directory}")

    texts = {}

    for path in sorted(directory.glob("*.json")):
        with path.open(encoding="utf-8") as stream:
            exhibit = json.load(stream)

        for key in ("id", "lang", "text"):
            if key not in exhibit:
                raise ValueError(f"{path}: missing '{key}'")

        identity = (str(exhibit["id"]), str(exhibit["lang"]))

        if identity in texts:
            raise ValueError(f"Duplicate exhibit/language pair: {identity}")

        texts[identity] = str(exhibit["text"])

    if not texts:
        raise ValueError(f"No exhibit JSON files found in {directory}")

    return texts


def read_questions(path: Path) -> pd.DataFrame:
    """Load the question CSV and check its essential columns."""
    if not path.is_file():
        raise FileNotFoundError(f"Question CSV not found: {path}")

    df = pd.read_csv(path, dtype=str, keep_default_na=False)

    required = {
        "qid", "exhibit_id", "lang",
        "question", "label", "split",
    }
    missing = required - set(df.columns)

    if missing:
        raise ValueError(f"Missing question columns: {sorted(missing)}")

    if df.empty:
        raise ValueError("Question CSV is empty")

    if df.qid.duplicated().any():
        raise ValueError("Duplicate question ids found")

    if not df.lang.isin(LANGS).all():
        raise ValueError("Unknown question language")

    if not df.label.isin(LABELS).all():
        raise ValueError("Unknown gold label")

    if (df.question.str.strip() == "").any():
        raise ValueError("Empty question found")

    if not df.split.isin(["", "train", "val", "test"]).all():
        raise ValueError("Unexpected split value")

    return df


def markdown_table(df: pd.DataFrame) -> str:
    """Convert a small DataFrame into a Markdown table."""
    columns = [str(x) for x in df.columns]

    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]

    for row in df.itertuples(index=False, name=None):
        values = [
            str(value).replace("|", "\\|")
            for value in row
        ]
        lines.append("| " + " | ".join(values) + " |")

    return "\n".join(lines)


def analyze(
    questions: Path,
    exhibits_dir: Path,
    out_dir: Path,
) -> None:
    """Calculate statistics, generate figures and write a report."""
    df = read_questions(questions)
    exhibits = load_exhibits(exhibits_dir)

    exhibit_texts = []

    for row in df.itertuples(index=False):
        key = (row.exhibit_id, row.lang)

        if key not in exhibits:
            raise ValueError(
                f"{row.qid}: missing exhibit text for {key}"
            )

        exhibit_texts.append(exhibits[key])

    df = df.copy()

    df["question_words"] = df.question.map(
        lambda text: len(text.split())
    )

    df["overlap"] = [
        jaccard(question, text)
        for question, text in zip(df.question, exhibit_texts)
    ]

    counts = pd.crosstab(df.label, df.lang).reindex(
        index=LABELS,
        columns=LANGS,
        fill_value=0,
    )

    counts["total"] = counts.sum(axis=1)
    counts.loc["total"] = counts.sum(axis=0)

    out_dir.mkdir(parents=True, exist_ok=True)

    figures_dir = out_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    # Figure 1: gold label distribution by language.
    ax = counts.loc[LABELS, LANGS].plot.bar(
        rot=15,
        figsize=(9, 5),
    )
    ax.set_xlabel("Gold label")
    ax.set_ylabel("Number of questions")
    ax.legend(title="Language")
    ax.figure.tight_layout()
    ax.figure.savefig(
        figures_dir / "questions_by_label_language.png",
        dpi=160,
    )
    plt.close(ax.figure)

    # Figure 2: question lengths.
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(
        df.question_words,
        bins=min(15, max(1, df.question_words.nunique())),
    )
    ax.set_xlabel("Question length (words)")
    ax.set_ylabel("Number of questions")
    fig.tight_layout()
    fig.savefig(figures_dir / "question_lengths.png", dpi=160)
    plt.close(fig)

    # Figure 3: exhibit lengths.
    exhibit_lengths = [
        len(text.split())
        for text in exhibits.values()
    ]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(
        exhibit_lengths,
        bins=min(15, max(1, len(set(exhibit_lengths)))),
    )
    ax.set_xlabel("Exhibit text length (words)")
    ax.set_ylabel("Number of language versions")
    fig.tight_layout()
    fig.savefig(figures_dir / "exhibit_lengths.png", dpi=160)
    plt.close(fig)

    # Lexical overlap summary for the three question classes.
    by_class = (
        df.groupby("label", observed=True)
        .overlap.agg(["count", "mean"])
        .reindex(LABELS, fill_value=0)
    )

    by_class.columns = ["questions", "mean_jaccard"]
    by_class["mean_jaccard"] = by_class.mean_jaccard.round(4)
    by_class.index.name = "label"

    # This measures the absence of diacritic characters,
    # not whether the writer deliberately omitted them.
    bs = df.loc[df.lang == "bs", "question"]

    no_diacritic_count = sum(
        not (set(question) & DIACRITICS)
        for question in bs
    )

    no_diacritic_share = (
        no_diacritic_count / len(bs)
        if len(bs) else None
    )

    parts = [
        "# Dataset analysis (descriptive only)",
        f"Input questions: `{questions}`",
        f"Input exhibit directory: `{exhibits_dir}`",
        (
            f"Questions: **{len(df)}**; "
            f"exhibit language versions: **{len(exhibits)}**."
        ),
        "## Gold label × language",
        markdown_table(
            counts.reset_index().rename(
                columns={"label": "gold_label"}
            )
        ),
    ]

    if (df.split != "").any():
        split_counts = pd.crosstab(
            [
                df.split.replace("", "unassigned"),
                df.label,
            ],
            df.lang,
        ).reindex(columns=LANGS, fill_value=0)

        split_counts.index.names = ["split", "label"]

        parts.extend([
            "## Split × label × language",
            markdown_table(split_counts.reset_index()),
        ])

    parts.extend([
        "## Lengths",
        (
            f"Mean question length: "
            f"**{df.question_words.mean():.2f} words**."
        ),
        (
            f"Mean exhibit length: "
            f"**{sum(exhibit_lengths) / len(exhibit_lengths):.2f} words**."
        ),
        "## Question–exhibit lexical overlap",
        markdown_table(by_class.reset_index()),
        (
            "Jaccard uses unique lowercase word tokens from "
            "the selected exhibit text in the same language."
        ),
        "## Bosnian diacritic proxy",
        (
            f"Bosnian questions without any č/ć/đ/š/ž character: "
            f"**{no_diacritic_count}/{len(bs)} "
            f"({100 * no_diacritic_share:.1f}%)**."
            if no_diacritic_share is not None
            else "No Bosnian questions available."
        ),
        (
            "This is **not** a reliable count of deliberately "
            "omitted diacritics: many correctly written "
            "questions naturally contain none."
        ),
        "## Figures",
        "- `figures/questions_by_label_language.png`",
        "- `figures/question_lengths.png`",
        "- `figures/exhibit_lengths.png`",
        (
            "These are descriptive statistics, "
            "not model performance results."
        ),
    ])

    destination = out_dir / "data_tables.md"

    destination.write_text(
        "\n\n".join(parts) + "\n",
        encoding="utf-8",
    )

    print(
        f"OK: analyzed {len(df)} questions and "
        f"{len(exhibits)} exhibit language versions"
    )
    print(
        f"Wrote {destination} and three PNG figures "
        f"to {figures_dir}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        "--questions",
        type=Path,
        default=ROOT / "data/questions/questions.csv",
    )
    parser.add_argument(
        "--exhibits",
        type=Path,
        default=ROOT / "data/exhibits",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "results",
    )

    args = parser.parse_args()

    try:
        analyze(args.questions, args.exhibits, args.out)
    except (
        OSError,
        ValueError,
        json.JSONDecodeError,
        pd.errors.ParserError,
    ) as exc:
        parser.exit(1, f"ERROR: {exc}\n")


if __name__ == "__main__":
    main()
