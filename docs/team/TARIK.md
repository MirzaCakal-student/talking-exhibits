# TARIK HADROVIĆ — podaci: izlošci, pitanja, split, kvalitet anotacije

> Lične upute za Tarika i Tarikovog Claude-a. Razrađuje `TEAM_PLAN.md` §4.2. Pravila: `TEAM_PLAN.md` §1, `HANDOFF.md` §12. Ako se nešto kosi, važi `course/` → `TEAM_PLAN.md` → ovaj fajl.
>
> GitHub: `@Tarik111345` · Lokalne bilješke: `study/tarik/` · Dnevnik sesija: dno ovog fajla.

---

## 1. Tvoja uloga u jednoj rečenici

Ti praviš **podatke na kojima se sve mjeri**: tekstove izložaka, pitanja, test set i split. Kurs eksplicitno traži test set "prepared or verified by the team" (≥100 primjera), pa je tvoj dio temelj ocjene. Na odbrani moraš najbolje znati kako je dataset napravljen, klase, split po izlošku, kappa i licence.

## 2. Fajlovi koje posjeduješ

| Fajl | Šta radi | Status |
| --- | --- | --- |
| `data/exhibits/README.md` | Lista izložaka: id, naslov, izvor (URL), ko piše | ☐ |
| `data/exhibits/<id>_<lang>.json` | Tekstovi izložaka BS + EN | ☐ |
| `data/questions/questions.csv` | Sva pitanja (spajaš doprinose sve trojice) | ☐ |
| `scripts/validate_questions.py` | Validator šeme i offseta | ☐ |
| `scripts/build_dataset.py` | Split po izlošku, seed 3004 → `data/processed/` | ☐ |
| `tests/test_data.py` (dio za validator) | pytest | ☐ (dogovori s Mirzom, on piše dio za `load_exhibits`) |

## 3. Ovisnosti

| Čekaš od | Šta | Do kad |
| --- | --- | --- |
| Mirza | `uv.lock` + `pytest` + `tests/` | odmah |
| Mirza | `load_exhibits` u `data.py` (validator ga može koristiti) | 14.11 |
| Kerim | `docs/annotation_guidelines.md` (prije pisanja pitanja!) | 13.11 |

| Čeka tebe | Šta | Do kad |
| --- | --- | --- |
| **Svi** | **Odluka o izlošcima + lista** | **kasni, odmah (13.11)** |
| Mirza | Format JSON-a i prva 2–3 izloška (za chunking i BM25) | 13.11 |
| Svi | Šema `questions.csv` + validator (prije pisanja pitanja) | 14.11 |
| Mirza, Kerim | `data/processed/{train,val,test}.csv` | 19.11 |

## 4. Zadaci do M3, korak po korak

### T-1 Odluka o izlošcima i lista (kasni, rok 13.11, ~2 h)
1. Dogovor s Mirzom i Kerimom (Discord): preporuka je **10–12 izložaka o IBU-u** (kampus, zgrade, biblioteka, fakulteti, historija, studentski projekti). Alternativa: Sarajevo/muzej.
2. `data/exhibits/README.md`: tabela `id | naslov | izvor (URL) | ko piše tekst | status`. id kratak, snake_case (`ibu_library`).
3. Podjela pisanja: Mirza 3–4, Kerim 3–4, ti ostale + ujednačavanje stila.
4. Upiši odluku u `HANDOFF.md` §13 (datum + "✅").
5. **Mail IBU-u** (PR ili studentska služba) za dozvolu objave tekstova. Ako dozvole nema, repo drži samo linkove i upute kako se tekst rekonstruiše.
6. **Mail profesorici/asistentici** (službeni kanal): (a) je li prezentacija u sedmici 14 (04.01.2027) ili u ispitnoj sedmici; (b) ako uključujemo kolege van tima za pitanja, tražimo odobrenje. Odgovore upiši u `HANDOFF.md` §13.

**Gotovo kad:** lista u repou i odluka u §13.

### T-2 Šema i validator pitanja (kasni, rok 14.11, ~3 h)
Kolone (iz `HANDOFF.md` §5.2): `qid, exhibit_id, lang, question, label, answer_text, answer_start, author, checked_by, source, split`.

`scripts/validate_questions.py` provjerava:
1. Sve kolone postoje.
2. `qid` jedinstven, format `q0001`.
3. `exhibit_id` postoji u `data/exhibits/`.
4. `lang ∈ {bs, en}`; `label ∈ {answerable, unanswerable_plausible, out_of_scope}`; `source ∈ {human, llm_checked}`.
5. Ako `answerable`: `text[answer_start : answer_start + len(answer_text)] == answer_text` u tekstu izloška **istog jezika**.
6. Ako nije answerable: `answer_text` i `answer_start` prazni.
7. `checked_by` ≠ `author`, oba iz `{mirza, tarik, kerim}`.
8. Nema dupliranih pitanja (isti tekst za isti izložak).
9. Ispis: `OK (N pitanja)` ili lista grešaka s `qid` i razlogom.

