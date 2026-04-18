from __future__ import annotations

from pathlib import Path

from trim.reasoning.agent_tools.manifests import build_all_task_tool_manifests, load_task_tool_manifest
from trim.utils.io import load_json, save_pickle


def test_agent_tool_manifests_save_relative_paths_and_load_resolved_paths(tmp_path: Path, monkeypatch):
    import trim.reasoning.agent_tools.manifests as manifests_module
    import trim.utils.paths as paths_module

    monkeypatch.setattr(paths_module, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(manifests_module, "PROJECT_ROOT", tmp_path)

    outputs_root = tmp_path / "outputs"
    manifest_root = outputs_root / "reasoning_agent_tools" / "manifests"
    feature_set_name = "fg_top_level+rdkit_descriptors_and_pka_easy_to_NLP_Lv1_core_pka_no_fr_counts"
    task = "AMES"

    global_bundle_path = (
        outputs_root
        / "models"
        / "global_ebm"
        / "all_tasks_njobs16_parallel_core_pka_no_fr_keep_nan"
        / task
        / feature_set_name
        / "model_bundle.pkl"
    )
    pos_bundle_path = (
        outputs_root
        / "models"
        / "pair_ebm"
        / "all_tasks_topk4_same_scaffold_njobs16_fg_plus_rdkit_core_pka_no_fr_counts"
        / task
        / feature_set_name
        / "pos_model_bundle.pkl"
    )
    neg_bundle_path = pos_bundle_path.with_name("neg_model_bundle.pkl")

    save_pickle(global_bundle_path, {"feature_columns": ["rdkit_pka__rdkit__MolWt"]})
    save_pickle(pos_bundle_path, {"raw_feature_columns": ["rdkit_pka__rdkit__MolWt"]})
    save_pickle(neg_bundle_path, {"raw_feature_columns": ["rdkit_pka__rdkit__MolWt"]})

    summary = build_all_task_tool_manifests(
        tasks=[task],
        feature_set_name=feature_set_name,
        dataset_root="data/processed/tdc_no_conflict_labels_salt_removed",
        cache_root="data/cache/tdc_mol_fingerprints",
        outputs_root=outputs_root,
        manifest_root=manifest_root,
    )

    manifest_path = manifest_root / feature_set_name / f"{task}.json"
    saved_manifest = load_json(manifest_path)
    saved_bundle_paths = dict(saved_manifest["bundle_paths"])

    assert saved_manifest["dataset_root"] == "data/processed/tdc_no_conflict_labels_salt_removed"
    assert saved_manifest["cache_root"] == "data/cache/tdc_mol_fingerprints"
    assert saved_bundle_paths["global_bundle_path"].startswith("outputs/models/global_ebm/")
    assert saved_bundle_paths["pos_bundle_path"].startswith("outputs/models/pair_ebm/")
    assert saved_bundle_paths["neg_bundle_path"].startswith("outputs/models/pair_ebm/")

    loaded_manifest = load_task_tool_manifest(
        task=task,
        feature_set_name=feature_set_name,
        manifest_root=manifest_root,
    )
    loaded_bundle_paths = dict(loaded_manifest["bundle_paths"])

    assert loaded_manifest["dataset_root"] == "data/processed/tdc_no_conflict_labels_salt_removed"
    assert loaded_manifest["cache_root"] == "data/cache/tdc_mol_fingerprints"
    assert loaded_bundle_paths["global_bundle_path"] == str(global_bundle_path)
    assert loaded_bundle_paths["pos_bundle_path"] == str(pos_bundle_path)
    assert loaded_bundle_paths["neg_bundle_path"] == str(neg_bundle_path)

    assert summary["tasks"][0]["manifest_path"] == str(Path("outputs/reasoning_agent_tools/manifests") / feature_set_name / f"{task}.json")
