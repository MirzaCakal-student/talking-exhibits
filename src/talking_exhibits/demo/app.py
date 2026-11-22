"""Serve exhibit pages, locally generated QR codes and grounded answers."""

import logging
import os
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

import qrcode
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from qrcode.image.svg import SvgPathFillImage

from talking_exhibits.data import load_exhibits
from talking_exhibits.llm_baseline import (
    DEFAULT_BASE_URL,
    DEFAULT_MODEL,
    OllamaError,
    PassageSelector,
    answer_with_retrieval,
    to_prediction,
)
from talking_exhibits.preprocess import chunk_exhibits
from talking_exhibits.retrieval import bm25_search, build_bm25_index

HERE = Path(__file__).resolve().parent
EXHIBITS_DIR = HERE.parents[2] / "data" / "exhibits"
MAX_QUESTION_LENGTH = 500
LANGUAGES = {"bs": "Bosanski", "en": "English"}
COPY = {
    "bs": {
        "exhibits": "Izlošci",
        "browse": "Odaberite izložak i postavite pitanje o njegovom tekstu.",
        "missing": "Izložak ili jezička verzija nije dostupna.",
        "question": "Šta želite znati o ovom izlošku?",
        "placeholder": "Upišite svoje pitanje na bosanskom…",
        "submit": "Postavi pitanje",
        "loading": "Tražimo odgovor u tekstu izloška…",
        "empty": "Upišite pitanje prije slanja.",
        "refused": "U tekstu izloška nema dovoljno informacija za odgovor.",
        "unavailable": "Lokalni model trenutno nije dostupan. Pokušajte ponovo kasnije.",
        "error": "Došlo je do greške pri obradi pitanja. Pokušajte ponovo.",
        "answer": "Odgovor iz teksta",
        "qr": "Otvori na telefonu",
        "qr_alt": "QR kod za ovaj izložak",
        "qr_download": "Preuzmi QR kod",
        "read": "Pročitaj tekst izloška",
        "sources": "Izvori",
        "language": "Jezik",
    },
    "en": {
        "exhibits": "Exhibits",
        "browse": "Choose an exhibit and ask a question about its text.",
        "missing": "This exhibit or language version is unavailable.",
        "question": "What would you like to know about this exhibit?",
        "placeholder": "Type your question in English…",
        "submit": "Ask a question",
        "loading": "Looking for an answer in the exhibit text…",
        "empty": "Enter a question before submitting.",
        "refused": "The exhibit text does not contain enough information to answer.",
        "unavailable": "The local model is currently unavailable. Please try again later.",
        "error": "Something went wrong while processing your question. Please try again.",
        "answer": "Answer from the text",
        "qr": "Open on your phone",
        "qr_alt": "QR code for this exhibit",
        "qr_download": "Download QR code",
        "read": "Read the exhibit text",
        "sources": "Sources",
        "language": "Language",
    },
}

logger = logging.getLogger(__name__)


class Question(BaseModel):
    question: str = Field(min_length=1, max_length=MAX_QUESTION_LENGTH)


def create_app(
    exhibits_dir: Path = EXHIBITS_DIR,
    *,
    base_url: str | None = None,
    select_passage: PassageSelector | None = None,
) -> FastAPI:
    """Load the exhibits once. An optional classifier adapter gates B2 generation."""
    base_url = (base_url or os.getenv("TALKING_EXHIBITS_BASE_URL", "")).rstrip("/")
    if base_url:
        url = urlsplit(base_url)
        if url.scheme not in {"http", "https"} or not url.hostname or any(
            (url.path, url.query, url.fragment, url.username, url.password)
        ):
            raise ValueError("TALKING_EXHIBITS_BASE_URL must be an HTTP(S) origin, e.g. http://192.168.1.5:8000")

    exhibits = load_exhibits(exhibits_dir)
    entries = {(row.id, row.lang): row for row in exhibits.itertuples(index=False)}
    search_index = build_bm25_index(chunk_exhibits(exhibits))
    model = os.getenv("OLLAMA_MODEL", DEFAULT_MODEL)
    ollama_url = os.getenv("OLLAMA_BASE_URL", DEFAULT_BASE_URL)
    templates = Jinja2Templates(directory=HERE / "templates")
    app = FastAPI(title="Talking Exhibits", docs_url=None, redoc_url=None, openapi_url=None)
    app.mount("/static", StaticFiles(directory=HERE / "static"), name="static")

    def search(question: str, exhibit_id: str, lang: str, k: int):
        return bm25_search(question, exhibit_id, lang, search_index, k=k)

    def page(request: Request, lang: str, exhibit=None, status: int = 200):
        language_options = [
            (code, name, app.url_path_for("exhibit", exhibit_id=exhibit.id, lang=code))
            if exhibit else (code, name, f"/?lang={code}")
            for code, name in LANGUAGES.items()
            if not exhibit or (exhibit.id, code) in entries
        ]
        return templates.TemplateResponse(
            request=request,
            name="page.html",
            status_code=status,
            context={
                "lang": lang, "words": COPY[lang], "exhibit": exhibit, "missing": status == 404,
                "exhibits": sorted((row for row in entries.values() if row.lang == lang), key=lambda row: row.title),
                "language_options": language_options, "max_question_length": MAX_QUESTION_LENGTH,
            },
        )

    @app.get("/", response_class=HTMLResponse)
    def index(request: Request, lang: Literal["bs", "en"] = "bs"):
        return page(request, lang)

    @app.get("/exhibits/{exhibit_id}/{lang}", response_class=HTMLResponse)
    def exhibit(request: Request, exhibit_id: str, lang: str):
        entry = entries.get((exhibit_id, lang))
        if entry is None:
            return page(request, lang if lang in COPY else "bs", status=404)
        return page(request, lang, entry)

    @app.get("/exhibits/{exhibit_id}/{lang}/qr.svg")
    def qr_code(request: Request, exhibit_id: str, lang: str):
        if (exhibit_id, lang) not in entries:
            raise HTTPException(404, COPY.get(lang, COPY["bs"])["missing"])
        destination = request.url_for("exhibit", exhibit_id=exhibit_id, lang=lang)
        if base_url:
            destination = base_url + destination.path
        svg = qrcode.make(str(destination), image_factory=SvgPathFillImage).to_string()
        return Response(svg, media_type="image/svg+xml", headers={"Cache-Control": "no-store"})

    @app.post("/exhibits/{exhibit_id}/{lang}/ask")
    def ask(exhibit_id: str, lang: str, body: Question):
        words = COPY.get(lang, COPY["bs"])
        if (exhibit_id, lang) not in entries:
            return JSONResponse({"status": "error", "message": words["missing"]}, status_code=404)

        question = body.question.strip()
        if not question:
            return JSONResponse({"status": "error", "message": words["empty"]}, status_code=400)

        try:
            answer = answer_with_retrieval(
                question, exhibit_id, lang, search,
                model=model, base_url=ollama_url, select_passage=select_passage,
            )
        except OllamaError as exc:
            logger.warning("Ollama inference failed: %s", exc)
            return JSONResponse({"status": "error", "message": words["unavailable"]}, status_code=503)
        except Exception:
            logger.exception("Exhibit question processing failed")
            return JSONResponse({"status": "error", "message": words["error"]}, status_code=500)

        prediction = to_prediction(answer)
        return {"status": prediction, "message": answer if prediction == "answer" else words["refused"]}

    return app
