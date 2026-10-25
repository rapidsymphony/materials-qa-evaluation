# QA Audit Report

## Method

The error categories in `docs/error_categories.md` were fixed before this review. The 50 pairs in `qa_audit_sample.jsonl` were reviewed pair by pair against the full source abstract. Abstracts were joined by `arxiv_id`, which also makes the `not_stated` cases verifiable. A pair was marked as an error when at least one predefined category applied; multiple categories could apply to one pair.

## Results

- Sample size: **50** of 240 QA pairs
- Passed: **27**
- Pairs with at least one error: **23**
- Observed pair-level error rate: **46%**
- Approximate 95% Wilson confidence interval: **33.0% to 59.6%**
- Pairs with only a question-type error: **9**
- Pairs with a content, evidence, or abstention error: **14 (28%)**

### Counts by category

| Category | Count |
|---|---:|
| `wrong_question_type` | 14 |
| `incorrect_abstention` | 7 |
| `incomplete_answer` | 6 |
| `evidence_mismatch` | 5 |
| `failed_abstention` | 3 |
| `ambiguous_question` | 1 |
| `unsupported_answer` | 0 |
| `contradicted_answer` | 0 |
| `passage_not_exact` | 0 |
| `numeric_or_unit_error` | 0 |
| `formula_corruption` | 0 |
| `formula_normalization_error` | 0 |
| `duplicate_pair` | 0 |
| `source_metadata_error` | 0 |

Category counts exceed the number of erroneous pairs because a pair may contain more than one kind of error.

## Interpretation

The sample estimates that about 46% of the complete QA dataset contains at least one error. Nine sampled pairs contain only a category-assignment problem, while 14 pairs, or 28% of the sample, contain a content, evidence, or abstention problem. The interval from 33.0% to 59.6% is fairly wide, so 50 reviews provide a useful warning about dataset quality but not a precise final error rate. The most frequent issue is incorrect question-type assignment, followed by false abstentions and answers that do not fully answer the question. Because the sample is random, it can estimate the overall pair-level error rate. It is too small to estimate rare error categories reliably. The review also reflects one reviewer’s judgement, especially for borderline distinctions between material properties, process conditions, and performance metrics.

## Pair-by-pair review

