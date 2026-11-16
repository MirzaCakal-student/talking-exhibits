# Exhibits

The knowledge base of the project: 12 short texts about International Burch University (IBU).
Each exhibit is what a visitor would read next to a QR code on campus. The system answers
questions **only from the text of that one exhibit** and refuses when the text has no answer.

Decided by the team on 16.11.2026. Sources were read in November 2026 on the **current**
IBU website (`www.ibu.edu.ba`); the old site (`old.ibu.edu.ba`) is not used.

## Exhibit list

| id | Title | Sources | Writer | Status |
| --- | --- | --- | --- | --- |
| `ibu_academic_calendar` | Academic Calendar 2026/2027 | [Academic Calendar 26/27 (PDF)](https://ibu-website.fra1.digitaloceanspaces.com/Academic_Calendar_for_2026_2027_docx_2_d2e509fce1.pdf) | Tarik | ☐ |
| `ibu_visitor_faq` | Information for Visitors and New Students | [FAQ](https://www.ibu.edu.ba/faq) | Tarik | ☐ |
| `ibu_kk_igman_burch` | Basketball Club KK Igman Burch | [KK Igman Burch](https://www.ibu.edu.ba/explore/kk-igman-burch) | Tarik | ☐ |
| `ibu_student_life` | Student Life, Clubs, Library and Digital Services | [Explore](https://www.ibu.edu.ba/explore), [Clubs](https://www.ibu.edu.ba/explore/clubs), [Club Day 2026](https://www.ibu.edu.ba/in-focus/ibu-club-day-2026), [Student area](https://www.ibu.edu.ba/student-area), [Library news](https://www.ibu.edu.ba/in-focus/a-new-chapter-for-the-ibu-library) | Tarik | ☐ |
| `ibu_fenms` | Faculty of Engineering, Natural and Medical Sciences | [Faculty page](https://www.ibu.edu.ba/faculty-of-engineering-natural-and-medical-sciences), [Tuition and fees](https://www.ibu.edu.ba/tuition-and-fees) | Mirza | ☐ |
| `ibu_projects` | Research and EU Projects | [Projects](https://www.ibu.edu.ba/explore/projects) | Mirza | ☐ |
| `ibu_erasmus` | Erasmus+ Exchange at IBU | [Erasmus+](https://www.ibu.edu.ba/explore/erasmus) | Mirza | ☐ |
| `ibu_accreditation` | Accreditation and Quality Assurance | [Accreditation](https://www.ibu.edu.ba/about/accreditation), [Quality Assurance Office](https://www.ibu.edu.ba/offices/office-for-standardization-and-quality-assurance) | Mirza | ☐ |
| `ibu_fess` | Faculty of Economics and Social Sciences | [Faculty page](https://www.ibu.edu.ba/faculty-of-economics-and-social-sciences), [Tuition and fees](https://www.ibu.edu.ba/tuition-and-fees) | Kerim | ☐ |
| `ibu_feh` | Faculty of Education and Humanities | [Faculty page](https://www.ibu.edu.ba/faculty-of-education-and-humanities), [Tuition and fees](https://www.ibu.edu.ba/tuition-and-fees) | Kerim | ☐ |
| `ibu_podcast_media` | IBU Podcast and Media Activities | [IBU Podcast](https://www.ibu.edu.ba/podcast), [BH Radio 1 visit](https://www.ibu.edu.ba/in-focus/ibu-radiobh1) | Kerim | ☐ |
| `ibu_about_programs` | About IBU and Study Programs | [About](https://www.ibu.edu.ba/about), [Admission](https://www.ibu.edu.ba/admission) | Kerim | ☐ |

Deadline for all texts (BS + EN): **17.11.2026**. When an exhibit is done, change ☐ to ☑.

## File format

One JSON file per exhibit **and language**: `data/exhibits/<id>_<lang>.json`, for example
`ibu_visitor_faq_bs.json` and `ibu_visitor_faq_en.json`. Both versions use the **same `id`**.

```json
{
  "id": "ibu_visitor_faq",
  "title": "Information for Visitors and New Students",
  "lang": "en",
  "text": "...",
  "sources": ["https://www.ibu.edu.ba/faq"]
}
```

- `lang` is `bs` or `en`.
- `title` and `text` must not be empty, and `sources` must have at least one URL;
  otherwise `talking_exhibits.data.load_exhibits` raises an error.
- Save the file as UTF-8 so that č, ć, š, ž, đ are kept.

## Writing rules

1. **300–800 words** per text, in **your own words** (no copy-paste from the website).
2. Write both versions: Bosnian (`bs`) and English (`en`) with the same facts.
3. Use only the sources in the table. If two sources disagree (e.g. the home page says
   15+ student clubs and the Explore page says 30+), write the newer value or leave the fact out.
4. **No private data:** no names of students or staff, no e-mails, no phone numbers.
5. Leave some facts that a visitor would expect **out of the text** (a price, a name, an exact
   number). These become good `unanswerable_plausible` questions later.
6. Write dates and numbers the way they appear in the language of the text
   (e.g. `20.000` in BS, `20,000` in EN), because answer spans are checked character by character.

## Known risks and backups

- `ibu_projects`: the projects page lists 17 project titles; detail pages were not checked.
  If they have no details, replace it with the backup topic below.
- `ibu_fess`, `ibu_feh`: the faculty pages have few numbers; use the tuition page and the
  program names to reach enough facts. If both stay too thin, merge them into one exhibit
  (11 exhibits in total is still within the plan of 10–12).
- The academic calendar is valid for 2026/2027 only; say so in the text.

**Backup topic:** `ibu_laws_regulations`, Laws and Regulations,
[source](https://www.ibu.edu.ba/laws-and-regulations).

A topic can be replaced only until **17.11.2026**. After that, questions are written on the
exhibits and a replacement would also mean new questions. Every replacement is recorded in
this file.
