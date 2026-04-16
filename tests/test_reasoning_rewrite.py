from __future__ import annotations

from pathlib import Path

from trim.reasoning.rewrite.candidates import build_rewrite_candidates
from trim.reasoning.rewrite.llm import (
    build_llm_request_config,
    extract_json_from_response_text,
)
from trim.reasoning.rewrite.pipeline import (
    build_candidates_from_filtered_records,
    collect_reasoning_post_checks,
    extract_reasoning_text_for_mode,
    reasoning_key_for_mode,
    run_rewrite_batch,
    run_single_rewrite,
    validate_saved_rewrite_output,
)
from trim.reasoning.rewrite.rendering import render_rewrite_prompt
from trim.utils.io import load_json, save_json


def _write_global_sample(path: Path, *, sample_index: int, correct: bool) -> None:
    save_json(
        path,
        {
            "sample_id": f"train_sample_{sample_index}",
            "sample_index": sample_index,
            "task": "BBB_Martins",
            "split": "train",
            "smiles": f"SMILES_{sample_index}",
            "gt_label": 1,
            "gt_label_semantics": {"option": "B", "text": "crosses the BBB", "label": 1},
            "global_prediction_correct": correct,
            "global_middle_draft": f"Global middle draft {sample_index}",
        },
    )


def _neighbor_evidence(role: str, rank: int) -> dict[str, object]:
    return {
        "neighbor_role": role,
        "neighbor_id": f"{role}_{rank}",
        "neighbor_smiles": f"{role}_smiles_{rank}",
        "neighbor_similarity": 0.9 - 0.1 * rank,
    }


def _neighbor_draft(role: str, rank: int) -> dict[str, object]:
    return {
        "neighbor_role": role,
        "neighbor_id": f"{role}_{rank}",
        "neighbor_smiles": f"{role}_smiles_{rank}",
        "middle_draft": f"{role} draft {rank}",
    }


def _write_local_sample(path: Path, *, sample_index: int, correct: bool) -> None:
    save_json(
        path,
        {
            "sample_id": f"train_sample_{sample_index}",
            "sample_index": sample_index,
            "task": "BBB_Martins",
            "split": "train",
            "smiles": f"SMILES_{sample_index}",
            "gt_label": 1,
            "gt_label_semantics": {"option": "B", "text": "crosses the BBB", "label": 1},
            "local_prediction_correct": correct,
            "local_prediction": 1,
            "local_per_neighbor_decision_evidence": {
                "positive_neighbors": [_neighbor_evidence("positive_neighbor", rank) for rank in range(1, 4)],
                "negative_neighbors": [_neighbor_evidence("negative_neighbor", rank) for rank in range(1, 4)],
            },
            "local_per_neighbor_middle_draft": {
                "positive_neighbors": [_neighbor_draft("positive_neighbor", rank) for rank in range(1, 4)],
                "negative_neighbors": [_neighbor_draft("negative_neighbor", rank) for rank in range(1, 4)],
            },
        },
    )


def test_build_rewrite_candidates_filters_both_wrong_and_writes_kept_records(tmp_path: Path):
    global_dir = tmp_path / "global"
    local_dir = tmp_path / "local"
    playbook_root = tmp_path / "playbooks"
    playbook_root.mkdir()
    (playbook_root / "BBB_Martins.md").write_text("BBB playbook", encoding="utf-8")

    _write_global_sample(global_dir / "sample_00000.json", sample_index=0, correct=True)
    _write_local_sample(local_dir / "sample_00000.json", sample_index=0, correct=False)

    _write_global_sample(global_dir / "sample_00001.json", sample_index=1, correct=False)
    _write_local_sample(local_dir / "sample_00001.json", sample_index=1, correct=False)

    output_dir = tmp_path / "rewrite_candidates"
    manifest = build_rewrite_candidates(
        global_dir=global_dir,
        local_dir=local_dir,
        playbook_root=playbook_root,
        output_dir=output_dir,
    )

    assert manifest["kept_record_count"] == 1
    assert manifest["dropped_record_count"] == 1
    assert manifest["dropped_records"][0]["teacher_case"] == "both_wrong"

    kept_payload = load_json(output_dir / "sample_00000.json")
    assert kept_payload["teacher_case"] == "global_only_correct"
    assert kept_payload["keep_for_rewrite"] is True
    assert kept_payload["local_rewrite_input"]["local_prediction"] == 1
    assert len(kept_payload["local_rewrite_input"]["neighbor_similarities"]) == 6


