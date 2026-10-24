import feedparser
import requests
import json
from pathlib import Path
import time

API_URL = "https://export.arxiv.org/api/query"

TOTAL_RESULTS = 1500
BATCH_SIZE = 10
REQUEST_DELAY = 3
MAX_RETRIES = 5

headers = {
    "User-Agent": (
        "materials-qa-evaluation/0.1 "
        "(https://github.com/rapidsymphony/materials-qa-evaluation)"
    )
}

output_path = Path("data/raw/abstracts.jsonl")
output_path.parent.mkdir(parents=True, exist_ok=True)

# Read abstracts already saved so the script can resume.
existing_ids = set()
processed_count = 0

if output_path.exists():
    with output_path.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                record = json.loads(line)
                existing_ids.add(record["arxiv_id"])
                processed_count += 1

saved_count = len(existing_ids)
start = processed_count

print(f"Already have {saved_count} abstracts")

while saved_count < TOTAL_RESULTS:
    batch_size = min(BATCH_SIZE, TOTAL_RESULTS - saved_count)

    params = {
        "search_query": "cat:cond-mat.mtrl-sci",
        "start": start,
        "max_results": batch_size,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }

    # Retry the request if arXiv is busy or rate-limits us.
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(
                API_URL,
                params=params,
                headers=headers,
                timeout=60,
            )

            if response.status_code == 429:
                wait_seconds = 30 * attempt
                print(
                    f"Rate limited. Waiting {wait_seconds} seconds..."
                )
                time.sleep(wait_seconds)
                continue

            response.raise_for_status()
            break

        except requests.exceptions.RequestException as error:
            if attempt == MAX_RETRIES:
                raise

            wait_seconds = 30 * attempt
            print(
                f"Request failed: {error}"
            )
            print(
                f"Waiting {wait_seconds} seconds before retrying..."
            )
            time.sleep(wait_seconds)
    else:
        raise RuntimeError("Could not retrieve this batch from arXiv")

    feed = feedparser.parse(response.content)

    if not feed.entries:
        raise RuntimeError(
            f"arXiv returned no entries for start={start}"
        )

    new_records = []

    for entry in feed.entries:
        arxiv_id = entry.id.rsplit("/", 1)[-1]

        if arxiv_id in existing_ids:
            continue

        record = {
            "arxiv_id": arxiv_id,
            "title": entry.title.strip(),
            "abstract": entry.summary.strip(),
            "published": entry.get("published", ""),
            "updated": entry.get("updated", ""),
            "authors": [
                author.name for author in entry.get("authors", [])
            ],
            "categories": [
                tag.term for tag in entry.get("tags", [])
            ],
            "source_url": entry.id,
        }

        new_records.append(record)
        existing_ids.add(arxiv_id)

    # Append each completed batch immediately.
    with output_path.open("a", encoding="utf-8") as file:
        for record in new_records:
            file.write(
                json.dumps(record, ensure_ascii=False) + "\n"
            )

    start += len(feed.entries)
    saved_count += len(new_records)

    print(f"Saved {saved_count}/{TOTAL_RESULTS} abstracts")

    if saved_count < TOTAL_RESULTS:
        time.sleep(REQUEST_DELAY)

print(f"Finished. Dataset saved to {output_path}")