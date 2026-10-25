# Qwen2.5-1.5B-Instruct Evaluation Summary

## Method

Each response was checked against the supplied source abstract using the required labels: `supported`, `unsupported`, and `correctly_abstained`. The generated reference answer was used as an aid but was not assumed to be correct. This matters because some generated `Not stated` references conflict with explicit information in their abstracts.

## Overall results

| Label | Count | Percentage |
|---|---:|---:|
| `supported` | 166 | 71.9% |
| `unsupported` | 55 | 23.8% |
| `correctly_abstained` | 10 | 4.3% |

## Results by question type

| Question type | Supported | Unsupported | Correctly abstained | Total |
|---|---:|---:|---:|---:|
| `material_property` | 59 | 15 | 0 | 74 |
| `not_stated` | 27 | 14 | 5 | 46 |
| `performance_metric` | 48 | 8 | 1 | 57 |
| `synthesis_condition` | 32 | 18 | 4 | 54 |

## Results by reference answerability

| Dataset reference | Supported | Unsupported | Correctly abstained | Total |
|---|---:|---:|---:|---:|
| `answerable` | 139 | 41 | 5 | 185 |
| `not_stated_reference` | 27 | 14 | 5 | 46 |

## Interpretation

Qwen produced abstract-supported answers for 166 of 231 prompts (71.9%). It produced 55 unsupported responses (23.8%) and correctly abstained on 10 prompts (4.3%).

The review found **33 reference conflicts** where the abstract supports a different judgement from the generated dataset metadata. These include false `Not stated` references, malformed questions that should have been unanswerable, and one sign error in the expected answer. Therefore, the evaluation measures both Qwen behavior and residual dataset quality; raw exact-match scoring would be misleading.

The largest issue was that 27 of the 46 `not_stated` references received source-supported answers. This suggests that many questions labelled unanswerable were actually answerable from their abstracts.

Common Qwen failures included invented numerical values, incorrect abstentions when the answer was explicit, incomplete answers, numerical mistakes, and occasional degenerate output.

## Limitations

One reviewer assigned all response labels. Borderline scientific, support, and category decisions may therefore be subjective. The generated reference answers were also imperfect, so the abstract was treated as the main evidence source.

## Representative failures

- `qa_0012`: invented an inverse-square scaling equation absent from the abstract.
- `qa_0169`: returned 1.19 eV instead of the stated 1.09 eV.
- `qa_0037`: reversed the reported single- and double-vacancy ranking.
- `qa_0200`: invented a critical fraction of x = 1.
- `qa_0009`: generated repeated greater-than symbols without the conductivity value.

## Representative successes

- `qa_0001`: correctly identified atomic volume.
- `qa_0115`: correctly reported approximately 1.7 S/cm at 300 K.
- `qa_0051`: correctly abstained because the maximum magnetic-field strength was absent.
- `qa_0131`: correctly reported the positive Gibbs-free-energy range despite a sign error in the reference answer.

The full response-level decisions and notes are stored in `qwen_results_classified.jsonl`.
