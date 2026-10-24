import json
import random

with open("data/processed/qa_candidates.jsonl", encoding="utf-8") as file:
    pairs = [json.loads(line) for line in file if line.strip()]

sample = random.Random(42).sample(pairs, 50)

with open("data/processed/qa_audit_sample.jsonl", "w", encoding="utf-8") as file:
    for pair in sample:
        pair["audit_label"] = None
        pair["audit_notes"] = ""
        file.write(json.dumps(pair, ensure_ascii=False) + "\n")