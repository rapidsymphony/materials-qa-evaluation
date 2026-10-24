import json
import re
from pathlib import Path

input_path = Path("data/raw/abstracts.jsonl")
output_path = Path("data/processed/abstracts_deduplicated.jsonl")
counts_path = Path("data/processed/filter_counts.json")

output_path.parent.mkdir(parents=True, exist_ok=True)

seen_ids = set()
seen_abstracts = set()
kept_records = []

counts = {
    "initial_records": 0,
    "duplicate_arxiv_ids": 0,
    "duplicate_abstracts": 0,
    "records_after_deduplication": 0,
}

with input_path.open("r", encoding="utf-8") as file:
    for line in file:
        if not line.strip():
            continue

        record = json.loads(line)
        counts["initial_records"] += 1

        # Treat different versions of the same paper as one paper.
        arxiv_id = record["arxiv_id"]
        base_arxiv_id = re.sub(r"v\d+$", "", arxiv_id)

        # Ignore capitalization and whitespace when comparing abstracts.
        normalized_abstract = " ".join(
            record["abstract"].split()
        ).casefold()

        if base_arxiv_id in seen_ids:
            counts["duplicate_arxiv_ids"] += 1
            continue

        if normalized_abstract in seen_abstracts:
            counts["duplicate_abstracts"] += 1
            continue

        seen_ids.add(base_arxiv_id)
        seen_abstracts.add(normalized_abstract)
        kept_records.append(record)

counts["records_after_deduplication"] = len(kept_records)

with output_path.open("w", encoding="utf-8") as file:
    for record in kept_records:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")

with counts_path.open("w", encoding="utf-8") as file:
    json.dump(counts, file, indent=2)

print(json.dumps(counts, indent=2))
print(f"Saved deduplicated abstracts to {output_path}")