# TEAM_PLAN — ko šta radi, kako i kad

Plan rada za tim i za Claude Code. Čita se zajedno s `HANDOFF.md`: HANDOFF objašnjava **šta** je projekat i **zašto** je takav, a ovaj fajl kaže **ko, kako i kad** radi.

Stanje na dan pisanja: **08.11.2026**. M1 i M2 su predani. **M3 je u ponedjeljak 23.11.2026 u 08:00**, za 15 dana. Plan iz HANDOFF-a (sedmice 4–5) kasni, pa je ovdje sabijen.

---

## 1. Pravila za Claude Code (OBAVEZNA)

Ova pravila su iznad svega ostalog u repou. Ako se nešto kosi s njima, važe ona.

### 1.1 Git: Claude nikad ne commita i ne pusha
- Claude **NIKAD** ne pokreće `git commit`, `git push`, `git add`, `git merge`, `git rebase`, `git reset`, `git checkout -- <fajl>`, `git stash`, `git tag` ni bilo šta što mijenja git historiju ili staging.
- Smije samo čitati: `git status`, `git diff`, `git log`, `git show`, `git branch` (bez brisanja), `git config user.name`.
- Na kraju zadatka Claude ispiše:
  1. listu fajlova koje je napravio ili promijenio,
  2. prijedlog commit poruke na engleskom,
  3. komande koje član **sam** pokreće (`git add ...`, `git commit -m "..."`, `git push`).
- Razlog: svaki član mora commitati svoj rad sa svog naloga, a git historija se boduje po osobi.

### 1.2 AI_LOG i CONTRIBUTIONS pišu studenti
- Claude **NE PIŠE i NE MIJENJA** `docs/AI_LOG.md` ni `CONTRIBUTIONS.md`.
- Na kraju zadatka Claude samo podsjeti člana da upiše unos i navede činjenice koje mu za to trebaju: datum, šta je tražio, koje fajlove je Claude dirao. Formulaciju piše član svojim riječima.

### 1.3 Pitaj i objasni, pa tek onda radi
Svaki zadatak ide ovim redom:
1. **Razumijevanje:** Claude kratko ponovi šta je shvatio da treba i pita ako nešto nije jasno.
2. **Plan i objašnjenje:** šta će napraviti, kojim fajlovima, zašto baš tako, koji NLP koncept je u pozadini (2–6 rečenica), te alternative i zašto ih ne bira.
3. **Čeka potvrdu** ("može", "radi", "ok"). Bez potvrde ne piše kod niti mijenja fajlove.
4. **Radi u malim koracima:** napiše, pokrene, pokaže output. Kod većeg zadatka staje nakon svakog koraka.
5. **Objasni šta je urađeno** i postavi 1–2 kontrolna pitanja da član provjeri razumije li.
6. **Upiše bilješku za učenje** (1.4).

Izuzetak: čitanje fajlova, pokretanje testova i read-only komande ne traže potvrdu.

### 1.4 Bilješke za učenje i odbranu (Obsidian), posebno za svakog člana
- Na početku sesije Claude utvrdi **s kim radi**: pročita `git config user.name`, a ako nije jasno, pita. Dalje piše samo u folder tog člana.
- Struktura (folder `study/` je u `.gitignore` i ostaje lokalno na računaru člana):

```
study/                      ← otvori ovaj folder kao Obsidian vault
├── mirza/
│   ├── LEARNING_LOG.md     ← dnevnik: šta je rađeno, sesija po sesija
│   ├── DEFENSE_QA.md       ← pitanja za odbranu i odgovori
│   └── concepts/           ← jedna bilješka po konceptu
│       ├── BM25.md
│       ├── Cross-encoder.md
│       └── ...
├── tarik/   (ista struktura)
└── kerim/   (ista struktura)
```

- **LEARNING_LOG.md:** nakon svakog zadatka Claude doda unos na vrh fajla, po ovom šablonu:

```markdown
## 2026-11-10 — BM25 retrieval nad izlošcima
**Zadatak:** ...
**Fajlovi:** [[src/talking_exhibits/retrieval.py]] (`bm25_search`, linije 20–58)
**Šta kod radi (svojim riječima):** ...
**Zašto ovako:** odluke i odbačene alternative
**Koncepti:** [[BM25]], [[Tokenizacija]], [[Retrieval]]
**Kako pokrenuti i provjeriti:** `uv run python scripts/run_baselines.py --system bm25`
**Rezultat / output:** stvarni brojevi iz pokretanja, nikad izmišljeni
**Greške usput i kako su riješene:** ...
**Pitanja koja profesorica može postaviti:** 2–3 pitanja, odgovori u [[DEFENSE_QA]]
```

