import json
import time
from pathlib import Path

import requests


MODEL = "llama3.2"
OLLAMA_URL = "http://localhost:11434/api/generate"

# Set this to like 10 for testing 
LIMIT = None

input_path = Path(
    "data/processed/abstracts_deduplicated.jsonl"
)
classifications_path = Path(
    "data/processed/material_filter_classifications.jsonl"
)
kept_path = Path(
    "data/processed/abstracts_filtered.jsonl"
)
rejected_path = Path(
    "data/processed/abstracts_rejected.jsonl"
)
review_path = Path(
    "data/processed/abstracts_review.jsonl"
)
counts_path = Path(
    "data/processed/filter_counts.json"
)


def classify_with_ollama(record):
    prompt = f"""
You are filtering papers collected from the arXiv materials-science
category. Most papers should be kept. Only reject a paper when it is
clearly unrelated to materials science.

Labels:

keep:
The paper discusses any material, substance, compound, liquid, solid,
crystal, semiconductor, defect, interface, device material, or material
class. Keep papers about thermal, electrical, optical, magnetic,
mechanical, structural, or chemical properties. Theoretical papers,
reviews, reinterpretations of experiments, and simulations should also
be kept when they concern a material or material property.

reject:
Use this only when the paper is clearly unrelated to materials,
material properties, synthesis, characterization, processing, or
material-based device performance.

review:
The connection to materials science is uncertain or indirect. When
unsure, choose review rather than reject.

Important rules:
- Liquids and soft matter count as materials.
- Thermal transport and thermal conductivity count as material
  properties.
- If the paper names a physical substance or material and investigates
  one of its properties, choose keep.
- Do not choose review merely because a paper is theoretical, is a
  review article, or does not perform synthesis.
- Use review only when no clear material, material property, synthesis,
  characterization, processing step, or material-based device can be
  identified.
- If the paper is solely about mathematics, software, or a general
  algorithm and names no physical material or material property, choose
  reject rather than review.

Examples:

Title: The role of sound in liquid thermal transport
Label: keep
Reason: Thermal conductivity is a material property of liquids.

Title: Donor-acceptor recombination in diamond
Label: keep
Reason: The paper studies optical behaviour and defects in diamond.

Title: A faster sorting algorithm for integer arrays
Label: reject
Reason: The paper studies a general algorithm and no physical material
or material property.

Return only valid JSON in this exact form:
{{"label": "keep", "reason": "Short explanation"}}

Title:
{record["title"]}

Abstract:
{record["abstract"]}
""".strip()

    for attempt in range(1, 4):
        try:
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                    "options": {
                        "temperature": 0,
                        "seed": 42,
                    },
                },
                timeout=180,
            )
            response.raise_for_status()

            generated_text = response.json()["response"]
            result = json.loads(generated_text)

            label = result.get("label", "").strip().lower()
            reason = result.get("reason", "").strip()

            if label not in {"keep", "reject", "review"}:
                raise ValueError(f"Invalid label: {label}")

            if not reason:
                raise ValueError("The model did not provide a reason")

            return {
                "arxiv_id": record["arxiv_id"],
                "label": label,
                "reason": reason,
                "method": "ollama_llama3.2",
            }

        except (
            requests.exceptions.RequestException,
            json.JSONDecodeError,
            KeyError,
            ValueError,
        ) as error:
            print(
                f"Attempt {attempt} failed for "
                f"{record['arxiv_id']}: {error}"
            )

            if attempt == 3:
                return {
                    "arxiv_id": record["arxiv_id"],
                    "label": "review",
                    "reason": (
                        "Automatic classification failed after "
                        "three attempts."
                    ),
                    "method": "classification_error",
                }

            time.sleep(2)


# Load the deduplicated abstracts.
records = []

with input_path.open("r", encoding="utf-8") as file:
    for line in file:
        if line.strip():
            records.append(json.loads(line))


# Load previous classifications so the script can resume.
classifications = {}

if classifications_path.exists():
    with classifications_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        for line in file:
            if line.strip():
                result = json.loads(line)
                classifications[result["arxiv_id"]] = result


records_to_process = (
    records if LIMIT is None else records[:LIMIT]
)

for index, record in enumerate(records_to_process, start=1):
    arxiv_id = record["arxiv_id"]

    if arxiv_id in classifications:
        continue

    # First perform the category check.
    if "cond-mat.mtrl-sci" not in record["categories"]:
        result = {
            "arxiv_id": arxiv_id,
            "label": "reject",
            "reason": (
                "The record does not contain the "
                "cond-mat.mtrl-sci category."
            ),
            "method": "category_check",
        }
    else:
        result = classify_with_ollama(record)

    classifications[arxiv_id] = result

    # Save immediately so progress is not lost.
    with classifications_path.open(
        "a",
        encoding="utf-8",
    ) as file:
        file.write(
            json.dumps(result, ensure_ascii=False) + "\n"
        )

    print(
        f"[{index}/{len(records_to_process)}] "
        f"{arxiv_id}: {result['label']}"
    )


# Write records into separate files based on their labels.
kept_count = 0
rejected_count = 0
review_count = 0
category_rejected_count = 0

with (
    kept_path.open("w", encoding="utf-8") as kept_file,
    rejected_path.open("w", encoding="utf-8") as rejected_file,
    review_path.open("w", encoding="utf-8") as review_file,
):
    for record in records:
        result = classifications.get(record["arxiv_id"])

        # This record has not been classified yet.
        if result is None:
            continue

        output_record = {
            **record,
            "filter_label": result["label"],
            "filter_reason": result["reason"],
            "filter_method": result["method"],
        }

        line = json.dumps(
            output_record,
            ensure_ascii=False,
        ) + "\n"

        if result["label"] == "keep":
            kept_file.write(line)
            kept_count += 1

        elif result["label"] == "reject":
            rejected_file.write(line)
            rejected_count += 1

            if result["method"] == "category_check":
                category_rejected_count += 1

        else:
            review_file.write(line)
            review_count += 1


# Preserve the earlier deduplication counts.
if counts_path.exists():
    with counts_path.open("r", encoding="utf-8") as file:
        counts = json.load(file)
else:
    counts = {}

counts.update({
    "content_records_classified": len(classifications),
    "category_check_removed": category_rejected_count,
    "content_filter_kept": kept_count,
    "content_filter_rejected": rejected_count,
    "content_filter_needs_review": review_count,
})

with counts_path.open("w", encoding="utf-8") as file:
    json.dump(counts, file, indent=2)

print()
print(json.dumps(counts, indent=2))
