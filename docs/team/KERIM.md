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
| `src/talking_exhibits/llm_baseline.py` | B2 prompted LLM (poslije M3) | ☑ implementacija i testovi |
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
- ☑ Vlastiti izložak `ibu_fess`: BS + EN tekstovi, izvori i tehnička provjera
- ☑ Vlastiti izložak `ibu_feh`: BS + EN tekstovi, izvori i tehnička provjera
- ☑ Vlastiti izložak `ibu_podcast_media`: BS + EN tekstovi, izvori i tehnička provjera
- ☑ Vlastiti izložak `ibu_about_programs`: BS + EN tekstovi, izvori i tehnička provjera
- ☑ `annotation_guidelines.md` pojašnjava izbor spana i granične slučajeve
- ☐ `annotation_guidelines.md` potvrđen od Tarika i Mirze
- ☑ `evaluate.py` + `test_metrics.py` (ručni primjeri)
- ☑ `data_analysis.py` → preliminarna analiza 200 nacrta: 3 figure + tabele
- ☐ K-3 ponovljen na kompletnom, pregledanom timskom skupu
- ☑ `evaluate_all.py` — implementacija i testovi
- ☐ K-4 pokrenut na stvarnom val skupu → `metrics_val.json` + tabela
- ☑ Paper: Introduction — nacrt u `docs/introduction.md`
- ☐ Introduction prenesen u zajednički `02 Paper` i citati usklađeni u Zotero/Paperpile
- ☑ 100 vlastitih nacrta pitanja napisano i tehnički provjereno (50 BS / 50 EN; q0001–q0100)
- ☑ Pitanja q0001–q0200 tehnički pregledana, nalazi u `docs/question_review.md`
- ☐ Vlastita pitanja ljudski potvrđena i nezavisno pregledana (`source`, `checked_by`)
- ☐ Tarikova pitanja: predložene korekcije i nezavisni pregled čekaju tim
- ☑ K-7 četiri slajda provjerena u `docs/m3_checkin.pptx`
- ☐ K-7 slajdovi uvezeni u zajednički `03 Presentation`
- ☐ AI_LOG i CONTRIBUTIONS upisani (sam)
- ☐ Znaš za 5 minuta objasniti: metrike → tabele → baseline rezultati

## 6. Poslije M3
1. ☑ **B2 prompted LLM** (`llm_baseline.py`) lokalno provjeren na BS i EN s Ollamom i `qwen2.5:1.5b`. Fiksna temperatura 0 i seed 3004. ☐ Mjerenje na pregledanom val skupu.
2. ☑ AUROC i **risk–coverage kriva** implementirani i testirani. ☐ Pokretanje na stvarnom val skupu.
3. Finalna evaluacija na testu **tek kad je konfiguracija zaključana** (jedno pokretanje, s Mirzom).
4. **Analiza grešaka: cilj 20, minimum 10** u `results/errors.csv` (`qid, system, gold, pred, kategorija, uzrok, objašnjenje`). Kategorije: retrieval promašio pasus / leksičko preklapanje zavarava / treba zaključivanje / greška u gold labeli / dijakritici ili sleng / prevod. Piši **uzrok, ne simptom**. ☑ Izvoz i testovi. ☐ Pregled stvarnih grešaka.
5. ☑ Lokalni FastAPI demo + QR kodovi s BM25 i B2. ☐ Povezivanje treniranog klasifikatora.
6. ☑ Lokalni Results nacrt za preliminarnu analizu i provjeru prototipa. ☐ Poređenje sistema nakon evaluacije.

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

### 2026-11-22 — Završna potvrda M3 i ručna integracija pitanja

- **Spremno za M3:** K-2 metrike i testovi, K-3 preliminarne tabele i tri figure, lokalni K-5 Introduction, K-6 tehnički pregled i K-7 četiri slajda. Rezultati opisuju 200 nacrta i 16 jezičkih verzija izložaka.
- **Ljudske potvrde:** K-1 čeka potvrde Tarika i Mirze. K-6 čeka Kerimovu potvrdu porijekla, nezavisni pregled i dogovor tima o različitim dodjelama u TEAM_PLAN §2 i §4.3. `02 Paper` i `03 Presentation` čekaju prijenos u zajedničke dokumente.
- **Ulazi za evaluaciju:** Tarik dostavlja pregledani `data/processed/val.csv` iz splita po izlošcima. Mirza dostavlja `results/val_predictions_b0.csv`, `results/val_predictions_b1_bm25.csv` i `results/val_predictions_b1b_e5.csv` za iste `qid`, te trenirani klasifikator i prag za završnu integraciju. Time se omogućavaju K-4, AUROC, risk–coverage, `results/errors.csv` i dopuna Results. Finalni test slijedi tek nakon zaključavanja konfiguracije.
- **Provjera:** 208 testova prolazi. Na privremenom CSV-u svih 200 zapisa i 93 raspona očuvani su u UTF-8. Validator nalazi 100 praznih `source` i 200 praznih `checked_by`. Namjerni sudar ID-ja odbijen je prije pisanja kandidata. Svi opisni brojevi i tri PNG-a reproducirani su, a PPTX ima četiri slajda.