def test_openrouter_prefers_dotenv_api_key_over_process_env(tmp_path: Path, monkeypatch):
    dotenv_path = tmp_path / ".env"
    dotenv_path.write_text("OPENROUTER_API_KEY=dotenv_key\n", encoding="utf-8")
    monkeypatch.setenv("OPENROUTER_API_KEY", "shell_key")

    config = build_llm_request_config(
        provider="openrouter",
        model="openai/gpt-5.4-mini",
        dotenv_path=dotenv_path,
    )

    assert config.api_key == "dotenv_key"


def test_render_rewrite_prompts_use_only_expected_inputs(tmp_path: Path):
    candidate_path = tmp_path / "candidate.json"
    save_json(
        candidate_path,
        {
            "schema_version": "trim_reasoning_rewrite_v1",
            "sample_id": "train_sample_0",
            "task": "BBB_Martins",
            "global_rewrite_input": {
                "task_description": "BBB task",
                "task_playbook": "BBB playbook",
                "global_middle_draft": "Global middle draft",
            },
            "local_rewrite_input": {
                "task_playbook": "BBB playbook",
                "task_description": "BBB local task",
                "positive_label_semantics": "crosses the BBB",
                "negative_label_semantics": "does not cross the BBB",
                "neighbor_similarities": [
                    {"neighbor_role": "positive_neighbor", "similarity": 0.8},
                    {"neighbor_role": "positive_neighbor", "similarity": 0.7},
                    {"neighbor_role": "positive_neighbor", "similarity": 0.6},
                    {"neighbor_role": "negative_neighbor", "similarity": 0.5},
                    {"neighbor_role": "negative_neighbor", "similarity": 0.4},
                    {"neighbor_role": "negative_neighbor", "similarity": 0.3},
                ],
                "local_per_neighbor_middle_draft": {
                    "positive_neighbors": [
                        {"middle_draft": "local draft p1"},
                        {"middle_draft": "local draft p2"},
                        {"middle_draft": "local draft p3"},
                    ],
                    "negative_neighbors": [
                        {"middle_draft": "local draft n4"},
                        {"middle_draft": "local draft n5"},
                        {"middle_draft": "local draft n6"},
                    ],
                },
                "local_prediction": 1,
                "local_prediction_semantics": "option (B): crosses the BBB",
            },
            "hybrid_rewrite_input": {
                "gt_label": 1,
                "gt_label_semantics": {"option": "B", "text": "crosses the BBB", "label": 1},
            },
        },
    )
    candidate_payload = load_json(candidate_path)

    global_prompt = render_rewrite_prompt(candidate_payload=candidate_payload, mode="global")
    assert "TASK_DESCRIPTION" not in global_prompt
    assert "Global middle draft" in global_prompt
    assert "global-model middle draft" not in global_prompt
    assert "global_decision_evidence" not in global_prompt
    assert "If you mention a feature without its concrete value, the rewrite is invalid" in global_prompt
    assert '"reasoning"' in global_prompt

    local_prompt = render_rewrite_prompt(candidate_payload=candidate_payload, mode="local")
    assert "TASK_DESCRIPTION" not in local_prompt
    assert "POSITIVE_LABEL_SEMANTICS" not in local_prompt
    assert "NEGATIVE_LABEL_SEMANTICS" not in local_prompt
    assert "NEIGHBOR_1_SIMILARITIES" not in local_prompt
    assert "NEIGHBOR_6_LOCAL_MIDDLE_DRAFT" not in local_prompt
    assert "local draft p1" in local_prompt
    assert "local draft n6" in local_prompt
    assert "0.800" in local_prompt
    assert "0.300" in local_prompt
    assert "option (B): crosses the BBB" in local_prompt
    assert "Final local prediction label" not in local_prompt
    assert "do not skip any feature that appears in that neighbor's supplied comparison note" in local_prompt
    assert "secondary features may be covered more briefly as long as they are not omitted" in local_prompt
    assert '"reasoning"' in local_prompt

    hybrid_prompt = render_rewrite_prompt(
        candidate_payload=candidate_payload,
        mode="hybrid",
        global_reasoning="Polished global reasoning",
        local_reasoning="Polished local reasoning",
    )
    assert "Polished global reasoning" in hybrid_prompt
    assert "ground truth is" not in hybrid_prompt.lower()
    assert "Input 3. Target final label\n" not in hybrid_prompt
    assert '"reasoning"' in hybrid_prompt
    assert "option (B): crosses the BBB" in hybrid_prompt

