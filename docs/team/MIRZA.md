# MIRZA ČAKAL — retrieval pipeline i answerability klasifikator

> Lične upute za Mirzu i Mirzinog Claude-a. Razrađuje `TEAM_PLAN.md` §4.1. Pravila: `TEAM_PLAN.md` §1, `HANDOFF.md` §12. Ako se nešto kosi, važi `course/` → `TEAM_PLAN.md` → ovaj fajl.
>
> GitHub: `@MirzaCakal-student` · Lokalne bilješke: `study/mirza/` · Dnevnik sesija: dno ovog fajla.

---

## 1. Tvoja uloga u jednoj rečenici

Ti gradiš **NLP srž sistema**: od teksta izloška do odluke "odgovori / odbij". To je dio koji profesorica boduje kao "team-built NLP component", pa na odbrani moraš najbolje znati chunking, BM25, e5, cross-encoder, fine-tuning i prag.

## 2. Fajlovi koje posjeduješ

| Fajl | Šta radi | Status |
| --- | --- | --- |
| `pyproject.toml`, `uv.lock` | Zavisnosti (zajedničko, ali ti ih uređuješ) | ☐ `uv.lock` fali |
| `src/talking_exhibits/data.py` | Učitavanje i validacija izložaka i pitanja | ☐ |
| `src/talking_exhibits/preprocess.py` | `normalize`, `strip_diacritics`, `split_sentences`, `chunk` | ☐ |
| `src/talking_exhibits/retrieval.py` | `bm25_search`, `e5_search`, keš embeddinga | ☐ |
| `src/talking_exhibits/answerability.py` | Klasifikator: trening i inferenca (poslije M3) | ☐ |
| `scripts/run_baselines.py` | B0, B1, B1b na val + izbor praga | ☐ |
| `scripts/train_classifier.py` + `notebooks/` | Fine-tuning na Colabu (poslije M3) | ☐ |
| `tests/test_data.py`, `tests/test_preprocess.py`, `tests/test_retrieval.py` | pytest | ☐ |

Tuđe fajlove (`data/exhibits/`, `data/questions/`, `evaluate.py`, ...) ne mijenjaš bez dogovora s vlasnikom.

## 3. Ovisnosti: šta čekaš i ko čeka tebe

| Čekaš od | Šta | Do kad |
| --- | --- | --- |
| Tarik | Konačan format JSON-a izložaka i prvi 2–3 izloška | 13.11 |
| Tarik | Šema `questions.csv` + validator | 14.11 |
| Kerim | `evaluate.py` (`refuse_metrics`) da B1 rezultati budu u istom formatu | 16.11 |

| Čeka tebe | Šta | Do kad |
| --- | --- | --- |
| Svi | `uv.lock` + `pytest` + `tests/` | **odmah** |
| Tarik | `load_exhibits` (njegov validator i `build_dataset.py` ga koriste) | 14.11 |
| Kerim | Predikcije B0/B1/B1b u `results/` za `evaluate_all.py` | 19.11 |

## 4. Zadaci do M3, korak po korak

### M-0 Zajednički setup (odmah, ~20 min)
1. `uv add --dev pytest`
2. `uv lock` pa `uv sync`
3. Napravi `tests/__init__.py` (prazan) i `tests/test_smoke.py` koji samo importuje `talking_exhibits`.
4. `uv run pytest` → mora proći.
5. Commit `pyproject.toml`, `uv.lock`, `tests/` i javi timu: "`git pull` + `uv sync`".

**Gotovo kad:** svi na svom računaru dobiju zelen `uv run pytest`.

### M-1 `data.py` (kasni, novi rok 14.11, ~2 h)
1. Konstante s obaveznim poljima: `EXHIBIT_FIELDS = ["id", "title", "lang", "text", "sources"]`, `QUESTION_COLUMNS` iz `HANDOFF.md` §5.2 (uključujući `source`).
2. `load_exhibits(dir) -> pd.DataFrame`: čita sve `*.json`, provjerava polja, `lang ∈ {bs, en}`, `text` nije prazan, `sources` je lista. Greška kaže **koji fajl i koje polje** (kao `collect.py` u Lab 01).
3. `load_questions(path) -> pd.DataFrame`: provjera kolona, prazni stringovi umjesto `NaN`.
4. Testovi s malim izmišljenim izlošcima u `tests/fixtures/` (ne pravi IBU tekstovi): ispravan fajl prolazi; fajl bez `sources` daje jasnu grešku; pogrešan `lang` daje grešku.