#### Priprema kandidata za CSV prije ručnog mergea

Na čistoj grani `kerim/evaluation-and-dataset`, nakon ručnog `git fetch origin`, pokreni ovaj blok iz korijena repozitorija. Provjereni `origin/main` je `e2cf0ad` (PR #7). Ako se ulazi promijene, blok će odbiti neočekivane raspone, autore ili nevažeće zapise.

```bash
question_csv=data/questions/questions.csv
integration_dir=$(mktemp -d) &&
  git show "HEAD:$question_csv" > "$integration_dir/kerim.csv" &&
  git show "origin/main:$question_csv" > "$integration_dir/tarik.csv" &&
  uv run --frozen python - "$integration_dir" <<'PY'
import csv
import sys
from pathlib import Path

sys.path.insert(0, "scripts")
import validate_questions as validator

directory = Path(sys.argv[1])
kerim, tarik = (directory / name for name in ("kerim.csv", "tarik.csv"))

def read_records(path):
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.reader(stream, strict=True)
        columns = next(reader, [])
        rows = list(reader)
    if columns != validator.REQUIRED_COLUMNS or any(len(row) != len(columns) for row in rows):
        raise SystemExit(f"Invalid CSV schema or row length in {path}")
    return rows

author = validator.REQUIRED_COLUMNS.index("author")
blocks = []
for path, member, start in ((kerim, "kerim", 1), (tarik, "tarik", 101)):
    rows = read_records(path)
    expected = {f"q{i:04d}" for i in range(start, start + 100)}
    if len(rows) != 100 or {row[0] for row in rows} != expected or any(row[author] != member for row in rows):
        raise SystemExit(f"Unexpected IDs or authors in {path}. Recheck the integration inputs.")
    blocks.extend(rows)

left = kerim.read_bytes()
separator = b"" if left.endswith(b"\n") else b"\n"
candidate = directory / "candidate.csv"
with candidate.open("xb") as stream:
    stream.write(left + separator + tarik.read_bytes().split(b"\n", 1)[1])

if read_records(candidate) != blocks:
    raise SystemExit("Merged values differ from the source records.")

questions = validator.load_questions(candidate)
problems = validator.validate(questions, validator.load_exhibit_texts(Path("data/exhibits")))
for problem in problems:
    if not (problem.endswith("got ''") and (": source must be one of" in problem or ": checked_by must be one of" in problem)):
        raise SystemExit(problem)

print(f"{candidate}: {len(questions)} records, all fields preserved.")
print(f"Exact answer spans: {int(questions.label.eq('answerable').sum())}")
print(f"Pending metadata: {(questions.source == '').sum()} source, {(questions.checked_by == '').sum()} checked_by")
PY
```

Kandidat zadržava Kerimovo zaglavlje i oba bloka u izvornom obliku. Tek nakon uspješne provjere ručno pokreni `git merge --no-commit --no-ff origin/main`. Za provjerene commitove očekuje se samo konflikt u `data/questions/questions.csv`. U istom terminalu provjeri da Gitov drugi i treći zapis konflikta odgovaraju kopijama prije nego potvrdiš zamjenu radnog CSV-a.

```bash
git show ":2:$question_csv" | cmp - "$integration_dir/kerim.csv" &&
  git show ":3:$question_csv" | cmp - "$integration_dir/tarik.csv" &&
  cp -i "$integration_dir/candidate.csv" "$question_csv"
cmp "$question_csv" "$integration_dir/candidate.csv"
```

Nakon provjere ručno dodaj samo razriješeni CSV, pregledaj indeks i pokreni pytest prije commita i pushanja grane. PR može ići na pregled kao draft. Prazna polja za ljudsku potvrdu ostaju vidljiva u PR-u.

### 2026-11-22 — M3 isporuke i tehnički pregled pitanja

- **Urađeno:** Dovršene dopune smjernica, ispravljeno osam Kerimovih pitanja, a prijedlozi za deset Tarikovih redova zabilježeni su u `docs/question_review.md`. K-3 tabele i tri figure koriste privremeni spoj Kerimovih i Tarikovih nacrta iz `e2cf0ad`. Ažuriran je status B2 u Introduction, pripremljen preliminarni Results nacrt i provjerena četiri slajda za check-in.
- **Provjera:** 200 jedinstvenih ID-jeva, 102 BS i 98 EN. Raspodjela klasa je 93 answerable, 76 plausible i 31 out of scope. Svih 93 spana odgovaraju tekstu i Unicode pomacima. Validator prijavljuje 100 praznih `source` i 200 praznih `checked_by`. Tri PNG-a su identična pri ponavljanju. Prošlo je 116 fokusiranih i 208 ukupnih testova.
- **Blokade / sljedeće:** Tarik i Mirza trebaju potvrditi smjernice i razriješiti različite dodjele nezavisnog pregleda u TEAM_PLAN §2 i §4.3. Kerim potvrđuje porijeklo svojih pitanja. Za punu K-3 analizu nedostaju Mirzini nacrti i timski pregled. Za K-4 i analizu stvarnih grešaka nedostaju `data/processed/val.csv` i predikcije B0/B1/B1b. `02 Paper` i `03 Presentation` čekaju pristup zajedničkim dokumentima. Read-only provjera pokazuje konflikt pri integraciji `questions.csv` u `main`, koji treba riješiti uz oba bloka redova. Test split nije korišten.

### 2026-11-22 — Lokalna B2 inferencija kroz demo

- **Urađeno:** Ollama 0.40.16 i `qwen2.5:1.5b` rade na `127.0.0.1:11434` s isključenim cloud funkcijama. B2 uputa sada traži potvrdu da jedan pasus izričito odgovara na cijelo pitanje prije citiranja. Time su u ponovljenoj provjeri otklonjeni HTTP 500 zbog ponavljanja tokena na BS pitanju i prihvatanje nepovezanog citata na EN pitanju.
- **Provjera:** Osam stvarnih upita kroz demo dalo je tri tačna citata i pet odbijanja `NOT_IN_TEXT`. Provjeren je sadržaj poslan Ollami i svaki upit je koristio samo pasuse izabrane verzije izloška. Za nedostajući model demo vraća HTTP 503 na oba jezika. Prošao je 41 fokusirani test i svih 208 testova. Test split nije korišten.

### 2026-11-22 — Izvoz grešaka i lokalni demo

- **Urađeno:** `uv run --frozen python scripts/analyze_errors.py` izvozi pogrešne binarne odluke iz validacijskih predikcija po `qid` u `results/errors.csv`. Čuva izvornu oznaku iz skupa i postojeće ručne anotacije. Skripta provjerava kategorije i broji potpune preglede.
- **Demo:** `uv run --frozen uvicorn --app-dir src talking_exhibits.demo.app:create_app --factory` pokreće BS/EN stranice, QR kodove i upite nad BM25 i B2. Za telefon postaviti `TALKING_EXHIBITS_BASE_URL` na privatni HTTP URL računara i pokrenuti Uvicorn na istoj privatnoj adresi i portu.
- **Provjera:** Prošlo je 56 fokusiranih testova analize i evaluatora, 41 test demoa i B2 te 208 ukupno. Lokalni HTTP poslužio je 16 stranica izložaka i 16 QR kodova. QR kod očitan s renderovane FEH stranice vodi na njenu BS verziju. Kada Ollama nije dostupna, API vraća lokalizirani HTTP 503 na oba jezika.
- **Blokade / sljedeće:** Za stvarne analize trebaju pregledani `val.csv` i predikcije sistema. Zatim ručno provjeriti najmanje 10 grešaka, s ciljem 20. Za stvarne odgovore pokrenuti Ollama s lokalnim modelom (`qwen2.5:1.5b` ili `OLLAMA_MODEL`). Kada Mirzin klasifikator i prag budu dostupni, predati adapter `select_passage` pri pokretanju demoa. Test split nije korišten.

### 2026-11-22 — AUROC i risk–coverage

- **Urađeno:** `evaluate.py` računa AUROC za odbijanje i udio neodgovorivih među prihvaćenim pitanjima na svakom pragu. `evaluate_all.py` spaja ocjene B1/B1b po `qid` i prikazuje metrike ukupno i po jeziku. Viša ocjena pogoduje prihvatanju. Rezultat je nedostupan za podskup s nepotpunim ocjenama. AUROC traži obje binarne klase.
- **Stvarni rezultati:** Prošlo je 85 fokusiranih i 184 ukupna testa. `git diff --check` je prošao. Test split nije korišten.
- **Blokade / sljedeće:** Za mjerenje na stvarnim podacima trebaju Tarikov `data/processed/val.csv` i Mirzini `results/val_predictions_*.csv` sa stvarnim BM25 i e5 ocjenama. B0 i B2 imaju metrike binarne odluke.

### 2026-11-22 — B2 prompted LLM preko Ollame

- **Urađeno:** `answer_question(question, passages)` poziva Ollama `/api/chat` za BS ili EN s temperaturom 0 i seedom 3004. Prihvata doslovan span iz jednog dostavljenog pasusa ili vraća `NOT_IN_TEXT`. `answer_with_retrieval(question, exhibit_id, lang, search)` koristi isti poziv pretrage kao postojeći runner i prosljeđuje pasuse odgovarajućeg izloška i jezika. `to_prediction(answer)` daje `answer` ili `refuse` za postojeći evaluator. `OllamaError` označava neuspjelo izvršavanje koje se ne boduje kao odbijanje.
- **Provjera:** `tests/test_llm_baseline.py` ima 22 prolazna slučaja, a kompletni pytest 164. Testirana je veza s postojećim BM25 retrievalom. HTTP odgovori Ollame su simulirani, pa kvalitet stvarnih odgovora na BS i EN još nije izmjeren. Test split nije korišten.
- **Sljedeće:** Za stvarno pokretanje potreban je Ollama server s lokalno instaliranim modelom (`qwen2.5:1.5b` po zadanim postavkama, izmjenjivo kroz `model`). Na pregledanom val skupu koristiti isti retrieval i `k` kao glavna metoda. U postojećem formatu predikcija koristiti `system=b2`, prazno `score` i `pred` iz `to_prediction`.

### 2026-11-22 — Tehnička provjera K-2, K-3, K-4 i K-6

- **Urađeno:** K-3 koristi zajednički loader izložaka pa nevažeći JSON tekst ne ulazi u statistiku. K-4 provjerava `gold` iz izvoza baselinea prema `qid` i binarnoj odluci iz `val.csv`, ako izvoz ima tu kolonu. Dodani regresijski testovi u postojeće testne fajlove.
- **Provjera:** 75 fokusiranih i 142 ukupna testa prolaze. Ponovljeni K-3 nad Kerimovim podskupom daje iste tabele i tri identična PNG-a. Četiri Kerimova izloška imaju osam ispravnih jezičkih verzija (316–385 riječi). Svih 100 nacrta ima ispravan izložak i jezik, 45/45 spanova ima tačne Unicode pomake, a 55 neodgovorivih redova ima prazna polja odgovora. Validator završava kodom 1 zbog 100 praznih `source` i 100 praznih `checked_by` polja.
- **Blokade / sljedeće:** K-1 čeka potvrde Tarika i Mirze. K-6 čeka Kerimovu ljudsku provjeru vlastitih nacrta, Mirzin nezavisni pregled i korekcije te ljudsku potvrdu Tarikovih pitanja iz prethodnog pregleda. Ponoviti K-3 kad tim pripremi kompletan pregledan skup. Za stvarni K-4 trebaju Tarikov `val.csv` i Mirzine baseline predikcije. Test split nije korišten.

### 2026-11-22 — K-7 odgođen; fokus na tehničkoj implementaciji

- **Tehničko stanje:** Lokalno postoji 100 Kerimovih nacrta; `source`, `checked_by` i `split` su prazni. Stvarni val split i baseline predikcije nisu dostupni, pa stvarna K-4 evaluacija čeka te zavisnosti. K-1 još čeka potvrde tima; K-2 ima implementaciju i postojeće testove; K-3 je preliminarno isporučen u commitu `1f5d2d7`.
- **Sljedeći prijedlog, bez implementacije:** K-4 — provjera i ciljani testovi postojećeg `scripts/evaluate_all.py`, prvenstveno zaštita ulaza i kompatibilnost s baseline predikcijama. Čitanjem je potvrđeno da `read_gold` provjerava naziv `val.csv`, ali ne provjerava vrijednosti kolone `split`; u `tests/` nema direktnih testova ove skripte. Promjene tek nakon Kerimovog odobrenja. Nije otvaran test split niti pokretana baseline evaluacija.

### 2026-11-22 — K-3: preliminarna analiza dostupnih podataka

- **Urađeno:** Postojeći `scripts/data_analysis.py` dopunjen tabelama po izlošku i autoru, opisnim statistikama dužina, statusom pregleda i reproduktivnom komandom. Zadržani su postojeće učitavanje, Jaccard i tri grafikona. Dodane su preliminarne oznake i provjerene oznake namjerno izostavljenih dijakritika; nepostojeća klasa sada ima Jaccard `N/A`, umjesto lažno izmjerene nule. Kreirani `results/data_tables.md`, tri PNG-a u `results/figures/` i `tests/test_data_analysis.py`. Dopunjene postojeće lokalne bilješke.
- **Tačan opseg:** Četiri Kerimova izloška u osam BS/EN verzija i 100 nacrta pitanja q0001–q0100 (`author=kerim`), sve već pohranjeno u commitima. Po 25 pitanja po izlošku; 50 BS i 50 EN. Zabilježenih valjanih `source` vrijednosti i nezavisnih pregleda ima 0/100; svih 100 `split` polja je prazno. Nema lokalnih train/val/test fajlova. Nisu kreirani splitovi niti pokretani modeli.
- **Dostupnost timskih podataka:** Read-only provjera `git ls-remote --heads origin` potvrdila je da pregledani remote refovi odgovaraju aktuelnim headovima. `origin/tarik/exhibit-drafts` sadrži osam JSON-a za četiri njegova izloška, ali nema redova pitanja; ništa nije kopirano. U `origin/mirza/retrieval-baselines` nisu dostupni izlošci ni pitanja. Ostale pregledane grane također ne daju dodatna pitanja ili splitove. Ovo nije tvrdnja o necommitanom ili drugdje pohranjenom radu članova tima.
- **Stvarni rezultati:** BS klase: 22 answerable / 20 plausible / 8 out_of_scope; EN: 23 / 20 / 7. Pitanja: prosjek 9,11 riječi, medijan 9, raspon 4–14; verzije izložaka: prosjek 353,88, medijan 355,5, raspon 316–385. Prosječni Jaccard: 0,0303 / 0,0232 / 0,0073 istim redom klasa. Plausible je iznad out_of_scope i ispod answerable; ovo ne dokazuje slabost BM25 praga. Prethodni K-6 zapis navodi 10/50 BS pitanja s namjerno izostavljenim dijakriticima (20%); samo odsustvo znakova daje 28/50 (56%), pa se preostalih 18 ne proglašava namjernim izostavljanjem.
- **Provjera:** Skripta na stvarnim podacima završila izlaznim kodom 0; komanda sa svih deset qid-jeva je u `results/data_tables.md`. Novi fokusirani testovi: 9 prošlo; `uv run --frozen pytest -q`: 96 prošlo. Nezavisni račun potvrđuje dužine, Jaccard, vrijednosti stubaca i histograme (100 pitanja / 8 verzija). Provjereni PNG renderi imaju iste SHA-256 vrijednosti kao isporučeni fajlovi; slike su otvorene i vizuelno pregledane. Učitavanje i svih 100 mapiranja na isti jezik prolaze; 45/45 answer spanova je ispravno. Validator i dalje prijavljuje samo 100 praznih `source` i 100 praznih `checked_by` polja. `git diff --check` prolazi; indeks je prazan.
- **Blokade / sljedeće:** Analiza je preliminarna dok ne budu dostupni kompletni, ljudski potvrđeni i nezavisno pregledani timski podaci. `course/` nije dostupan. Ponoviti K-3 nakon njihove integracije; K-4 zavisi od val splita i stvarnih baseline predikcija i nije započet. Kerim pregleda ove promjene, sam ažurira evidencije i ručno commita/pusha. Introduction je već committan kao `6b4d520`; početno stablo bilo je čisto na `kerim/evaluation-and-dataset`. Izlošci, pitanja, Introduction, AI_LOG i CONTRIBUTIONS ostaju nepromijenjeni.

### 2026-11-22 — K-5: Introduction nacrt za M3

- **Urađeno:** Kreiran `docs/introduction.md` kao samostalan engleski nacrt za naknadni prijenos u postojeći Google Doc `02 Paper`, u zajedničkom folderu `Čakal, Hadrović, Hodžić`. Obuhvata kontekst QA vodiča, nedovoljnu tekstualnu podršku i halucinacije, BS/EN opseg, tačne RQ1–RQ3, plan retrievala i klasifikatora, baseline poređenja, namjeravane doprinose i strukturu rada. Postojeći kod razlikovan je od planiranog fine-tuninga i LLM baselinea, a pitanje-dataset opisan je kao nacrt koji čeka ljudski pregled. Dopunjene postojeće lokalne bilješke.
- **Stvarni rezultati:** Oko 650 riječi uvoda bez referenci. Programski potvrđeno da sva tri istraživačka pitanja odgovaraju HANDOFF-u riječ po riječ, uključujući interpunkciju; četiri upotrijebljena citata imaju četiri odgovarajuće reference. Izvori provjereni na ACL Anthology i arXiv stranicama: Ji et al. (arXiv preprint, 2022), Rajpurkar et al. (2018), Kamath et al. (2020), Conneau et al. (2020). Unicode NFC i provjere placeholdera prolaze; `git diff --check` prolazi. Nisu izvođeni eksperimenti niti prijavljivani rezultati modela.
- **Sljedeće:** Kerim pregleda sadržaj, dopuni svoje evidencije i ručno commita/pusha nacrt. Tekst potom treba prenijeti u `02 Paper`, uskladiti s postojećim dijelovima i konačnim stilom citiranja te reference unijeti kroz timski Zotero/Paperpile. Ova isporuka ne mijenja Literature Review, Dataset, Methodology ili Results.
- **Blokade / čekam na:** Google Drive plugin nije povezan, preglednik traži prijavu, a direktna poveznica na `02 Paper` trenutno nije dostupna. Kerim je izričito odobrio nacrt u postojećem `docs/` direktoriju; zajednički dokument nije mijenjan. `course/` i lokalne Project Report Guidelines nisu dostupni; korišteni su zahtjevi iz HANDOFF §10 i TEAM_PLAN §4.3, uključujući IEEE preporuku. Konačna numeracija citata i unos u reference manager nisu potvrđeni.
- **Ciljevi do sljedećeg roka:** Prenijeti pregledan Introduction prije M3 roka 23.11.2026 u 08:00. K-5 nacrt je pripremljen, ali zahtjev „tekst u 02 Paper“ ostaje otvoren do prijenosa. Cijeli M3 paper i njegov minimum od osam izvora nisu označeni završenim. Prethodni K-6 commit je `814f962`; početno stablo bilo je čisto na `kerim/evaluation-and-dataset`. Podaci, izlošci, kod, AI_LOG i CONTRIBUTIONS nisu mijenjani.

### 2026-11-22 — K-6: 100 nacrta pitanja za ljudski pregled

- **Urađeno:** U postojeći `data/questions/questions.csv` dodano 100 novih pitanja s `author=kerim`, ID-jevima q0001–q0100 i izvornom šemom od 11 kolona. Prije rada nije bilo pitanja ni pitanja drugih autora za očuvanje. Pitanja koriste samo odgovarajuće BS/EN tekstove četiri vlastita izloška. Obrađeni su kratki odgovori, parafraze, brojčani podaci, nenavedeni detalji iste teme i jasno nepovezana pitanja. Deset BS pitanja namjerno je bez dijakritika; odgovorima je sačuvan izvorni zapis.
- **Stvarni rezultati:** FESS: 13 BS / 12 EN, klase 12 answerable / 10 plausible / 3 out_of_scope; FEH: 12/13, klase 11/10/4; podcast: 13/12, klase 11/10/4; about/programs: 12/13, klase 11/10/4. Ukupno 50 BS + 50 EN i tačno 45/40/15 po klasama. Svih 45 answer spanova i Unicode offseta prolazi; svih 55 neodgovorivih pitanja ima prazna answer polja. Nema tačnih normalizovanih duplikata niti kandidata s SequenceMatcher ≥0.78 ili token Jaccard ≥0.60 nakon normalizacije bez dijakritika. To nije zamjena za semantički ljudski pregled. `uv run --frozen pytest -q`: **87 passed**. `git diff --check` prolazi.
- **Validator i status:** `uv run --frozen python scripts/validate_questions.py` završava kodom **1** i prijavljuje tačno **200** problema: 100 praznih `source` i 100 praznih `checked_by`. Nema drugih prijavljenih grešaka. Ova polja su namjerno prazna jer `llm_checked` prema guidelines podrazumijeva stvarnu ljudsku potvrdu, a nezavisni pregled nije izvršen. `split` je prazan za svih 100 redova. Ovo su nacrti za pregled, ne prihvaćen gold dataset.
- **Sljedeće:** Kerim treba sadržajno pregledati svih 100 nacrta i, nakon stvarne provjere, evidentirati odgovarajući `source`. Nezavisni recenzent treba provjeriti oznake i spanove te stvarno upisati `checked_by`. Prema TEAM_PLAN §4.1 M-7, Mirza provjerava Kerimova pitanja; Kerim zasebno provjerava Tarikova prema K-6. Nakon tih koraka ponoviti validator. Kerim sam pregleda i commita/pusha ovu isporuku te dopunjava AI_LOG i CONTRIBUTIONS.
- **Blokade / čekam na:** Ljudska potvrda i nezavisni pregled svih 100 pitanja; prihvaćanje guidelines još nije evidentirano lokalno. Trenutni CSV nema Tarikovih pitanja za Kerimov pregled. `course/` nije dostupan. Početno stablo bilo je čisto na `kerim/evaluation-and-dataset`, a sva četiri izloška commitana; nijedan izložak, validator ili tuđi fajl nije mijenjan.
- **Ciljevi do sljedećeg roka:** Razriješiti stvarni pregled prije prihvatanja podataka za M3, 23.11.2026 u 08:00. K-6 nije u cijelosti označen završenim: autorstvo nacrta je završeno, nezavisni pregled i provjera Tarikovih pitanja čekaju. Split, modeliranje, evaluacija i drugi zadaci nisu pokretani.

### 2026-11-22 — Izložak ibu_about_programs (BS i EN)

- **Urađeno:** Kreirani `data/exhibits/ibu_about_programs_bs.json` i `data/exhibits/ibu_about_programs_en.json`. Oba planirana izvora otvorena i provjerena 22.11.2026: `/about` podržava institucionalno usmjerenje, lokaciju i strukturu fakulteta, a `/admission` nazive programa, prikazane nivoe studija i poveznice za buduće studente. Činjenice upoređene kroz svih šest odlomaka u oba jezika; nivoi nisu pripisivani svim programima na osnovu općeg pregleda. Dopunjene postojeće lokalne bilješke.
- **Stvarni rezultati:** BS **327 riječi**, EN **353 riječi**; svaki tekst ima 23 rečenice i daje četiri pasusa uz `chunk(size=120, overlap=30)`. JSON ključevi, tipovi, ID-jevi, jezici, izvori i Unicode NFC prolaze. Razdvajanje rečenica čuva sav sadržaj osim normalizacije razmaka; svaka rečenica prisutna je u barem jednom pasusu. `uv run --frozen pytest -q`: **87 passed**. `git diff --check` prolazi. Svih osam očekivanih fajlova za četiri Kerimova izloška postoji, ima 300–800 riječi i uspješno se učitava postojećim loaderom.
- **Sljedeće:** Kerim pregleda i ručno commita/pusha ovu isporuku. Četiri vlastita dvojezična teksta su pripremljena i tehnički provjerena; u ovoj sesiji nije započet drugi zadatak.
- **Blokade / čekam na:** Timski sadržajni pregled i postojeće otvoreno pitanje IBU dozvole za objavu. `course/` nije dostupan lokalno; korišteni su dostupni zahtjevi iz HANDOFF-a i TEAM_PLAN-a. Početno radno stablo bilo je čisto na `kerim/evaluation-and-dataset`; prethodni podcast commitan je kao `53b4cf8`. Prethodnih šest JSON-a nije mijenjano.
- **Ciljevi do sljedećeg roka:** Pregledati posljednji par prije M3 roka 23.11.2026 u 08:00. Potpunost vlastitih izložaka ne označava kompletan dataset ili M3 završenim. Pitanja, evaluacija, paper i slajdovi nisu rađeni; test split nije otvaran. Kerim sam dopunjava AI_LOG i CONTRIBUTIONS.

### 2026-11-22 — Izložak ibu_podcast_media (BS i EN)

- **Urađeno:** Kreirani `data/exhibits/ibu_podcast_media_bs.json` i `data/exhibits/ibu_podcast_media_en.json`. Oba odobrena izvora otvorena su i provjerena 22.11.2026: stranica podcasta podržava opis produkcije, DCPR studija, studentskog formata, poveznica i tema epizoda; članak o BH Radiju 1 podržava opis obrazovne posjete, arhiva i obiđenih studija. Pet odlomaka u oba jezika upoređeno je po činjenicama, uključujući razliku između datuma posjete i objave. Nisu uključena lična imena, kontakti, tvrdnje o publici ili neprovjerena oprema. Dopunjene postojeće lokalne bilješke.
- **Stvarni rezultati:** BS **316 riječi**, EN **378 riječi**; po pet odlomaka, pet JSON polja i dva izvora. `load_exhibits` učitava svih šest JSON-a, a `get_exhibit_text` vraća oba nova teksta. Unicode NFC, nazivi, šema i granice dužine prolaze. `chunk(size=120, overlap=30)` daje po četiri pasusa; svaka izvorna rečenica prisutna je u barem jednom pasusu. `uv run --frozen pytest -q`: **87 passed**. `git diff --check` prolazi.
- **Sljedeće:** Kerim pregleda i ručno commita/pusha ovu isporuku. Četvrti vlastiti izložak je `ibu_about_programs` (BS + EN); nije započet.
- **Blokade / čekam na:** Timski pregled i postojeće otvoreno pitanje IBU dozvole za objavu. `course/` nije dostupan lokalno; korišteni su dostupni zahtjevi iz HANDOFF-a i TEAM_PLAN-a. Početno radno stablo bilo je čisto na `kerim/evaluation-and-dataset`; FESS i FEH već su commitani kao `53d1573` i `5ea19e2` i nisu mijenjani.
- **Ciljevi do sljedećeg roka:** Pregledati ovu isporuku prije M3 roka 23.11.2026 u 08:00. Pitanja i četvrti izložak nisu rađeni; test split nije otvaran. Kerim sam dopunjava AI_LOG i CONTRIBUTIONS.

### 2026-11-22 — Izložak ibu_feh (BS i EN)

- **Urađeno:** Kreirani `data/exhibits/ibu_feh_bs.json` i `data/exhibits/ibu_feh_en.json` za drugi izložak dodijeljen Kerimu. Činjenice provjerene 22.11.2026 na dogovorenoj fakultetskoj stranici i stranici školarina: obrazovno usmjerenje, četiri studijske oblasti, mogući profesionalni pravci, četiri kluba i kategorije školarina. Obje verzije imaju isti skup činjenica, bez ličnih imena, kontakata i tvrdnji o garantovanom zaposlenju. Dopunjene postojeće lokalne bilješke u `study/kerim/`.
- **Stvarni rezultati:** BS 349 riječi; EN 365 riječi; po šest odlomaka, pet JSON polja i dva izvora. `load_exhibits` učitava sva četiri postojeća JSON-a, a `get_exhibit_text` vraća tačan tekst za oba nova jezika. `chunk(size=120, overlap=30)` daje po četiri pasusa. `uv run --frozen pytest -q`: **87 passed**. Provjere JSON šeme, dužine, Unicode zapisa, izvora i `git diff --check` prolaze.
- **Sljedeće:** Kerim pregleda i ručno commita/pusha ovu isporuku. Sljedeći zasebni izložak je `ibu_podcast_media` (BS + EN), prema postojećoj podjeli; nije započet.
- **Blokade / čekam na:** Timski pregled sadržaja i postojeće otvoreno pitanje IBU dozvole za objavu. `course/` nije lokalno dostupan; primijenjeni su dostupni zahtjevi iz HANDOFF-a i TEAM_PLAN-a. Prethodni FESS je commitan kao `53d1573`; početno radno stablo bilo je čisto na `kerim/evaluation-and-dataset`, a FESS fajlovi nisu mijenjani.
- **Ciljevi do sljedećeg roka:** Pregledati ovaj par prije M3 roka 23.11.2026 u 08:00 i nastaviti preostale vlastite izloške u zasebnim isporukama. U ovoj sesiji nisu kreirana pitanja, otvaran test split niti mijenjani AI_LOG i CONTRIBUTIONS; njihove unose dopunjava Kerim.

### 2026-11-22 — Izložak ibu_fess (BS i EN)

- **Urađeno:** Završena jedna samostalna isporuka Kerimovog dijela T-3: `data/exhibits/ibu_fess_bs.json` i `data/exhibits/ibu_fess_en.json`. Obje verzije zasnovane su na fakultetskoj stranici i stranici školarina iz dogovorene liste izvora, otvorenim 22.11.2026. Sadrže iste činjenice o oblastima, odsjecima, praktičnom obrazovanju, klubovima i strukturi studija, bez ličnih imena i kontakata. Dodane lokalne bilješke u `study/kerim/`.
- **Stvarni rezultati:** BS tekst ima 358 riječi, EN tekst 385; oba imaju traženih pet JSON polja i po dva izvora. `load_exhibits` uspješno učitava oba teksta; `chunk(size=120, overlap=30)` daje 4 BS i 5 EN pasusa. `uv run --frozen pytest -q`: **87 passed**. Ovo su tehničke provjere, ne rezultati eksperimenata.
- **Odabir zadatka:** K-1 već ima nacrt, ali potvrda oba recenzenta nije evidentirana lokalno. K-2 je implementiran i postojeći testovi prolaze. K-3/K-4 imaju skripte, ali stvarna analiza i evaluacija čekaju podatke i predikcije. Izložak `ibu_fess`, prvi dodijeljen Kerimu u `data/exhibits/README.md`, nije postojao i predstavlja nezavisno isporučiv preduslov za pitanja i analizu. `course/` nije dostupan lokalno; korišteni su dostupni zahtjevi iz HANDOFF-a i TEAM_PLAN-a.
- **Sljedeće:** Pregledati ovaj par prije ručnog commita i pusha; sljedeća zasebna isporuka je Kerimov `ibu_feh` (BS + EN), do M3 roka 23.11.2026 u 08:00.
- **Blokade / čekam na:** Timski pregled sadržaja i postojeće otvoreno pitanje dozvole IBU-a za objavu; stvarna pitanja, split i baseline predikcije još nedostaju. Nije izvršeno pisanje niti potvrđivanje pitanja, otvaranje test splita ili odobravanje guidelines.
- **Ciljevi do sljedećeg roka:** Nastaviti s preostalim vlastitim izlošcima u odvojenim isporukama; ne označavati kompletan dataset, K-3 ili K-4 završenim bez stvarnih podataka i izlaza. Kerim sam dopunjava AI_LOG i CONTRIBUTIONS.


### 2026-11-16 — Annotation guidelines and evaluation metrics

- **Urađeno:** Kreiran `docs/annotation_guidelines.md` s pravilima za tri klase pitanja, granične slučajeve, BS/EN anotaciju i tačne answer spanove. Implementiran `src/talking_exhibits/evaluate.py` s refusal metrikama, confusion matricom, jezičkim filterima i bootstrap 95% CI. Dodan `tests/test_metrics.py`.
- **Stvarni rezultati:** 20 novih testova i ukupno 36 testova prošlo je uz `PYTHONPATH=src`. Stvarne baseline predikcije još nisu evaluirane.
- **Sljedeće:** Tarik i Mirza trebaju pregledati i potvrditi annotation guidelines. Nastaviti s `scripts/data_analysis.py` i `scripts/evaluate_all.py`.
- **Blokade / čekam na:** Mirzin PR #2, tekstovi izložaka, validation dataset i baseline predikcije.
- **Ciljevi do sljedećeg roka:** Predati K-1 i K-2 kroz Pull Request. Do 19.11. pripremiti analizu podataka i evaluacijske izvještaje.


### 2026-11-16 — Data analysis and baseline evaluation scripts (K-3/K-4)

- **Urađeno:** Implementiran `scripts/data_analysis.py` za statistiku pitanja i tekstova izložaka, Jaccardovo preklapanje i PNG grafikone. Implementiran `scripts/evaluate_all.py` za evaluaciju baseline predikcija na validacijskom skupu, uključujući refusal metrike, jezičke rezultate i bootstrap intervale pouzdanosti.
- **Provjera:** Obje skripte prošle provjeru Python sintakse i kontrolno pokretanje na šest sintetičkih pitanja. Generisano svih šest očekivanih izlaznih fajlova. Postojećih 36 testova prolazi.
- **Blokade:** Stvarni `questions.csv` još nema pitanja, `data/exhibits/` nema tekstove, a `data/processed/val.csv` i baseline predikcije nisu dostupni.
- **Sljedeće:** Uskladiti format predikcija s Mirzom, pokrenuti skripte na stvarnim podacima, provjeriti rezultate i dopuniti izvještaje.


### 2026-11-12 — fajl napravljen (Mirzina sesija)
- **Urađeno:** napravljene lične upute. Kerim još nije imao sesiju s Claude Code-om.
- **Sljedeće:** K-1 annotation guidelines (blokira pisanje pitanja), pa K-2 `evaluate.py`.
- **Blokade:** nema; guidelines trenutno blokiraju ostale.
