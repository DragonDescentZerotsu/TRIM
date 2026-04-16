from __future__ import annotations

import json
from pathlib import Path

from trim.reasoning.agent_sft import (
    COMPARE_SIMILAR_MOLS_CALL_ID,
    COMPARE_SIMILAR_MOLS_TOOL_NAME,
    GET_MOL_PROPERTIES_CALL_ID,
    GET_MOL_PROPERTIES_TOOL_NAME,
    GLOBAL_TOOL_BRIDGE,
    LOCAL_TOOL_BRIDGE,
    build_agent_reasoning_sft_datasets,
    build_agent_reasoning_sft_for_task,
    build_agent_reasoning_sft_record,
)


class _FakeToolRunner:
    def get_mol_properties_and_fg(self, smiles: str) -> str:
        return f"global::{smiles}"

    def compare_similar_mols(self, smiles: str) -> str:
        return f"local::{smiles}"


class _FakeSplit:
    def __init__(self, *, smiles: list[str], labels: list[int]):
        self.smiles = smiles
        self.labels = labels


def _write_rewrite_result(
    root: Path,
    *,
    provider: str,
    model_slug: str,
    mode: str,
    split: str,
    task: str,
    sample_index: int,
    reasoning: str,
    sample_id: str | None = None,
) -> None:
    sample_dir = root / provider / model_slug / mode / split / task / f"sample_{sample_index:05d}"
    sample_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "trim_reasoning_rewrite_output_v1",
        "mode": mode,
        "task": task,
        "split": split,
        "sample_id": sample_id or f"{split}_sample_{sample_index}",
        "sample_index": sample_index,
        "parsed_output": {"reasoning": reasoning},
    }
    (sample_dir / "result.json").write_text(json.dumps(payload), encoding="utf-8")


def test_build_agent_reasoning_sft_record_assembles_expected_six_message_transcript(tmp_path: Path, monkeypatch):
    rewrite_root = tmp_path / "rewrite_outputs"
    task = "BBB_Martins"
    split = "train"
    sample_index = 0

    _write_rewrite_result(
        rewrite_root,
        provider="openrouter",
        model_slug="openai__gpt-5.4-mini",
        mode="global",
        split=split,
        task=task,
        sample_index=sample_index,
        reasoning="Global polished reasoning",
    )
    _write_rewrite_result(
        rewrite_root,
        provider="openrouter",
        model_slug="openai__gpt-5.4-mini",
        mode="local",
        split=split,
        task=task,
        sample_index=sample_index,
        reasoning="Local polished reasoning",
    )
    _write_rewrite_result(
        rewrite_root,
        provider="openrouter",
        model_slug="openai__gpt-5.4-mini",
        mode="hybrid",
        split=split,
        task=task,
        sample_index=sample_index,
        reasoning="Hybrid polished reasoning",
    )

    monkeypatch.setattr(
        "trim.reasoning.agent_sft.render_task_user_message",
        lambda **kwargs: f"user::{kwargs['task']}::{kwargs['smiles']}",
    )
    monkeypatch.setattr(
        "trim.reasoning.agent_sft.load_task_label_semantics",
        lambda task_name: {
            0: {"option": "A", "text": "negative"},
            1: {"option": "B", "text": "positive"},
        },
    )

    record = build_agent_reasoning_sft_record(
        task=task,
        split=split,
        sample_index=sample_index,
        smiles="CCO",
        gt_label=1,
        tool_runner=_FakeToolRunner(),
        rewrite_output_root=rewrite_root,
        provider="openrouter",
        model="openai/gpt-5.4-mini",
    )

    assert record["sample_id"] == "train_sample_0"
    assert record["final_answer_option"] == "B"
    assert set(record["source_paths"]) == {"global_result_json", "local_result_json", "hybrid_result_json"}

    messages = record["messages"]
    assert [message["role"] for message in messages] == [
        "user",
        "assistant",
        "tool",
        "assistant",
        "tool",
        "assistant",
    ]
    assert messages[0]["content"] == "user::BBB_Martins::CCO"

    assert messages[1]["content"] == ""
    assert messages[1]["thinking"] == GLOBAL_TOOL_BRIDGE
    assert messages[1]["tool_calls"][0]["id"] == GET_MOL_PROPERTIES_CALL_ID
    assert messages[1]["tool_calls"][0]["function"]["name"] == GET_MOL_PROPERTIES_TOOL_NAME
    assert messages[1]["tool_calls"][0]["function"]["arguments"] == '{"smiles": "CCO"}'

    assert messages[2] == {
        "role": "tool",
        "tool_call_id": GET_MOL_PROPERTIES_CALL_ID,
        "name": GET_MOL_PROPERTIES_TOOL_NAME,
        "content": "global::CCO",
    }

    assert messages[3]["content"] == ""
    assert messages[3]["thinking"] == f"Global polished reasoning\n\n{LOCAL_TOOL_BRIDGE}"
    assert messages[3]["tool_calls"][0]["id"] == COMPARE_SIMILAR_MOLS_CALL_ID
    assert messages[3]["tool_calls"][0]["function"]["name"] == COMPARE_SIMILAR_MOLS_TOOL_NAME

    assert messages[4] == {
        "role": "tool",
        "tool_call_id": COMPARE_SIMILAR_MOLS_CALL_ID,
        "name": COMPARE_SIMILAR_MOLS_TOOL_NAME,
        "content": "local::CCO",
    }

    assert "tool_calls" not in messages[5]
    assert messages[5]["thinking"] == "Local polished reasoning\n\nHybrid polished reasoning"
    assert messages[5]["content"] == "Answer: (B)"


