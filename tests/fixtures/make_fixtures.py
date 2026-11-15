"""Generate the fictional test fixtures (exhibits + questions).

Run:  uv run python tests/fixtures/make_fixtures.py

Everything here is made up ("Univerzitet Lipa" in the town of Brezovac does
not exist). The files only let the tests and scripts run before the real
dataset is ready. Do not edit the generated files by hand: change this script.
"""

import csv
import json
from pathlib import Path

HERE = Path(__file__).parent

EXHIBITS = [
    {
        "id": "lipa_library",
        "lang": "bs",
        "title": "Biblioteka Univerziteta Lipa",
        "text": (
            "Biblioteka Univerziteta Lipa otvorena je 2009. godine u prizemlju glavne zgrade. "
            "Danas zauzima dva sprata i ima čitaonicu sa 180 mjesta. "
            "Fond biblioteke broji oko 42.000 knjiga i više od 300 naslova časopisa. "
            "Najveći dio fonda čine udžbenici iz inženjerstva, ekonomije i stranih jezika. "
            "Studenti mogu posuditi do pet knjiga na period od dvije sedmice. "
            "Posudba se produžava putem interneta ili na pultu. "
            "Biblioteka je radnim danima otvorena od 8 do 22 sata, a subotom od 9 do 15 sati. "
            "U ispitnim rokovima čitaonica radi i nedjeljom. "
            "Na drugom spratu nalaze se četiri sobe za grupni rad, koje se rezervišu dan unaprijed. "
            "Svaka soba ima ploču i ekran za prezentacije. "
            "Posebna zbirka čuva stare rukopise i mape grada Brezovca iz devetnaestog vijeka. "
            "Zbirku je univerzitetu poklonila porodica Šarić. "
            "Rukopisi se ne iznose iz zgrade, ali su digitalizovani i dostupni na računarima u čitaonici. "
            "Biblioteka svake jeseni organizuje sedmicu otvorenih vrata za učenike srednjih škola."
        ),
    },
    {
        "id": "lipa_library",
        "lang": "en",
        "title": "Lipa University Library",
        "text": (
            "The Lipa University Library opened in 2009 on the ground floor of the main building. "
            "Today it covers two floors and has a reading room with 180 seats. "
            "The collection holds about 42,000 books and more than 300 journal titles. "
            "Most of the collection consists of textbooks in engineering, economics and foreign languages. "
            "Students may borrow up to five books for a period of two weeks. "
            "Loans are renewed online or at the front desk. "
            "The library is open on weekdays from 8 to 22 and on Saturdays from 9 to 15. "
            "During exam periods the reading room is also open on Sundays. "
            "On the second floor there are four group study rooms, which are booked one day in advance. "
            "Each room has a whiteboard and a screen for presentations. "
            "A special collection keeps old manuscripts and maps of the town of Brezovac from the nineteenth century. "
            "The collection was donated to the university by the Šarić family. "
            "The manuscripts never leave the building, but they have been digitised and are available on the computers in the reading room. "
            "Every autumn the library organises an open week for secondary school pupils."
        ),
    },
    {
        "id": "lipa_solar_car",
        "lang": "bs",
        "title": "Solarni automobil Lipa One",
        "text": (
            "Lipa One je solarni automobil koji su napravili studenti mašinstva i elektrotehnike. "
            "Rad na projektu počeo je u oktobru 2021. godine, a vozilo je prvi put predstavljeno u junu 2023. "
            "Tim je brojao dvadeset i šest studenata sa tri fakulteta. "
            "Automobil je težak 310 kilograma i ima mjesta samo za vozača. "
            "Karoserija je izrađena od karbonskih vlakana, što je čini laganom i čvrstom. "
            "Na krovu se nalazi šest kvadratnih metara solarnih ćelija. "
            "Baterija omogućava vožnju od oko 400 kilometara bez sunca. "
            "Najveća brzina vozila je 110 kilometara na sat. "
            "Motor je smješten u zadnjem točku, pa nema klasičnog mjenjača. "
            "Vozilo je 2024. godine učestvovalo na evropskoj trci solarnih automobila u Belgiji. "
            "Tim je zauzeo sedmo mjesto u svojoj klasi. "
            "Tokom trke pokvario se senzor temperature baterije, pa je tim izgubio dva sata na popravku. "
            "Danas je automobil izložen u holu Tehničkog fakulteta. "
            "Nova generacija studenata radi na modelu sa dva sjedišta."
        ),
    },
    {
        "id": "lipa_solar_car",
        "lang": "en",
        "title": "The Lipa One Solar Car",
        "text": (
            "Lipa One is a solar car built by students of mechanical and electrical engineering. "
            "Work on the project began in October 2021, and the vehicle was first presented in June 2023. "
            "The team had twenty-six students from three faculties. "
            "The car weighs 310 kilograms and has room only for the driver. "
            "The body is made of carbon fibre, which makes it light and strong. "
            "Six square metres of solar cells are placed on the roof. "
            "The battery allows a drive of about 400 kilometres without sun. "
            "The top speed of the vehicle is 110 kilometres per hour. "
            "The motor sits in the rear wheel, so there is no classic gearbox. "
            "In 2024 the vehicle took part in the European solar car race in Belgium. "
            "The team finished seventh in its class. "
            "During the race the battery temperature sensor failed, and the team lost two hours on the repair. "
            "Today the car is displayed in the hall of the Faculty of Engineering. "
            "A new generation of students is working on a model with two seats."
        ),
    },
]

