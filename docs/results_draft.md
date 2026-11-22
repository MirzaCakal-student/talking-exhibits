# Results

## Preliminary question-set analysis

The merged Bosnian and English drafts include answerable, plausibly unanswerable and out-of-scope questions. The preliminary analysis shows that answerable questions have the highest mean lexical overlap with their exhibit text, followed by plausibly unanswerable and out-of-scope questions. The ranges overlap. A plausibly unanswerable question can share vocabulary with its exhibit while requesting a detail the exhibit omits. The class distributions and token-overlap statistics are recorded in the [dataset analysis](../results/data_tables.md). Human verification and exhibit-level splits are pending.

## Local prototype verification

Local checks with the prompted baseline confirmed that the system can return a verbatim answer from the selected-language exhibit and refuse questions whose requested facts are absent. An identical question about a radio station was answered in the media exhibit and refused in the faculty exhibit. These checks verify the behaviour of selected examples. Validation metrics for the always-answer, BM25 and multilingual e5 baselines await the reviewed validation split and matching predictions. Results for the trained classifier also require a completed model and a fixed evaluation configuration.