def test_build_agent_reasoning_sft_record_falls_back_to_binary_a_b_mapping(tmp_path: Path, monkeypatch):
    rewrite_root = tmp_path / "rewrite_outputs"
    task = "BBB_Martins"

    for mode in ("global", "local", "hybrid"):
        _write_rewrite_result(
            rewrite_root,
            provider="openrouter",
            model_slug="openai__gpt-5.4-mini",
            mode=mode,
            split="train",
            task=task,
            sample_index=0,
            reasoning=f"{mode} reasoning",
        )

    monkeypatch.setattr("trim.reasoning.agent_sft.render_task_user_message", lambda **kwargs: "prompt")
    monkeypatch.setattr("trim.reasoning.agent_sft.load_task_label_semantics", lambda task_name: None)

    record_zero = build_agent_reasoning_sft_record(
        task=task,
        split="train",
        sample_index=0,
        smiles="CCO",
        gt_label=0,
        tool_runner=_FakeToolRunner(),
        rewrite_output_root=rewrite_root,
        provider="openrouter",
        model="openai/gpt-5.4-mini",
    )
    record_one = build_agent_reasoning_sft_record(
        task=task,
        split="train",
        sample_index=0,
        smiles="CCO",
        gt_label=1,
        tool_runner=_FakeToolRunner(),
        rewrite_output_root=rewrite_root,
        provider="openrouter",
        model="openai/gpt-5.4-mini",
    )

    assert record_zero["messages"][-1]["content"] == "Answer: (A)"
    assert record_one["messages"][-1]["content"] == "Answer: (B)"


def test_build_agent_reasoning_sft_record_fails_fast_when_rewrite_artifact_is_missing(tmp_path: Path, monkeypatch):
    rewrite_root = tmp_path / "rewrite_outputs"
    task = "BBB_Martins"

    _write_rewrite_result(
        rewrite_root,
        provider="openrouter",
        model_slug="openai__gpt-5.4-mini",
        mode="global",
        split="train",
        task=task,
        sample_index=0,
        reasoning="global reasoning",
    )
    _write_rewrite_result(
        rewrite_root,
        provider="openrouter",
        model_slug="openai__gpt-5.4-mini",
        mode="local",
        split="train",
        task=task,
        sample_index=0,
        reasoning="local reasoning",
    )

    monkeypatch.setattr("trim.reasoning.agent_sft.render_task_user_message", lambda **kwargs: "prompt")

    try:
        build_agent_reasoning_sft_record(
            task=task,
            split="train",
            sample_index=0,
            smiles="CCO",
            gt_label=1,
            tool_runner=_FakeToolRunner(),
            rewrite_output_root=rewrite_root,
            provider="openrouter",
            model="openai/gpt-5.4-mini",
        )
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("Expected FileNotFoundError when hybrid rewrite output is missing")


