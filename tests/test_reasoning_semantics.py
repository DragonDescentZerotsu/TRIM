from __future__ import annotations

from pathlib import Path

from trim.reasoning.evidence.global_evidence import build_default_global_evidence_output_dir
from trim.reasoning.semantics.feature_semantics import build_feature_semantics_map, describe_feature_name
from trim.reasoning.semantics.task_semantics import (
    BRIEF_TASK_SEMANTICS_BY_TASK,
    load_brief_task_semantics,
    load_task_label_semantics,
)


def test_describe_feature_name_for_rdkit_and_fg_features():
    tpsa = describe_feature_name("rdkit_pka__rdkit__TPSA")
    assert tpsa["display_name"] == "topological polar surface area"
    assert tpsa["source_family"] == "rdkit"

    fg = describe_feature_name("fg_top_level__carboxylic acid")
    assert fg["display_name"] == "carboxylic acid"
    assert fg["source_family"] == "fg_top_level"


def test_build_feature_semantics_map_assigns_nlp_readiness():
    semantics_map = build_feature_semantics_map(
        [
            "rdkit_pka__rdkit__TPSA",
            "rdkit_pka__rdkit__BCUT2D_CHGLO",
            "fg_top_level__carboxylic acid",
        ]
    )
    assert semantics_map["rdkit_pka__rdkit__TPSA"]["nlp_readiness"] == "natural_language_ready"
    assert semantics_map["rdkit_pka__rdkit__BCUT2D_CHGLO"]["nlp_readiness"] == "too_technical_for_direct_reasoning"
    assert semantics_map["fg_top_level__carboxylic acid"]["nlp_readiness"] == "natural_language_ready"


def test_load_task_label_semantics_from_custom_prompt_root(tmp_path: Path):
    prompt_root = tmp_path / "prompts"
    prompt_root.mkdir()
    prompt_path = prompt_root / "BBB_Martins.jsonl"
    prompt_path.write_text(
        '{"text":"Choose the correct label: (A) does not cross the BBB (B) crosses the BBB\\nDrug SMILES: CC"}\n',
        encoding="utf-8",
    )

    payload = load_task_label_semantics("BBB_Martins", prompt_root=prompt_root)
    assert payload is not None
    assert payload[0]["option"] == "A"
    assert payload[1]["text"] == "crosses the BBB"


def test_brief_task_semantics_cover_default_sixteen_tasks():
    assert set(BRIEF_TASK_SEMANTICS_BY_TASK) == {
        "AMES",
        "BBB_Martins",
        "Bioavailability_Ma",
        "CYP2C9_Substrate_CarbonMangels",
        "CYP2D6_Substrate_CarbonMangels",
        "CYP3A4_Substrate_CarbonMangels",
        "Carcinogens_Lagunin",
        "ClinTox",
        "DILI",
        "HIA_Hou",
        "PAMPA_NCATS",
        "Pgp_Broccatelli",
        "SARSCoV2_3CLPro_Diamond",
        "SARSCoV2_Vitro_Touret",
        "Skin_Reaction",
        "hERG",
    }
    assert load_brief_task_semantics("AMES") == "mutagenicity (not mutagenic or mutagenic)"
    assert load_brief_task_semantics("Bioavailability_Ma") == "oral bioavailability (<20% or >=20%)"


def test_brief_task_semantics_falls_back_to_label_semantics(tmp_path: Path):
    prompt_root = tmp_path / "prompts"
    prompt_root.mkdir()
    prompt_path = prompt_root / "NewTask.jsonl"
    prompt_path.write_text(
        '{"text":"Choose the correct label: (A) is low risk (B) is high risk\\nDrug SMILES: CC"}\n',
        encoding="utf-8",
    )

    assert load_brief_task_semantics("NewTask", prompt_root=prompt_root) == "whether it is low risk or is high risk"


def test_build_default_global_evidence_output_dir():
    bundle_path = Path(
        "outputs/models/global_ebm/all_tasks_njobs16_parallel/BBB_Martins/"
        "fg_top_level+rdkit_descriptors_and_pka_easy_to_NLP_Lv1/model_bundle.pkl"
    )
    output_dir = build_default_global_evidence_output_dir(bundle_path=bundle_path, split="valid")
    assert output_dir.parts[-4:] == (
        "all_tasks_njobs16_parallel",
        "BBB_Martins",
        "fg_top_level+rdkit_descriptors_and_pka_easy_to_NLP_Lv1",
        "valid",
    )