**Gotovo kad:** `uv run pytest tests/test_data.py` prolazi.
**Pitanje za odbranu:** zašto provjera kolona odmah na ulazu, a ne kasnije?

### M-2 `preprocess.py` (kasni, novi rok 14.11, ~3 h)
1. `normalize(text)`: lowercase, sređeni razmaci, **dijakritike se čuvaju** (č, ć, š, ž, đ nose značenje: *kuća* ≠ *kuca*).
2. `strip_diacritics(text)`: samo pomoćna, za mjerenje koliko pitanja nema dijakritike i za eksperiment.
3. `split_sentences(text)`: regex za kraj rečenice, pazi na skraćenice (npr., dr., god.).
4. `chunk(text, size=120, overlap=30)`: pasusi od cijelih rečenica, ~120 riječi, ~30 riječi preklapanja.
5. Testovi: nijedna rečenica nije izgubljena; overlap je tačan; kratak tekst daje 1 pasus; prazan tekst daje grešku.

**Gotovo kad:** testovi prolaze, a ručno si pogledao chunkove jednog Tarikovog izloška.
**Koncept:** sedmica 2 (tokenizacija, normalizacija, segmentacija rečenica).
**Pitanje za odbranu:** šta bi se desilo s BM25 da brišemo dijakritike u tekstu, a pitanja posjetilaca ih imaju?

### M-3 BM25 retrieval (rok 13.11 → realno 15.11, ~3 h)
1. `rank-bm25` (`BM25Okapi`) nad pasusima **jednog** izloška (svaki izložak ima svoj indeks).
2. `bm25_search(question, exhibit_id, k=3) -> list[(passage_id, text, score)]`.
3. Tokenizacija ista za pitanje i pasus (koristi `normalize`).
4. Ručna provjera: 10 pitanja, je li pravi pasus u top-3. Zapiši rezultat u `study/mirza/LEARNING_LOG.md` (stvarni broj).

**Gotovo kad:** test na fixture izlošku + ručna provjera upisana.
**Koncepti:** TF-IDF (sedmica 7), BM25 (k1, b, normalizacija dužine), sedmica 13 (semantic search).

### M-4 Dense retrieval e5 (rok 19.11, ~3 h)
1. `sentence-transformers` + `intfloat/multilingual-e5-base`.
2. **Obavezni prefiksi:** `"query: "` za pitanje, `"passage: "` za pasus. Bez njih model radi lošije.
3. Normalizovani embeddingi → kosinusna sličnost = dot product.
4. Keš u `data/processed/embeddings_<exhibit>.npy` (nije u gitu).
5. Recall@3 za BM25 i e5 na **val**, samo answerable pitanja.

**Gotovo kad:** tabela Recall@3 (BM25 vs e5, po jeziku) iz stvarnog pokretanja.
**Pazi:** prvi download modela ~1 GB. Na CPU je spor, ali za ~300 pitanja je OK.

### M-5 `scripts/run_baselines.py`: B0, B1, B1b (rok 19.11, ~3 h)
1. B0: uvijek `answer`.
2. B1: `max BM25 score < prag → refuse`. Prag bira grid search na **val** i maksimizira refuse-F1 (koristi Kerimov `refuse_metrics`).
3. B1b: isto s e5 kosinusom.
4. Snimi predikcije `results/val_predictions_{b0,b1,b1b}.csv` (kolone dogovori s Kerimom: `qid, system, score, pred`) i `results/val_baselines.json`.
5. Tabela u terminalu. **Test set se NE dira.**

**Gotovo kad:** `uv run python scripts/run_baselines.py` od nule daje iste brojeve (seed 3004).
**Pitanje za odbranu:** zašto prag biramo na val, a ne na test? Šta bi bilo da biramo na test?

### M-6 Paper: Literature Review, tvoja polovina (rok 22.11)
Bar 4 izvora, svaki **otvoren i pročitan**, ubačen u Zotero:
- Robertson & Zaragoza (2009), BM25
- Karpukhin et al. (2020), DPR
- Wang et al. (2024), Multilingual E5
- Lewis et al. (2020), RAG
- Conneau et al. (2020), XLM-R
- Ljubešić & Lauc (2021), BERTić

Piši svojim riječima: šta rad radi, šta nalazi, kako se odnosi na nas. Claude smije objasniti rad, ali tekst u Google Docs pišeš ti, i to ide u AI_LOG.