# (exhibit_id, lang, question, label, answer_text)
QUESTIONS = [
    ("lipa_library", "bs", "Koliko mjesta ima čitaonica?", "answerable", "180 mjesta"),
    ("lipa_library", "bs", "Koliko knjiga student moze posuditi?", "answerable", "do pet knjiga"),
    ("lipa_library", "bs", "Ko je poklonio posebnu zbirku?", "answerable", "porodica Šarić"),
    ("lipa_library", "bs", "Koliko košta članarina u biblioteci?", "unanswerable_plausible", ""),
    ("lipa_library", "bs", "Ko je direktor biblioteke?", "unanswerable_plausible", ""),
    ("lipa_library", "bs", "Koji je glavni grad Japana?", "out_of_scope", ""),
    ("lipa_library", "en", "When did the library open?", "answerable", "2009"),
    ("lipa_library", "en", "How many group study rooms are there?", "answerable", "four group study rooms"),
    ("lipa_library", "en", "How many librarians work in the library?", "unanswerable_plausible", ""),
    ("lipa_library", "en", "Who designed the library building?", "unanswerable_plausible", ""),
    ("lipa_library", "en", "How do I bake sourdough bread?", "out_of_scope", ""),
    ("lipa_solar_car", "bs", "Koliko je težak automobil?", "answerable", "310 kilograma"),
    ("lipa_solar_car", "bs", "Koja je najveca brzina vozila?", "answerable", "110 kilometara na sat"),
    ("lipa_solar_car", "bs", "Koje mjesto je tim zauzeo na trci?", "answerable", "sedmo mjesto"),
    ("lipa_solar_car", "bs", "Koliko je koštala izrada automobila?", "unanswerable_plausible", ""),
    ("lipa_solar_car", "bs", "Ko je bio vozač na trci u Belgiji?", "unanswerable_plausible", ""),
    ("lipa_solar_car", "bs", "Kada je sljedeći rok za prijavu ispita?", "out_of_scope", ""),
    ("lipa_solar_car", "en", "What is the body of the car made of?", "answerable", "carbon fibre"),
    ("lipa_solar_car", "en", "How far can the car drive without sun?", "answerable", "about 400 kilometres"),
    ("lipa_solar_car", "en", "Who sponsored the solar car project?", "unanswerable_plausible", ""),
    ("lipa_solar_car", "en", "How long does the battery take to charge?", "unanswerable_plausible", ""),
    ("lipa_solar_car", "en", "What is the best pizza place in town?", "out_of_scope", ""),
]

COLUMNS = [
    "qid", "exhibit_id", "lang", "question", "label", "answer_text",
    "answer_start", "author", "checked_by", "source", "split",
]


def main():
    exhibits_dir = HERE / "exhibits"
    exhibits_dir.mkdir(exist_ok=True)
    texts = {}
    for exhibit in EXHIBITS:
        record = dict(exhibit, sources=["https://example.org/fictional-fixture"])
        path = exhibits_dir / f"{exhibit['id']}_{exhibit['lang']}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
        texts[(exhibit["id"], exhibit["lang"])] = exhibit["text"]
        print(f"wrote {path.name} ({len(exhibit['text'].split())} words)")

    questions_path = HERE / "questions_val.csv"
    with open(questions_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(COLUMNS)
        for i, (exhibit_id, lang, question, label, answer) in enumerate(QUESTIONS, start=1):
            # The offset is computed, never typed by hand.
            start = texts[(exhibit_id, lang)].index(answer) if answer else ""
            # author/checked_by use team names only because the validator
            # (scripts/validate_questions.py) accepts nothing else; nobody
            # on the team wrote these fictional questions.
            writer.writerow(
                [f"q{i:04d}", exhibit_id, lang, question, label, answer, start,
                 "mirza", "tarik", "human", "val"]
            )
    print(f"wrote {questions_path.name} ({len(QUESTIONS)} questions)")


if __name__ == "__main__":
    main()
