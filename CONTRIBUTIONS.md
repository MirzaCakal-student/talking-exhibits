# Contributions

Each member commits their own work from their own GitHub account. Update this file whenever you finish a piece of work.

## Planned responsibilities

| Member | Main responsibility | Also contributes |
| --- | --- | --- |
| Mirza Čakal | Answerability classifier (fine-tuning, calibration), retrieval pipeline | Question writing, paper: Methodology |
| Tarik Hadrović | Exhibit texts and sources, question set, test set labelling and checks | BM25 baseline, paper: Dataset, Literature Review |
| Kerim Hodžić | Evaluation scripts, LLM baseline, error analysis, web demo with QR codes | Question writing, paper: Results, slides |

## Log

| Date | Member | Work done |
| --- | --- | --- |
| 25.10.2026 | Mirza Čakal | Proposal draft, repository setup (README, CONTRIBUTIONS.md, docs/AI_LOG.md) |
| 25.10.2026 | Tarik Hadrović | Proposal review; discussed project setup and division of work with Mirza Čakal (Discord) |
| 25.10.2026 | Kerim Hodžić | Reviewed the project proposal, discussed the planned evaluation approach, and confirmed responsibilities for the LLM baseline, error analysis, and web demo |
| 25.10.2026 | Tarik Hadrović | Added GitHub usernames to README, added own entry to docs/AI_LOG.md |
| 12–14.11.2026 | Tarik Hadrović | Added the question set template, the question validator (scripts/validate_questions.py) with 16 pytest tests, and pytest with uv.lock to the project |
| 16.11.2026 | Kerim Hodžić | Added annotation guidelines (docs/annotation_guidelines.md), implemented evaluation metrics (src/talking_exhibits/evaluate.py), added 20 unit tests (tests/test_metrics.py), verified all 36 project tests passed, and updated personal project documentation |
| 16.11.2026 | Kerim Hodžić | Implemented data analysis and baseline evaluation scripts (scripts/data_analysis.py and scripts/evaluate_all.py), verified syntax and successful output generation using temporary test data; actual dataset analysis and baseline results pending |
| 16.11.2026 | Tarik Hadrović | Exhibit list (T-1): chose 12 IBU exhibits with the team split (4 per member), sources and writing rules in data/exhibits/README.md, linked from HANDOFF.md |
| 18.11.2026 | Tarik Hadrović | Data tools: answer_start filler, exhibit-level split (T-6), Cohen's kappa (T-5), 14 tests; exhibit decision in HANDOFF |
| 19.11.2026 | Tarik Hadrović | Exhibit texts for the academic calendar, visitor FAQ, KK Igman Burch and student life (BS and EN, 8 files in data/exhibits/); removed the rule against AI-drafted texts as agreed by the team |
| 22.11.2026 | Tarik Hadrović | Question set for my 4 exhibits: 100 questions (q0101–q0200) in Bosnian and English across the three classes, drafted with Claude Code; answer positions filled with fill_answer_starts.py |
| 22.11.2026 | Tarik Hadrović | Paper: Dataset section (T-7) and half of the Literature Review (T-8) in 02 Paper, 7 sources in Zotero |
| 22.11.2026 | Kerim Hodžić | Resolved the PR #8 question dataset merge conflict, preserving all 200 questions, 11 columns, and 93 exact answer spans. Committed and pushed the resolution as `af3effc`; PR #8 remained open for review. |
| 16–22.11.2026 | Kerim Hodžić | Prepared four bilingual IBU exhibit drafts (eight JSON files) and 100 questions (`q0001–q0100`) across the three answerability classes. Reviewed the AI-assisted questions and recorded their provenance as `llm_checked`. |
| 19–22.11.2026 | Kerim Hodžić | Expanded dataset analysis to 200 draft questions and 16 language-specific exhibit texts. Generated updated statistics, a Markdown summary, and three figures showing question distribution and text lengths. |
| 19–22.11.2026 | Kerim Hodžić | Extended the evaluation pipeline with refusal AUROC, risk–coverage analysis, language-specific results, confidence intervals, and prediction alignment by question ID. Added automated tests for the evaluation functionality. |
| 22.11.2026 | Kerim Hodžić | Implemented the B2 prompted LLM baseline using local Ollama and Qwen2.5 1.5B. Tested real Bosnian and English questions, verified passage-grounded answers and refusals, and improved the prompt to require explicit textual support. |
| 22.11.2026 | Kerim Hodžić | Implemented error-analysis export and a bilingual FastAPI demonstration with exhibit-specific QR codes. Verified local routing, exhibit and language isolation, model error handling, and the complete automated test suite (208 tests passed). |
| 22.11.2026 | Kerim Hodžić | Prepared the Introduction and preliminary Results drafts, updated the question review documentation, and created four M3 check-in slides. Independently reviewed Tarik's 100 questions and documented proposed corrections requiring Tarik's approval. |
| 22.11.2026 | Tarik Hadrović | Reviewed Kerim's PR #8 before merge; kappa sample: script and 50 unlabelled questions (25 per author, seed 3004) for the agreement check (T-5) |