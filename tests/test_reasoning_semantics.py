from __future__ import annotations

from pathlib import Path

from trim.reasoning.evidence.global_evidence import build_default_global_evidence_output_dir
from trim.reasoning.semantics.feature_semantics import build_feature_semantics_map, describe_feature_name
from trim.reasoning.semantics.task_semantics import load_task_label_semantics


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
