# Question review for M3

Kerim Hodžić (`kerim279`) is the author of `q0001`–`q0100`. Tarik Hadrović is the author of `q0101`–`q0200`. Both blocks are in `data/questions/questions.csv` after merge commit `af3effc`. The merged draft has 200 unique IDs, 93 exact answer spans with valid offsets, and 107 unanswerable items with empty answer fields. The validator found zero normalized exact duplicates. All split fields are unassigned.

## Kerim edits

| QID | Issue | Applied correction |
| --- | --- | --- |
| q0017 | The question assumes the activity takes place abroad. | Ask what international study opportunity the department encourages. |
| q0027 | Translation and editing are described as possible careers. | Ask which study area lists them as possible career paths. |
| q0052 | The wording asks for a nominative department name while the exact span is genitive. | Ask which department's studio serves as the podcast base. |
| q0066 | The question requests one name and the span gives two. | Ask for both names. |
| q0073 | The question presupposes one recording. The exhibit mentions multiple recordings. | Ask for the title of an archival recording and preserve `unanswerable_plausible`. |
| q0075 | Near duplicate of the passport renewal question q0200. | Ask about solving a quadratic equation and preserve `out_of_scope`. |
| q0092 | The question asks where the link leads and repeats the purpose given in the answer. | Ask what each undergraduate programme entry links to. |
| q0093 | “Covered” implies funding. | Ask what the separate admissions link lists. |

## Recommendations for Tarik

The ten edits below are pending Tarik's approval. The CSV currently contains his submitted wording and spans.

| QID | Issue | Suggested correction |
| --- | --- | --- |
| q0116 | The department-specific schedule caveat occurs in the paragraph about winter midterms. The question asks about finals. | Ask `Kada počinju zimski midterm ispiti na Odsjeku za informacione tehnologije?` and keep `unanswerable_plausible`. |
| q0119 | “The semester” could refer to fall or spring. | Specify the first day of fall classes for the first study cycle. Keep `unanswerable_plausible`. |
| q0131 | “Koliko ECTS bodova ima studij” can ask for a total. The span gives a breakdown. | Ask `Kako su ECTS bodovi raspoređeni po ciklusima na Fakultetu obrazovanja?` to retain the span. |
| q0134 | The answer omits the requirement that certificates be valid. | Use `valid TOEFL or IELTS certificates` at Unicode offset `2038`. |
| q0151 | “Klub” could refer to the merged club or its historical predecessor. | Ask `Kada je osnovan Omladinski košarkaški klub Ilidža?` to retain the date span. |
| q0152 | The founding name can be misread as the founding name of the merged club. | Ask `Pod kojim je imenom 1970. osnovan klub koji je 1972. preimenovan u KK Igman?` |
| q0158 | The count is tied to a stated period. | Ask `How many times from 1972 to 1975 were the club's juniors champions of Bosnia and Herzegovina?` |
| q0181 | The question asks for a count of clubs alone. The number covers three categories. | Ask `U koliko se klubova, udruženja i događaja studenti mogu uključiti prema stranici Explore?` |
| q0185 | The answer includes confidence as well as skills. | Ask `What do clubs help students build in addition to friendships?` to retain the span. |
| q0190 | The club is unspecified. | Name a listed club, for example `Koliko košta članarina u klubu SpeakUp?` Keep `unanswerable_plausible`. |

The similar pairs `q0104/q0114`, `q0129/q0141` and `q0139/q0140` request different attributes. The pair `q0133/q0143` contrasts a stated period with an absent exact date. These items can be retained.

## Human verification

Kerim's 100 rows have empty `source` and `checked_by` fields. Tarik records `llm_checked` on his 100 rows and his author review is documented in the history of PR #7. His independent reviewer fields are empty. The validator reports 100 missing `source` values and 200 missing `checked_by` values across the combined snapshot. This technical review does not populate either field.

Mirza confirmed the M3 review assignments on 22 November 2026. Mirza reviews Kerim's `q0001`–`q0100`. Kerim reviews Tarik's `q0101`–`q0200`. Tarik reviews Mirza's questions once available.

- Kerim verifies each of his own AI-assisted drafts against the assigned exhibit and language. Enter `source=llm_checked` only for the exact wording, label and span he has personally checked. Use `human` only for independently human-written questions.
- Kerim independently reviews each of Tarik's questions and confirms, revises or rejects the proposed changes above. Coordinate changes to Tarik's rows with Tarik. Enter `checked_by=kerim` only for rows Kerim has actually reviewed in their accepted form. Mirza enters `checked_by=mirza` for Kerim's rows after his own review.
