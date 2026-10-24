import json
import re
import shutil
from pathlib import Path


QA_PATH = Path("data/processed/qa_candidates.jsonl")
ABSTRACTS_PATH = Path("data/processed/abstracts_filtered.jsonl")
BACKUP_PATH = Path("data/processed/qa_candidates_before_formula_cleanup.jsonl")
REPORT_PATH = Path("data/processed/formula_cleanup_report.json")


# These cases need a human decision because the generated formula either came
# from the title, was not a chemical formula, or did not match the abstract.
PATCHES = {
    "qa_0004": {"chemical_formulas": []},
    "qa_0005": {
        "chemical_formulas": [
            {
                "original": "Mo4TGa16Ge",
                "normalized": None,
                "unresolved": "T is a variable site occupied by Co, Rh, or Ir.",
            }
        ]
    },
    "qa_0009": {"chemical_formulas": []},
    "qa_0025": {
        "chemical_formulas": [
            {
                "original": "$A_3$V$_9$Te$_{13}$",
                "normalized": "A3V9Te13",
                "unresolved": None,
            }
        ]
    },
    "qa_0038": {
        "question": "What is the effective second-harmonic generation (SHG) response magnitude of the nanoporous photonic metamaterial when the channels are filled with benzil and solidify independently?",
        "chemical_formulas": [],
    },
    "qa_0047": {
        "question": "What fraction of transferred carbon is retained in chains at 1273 K during zirconium carbide oxidation?",
        "chemical_formulas": [],
    },
    "qa_0069": {"chemical_formulas": []},
    "qa_0071": {"chemical_formulas": []},
    "qa_0074": {"chemical_formulas": []},
    "qa_0085": {"chemical_formulas": []},
    "qa_0101": {
        "question": "What magnetic property does NbFeTe$_2$ exhibit in thin-film form?",
        "chemical_formulas": [
            {
                "original": "NbFeTe$_2$",
                "normalized": "NbFeTe2",
                "unresolved": None,
            }
        ],
    },
    "qa_0104": {
        "question": "What performance metric is reported for the interfacial magnetism induced in monolayer FePS$_3$ by the gold film?",
        "chemical_formulas": [
            {
                "original": "FePS$_3$",
                "normalized": "FePS3",
                "unresolved": None,
            }
        ],
    },
    "qa_0109": {
        "question": "What material property is enhanced by Zr clustering in Ba(Zr$_x$Ti$_{1-x}$)O$_3$?",
        "chemical_formulas": [
            {
                "original": "Ba(Zr$_x$Ti$_{1-x}$)O$_3$",
                "normalized": None,
                "unresolved": "The composition contains the variable x rather than a fixed stoichiometry.",
            }
        ],
    },
    "qa_0111": {"chemical_formulas": []},
    "qa_0117": {"chemical_formulas": []},
    "qa_0129": {
        "question": "How stable were the tested machine-learning potentials during molecular dynamics simulations of the cadmium selenide nanocluster?",
        "chemical_formulas": [],
    },
    "qa_0157": {
        "question": "What magnetic anisotropy is reported for YbMn$_\\text{6}$Sn$_\\text{6}$?",
        "chemical_formulas": [
            {
                "original": "YbMn$_\\text{6}$Sn$_\\text{6}$",
                "normalized": "YbMn6Sn6",
                "unresolved": None,
            }
        ],
    },
    "qa_0170": {
        "chemical_formulas": [
            {
                "original": "Li$_x$CoO$_2$",
                "normalized": "LixCoO2",
                "unresolved": None,
            }
        ]
    },
    "qa_0191": {
        "question": "What maximum relative luminescence brightness is achieved under X-ray excitation for Mn-doped ZnGa$_2$O$_4$ nanocrystals?",
        "chemical_formulas": [
            {
                "original": "ZnGa$_2$O$_4$",
                "normalized": "ZnGa2O4",
                "unresolved": None,
            },
            {"original": "Mn", "normalized": "Mn", "unresolved": None},
        ],
    },
    "qa_0195": {
        "question": "What magnetoelastic response is reported for Al-rich Co Fe Al films?",
        "chemical_formulas": [],
    },
    "qa_0229": {
        "question": "What internal electric field does the phase-field model quantitatively capture in Hf0.5Zr0.5O2?",
        "answer": "0.55 MV/cm",
        "supporting_passage": "The impact of defects is further corroborated through phase-field modeling(PFM), which only recreates the coercive fields, FORC, and internal bias for defect densities and tunneling barrier heights that are consistent with experiment, quantitatively capturing an internal electric field of 0.55 MV/cm.",
        "chemical_formulas": [
            {
                "original": "Hf0.5Zr0.5O2",
                "normalized": "Hf0.5Zr0.5O2",
                "unresolved": None,
            }
        ],
    },
}


