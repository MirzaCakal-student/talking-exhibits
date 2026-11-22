
"""Describe the question set and exhibit texts (K-3).

Run: uv run python scripts/data_analysis.py
No model training or held-out test evaluation is performed here.
"""

from __future__ import annotations

import argparse
import json
import re
import shlex
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
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
            "N/A" if pd.isna(value) else str(value).replace("|", "\\|")
            for value in row
        ]
        lines.append("| " + " | ".join(values) + " |")

    return "\n".join(lines)


def length_statistics(group: str, lengths: list[int]) -> dict:
    """Summarize word counts; SD uses the sample denominator n - 1."""
    values = pd.Series(lengths, dtype=float)
    if values.empty:
        raise ValueError("Cannot summarize empty lengths")
    return {
        "group": group,
        "n": len(values),
        "mean": round(values.mean(), 2),
        "median": round(values.median(), 2),
        "sample_sd": round(values.std(), 2),
        "min": int(values.min()),
        "max": int(values.max()),
    }


def diacritic_statistics(
    df: pd.DataFrame,
    intentional_qids: list[str] | None = None,
) -> dict:
    """Keep declared omissions separate from absence of diacritic characters."""
    bs = df.loc[df.lang == "bs"]
    absent = bs.question.map(lambda text: not (set(text) & DIACRITICS))
    count = None
    if intentional_qids is not None:
        if len(set(intentional_qids)) != len(intentional_qids):
            raise ValueError("Duplicate intentional-omission qids")
        unknown = set(intentional_qids) - set(df.qid)
        if unknown:
            raise ValueError(f"Unknown intentional-omission qids: {sorted(unknown)}")
        selected = df.loc[df.qid.isin(intentional_qids)]
        if (selected.lang != "bs").any():
            raise ValueError("Intentional-omission qids must refer to Bosnian questions")
        if selected.question.map(lambda text: bool(set(text) & DIACRITICS)).any():
            raise ValueError("Intentional-omission questions must contain no diacritics")
        count = len(selected)
    return {
        "bs_questions": len(bs),
        "without_diacritics": int(absent.sum()),
        "intentional_omissions": count,
    }


def save_figure(fig, path: Path, caption: str) -> None:
    for ax in fig.axes:
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    if caption:
        fig.text(0.5, 0.015, caption, ha="center", fontsize=9)
    fig.tight_layout(rect=(0, 0.055 if caption else 0, 1, 1))
    fig.savefig(path, dpi=160)
    plt.close(fig)


