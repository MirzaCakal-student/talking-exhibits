# HANDOFF — Talking Exhibits (IT 3004, IBU)

Ovaj fajl je **jedini izvor istine** za projekat. Čita ga svaki član tima i svaki Claude (ili drugi AI asistent) koji radi na repou, **prije** bilo kakvog rada. Kad se nešto bitno promijeni (odluka, rok, metoda), ažuriraj ovaj fajl u istom commitu.

> Za Claude: pročitaj cijeli fajl, pa `README.md`, `CONTRIBUTIONS.md` i `docs/AI_LOG.md`. Sekcija 12 ima pravila kako radiš s nama.

---

## 0. Brze činjenice

| | |
| --- | --- |
| Predmet | IT 3004 Introduction to Natural Language Processing, International Burch University, 2026/2027, semestar V |
| Profesorica | Assist. Prof. Dr. Dželila Mehanović (dzelila.mehanovic@ibu.edu.ba) |
| Asistentica | Ilma Dlakić (ilma.dlakic@ibu.edu.ba) |
| Tim | Mirza Čakal (mirza.cakal@stu.ibu.edu.ba), Tarik Hadrović (tarik.hadrovic@stu.ibu.edu.ba), Kerim Hodžić (kerim.hodzic@stu.ibu.edu.ba) |
| Tema | #1 Talking exhibits |
| Naslov | Talking Exhibits: Detecting Unanswerable Visitor Questions in Exhibit-Grounded Question Answering for Bosnian and English |
| Težina | Projekat **je** završni ispit: **50% ocjene** |
| Jezik rada, koda, papera | Engleski. Razgovor u timu i s Claudeom: bosanski. |
| Drive | Zajednički folder kursa → `Čakal, Hadrović, Hodžić` → `01 Proposal`, `02 Paper` (Google Doc), `03 Presentation` (Google Slides) |
| GitHub | Repo `talking-exhibits` (dijeljen s profesoricom i asistenticom) |
| Lab repo (stil koda koji profesorica voli) | https://github.com/nlp3004/labs-2026-2027 |

## 1. Rokovi

| Milestone | Rok (08:00) | Status | Šta |
| --- | --- | --- | --- |
| M1 Tim i tema | 19.10.2026 | ✅ predano | Form 1 |
| M2 Prijedlog i repo | 26.10.2026 | ✅ predano | 01 Proposal + repo s README, CONTRIBUTIONS.md, docs/AI_LOG.md + Form 2 |
| **M3 Mid-semester check-in** | **23.11.2026** | ⏳ sljedeće | Vidi sekciju 9 |
| Finalna predaja | Prije početka ispitnog roka | ⏳ | Kod, podaci, paper, slajdovi |
| Prezentacija + individualna pitanja | Ispitna sedmica | ⏳ | 10–15 min, svako prezentira, pitanja **bez AI-a** |

Zakasnjeli milestone = 0 bodova za taj milestone. Sve što se brani mora biti predano prije ispitnog roka; Drive i git historija se provjeravaju.

## 2. Obavezni zahtjevi (iz "Project Requirements and Guidelines")

Projekat **mora** imati:

- [ ] Jasno definisan NLP problem
- [ ] Dataset, uključujući **test set koji je tim pripremio ili provjerio, minimum 100 primjera**
- [ ] Preprocessing i analizu podataka
- [ ] **Bar jedan baseline i jednu glavnu NLP metodu**
- [ ] Sistematsku evaluaciju
- [ ] Diskusiju i **analizu grešaka (minimum 10 analiziranih grešaka)**
- [ ] Radni prototip ili reproducibilnu implementaciju
- [ ] Research paper po Project Report Guidelines (max 20 strana bez referenci i priloga)
- [ ] Finalnu prezentaciju

**Najvažnije pravilo:** bar jedna centralna NLP komponenta mora biti **implementirana, trenirana ili fine-tunovana od strane tima**. Pipeline sastavljen samo od API poziva ili promptova **ne prolazi**. Ako je LLM glavna metoda, tim i dalje mora imati svoj baseline. → Zato je naša glavna metoda **fine-tunovani answerability klasifikator**, a ne "RAG sa strogim promptom".

