"""Run the baselines B0, B1 (BM25 + threshold) and B1b (e5 + threshold).

Usage (real data, after scripts/build_dataset.py has made the split):

    uv run python scripts/run_baselines.py

Smoke test on the fictional fixtures (no real data needed):

    uv run python scripts/run_baselines.py --exhibits tests/fixtures/exhibits \
        --questions tests/fixtures/questions_val.csv --out results/fixture_demo

What it does, step by step:
  1. load the exhibits and cut them into passages;
  2. for every question, retrieve the top-k passages of ITS exhibit and keep
     the best score (BM25 score, e5 cosine);
  3. B0 always answers; B1/B1b refuse when the best score is below a threshold;
  4. the threshold is chosen on these (validation) questions by trying every
     candidate and keeping the one with the highest F1 of the class "refuse";
  5. print a table and save predictions + metrics to the output folder.

The test split is never read here: the script stops if it sees test rows.
"""

import argparse
import json
import random
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# The package lives in src/ (the project is not installed as a package).
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from talking_exhibits.data import load_exhibits, load_questions  # noqa: E402
from talking_exhibits.preprocess import chunk_exhibits  # noqa: E402
from talking_exhibits.retrieval import (  # noqa: E402
    E5_MODEL_NAME,
    bm25_search,
    build_bm25_index,
    build_e5_index,
    e5_search,
    load_e5_model,
)

SEED = 3004
ANSWER, REFUSE = "answer", "refuse"


def to_gold_decision(label):
    """Three question classes -> two decisions. Only 'answerable' is answered."""
    return ANSWER if label == "answerable" else REFUSE


def refuse_metrics(gold, pred):
    """Precision, recall and F1 of the class 'refuse', plus false refusal rate.

    TODO(team): switch to talking_exhibits.evaluate.refuse_metrics once Kerim's
    evaluate.py is in the repository, so every number comes from one place.
    """
    gold = np.asarray(gold)
    pred = np.asarray(pred)
    true_refuse = int(((gold == REFUSE) & (pred == REFUSE)).sum())
    false_refuse = int(((gold == ANSWER) & (pred == REFUSE)).sum())
    missed_refuse = int(((gold == REFUSE) & (pred == ANSWER)).sum())
    n_answerable = int((gold == ANSWER).sum())

    precision = true_refuse / (true_refuse + false_refuse) if true_refuse + false_refuse else 0.0
    recall = true_refuse / (true_refuse + missed_refuse) if true_refuse + missed_refuse else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "refuse_precision": precision,
        "refuse_recall": recall,
        "refuse_f1": f1,
        # Share of answerable questions that the system wrongly refused.
        "false_refusal_rate": false_refuse / n_answerable if n_answerable else 0.0,
    }


def decide(scores, threshold):
    """Refuse when the best retrieval score is below the threshold."""
    return np.where(np.asarray(scores) < threshold, REFUSE, ANSWER)


def choose_threshold(scores, gold):
    """Grid search: try a threshold between every two neighbouring scores.

    Returns the threshold with the highest refuse-F1. Ties go to the lowest
    threshold (it refuses the fewest questions).
    """
    unique = np.unique(scores)
    candidates = [unique[0] - 1e-6]  # refuse nothing
    candidates += [(a + b) / 2 for a, b in zip(unique, unique[1:])]
    candidates += [unique[-1] + 1e-6]  # refuse everything

    best_threshold, best_f1 = candidates[0], -1.0
    for threshold in candidates:
        f1 = refuse_metrics(gold, decide(scores, threshold))["refuse_f1"]
        if f1 > best_f1:
            best_threshold, best_f1 = float(threshold), f1
    return best_threshold


def score_questions(questions, search, k):
    """Best retrieval score per question and whether the answer was retrieved.

    ``search(question, exhibit_id, lang, k)`` returns the top-k passages.
    ``hit`` is True/False for answerable questions (is the gold answer text
    inside one of the top-k passages?) and None for the other classes.
    """
    scores, hits = [], []
    for q in questions.itertuples(index=False):
        top = search(q.question, q.exhibit_id, q.lang, k)
        scores.append(float(top.iloc[0]["score"]))
        if q.label == "answerable":
            answer = " ".join(q.answer_text.split())
            hits.append(any(answer in text for text in top["text"]))
        else:
            hits.append(None)
    return scores, hits


def recall_at_k(questions, hits):
    """Share of answerable questions whose answer is in the top-k passages."""
    result = {}
    hits = pd.Series(hits, index=questions.index)
    answerable = questions["label"] == "answerable"
    for name, mask in [("all", answerable)] + [
        (lang, answerable & (questions["lang"] == lang)) for lang in sorted(questions["lang"].unique())
    ]:
        if mask.any():
            result[name] = float(hits[mask].astype(bool).mean())
    return result


def metrics_by_language(questions, gold, pred):
    """refuse_metrics for all questions and for each language separately."""
    result = {"all": refuse_metrics(gold, pred)}
    for lang in sorted(questions["lang"].unique()):
        mask = (questions["lang"] == lang).to_numpy()
        result[lang] = refuse_metrics(np.asarray(gold)[mask], np.asarray(pred)[mask])
    return result