- **concepts/<Koncept>.md:** kratko objašnjenje (definicija, formula ako postoji, primjer na našim podacima, gdje je u našem kodu, link na sedmicu kursa i poglavlje iz Jurafsky & Martin). Frontmatter i tagovi:

```markdown
---
tags: [nlp, retrieval, sedmica-13]
kurs: "Week 13: Semantic Search & RAG"
kod: src/talking_exhibits/retrieval.py
---
```

  Postojeću bilješku Claude dopuni, nikad je ne duplira. Koristi `[[wikilinkove]]` da se u Obsidianu vidi graf koncepata.
- **DEFENSE_QA.md:** pitanja grupisana po temama (Podaci, Baseline, Glavna metoda, Evaluacija, Greške, Kod). Svako pitanje ima kratak odgovor i link na kod i koncept. Član pokrije odgovore i vježba **naglas, bez AI-a**, jer na odbrani AI nije dozvoljen.
- Član mora razumjeti i **tuđe** dijelove projekta, jer se na odbrani pita o cijelom projektu. Zato Claude jednom sedmično, na zahtjev, napravi u folderu člana `CROSS_REVIEW.md` sa sažetkom onoga što su druga dvojica uradila (iz `git log` i koda).

### 1.5 Ostala pravila (iz HANDOFF-a)
- Razgovor na **bosanskom** (ijekavica). Kod, komentari, docstringovi, README i paper su na **engleskom**.
- **Nikad ne izmišljaj** rezultate, brojeve, datasetove ni reference. Svaki broj mora doći iz pokrenutog koda, a svaka referenca iz otvorenog izvora.
- Seed **3004**, sve komande preko **`uv run`**, novi paketi idu u `pyproject.toml` (član pokreće `uv add`, Claude predloži).
- **Test set se ne dira** dok konfiguracija nije zaključana. Podešavanje se radi samo na val.
- Jednostavan, komentarisan kod u stilu lab repoa (`nlp3004/labs-2026-2027`): jedna funkcija za jedan korak, provjera ulaza s jasnom greškom, testovi u `tests/`.
- Claude radi samo na zadacima **člana s kojim radi**. Tuđe fajlove mijenja samo uz pitanje i kaže koga treba obavijestiti.
- Materijali kursa su u `course/` (u `.gitignore`, jer su to profesoričini materijali i ne objavljuju se). Claude ih čita na početku, a za pravila uvijek provjerava `course/` i `HANDOFF.md`.
- Ako je zadatak nejasan i skup za vraćanje (promjena metode, novi dataset, promjena splita), Claude pita. Ako je jeftin, odluči, kaže šta je odlučio i nastavi.

---

## 2. Raspodjela uloga (kratko)

| Član | Glavna uloga | Kod (vlasnik fajlova) | Paper | Odbrana: mora najbolje znati |
| --- | --- | --- | --- | --- |
| **Mirza Čakal** | Retrieval pipeline + answerability klasifikator | `data.py`, `preprocess.py`, `retrieval.py`, `answerability.py`, `scripts/run_baselines.py`, `scripts/train_classifier.py`, `notebooks/` | Methodology; Literature Review (pola) | Chunking, BM25, e5, cross-encoder, fine-tuning, prag |
| **Tarik Hadrović** | Podaci: izlošci, pitanja, split, kvalitet anotacije | `data/exhibits/`, `data/questions/`, `scripts/build_dataset.py`, `scripts/validate_questions.py`, `tests/test_data.py` | Dataset; Literature Review (pola) | Kako je napravljen dataset, klase, split po izlošku, kappa, licence |
| **Kerim Hodžić** | Evaluacija, analiza, LLM baseline, demo | `evaluate.py`, `scripts/evaluate_all.py`, `scripts/data_analysis.py`, `llm_baseline.py`, `demo/`, `docs/annotation_guidelines.md`, `tests/test_metrics.py` | Introduction; Results; slajdovi | Metrike (F1, AUROC, risk–coverage), bootstrap CI, analiza grešaka |

Svi zajedno: svako piše **100 pitanja**, svako provjerava pitanja drugog člana, svako upisuje svoj AI_LOG i CONTRIBUTIONS, svako prezentira dio.

Lanac provjere pitanja: **Mirza → provjerava Tarik**, **Tarik → provjerava Kerim**, **Kerim → provjerava Mirza**.

---

## 3. Vremenski plan do M3