def test_build_rewrite_candidates_without_tool_previews_still_supports_non_agent_modes(tmp_path: Path):
    global_dir = tmp_path / "global"
    local_dir = tmp_path / "local"
    playbook_root = tmp_path / "playbooks"
    playbook_root.mkdir()
    (playbook_root / "BBB_Martins.md").write_text("BBB playbook", encoding="utf-8")

    _write_global_sample(global_dir / "sample_00000.json", sample_index=0, correct=True)
    _write_local_sample(local_dir / "sample_00000.json", sample_index=0, correct=True)

    manifest = build_rewrite_candidates(
        global_dir=global_dir,
        local_dir=local_dir,
        playbook_root=playbook_root,
        output_dir=tmp_path / "rewrite_candidates",
    )
    assert manifest["kept_record_count"] == 1
    candidate_payload = load_json(tmp_path / "rewrite_candidates" / "sample_00000.json")

    global_prompt = render_rewrite_prompt(candidate_payload=candidate_payload, mode="global")
    local_prompt = render_rewrite_prompt(candidate_payload=candidate_payload, mode="local")
    hybrid_prompt = render_rewrite_prompt(
        candidate_payload=candidate_payload,
        mode="hybrid",
        global_reasoning="global polished",
        local_reasoning="local polished",
    )
    assert "Global middle draft 0" in global_prompt
    assert "option (B): crosses the BBB" in local_prompt
    assert "global polished" in hybrid_prompt


def test_extract_json_from_response_text_handles_fenced_json():
    parsed = extract_json_from_response_text(
        """```json
{
  "reasoning": "rewritten"
}
```"""
    )
    assert parsed == {"reasoning": "rewritten"}


def test_extract_json_from_response_text_recovers_unescaped_newlines_in_json_string():
    parsed = extract_json_from_response_text(
        '{"reasoning":"line one\n\nline two","quality_check":{"ok":true}}'
    )
    assert parsed["reasoning"] == "line one\n\nline two"


def test_collect_reasoning_post_checks_flags_meta_language():
    checks = collect_reasoning_post_checks(
        mode="local",
        parsed_output={
            "reasoning": "Neighbor 5 is favorable, but in this draft that contribution is treated as stronger."
        },
    )
    assert checks["meta_reference_free"] is False
    assert "draft" in checks["meta_terms_found"]
    assert "contribution" in checks["meta_terms_found"]


def test_collect_reasoning_post_checks_also_works_for_global():
    checks = collect_reasoning_post_checks(
        mode="global",
        parsed_output={
            "reasoning": "This playbook says the molecule should cross, and that prompt framing is explicit."
        },
    )
    assert checks["reasoning_key"] == "reasoning"
    assert checks["meta_reference_free"] is False
    assert "playbook" in checks["meta_terms_found"]
    assert "prompt" in checks["meta_terms_found"]


def test_reasoning_key_and_extraction_use_local_reasoning_field():
    assert reasoning_key_for_mode("global") == "reasoning"
    assert reasoning_key_for_mode("local") == "reasoning"
    assert reasoning_key_for_mode("hybrid") == "reasoning"
    extracted = extract_reasoning_text_for_mode(
        payload={
            "parsed_output": {
                "reasoning": "neighbor-based explanation",
                "quality_check": {
                    "covers_all_neighbors": True,
                    "distinguishes_pos_neg_neighbors": True,
                    "final_prediction_matches_provided_label": True,
                    "no_neighbor_hallucination": True,
                },
            }
        },
        mode="local",
    )
    assert extracted == "neighbor-based explanation"


def test_validate_saved_rewrite_output_rejects_meta_reference_terms():
    try:
        validate_saved_rewrite_output(
            mode="global",
            payload={
                "parsed_output": {"reasoning": "This prompt framing leaks into the reasoning."},
                "post_checks": {"meta_reference_free": False, "meta_terms_found": ["prompt"]},
            },
        )
    except ValueError as exc:
        assert "meta terms found" in str(exc)
    else:
        raise AssertionError("Expected validate_saved_rewrite_output to reject failed post-checks")


