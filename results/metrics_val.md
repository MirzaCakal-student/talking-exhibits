# Validation evaluation

Only validation data are evaluated; these are **not test-set results**.
Bootstrap: 1000 question-level paired (gold/pred) draws, seed 3004.

| System | Language | N | Refuse precision | Refuse recall | Refuse F1 | 95% CI | False refusal rate | Macro-F1 |
| --- | --- | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| b0 | all | 25 | 0.000 | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | 0.306 |
| b0 | bs | 12 | 0.000 | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | 0.294 |
| b0 | en | 13 | 0.000 | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | 0.316 |
| b1_bm25 | all | 25 | 0.824 | 1.000 | 0.903 | [0.759, 1.000] | 0.273 | 0.873 |
| b1_bm25 | bs | 12 | 0.700 | 1.000 | 0.824 | [0.571, 1.000] | 0.600 | 0.697 |
| b1_bm25 | en | 13 | 1.000 | 1.000 | 1.000 | [1.000, 1.000] | 0.000 | 1.000 |
| b1b_e5 | all | 25 | 0.923 | 0.857 | 0.889 | [0.727, 1.000] | 0.091 | 0.879 |
| b1b_e5 | bs | 12 | 1.000 | 0.714 | 0.833 | [0.500, 1.000] | 0.000 | 0.833 |
| b1b_e5 | en | 13 | 0.875 | 1.000 | 0.933 | [0.769, 1.000] | 0.167 | 0.921 |

## Results by gold class

| System | Gold class | N | Correct decision rate |
| --- | --- | ---: | ---: |
| b0 | answerable | 11 | 1.000 |
| b0 | unanswerable_plausible | 10 | 0.000 |
| b0 | out_of_scope | 4 | 0.000 |
| b1_bm25 | answerable | 11 | 0.727 |
| b1_bm25 | unanswerable_plausible | 10 | 1.000 |
| b1_bm25 | out_of_scope | 4 | 1.000 |
| b1b_e5 | answerable | 11 | 0.909 |
| b1b_e5 | unanswerable_plausible | 10 | 0.800 |
| b1b_e5 | out_of_scope | 4 | 1.000 |

## Three-class gold × binary prediction confusion

### b0

| Gold class | Answer | Refuse |
| --- | ---: | ---: |
| answerable | 11 | 0 |
| unanswerable_plausible | 10 | 0 |
| out_of_scope | 4 | 0 |

### b1_bm25

| Gold class | Answer | Refuse |
| --- | ---: | ---: |
| answerable | 8 | 3 |
| unanswerable_plausible | 0 | 10 |
| out_of_scope | 0 | 4 |

### b1b_e5

| Gold class | Answer | Refuse |
| --- | ---: | ---: |
| answerable | 10 | 1 |
| unanswerable_plausible | 2 | 8 |
| out_of_scope | 0 | 4 |

Confidence intervals are descriptive; question-level bootstrap does not account for exhibit clustering.

## Score-based evaluation

Higher BM25 and e5 scores favor answering. Refusal AUROC uses lower scores to rank unanswerable questions and requires both binary classes.
Risk is the share of accepted questions labeled unanswerable. Coverage is the share of all questions accepted.
Only subsets with complete scores of known direction have curve points in `metrics_val.json`.

| System | Language | Refusal AUROC | Risk–coverage points |
| --- | --- | ---: | ---: |
| b0 | all | N/A | N/A |
| b0 | bs | N/A | N/A |
| b0 | en | N/A | N/A |
| b1_bm25 | all | 0.922 | 26 |
| b1_bm25 | bs | 0.914 | 13 |
| b1_bm25 | en | 1.000 | 14 |
| b1b_e5 | all | 0.883 | 26 |
| b1b_e5 | bs | 0.829 | 13 |
| b1b_e5 | en | 0.929 | 14 |