| # | QA ID | Type | Result | Categories | Review note |
|---:|---|---|---|---|---|
| 1 | `qa_0164` | `not_stated` | **pass** | None | The abstract discusses damping and low-loss operation but gives no numerical or comparative damping metric. The abstention is justified. |
| 2 | `qa_0029` | `material_property` | **pass** | None | The answer and exact passage correctly define the thermodynamic factor. |
| 3 | `qa_0007` | `material_property` | **pass** | None | The abstract directly states that curvilinear magnetism designs chiral and anisotropic responses. |
| 4 | `qa_0190` | `synthesis_condition` | **error** | `wrong_question_type` | The passage describes the scope of a theory, not a synthesis condition. |
| 5 | `qa_0071` | `performance_metric` | **pass** | None | The conductivity value and unit match the supporting passage. |
| 6 | `qa_0063` | `performance_metric` | **pass** | None | The reported 63% average increase is copied correctly and answers the question. |
| 7 | `qa_0058` | `synthesis_condition` | **pass** | None | The Ti/W bilayer and 300-mm process context are explicitly stated and fit the broad fabrication/process-condition definition. |
| 8 | `qa_0036` | `synthesis_condition` | **error** | `wrong_question_type` | 500 K is the temperature used for a theoretical evaluation, not a synthesis temperature. |
| 9 | `qa_0189` | `material_property` | **pass** | None | The abstract directly identifies dynamically induced oxygen vacancies. |
| 10 | `qa_0027` | `synthesis_condition` | **error** | `evidence_mismatch`, `incomplete_answer`, `wrong_question_type` | The passage names the example systems and transformation, but gives no synthesis conditions. The answer therefore does not answer the question. |
| 11 | `qa_0174` | `synthesis_condition` | **error** | `wrong_question_type` | Rotational twinning is a physical twisting mechanism, not a synthesis condition. |
| 12 | `qa_0237` | `material_property` | **pass** | None | The DOS-derived Seebeck indicator is explicitly identified as the ranking property. |
| 13 | `qa_0140` | `not_stated` | **pass** | None | Molecular-beam epitaxy is named, but no temperature, pressure, duration, or growth rate is provided. The requested specific conditions are absent. |
| 14 | `qa_0023` | `material_property` | **pass** | None | The abstract explicitly describes the simulated transport as non-Markovian. |
| 15 | `qa_0152` | `not_stated` | **error** | `incorrect_abstention` | The abstract directly identifies the compared processing methods as spin coating and gravure printing. |
| 16 | `qa_0109` | `material_property` | **pass** | None | The abstract directly states that Zr clustering enhances local polarization. |
| 17 | `qa_0009` | `material_property` | **pass** | None | The conductivity threshold and unit match the abstract. |
| 18 | `qa_0008` | `material_property` | **error** | `wrong_question_type` | The mapping learned by an ML potential is a model target, not a material property. |
| 19 | `qa_0024` | `synthesis_condition` | **error** | `evidence_mismatch`, `wrong_question_type` | K-medoids clustering is a data-analysis method for selecting environments, not a synthesis condition. |
| 20 | `qa_0056` | `not_stated` | **pass** | None | The abstract gives only the direction of the effect and a correlation coefficient, not the requested magnitude and sign for each parent functional. |
| 21 | `qa_0060` | `not_stated` | **error** | `incorrect_abstention` | The undoped parent formula KSb3Mn9O19 is explicitly stated as the model system. |
| 22 | `qa_0130` | `synthesis_condition` | **pass** | None | Ag2Te is the investigated composition, which is allowed under the synthesis-condition category definition used for generation. |
| 23 | `qa_0155` | `performance_metric` | **error** | `evidence_mismatch`, `incomplete_answer`, `wrong_question_type` | The answer describes the channel as performance-limiting but supplies no performance metric. The passage does not support the question as phrased. |
| 24 | `qa_0238` | `synthesis_condition` | **error** | `failed_abstention`, `evidence_mismatch`, `incomplete_answer` | The question requests a layer thickness, but the abstract gives no thickness value. The answer lists optimized variables without answering the question. |
| 25 | `qa_0144` | `not_stated` | **error** | `incorrect_abstention` | The composition is explicitly given as [Sr6TaS8]1+x[TaS2]8. |
| 26 | `qa_0051` | `performance_metric` | **error** | `failed_abstention`, `evidence_mismatch`, `incomplete_answer` | The abstract does not state a maximum magnetic-field strength. The answer merely says that a coil dipole field was used. |
| 27 | `qa_0184` | `not_stated` | **error** | `incorrect_abstention` | The abstract names an anion-electron exchange process as the proposed stabilization route, which is a supported short answer to the question. |
| 28 | `qa_0167` | `performance_metric` | **error** | `ambiguous_question`, `incomplete_answer`, `wrong_question_type` | The question does not define a performance metric, and the answer is a fragment describing an underestimation rather than a metric or magnitude. |
| 29 | `qa_0180` | `not_stated` | **error** | `incorrect_abstention` | The abstract explicitly relates high stress to trans-granular cracking, intermediate stress to mixed cracking, and low stress to inter-granular cracking. |
| 30 | `qa_0228` | `not_stated` | **error** | `incorrect_abstention` | The abstract explicitly gives the material formula SnS. |
| 31 | `qa_0108` | `not_stated` | **pass** | None | The abstract proposes sidewall descriptors but reports no measured superconducting-qubit performance metric. |
| 32 | `qa_0057` | `material_property` | **pass** | None | Perfect rectification efficiency is directly stated. |
| 33 | `qa_0115` | `performance_metric` | **pass** | None | The ionic conductivity of approximately 1.7 S/cm at 300 K is directly supported. |
| 34 | `qa_0151` | `performance_metric` | **error** | `wrong_question_type` | The sum rule is a spectroscopic analysis quantity, not a material performance metric. |
| 35 | `qa_0072` | `not_stated` | **pass** | None | The abstract reports outcomes and conductivities but gives no synthesis temperatures, pressures, durations, or process steps. |
| 36 | `qa_0002` | `material_property` | **pass** | None | The interface-induced Berry-curvature asymmetry or dipole is directly identified as enabling the response. |
| 37 | `qa_0195` | `performance_metric` | **pass** | None | The strain-dependent saturation-magnetization response matches the passage. |
| 38 | `qa_0041` | `material_property` | **error** | `wrong_question_type` | The answer lists electronic-structure outputs resolved by the computational framework rather than a material property. |
| 39 | `qa_0179` | `performance_metric` | **pass** | None | The short-range organization and two-to-three-times stronger interlayer ordering are directly supported. |
| 40 | `qa_0225` | `material_property` | **pass** | None | The abstract directly states that a spin polarizer requires a chiral junction. |
| 41 | `qa_0088` | `not_stated` | **pass** | None | The abstract provides only qualitative comparison to PBE, SCAN, and HSE06, not a numerical band-gap-error metric. |
| 42 | `qa_0206` | `synthesis_condition` | **error** | `failed_abstention`, `incomplete_answer`, `wrong_question_type` | The abstract does not give the numerical Fermi-level ranges, and surface orientation is a transport-evaluation condition rather than a synthesis condition. |
| 43 | `qa_0040` | `performance_metric` | **pass** | None | The 98.82% classification accuracy exactly matches the source passage. |
| 44 | `qa_0221` | `material_property` | **error** | `wrong_question_type` | The sixteenfold advantage is a performance metric, while the pair is labelled as a material property. |
| 45 | `qa_0196` | `not_stated` | **error** | `incorrect_abstention` | The abstract explicitly identifies the material as AlN. |
| 46 | `qa_0087` | `performance_metric` | **pass** | None | The precomputed library coverage of over one thousand structures is directly supported. |
| 47 | `qa_0231` | `performance_metric` | **pass** | None | The approximately 1.1 eV activation energy is directly supported. |
| 48 | `qa_0222` | `synthesis_condition` | **error** | `wrong_question_type` | Heating and cooling during ARPES are measurement conditions, not synthesis conditions. |
| 49 | `qa_0098` | `synthesis_condition` | **pass** | None | The three evaluated electrolyte concentration regimes are listed exactly in the passage. |
| 50 | `qa_0025` | `performance_metric` | **error** | `wrong_question_type` | The answer describes a qualitative magnetic-field dependence of Néel temperature, not a performance metric. |