def test_run_single_rewrite_retries_when_post_check_fails(tmp_path: Path, monkeypatch):
    calls = {"count": 0}

    monkeypatch.setattr(
        "trim.reasoning.rewrite.pipeline.render_rewrite_prompt",
        lambda **kwargs: "prompt",
    )

    def _fake_completion(*, prompt, config):
        calls["count"] += 1
        if calls["count"] == 1:
            return {
                "content": '{"reasoning":"This prompt wording should not survive."}',
                "raw_response": {"attempt": 1},
            }
        return {
            "content": '{"reasoning":"Clean final reasoning."}',
            "raw_response": {"attempt": 2},
        }

    monkeypatch.setattr("trim.reasoning.rewrite.pipeline.run_chat_completion", _fake_completion)

    llm_config = build_llm_request_config(
        provider="vllm",
        model="demo-model",
        api_key="dummy",
    )
    payload = run_single_rewrite(
        candidate_payload={
            "sample_id": "train_sample_0",
            "sample_index": 0,
            "task": "BBB_Martins",
            "split": "train",
        },
        mode="global",
        llm_config=llm_config,
        output_root=tmp_path / "outputs",
        max_retries=1,
        retry_delay_s=0.0,
        skip_existing=False,
    )

    assert calls["count"] == 2
    assert payload["attempt_count"] == 2
    assert payload["parsed_output"]["reasoning"] == "Clean final reasoning."
    assert payload["post_checks"]["meta_reference_free"] is True


def test_build_llm_request_config_reads_api_key_from_dotenv(tmp_path: Path, monkeypatch):
    dotenv_path = tmp_path / ".env"
    dotenv_path.write_text('OPENROUTER_API_KEY="test-key"\n', encoding="utf-8")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    config = build_llm_request_config(
        provider="openrouter",
        model="demo-model",
        dotenv_path=dotenv_path,
    )
    assert config.api_key == "test-key"


def test_build_candidates_from_filtered_records_uses_kept_records_json(tmp_path: Path):
    playbook_root = tmp_path / "playbooks"
    playbook_root.mkdir()
    (playbook_root / "BBB_Martins.md").write_text("BBB playbook", encoding="utf-8")

    global_root = tmp_path / "global_root"
    local_root = tmp_path / "local_root"
    task = "BBB_Martins"
    split = "train"

    _write_global_sample(global_root / task / split / "sample_00000.json", sample_index=0, correct=True)
    _write_local_sample(local_root / task / split / "sample_00000.json", sample_index=0, correct=True)
    _write_global_sample(global_root / task / split / "sample_00001.json", sample_index=1, correct=True)
    _write_local_sample(local_root / task / split / "sample_00001.json", sample_index=1, correct=True)

    filtered_root = tmp_path / "filtered"
    save_json(
        filtered_root / split / task / "manifest.json",
        {
            "task": task,
            "split": split,
            "kept_record_count": 1,
        },
    )
    (filtered_root / split / task / "kept_records.json").parent.mkdir(parents=True, exist_ok=True)
    (filtered_root / split / task / "kept_records.json").write_text(
        '[{"sample_id":"train_sample_0","sample_index":0,"task":"BBB_Martins","split":"train","smiles":"SMILES_0","gt_label":1,"global_prediction_correct":true,"local_prediction_correct":true,"teacher_case":"both_correct","keep_for_rewrite":true,"drop_reason":null}]',
        encoding="utf-8",
    )

    manifest = build_candidates_from_filtered_records(
        task=task,
        split=split,
        filtered_root=filtered_root,
        global_root=global_root,
        local_root=local_root,
        playbook_root=playbook_root,
        candidate_root=tmp_path / "candidates",
    )
    assert manifest["kept_record_count"] == 1
    candidate_payload = load_json(tmp_path / "candidates" / split / task / "sample_00000.json")
    assert candidate_payload["sample_index"] == 0