Napravi i prazan `data/questions/questions.csv` sa samo zaglavljem, da svi pišu u isti format.

**Gotovo kad:** `uv run python scripts/validate_questions.py` ispiše "OK" na ispravnom fajlu, a na namjerno pokvarenom primjeru (test) nabroji greške.
**Pitanje za odbranu:** zašto je `answer_start` provjera bitna (šta bi se desilo s token F1 metrikom da offset nije tačan)?

### T-3 Tekstovi izložaka (rok 13.11 → realno 15.11)
- 300–800 riječi po izlošku, **BS i EN**, napisani **svojim riječima** iz javnih izvora (ne copy-paste), URL-ovi u `sources`.
- Format, jedan fajl po jeziku: `data/exhibits/ibu_library_bs.json`
  ```json
  {"id": "ibu_library", "title": "Biblioteka IBU", "lang": "bs", "text": "...", "sources": ["https://..."]}
  ```
  (Ako tim odluči drugačije, npr. jedan fajl s obje verzije, javi Mirzi **prije** nego napiše `load_exhibits`.)
- Bez privatnih podataka (imena studenata, mailovi).
- Namjerno ostavi neke "očekivane" činjenice **van teksta** (cijena, arhitekta, tačan broj), jer su to dobra `unanswerable_plausible` pitanja.
- **Tekstove pišete vi.** Claude smije provjeriti format, dužinu i JSON, i predložiti strukturu, ali ne piše tekst.

### T-4 Koordinacija pitanja (rok 16.11)
- Podijeli izloške za pitanja (svako ~4). Svako piše pitanja za izloške koje **nije** sam pisao, da pitanja ne budu "preblizu" tekstu.
- Ciljna raspodjela: 45% answerable / 40% unanswerable_plausible / 15% out_of_scope; pola BS, pola EN; ~20% BS bez dijakritika.
- Tabela brojeva po klasi × jeziku × autoru (može iz Kerimovog `data_analysis.py`).

### T-5 Provjera i slaganje (rok 19.11)
1. ~50 pitanja dva člana anotiraju **nezavisno** (bez gledanja tuđe labele).
2. `sklearn.metrics.cohen_kappa_score(a, b)`. Stvarni broj ide u paper.
3. Razmimoilaženja riješite zajedno, a pravilo upišite u `docs/annotation_guidelines.md` (s Kerimom).
4. Lanac provjere: Mirza → provjerava Tarik, Tarik → Kerim, Kerim → Mirza.

**Pitanje za odbranu:** kappa 0.6 vs 0.8, šta znači? Zašto kappa, a ne obični postotak slaganja?

### T-6 `scripts/build_dataset.py` (rok 19.11, ~2 h)
1. Učita pitanja (validator mora proći).
2. Split **po izlošku**: ~60/15/25 % izložaka u train/val/test, `random.Random(3004)`.
3. Provjeri da test ima **≥100 pitanja** i sve tri klase; ako nema, ispiši upozorenje (ne mijenjaj seed dok "ne ispadne dobro", nego pomjeri izloške ručno i dokumentuj).
4. Snimi `data/processed/{train,val,test}.csv` i ispiši tabelu: broj pitanja po splitu × klasi × jeziku.
5. Popuni kolonu `split`.

**Pitanje za odbranu:** zašto split po izlošku, a ne po pitanju? (curenje: isti tekst izloška u train i test → precijenjeni rezultati)

### T-7 Paper: Dataset (rok 22.11)
Izvori izložaka, proces pisanja pitanja, klase s primjerima, guidelines, kappa, split, statistike (Kerimove tabele), licence (SQuAD 2.0 je CC BY-SA 4.0), etika i privatnost, ograničenja (mali dataset, pisali studenti).

### T-8 Paper: Literature Review, tvoja polovina (rok 22.11)
Bar 4 izvora, svaki **otvoren i pročitan**, u Zotero:
- Rajpurkar, Jia, Liang (2018), SQuAD 2.0
- Kamath, Jia, Liang (2020), Selective QA under domain shift
- Ji et al. (2023), Hallucination survey
- regionalni QA resursi (npr. Rađenović et al. 2026; **prvo provjeri da rad postoji** u ACL Anthology)
- dodatno: abstention u LLM-ovima, chatbotovi za muzeje i kulturno naslijeđe

### T-9 Pitanja (pisanje 16.11, provjera 19.11)
100 svojih pitanja; ti provjeravaš **Mirzina** (`checked_by = tarik`). Pitanja za test set piše čovjek, a Claude smije samo validirati.

