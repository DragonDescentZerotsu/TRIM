from __future__ import annotations

import os
from pathlib import Path

from trim.reasoning.agent_tools.tools import TaskReasoningAgentTools
from trim.utils.io import save_json


def _write_stub_file(path: Path, contents: str = "stub") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contents, encoding="utf-8")
    return path


def _build_fake_tool_runner(tmp_path: Path) -> TaskReasoningAgentTools:
    bundle_root = tmp_path / "bundles"
    global_bundle = _write_stub_file(bundle_root / "global.pkl", "global")
    pos_bundle = _write_stub_file(bundle_root / "pos.pkl", "pos")
    neg_bundle = _write_stub_file(bundle_root / "neg.pkl", "neg")

    similarity_root = tmp_path / "similarity"
    for family in ("Morgan_similarity", "Feature_Morgan_similarity"):
        for split in ("train", "valid", "test"):
            _write_stub_file(
                similarity_root / family / "by_task" / "BBB_Martins" / f"{split}_similarity.pkl",
                f"{family}-{split}",
            )

    tools = TaskReasoningAgentTools.__new__(TaskReasoningAgentTools)
    tools.task = "BBB_Martins"
    tools.feature_set_name = "core_pka_no_fr"
    tools.manifest = {
        "schema_version": "manifest_v1",
        "bundle_paths": {
            "global_bundle_path": str(global_bundle),
            "pos_bundle_path": str(pos_bundle),
            "neg_bundle_path": str(neg_bundle),
        },
        "global_tool": {"top_k_per_sample": 6, "dense_feature_names": ["a"]},
        "local_tool": {"top_k_pos": 3, "top_k_neg": 3, "top_term_k_per_neighbor": 6},
    }
    tools.cache_root = similarity_root
    tools.tool_cache_root = tmp_path / "tool_cache"
    tools.enable_tool_cache = True
    tools._tool_payload_cache = {}
    tools._compatible_tool_cache_path_cache = {}
    tools._resolved_smiles_cache = {}
    tools._tool_cache_namespace = tools._build_tool_cache_namespace()
    return tools


def test_tool_payload_cache_round_trip_uses_disk_cache(tmp_path: Path):
    tools = _build_fake_tool_runner(tmp_path)
    payload = {
        "tool_name": "get_mol_properties_and_fg",
        "task": "BBB_Martins",
        "smiles": "CCO",
        "features": [],
    }

    tools._store_cached_tool_payload(
        tool_name="get_mol_properties_and_fg",
        smiles="CCO",
        payload=payload,
    )

    cache_path = tools._tool_cache_path(tool_name="get_mol_properties_and_fg", smiles="CCO")
    signature_path = cache_path.parents[1] / "cache_signature.json"
    assert cache_path.exists()
    assert signature_path.exists()

    tools._tool_payload_cache = {}
    loaded_payload = tools._load_cached_tool_payload(tool_name="get_mol_properties_and_fg", smiles="CCO")
    assert loaded_payload == payload


def test_compare_tool_payload_cache_is_partitioned_by_neighbors_per_label(tmp_path: Path):
    tools = _build_fake_tool_runner(tmp_path)
    payload_one = {
        "tool_name": "compare_similar_mols",
        "task": "BBB_Martins",
        "smiles": "CCO",
        "neighbors_per_label": 1,
        "positive_neighbors": ["p1"],
        "negative_neighbors": ["n1"],
    }
    payload_two = {
        "tool_name": "compare_similar_mols",
        "task": "BBB_Martins",
        "smiles": "CCO",
        "neighbors_per_label": 2,
        "positive_neighbors": ["p1", "p2"],
        "negative_neighbors": ["n1", "n2"],
    }

    tools._store_cached_tool_payload(
        tool_name="compare_similar_mols",
        smiles="CCO",
        payload=payload_one,
        neighbors_per_label=1,
    )
    tools._store_cached_tool_payload(
        tool_name="compare_similar_mols",
        smiles="CCO",
        payload=payload_two,
        neighbors_per_label=2,
    )

    path_one = tools._tool_cache_path(
        tool_name="compare_similar_mols",
        smiles="CCO",
        cache_variant="neighbors_per_label_1",
    )
    path_two = tools._tool_cache_path(
        tool_name="compare_similar_mols",
        smiles="CCO",
        cache_variant="neighbors_per_label_2",
    )
    assert path_one.exists()
    assert path_two.exists()
    assert path_one != path_two

    tools._tool_payload_cache = {}
    assert (
        tools._load_cached_tool_payload(
            tool_name="compare_similar_mols",
            smiles="CCO",
            neighbors_per_label=1,
        )
        == payload_one
    )
    assert (
        tools._load_cached_tool_payload(
            tool_name="compare_similar_mols",
            smiles="CCO",
            neighbors_per_label=2,
        )
        == payload_two
    )