UI je opcionalan. Sam vizuelni interfejs nije NLP projekat. Rad na integraciji i interfejsu nosi manje bodova od NLP komponente.

**Reproducibilnost (GitHub):**
- Organizovan, čitljiv, komentarisan kod koji radi bez nedokumentovanih ručnih koraka
- README s instalacijom i pokretanjem, dependency fajl, **fiksni random seedovi**
- Jasno označeni pretrenirani modeli, API-ji, eksterni kod; **README ima dijagram pipelinea koji označava šta je naše, a šta eksterno**
- **Svaki član commita svoj rad sa svog GitHub naloga**
- `CONTRIBUTIONS.md` (ko je šta radio) i `docs/AI_LOG.md` (**svaka** upotreba AI alata)

**Etika i podaci:** legalno korištenje i citiranje svih datasetova; bez privatnih poruka, imena, mailova, studentskih podataka. Ako uključujemo ljude van tima (npr. kolege pišu pitanja), **prvo tražiti odobrenje profesorice**.

**Ocjenjivanje:** Implementacija (tim), redovni rad M1–M3 (tim, korigovano po doprinosu), paper (tim), prezentacija (pojedinac), individualna pitanja (pojedinac). Ako git historija, CONTRIBUTIONS ili odgovori pokažu da neko nije doprinio ili ne razumije projekat, bodovi mu se smanjuju **do 0**.

## 3. Problem i istraživačka pitanja

Posjetilac skenira QR kod pored izloška (IBU kampus, projekti, historija), postavi pitanje (tekst, opcionalno glas) i dobije odgovor **samo iz teksta tog izloška**. Ako tekst nema odgovor, sistem mora **odbiti** umjesto da izmišlja.

- **RQ1 (glavno, iz liste tema):** How reliably can the system detect questions the exhibit text cannot answer and refuse instead of guessing?
- **RQ2:** Does a team-trained answerability classifier detect unanswerable questions better than a retrieval-score threshold and a prompted LLM?
- **RQ3:** Is refusal detection weaker for Bosnian questions than for English ones?

## 4. Arhitektura

```
QR stranica izloška ──► pitanje ──► [Retrieval nad tekstom TOG izloška] ──► top-k pasusa
                                                                 │
                                         [Answerability klasifikator] ── p(answerable)
                                                │                         │
                                         ≥ prag (answer)            < prag (refuse)
                                                │                         │
                               [Odgovor iz pasusa: extractive QA / LLM]   "Ovaj izložak to ne navodi."
```

| Komponenta | Naše / eksterno | Napomena |
| --- | --- | --- |
| Chunking izložaka (rečenice → pasusi ~100–150 riječi, overlap) | Naše | |
| BM25 retrieval + prag (Baseline 1) | Naše | `rank-bm25` |
| Dense retrieval | Eksterno model, naš pipeline | `intfloat/multilingual-e5-base`, MIT licenca. **Obavezni prefiksi** `"query: "` i `"passage: "`, max 512 tokena |
| **Answerability klasifikator (glavna metoda)** | **Naše (fine-tuning)** | Cross-encoder nad (pitanje, pasus), baza `xlm-roberta-base`; opcionalno poređenje s `classla/bcms-bertic` |
| Kalibracija praga | Naše | Na validation setu |
| Prompted LLM (Baseline 2) | Eksterno | Open model preko Ollame (npr. Qwen ili Llama, mali model) ili API |
| Formulacija odgovora | Eksterno | Extractive QA model ili LLM, **samo** nad odobrenim pasusom |
| Speech-to-text | Eksterno, opcionalno | Whisper |
| Web demo + QR kodovi | Naše | FastAPI ili Streamlit, `qrcode` paket |
| Question set, test set, evaluacija, analiza grešaka | Naše | |

## 5. Podaci

