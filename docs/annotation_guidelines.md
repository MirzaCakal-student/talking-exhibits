
# Annotation Guidelines — Talking Exhibits

**Course:** IT 3004 — Introduction to Natural Language Processing  
**Project:** Talking Exhibits  
**Languages:** Bosnian (bs) and English (en)  
**Responsible member:** Kerim Hodžić  
**Status:** Draft — awaiting team review

## 1. Purpose

These guidelines establish consistent rules for annotating visitor questions in the Talking Exhibits project.

The system receives a question about a selected exhibit and must determine whether that question can be answered using only the exhibit's text.

The main research objective is to evaluate how reliably the system recognizes unanswerable questions and refuses to answer instead of generating unsupported information.

Each question must receive exactly one of three gold labels:

- `answerable`
- `unanswerable_plausible`
- `out_of_scope`

These labels are assigned by human annotators based on the selected exhibit text.

## 2. Fundamental annotation principle

The selected exhibit text is the only permitted source of evidence.

Annotators must not use:

- External websites or search engines.
- General knowledge.
- Personal assumptions.
- Information from another exhibit.
- LLM-generated responses as evidence.
- Speculative conclusions.

A question is answerable only when the exhibit explicitly contains enough information to provide a complete answer.

This principle applies equally to Bosnian and English questions.

## 3. Annotation classes

### 3.1 Answerable

**Label:** `answerable`

A question is answerable when its complete answer is explicitly stated in the selected exhibit text.

The annotator must identify an exact answer span within the exhibit text.

Example exhibit (Bosnian):

"Biblioteka je otvorena 2012. godine. Ima dvije čitaonice. Nalazi se u zgradi C."

| Question | Label | Answer span |
| --- | --- | --- |
| Kada je otvorena biblioteka? | answerable | 2012 |
| Koliko čitaonica ima biblioteka? | answerable | dvije |
| U kojoj zgradi se nalazi biblioteka? | answerable | zgradi C |

Example exhibit (English):

"The library opened in 2012. It has two reading rooms. It is located in Building C."

| Question | Label | Answer span |
| --- | --- | --- |
| When did the library open? | answerable | 2012 |
| How many reading rooms does it have? | answerable | two |
| Where is the library located? | answerable | Building C |

The wording of the question does not need to match the exhibit exactly. Semantic equivalence is acceptable when a direct textual answer exists.

### 3.2 Plausible but unanswerable

**Label:** `unanswerable_plausible`

A question belongs to this class when it is relevant to the exhibit and sounds reasonable, but the exhibit does not provide enough information to answer it.

Bosnian examples using the library exhibit:

| Question | Label | Reason |
| --- | --- | --- |
| Ko je projektovao biblioteku? | unanswerable_plausible | The architect is not identified. |
| Koliko knjiga ima biblioteka? | unanswerable_plausible | The number of books is missing. |
| Koje je radno vrijeme biblioteke? | unanswerable_plausible | Opening hours are not stated. |

English examples:

| Question | Label | Reason |
| --- | --- | --- |
| Who designed the library? | unanswerable_plausible | The designer is not mentioned. |
| How many books does the library contain? | unanswerable_plausible | The number of books is not provided. |
| What are the library's opening hours? | unanswerable_plausible | Opening hours are not stated. |

A question remains unanswerable even if the correct answer may be publicly available elsewhere.

### 3.3 Out of scope

**Label:** `out_of_scope`

A question is out of scope when it is unrelated to the selected exhibit or explicitly concerns another exhibit.

Bosnian examples:

| Question | Label |
| --- | --- |
| Ko je osvojio Svjetsko prvenstvo u fudbalu? | out_of_scope |
| Kakva je vremenska prognoza za sutra? | out_of_scope |
| Koliko planeta ima Sunčev sistem? | out_of_scope |

English examples:

| Question | Label |
| --- | --- |
| Who won the Football World Cup? | out_of_scope |
| What is tomorrow's weather forecast? | out_of_scope |
| How many planets are in the Solar System? | out_of_scope |

An unrelated question must not be classified as `unanswerable_plausible` simply because the answer is missing.

### 3.4 Binary decision mapping

For evaluation, the three gold labels are mapped to two system decisions.

| Gold label | Expected system decision |
| --- | --- |
| answerable | answer |
| unanswerable_plausible | refuse |
| out_of_scope | refuse |

Therefore:

`refuse = unanswerable_plausible ∪ out_of_scope`

The original three-class labels must be preserved for detailed evaluation and error analysis.

## 4. Annotation procedure

