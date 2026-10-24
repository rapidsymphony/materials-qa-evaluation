# QA Review Error Categories

These categories are defined before manual review. A reviewed QA pair may
receive more than one error label. A pair with no identified problem is marked
`pass`.

## Error categories

### `unsupported_answer`

The answer includes a claim that cannot be verified from the supplied abstract.
Outside knowledge and reasonable-sounding inferences still count as unsupported.

### `contradicted_answer`

The answer conflicts with information stated in the abstract.

### `evidence_mismatch`

The supporting passage is copied from the abstract but does not establish the
given answer.

### `passage_not_exact`

The supporting passage is paraphrased, altered, or is not a contiguous exact
substring of the source abstract.

### `incomplete_answer`

The answer omits information needed to answer the question correctly, such as a
value, unit, material, condition, comparison, or important qualifier.

### `numeric_or_unit_error`

A number, sign, range, unit, percentage, or comparison direction differs from
the abstract.

### `ambiguous_question`

The question has multiple reasonable interpretations, lacks necessary context,
or could have more than one answer from the abstract.

### `incorrect_abstention`

The pair says `Not stated` even though the abstract contains enough information
to answer the question.

### `failed_abstention`

The pair gives a factual answer even though the requested information is absent
from the abstract.

### `formula_corruption`

A chemical formula was changed, reformatted incorrectly, or confused with a
different compound.

### `formula_normalization_error`

The optional normalized formula is incorrect, ambiguous, or was supplied when
the source notation could not be normalized safely.

### `wrong_question_type`

The pair is assigned to the wrong group: `material_property`,
`synthesis_condition`, `performance_metric`, or `not_stated`.

### `duplicate_pair`

The question repeats another pair or asks for the same fact with only superficial
wording changes.

### `source_metadata_error`

The arXiv ID, source title, or other source information does not match the
abstract used to create the pair.

## Review rule

Reviewers should record every applicable category and add a short note. When
several errors apply, the most serious factual problem should be listed first.
The audit should report both the number of affected QA pairs and the number of
occurrences of each category.