```
pon 9.11 ──► uto 10.11 ──► pet 13.11 ──► pon 16.11 ──► čet 19.11 ──► ned 22.11 ──► PON 23.11 08:00 (M3)
  odluka      guidelines     izlošci        pitanja        B1 rezultati   paper nacrt     predaja
  izlošci     + skeleton     gotovi         provjerena     + grafike      + README
```

| Rok | Šta mora biti gotovo | Ko |
| --- | --- | --- |
| **pon 9.11** | **Odluka o izlošcima** (preporuka: 10–12 izložaka o IBU kampusu, zgradama, projektima i historiji) | Svi, odluku upisuje Tarik u HANDOFF §13 |
| **uto 10.11** | `docs/annotation_guidelines.md`; skeleton koda (`data.py`, `preprocess.py`) s testovima; šema `questions.csv` i validator | Kerim; Mirza; Tarik |
| **pet 13.11** | Svi tekstovi izložaka BS + EN s izvorima; BM25 retrieval radi nad njima | Tarik; Mirza |
| **pon 16.11** | 300 pitanja napisano (100 po članu); `evaluate.py` s metrikama i testovima | Svi; Kerim |
| **čet 19.11** | Sva pitanja provjerena; kappa izračunata; split po izlošku; **B0 i B1 s prvim rezultatima na val**; ≥2 tabele/grafika o podacima | Tarik; Mirza + Kerim; Kerim |
| **ned 22.11** | README s pokretanjem; nacrt dijagrama pipelinea; paper u 02 Paper: Introduction, Literature Review (≥8 izvora, 5 direktno o problemu), Dataset; svako ažurira AI_LOG i CONTRIBUTIONS i pusha | Svi |
| **pon 23.11 08:00** | **Rok M3**. Ništa se ne mijenja poslije 08:00 | — |
| **sedmica 8 (lab)** | Check-in od ~5 min: podaci, baseline, plan glavne metode; svako objašnjava svoj dio | Svi |

Napomena: za M3 baseline se prijavljuje na **val**, ne na test. Test se otvara tek u finalnoj evaluaciji.

---

## 4. Detaljni zadaci po članu

### 4.1 Mirza Čakal — retrieval i klasifikator

**Do M3**

| # | Zadatak | Kako | Gotovo kad | Rok |
| --- | --- | --- | --- | --- |
| M-1 | `src/talking_exhibits/data.py` | `load_exhibits(dir)` čita `data/exhibits/*.json` i provjerava polja (`id`, `title`, `lang`, `text`, `sources`); `load_questions(path)` čita CSV i provjerava kolone. Jasna greška ako nešto fali, isto kao `collect.py` u labu | `uv run pytest tests/test_data.py` prolazi | 10.11 |
| M-2 | `src/talking_exhibits/preprocess.py` | `normalize(text)`: lowercase za BM25, **dijakritike se čuvaju**; `strip_diacritics` samo kao pomoćna funkcija za poređenje. `chunk(text, size≈120 riječi, overlap≈30)` po rečenicama | Testovi za chunking (nijedna rečenica nije izgubljena, overlap tačan) | 10.11 |
| M-3 | `src/talking_exhibits/retrieval.py`: BM25 | `rank-bm25` nad pasusima **jednog izloška**; `bm25_search(question, exhibit_id, k)` vraća pasuse i score | Ručna provjera na 10 pitanja: je li pravi pasus u top-3 | 13.11 |
| M-4 | Isto: dense retrieval e5 | `intfloat/multilingual-e5-base`, prefiksi `query: ` i `passage: `, keš embeddinga u `data/processed/` | Recall@3 za BM25 i e5 na val (answerable pitanja) | 19.11 |
| M-5 | `scripts/run_baselines.py`: B0 i B1 | B0 = uvijek odgovara. B1 = odbij ako max BM25 score < prag; prag bira grid search na val, maksimizira refuse-F1. Isto i za e5 (B1b) | `results/val_baselines.json` + tabela u terminalu | 19.11 |
| M-6 | Paper: Literature Review (pola) | ≥4 izvora: retrieval (BM25, DPR, e5), RAG, XLM-R, BERTić. Svaki izvor otvoren i ubačen u Zotero | Tekst u 02 Paper | 22.11 |
| M-7 | Pitanja | 100 pitanja (50 BS, 50 EN) za dodijeljene izloške; provjera Kerimovih pitanja | Validator prolazi | 16.11 / 19.11 |

**Poslije M3:** fine-tuning XLM-R cross-encodera na Colabu (`scripts/train_classifier.py` + notebook), kalibracija praga, ablacije M-zs i (opcionalno) BERTić, Methodology sekcija u paperu.

