"""Inter-annotator agreement (Cohen's kappa) on the double-annotated questions.

Two team members label the SAME ~50 questions independently (without looking at
each other's labels). Each saves a CSV with two columns, qid and label, e.g.
    data/questions/agreement/tarik.csv
    data/questions/agreement/kerim.csv

Plain agreement (share of equal labels) is too optimistic: two people who guess
would also agree sometimes. Cohen's kappa removes that chance agreement:

    kappa = (p_o - p_e) / (1 - p_e)

    p_o = observed agreement (share of questions with the same label)
    p_e = agreement expected by chance, from how often each person uses each label

kappa = 1 is perfect agreement, 0 is chance level. A common reading
(Landis and Koch, 1977): 0.41-0.60 moderate, 0.61-0.80 substantial, > 0.80 almost perfect.

We report kappa for the 3 labels and for the 2 system decisions (answer / refuse).
Compute it on the independent labels, BEFORE the two annotators discuss and fix them.

Run:
    uv run python scripts/compute_kappa.py --a data/questions/agreement/tarik.csv \
        --b data/questions/agreement/kerim.csv
"""

import argparse
import sys
from pathlib import Path

import pandas as pd
from sklearn.metrics import cohen_kappa_score

sys.path.insert(0, str(Path(__file__).resolve().parent))

from validate_questions import LABELS  # noqa: E402


def load_annotations(path: Path) -> pd.DataFrame:
    """Read one annotator's file (columns qid, label) and check it."""
    if not path.exists():
        raise FileNotFoundError(f"Annotation file not found: {path}")
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    missing = [col for col in ("qid", "label") if col not in df.columns]
    if missing:
        raise ValueError(f"{path.name}: missing column(s) {missing}")
    bad = df.loc[~df["label"].isin(LABELS), "qid"].tolist()
    if bad:
        raise ValueError(f"{path.name}: unknown label for qid(s) {bad}")
    duplicated = df.loc[df["qid"].duplicated(), "qid"].tolist()
    if duplicated:
        raise ValueError(f"{path.name}: duplicate qid(s) {duplicated}")
    return df[["qid", "label"]]


def align(a: pd.DataFrame, b: pd.DataFrame) -> pd.DataFrame:
    """Put both annotators' labels side by side; both must label the same questions."""
    only_a = sorted(set(a["qid"]) - set(b["qid"]))
    only_b = sorted(set(b["qid"]) - set(a["qid"]))
    if only_a or only_b:
        raise ValueError(f"Different questions: only in A {only_a}, only in B {only_b}")
    merged = a.merge(b, on="qid", suffixes=("_a", "_b"))
    if merged.empty:
        raise ValueError("No questions to compare")
    return merged.sort_values("qid").reset_index(drop=True)


def to_decision(label: str) -> str:
    """Three labels -> the two system decisions (same mapping as the evaluation)."""
    return "answer" if label == "answerable" else "refuse"


def agreement_report(merged: pd.DataFrame) -> dict:
    """Observed agreement and Cohen's kappa for 3 labels and for answer/refuse."""
    a, b = merged["label_a"], merged["label_b"]
    decision_a, decision_b = a.map(to_decision), b.map(to_decision)
    return {
        "n": len(merged),
        "agreement_3": float((a == b).mean()),
        "kappa_3": float(cohen_kappa_score(a, b)),
        "agreement_2": float((decision_a == decision_b).mean()),
        "kappa_2": float(cohen_kappa_score(decision_a, decision_b)),
        "disagreements": merged.loc[a != b, ["qid", "label_a", "label_b"]],
        "confusion": pd.crosstab(a, b, rownames=["A"], colnames=["B"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Cohen's kappa between two annotators.")
    parser.add_argument("--a", type=Path, required=True, help="first annotator's CSV (qid,label)")
    parser.add_argument("--b", type=Path, required=True, help="second annotator's CSV (qid,label)")
    args = parser.parse_args()

    merged = align(load_annotations(args.a), load_annotations(args.b))
    report = agreement_report(merged)

    print(f"Questions labelled by both: {report['n']}")
    print(f"3 labels      : agreement {report['agreement_3']:.3f}, Cohen's kappa {report['kappa_3']:.3f}")
    print(f"answer/refuse : agreement {report['agreement_2']:.3f}, Cohen's kappa {report['kappa_2']:.3f}")
    print("\nWho labelled what (rows A, columns B):")
    print(report["confusion"].to_string())
    print(f"\nDisagreements ({len(report['disagreements'])}): discuss them and add a rule to the guidelines")
    print(report["disagreements"].to_string(index=False))


if __name__ == "__main__":
    main()