def test_compare_tool_payload_cache_reads_legacy_default_neighbor_cache_only_for_default(tmp_path: Path):
    tools = _build_fake_tool_runner(tmp_path)
    payload = {
        "tool_name": "compare_similar_mols",
        "task": "BBB_Martins",
        "smiles": "CCO",
        "positive_neighbors": ["p1", "p2", "p3"],
        "negative_neighbors": ["n1", "n2", "n3"],
    }
    smiles_digest = tools._smiles_cache_digest("CCO")
    legacy_path = (
        tools.tool_cache_root
        / tools.feature_set_name
        / tools.task
        / "legacy_namespace"
        / "compare_similar_mols"
        / f"{smiles_digest}.json"
    )
    save_json(
        legacy_path,
        {
            "schema_version": "trim_agent_tool_payload_cache_v1",
            "tool_name": "compare_similar_mols",
            "task": "BBB_Martins",
            "feature_set_name": tools.feature_set_name,
            "cache_namespace": "legacy_namespace",
            "smiles": "CCO",
            "payload": payload,
        },
    )

    assert tools.has_cached_tool_payload(
        tool_name="compare_similar_mols",
        smiles="CCO",
        neighbors_per_label=3,
    )
    assert not tools.has_cached_tool_payload(
        tool_name="compare_similar_mols",
        smiles="CCO",
        neighbors_per_label=1,
    )
    assert (
        tools._load_cached_tool_payload(
            tool_name="compare_similar_mols",
            smiles="CCO",
            neighbors_per_label=3,
        )
        == payload
    )


def test_tool_cache_namespace_ignores_bundle_file_byte_changes(tmp_path: Path):
    tools = _build_fake_tool_runner(tmp_path)
    namespace_before = tools._build_tool_cache_namespace()

    bundle_path = Path(tools.manifest["bundle_paths"]["global_bundle_path"])
    bundle_path.write_text("global-v2-with-different-size", encoding="utf-8")

    namespace_after = tools._build_tool_cache_namespace()
    assert namespace_after == namespace_before


def test_tool_cache_namespace_ignores_file_mtime_changes(tmp_path: Path):
    tools = _build_fake_tool_runner(tmp_path)
    namespace_before = tools._build_tool_cache_namespace()

    bundle_path = Path(tools.manifest["bundle_paths"]["global_bundle_path"])
    os.utime(bundle_path, ns=(1234567890000000000, 1234567890000000000))

    namespace_after = tools._build_tool_cache_namespace()
    assert namespace_after == namespace_before


def test_tool_cache_diagnostics_track_small_file_content_digest(tmp_path: Path):
    tools = _build_fake_tool_runner(tmp_path)
    namespace_before = tools._build_tool_cache_namespace()
    diagnostics_before = tools._build_tool_cache_diagnostic_payload()

    bundle_path = Path(tools.manifest["bundle_paths"]["global_bundle_path"])
    bundle_path.write_text("GLOBAL", encoding="utf-8")

    namespace_after = tools._build_tool_cache_namespace()
    diagnostics_after = tools._build_tool_cache_diagnostic_payload()
    assert namespace_after == namespace_before
    assert (
        diagnostics_after["bundle_file_diagnostics"]["global_bundle_path"]["sha256"]
        != diagnostics_before["bundle_file_diagnostics"]["global_bundle_path"]["sha256"]
    )


