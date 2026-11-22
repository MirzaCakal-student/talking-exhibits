import importlib.util
from pathlib import Path

import pandas as pd
import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "make_kappa_sample.py"
spec = importlib.util.spec_from_file_location("make_kappa_sample", SCRIPT)
mks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mks)


def _questions():
    rows = []
    for author in ("kerim", "tarik"):
        for i in range(30):
            rows.append({"qid": f"{author}{i}", "exhibit_id": "ex", "lang": "en",
                         "question": f"q {author} {i}", "label": "answerable",
                         "author": author})
    return pd.DataFrame(rows)


def test_same_number_per_author_and_labels_hidden():
    q = _questions()
    s = mks.make_sample(q, per_author=10)
    authors = q.set_index("qid").loc[s["qid"], "author"].value_counts().to_dict()
    assert authors == {"kerim": 10, "tarik": 10}
    assert list(s.columns) == ["qid", "exhibit_id", "lang", "question", "label"]
    assert (s["label"] == "").all()
    assert not s["qid"].duplicated().any()


def test_same_seed_gives_same_sample():
    q = _questions()
    assert mks.make_sample(q, 10)["qid"].tolist() == mks.make_sample(q, 10)["qid"].tolist()


def test_too_few_questions_raises():
    with pytest.raises(ValueError):
        mks.make_sample(_questions(), per_author=31)
