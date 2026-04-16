from __future__ import annotations

import json
from pathlib import Path

from trim.reasoning.task_user_prompts import (
    DRUG_SMILES_PLACEHOLDER,
    export_task_user_prompts_for_tasks,
    infer_drug_task_user_prompt_template,
    load_task_user_prompt_payload,
    render_task_user_message,
    render_task_user_messages,
)
from trim.reasoning.semantics.task_semantics import load_task_label_semantics


def _write_legacy_prompt_jsonl(root: Path, task: str, smiles_values: list[str]) -> None:
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"{task}.jsonl"
    with path.open("w", encoding="utf-8") as handle:
        for smiles in smiles_values:
            payload = {
                "text": (
                    "Instructions: Answer the following question about drug properties.\n"
                    "Question: Given a drug SMILES string, predict whether it\n"
                    "(A) inactive (B) active\n"
                    f"Drug SMILES: {smiles}\n"
                    'Please think step by step and then put ONLY your final choice ((A) or (B)) after "Answer:"'
                ),
                "Y": 1,
            }
            handle.write(json.dumps(payload) + "\n")


def test_infer_drug_task_user_prompt_template_masks_smiles_and_requires_single_template(tmp_path: Path):
    train_root = tmp_path / "train_prompts"
    valid_root = tmp_path / "valid_prompts"
    _write_legacy_prompt_jsonl(train_root, "BBB_Martins", ["CCO", "CCN"])
    _write_legacy_prompt_jsonl(valid_root, "BBB_Martins", ["CCC"])

    template = infer_drug_task_user_prompt_template(
        "BBB_Martins",
        legacy_prompt_roots=[train_root, valid_root],
    )
    assert DRUG_SMILES_PLACEHOLDER in template
    assert "Drug SMILES: CCO" not in template
    assert "(A) inactive (B) active" in template


def test_export_task_user_prompts_for_tasks_writes_payloads_and_manifest(tmp_path: Path):
    legacy_root = tmp_path / "legacy"
    output_root = tmp_path / "exported"
    _write_legacy_prompt_jsonl(legacy_root, "BBB_Martins", ["CCO", "CCN"])
    _write_legacy_prompt_jsonl(legacy_root, "AMES", ["O=C=O"])

    summary = export_task_user_prompts_for_tasks(
        tasks=["BBB_Martins", "AMES"],
        output_root=output_root,
        legacy_prompt_roots=[legacy_root],
    )

    assert summary["num_tasks"] == 2
    assert (output_root / "BBB_Martins.json").exists()
    assert (output_root / "AMES.json").exists()
    assert (output_root / "manifest.json").exists()


def test_render_task_user_message_and_messages_from_json_prompt_root(tmp_path: Path):
    prompt_root = tmp_path / "prompts"
    prompt_root.mkdir()
    payload = {
        "schema_version": "trim_tdc_cot_user_prompt_v1",
        "task": "BBB_Martins",
        "input_type": "drug_smiles",
        "placeholders": {"drug_smiles": "{{DRUG_SMILES}}"},
        "messages": [
            {
                "role": "user",
                "content": "Question: classify\nDrug SMILES: {{DRUG_SMILES}}\nAnswer carefully.",
            }
        ],
    }
    (prompt_root / "BBB_Martins.json").write_text(json.dumps(payload), encoding="utf-8")

    loaded = load_task_user_prompt_payload("BBB_Martins", prompt_root=prompt_root)
    assert loaded["task"] == "BBB_Martins"

    rendered_text = render_task_user_message(
        task="BBB_Martins",
        smiles="CCCl",
        prompt_root=prompt_root,
    )
    rendered_messages = render_task_user_messages(
        task="BBB_Martins",
        smiles="CCCl",
        prompt_root=prompt_root,
    )

    assert "CCCl" in rendered_text
    assert "{{DRUG_SMILES}}" not in rendered_text
    assert rendered_messages == [{"role": "user", "content": rendered_text}]


def test_load_task_label_semantics_can_read_repo_style_json_prompt_assets(tmp_path: Path):
    prompt_root = tmp_path / "prompts"
    prompt_root.mkdir()
    payload = {
        "schema_version": "trim_tdc_cot_user_prompt_v1",
        "task": "BBB_Martins",
        "input_type": "drug_smiles",
        "placeholders": {"drug_smiles": "{{DRUG_SMILES}}"},
        "messages": [
            {
                "role": "user",
                "content": (
                    "Question: Given a drug SMILES string, predict whether it\n"
                    "(A) does not cross the BBB (B) crosses the BBB\n"
                    "Drug SMILES: {{DRUG_SMILES}}\n"
                    'Please think step by step and then put ONLY your final choice ((A) or (B)) after "Answer:"'
                ),
            }
        ],
    }
    (prompt_root / "BBB_Martins.json").write_text(json.dumps(payload), encoding="utf-8")

    semantics = load_task_label_semantics("BBB_Martins", prompt_root=prompt_root)
    assert semantics is not None
    assert semantics[0]["text"] == "does not cross the BBB"
    assert semantics[1]["text"] == "crosses the BBB"