def test_tool_cache_namespace_uses_project_relative_symlink_path(tmp_path: Path, monkeypatch):
    tools = _build_fake_tool_runner(tmp_path)
    project_root = tmp_path / "project"
    outside_root = tmp_path / "outside"
    project_root.mkdir()
    outside_root.mkdir()
    target_path = outside_root / "target.pkl"
    target_path.write_text("target", encoding="utf-8")
    symlink_path = project_root / "link.pkl"
    symlink_path.symlink_to(target_path)

    monkeypatch.setattr("trim.reasoning.agent_tools.tools.PROJECT_ROOT", project_root)

    assert tools._cache_file_identity(symlink_path)["path"] == "link.pkl"
    assert tools._cache_file_signature(symlink_path)["path"] == "link.pkl"


def test_tool_payload_cache_accepts_legacy_portable_v2_namespace(tmp_path: Path):
    tools = _build_fake_tool_runner(tmp_path)
    payload = {
        "tool_name": "get_mol_properties_and_fg",
        "task": "BBB_Martins",
        "smiles": "CCO",
        "features": [],
    }
    smiles_digest = tools._smiles_cache_digest("CCO")
    legacy_path = (
        tools.tool_cache_root
        / tools.feature_set_name
        / tools.task
        / "portable_v2_namespace"
        / "get_mol_properties_and_fg"
        / f"{smiles_digest}.json"
    )
    save_json(
        legacy_path,
        {
            "schema_version": "trim_agent_tool_payload_cache_v1",
            "cache_signature_version": "portable_v2",
            "tool_name": "get_mol_properties_and_fg",
            "task": "BBB_Martins",
            "feature_set_name": tools.feature_set_name,
            "cache_namespace": "portable_v2_namespace",
            "smiles": "CCO",
            "payload": payload,
        },
    )

    assert tools._load_cached_tool_payload(tool_name="get_mol_properties_and_fg", smiles="CCO") == payload


def test_tool_payload_cache_can_read_legacy_namespace_without_migrating(tmp_path: Path):
    tools = _build_fake_tool_runner(tmp_path)
    payload = {
        "tool_name": "get_mol_properties_and_fg",
        "task": "BBB_Martins",
        "smiles": "CCO",
        "features": [],
    }
    smiles_digest = tools._smiles_cache_digest("CCO")
    legacy_path = (
        tools.tool_cache_root
        / tools.feature_set_name
        / tools.task
        / "legacy_namespace"
        / "get_mol_properties_and_fg"
        / f"{smiles_digest}.json"
    )
    save_json(
        legacy_path,
        {
            "schema_version": "trim_agent_tool_payload_cache_v1",
            "tool_name": "get_mol_properties_and_fg",
            "task": "BBB_Martins",
            "feature_set_name": tools.feature_set_name,
            "cache_namespace": "legacy_namespace",
            "smiles": "CCO",
            "payload": payload,
        },
    )

    assert tools.has_cached_tool_payload(tool_name="get_mol_properties_and_fg", smiles="CCO")
    loaded_payload = tools._load_cached_tool_payload(tool_name="get_mol_properties_and_fg", smiles="CCO")

    assert loaded_payload == payload
    current_path = tools._tool_cache_path(tool_name="get_mol_properties_and_fg", smiles="CCO")
    assert not current_path.exists()


def test_tool_smiles_lookup_falls_back_to_canonical_task_smiles(tmp_path: Path, monkeypatch):
    tools = _build_fake_tool_runner(tmp_path)
    tools._smiles_index = {
        "canonical": [
            {
                "split": "valid",
                "label": 0,
                "scaffold": "scaffold",
            }
        ]
    }

    monkeypatch.setattr(
        "trim.reasoning.agent_tools.tools._canonicalize_smiles_for_tool_lookup",
        lambda smiles: "canonical" if smiles == "raw" else None,
    )

    assert tools._resolve_tool_smiles("raw") == "canonical"
    assert tools._resolve_tool_smiles("canonical") == "canonical"
    assert tools._resolve_tool_smiles("unknown") == "unknown"
