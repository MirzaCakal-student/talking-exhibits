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