### 5.1 Izlošci (knowledge base)
- **Otvorena odluka:** koji izlošci. Preporuka: 10–15 izložaka o IBU kampusu, zgradama, projektima i historiji (tim to može "posjedovati" i provjeriti). Alternativa: Sarajevo/muzej.
- Svaki izložak: 300–800 riječi, **BS i EN verzija**, izvori navedeni.
- Tekst piše tim na osnovu javnih IBU stranica i brošura (ne copy-paste). Tražiti od IBU dozvolu za objavu; ako je nema, repo sadrži linkove izvora i upute.
- Format: `data/exhibits/<exhibit_id>.json` → `{"id", "title", "lang", "text", "sources": [url...]}`.

### 5.2 Question set (naš, najvažniji podaci)
- Cilj 300 pitanja (minimum 100 u **test** setu), pola BS pola EN.
- Tri klase:
  - `answerable` — odgovor postoji u tekstu (+ `answer_text`, `answer_start`)
  - `unanswerable_plausible` — na temu izloška, zvuči kao da bi trebalo biti tu, ali nije (srž istraživanja; npr. cijena, ime arhitekte, godina koja se ne spominje)
  - `out_of_scope` — nema veze s izloškom
- Ciljna raspodjela: ~45% answerable, ~40% unanswerable_plausible, ~15% out_of_scope.
- Bez dijakritika i neformalno pisanje u ~20% BS pitanja (realno ponašanje posjetilaca).
- Fajl: `data/questions/questions.csv`

| kolona | primjer |
| --- | --- |
| `qid` | `q0001` |
| `exhibit_id` | `ibu_library` |
| `lang` | `bs` / `en` |
| `question` | `Koliko knjiga ima biblioteka?` |
| `label` | `answerable` / `unanswerable_plausible` / `out_of_scope` |
| `answer_text` | prazno ako nije answerable |
| `answer_start` | char offset u tekstu izloška, prazno ako nije answerable |
| `author` | `mirza` / `tarik` / `kerim` |
| `checked_by` | drugi član koji je provjerio |
| `split` | `train` / `val` / `test` |