def analyze(
    questions: Path,
    exhibits_dir: Path,
    out_dir: Path,
    *,
    preliminary: bool = False,
    intentional_qids: list[str] | None = None,
) -> None:
    """Calculate statistics, generate figures and write a report."""
    df = read_questions(questions)
    exhibits = load_exhibits(exhibits_dir)
    diacritics = diacritic_statistics(df, intentional_qids)

    source_count = int(df.source.isin(["human", "llm_checked"]).sum()) if "source" in df else 0
    review_count = 0
    if {"author", "checked_by"} <= set(df.columns):
        review_count = int((
            df.author.isin(["kerim", "mirza", "tarik"])
            & df.checked_by.isin(["kerim", "mirza", "tarik"])
            & df.author.ne(df.checked_by)
        ).sum())
    preliminary = preliminary or source_count < len(df) or review_count < len(df)
    caption = (
        f"Preliminary: {len(df)} question drafts; "
        f"{df.exhibit_id.nunique()} exhibits"
        if preliminary else ""
    )

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
    ax.set_xticklabels(["Answerable", "Plausible unanswerable", "Out of scope"], rotation=0)
    ax.set_xlabel("Question class")
    ax.set_ylabel("Number of questions")
    ax.legend(title="Language")
    for bars in ax.containers:
        ax.bar_label(bars, padding=3)
    ax.margins(y=0.15)
    save_figure(ax.figure, figures_dir / "questions_by_label_language.png", caption)

    # Figure 2: question lengths.
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(
        df.question_words,
        bins=min(15, max(1, df.question_words.nunique())),
    )
    ax.set_xlabel("Question length (words)")
    ax.set_ylabel("Number of questions")
    save_figure(fig, figures_dir / "question_lengths.png", caption)

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
    save_figure(fig, figures_dir / "exhibit_lengths.png", caption)

    # Lexical overlap summary for the three question classes.
    by_class = (
        df.groupby("label", observed=True)
        .overlap.agg(["count", "mean", "median", "min", "max"])
        .reindex(LABELS)
    )

    by_class["count"] = by_class["count"].fillna(0).astype(int)
    by_class.columns = ["questions", "mean_jaccard", "median_jaccard", "min_jaccard", "max_jaccard"]
    by_class = by_class.round(4)
    by_class.index.name = "label"

    length_rows = [length_statistics("questions_all", df.question_words.tolist())]
    for lang in LANGS:
        lengths = df.loc[df.lang == lang, "question_words"].tolist()
        if lengths:
            length_rows.append(length_statistics(f"questions_{lang}", lengths))
    length_rows.append(length_statistics("exhibit_versions_all", exhibit_lengths))
    for lang in LANGS:
        lengths = [len(text.split()) for (_, language), text in exhibits.items() if language == lang]
        if lengths:
            length_rows.append(length_statistics(f"exhibit_versions_{lang}", lengths))

    exhibit_counts = pd.crosstab(df.exhibit_id, df.lang).reindex(columns=LANGS, fill_value=0)
    exhibit_counts["total"] = exhibit_counts.sum(axis=1)
    exhibit_rows = pd.DataFrame([
        {"exhibit_id": identity, "lang": lang, "words": len(text.split())}
        for (identity, lang), text in exhibits.items()
    ])

    parts = [
        "# Preliminary dataset analysis" if preliminary else "# Dataset analysis (descriptive only)",
        (
            "These statistics describe the supplied question drafts and exhibit texts. "
            "They are not final M3 dataset statistics or model performance results."
            if preliminary else "These are descriptive dataset statistics, not model performance results."
        ),
        f"Input questions: `{questions}`",
        f"Input exhibit directory: `{exhibits_dir}`",
        (
            f"Questions: **{len(df)}**; "
            f"distinct question exhibits: **{df.exhibit_id.nunique()}**; "
            f"exhibit texts: **{len({key[0] for key in exhibits})}** "
            f"with **{len(exhibits)} language versions**."
        ),
        "## Review status",
        f"Rows with a recorded valid source value: **{source_count}/{len(df)}**.",
        f"Rows with an independent reviewer recorded: **{review_count}/{len(df)}**.",
        "Recorded metadata counts do not replace validation of labels and answer spans.",
        "## Question class × language",
        markdown_table(
            counts.reset_index().rename(
                columns={"label": "question_class"}
            )
        ),
        "## Questions per exhibit",
        markdown_table(exhibit_counts.reset_index()),
    ]

    if "author" in df:
        parts.extend([
            "## Question contributors",
            markdown_table(df.author.value_counts().rename_axis("author").reset_index(name="questions")),
        ])

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
    else:
        parts.extend(["## Split status", f"All **{len(df)}** split values are unassigned. No split distribution is reported."])

    parts.extend([
        "## Lengths",
        markdown_table(pd.DataFrame(length_rows)),
        "Lengths count whitespace-separated words. SD uses n − 1; N/A denotes an undefined statistic.",
        "## Exhibit text lengths",
        markdown_table(exhibit_rows),
        "## Question–exhibit lexical overlap",
        markdown_table(by_class.reset_index()),
        (
            "Jaccard uses unique lowercase word tokens from "
            "the selected exhibit text in the same language. Tokens match Unicode "
            "`\\w+`; diacritics are retained, without stemming or stopword removal. "
            "Similarity is the size of the token intersection divided by the token "
            "union, or zero for an empty union."
        ),
        (
            f"Mean Jaccard: answerable **{by_class.loc['answerable', 'mean_jaccard']:.4f}**, "
            f"plausible **{by_class.loc['unanswerable_plausible', 'mean_jaccard']:.4f}**, "
            f"out of scope **{by_class.loc['out_of_scope', 'mean_jaccard']:.4f}**."
            if (by_class.questions > 0).all() else "Some question classes are absent; their overlap is N/A."
        ),
        (
            "A plausible question can share topic words with the text while requesting an unstated fact. "
            "Jaccard measures lexical overlap, not answerability or BM25 performance. "
            "These descriptive results do not establish that a retrieval threshold succeeds or fails."
        ),
        "## Bosnian diacritics",
        (
            f"Bosnian questions without any č/ć/đ/š/ž character: "
            f"**{diacritics['without_diacritics']}/{diacritics['bs_questions']} "
            f"({100 * diacritics['without_diacritics'] / diacritics['bs_questions']:.1f}%)**."
            if diacritics["bs_questions"]
            else "No Bosnian questions available."
        ),
        (
            "This is **not** a reliable count of deliberately "
            "omitted diacritics: many correctly written "
            "questions naturally contain none."
        ),
    ])

    if intentional_qids is not None and diacritics["bs_questions"]:
        count = diacritics["intentional_omissions"]
        parts.extend([
            f"Documented intentional omissions supplied from the authoring record: **{count}/{diacritics['bs_questions']} ({100 * count / diacritics['bs_questions']:.1f}%)**.",
            "Declared qids: " + ", ".join(f"`{qid}`" for qid in sorted(intentional_qids)) + ".",
            f"Other diacritic-free Bosnian questions: **{diacritics['without_diacritics'] - count}**. Character absence alone does not establish their writing intent.",
            "The declared qids are authoring annotations, not independent human review approvals.",
        ])
    else:
        parts.append("The intentional-omission proportion is unknown without explicit authoring annotations.")

    command = [
        "uv", "run", "--frozen", "python", "scripts/data_analysis.py",
        "--questions", str(questions), "--exhibits", str(exhibits_dir), "--out", str(out_dir),
    ]
    if preliminary:
        command.append("--preliminary")
    if intentional_qids is not None:
        command.extend(["--intentional-no-diacritics", *intentional_qids])
    parts.extend([
        "## Reproduce",
        "Run from the repository root:",
        "```bash\n" + shlex.join(command) + "\n```",
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
    parser.add_argument("--preliminary", action="store_true", help="Label an incomplete dataset analysis as preliminary")
    parser.add_argument(
        "--intentional-no-diacritics", nargs="*", metavar="QID", default=None,
        help="Complete list of known intentional omissions from the question-authoring record",
    )

    args = parser.parse_args()

    try:
        analyze(
            args.questions, args.exhibits, args.out,
            preliminary=args.preliminary,
            intentional_qids=args.intentional_no_diacritics,
        )
    except (
        OSError,
        ValueError,
        json.JSONDecodeError,
        pd.errors.ParserError,
    ) as exc:
        parser.exit(1, f"ERROR: {exc}\n")


if __name__ == "__main__":
    main()
