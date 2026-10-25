import json
from collections import Counter, defaultdict
from pathlib import Path


INPUT_PATH = Path("data/evaluation/qwen_results.jsonl")
OUTPUT_PATH = Path("data/evaluation/qwen_results_classified.jsonl")
SUMMARY_JSON_PATH = Path("data/evaluation/qwen_evaluation_summary.json")
SUMMARY_MD_PATH = Path("data/evaluation/qwen_evaluation_summary.md")


# Pair-by-pair rubric review against the supplied abstract. These responses
# either contradict the abstract, omit the requested fact, give an incorrect
# number, hallucinate a detail, or fail to abstain when the answer is absent.
UNSUPPORTED_IDS = {
    "qa_0009", "qa_0011", "qa_0012", "qa_0013", "qa_0016",
    "qa_0018", "qa_0037", "qa_0038", "qa_0039", "qa_0042",
    "qa_0044", "qa_0046", "qa_0050", "qa_0053", "qa_0056",
    "qa_0074", "qa_0080", "qa_0086", "qa_0091", "qa_0093",
    "qa_0094", "qa_0096", "qa_0097", "qa_0105", "qa_0108",
    "qa_0111", "qa_0116", "qa_0121", "qa_0122", "qa_0127",
    "qa_0129", "qa_0138", "qa_0144", "qa_0149", "qa_0158",
    "qa_0159", "qa_0160", "qa_0169", "qa_0170", "qa_0177",
    "qa_0179", "qa_0180", "qa_0186", "qa_0194", "qa_0196",
    "qa_0198", "qa_0200", "qa_0201", "qa_0206", "qa_0214",
    "qa_0216", "qa_0224", "qa_0232", "qa_0236", "qa_0237",
    "qa_0240",
}


# These abstentions are correct when judged against the actual abstract. Five
# of them expose incorrect answerable/reference metadata in the final dataset.
CORRECTLY_ABSTAINED_IDS = {
    "qa_0015", "qa_0051", "qa_0072", "qa_0106", "qa_0146",
    "qa_0156", "qa_0164", "qa_0182", "qa_0227", "qa_0238",
}


SPECIFIC_NOTES = {
    "qa_0009": "The response degenerates into repeated greater-than symbols and never gives the stated conductivity above 40,000 S/cm.",
    "qa_0012": "The response invents an inverse-square scaling equation that is not present in the abstract.",
    "qa_0016": "The response invents a 94% top-1 success rate; the abstract gives no numerical rate.",
    "qa_0037": "The response reverses the reported defect ranking after irradiation: the abstract says single vacancies predominate.",
    "qa_0129": "The response is truncated and reports validation errors instead of answering the dynamical-stability question.",
    "qa_0131": "The model correctly gives the positive range stated in the abstract; the dataset reference has an incorrect negative sign.",
    "qa_0144": "The response corrupts the composition [Sr6TaS8]1+x[TaS2]8 into an x-percent mixture.",
    "qa_0169": "The response gives 1.19 eV instead of the stated 1.09 eV.",
    "qa_0177": "The response gives 1.19 eV instead of the stated 1.09 eV.",
    "qa_0179": "The response changes the reported two-to-three-times comparison to exactly two times.",
    "qa_0180": "The response reverses the stress progression by placing inter-granular cracking at higher rather than lower stress.",
    "qa_0200": "The response invents a critical fraction x = 1; the abstract does not provide the value.",
    "qa_0224": "The question asks for magnetic anisotropy, but the response gives the topological Hall effect instead of easy-axis anisotropy.",
    "qa_0237": "The response substitutes the Seebeck coefficient for the distinct DOS-derived Seebeck indicator.",
}


