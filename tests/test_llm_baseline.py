import io
import json
from unittest.mock import Mock
from urllib.error import HTTPError, URLError

import pandas as pd
import pytest

from talking_exhibits import llm_baseline as b2
from talking_exhibits.retrieval import bm25_search, build_bm25_index


def mock_response(monkeypatch, payload):
    body = payload if isinstance(payload, bytes) else json.dumps(payload).encode("utf-8")
    transport = Mock(return_value=io.BytesIO(body))
    monkeypatch.setattr(b2, "urlopen", transport)
    return transport


def mock_answer(monkeypatch, answer):
    return mock_response(monkeypatch, {
        "done": True, "done_reason": "stop", "message": {"content": answer},
    })


def sent_payload(transport):
    request = transport.call_args.args[0]
    return json.loads(request.data)


@pytest.mark.parametrize("question,passage,answer", [
    ("Koliko čitaonica ima biblioteka?", "Biblioteka ima dvije čitaonice.", "dvije čitaonice"),
    ("How many rooms are there?", "There are two study rooms.", "two study rooms"),
])
def test_answers_bs_and_en_with_deterministic_chat(monkeypatch, question, passage, answer):
    transport = mock_answer(monkeypatch, f"\n{answer} \n")

    result = b2.answer_question(question, passage, model="local-qwen", timeout=5.0)

    assert result == answer
    assert b2.to_prediction(result) == "answer"
    request = transport.call_args.args[0]
    assert request.get_method() == "POST"
    assert request.full_url == "http://127.0.0.1:11434/api/chat"
    assert request.get_header("Content-type") == "application/json"
    assert transport.call_args.kwargs["timeout"] == 5.0
    payload = sent_payload(transport)
    assert payload["model"] == "local-qwen"
    assert payload["stream"] is False
    assert payload["options"] == {"temperature": 0, "seed": 3004}
    system, user = payload["messages"]
    assert system["role"] == "system"
    instruction = system["content"]
    assert "explicitly answers the entire question" in instruction
    assert "Mentioning the same topic or a related name is insufficient" in instruction
    assert instruction.index("exactly: NOT_IN_TEXT") < instruction.index("exact quote")
    assert user["role"] == "user"
    assert json.loads(user["content"]) == {"question": question, "passages": [passage]}


@pytest.mark.parametrize("model_reply", [" NOT_IN_TEXT\n", "Paris", "Room 12"])
def test_returns_exact_refusal_for_missing_or_unsupported_answers(monkeypatch, model_reply):
    mock_answer(monkeypatch, model_reply)

    result = b2.answer_question("Where is the office?", ["Room", "12"])

    assert result == "NOT_IN_TEXT"
    assert b2.to_prediction(result) == "refuse"


@pytest.mark.parametrize("question,passages", [
    (" \n", ["The library has two rooms."]),
    ("Where is it?", []),
    ("Where is it?", ["", " \t"]),
])
def test_empty_input_skips_ollama(monkeypatch, question, passages):
    transport = Mock()
    monkeypatch.setattr(b2, "urlopen", transport)

    assert b2.answer_question(question, passages) == "NOT_IN_TEXT"
    transport.assert_not_called()


@pytest.mark.parametrize("error,match", [
    (HTTPError("http://localhost", 404, "Not Found", {}, None), "404.*installed model"),
    (HTTPError("http://localhost", 503, "Unavailable", {}, None), "HTTP 503"),
    (URLError("connection refused"), "Ollama request.*connection refused"),
    (TimeoutError("timed out"), "Ollama request.*timed out"),
])
def test_ollama_transport_errors_are_not_predictions(monkeypatch, error, match):
    monkeypatch.setattr(b2, "urlopen", Mock(side_effect=error))

    with pytest.raises(b2.OllamaError, match=match):
        b2.answer_question("Where is the office?", ["It is in room 12."])


@pytest.mark.parametrize("payload,match", [
    (b"{bad json", "invalid JSON"),
    (b"\xff\x00\xff", "invalid JSON"),
    ([], "malformed or incomplete"),
    ({"done": False, "message": {"content": "room 12"}}, "malformed or incomplete"),
    ({"done": True, "message": {}}, "missing or empty"),
    ({"done": True, "message": {"content": " "}}, "missing or empty"),
    ({"done": True, "message": {"content": 12}}, "missing or empty"),
    ({"done": True, "done_reason": "length", "message": {"content": "room"}}, "length limit"),
])
def test_invalid_or_truncated_chat_responses_raise(monkeypatch, payload, match):
    mock_response(monkeypatch, payload)

    with pytest.raises(b2.OllamaError, match=match):
        b2.answer_question("Where is the office?", ["It is in room 12."])


def test_reuses_bm25_search_without_sending_other_exhibits_or_languages(monkeypatch):
    passages = pd.DataFrame([
        ("library", "bs", "library_bs_p0", "Biblioteka ima čitaonicu."),
        ("library", "en", "library_en_p0", "The library has a study room."),
        ("museum", "bs", "museum_bs_p0", "Muzej ima galeriju."),
    ], columns=["exhibit_id", "lang", "passage_id", "text"])
    index = build_bm25_index(passages)
    search = Mock(side_effect=lambda q, e, lang, k: bm25_search(q, e, lang, index, k))
    transport = mock_answer(monkeypatch, "čitaonicu")
    question = "Šta ima biblioteka?"

    assert b2.answer_with_retrieval(question, "library", "bs", search, k=2) == "čitaonicu"
    search.assert_called_once_with(question, "library", "bs", 2)
    context = json.loads(sent_payload(transport)["messages"][1]["content"])
    assert context["passages"] == ["Biblioteka ima čitaonicu."]


def test_retrieval_with_no_matching_passages_refuses_without_ollama(monkeypatch):
    search = Mock(return_value=pd.DataFrame({
        "passage_id": ["library_en_p0", "museum_bs_p0"],
        "text": ["The library has a study room.", "Muzej ima galeriju."],
    }))
    transport = Mock()
    monkeypatch.setattr(b2, "urlopen", transport)

    assert b2.answer_with_retrieval("Šta ima biblioteka?", "library", "bs", search) == "NOT_IN_TEXT"
    transport.assert_not_called()
