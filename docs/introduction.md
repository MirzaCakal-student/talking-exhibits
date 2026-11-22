# Introduction

Natural language question answering offers visitors a way to explore information about exhibits, campus services and academic programmes through their own questions. In an exhibit guide, a visitor can select an exhibit through a QR code and ask about the accompanying text. The available information is necessarily limited: a description may explain what a faculty offers without stating an admission deadline or the cost of a particular activity. A useful guide must recognise these limits when deciding whether to answer.

Fluent language alone does not establish that an answer is supported by the available evidence. Research on hallucination in natural language generation describes the production of content that is inconsistent with or unsupported by its source [1]. Reading comprehension research also shows the importance of plausible questions whose answers are absent from the supplied passage. SQuAD 2.0 introduced such questions to require systems to distinguish supported answers from cases in which they should abstain [2]. In a campus guide, an unsupported answer could mislead a visitor about a programme, service or event, even when it sounds reasonable.

This motivates answerability detection: determining whether the selected text contains sufficient information to answer the question. Refusal is an appropriate outcome when that evidence is missing, while unnecessary refusal prevents access to information that is present. Selective question answering studies this broader problem of deciding when a system should answer and when it should abstain, including under changes in the data distribution [3]. For this project, a question can be related to an exhibit and share many of its words while still requesting an unstated fact. Retrieval relevance therefore needs to be distinguished from support for a complete answer.

Talking Exhibits investigates this problem using Bosnian and English descriptions of International Burch University exhibits. The evidence for each question is restricted to the selected exhibit in the question's language. The draft dataset distinguishes answerable questions, plausible questions without sufficient textual support, and questions outside the exhibit's scope. The latter two classes require the same refusal decision but remain separate for analysis. The bilingual setting allows the project to examine whether refusal detection behaves differently across the two languages. The study addresses three research questions:

- **RQ1:** How reliably can the system detect questions the exhibit text cannot answer and refuse instead of guessing?
- **RQ2:** Does a team-trained answerability classifier detect unanswerable questions better than a retrieval-score threshold and a prompted LLM?
- **RQ3:** Is refusal detection weaker for Bosnian questions than for English ones?

The proposed workflow retrieves passages only from the selected exhibit and uses an answerability classifier to assess the question together with the retrieved evidence. The planned classifier will fine-tune XLM-R, a pretrained multilingual language model [4], on SQuAD 2.0 and the project's training questions. It will control whether the system may formulate an answer or must refuse. Comparisons will include an always-answer baseline, thresholds on lexical and multilingual dense retrieval scores, and a prompted language model instructed to answer only from the supplied text. Thresholds will be selected on validation data, with the test split reserved until the configuration is fixed.

At the M3 stage, the repository contains implementations for preprocessing, retrieval baselines, refusal evaluation and the prompted language-model baseline. The prompted baseline has been exercised locally in both languages. The merged question drafts cover eight bilingual exhibits. Provenance confirmation and independent reviews are pending before the exhibit-level split. The answerability classifier remains a planned component.

The intended contributions are a bilingual question set grounded in campus exhibits, a reproducible framework for evaluating refusal decisions, and a comparison of classification, retrieval thresholds and prompted generation. The evaluation will consider refusal precision, recall and F1, false refusals on answerable questions, and results by language and question class. Examining both plausible and unrelated questions will help identify where systems confuse topical similarity with answerability.

The paper continues with the Literature Review, Dataset and Methodology sections. The Results section will present measured comparisons, followed by Discussion and Limitations and the Conclusion.

## References

[1] Z. Ji et al., “Survey of Hallucination in Natural Language Generation,” arXiv preprint arXiv:2202.03629, 2022. [Online]. Available: [arXiv](https://arxiv.org/abs/2202.03629).

[2] P. Rajpurkar, R. Jia, and P. Liang, “Know What You Don't Know: Unanswerable Questions for SQuAD,” in *Proceedings of the 56th Annual Meeting of the Association for Computational Linguistics (Volume 2: Short Papers)*, 2018, pp. 784–789, doi: [10.18653/v1/P18-2124](https://doi.org/10.18653/v1/P18-2124).

[3] A. Kamath, R. Jia, and P. Liang, “Selective Question Answering under Domain Shift,” in *Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics*, 2020, pp. 5684–5696, doi: [10.18653/v1/2020.acl-main.503](https://doi.org/10.18653/v1/2020.acl-main.503).

[4] A. Conneau et al., “Unsupervised Cross-lingual Representation Learning at Scale,” in *Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics*, 2020, pp. 8440–8451, doi: [10.18653/v1/2020.acl-main.747](https://doi.org/10.18653/v1/2020.acl-main.747).