**Mirzin Claude posebno pazi na:** učenje kroz kod (nakon svakog modula 3 pitanja tipa "šta bi se desilo kad bi..."), te da je trening reproducibilan i pokreće se iz skripte, a ne samo iz notebooka.

### 4.2 Tarik Hadrović — podaci

**Do M3**

| # | Zadatak | Kako | Gotovo kad | Rok |
| --- | --- | --- | --- | --- |
| T-1 | Odluka o izlošcima i lista | `data/exhibits/README.md`: id, naslov, izvor (URL), ko piše tekst. Pitati IBU (PR ili studentska služba) za dozvolu objave tekstova | Lista od 10–12 izložaka; upisano u HANDOFF §13 | 9.11 |
| T-2 | Šema i validator pitanja | `scripts/validate_questions.py`: kolone iz HANDOFF §5.2; `answer_text` mora biti tačno na `answer_start` u tekstu izloška; klase samo iz dozvoljene liste; nema duplikata `qid`; `checked_by` ≠ `author` | `uv run python scripts/validate_questions.py` ispiše "OK" ili listu grešaka | 10.11 |
| T-3 | Tekstovi izložaka | 300–800 riječi po izlošku, BS + EN, napisani **svojim riječima** iz javnih izvora, izvori u `sources`. Mirza i Kerim pišu po 3–4 izloška, Tarik ostale i ujednačava stil | Svi JSON fajlovi prolaze `load_exhibits` | 13.11 |
| T-4 | Koordinacija pitanja | Podijeli izloške za pisanje pitanja (svako ~4 izloška). Ciljna raspodjela: 45% answerable, 40% unanswerable_plausible, 15% out_of_scope; ~20% BS pitanja bez dijakritika | Brojevi po klasi i jeziku u tabeli | 16.11 |
| T-5 | Provjera i slaganje | ~50 pitanja anotiraju dvojica nezavisno → **Cohen's kappa** (`sklearn.metrics.cohen_kappa_score`). Razmimoilaženja riješiti zajedno i upisati pravila u guidelines | Kappa broj + lista riješenih spornih slučajeva | 19.11 |
| T-6 | `scripts/build_dataset.py` | Split **po izlošku** (otprilike 60/15/25 % izložaka), seed 3004, test ≥100 pitanja; snimi `data/processed/{train,val,test}.csv` | Script štampa broj pitanja po splitu, klasi i jeziku | 19.11 |
| T-7 | Paper: Dataset | Izvori izložaka, proces pisanja pitanja, klase s primjerima, kappa, split, licence (SQuAD 2.0 CC BY-SA 4.0), etika i privatnost | Tekst u 02 Paper | 22.11 |
| T-8 | Paper: Literature Review (pola) | ≥4 izvora: SQuAD 2.0, selective QA i abstention, halucinacije, regionalni QA resursi | Tekst u 02 Paper | 22.11 |
| T-9 | Pitanja | 100 svojih pitanja; provjera Mirzinih | Validator prolazi | 16.11 / 19.11 |

**Poslije M3:** finalna verzija dataseta, priprema SQuAD 2.0 parova za trening (zajedno s Mirzom), kategorije grešaka u analizi, dio slajdova o podacima.

**Tarikov Claude posebno pazi na:** da nikad ne piše tekstove izložaka ni pitanja **umjesto** Tarika za test set (test mora biti ljudski), te da objasni zašto je split po izlošku, šta mjeri kappa i kako se čita.

### 4.3 Kerim Hodžić — evaluacija, analiza, demo

**Do M3**

| # | Zadatak | Kako | Gotovo kad | Rok |
| --- | --- | --- | --- | --- |
| K-1 | `docs/annotation_guidelines.md` | Definicija svake klase s 2–3 primjera, granični slučajevi (djelimičan odgovor, zaključivanje, brojevi riječima, sinonimi), pravilo za `answer_start` | Tarik i Mirza pročitali i potvrdili | 10.11 |
| K-2 | `src/talking_exhibits/evaluate.py` | `refuse_metrics(gold, pred)` (precision, recall, F1 klase refuse), false refusal rate, macro-F1, confusion matrica, `bootstrap_ci(metric, n=1000, seed=3004)`, sve po jeziku i po klasi | `tests/test_metrics.py` s ručno izračunatim primjerima prolazi | 16.11 |
| K-3 | `scripts/data_analysis.py` | Tabele i grafike: broj pitanja po klasi × jeziku; dužina pitanja i izložaka; udio pitanja bez dijakritika; leksičko preklapanje pitanja i teksta po klasi (zanimljivo: plausible pitanja dijele riječi s tekstom) | ≥2 figure u `results/figures/` + tabela u Markdownu | 19.11 |
| K-4 | `scripts/evaluate_all.py` (prva verzija) | Učita predikcije B0/B1/B1b, izračuna sve metrike, snimi `results/metrics_val.json` i tabelu za paper | Jedna komanda daje sve brojeve | 19.11 |
| K-5 | Paper: Introduction | Problem, motivacija, RQ1–3, doprinos, struktura rada | Tekst u 02 Paper | 22.11 |
| K-6 | Pitanja | 100 svojih pitanja; provjera Tarikovih | Validator prolazi | 16.11 / 19.11 |
| K-7 | M3 prezentacija | 3–4 slajda ili ekran za 5-minutni check-in: podaci, baseline brojevi, plan | Spremno za lab | 22.11 |

