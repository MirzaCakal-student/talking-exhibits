# Preliminary dataset analysis

These statistics describe the available preliminary drafts. Question review and exhibit-level splits are pending. Model performance is reported separately after validation.

Input questions: Kerim's `data/questions/questions.csv` (q0001–q0100) and Tarik's snapshot at `e2cf0ad:data/questions/questions.csv` (q0101–q0200).

Input exhibit directory: `data/exhibits`

Questions: **200**; distinct question exhibits: **8**; exhibit texts: **8** with **16 language versions**.

## Review status

Rows with a recorded valid source value: **100/200**.

Rows with an independent reviewer recorded: **0/200**.

Recorded metadata counts do not replace validation of labels and answer spans.

## Question class × language

| question_class | bs | en | total |
| --- | --- | --- | --- |
| answerable | 46 | 47 | 93 |
| unanswerable_plausible | 40 | 36 | 76 |
| out_of_scope | 16 | 15 | 31 |
| total | 102 | 98 | 200 |

## Questions per exhibit

| exhibit_id | bs | en | total |
| --- | --- | --- | --- |
| ibu_about_programs | 12 | 13 | 25 |
| ibu_academic_calendar | 13 | 12 | 25 |
| ibu_feh | 12 | 13 | 25 |
| ibu_fess | 13 | 12 | 25 |
| ibu_kk_igman_burch | 13 | 12 | 25 |
| ibu_podcast_media | 13 | 12 | 25 |
| ibu_student_life | 13 | 12 | 25 |
| ibu_visitor_faq | 13 | 12 | 25 |

## Question contributors

| author | questions |
| --- | --- |
| kerim | 100 |
| tarik | 100 |

## Split status

All **200** split values are unassigned. No split distribution is reported.

## Lengths

| group | n | mean | median | sample_sd | min | max |
| --- | --- | --- | --- | --- | --- | --- |
| questions_all | 200 | 8.2 | 8.0 | 2.31 | 4 | 15 |
| questions_bs | 102 | 7.43 | 7.0 | 2.2 | 4 | 14 |
| questions_en | 98 | 8.99 | 9.0 | 2.15 | 4 | 15 |
| exhibit_versions_all | 16 | 386.31 | 371.5 | 54.59 | 316 | 504 |
| exhibit_versions_bs | 8 | 361.12 | 353.5 | 37.07 | 316 | 432 |
| exhibit_versions_en | 8 | 411.5 | 385.0 | 59.68 | 353 | 504 |

Lengths count whitespace-separated words. SD uses n − 1; N/A denotes an undefined statistic.

## Exhibit text lengths

| exhibit_id | lang | words |
| --- | --- | --- |
| ibu_about_programs | bs | 327 |
| ibu_about_programs | en | 353 |
| ibu_academic_calendar | bs | 394 |
| ibu_academic_calendar | en | 504 |
| ibu_feh | bs | 349 |
| ibu_feh | en | 365 |
| ibu_fess | bs | 358 |
| ibu_fess | en | 385 |
| ibu_kk_igman_burch | bs | 364 |
| ibu_kk_igman_burch | en | 420 |
| ibu_podcast_media | bs | 316 |
| ibu_podcast_media | en | 378 |
| ibu_student_life | bs | 349 |
| ibu_student_life | en | 385 |
| ibu_visitor_faq | bs | 432 |
| ibu_visitor_faq | en | 502 |

## Question–exhibit lexical overlap

| label | questions | mean_jaccard | median_jaccard | min_jaccard | max_jaccard |
| --- | --- | --- | --- | --- | --- |
| answerable | 93 | 0.0301 | 0.0312 | 0.0084 | 0.0635 |
| unanswerable_plausible | 76 | 0.0216 | 0.021 | 0.0033 | 0.0515 |
| out_of_scope | 31 | 0.009 | 0.0084 | 0.0 | 0.0188 |

Jaccard uses unique lowercase word tokens from the selected exhibit text in the same language. Tokens match Unicode `\w+`; diacritics are retained, without stemming or stopword removal. Similarity is the size of the token intersection divided by the token union, or zero for an empty union.

Mean Jaccard: answerable **0.0301**, plausible **0.0216**, out of scope **0.0090**.

A plausible question can share topic words with the text while requesting an unstated fact. Jaccard measures lexical overlap, not answerability or BM25 performance. These descriptive results do not establish that a retrieval threshold succeeds or fails.

## Bosnian diacritics

Bosnian questions without any č/ć/đ/š/ž character: **61/102 (59.8%)**.

This is **not** a reliable count of deliberately omitted diacritics: many correctly written questions naturally contain none.

Kerim's authoring record identifies 10 intentional omissions among his 50 Bosnian drafts. Intentional omissions across both authors remain unquantified.

## Reproduce

Run from the pre-integration Kerim branch with the reviewed wording in `data/questions/questions.csv`:

```bash
analysis_dir=$(mktemp -d)
cp data/questions/questions.csv "$analysis_dir/questions.csv"
git show e2cf0ad:data/questions/questions.csv | tail -n +2 >> "$analysis_dir/questions.csv"
uv run --frozen python scripts/data_analysis.py --questions "$analysis_dir/questions.csv" --exhibits data/exhibits --out results --preliminary
```

## Figures

- `figures/questions_by_label_language.png`

- `figures/question_lengths.png`

- `figures/exhibit_lengths.png`

These are descriptive statistics, not model performance results.