## 5. Checklist za M3 (tvoj dio)
- ☐ Odluka o izlošcima u HANDOFF §13
- ☐ Mailovi: IBU (dozvola) i profesorica (sedmica 14, vanjski ljudi)
- ☐ `data/exhibits/` svi tekstovi BS + EN, prolaze `load_exhibits`
- ☑ `validate_questions.py` + prazan `questions.csv` sa zaglavljem
- ☐ ~300 pitanja spojeno, validator "OK"
- ☐ Kappa izračunata (stvarni broj)
- ☐ `build_dataset.py` → train/val/test, test ≥100
- ☐ Paper: Dataset + pola Literature Review (4+ izvora)
- ☐ AI_LOG i CONTRIBUTIONS upisani (sam)
- ☐ Znaš za 5 minuta objasniti: izlošci → pitanja → klase → kappa → split

## 6. Poslije M3
- Finalna verzija dataseta (feedback s M3).
- Priprema SQuAD 2.0 parova za trening, zajedno s Mirzom (filter, podskup, out-of-scope negativi).
- Kategorije grešaka i analiza grešaka s Kerimom (cilj 20, minimum 10).
- Demo: QR kodovi po izlošku (s Kerimom).
- Slajdovi o podacima; Discussion and Limitations (bias, privatnost, ograničenja).

## 7. Šta moraš znati na odbrani
- Kako su izlošci napisani i odakle su izvori; licence i dozvole.
- Tri klase s primjerom za svaku i granični slučajevi.
- Zašto `unanswerable_plausible` čini srž istraživanja (leksičko preklapanje zavarava BM25).
- Cohen's kappa: formula `(p_o − p_e) / (1 − p_e)` i tumačenje.
- Split po izlošku i curenje podataka.
- Zašto test set ne smije imati neprovjerena LLM pitanja.
- Zašto ~20% BS pitanja bez dijakritika.

## 8. Kako početi sesiju s Claude-om
1. `git pull` → `uv sync`. Stavi materijale kursa u `course/` (nije u gitu).
2. Pokreni Claude Code u repou. U prvoj sesiji zalijepi `PROMPT_CLAUDE_CODE.md`.
3. Reci mu: *"Radim kao Tarik. Pročitaj `docs/team/TARIK.md` i zadnji unos u dnevniku, pa predloži sljedeći zadatak."*
4. Claude ti napravi `study/tarik/` (Obsidian vault: otvori folder `study/`).
5. Na kraju: pregledaj `git diff`, upiši AI_LOG i CONTRIBUTIONS, pa **sam** commit + push.

---

## Dnevnik sesija (handoff)

Najnoviji unos na vrhu. Piše Claude na kraju sesije (`TEAM_PLAN.md` §1.5).

### 2026-11-14 — T-2 šema i validator pitanja (branch `tarik/validate-questions`)
- **Urađeno:**
  - `data/questions/questions.csv`: prazan obrazac, samo zaglavlje s 11 kolona (`qid, exhibit_id, lang, question, label, answer_text, answer_start, author, checked_by, source, split`). **Svi pišu pitanja u ovaj fajl.**
  - `scripts/validate_questions.py`: provjerava kolone, `qid` (format `q0001`, jedinstven), dozvoljene vrijednosti (`lang`, `label`, `source`, `split`, poznat `exhibit_id`), `author`/`checked_by` (članovi tima, nisu ista osoba), span odgovora (`text[answer_start:...] == answer_text` u izlošku **istog jezika**; prazno za neodgovoriva) i duplikate (bez razlike u velikim slovima i razmacima). Kad je pozicija pogrešna, ispiše gdje se odgovor stvarno nalazi.
  - `tests/test_validate_questions.py`: 16 testova na izmišljenim podacima.
  - `pytest` dodan kao dev zavisnost (`pyproject.toml` + `uv.lock`); `.pytest_cache/` u `.gitignore`.
- **Stvarni rezultati:** `uv run pytest tests -v` → `16 passed in 1.17s`. `uv run python scripts/validate_questions.py` na praznom fajlu → `OK (0 questions)`.
- **Format izložaka koji validator očekuje:** `data/exhibits/<id>_<lang>.json` s poljima `id`, `lang`, `text` (isti `id` za BS i EN verziju). Validator ih zasad čita svojom funkcijom `load_exhibit_texts`; prelazi na Mirzin `data.load_exhibits` kad on bude gotov.
- **Mirza:** `pytest` i `uv.lock` su dodani na ovom branchu, ne dodaji ih ponovo. Poslije merge-a: `git pull` + `uv sync`.
- **Sljedeće:** T-1 lista izložaka (`data/exhibits/README.md`) + odluka u HANDOFF §13 + mailovi (IBU, profesorica); zatim T-3 tekstovi.
- **Blokade / čekam na:** Kerimov `docs/annotation_guidelines.md` prije pisanja pitanja.
- **Ciljevi do sljedećeg roka:** lista izložaka i prvi tekstovi do 15.11, da Mirza može pokrenuti BM25.

### 2026-11-12 — fajl napravljen (Mirzina sesija)
- **Urađeno:** napravljene lične upute. Tarik još nije imao sesiju s Claude Code-om.
- **Sljedeće:** T-1 odluka o izlošcima + mailovi; T-2 šema i validator.
- **Blokade:** nema; ti si trenutno blokada za ostale (izlošci, šema).
