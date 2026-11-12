# KERIM HODŽIĆ — evaluacija, analiza podataka, LLM baseline, demo

> Lične upute za Kerima i Kerimovog Claude-a. Razrađuje `TEAM_PLAN.md` §4.3. Pravila: `TEAM_PLAN.md` §1, `HANDOFF.md` §12. Ako se nešto kosi, važi `course/` → `TEAM_PLAN.md` → ovaj fajl.
>
> GitHub: `@kerim279` · Lokalne bilješke: `study/kerim/` · Dnevnik sesija: dno ovog fajla.

---

## 1. Tvoja uloga u jednoj rečenici

Ti odlučuješ **kako se mjeri da li sistem radi**: guidelines za anotaciju, metrike, analizu podataka, poređenje sistema, analizu grešaka i kasnije LLM baseline i demo. Kurs traži "systematic evaluation" i "≥10 analyzed errors", pa bez tvog dijela nijedan broj ne vrijedi. Na odbrani moraš najbolje znati metrike (refuse-F1, AUROC, risk–coverage), bootstrap CI i analizu grešaka.

## 2. Fajlovi koje posjeduješ

| Fajl | Šta radi | Status |
| --- | --- | --- |
| `docs/annotation_guidelines.md` | Pravila za klase i granične slučajeve | ☐ (kasni) |
| `src/talking_exhibits/evaluate.py` | Metrike, bootstrap CI, confusion matrice | ☐ |
| `tests/test_metrics.py` | Testovi s ručno izračunatim primjerima | ☐ |
| `scripts/data_analysis.py` | Tabele i grafike o podacima | ☐ |
| `scripts/evaluate_all.py` | Jedna komanda → svi brojevi za paper | ☐ |
| `src/talking_exhibits/llm_baseline.py` | B2 prompted LLM (poslije M3) | ☐ |
| `demo/` | Web demo + QR (poslije glavne metode) | ☐ |
| `results/figures/`, `results/*.json`, `results/errors.csv` | Izlazi | ☐ |

## 3. Ovisnosti

| Čekaš od | Šta | Do kad |
| --- | --- | --- |
| Mirza | `uv.lock` + `pytest` + `tests/` | odmah |
| Tarik | Pitanja i split (`data/processed/*.csv`) | 19.11 |
| Mirza | Predikcije B0/B1/B1b u `results/` | 19.11 |

| Čeka tebe | Šta | Do kad |
| --- | --- | --- |
| **Svi** | **`annotation_guidelines.md` (bez njih se ne mogu pisati pitanja)** | **kasni, odmah (13.11)** |
| Mirza | `refuse_metrics` (za izbor praga u B1) | 16.11 |
| Svi | Tabele o podacima za paper i M3 | 19.11 |

## 4. Zadaci do M3, korak po korak

### K-1 `docs/annotation_guidelines.md` (kasni, rok 13.11, ~2–3 h)
1. Definicija svake klase s 2–3 primjera na BS i EN:
   - `answerable`: odgovor je eksplicitno u tekstu (+ tačan span).
   - `unanswerable_plausible`: na temu izloška, zvuči kao da bi trebalo biti tu, ali nije.
   - `out_of_scope`: nema veze s izloškom.
2. Granični slučajevi, svaki s pravilom i primjerom:
   - djelimičan odgovor (tekst daje godinu, pitanje traži datum)
   - odgovor koji traži zaključivanje ili računanje
   - brojevi riječima vs ciframa
   - sinonimi i parafraze
   - pitanje o drugom izlošku
   - pitanje bez dijakritika
   - više mogućih spanova
3. Pravilo za `answer_start`: prvi pun, najkraći span koji odgovara; char offset u tekstu **istog jezika**.
4. Pravilo za `source` (`human` / `llm_checked`); u test idu samo pitanja koja je čovjek napisao ili provjerio.
5. Tarik i Mirza pročitaju i potvrde (napišu "OK" u Discordu ili PR komentaru).

**Gotovo kad:** oba potvrdila. Kasnije se dopunjava pravilima iz rješavanja kappa nesuglasica.

### K-2 `evaluate.py` + `tests/test_metrics.py` (rok 16.11, ~4 h)
1. Mapiranje: `refuse = unanswerable_plausible ∪ out_of_scope`; pozitivna klasa je **refuse**.
2. `refuse_metrics(gold, pred) -> dict`: precision, recall, F1 za refuse.
3. `false_refusal_rate(gold, pred)`: udio answerable pitanja koja je sistem odbio.
4. `macro_f1(gold, pred)` za answer/refuse.
5. `confusion(gold_3class, pred_2class)`: posebno se vidi plausible vs out_of_scope.
6. `bootstrap_ci(metric_fn, gold, pred, n=1000, seed=3004) -> (low, high)`.
7. Sve funkcije primaju i opcioni filter po jeziku i klasi (BS vs EN = RQ3).
8. Testovi: **prvo ručno** izračunaj na papiru mali primjer (npr. 6 pitanja), pa test provjerava tačno te brojeve. Rubni slučaj: nijedan refuse u pred → F1 = 0, a ne pad programa.

**Gotovo kad:** `uv run pytest tests/test_metrics.py` prolazi, a ručni primjeri su u `study/kerim/`.
**Pitanje za odbranu:** zašto refuse-F1, a ne accuracy? (B0 "uvijek odgovori" ima ~45% accuracy, a refuse-F1 = 0)

