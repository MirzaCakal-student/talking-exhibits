import io
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import Mock
from urllib.error import HTTPError, URLError

import pytest
from fastapi.testclient import TestClient

from talking_exhibits import llm_baseline as b2
from talking_exhibits.demo import app as demo

EXHIBITS = Path(__file__).parent / "fixtures" / "exhibits"
CAR = "/exhibits/lipa_solar_car"


@pytest.fixture
def client():
    with TestClient(demo.create_app(EXHIBITS)) as test_client:
        yield test_client


def mock_ollama(monkeypatch, answer):
    body = json.dumps({"done": True, "message": {"content": answer}}).encode("utf-8")
    transport = Mock(return_value=io.BytesIO(body))
    monkeypatch.setattr(b2, "urlopen", transport)
    return transport


def ollama_context(transport):
    payload = json.loads(transport.call_args.args[0].data)
    return json.loads(payload["messages"][1]["content"])


@pytest.mark.parametrize("lang, title, other", [
    ("bs", "Solarni automobil Lipa One", "en"),
    ("en", "The Lipa One Solar Car", "bs"),
])
def test_exhibit_navigation_and_form(client, lang, title, other):
    index = client.get(f"/?lang={lang}")
    assert f'href="{CAR}/{lang}"' in index.text

    page = client.get(f"{CAR}/{lang}")
    assert page.status_code == 200
    assert f'<html lang="{lang}">' in page.text
    assert f"<h1>{title}</h1>" in page.text
    assert f'href="{CAR}/{other}"' in page.text
    assert f'data-endpoint="{CAR}/{lang}/ask"' in page.text
    assert f'src="{CAR}/{lang}/qr.svg"' in page.text
    assert 'aria-live="polite"' in page.text
    assert client.get("/static/style.css").status_code == 200
    assert client.get("/static/ask.js").status_code == 200


@pytest.mark.parametrize("base_url, origin", [
    (None, "http://testserver"), ("http://192.168.1.5:8000/", "http://192.168.1.5:8000"),
])
def test_qr_encodes_the_exact_exhibit_and_language(monkeypatch, base_url, origin):
    monkeypatch.delenv("TALKING_EXHIBITS_BASE_URL", raising=False)
    make = Mock(wraps=demo.qrcode.make)
    monkeypatch.setattr(demo.qrcode, "make", make)

    with TestClient(demo.create_app(EXHIBITS, base_url=base_url)) as client:
        response = client.get(f"{CAR}/en/qr.svg")

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/svg+xml"
    make.assert_called_once_with(f"{origin}{CAR}/en", image_factory=demo.SvgPathFillImage)
    image = ET.fromstring(response.content)
    assert image.tag.endswith("}svg")
    assert image.find("{*}path") is not None


@pytest.mark.parametrize("lang, question, answer", [
    ("bs", "Koliko je težak automobil?", "310 kilograma"),
    ("en", "How much does the car weigh?", "310 kilograms"),
])
def test_asks_b2_using_real_scoped_bm25_and_localized_question(client, monkeypatch, lang, question, answer):
    transport = mock_ollama(monkeypatch, answer)
    response = client.post(f"{CAR}/{lang}/ask", json={"question": f"  {question}  "})

    assert response.status_code == 200
    assert response.json() == {"status": "answer", "message": answer}
    context = ollama_context(transport)
    assert context["question"] == question
    assert 1 <= len(context["passages"]) <= 3
    assert any(answer in text for text in context["passages"])
    exhibit = demo.load_exhibits(EXHIBITS).query("id == 'lipa_solar_car' and lang == @lang")
    assert set(context["passages"]) <= set(demo.chunk_exhibits(exhibit).text)


@pytest.mark.parametrize("lang, reply", [("bs", "NOT_IN_TEXT"), ("en", "Unsupported information")])
def test_model_refusal_and_unsupported_output_are_localized(client, monkeypatch, lang, reply):
    mock_ollama(monkeypatch, reply)
    response = client.post(f"{CAR}/{lang}/ask", json={"question": "?"})

    assert response.status_code == 200
    assert response.json() == {"status": "refuse", "message": demo.COPY[lang]["refused"]}


@pytest.mark.parametrize("failure", [
    URLError("connection refused"),
    HTTPError("http://localhost/api/chat", 404, "model missing", {}, None),
    None,
])
def test_ollama_errors_are_distinct_from_refusals(client, monkeypatch, failure):
    transport = Mock(side_effect=failure, return_value=io.BytesIO(b"invalid json"))
    monkeypatch.setattr(b2, "urlopen", transport)
    response = client.post(f"{CAR}/en/ask", json={"question": "How much does it weigh?"})

    assert response.status_code == 503
    assert response.json() == {"status": "error", "message": demo.COPY["en"]["unavailable"]}


@pytest.mark.parametrize("path, question, status", [
    (f"{CAR}/en/ask", "  ", 400),
    (f"{CAR}/en/ask", "a" * 501, 422),
    (f"{CAR}/de/ask", "Test", 404),
    ("/exhibits/unknown/en/ask", "Test", 404),
])
def test_invalid_input_never_reaches_model(client, monkeypatch, path, question, status):
    transport = Mock()
    monkeypatch.setattr(b2, "urlopen", transport)

    assert client.post(path, json={"question": question}).status_code == status
    transport.assert_not_called()


def test_optional_classifier_only_sends_approved_passage(monkeypatch):
    transport = mock_ollama(monkeypatch, "310 kilograms")
    selector = Mock(side_effect=lambda question, passages: next(text for text in passages if "310 kilograms" in text))

    with TestClient(demo.create_app(EXHIBITS, select_passage=selector)) as client:
        response = client.post(f"{CAR}/en/ask", json={"question": "How much does it weigh?"})

    question, passages = selector.call_args.args
    assert len(passages) > 1
    approved = next(text for text in passages if "310 kilograms" in text)
    assert ollama_context(transport) == {"question": question, "passages": [approved]}
    assert response.json() == {"status": "answer", "message": "310 kilograms"}


@pytest.mark.parametrize("selected, status, decision", [(None, 200, "refuse"), ("outside context", 500, "error")])
def test_classifier_gate_refuses_or_handles_invalid_selection_without_generation(monkeypatch, selected, status, decision):
    transport = Mock()
    monkeypatch.setattr(b2, "urlopen", transport)
    with TestClient(demo.create_app(EXHIBITS, select_passage=Mock(return_value=selected))) as client:
        response = client.post(f"{CAR}/en/ask", json={"question": "How much does it weigh?"})

    assert response.status_code == status
    assert response.json()["status"] == decision
    transport.assert_not_called()


def test_unknown_exhibit_displays_a_localized_page(client):
    response = client.get("/exhibits/unknown/en")

    assert response.status_code == 404
    assert demo.COPY["en"]["missing"] in response.text
    assert client.get("/exhibits/unknown/en/qr.svg").status_code == 404