def test_run_rewrite_batch_accepts_max_concurrency_and_preserves_row_order(tmp_path: Path, monkeypatch):
    candidate_dir = tmp_path / "candidates" / "train" / "BBB_Martins"
    candidate_dir.mkdir(parents=True, exist_ok=True)
    for sample_index in (2, 0, 1):
        save_json(
            candidate_dir / f"sample_{sample_index:05d}.json",
            {
                "sample_id": f"train_sample_{sample_index}",
                "sample_index": sample_index,
                "task": "BBB_Martins",
                "split": "train",
            },
        )

    monkeypatch.setattr(
        "trim.reasoning.rewrite.pipeline.build_candidates_from_filtered_records",
        lambda **kwargs: {
            "artifacts": {"output_dir": str(candidate_dir.resolve())},
            "kept_record_count": 3,
        },
    )

    def _fake_run_single_rewrite(
        *,
        candidate_payload,
        mode,
        llm_config,
        output_root,
        template_root=None,
        global_reasoning=None,
        local_reasoning=None,
        hybrid_reasoning=None,
        max_retries=0,
        retry_delay_s=0.0,
        skip_existing=True,
    ):
        return {
            "parsed_output": {"reasoning": f"{mode} reasoning {candidate_payload['sample_index']}"},
            "sample_index": candidate_payload["sample_index"],
            "mode": mode,
        }

    monkeypatch.setattr("trim.reasoning.rewrite.pipeline.run_single_rewrite", _fake_run_single_rewrite)

    llm_config = build_llm_request_config(
        provider="vllm",
        model="demo-model",
        api_key="dummy",
    )
    summary = run_rewrite_batch(
        task="BBB_Martins",
        split="train",
        mode="all",
        llm_config=llm_config,
        filtered_root=tmp_path / "filtered",
        global_root=tmp_path / "global",
        local_root=tmp_path / "local",
        playbook_root=tmp_path / "playbooks",
        candidate_root=tmp_path / "candidates",
        output_root=tmp_path / "outputs",
        max_concurrency=3,
    )

    assert summary["max_concurrency"] == 3
    assert summary["num_failed"] == 0
    assert [row["sample_index"] for row in summary["rows"]] == [0, 0, 0, 1, 1, 1, 2, 2, 2]
    assert [row["mode"] for row in summary["rows"][:3]] == ["global", "local", "hybrid"]


def test_run_rewrite_batch_records_failures_without_aborting_task(tmp_path: Path, monkeypatch):
    candidate_dir = tmp_path / "candidates" / "train" / "BBB_Martins"
    candidate_dir.mkdir(parents=True, exist_ok=True)
    for sample_index in (0, 1):
        save_json(
            candidate_dir / f"sample_{sample_index:05d}.json",
            {
                "sample_id": f"train_sample_{sample_index}",
                "sample_index": sample_index,
                "task": "BBB_Martins",
                "split": "train",
            },
        )

    monkeypatch.setattr(
        "trim.reasoning.rewrite.pipeline.build_candidates_from_filtered_records",
        lambda **kwargs: {
            "artifacts": {"output_dir": str(candidate_dir.resolve())},
            "kept_record_count": 2,
        },
    )

    def _fake_run_single_rewrite(
        *,
        candidate_payload,
        mode,
        llm_config,
        output_root,
        template_root=None,
        global_reasoning=None,
        local_reasoning=None,
        hybrid_reasoning=None,
        max_retries=0,
        retry_delay_s=0.0,
        skip_existing=True,
    ):
        if int(candidate_payload["sample_index"]) == 1 and mode == "local":
            raise RuntimeError("post-check failed after retries")
        return {
            "parsed_output": {"reasoning": f"{mode} reasoning {candidate_payload['sample_index']}"},
            "sample_index": candidate_payload["sample_index"],
            "mode": mode,
        }

    monkeypatch.setattr("trim.reasoning.rewrite.pipeline.run_single_rewrite", _fake_run_single_rewrite)

    llm_config = build_llm_request_config(
        provider="vllm",
        model="demo-model",
        api_key="dummy",
    )
    summary = run_rewrite_batch(
        task="BBB_Martins",
        split="train",
        mode="all",
        llm_config=llm_config,
        filtered_root=tmp_path / "filtered",
        global_root=tmp_path / "global",
        local_root=tmp_path / "local",
        playbook_root=tmp_path / "playbooks",
        candidate_root=tmp_path / "candidates",
        output_root=tmp_path / "outputs",
        max_concurrency=2,
        max_retries=1,
    )

    assert summary["num_succeeded"] == 1
    assert summary["num_failed"] == 1
    assert summary["failures"][0]["sample_index"] == 1
    assert summary["failures"][0]["failed_mode"] == "local"
