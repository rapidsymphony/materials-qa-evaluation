import asyncio
import json
import os
import random
from collections import Counter
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI


MISTRAL_BASE_URL = "https://api.mistral.ai/v1"
MODEL = "mistral-small-latest"

TARGETS = {
    "material_property": 70,
    "synthesis_condition": 60,
    "performance_metric": 60,
    "not_stated": 50,
}

INPUT_PATH = Path("data/processed/abstracts_filtered.jsonl")
OUTPUT_PATH = Path("data/processed/qa_candidates.jsonl")


def read_jsonl(path):
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def make_prompt(paper, question_type):
    return f"""
Create one evidence-grounded QA pair from this materials-science abstract.
The required question type is: {question_type}

Type definitions:
- material_property: an explicitly stated physical, chemical, structural,
  optical, electrical, magnetic, mechanical, or thermal property.
- synthesis_condition: an explicitly stated preparation, fabrication, growth,
  treatment, composition, temperature, pressure, duration, or process condition.
- performance_metric: an explicitly stated performance result for a material or
  material-based device.
- not_stated: a relevant question whose answer is absent from the abstract.

Use only the abstract. Do not use outside knowledge or unsupported inference.
For an answerable question, copy supporting_passage character-for-character
from one contiguous part of the abstract. If the abstract cannot support the
requested answerable type, return {{"skip": true}}.

For not_stated, answer exactly "Not stated", use an empty supporting_passage,
and explain what is missing in not_stated_reason.

Preserve chemical formulas exactly. chemical_formulas must be a list. For each
formula used in the question, answer, or passage, record:
{{"original": "source form", "normalized": null, "unresolved": null}}
Add a normalized form only when unambiguous. Otherwise explain the ambiguity in
unresolved. Use an empty list when no formula appears in the pair.

Return only JSON:
{{
  "skip": false,
  "question": "...",
  "answer": "...",
  "supporting_passage": "...",
  "not_stated_reason": null,
  "chemical_formulas": []
}}

Title: {paper["title"]}
Abstract: {paper["abstract"]}
""".strip()


async def main():
    load_dotenv()
    api_key = os.getenv("MISTRAL_API_KEY")

    if not api_key:
        raise RuntimeError("MISTRAL_API_KEY is not set")

    client = AsyncOpenAI(
        base_url=MISTRAL_BASE_URL,
        api_key=api_key,
    )

    papers = read_jsonl(INPUT_PATH)
    random.Random(42).shuffle(papers)

    existing = read_jsonl(OUTPUT_PATH)
    counts = Counter(pair["question_type"] for pair in existing)
    used_papers = {pair["arxiv_id"] for pair in existing}
    seen_questions = {
        " ".join(pair["question"].casefold().split())
        for pair in existing
    }
    next_id = len(existing) + 1

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open("a", encoding="utf-8") as output_file:
        for paper in papers:
            remaining = {
                name: target - counts[name]
                for name, target in TARGETS.items()
                if counts[name] < target
            }

            if not remaining:
                break

            if paper["arxiv_id"] in used_papers:
                continue

            question_type = max(remaining, key=remaining.get)
            print(f"{paper['arxiv_id']} -> {question_type}")

            response = await client.chat.completions.create(
                model=MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": make_prompt(paper, question_type),
                    }
                ],
                temperature=0,
                response_format={"type": "json_object"},
            )

            result = json.loads(response.choices[0].message.content)

            if result.get("skip") is True:
                continue

            question = result.get("question", "").strip()
            answer = result.get("answer", "").strip()
            passage = result.get("supporting_passage", "").strip()
            normalized_question = " ".join(question.casefold().split())
            is_not_stated = question_type == "not_stated"

            if not question or not answer:
                continue

            if normalized_question in seen_questions:
                continue

            if is_not_stated:
                reason = result.get("not_stated_reason")
                if answer.casefold() != "not stated" or passage or not reason:
                    continue
            else:
                reason = None
                if not passage or passage not in paper["abstract"]:
                    continue

            record = {
                "qa_id": f"qa_{next_id:04d}",
                "arxiv_id": paper["arxiv_id"],
                "source_title": paper["title"],
                "question_type": question_type,
                "question": question,
                "answer": answer,
                "supporting_passage": passage,
                "is_answerable": not is_not_stated,
                "not_stated_reason": reason,
                "chemical_formulas": result.get("chemical_formulas", []),
                "generation_model": MODEL,
            }

            output_file.write(json.dumps(record, ensure_ascii=False) + "\n")
            output_file.flush()

            counts[question_type] += 1
            seen_questions.add(normalized_question)
            used_papers.add(paper["arxiv_id"])
            next_id += 1

    print("Final counts:")
    print(json.dumps(dict(counts), indent=2))


if __name__ == "__main__":
    asyncio.run(main())