For each question, the annotator must:

1. Identify the selected exhibit.
2. Identify the question language (`bs` or `en`).
3. Read the corresponding exhibit text in that language.
4. Determine exactly what the question requests.
5. Search the exhibit for explicit supporting information.
6. Decide whether the complete answer is present.
7. Assign one of the three gold labels.
8. For answerable questions, record the exact answer span and character offset.
9. For unanswerable questions, leave answer fields empty.
10. Flag ambiguous cases for human review.

The label must be assigned independently of retrieval scores or model predictions.

## 5. Boundary cases

### 5.1 Partial information

If the exhibit contains only part of the required answer, the question is not answerable.

Exhibit:

"The laboratory opened in 2015."

Question:

"On which exact date did the laboratory open?"

Label: `unanswerable_plausible`

Reason: The year is provided, but the day and month are missing.

### 5.2 Reasoning and calculations

For the project's extractive annotation task, answers requiring unsupported reasoning or arithmetic should not be labelled as directly answerable.

Exhibit:

"The laboratory opened in 2015."

Question:

"How old was the laboratory in 2026?"

Label: `unanswerable_plausible`

Reason: The requested age is not explicitly stated and requires calculation.

### 5.3 Numbers written as words or digits

Questions may use different representations of the same number.

Exhibit:

"The laboratory contains three computers."

Question:

"How many computers are in the laboratory?"

Label: `answerable`

Answer span: `three`

The answer span must preserve the original representation from the exhibit.

### 5.4 Synonyms and paraphrases

An answerable question may use synonyms or different sentence structures.

Exhibit:

"The exhibition is located on the second floor."

Question:

"Where can visitors find the exhibition?"

Label: `answerable`

Answer span: `the second floor`

Annotators should judge meaning, not exact word overlap.

### 5.5 Questions about another exhibit

Each question is evaluated only against its assigned exhibit.

If a question explicitly concerns a different exhibit, it is `out_of_scope` for the selected exhibit.

For example, “Which radio station did the students visit?” is out of scope for the library exhibit even if a separate media exhibit names the station. “What are the library's opening hours?” is `unanswerable_plausible` when the library exhibit omits the hours.

### 5.6 Bosnian questions without diacritics

Bosnian questions may be written without the characters č, ć, đ, š and ž.

Example:

"Koliko citaonica ima biblioteka?"

This has the same intended meaning as:

"Koliko čitaonica ima biblioteka?"

If the exhibit explicitly contains the answer, the question remains `answerable`.

The answer span must still preserve the original spelling and diacritics of the exhibit text.

### 5.7 Multiple possible answer spans

Choose the shortest contiguous span that fully answers the question. If equally short spans are equally valid, use the earliest occurrence that expresses the requested fact in context.

Example:

"The library opened in 2012. In 2012, it welcomed its first visitors."

Question:

"When did the library open?"

Answer span: `2012`

Use the first `2012` because its sentence explicitly gives the opening year.

### 5.8 Multi-part questions

Prefer questions requesting one specific fact.

Example:

"When did the library open, and who designed it?"

If the exhibit provides the opening year but not the designer, the question is only partially supported.

Such questions should preferably be split into separate questions during dataset preparation.

If they cannot be rewritten, they must not be labelled answerable unless all essential requested information is explicitly supported.

### 5.9 Ambiguous questions

Avoid questions with unclear references.

Example:

"When did it open?"

If the exhibit discusses multiple buildings or events, identify the intended subject before assigning a label. For example, use “When did the library open?” when the exhibit gives different opening years for the library and the laboratory. If the intended subject or reading cannot be established, hold the item for review before inclusion.

### 5.10 Yes/no questions

Prefer questions with extractive answers.

Instead of:

"Does the library have two reading rooms?"

Use:

"How many reading rooms does the library have?"

This ensures that the annotated answer can be represented by an exact text span.

### 5.11 Contradictory evidence

If an exhibit contains conflicting facts about the requested answer, flag the question for manual review.

Do not arbitrarily choose one contradictory statement.

### 5.12 Questions requiring external knowledge

Even if an answer is widely known, the question is unanswerable if the selected exhibit does not explicitly provide the information.

General knowledge must not override the exhibit text.

## 6. Answer span annotation

Every `answerable` question must contain:

- `answer_text`
- `answer_start`

### 6.1 Answer text

The answer text must be an exact, contiguous substring of the original exhibit text.

It should:

- Fully answer the question.
- Be as short as possible.
- Preserve original spelling and capitalization.
- Preserve diacritics.
- Come from the exhibit in the question's language.
- Exclude unnecessary surrounding sentences.

Do not rewrite, normalize or translate the extracted answer.

### 6.2 Answer start

`answer_start` is the zero-based Python character offset of the answer within the full original exhibit text.

It must not be calculated from:

- A translated version of the exhibit.
- A retrieved chunk.
- A normalized version of the text.
- A byte offset.

Example:

```python
text = "Biblioteka je otvorena 2012. godine."
answer_text = "2012"
answer_start = text.find(answer_text)

assert answer_start == 23
assert text[
    answer_start:answer_start + len(answer_text)
] == answer_text
```

When the same answer appears more than once, select the first complete, valid occurrence according to Section 5.7.

A value of `0` is valid if the answer begins at the start of the exhibit.

### 6.3 Unanswerable questions

For `unanswerable_plausible` and `out_of_scope`:

- `answer_text` must be empty.
- `answer_start` must be empty.

Do not use `"None"`, `"null"`, `"NaN"` or `0` as missing-value placeholders.

## 7. Language consistency

The project supports Bosnian (`bs`) and English (`en`).

Questions must be labelled using the corresponding language version of the selected exhibit.

Do not use the English exhibit to supply information missing from the Bosnian exhibit, or vice versa.

Both languages follow the same class definitions.

Language-specific differences should be considered during evaluation and error analysis.

## 8. Question authorship and AI assistance

The dataset must preserve the origin of each question.

The `source` field uses:

- `human`
- `llm_checked`

### Human-authored questions

Use `human` when a student independently writes the question.

### AI-assisted questions

Use `llm_checked` only when a question involved LLM assistance and was subsequently checked, corrected where necessary, and approved by a human annotator.

LLM output must never be accepted as a gold annotation without human verification.

Only human-authored or human-verified questions may be included in the held-out test set.

Any AI assistance must be documented according to the team's AI usage rules.

## 9. Independent review

Each question must be checked by a team member other than its author.

The reviewer should verify:

1. Correct exhibit and language.
2. Clear question wording.
3. Correct gold label.
4. Complete textual evidence for answerable questions.
5. Correct answer text and character offset.
6. Appropriate distinction between plausible and out-of-scope questions.
7. Compliance with the project's authorship rules.

The reviewer must not approve a question solely because an automated validator accepts it.

## 10. Annotation disagreements

When two annotators disagree:

1. Re-read the full original exhibit.
2. Identify the textual evidence.
3. Apply the relevant guideline rule.
4. Discuss the disagreement.
5. Rewrite the question if ambiguity cannot be resolved.
6. Record any new annotation rule that is needed.

If inter-annotator agreement is measured, calculate it from the independent annotations before reconciliation.

Do not alter the original annotations merely to improve agreement statistics.

## 11. Dataset quality and leakage prevention

Questions should vary in wording, difficulty, answer type and lexical similarity.

Avoid near-duplicate questions that differ only by a few words.

Ensure that plausible unanswerable questions are genuinely related to the exhibit, rather than random unrelated questions.

Dataset splitting must prevent exhibit-level leakage: questions from the same exhibit must not be distributed across training, validation and test sets.

Validation data may be used for selecting models and thresholds.

The held-out test set must not be used for tuning.

The final report must contain only measured results obtained from actual experiments.

## 12. Automated checks

The repository provides the question validation script:

`scripts/validate_questions.py`

Its implementation defines the expected input schema and automated checks.

Before finalizing the question dataset, use the validator's required fields and values.

After adding questions, run the validator according to its command-line interface.

Automated validation should check structural consistency, while human reviewers remain responsible for semantic correctness.

## 13. Final annotation checklist

Before accepting a question:

- [ ] The selected exhibit is correct.
- [ ] The language is correct.
- [ ] The question is understandable.
- [ ] The gold label follows these guidelines.
- [ ] No external facts were used.
- [ ] Answer text is exact when required.
- [ ] Answer offset is correct.
- [ ] Unanswerable questions have empty answer fields.
- [ ] The question was reviewed by another team member.
- [ ] Any AI assistance was recorded.
- [ ] No test-set leakage was introduced.

## 14. Team approval

These guidelines must be reviewed by Mirza Čakal and Tarik Hadrović before the main question annotation process proceeds.

Both reviewers should confirm approval through a GitHub Pull Request comment or the team's agreed communication channel.

The guidelines may be updated later when disagreements or new annotation edge cases reveal a need for clarification.

All changes must be applied consistently across the dataset.