def save_predictions(out_dir, questions, system, scores, threshold, pred, gold):
    """One CSV per system: qid, system, score, threshold, pred, gold."""
    table = pd.DataFrame(
        {
            "qid": questions["qid"],
            "system": system,
            "score": scores,
            "threshold": threshold,
            "pred": pred,
            "gold": gold,
        }
    )
    path = out_dir / f"val_predictions_{system}.csv"
    table.to_csv(path, index=False, encoding="utf-8")
    print(f"  saved {path}")


def main():
    parser = argparse.ArgumentParser(description="Baselines B0, B1 (BM25) and B1b (e5).")
    parser.add_argument("--exhibits", default="data/exhibits", help="folder with exhibit JSON files")
    parser.add_argument("--questions", default="data/processed/val.csv", help="validation questions CSV")
    parser.add_argument("--out", default="results", help="output folder")
    parser.add_argument("--k", type=int, default=3, help="passages retrieved per question")
    parser.add_argument("--chunk-size", type=int, default=120, help="passage size in words")
    parser.add_argument("--overlap", type=int, default=30, help="passage overlap in words")
    parser.add_argument("--no-e5", action="store_true", help="skip B1b (no model download)")
    parser.add_argument("--cache", default="data/processed", help="folder for cached e5 embeddings")
    args = parser.parse_args()

    random.seed(SEED)
    np.random.seed(SEED)

    print("1. Loading data")
    exhibits = load_exhibits(args.exhibits)
    questions = load_questions(args.questions).reset_index(drop=True)
    if (questions["split"] == "test").any():
        raise SystemExit("These questions contain test rows. Baselines are tuned on val only.")
    passages = chunk_exhibits(exhibits, size=args.chunk_size, overlap=args.overlap)
    print(f"  {len(exhibits)} exhibit texts -> {len(passages)} passages")
    print(f"  {len(questions)} questions: {questions['label'].value_counts().to_dict()}")

    gold = questions["label"].map(to_gold_decision).to_numpy()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "config": {
            "seed": SEED,
            "k": args.k,
            "chunk_size": args.chunk_size,
            "overlap": args.overlap,
            "exhibits": args.exhibits,
            "questions": args.questions,
            "n_questions": len(questions),
            "n_passages": len(passages),
            "threshold_selected_on": "the same (validation) questions that are reported",
        },
        "systems": {},
    }

    print("2. B0: always answer")
    pred = np.full(len(questions), ANSWER)
    report["systems"]["b0"] = {"metrics": metrics_by_language(questions, gold, pred)}
    save_predictions(out_dir, questions, "b0", np.nan, np.nan, pred, gold)

    print("3. B1: BM25 + threshold")
    bm25_index = build_bm25_index(passages)
    scores, hits = score_questions(
        questions, lambda q, e, lang, k: bm25_search(q, e, lang, bm25_index, k), args.k
    )
    threshold = choose_threshold(scores, gold)
    pred = decide(scores, threshold)
    report["systems"]["b1_bm25"] = {
        "threshold": threshold,
        "metrics": metrics_by_language(questions, gold, pred),
        f"recall_at_{args.k}": recall_at_k(questions, hits),
    }
    save_predictions(out_dir, questions, "b1_bm25", scores, threshold, pred, gold)

    if not args.no_e5:
        print(f"4. B1b: e5 + threshold (model: {E5_MODEL_NAME})")
        model = load_e5_model()
        e5_index = build_e5_index(passages, model, cache_dir=args.cache)
        scores, hits = score_questions(
            questions, lambda q, e, lang, k: e5_search(q, e, lang, e5_index, k), args.k
        )
        threshold = choose_threshold(scores, gold)
        pred = decide(scores, threshold)
        report["systems"]["b1b_e5"] = {
            "threshold": threshold,
            "metrics": metrics_by_language(questions, gold, pred),
            f"recall_at_{args.k}": recall_at_k(questions, hits),
        }
        save_predictions(out_dir, questions, "b1b_e5", scores, threshold, pred, gold)

    report_path = out_dir / "val_baselines.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"  saved {report_path}")

    print("\nResults on the validation questions (threshold chosen on the same questions)")
    header = f"{'system':<10}{'lang':<6}{'refuse P':>10}{'refuse R':>10}{'refuse F1':>11}{'false ref.':>12}{'recall@' + str(args.k):>11}"
    print(header)
    print("-" * len(header))
    for system, result in report["systems"].items():
        recall = result.get(f"recall_at_{args.k}", {})
        for lang, m in result["metrics"].items():
            recall_text = f"{recall[lang]:.3f}" if lang in recall else "-"
            print(
                f"{system:<10}{lang:<6}{m['refuse_precision']:>10.3f}{m['refuse_recall']:>10.3f}"
                f"{m['refuse_f1']:>11.3f}{m['false_refusal_rate']:>12.3f}{recall_text:>11}"
            )


if __name__ == "__main__":
    main()
