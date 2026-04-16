from __future__ import annotations

from pathlib import Path

from trim.playbook_prompt import (
    build_feature_list,
    build_task_description,
    load_task_names_from_manifest_index,
    load_feature_names_from_config,
    render_playbook_research_prompt,
    render_playbook_research_prompts_for_tasks,
)


def test_load_default_playbook_feature_scope_has_expected_size():
    feature_names = load_feature_names_from_config(
        Path("configs/features/rdkit_descriptors_and_pka_easy_to_NLP_Lv1_core_pka_no_fr_counts.json")
    )
    assert len(feature_names) == 36
    assert "rdkit_pka__rdkit__TPSA" in feature_names
    assert "rdkit_pka__pka__fraction_neutral" in feature_names


def test_feature_list_uses_human_readable_names_instead_of_raw_feature_ids():
    rendered = build_feature_list(
        [
            "rdkit_pka__rdkit__TPSA",
            "rdkit_pka__pka__fraction_neutral",
        ]
    )
    assert "topological polar surface area" in rendered
    assert "neutral fraction" in rendered
    assert "rdkit_pka__rdkit__TPSA" not in rendered
    assert "estimated fraction of the molecule that is neutral" in rendered


def test_task_description_falls_back_to_loaded_label_semantics():
    description = build_task_description("BBB_Martins", explicit_description=None)
    assert "BBB_Martins" in description
    assert "option (A)" in description
    assert "option (B)" in description


def test_rendered_prompt_requests_functional_group_notes_and_avoids_trim_specific_meta_language():
    rendered = render_playbook_research_prompt(task="BBB_Martins")
    assert "TRIM" not in rendered
    assert "rewriting" not in rendered
    assert "internal feature ID" not in rendered
    assert "## Functional-group notes" in rendered
    assert "topological polar surface area" in rendered
    assert "rdkit_pka__rdkit__TPSA" not in rendered


def test_load_task_names_from_manifest_index(tmp_path: Path):
    manifest_index = tmp_path / "manifest_index.json"
    manifest_index.write_text(
        '{\n  "tasks": [\n    {"task": "BBB_Martins"},\n    {"task": "AMES"}\n  ]\n}\n',
        encoding="utf-8",
    )
    assert load_task_names_from_manifest_index(manifest_index) == ["BBB_Martins", "AMES"]


def test_render_playbook_research_prompts_for_tasks_writes_summary_and_outputs(tmp_path: Path):
    summary = render_playbook_research_prompts_for_tasks(
        tasks=["BBB_Martins", "AMES"],
        output_root=tmp_path,
    )
    assert summary["num_tasks"] == 2
    assert (tmp_path / "BBB_Martins" / "deepresearch_threshold_playbook_prompt_filled.md").exists()
    assert (tmp_path / "AMES" / "deepresearch_threshold_playbook_prompt_filled.md").exists()
    assert (tmp_path / "render_summary.json").exists()