**Poslije M3:** B2 prompted LLM (`llm_baseline.py`, Ollama), risk–coverage i AUROC, **analiza grešaka (cilj 20)** u `results/errors.csv`, demo (FastAPI ili Streamlit + QR kodovi), Results sekcija, slajdovi.

**Kerimov Claude posebno pazi na:** da član ručno izračuna bar jedan primjer svake metrike prije nego što prihvati kod, te da objasni zašto se prijavljuje refuse-F1, a ne accuracy.

---

## 5. Plan poslije M3 (do finalne predaje)

| Faza | Šta | Ko |
| --- | --- | --- |
| 24.11–6.12 | Fine-tuning klasifikatora (Colab, seed 3004); B2 LLM baseline; feedback s M3 upisan u HANDOFF §13 | Mirza; Kerim; svi |
| 7.12–13.12 | Ablacije (M-zs, BERTić opcionalno), kalibracija praga na val, **zaključavanje konfiguracije**, pa tek onda jedno pokretanje na testu | Mirza, Kerim |
| 14.12–20.12 | Analiza grešaka (20); figure; demo s QR kodovima | Kerim, Tarik |
| 21.12–ispitni rok | Paper: Methodology (Mirza), Results (Kerim), Discussion and Limitations (svi), Conclusion, Author Contributions, AI Tools Disclosure; slajdovi; **probna prezentacija**; svako prođe cijeli kod | Svi |

Tačni datumi zavise od ispitnog rasporeda na LMS-u. Sve mora biti predano prije početka ispitnog roka.

---

## 6. Rutina jedne sesije s Claude Codeom

1. Član otvori terminal u repou i pokrene `git pull`.
2. Pokrene Claude Code. Claude pročita `CLAUDE.md`, a ono ga uputi na `TEAM_PLAN.md`, `HANDOFF.md` i `course/`.
3. Claude utvrdi s kim radi, pogleda `git log` od zadnje sesije i `study/<član>/LEARNING_LOG.md`, pa predloži sljedeći zadatak iz §4.
4. Rad ide po §1.3: razumijevanje, plan, potvrda, mali koraci, objašnjenje.
5. Na kraju Claude:
   - upiše unos u `study/<član>/LEARNING_LOG.md` i dopuni `concepts/` i `DEFENSE_QA.md`,
   - ispiše listu promijenjenih fajlova, prijedlog commit poruke i git komande,
   - podsjeti člana da upiše **AI_LOG** i **CONTRIBUTIONS** (navede činjenice, ne piše tekst u fajl).
6. Član pregleda diff, upiše AI_LOG i CONTRIBUTIONS, pa **sam** commita i pusha.

## 7. Obsidian: podešavanje za svakog člana

1. Instaliraj Obsidian (obsidian.md, besplatan).
2. Open folder as vault → izaberi `talking-exhibits/study/`. Vault je lokalni, ne ide u git.
3. Settings → Files and links → uključi **Use [[Wikilinks]]**, a *Default location for new notes* postavi na tvoj folder (`mirza/`, `tarik/` ili `kerim/`).
4. Korisni prikazi:
   - **Graph view:** veze između koncepata i koda; prije odbrane provjeri da nijedan koncept nije "ostrvo".
   - **Tags pane:** filtriranje po sedmici kursa (`sedmica-13`) ili temi (`retrieval`, `evaluacija`).
   - **Backlinks:** iz bilješke `BM25` vidiš svaku sesiju u kojoj se pojavio.
5. Opcionalno: core plugin **Daily notes** za lične bilješke s predavanja. Claude ih ne dira.
6. Pred odbranu: otvori `DEFENSE_QA.md`, pokrij odgovore i odgovaraj naglas. Za svaku rupu otvori koncept i kod.
7. `CROSS_REVIEW.md` (sažetak tuđeg rada) traži od Claudea jednom sedmično.