def test_build_agent_reasoning_sft_datasets_writes_per_task_jsonl_in_sample_order(tmp_path: Path, monkeypatch):
    rewrite_root = tmp_path / "rewrite_outputs"
    output_root = tmp_path / "sft"
    provider = "openrouter"
    model = "openai/gpt-5.4-mini"
    model_slug = "openai__gpt-5.4-mini"

    for mode in ("global", "local", "hybrid"):
        _write_rewrite_result(
            rewrite_root,
            provider=provider,
            model_slug=model_slug,
            mode=mode,
            split="train",
            task="BBB_Martins",
            sample_index=0,
            reasoning=f"BBB_Martins {mode} reasoning 0",
        )
        _write_rewrite_result(
            rewrite_root,
            provider=provider,
            model_slug=model_slug,
            mode=mode,
            split="train",
            task="BBB_Martins",
            sample_index=1,
            reasoning=f"BBB_Martins {mode} reasoning 1",
        )
        _write_rewrite_result(
            rewrite_root,
            provider=provider,
            model_slug=model_slug,
            mode=mode,
            split="train",
            task="AMES",
            sample_index=1,
            reasoning=f"AMES {mode} reasoning 1",
        )

    def _fake_split(task: str, split: str, data_root=None):
        assert split == "train"
        if task == "BBB_Martins":
            return _FakeSplit(smiles=["BBB_0", "BBB_1"], labels=[1, 0])
        if task == "AMES":
            return _FakeSplit(smiles=["AMES_0", "AMES_1"], labels=[0, 1])
        raise AssertionError(f"Unexpected task: {task}")

    monkeypatch.setattr("trim.reasoning.agent_sft.load_tdc_split", _fake_split)
    monkeypatch.setattr("trim.reasoning.agent_sft.render_task_user_message", lambda **kwargs: f"prompt::{kwargs['smiles']}")
    monkeypatch.setattr("trim.reasoning.agent_sft.build_task_tool_runner", lambda **kwargs: _FakeToolRunner())
    monkeypatch.setattr("trim.reasoning.agent_sft.load_task_label_semantics", lambda task_name: None)

    summary = build_agent_reasoning_sft_datasets(
        tasks=["BBB_Martins", "AMES"],
        split="train",
        rewrite_output_root=rewrite_root,
        provider=provider,
        model=model,
        output_root=output_root,
    )

    assert summary["num_tasks"] == 2
    assert summary["num_records"] == 3

    bbb_path = output_root / provider / model_slug / "train" / "BBB_Martins.jsonl"
    ames_path = output_root / provider / model_slug / "train" / "AMES.jsonl"
    manifest_path = output_root / provider / model_slug / "train" / "manifest.json"
    assert bbb_path.exists()
    assert ames_path.exists()
    assert manifest_path.exists()

    bbb_rows = [json.loads(line) for line in bbb_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert [row["sample_index"] for row in bbb_rows] == [0, 1]
    assert [row["smiles"] for row in bbb_rows] == ["BBB_0", "BBB_1"]
    assert [row["final_answer_option"] for row in bbb_rows] == ["B", "A"]
    assert "source_paths" in bbb_rows[0]
    assert "messages" in bbb_rows[0]

    ames_rows = [json.loads(line) for line in ames_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert [row["sample_index"] for row in ames_rows] == [1]
    assert [row["smiles"] for row in ames_rows] == ["AMES_1"]
    assert summary["summary_path"] == str(manifest_path.resolve())


def test_build_agent_reasoning_sft_datasets_resumes_from_existing_jsonl_prefix(tmp_path: Path, monkeypatch):
    rewrite_root = tmp_path / "rewrite_outputs"
    output_root = tmp_path / "sft"
    provider = "openrouter"
    model = "openai/gpt-5.4-mini"
    model_slug = "openai__gpt-5.4-mini"
    task = "BBB_Martins"

    for sample_index in (0, 1, 2):
        for mode in ("global", "local", "hybrid"):
            _write_rewrite_result(
                rewrite_root,
                provider=provider,
                model_slug=model_slug,
                mode=mode,
                split="train",
                task=task,
                sample_index=sample_index,
                reasoning=f"{task} {mode} reasoning {sample_index}",
            )

    def _fake_split(task_name: str, split: str, data_root=None):
        assert task_name == task
        assert split == "train"
        return _FakeSplit(smiles=["BBB_0", "BBB_1", "BBB_2"], labels=[1, 0, 1])

    monkeypatch.setattr("trim.reasoning.agent_sft.load_tdc_split", _fake_split)
    monkeypatch.setattr("trim.reasoning.agent_sft.render_task_user_message", lambda **kwargs: f"prompt::{kwargs['smiles']}")
    monkeypatch.setattr("trim.reasoning.agent_sft.load_task_label_semantics", lambda task_name: None)

    class _CountingToolRunner(_FakeToolRunner):
        def __init__(self):
            self.calls: list[str] = []

        def get_mol_properties_and_fg(self, smiles: str) -> str:
            self.calls.append(f"global::{smiles}")
            return super().get_mol_properties_and_fg(smiles)

        def compare_similar_mols(self, smiles: str) -> str:
            self.calls.append(f"local::{smiles}")
            return super().compare_similar_mols(smiles)

    tool_runner = _CountingToolRunner()
    monkeypatch.setattr("trim.reasoning.agent_sft.build_task_tool_runner", lambda **kwargs: tool_runner)

    output_dir = output_root / provider / model_slug / "train"
    output_dir.mkdir(parents=True, exist_ok=True)
    existing_path = output_dir / f"{task}.jsonl"
    prefix_record = {
        "schema_version": "trim_agent_reasoning_sft_messages_v1",
        "task": task,
        "split": "train",
        "sample_index": 0,
        "sample_id": "train_sample_0",
        "smiles": "BBB_0",
        "gt_label": 1,
        "final_answer_option": "B",
        "source_paths": {
            "global_result_json": "g0",
            "local_result_json": "l0",
            "hybrid_result_json": "h0",
        },
        "messages": [{"role": "user", "content": "existing"}],
    }
    existing_path.write_text(json.dumps(prefix_record, ensure_ascii=False) + "\n", encoding="utf-8")

    summary = build_agent_reasoning_sft_datasets(
        tasks=[task],
        split="train",
        rewrite_output_root=rewrite_root,
        provider=provider,
        model=model,
        output_root=output_root,
        max_concurrency=1,
        skip_existing=True,
    )

    rows = [json.loads(line) for line in existing_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert [row["sample_index"] for row in rows] == [0, 1, 2]
    assert rows[0]["messages"] == [{"role": "user", "content": "existing"}]
    assert rows[1]["smiles"] == "BBB_1"
    assert rows[2]["smiles"] == "BBB_2"
    assert sorted(tool_runner.calls) == [
        "global::BBB_1",
        "global::BBB_2",
        "local::BBB_1",
        "local::BBB_2",
    ]
    assert summary["num_records"] == 3