### K-3 `scripts/data_analysis.py` (rok 19.11, ~3 h). M3 traži ≥2 tabele/grafika!
1. Tabela: broj pitanja po klasi × jeziku (i po splitu).
2. Histogram dužine pitanja (riječi) i dužine izložaka.
3. Udio BS pitanja bez dijakritika.
4. **Leksičko preklapanje** pitanja i teksta izloška po klasi (Jaccard nad tokenima). Hipoteza: plausible pitanja dijele mnogo riječi s tekstom, zato je BM25 prag slab. To je dobra rečenica za paper.
5. Figure u `results/figures/*.png` (matplotlib, čitljive oznake osa, bez naslova "Figure 1" u slici), tabele kao Markdown u `results/data_tables.md`.

### K-4 `scripts/evaluate_all.py`, prva verzija (rok 19.11, ~2 h)
1. Učita `results/val_predictions_*.csv` (format dogovori s Mirzom: `qid, system, score, pred`).
2. Spoji s gold labelama iz `data/processed/val.csv`.
3. Za svaki sistem izračuna sve metrike + CI, ukupno i po jeziku.
4. Snimi `results/metrics_val.json` i tabelu `results/metrics_val.md` za paper.
5. **Pravilo:** nijedan broj u paperu koji ne izlazi iz ove skripte.

### K-5 Paper: Introduction (rok 22.11)
Problem (halucinacije, pouzdanost vodiča kroz izložbu), motivacija, RQ1–RQ3 (iz `HANDOFF.md` §3), doprinos (dataset BS+EN, poređenje odbijanja), struktura rada.

### K-6 Pitanja (pisanje 16.11, provjera 19.11)
100 svojih pitanja; ti provjeravaš **Tarikova** (`checked_by = kerim`). Pitanja piše čovjek, a Claude ih samo validira.

### K-7 M3 check-in (rok 22.11)
3–4 slajda ili jedan ekran za 5 minuta u labu (sedmica 8):
1. Podaci (tvoje tabele)
2. Baseline brojevi na val (iz `evaluate_all.py`)
3. Plan glavne metode

Svako objašnjava svoj dio; Feedback se poslije upisuje u `HANDOFF.md` §13.

## 5. Checklist za M3 (tvoj dio)
- ☐ `annotation_guidelines.md` potvrđen od Tarika i Mirze
- ☐ `evaluate.py` + `test_metrics.py` (ručni primjeri)
- ☐ `data_analysis.py` → ≥2 figure + tabela
- ☐ `evaluate_all.py` → `metrics_val.json` + tabela
- ☐ Paper: Introduction
- ☐ 100 pitanja napisano, Tarikova provjerena
- ☐ M3 slajdovi
- ☐ AI_LOG i CONTRIBUTIONS upisani (sam)
- ☐ Znaš za 5 minuta objasniti: metrike → tabele → baseline rezultati

## 6. Poslije M3
1. **B2 prompted LLM** (`llm_baseline.py`): open model preko Ollame (Qwen ili Llama, mali) ili API. Prompt: *"Answer only from the text; otherwise reply exactly: NOT_IN_TEXT"*. Isti retrieval kao glavni sistem. Fiksna temperatura 0. Odluka lokalno vs API ide u HANDOFF §13.
2. AUROC i **risk–coverage kriva** (treba score, ne samo labela).
3. Finalna evaluacija na testu **tek kad je konfiguracija zaključana** (jedno pokretanje, s Mirzom).
4. **Analiza grešaka: cilj 20, minimum 10** u `results/errors.csv` (`qid, system, gold, pred, kategorija, uzrok, objašnjenje`). Kategorije: retrieval promašio pasus / leksičko preklapanje zavarava / treba zaključivanje / greška u gold labeli / dijakritici ili sleng / prevod. Piši **uzrok, ne simptom**.
5. Demo (FastAPI ili Streamlit) + QR kodovi (`qrcode`), tek kad glavna metoda radi.
6. Paper: Results; slajdovi.

## 7. Šta moraš znati na odbrani
- Precision, recall, F1 za refuse, s ručnim računom.
- False refusal rate i zašto je bitan za posjetioca.
- AUROC: šta mjeri i zašto ne zavisi od praga.
- Risk–coverage kriva i kako se čita.
- Bootstrap CI: zašto (mali test set), kako (uzorkovanje s ponavljanjem, 1000 puta, 2.5/97.5 percentil).
- Zašto se BS i EN mjere odvojeno (RQ3).
- Najčešća greška modela i zašto.
- Kako guidelines rješavaju granične slučajeve.

## 8. Kako početi sesiju s Claude-om
1. `git pull` → `uv sync`. Stavi materijale kursa u `course/` (nije u gitu).
2. Pokreni Claude Code u repou. U prvoj sesiji zalijepi `PROMPT_CLAUDE_CODE.md`.
3. Reci mu: *"Radim kao Kerim. Pročitaj `docs/team/KERIM.md` i zadnji unos u dnevniku, pa predloži sljedeći zadatak."*
4. Claude ti napravi `study/kerim/` (Obsidian vault: otvori folder `study/`).
5. Na kraju: pregledaj `git diff`, upiši AI_LOG i CONTRIBUTIONS, pa **sam** commit + push.

---

## Dnevnik sesija (handoff)

Najnoviji unos na vrhu. Piše Claude na kraju sesije (`TEAM_PLAN.md` §1.5).

### 2026-11-12 — fajl napravljen (Mirzina sesija)
- **Urađeno:** napravljene lične upute. Kerim još nije imao sesiju s Claude Code-om.
- **Sljedeće:** K-1 annotation guidelines (blokira pisanje pitanja), pa K-2 `evaluate.py`.
- **Blokade:** nema; guidelines trenutno blokiraju ostale.