## Data card and filtering history

| Stage | Input | Removed or rejected | Remaining |
|---|---:|---:|---:|
| arXiv retrieval from `cond-mat.mtrl-sci` | 1,500 | 0 | 1,500 |
| Duplicate arXiv ID removal | 1,500 | 0 | 1,500 |
| Duplicate abstract-text removal | 1,500 | 0 | 1,500 |
| Category metadata check | 1,500 | 0 | 1,500 |
| Content relevance classification | 1,500 | 7 rejected after review | 1,493 |
| QA generation and automatic format checks | Attempts not logged | Count not recoverable | 240 accepted |
| Chemical-formula metadata cleanup | 240 pairs / 187 entries | 0 pairs / 82 metadata entries | 240 pairs / 105 entries |
| Random manual audit | 50 sampled | 23 flagged, not removed | 27 passed review |
| Post-audit curation | 240 | 6 removed | 234 |
| Category cleanup | 234 | 3 removed | 231 |

The content filter initially sent 21 abstracts to a review queue. Manual review kept 14 and rejected 7, producing 1,493 final abstracts. The QA generator saved only accepted pairs and did not log every skipped or rejected generation attempt, so that removed count cannot be reconstructed reliably. Formula cleanup removed metadata entries rather than QA records.

The materials filter removed only 7 of the 1,500 collected abstracts. The random audit covered 50 pairs. After removing nine unsuitable pairs across the two curation stages, 190 pairs in the final dataset had not been included in the manual audit.

## Files

- `data/processed/qa_audit_reviewed.jsonl` contains all 50 reviewed pairs, their full source abstracts, labels, categories, and notes.
- `data/processed/qa_audit_sample.jsonl` is the unchanged sampled input.
- `docs/error_categories.md` contains the categories fixed before review.
