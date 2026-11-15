# STATUS — stanje projekta i šta je ostalo do M3

**Datum:** 15.11.2026 · **M3:** ponedjeljak 23.11.2026 u 08:00 (8 dana) · Napisao Claude u Mirzinoj sesiji, iz stanja repoa i GitHuba.

Ovaj fajl je presjek stanja za cijeli tim. Pravila i plan su u `TEAM_PLAN.md`, lične upute u `docs/team/`.

---

## 1. Šta je urađeno

### Mirza (branch `mirza/retrieval-baselines`, spojen s `main` poslije PR #1)
| Šta | Fajl | Stanje |
| --- | --- | --- |
| Učitavanje i provjera izložaka i pitanja | `src/talking_exhibits/data.py` | ✅ + testovi |
| Normalizacija, rečenice, chunking s overlapom | `src/talking_exhibits/preprocess.py` | ✅ + testovi |
| BM25 (vlastita implementacija) i e5 pretraga, keš | `src/talking_exhibits/retrieval.py` | ✅ + testovi |
| Baseline B0, B1 (BM25 + prag), B1b (e5 + prag), Recall@3 | `scripts/run_baselines.py` | ✅ kod; **bez pravih rezultata** |
| Testovi i izmišljeni fixture izlošci | `tests/`, `tests/fixtures/` | ✅ 37 testova prolazi |
| README "How to run", struktura repoa | `README.md` | ✅ |
| Usklađivanje planova s `course/`, lične upute | `HANDOFF.md`, `TEAM_PLAN.md`, `docs/team/*.md` | ✅ (pushano 12.11) |
| Literature Review, Mirzina polovina | Google Docs (02 Paper) | ⏳ 6 izvora provjereno, AI nacrt postoji lokalno; Mirza mora pročitati radove i napisati tekst |

Baseline skripta je pokrenuta samo na 22 izmišljena pitanja (fixtures). Ti brojevi pokazuju da kod radi i **ne prijavljuju se**.

### Tarik (PR #1, branch `tarik/validate-questions`, **merge-an u `main` 15.11**)
| Šta | Fajl | Stanje |
| --- | --- | --- |
| Prazan obrazac pitanja s 11 kolona | `data/questions/questions.csv` | ✅ |
| Validator pitanja (kolone, qid, vrijednosti, autor ≠ provjerio, span odgovora, duplikati) | `scripts/validate_questions.py` | ✅ |
| 16 testova za validator | `tests/test_validate_questions.py` | ✅ (po PR-u: 16 passed) |
| `pytest` + `uv.lock` | `pyproject.toml`, `uv.lock` | ✅ (spojeno s Mirzinim izmjenama, vidi §3) |
| AI_LOG, CONTRIBUTIONS, dnevnik sesije | | ✅ |

### Kerim
U repou i na GitHubu nema ničega od Kerima poslije 25.10.

---

## 2. Šta fali za M3 (po zahtjevima iz Project Requirements)

| Zahtjev M3 | Stanje | Ko | Blokira |
| --- | --- | --- | --- |
| Dataset: prikupljen, očišćen, podijeljen na train/val/test | ❌ nema nijednog izloška ni pitanja | Tarik (+ svi pišu) | **sve ostalo** |
| Prva verzija test seta (≥100 primjera) | ❌ | svi, split Tarik | |
| Preprocessing i analiza podataka, ≥2 tabele/grafika | 🟡 preprocessing gotov; analiza ❌ | Kerim | |
| Baseline koji radi, s prvim rezultatima | 🟡 kod gotov; rezultati čekaju podatke | Mirza | |
| Nacrt dijagrama pipelinea | ✅ u README | | |
| CONTRIBUTIONS i AI_LOG ažurirani | 🟡 Tarik da; Mirza i Kerim ne | svako svoje | |
| Paper: Introduction | ❌ | Kerim | |
| Paper: Literature Review (≥8 izvora, 5 direktno o problemu) | ❌ | Mirza + Tarik | |
| Paper: Dataset | ❌ | Tarik | |
| Check-in u labu (5 min) | ❌ slajdovi | Kerim | |

**Kritični put:** odluka o izlošcima → tekstovi izložaka → guidelines → pitanja → provjera i kappa → split → baseline rezultati → tabele → paper. Prva tri koraka kasne od 9.–13.11.

---

## 3. Spajanje Tarikovog PR-a i Mirzinog koda (riješeno 15.11)

Oba su dodala `pytest` i `uv.lock`. Kod se nije sudarao (različiti fajlovi), a format izložaka je isti kod obojice: `data/exhibits/<id>_<lang>.json`.

