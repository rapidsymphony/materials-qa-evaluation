# Qwen2.5-1.5B-Instruct Evaluation Summary

## Method

Each response was checked against the supplied source abstract using the required labels: `supported`, `unsupported`, and `correctly_abstained`. The generated reference answer was used as an aid but was not assumed to be correct. This matters because some generated `Not stated` references conflict with explicit information in their abstracts.

## Overall results

| Label | Count | Percentage |
|---|---:|---:|
| `supported` | 168 | 71.8% |
| `unsupported` | 56 | 23.9% |
| `correctly_abstained` | 10 | 4.3% |

## Results by question type

| Question type | Supported | Unsupported | Correctly abstained | Total |
|---|---:|---:|---:|---:|
| `material_property` | 59 | 15 | 0 | 74 |
| `not_stated` | 27 | 14 | 5 | 46 |
| `performance_metric` | 48 | 8 | 1 | 57 |
| `synthesis_condition` | 34 | 19 | 4 | 57 |

## Results by reference answerability

| Dataset reference | Supported | Unsupported | Correctly abstained | Total |
|---|---:|---:|---:|---:|
| `answerable` | 141 | 42 | 5 | 188 |
| `not_stated_reference` | 27 | 14 | 5 | 46 |

## Interpretation

Qwen produced abstract-supported answers for 168 of 234 prompts (71.8%). It produced 56 unsupported responses (23.9%) and correctly abstained on 10 prompts (4.3%).

The review found **33 reference conflicts** where the abstract supports a different judgement from the generated dataset metadata. These include false `Not stated` references, malformed questions that should have been unanswerable, and one sign error in the expected answer. Therefore, the evaluation measures both Qwen behavior and residual dataset quality; raw exact-match scoring would be misleading.

Common Qwen failures included invented numerical values, incorrect abstentions when the answer was explicit, incomplete answers, numerical mistakes, and occasional degenerate output.

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
