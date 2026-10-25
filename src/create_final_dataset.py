import json
from collections import Counter
from pathlib import Path


INPUT_PATH = Path("data/processed/qa_candidates.jsonl")
ABSTRACTS_PATH = Path("data/processed/abstracts_filtered.jsonl")
OUTPUT_PATH = Path("data/final/qa_dataset.jsonl")
REPORT_PATH = Path("data/final/curation_report.json")


# These audited pairs cannot be rewritten honestly into one of the requested
# dataset categories using only their source abstracts.
REMOVE_IDS = {
    "qa_0008",  # ML model target, not a material property
    "qa_0024",  # clustering method, not a synthesis condition
    "qa_0027",  # example systems are given, but no synthesis condition
    "qa_0151",  # spectroscopic sum rule, not a performance metric
    "qa_0184",  # stabilization theory does not fit a requested category
    "qa_0190",  # scope of a theory, not a synthesis condition
}


# Corrections are based only on statements in the corresponding abstract.
CORRECTIONS = {
    "qa_0025": {
        "question_type": "material_property",
        "question": "How does the Néel temperature of the vortex or anti-vortex phase in $A_3$V$_9$Te$_{13}$ depend on external magnetic fields?",
        "answer": "It has an extremely weak dependence on both the magnitude and direction of external magnetic fields.",
    },
    "qa_0036": {
        "question_type": "performance_metric",
        "question": "What percentage of equimolar BCC quaternaries have at least two unstable modes at 500 K?",
        "answer": "15.2%",
    },
    "qa_0041": {
        "question_type": "material_property",
        "question": "What full-band electronic features does the reciprocal-space framework uncover in the studied quasicrystals?",
    },
    "qa_0051": {
        "question_type": "not_stated",
        "answer": "Not stated",
        "supporting_passage": "",
        "is_answerable": False,
        "not_stated_reason": "The abstract says that a coil dipole field was used but gives no maximum magnetic-field strength.",
        "chemical_formulas": [],
    },
    "qa_0060": {
        "question_type": "synthesis_condition",
        "question": "What is the chemical formula of the undoped parent compound used as the model system?",
        "answer": "KSb3Mn9O19",
        "supporting_passage": "Here, we investigate the origin and evolution of cation distribution in the extensively studied M-type hexaferrite structure using the first Mn-based M-type hexaferrite, KSb3Mn9O19, as a model system.",
        "is_answerable": True,
        "not_stated_reason": None,
        "chemical_formulas": [
            {
                "original": "KSb3Mn9O19",
                "normalized": "KSb3Mn9O19",
                "unresolved": None,
            }
        ],
    },
    "qa_0144": {
        "question_type": "synthesis_condition",
        "question": "What is the chemical composition of the bulk moiré material studied?",
        "answer": "[Sr6TaS8]1+x[TaS2]8",
        "supporting_passage": "Here, we report the evidence of bulk superconductivity in single crystals of a recently reported bulk Moire material [Sr6TaS8]1+x[TaS2]8 at ambient pressure.",
        "is_answerable": True,
        "not_stated_reason": None,
        "chemical_formulas": [
            {
                "original": "[Sr6TaS8]1+x[TaS2]8",
                "normalized": None,
                "unresolved": "The composition contains the variable x rather than a fixed stoichiometry.",
            }
        ],
    },
    "qa_0152": {
        "question_type": "synthesis_condition",
        "question": "Which processing methods were used to fabricate the organic solar cells compared in the study?",
        "answer": "Spin coating and fully roll-to-roll-compatible gravure printing.",
        "supporting_passage": "Here, we compare spin-coated and fully roll-to-roll-compatible gravure-printed PM6:Y12 solar cells during $\\sim$1000 h of continuous illumination.",
        "is_answerable": True,
        "not_stated_reason": None,
        "chemical_formulas": [],
    },
    "qa_0155": {
        "question_type": "material_property",
        "question": "Which non-radiative recombination channel is shared across the FA$_{1-x}$Cs$_x$PbI$_3$ series and limits device performance?",
        "answer": "$Tα$",
    },
    "qa_0167": {
        "question_type": "material_property",
        "question": "How does the thermally averaged structure represent band-gap renormalization in Bi$_2$Se$_3$?",
        "answer": "It substantially underestimates the band-gap renormalization.",
    },
    "qa_0174": {
        "question_type": "material_property",
        "question": "What mechanism produces spontaneous twisting in GeSe_{2-x}Te_x nanowires?",
        "answer": "Preferred tilted stacking and twinning in van der Waals crystals.",
    },
    "qa_0180": {
        "question_type": "material_property",
        "question": "How does the dominant cracking mechanism in high-temperature creep change with stress level?",
        "answer": "Cracking is trans-granular-dominated at high stress, mixed at intermediate stress, and inter-granular-dominated at lower stress.",
        "supporting_passage": "The microscale computation reveals the transition from trans-granular-dominated cracking at high stress levels to mixed inter- and trans-granular cracking at intermediate stresses and inter-granular-dominated cracking at lower stresses, accompanied by distinct damage localization modes and the evolution of crack paths from grain boundary to grain-interior propagation.",
        "is_answerable": True,
        "not_stated_reason": None,
    },
    "qa_0196": {
        "question_type": "synthesis_condition",
        "question": "What is the chemical formula of the material studied?",
        "answer": "AlN",
        "supporting_passage": "AlN is a promising material for integrated quantum photonics due to its broad transparency window, its compatibility with CMOS technology, and the possibility to host localized light emitters acting as single photon sources.",
        "is_answerable": True,
        "not_stated_reason": None,
        "chemical_formulas": [
            {"original": "AlN", "normalized": "AlN", "unresolved": None}
        ],
    },
    "qa_0206": {
        "question_type": "not_stated",
        "question": "What numerical Fermi-level ranges produce nearly perfect insensitivity to defects in CoSi(001)?",
        "answer": "Not stated",
        "supporting_passage": "",
        "is_answerable": False,
        "not_stated_reason": "The abstract says that specific Fermi-level ranges exist but does not give their numerical bounds.",
        "chemical_formulas": [
            {"original": "CoSi", "normalized": "CoSi", "unresolved": None}
        ],
    },
    "qa_0221": {
        "question_type": "performance_metric",
    },
    "qa_0222": {
        "question_type": "material_property",
        "question": "How does the in-gap state in 1T-TaS2 evolve across heating and cooling cycles?",
        "answer": "It collapses abruptly on heating into the NC-CDW phase and re-emerges sharply on cooling into the C-CDW phase.",
    },
    "qa_0228": {
        "question_type": "synthesis_condition",
        "question": "What is the chemical formula of the material grown in the study?",
        "answer": "SnS",
        "supporting_passage": "Tin monosulfide (SnS) is a layered IV-VI semiconductor with strong in-plane anisotropy and promising properties for optoelectronic and ferroic applications.",
        "is_answerable": True,
        "not_stated_reason": None,
        "chemical_formulas": [
            {"original": "SnS", "normalized": "SnS", "unresolved": None}
        ],
    },
    "qa_0238": {
        "question_type": "not_stated",
        "answer": "Not stated",
        "supporting_passage": "",
        "is_answerable": False,
        "not_stated_reason": "The abstract says that layer thickness was optimized but does not report the optimized thickness value.",
    },
}