Šta je urađeno (komande je pokrenuo Mirza):
1. PR #1 merge-an u `main` na GitHubu.
2. Mirzin rad commitan na branch `mirza/retrieval-baselines`, pa je u njega povučen `main`.
3. Konflikti u `pyproject.toml` i `uv.lock` riješeni Mirzinom verzijom (sadrži Tarikov `pytest`, uz to `[tool.pytest.ini_options]` i uklonjen `rank-bm25`). `.gitignore` se spojio sam.
4. Provjera poslije spajanja: `uv lock --check` uredan, `uv run pytest` → **53 passed** (37 + 16), validator na fixture podacima → `OK (22 questions)`.

**Svi poslije merge-a ovog brancha:** `git pull` + `uv sync` (`rank-bm25` se briše iz okoline).

Sljedeći korak (Tarik): validator može umjesto svoje `load_exhibit_texts` koristiti `talking_exhibits.data.load_exhibits`.

---

## 4. Šta ko treba uraditi (po prioritetu)

### Tarik
1. **Odmah:** odluka o izlošcima + `data/exhibits/README.md` (lista, izvori, ko piše koji tekst) + upis u `HANDOFF.md` §13.
2. **Do 17.11:** tekstovi izložaka BS + EN (podjela pisanja na sve trojicu), format `<id>_<lang>.json`.
3. Mailovi: IBU (dozvola za objavu tekstova), profesorica (prezentacije u sedmici 14 ili 16; vanjski ljudi za pitanja).
4. Podjela izložaka za pisanje pitanja; spajanje u `questions.csv`; validator "OK".
5. **Do 20.11:** kappa na ~50 pitanja; `scripts/build_dataset.py` (split po izlošku, seed 3004, test ≥100).
6. **Do 22.11:** paper Dataset + pola Literature Review.

### Kerim
1. **Odmah:** `docs/annotation_guidelines.md` (bez njega se ne mogu pisati pitanja).
2. **Do 18.11:** `src/talking_exhibits/evaluate.py` + `tests/test_metrics.py`. Mirzina skripta trenutno ima privremenu `refuse_metrics`; zamjenjuje se tvojom.
3. **Do 20.11:** `scripts/data_analysis.py` (≥2 figure + tabela) i `scripts/evaluate_all.py`. Ulaz: `results/val_predictions_<system>.csv` s kolonama `qid, system, score, threshold, pred, gold`.
4. **Do 22.11:** paper Introduction; slajdovi za check-in.
5. 3–4 teksta izložaka i 100 pitanja; provjera Tarikovih pitanja.
6. Javi se timu: od 25.10 nema tvojih commitova, a git historija se boduje po osobi.

### Mirza
1. ~~Pregledati i merge-ati PR #1~~ ✅; pushati `mirza/retrieval-baselines` i otvoriti PR.
2. Napisati 3–4 teksta izložaka kad Tarik podijeli.
3. 100 pitanja (50 BS, 50 EN) kad postoje izlošci i guidelines; provjera Kerimovih pitanja.
4. Kad stigne `data/processed/val.csv`: `uv run python scripts/run_baselines.py`, ručna provjera 10 pitanja, rezultati u `results/`.
5. Literature Review: pročitati 6 radova i napisati svoju polovinu u Google Docs.
6. Upisati AI_LOG i CONTRIBUTIONS.

---

## 5. Otvorene odluke za tim

| Pitanje | Ko odlučuje |
| --- | --- |
| Koji izlošci (IBU kampus ili muzej), koliko (10–12) | svi, upisuje Tarik |
| Smije li dio pitanja generisati LLM? Po `HANDOFF.md` §5.2 smije u **train** uz `source = llm_checked` i ljudsku provjeru; u **test** samo pitanja koja je napisao ili provjerio čovjek. Pravilo u `CLAUDE.md` trenutno zabranjuje da Claude piše pitanja | svi; ako se mijenja, upisati u HANDOFF §13 |
| Datum prezentacija (sedmica 14 ili ispitna sedmica) | pitati profesoricu |
| LLM za B2: Ollama ili API | Kerim, poslije M3 |

---

## 6. Realna procjena

Kod za baseline je spreman, validator je spreman. **Usko grlo su podaci:** do M3 je 8 dana, a nema nijednog izloška, guidelines ni pitanja. Ako tekstovi izložaka ne budu gotovi do 17.11, a pitanja do 19.11, neće biti vremena za provjeru, kappu, split i baseline rezultate prije 23.11 u 08:00. Minimum koji M3 traži: dataset sa splitom, test set ≥100, baseline s prvim rezultatima, 2 tabele ili grafika, tri sekcije papera.