### M-7 Pitanja (pisanje 16.11, provjera 19.11)
- 100 pitanja (50 BS, 50 EN) za izloške koje ti Tarik dodijeli, po `docs/annotation_guidelines.md`.
- Raspodjela: ~45 answerable, ~40 unanswerable_plausible, ~15 out_of_scope; ~10 BS pitanja bez dijakritika.
- Ti provjeravaš **Kerimova** pitanja (`checked_by = mirza`).
- **Pitanja pišeš sam.** Claude ih smije samo provjeriti (format, `answer_start`, da li klasa odgovara guidelinesu).

## 5. Checklist za M3 (tvoj dio)
- ☐ `uv.lock` i `pytest` u gitu
- ☐ `data.py` + testovi
- ☐ `preprocess.py` + testovi
- ☐ `retrieval.py` (BM25 + e5) + testovi
- ☐ `run_baselines.py` → B0, B1, B1b rezultati na val
- ☐ Recall@3 tabela
- ☐ README: sekcija "How to run" za tvoje skripte
- ☐ Literature Review: 4+ izvora
- ☐ 100 pitanja napisano, Kerimova provjerena
- ☐ AI_LOG i CONTRIBUTIONS upisani (sam)
- ☐ Znaš za 5 minuta objasniti: chunking → BM25 → prag → rezultat

## 6. Poslije M3 (24.11 → kraj)
1. `answerability.py` + `scripts/train_classifier.py`: XLM-R-base cross-encoder, `[CLS] pitanje [SEP] pasus [SEP]`, SQuAD 2.0 podskup (30–50k) + dodatni negativi + naš train. Postavke: `max_length=384`, lr 2e-5, batch 16, 2–3 epohe, warmup 10%, seed 3004.
2. Trening na **Colabu/Kaggleu** (tvoj AMD GPU nema CUDA). Notebook samo poziva `scripts/train_classifier.py`; logika je u `src/`. Model u `models/` (van gita), a README kaže kako se dobije.
3. Odluka na nivou izloška: `max p(answerable)` preko top-k pasusa, prag na val.
4. Ablacije: M-zs (samo SQuAD) za RQ3; opcionalno BERTić.
5. Zaključaj konfiguraciju → tek onda **jedno** pokretanje na testu (s Kerimom).
6. Paper: Methodology.

## 7. Šta moraš znati na odbrani
- Zašto cross-encoder, a ne bi-encoder (zajednička pažnja nad pitanjem i pasusom vs odvojeni vektori; brzina vs tačnost).
- BM25 formula: TF zasićenje (k1), normalizacija dužine (b), IDF.
- Zašto e5 treba `query:` / `passage:`.
- Zašto chunking s overlapom (odgovor ne smije pasti na granicu pasusa).
- Zašto se dijakritike čuvaju.
- Zašto prag na val, a izvještaj na test.
- Kako se iz SQuAD 2.0 prave parovi i zašto dodajemo out-of-scope negative.
- Kako se cijeli trening reproducira iz jedne komande.

## 8. Kako početi sesiju s Claude-om
1. `git pull` → `uv sync`
2. Pokreni Claude Code u repou. Ako je prva sesija, zalijepi `PROMPT_CLAUDE_CODE.md`.
3. Reci mu: *"Radim kao Mirza. Pročitaj `docs/team/MIRZA.md` i zadnji unos u dnevniku, pa predloži sljedeći zadatak."*
4. Na kraju: pregledaj `git diff`, upiši AI_LOG i CONTRIBUTIONS, pa **sam** `git add` / `commit` / `push`.

---

## Dnevnik sesija (handoff)

Najnoviji unos na vrhu. Piše Claude na kraju sesije (`TEAM_PLAN.md` §1.5).

### 2026-11-12 — usklađivanje planova i lične upute
- **Urađeno:** HANDOFF.md i TEAM_PLAN.md usklađeni s `course/` (kolona `source`, `uv.lock`/`pytest`, ≥10 citata za finalni paper, nejasnoća oko sedmice 14, pravilo o handoffu). Napravljeni `docs/team/MIRZA.md`, `TARIK.md`, `KERIM.md`. Ažurirani `CLAUDE.md` i `PROMPT_CLAUDE_CODE.md`.
- **Stvarni rezultati:** nema (kod još nije pisan).
- **Sljedeće:** M-0 setup (`uv.lock`, `pytest`), pa M-1 `data.py` i M-2 `preprocess.py` do 14.11.
- **Blokade / čekam na:** Tarikov format JSON-a izložaka.
- **Ciljevi do M3:** B0/B1/B1b na val, Recall@3, 4 izvora, 100 pitanja.

### 2026-11-08 — uvodna sesija
- **Urađeno:** pročitan sav kontekst i `course/`; napravljen `study/mirza/`.
- **Stvarni rezultati:** nema.
- **Sljedeće:** M-1, M-2.