def read_jsonl(path):
    with path.open("r", encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")


def percentage(count, total):
    return round(100 * count / total, 1) if total else 0.0


def main():
    rows = read_jsonl(INPUT_PATH)
    ids = {row["qa_id"] for row in rows}

    if len(rows) != 234 or len(ids) != 234:
        raise ValueError("Expected 234 unique Qwen results")
    if UNSUPPORTED_IDS & CORRECTLY_ABSTAINED_IDS:
        raise ValueError("Classification ID sets overlap")
    if not (UNSUPPORTED_IDS | CORRECTLY_ABSTAINED_IDS) <= ids:
        raise ValueError("Classification contains an unknown QA ID")

    classified = []
    reference_conflicts = []

    for row in rows:
        item = dict(row)
        qa_id = item["qa_id"]

        if qa_id in UNSUPPORTED_IDS:
            label = "unsupported"
            note = SPECIFIC_NOTES.get(
                qa_id,
                "The response is incorrect, incomplete, non-responsive, or includes a claim that is not supported by the abstract.",
            )
        elif qa_id in CORRECTLY_ABSTAINED_IDS:
            label = "correctly_abstained"
            if item["is_answerable"]:
                note = (
                    "The requested information is not actually supplied by the abstract, "
                    "despite the dataset marking this pair as answerable. The abstention is appropriate."
                )
                reference_conflicts.append(qa_id)
            else:
                note = "The abstract does not supply the requested information, and the model appropriately abstains."
        else:
            label = "supported"
            if not item["is_answerable"]:
                note = (
                    "The response is supported by the abstract. This conflicts with the dataset's "
                    "Not stated reference and indicates a reference-label error."
                )
                reference_conflicts.append(qa_id)
            else:
                note = "The response answers the question and is supported by the supplied abstract."

        if qa_id == "qa_0131":
            note = SPECIFIC_NOTES[qa_id]
            reference_conflicts.append(qa_id)

        item["evaluation_label"] = label
        item["evaluation_notes"] = note
        classified.append(item)

    write_jsonl(OUTPUT_PATH, classified)

    overall = Counter(row["evaluation_label"] for row in classified)
    by_type = defaultdict(Counter)
    by_answerability = defaultdict(Counter)
    for row in classified:
        by_type[row["question_type"]][row["evaluation_label"]] += 1
        key = "answerable" if row["is_answerable"] else "not_stated_reference"
        by_answerability[key][row["evaluation_label"]] += 1

    total = len(classified)
    summary = {
        "model_id": classified[0]["model_id"],
        "total_responses": total,
        "overall": {
            label: {
                "count": overall[label],
                "percentage": percentage(overall[label], total),
            }
            for label in ("supported", "unsupported", "correctly_abstained")
        },
        "by_question_type": {
            question_type: {
                label: counts[label]
                for label in ("supported", "unsupported", "correctly_abstained")
            }
            for question_type, counts in sorted(by_type.items())
        },
        "by_reference_answerability": {
            group: {
                label: counts[label]
                for label in ("supported", "unsupported", "correctly_abstained")
            }
            for group, counts in sorted(by_answerability.items())
        },
        "reference_conflicts": {
            "count": len(set(reference_conflicts)),
            "qa_ids": sorted(set(reference_conflicts)),
        },
        "classification_method": (
            "Pair-by-pair rubric review against the supplied abstract. The reference answer "
            "was used as an aid but was not assumed to be correct."
        ),
    }
    SUMMARY_JSON_PATH.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Qwen2.5-1.5B-Instruct Evaluation Summary",
        "",
        "## Method",
        "",
        "Each response was checked against the supplied source abstract using the required labels: "
        "`supported`, `unsupported`, and `correctly_abstained`. The generated reference answer was "
        "used as an aid but was not assumed to be correct. This matters because some generated "
        "`Not stated` references conflict with explicit information in their abstracts.",
        "",
        "## Overall results",
        "",
        "| Label | Count | Percentage |",
        "|---|---:|---:|",
    ]
    for label in ("supported", "unsupported", "correctly_abstained"):
        lines.append(
            f"| `{label}` | {overall[label]} | {percentage(overall[label], total):.1f}% |"
        )

    lines += [
        "",
        "## Results by question type",
        "",
        "| Question type | Supported | Unsupported | Correctly abstained | Total |",
        "|---|---:|---:|---:|---:|",
    ]
    for question_type, counts in sorted(by_type.items()):
        subtotal = sum(counts.values())
        lines.append(
            f"| `{question_type}` | {counts['supported']} | {counts['unsupported']} | "
            f"{counts['correctly_abstained']} | {subtotal} |"
        )

    lines += [
        "",
        "## Results by reference answerability",
        "",
        "| Dataset reference | Supported | Unsupported | Correctly abstained | Total |",
        "|---|---:|---:|---:|---:|",
    ]
    for group, counts in sorted(by_answerability.items()):
        subtotal = sum(counts.values())
        lines.append(
            f"| `{group}` | {counts['supported']} | {counts['unsupported']} | "
            f"{counts['correctly_abstained']} | {subtotal} |"
        )

    conflict_count = len(set(reference_conflicts))
    lines += [
        "",
        "## Interpretation",
        "",
        f"Qwen produced abstract-supported answers for {overall['supported']} of {total} prompts "
        f"({percentage(overall['supported'], total):.1f}%). It produced {overall['unsupported']} "
        f"unsupported responses ({percentage(overall['unsupported'], total):.1f}%) and correctly "
        f"abstained on {overall['correctly_abstained']} prompts ({percentage(overall['correctly_abstained'], total):.1f}%).",
        "",
        f"The review found **{conflict_count} reference conflicts** where the abstract supports a "
        "different judgement from the generated dataset metadata. These include false `Not stated` "
        "references, malformed questions that should have been unanswerable, and one sign error in "
        "the expected answer. Therefore, the evaluation measures both Qwen behavior and residual "
        "dataset quality; raw exact-match scoring would be misleading.",
        "",
        "Common Qwen failures included invented numerical values, incorrect abstentions when the "
        "answer was explicit, incomplete answers, numerical mistakes, and occasional degenerate output.",
        "",
        "## Representative failures",
        "",
        "- `qa_0012`: invented an inverse-square scaling equation absent from the abstract.",
        "- `qa_0169`: returned 1.19 eV instead of the stated 1.09 eV.",
        "- `qa_0037`: reversed the reported single- and double-vacancy ranking.",
        "- `qa_0200`: invented a critical fraction of x = 1.",
        "- `qa_0009`: generated repeated greater-than symbols without the conductivity value.",
        "",
        "## Representative successes",
        "",
        "- `qa_0001`: correctly identified atomic volume.",
        "- `qa_0115`: correctly reported approximately 1.7 S/cm at 300 K.",
        "- `qa_0051`: correctly abstained because the maximum magnetic-field strength was absent.",
        "- `qa_0131`: correctly reported the positive Gibbs-free-energy range despite a sign error in the reference answer.",
        "",
        "The full response-level decisions and notes are stored in `qwen_results_classified.jsonl`.",
    ]
    SUMMARY_MD_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