def read_jsonl(path):
    with path.open("r", encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def write_jsonl(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")


def validate(records, abstracts):
    allowed_types = {
        "material_property",
        "synthesis_condition",
        "performance_metric",
        "not_stated",
    }
    errors = []
    seen_ids = set()
    seen_questions = set()

    for record in records:
        qa_id = record["qa_id"]
        abstract = abstracts[record["arxiv_id"]]
        normalized_question = " ".join(record["question"].casefold().split())

        if record.get("source_abstract") != abstract:
            errors.append(f"{qa_id}: embedded source abstract does not match")

        if qa_id in seen_ids:
            errors.append(f"{qa_id}: duplicate QA ID")
        if normalized_question in seen_questions:
            errors.append(f"{qa_id}: duplicate question")
        if record["question_type"] not in allowed_types:
            errors.append(f"{qa_id}: invalid question type")

        seen_ids.add(qa_id)
        seen_questions.add(normalized_question)

        if record["question_type"] == "not_stated":
            if record["answer"] != "Not stated":
                errors.append(f"{qa_id}: invalid abstention answer")
            if record["supporting_passage"]:
                errors.append(f"{qa_id}: abstention has a supporting passage")
            if not record.get("not_stated_reason"):
                errors.append(f"{qa_id}: abstention has no reason")
            if record.get("is_answerable") is not False:
                errors.append(f"{qa_id}: abstention marked answerable")
        else:
            passage = record["supporting_passage"]
            if not passage or passage not in abstract:
                errors.append(f"{qa_id}: passage is not an exact abstract substring")
            if record.get("not_stated_reason") is not None:
                errors.append(f"{qa_id}: answerable pair has an abstention reason")
            if record.get("is_answerable") is not True:
                errors.append(f"{qa_id}: answerable pair marked unanswerable")

        pair_text = " ".join(
            [record["question"], record["answer"], record["supporting_passage"]]
        )
        for formula in record.get("chemical_formulas", []):
            original = formula.get("original")
            if not original or original not in abstract:
                errors.append(f"{qa_id}: formula is absent from abstract: {original}")
            if original not in pair_text:
                errors.append(f"{qa_id}: formula is unused in pair: {original}")
            if bool(formula.get("normalized")) == bool(formula.get("unresolved")):
                errors.append(f"{qa_id}: formula metadata has an invalid state: {original}")

    if errors:
        raise ValueError("Final dataset validation failed:\n" + "\n".join(errors))


def main():
    candidates = read_jsonl(INPUT_PATH)
    abstracts = {
        paper["arxiv_id"]: paper["abstract"]
        for paper in read_jsonl(ABSTRACTS_PATH)
    }

    final_records = []
    for record in candidates:
        if record["qa_id"] in REMOVE_IDS:
            continue

        updated = dict(record)
        correction = CORRECTIONS.get(record["qa_id"])
        if correction:
            updated.update(correction)

        updated["source_abstract"] = abstracts[updated["arxiv_id"]]

        final_records.append(updated)

    validate(final_records, abstracts)
    write_jsonl(OUTPUT_PATH, final_records)

    report = {
        "input_pairs": len(candidates),
        "corrected_pairs": len(CORRECTIONS),
        "removed_pairs": len(REMOVE_IDS),
        "removed_qa_ids": sorted(REMOVE_IDS),
        "final_pairs": len(final_records),
        "question_type_counts": dict(
            sorted(Counter(row["question_type"] for row in final_records).items())
        ),
        "source_audit": "data/processed/qa_audit_reviewed.jsonl",
    }
    REPORT_PATH.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
