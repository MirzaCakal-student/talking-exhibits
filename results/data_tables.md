# Preliminary dataset analysis

These statistics describe the supplied question drafts and exhibit texts. They are not final M3 dataset statistics or model performance results.

Input questions: `data/questions/questions.csv`

Input exhibit directory: `data/exhibits`

Questions: **100**; distinct question exhibits: **4**; exhibit texts: **4** with **8 language versions**.

## Review status

Rows with a recorded valid source value: **0/100**.

Rows with an independent reviewer recorded: **0/100**.

Recorded metadata counts do not replace validation of labels and answer spans.

## Question class × language

| question_class | bs | en | total |
| --- | --- | --- | --- |
| answerable | 22 | 23 | 45 |
| unanswerable_plausible | 20 | 20 | 40 |
| out_of_scope | 8 | 7 | 15 |
| total | 50 | 50 | 100 |

## Questions per exhibit

| exhibit_id | bs | en | total |
| --- | --- | --- | --- |
| ibu_about_programs | 12 | 13 | 25 |
| ibu_feh | 12 | 13 | 25 |
| ibu_fess | 13 | 12 | 25 |
| ibu_podcast_media | 13 | 12 | 25 |

## Question contributors

| author | questions |
| --- | --- |
| kerim | 100 |

## Split status

All **100** split values are unassigned. No split distribution is reported.

## Lengths

| group | n | mean | median | sample_sd | min | max |
| --- | --- | --- | --- | --- | --- | --- |
| questions_all | 100 | 9.11 | 9.0 | 2.02 | 4 | 14 |
| questions_bs | 50 | 8.32 | 8.0 | 1.96 | 4 | 14 |
| questions_en | 50 | 9.9 | 9.5 | 1.78 | 7 | 14 |
| exhibit_versions_all | 8 | 353.88 | 355.5 | 23.52 | 316 | 385 |
| exhibit_versions_bs | 4 | 337.5 | 338.0 | 19.36 | 316 | 358 |
| exhibit_versions_en | 4 | 370.25 | 371.5 | 14.17 | 353 | 385 |

Lengths count whitespace-separated words. SD uses n − 1; N/A denotes an undefined statistic.

## Exhibit text lengths

| exhibit_id | lang | words |
| --- | --- | --- |
| ibu_about_programs | bs | 327 |
| ibu_about_programs | en | 353 |
| ibu_feh | bs | 349 |
| ibu_feh | en | 365 |
| ibu_fess | bs | 358 |
| ibu_fess | en | 385 |
| ibu_podcast_media | bs | 316 |
| ibu_podcast_media | en | 378 |

## Question–exhibit lexical overlap

| label | questions | mean_jaccard | median_jaccard | min_jaccard | max_jaccard |
| --- | --- | --- | --- | --- | --- |
| answerable | 45 | 0.0303 | 0.0338 | 0.0084 | 0.0524 |
| unanswerable_plausible | 40 | 0.0232 | 0.0242 | 0.0041 | 0.0515 |
| out_of_scope | 15 | 0.0073 | 0.0052 | 0.0 | 0.015 |

Jaccard uses unique lowercase word tokens from the selected exhibit text in the same language. Tokens match Unicode `\w+`; diacritics are retained, without stemming or stopword removal. Similarity is the size of the token intersection divided by the token union, or zero for an empty union.

Mean Jaccard: answerable **0.0303**, plausible **0.0232**, out of scope **0.0073**.

A plausible question can share topic words with the text while requesting an unstated fact. Jaccard measures lexical overlap, not answerability or BM25 performance. These descriptive results do not establish that a retrieval threshold succeeds or fails.

## Bosnian diacritics

Bosnian questions without any č/ć/đ/š/ž character: **28/50 (56.0%)**.

This is **not** a reliable count of deliberately omitted diacritics: many correctly written questions naturally contain none.

Documented intentional omissions supplied from the authoring record: **10/50 (20.0%)**.

Declared qids: `q0003`, `q0009`, `q0011`, `q0028`, `q0032`, `q0054`, `q0059`, `q0061`, `q0079`, `q0083`.

Other diacritic-free Bosnian questions: **18**. Character absence alone does not establish their writing intent.

The declared qids are authoring annotations, not independent human review approvals.

## Reproduce

Run from the repository root:

```bash
uv run --frozen python scripts/data_analysis.py --questions data/questions/questions.csv --exhibits data/exhibits --out results --preliminary --intentional-no-diacritics q0003 q0009 q0011 q0028 q0032 q0054 q0059 q0061 q0079 q0083
```

## Figures

- `figures/questions_by_label_language.png`

- `figures/question_lengths.png`

- `figures/exhibit_lengths.png`

These are descriptive statistics, not model performance results.