def read_jsonl(path):
    with path.open("r", encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def write_jsonl(path, records):
    with path.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")


def pair_text(pair):
    return " ".join(
        [pair["question"], pair["answer"], pair["supporting_passage"]]
    )


def has_variable_composition(formula, unresolved):
    explanation = (unresolved or "").casefold()
    if any(word in explanation for word in ("variable", "unspecified", "ambigu")):
        return True
    return bool(re.search(r"(?:_|\{|-)\s*[xyzδ]", formula, re.IGNORECASE))


def clean_formulas(pair, abstract, counters):
    cleaned = []

    for formula in pair.get("chemical_formulas", []):
        original = str(formula.get("original") or "").strip()
        normalized = formula.get("normalized")
        unresolved = formula.get("unresolved")

        if not original or original not in abstract:
            counters["metadata_entries_removed"] += 1
            continue

        # If the model used a plain normalized form in the question or answer,
        # restore the exact source form. Supporting passages are never altered.
        if original not in pair_text(pair) and normalized:
            for field in ("question", "answer"):
                if normalized in pair[field]:
                    pair[field] = pair[field].replace(normalized, original)
                    counters["source_format_restorations"] += 1

        if original not in pair_text(pair):
            counters["metadata_entries_removed"] += 1
            continue

        normalized = str(normalized).strip() if normalized else None
        unresolved = str(unresolved).strip() if unresolved else None

        # Each retained entry gets either an unambiguous normalized form or an
        # explanation of why normalization is unresolved, but never both.
        if normalized and unresolved:
            if has_variable_composition(original, unresolved):
                normalized = None
            else:
                unresolved = None
            counters["normalization_states_fixed"] += 1
        elif not normalized and not unresolved:
            if re.fullmatch(r"[A-Za-z0-9().+\-]+", original):
                normalized = original
            else:
                unresolved = "No unambiguous plain-text normalization was recorded."
            counters["normalization_states_fixed"] += 1

        cleaned.append(
            {
                "original": original,
                "normalized": normalized,
                "unresolved": unresolved,
            }
        )

    pair["chemical_formulas"] = cleaned


def main():
    if not BACKUP_PATH.exists():
        shutil.copy2(QA_PATH, BACKUP_PATH)

    # Always rebuild from the untouched backup so repeated runs give the same
    # dataset and report.
    pairs = read_jsonl(BACKUP_PATH)
    papers = {paper["arxiv_id"]: paper for paper in read_jsonl(ABSTRACTS_PATH)}

    counters = {
        "pairs_read": len(pairs),
        "pairs_with_targeted_edits": 0,
        "questions_or_answers_changed": 0,
        "supporting_passages_changed": 0,
        "formula_entries_before": sum(
            len(pair.get("chemical_formulas", [])) for pair in pairs
        ),
        "formula_entries_after": 0,
        "metadata_entries_removed": 0,
        "source_format_restorations": 0,
        "normalization_states_fixed": 0,
    }
    changed_ids = []

    for pair in pairs:
        before = json.dumps(pair, ensure_ascii=False, sort_keys=True)
        old_question = pair["question"]
        old_answer = pair["answer"]
        old_passage = pair["supporting_passage"]

        patch = PATCHES.get(pair["qa_id"])
        if patch:
            pair.update(patch)
            counters["pairs_with_targeted_edits"] += 1

        paper = papers.get(pair["arxiv_id"])
        if paper is None:
            raise ValueError(f"Missing source abstract for {pair['qa_id']}")

        clean_formulas(pair, paper["abstract"], counters)

        if pair["question"] != old_question or pair["answer"] != old_answer:
            counters["questions_or_answers_changed"] += 1
        if pair["supporting_passage"] != old_passage:
            counters["supporting_passages_changed"] += 1
        if json.dumps(pair, ensure_ascii=False, sort_keys=True) != before:
            changed_ids.append(pair["qa_id"])

    counters["formula_entries_after"] = sum(
        len(pair.get("chemical_formulas", [])) for pair in pairs
    )
    counters["formula_entries_removed_total"] = (
        counters["formula_entries_before"] - counters["formula_entries_after"]
    )
    counters["pairs_changed"] = len(changed_ids)
    counters["changed_qa_ids"] = changed_ids

    write_jsonl(QA_PATH, pairs)
    REPORT_PATH.write_text(
        json.dumps(counters, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(counters, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