- **Pravila anotacije** napisati u `docs/annotation_guidelines.md` prije pisanja pitanja (granični slučajevi: djelimični odgovor, odgovor koji traži zaključivanje, brojevi napisani riječima).
- Svako pitanje provjerava **drugi** član. Izmjeriti slaganje (Cohen's kappa) na ~50 dvostruko anotiranih pitanja → ide u paper.
- **Split po izlošku** (npr. 60/15/25 izložaka), nikad po pitanju, da test izlošci nisu viđeni u treningu ni u podešavanju praga.
- Synthetic pitanja (od LLM-a) **smiju** u train, ali u testu samo pitanja koja je čovjek napisao ili provjerio. Označiti u koloni `source` (`human` / `llm_checked`).

### 5.3 Trening podaci za klasifikator
- **SQuAD 2.0** (Rajpurkar et al., 2018), HF `rajpurkar/squad_v2`, **CC BY-SA 4.0**, 130,319 train / 11,873 validation. Neodgovorivo pitanje = prazna lista `answers.text`.
  - Parovi: (pitanje, kontekst) → label `answerable` ako `answers.text` nije prazan.
  - Dodatni negativi: pitanje + pasus iz **drugog** konteksta (lako) — da model vidi i out-of-scope.
  - Za brzinu treninga dovoljan je podskup (npr. 30–50k parova).
- **Naš train split** (BS + EN) za domensku adaptaciju.
- Opcije za više bosanskog/regionalnog signala (provjeriti licence prije upotrebe):
  - Mašinski prevod dijela SQuAD 2.0 na bosanski (dokumentovati model prevoda; prevesti pitanje i kontekst, za unanswerable nema problema sa spanom).
  - `te-sla/QuestionAnswering` (srpski, SQuAD-sr-md ~7k ručno ispravljenih + SerbianQA-Gen ~74k sintetičkih, CC BY-SA 4.0) — **nema unanswerable pitanja**, može samo kao answerable pozitivi.
  - Slovenski SQuAD 2.0 prevod na CLARIN.SI (CC BY 4.0, ima unanswerable) — srodan jezik, eksperiment cross-lingual transfera.

## 6. Metode i eksperimenti

| Sistem | Tip | Opis |
| --- | --- | --- |
| **B0** Always-answer | trivijalni baseline | Nikad ne odbija → pokazuje koliko pogrešnih odgovora bi bilo |
| **B1** BM25 + prag | naš baseline | Odbij ako je max BM25 score < prag (prag na val) |
| **B1b** e5 + prag | naš baseline | Isto, s kosinusnom sličnošću e5 embeddinga |
| **B2** Prompted LLM | eksterni baseline | "Answer only from the text; otherwise reply exactly: NOT_IN_TEXT". Isti retrieval kao glavni sistem |
| **M** Answerability klasifikator | **glavna metoda** | XLM-R-base cross-encoder, fine-tunovan na SQuAD 2.0 (+ naš train) |
| M-zs | ablacija | Samo SQuAD 2.0, bez našeg train seta (zero-shot na bosanskom → RQ3) |
| M-bertic | ablacija, opcionalno | BERTić umjesto XLM-R |
| M + LLM | demo konfiguracija | Klasifikator odlučuje, LLM samo formuliše odgovor iz odobrenog pasusa |

**Fine-tuning (početne postavke, mijenjati samo na val):** `max_length=384`, lr `2e-5`, batch 16, 2–3 epohe, warmup 10%, seed 3004 (isti kao u labu). Ulaz: `[CLS] pitanje [SEP] pasus [SEP]`. Odluka na nivou izloška: `max` vjerovatnoće preko top-k pasusa.

**Hardver:** Mirzin PC ima AMD GPU (bez CUDA-e). Trening raditi u **Google Colab** ili **Kaggle** (besplatni GPU). Notebook u `notebooks/`, ali logika mora biti u `src/` i `scripts/` da je reproducibilno. Sačuvati modele van gita (`models/`), a u README napisati kako se dobiju.

## 7. Evaluacija

Pravilo iz laba: **podešavaj na val, prijavljuj na test.** Test set se ne gleda dok se ne zaključa konfiguracija.

- Glavna metrika: **F1 klase "refuse"** (unanswerable_plausible + out_of_scope zajedno).
- Plus: precision/recall refuse, **false refusal rate** na answerable, macro-F1 answer/refuse, AUROC i **risk–coverage kriva** (koliko je odgovora tačno kad sistem odgovara na X% pitanja), tačnost odgovora (token F1 / exact match prema gold spanu).
- Sve **po jeziku (BS vs EN)** i po klasi (plausible vs out_of_scope odvojeno — plausible je teži).
- Confusion matrice za sve sisteme.
- Statistika: bootstrap 95% CI za F1 razlike između B1, B2 i M (test set je mali).
- **Analiza grešaka (min 10, cilj 20):** `results/errors.csv` s kategorijama: retrieval promašio pasus / leksičko preklapanje zavarava model / odgovor zahtijeva zaključivanje / greška u gold labeli / dijakritici ili sleng / prevod. Svaka greška: uzrok, ne simptom (isto pravilo kao u Labu 1).
- Figure u `results/figures/`: raspodjela podataka (≥2 tabele/grafika za M3), poređenje sistema, risk–coverage, BS vs EN.

## 8. Struktura repoa (ciljna)

```
talking-exhibits/
├── HANDOFF.md              # ovaj fajl
├── CLAUDE.md               # kratka uputa za Claude Code → pokazuje na HANDOFF.md
├── README.md               # instalacija, pokretanje, dijagram (naše vs eksterno)
├── CONTRIBUTIONS.md
├── docs/
│   ├── AI_LOG.md
│   └── annotation_guidelines.md
├── data/
│   ├── exhibits/           # tekstovi izložaka (ili upute)
│   ├── questions/          # questions.csv
│   └── processed/          # generisano, nije u gitu
├── src/talking_exhibits/
│   ├── data.py             # učitavanje i validacija (provjera kolona, kao collect.py u labu)
│   ├── preprocess.py       # normalizacija, chunking (dijakritike se ČUVAJU)
│   ├── retrieval.py        # BM25 i e5
│   ├── answerability.py    # klasifikator: trening i inferenca
│   ├── llm_baseline.py
│   ├── evaluate.py         # metrike, CI, confusion, figure
│   └── demo/               # web app + QR
├── scripts/
│   ├── build_dataset.py    # split po izlošku, fiksni seed
│   ├── train_classifier.py
│   ├── run_baselines.py
│   └── evaluate_all.py     # jedna komanda → svi brojevi u paperu
├── notebooks/              # Colab za trening
├── results/                # metrics.json, errors.csv, figures/
├── tests/                  # pytest: učitavanje podataka, chunking, metrike
├── pyproject.toml          # uv, Python 3.12
└── uv.lock
```

Konvencije: `uv run ...` za sve komande (kao u labu), seed `3004` svuda, svaki skript štampa šta radi i gdje snima, nijedan broj u paperu koji ne izlazi iz `scripts/evaluate_all.py`.

## 9. Plan rada

| Sedmica | Datum | Cilj | Vlasnik |
| --- | --- | --- | --- |
| 4 | do 1.11. | Odluka o izlošcima; `annotation_guidelines.md`; skeleton koda (`data.py`, `preprocess.py`), pytest | Tarik (izlošci), Mirza (kod), Kerim (guidelines) |
| 5 | do 8.11. | Tekstovi izložaka BS+EN; prvih ~150 pitanja; BM25 retrieval | Svi pišu pitanja; Tarik izlošci; Mirza retrieval |
| 6 | do 15.11. | 300 pitanja + cross-check + kappa; split po izlošku; **B1 s prvim rezultatima**; 2 tabele/grafika | Tarik podaci; Kerim evaluate.py; Mirza B1 |
| 7 | do **22.11.** | **M3:** README pokretanje, nacrt dijagrama, CONTRIBUTIONS/AI_LOG; paper: Introduction, Literature Review (≥8 izvora, 5 direktno), Dataset | Svi; paper sekcije po podjeli |
| 8 | lab | M3 check-in (~5 min): podaci, baseline, plan za glavnu metodu; **svako objašnjava svoj dio** | Svi |
| 9–10 | | Fine-tuning klasifikatora (Colab); B2 LLM baseline; e5 retrieval | Mirza M; Kerim B2 |
| 11 | | Ablacije (M-zs, opcionalno BERTić); kalibracija praga; finalna evaluacija na testu | Mirza, Kerim |
| 12 | | Analiza grešaka (20); figure; demo s QR kodovima | Kerim (greške, demo), Tarik (greške) |
| 13 | | Paper: Methodology, Results, Discussion, Conclusion, Contributions, AI Disclosure; slajdovi | Svi |
| 14+ | | Probna prezentacija; svako prođe **cijeli** kod i rezultate; predaja prije ispitnog roka | Svi |

Feedback s M3 check-ina **mora** biti obrađen u finalnoj predaji — upisati ga u sekciju 13 ovog fajla.

## 10. Paper (Google Docs, 02 Paper)

- Sekcije (obavezne): Abstract, Introduction, Literature Review, Dataset, Methodology, Results, Discussion and Limitations, Conclusion, Author Contributions, AI Tools Disclosure, References.
- Max 20 strana bez referenci i priloga. Citation manager: **Zotero** ili Paperpile, jedan stil (IEEE preporuka).
- Citirati **sve**: datasetove, modele, biblioteke, figure, eksterni kod.
- Naš rad jasno odvojen od tuđeg.
- Šablon i primjer papera su u Lab 01 dokumentu (IBU naslovna strana: Faculty of Engineering, Natural and Medical Sciences, Department of Information Technology; Supervisor Prof. Dr. Dželila Mehanović).

**Kandidati za literaturu (svaki izvor OTVORITI i provjeriti prije citiranja — izmišljene reference su zabranjene):**

| Izvor | Zašto |
| --- | --- |
| Rajpurkar, Jia, Liang (2018). Know What You Don't Know: Unanswerable Questions for SQuAD. ACL. arXiv:1806.03822 | Direktno: unanswerable QA, naš trening set |
| Ljubešić, Lauc (2021). BERTić – The Transformer Language Model for Bosnian, Croatian, Montenegrin and Serbian. BSNLP. | BCMS model, ablacija |
| Conneau et al. (2020). Unsupervised Cross-lingual Representation Learning at Scale (XLM-R). ACL | Naš bazni model |
| Wang et al. (2024). Multilingual E5 Text Embeddings: A Technical Report. arXiv | Dense retrieval |
| Lewis et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. NeurIPS | RAG okvir |
| Karpukhin et al. (2020). Dense Passage Retrieval for Open-Domain QA. EMNLP | Dense vs BM25 |
| Robertson, Zaragoza (2009). The Probabilistic Relevance Framework: BM25 and Beyond | Baseline 1 |
| Kamath, Jia, Liang (2020). Selective Question Answering under Domain Shift. ACL | Direktno: odbijanje / abstention |
| Ji et al. (2023). Survey of Hallucination in Natural Language Generation. ACM Computing Surveys | Motivacija |
| Rađenović et al. (2026). Development of Serbian QA Datasets through Prompt-Based Generation and Human Validation. LREC 2026 | Regionalni QA resursi |
| Jurafsky & Martin, Speech and Language Processing, 3rd ed. (QA i RAG poglavlja) | Obavezna literatura kursa |

Za pretragu koristiti Google Scholar, ACL Anthology, Semantic Scholar. Tražiti još radova o: answerability detection, abstention u LLM-ovima, museum/cultural heritage chatbots, QA za low-resource južnoslavenske jezike.

## 11. Prezentacija i odbrana

- 10–15 min: problem i motivacija, RQ, dataset, preprocessing, baseline i glavna metoda, workflow, evaluacija, ključni rezultati, primjeri izlaza i grešaka, ograničenja, zaključak, **kratki demo** (skeniranje QR koda uživo).
- **Svako prezentira dio.** Prisustvo na prezentacijama drugih timova je obavezno.
- Individualna pitanja su o **cijelom** projektu, bez AI-a i bez pomoći: pokreni dio koda, objasni segment, interpretiraj rezultat, opravdaj odluku, objasni grešku modela.
- Priprema: prije predaje svako prođe svaki fajl u `src/` i `scripts/` i zna odgovoriti: zašto cross-encoder a ne bi-encoder, zašto split po izlošku, zašto prag na val a ne na test, šta je AUROC, zašto e5 treba prefikse, kako je napravljen test set, koja je najčešća greška i zašto.

## 12. Pravila za Claude (i druge AI asistente)

1. **Prvo pročitaj** ovaj fajl, README, CONTRIBUTIONS i AI_LOG. Ne pitaj ono što piše ovdje.
2. **Razgovaraj na bosanskom** (ijekavica), direktno i kratko. Kod, komentari, commit poruke, README i paper su na **engleskom**.
3. **Ne piši u `docs/AI_LOG.md` ni `CONTRIBUTIONS.md`.** Te fajlove pišu studenti. Na kraju zadatka podsjeti člana i navedi činjenice za unos (datum, šta je traženo, koji fajlovi). Neprijavljena AI upotreba je kršenje akademskog integriteta. Detalji su u `TEAM_PLAN.md` §1.
4. **Nikad ne izmišljaj** rezultate, brojeve, eksperimente, datasetove ni reference. Svaki broj mora izaći iz pokrenutog koda. Svaka referenca mora biti otvorena i provjerena.
5. **Studenti moraju razumjeti sve.** Piši jednostavan, komentarisan kod u stilu lab repoa (jedna funkcija = jedan korak, DataFrame kroz pipeline). Nakon većeg komada koda objasni ga u 3–5 rečenica i predloži 2 pitanja koja bi profesorica mogla postaviti o njemu.
6. **Nikad ne commituj, ne stage-aj i ne pushaj.** Svaki član commita svoj rad sa svog naloga. Ti predložiš commit poruku i komande, a član ih pokrene sam. Prije rada pitaj i objasni, a poslije svakog zadatka upiši bilješke za učenje u `study/<član>/` (vidi `TEAM_PLAN.md` §1.3–1.4).
7. **Ne diraj test set** dok konfiguracija nije zaključana. Podešavanje samo na val.
8. Seed `3004`, `uv run` za sve, novi paketi idu u `pyproject.toml`.
9. Mala, provjerljiva koraka: napiši → pokreni → pokaži output → commit. Testovi u `tests/` za podatke, chunking i metrike.
10. **Ne ubacuj** privatne podatke (imena, mailove, studentske podatke) u podatke ni repo.
11. NLP komponenta je prioritet. Demo/UI je sporedan i radi se tek kad glavna metoda radi.
12. Kad odluka nije jasna i skupa je za vraćanje (npr. promjena glavne metode, novi dataset), pitaj tim. Kad je jeftina, odluči, napiši šta si odlučio i nastavi.

## 13. Otvorena pitanja i dnevnik odluka

| Datum | Odluka / pitanje | Status |
| --- | --- | --- |
| 08.10.2026 | Izabrana tema #1 Talking exhibits | ✅ |
| 25.10.2026 | Glavna metoda = fine-tunovani answerability klasifikator (zbog pravila o "team-built" komponenti) | ✅ |
| 25.10.2026 | Koji izlošci (IBU kampus vs muzej)? | ❓ otvoreno |
| 25.10.2026 | Dozvola IBU-a za objavu tekstova izložaka | ❓ pitati |
| 25.10.2026 | Uključujemo li kolege van tima za pitanja? Ako da → odobrenje profesorice prije prikupljanja | ❓ |
| 25.10.2026 | LLM za B2: lokalno (Ollama) ili API? | ❓ |
| | Feedback s M3 check-ina | ⏳ |

## 14. Alati i skillovi koje imamo (Claude + ostalo)

Koristi ono što ubrzava rad, ali sve upisati u AI_LOG.

**Kodiranje (Claude Code / agentni rad)**
- **Claude Code** nad repoom za pisanje i pokretanje koda, testova i skripti. `CLAUDE.md` u rootu ga upućuje na ovaj fajl.
- **Plan mode** (i Plan agent) prije većih komada: trening skripta, evaluate_all, demo.
- **Explore agent** za pretragu po većem repou; **general-purpose agent** za višekoračne zadatke.
- **Graphify** (Mirza ima nalog) za graf koda kad repo naraste — korisno za učenje prije odbrane.
- Google Colab / Kaggle za GPU trening.

**Razmišljanje i istraživanje**
- **Extended thinking** za dizajn eksperimenta, analizu grešaka i interpretaciju rezultata.
- **deep-research** skill za Literature Review (pa svaki izvor ručno provjeriti i ubaciti u Zotero).
- Web search za modele, licence, verzije paketa.

**Memorija i kontinuitet**
- **Claude memory** (claude.ai) pamti projekat između razgovora; ovaj HANDOFF je ipak glavni izvor.
- **Obsidian** (Mirza) za lične bilješke i pripremu za odbranu (pitanja i odgovori po fajlu koda).
- `docs/` u repou za sve što tim treba vidjeti.

**Pisanje (paper i dokumenti)**
- **google-workspace** skill / Google Drive konektor za 02 Paper (mora ostati u Google Docsu zbog revision historije).
- **docs** skill za brze nacrte prije prebacivanja u Google Doc.

**Grafike, demo i dizajn**
- **dataviz** skill za grafike u paperu i slajdovima (risk–coverage, confusion, BS vs EN).
- **frontend-design** skill za demo web stranicu po izlošku.
- **artifact-design** za interaktivni prikaz rezultata ako zatreba.
- **Figma** konektor (wireframe demoa, opcionalno), **Canva** / **Adobe Express** za vizuale slajdova.
- **pptx** skill ili Google Slides (03 Presentation) za prezentaciju.

**Ostalo**
- **skill-creator**: možemo napraviti projektni skill (npr. "dodaj pitanja po guidelines i validiraj CSV" ili "pokreni evaluaciju i ažuriraj tabele").
- Whisper (opcionalno) za glasovni unos u demou.

---

*Zadnje ažuriranje: 25.10.2026 (nakon M2). Napisao: Claude na zahtjev Mirze Čakala; tim provjerava i dopunjava.*
