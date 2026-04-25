from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from trim.utils.io import load_json, save_json
from trim.utils.paths import DATA_ROOT, OUTPUTS_ROOT, resolve_project_path, serialize_project_path


TASK_USER_PROMPT_SCHEMA_VERSION = "trim_tdc_cot_user_prompt_v1"
DRUG_SMILES_PLACEHOLDER = "{{DRUG_SMILES}}"

DEFAULT_TASK_USER_PROMPT_ROOT = DATA_ROOT / "prompts" / "tdc_cot_user_messages"
DEFAULT_LEGACY_PROMPT_ROOTS = [
    Path("/data1/tianang/Projects/Intern-S1/DataPrepare/TDC_train_prompts_label_scaffold"),
    Path("/data1/tianang/Projects/Intern-S1/DataPrepare/TDC_valid_prompts_label_scaffold"),
    Path("/data1/tianang/Projects/Intern-S1/DataPrepare/TDC_test_prompts_label_scaffold"),
]
DEFAULT_TASK_MANIFEST_INDEX = (
    OUTPUTS_ROOT
    / "reasoning_agent_tools"
    / "manifests"
    / "fg_top_level+rdkit_descriptors_and_pka_easy_to_NLP_Lv1_core_pka_no_fr_counts"
    / "manifest_index.json"
)

_DRUG_SMILES_LINE_PATTERN = re.compile(r"(?m)^Drug SMILES:\s*.*$")


def _mask_prompt_text(prompt_text: str, *, placeholder: str = DRUG_SMILES_PLACEHOLDER) -> str:
    if "Drug SMILES:" not in prompt_text:
        raise ValueError("Prompt text does not contain a 'Drug SMILES:' line")
    masked_text, count = _DRUG_SMILES_LINE_PATTERN.subn(f"Drug SMILES: {placeholder}", prompt_text)
    if count != 1:
        raise ValueError(f"Expected exactly one 'Drug SMILES:' line, found {count}")
    return masked_text


def infer_drug_task_user_prompt_template(
    task: str,
    *,
    legacy_prompt_roots: list[str | Path] | None = None,
    max_records_per_root: int | None = 32,
    placeholder: str = DRUG_SMILES_PLACEHOLDER,
) -> str:
    candidate_roots = (
        [resolve_project_path(root) for root in legacy_prompt_roots]
        if legacy_prompt_roots is not None
        else list(DEFAULT_LEGACY_PROMPT_ROOTS)
    )
    template_counts: dict[str, int] = {}

    for root in candidate_roots:
        prompt_path = root / f"{task}.jsonl"
        if not prompt_path.exists():
            continue

        with prompt_path.open("r", encoding="utf-8") as handle:
            for line_index, line in enumerate(handle):
                if max_records_per_root is not None and line_index >= max_records_per_root:
                    break
                if not line.strip():
                    continue
                record = json.loads(line)
                prompt_text = str(record.get("text", ""))
                template_text = _mask_prompt_text(prompt_text, placeholder=placeholder)
                template_counts[template_text] = template_counts.get(template_text, 0) + 1

    if not template_counts:
        searched = ", ".join(str(root) for root in candidate_roots)
        raise FileNotFoundError(f"Could not find legacy prompt jsonl for task {task} under: {searched}")

    if len(template_counts) != 1:
        counts = sorted(template_counts.items(), key=lambda item: (-item[1], item[0]))
        summary = "; ".join(f"count={count}" for _, count in counts)
        raise ValueError(f"Found multiple prompt templates for task {task}: {summary}")

    return next(iter(template_counts))


def build_task_user_prompt_payload(
    *,
    task: str,
    template_text: str,
    placeholder: str = DRUG_SMILES_PLACEHOLDER,
) -> dict[str, Any]:
    return {
        "schema_version": TASK_USER_PROMPT_SCHEMA_VERSION,
        "task": task,
        "input_type": "drug_smiles",
        "placeholders": {
            "drug_smiles": placeholder,
        },
        "messages": [
            {
                "role": "user",
                "content": template_text,
            }
        ],
    }


def load_task_user_prompt_payload(
    task: str,
    *,
    prompt_root: str | Path = DEFAULT_TASK_USER_PROMPT_ROOT,
) -> dict[str, Any]:
    prompt_path = resolve_project_path(prompt_root) / f"{task}.json"
    if not prompt_path.exists():
        raise FileNotFoundError(f"Task user prompt payload not found: {prompt_path}")
    payload = load_json(prompt_path)
    if payload.get("schema_version") != TASK_USER_PROMPT_SCHEMA_VERSION:
        raise ValueError(f"Unexpected schema_version in {prompt_path}: {payload.get('schema_version')!r}")
    return payload


def render_task_user_messages(
    *,
    task: str,
    smiles: str,
    prompt_root: str | Path = DEFAULT_TASK_USER_PROMPT_ROOT,
) -> list[dict[str, str]]:
    payload = load_task_user_prompt_payload(task, prompt_root=prompt_root)
    placeholder = str(payload["placeholders"]["drug_smiles"])
    rendered_messages: list[dict[str, str]] = []
    for message in payload["messages"]:
        content = str(message["content"]).replace(placeholder, smiles)
        rendered_messages.append(
            {
                "role": str(message["role"]),
                "content": content,
            }
        )
    return rendered_messages


def render_task_user_message(
    *,
    task: str,
    smiles: str,
    prompt_root: str | Path = DEFAULT_TASK_USER_PROMPT_ROOT,
) -> str:
    rendered_messages = render_task_user_messages(task=task, smiles=smiles, prompt_root=prompt_root)
    if len(rendered_messages) != 1 or rendered_messages[0]["role"] != "user":
        raise ValueError(f"Expected exactly one user message for task {task}")
    return rendered_messages[0]["content"]


def load_task_names_from_manifest_index(
    manifest_index_path: str | Path = DEFAULT_TASK_MANIFEST_INDEX,
) -> list[str]:
    payload = load_json(resolve_project_path(manifest_index_path))
    task_rows = payload.get("tasks")
    if not isinstance(task_rows, list) or not task_rows:
        raise ValueError(f"Manifest index must contain a non-empty 'tasks' list: {manifest_index_path}")

    task_names: list[str] = []
    for row in task_rows:
        if not isinstance(row, dict) or "task" not in row:
            raise ValueError(f"Malformed task row in manifest index: {row!r}")
        task_names.append(str(row["task"]))
    return task_names


def export_task_user_prompts_for_tasks(
    *,
    tasks: list[str],
    output_root: str | Path = DEFAULT_TASK_USER_PROMPT_ROOT,
    legacy_prompt_roots: list[str | Path] | None = None,
    max_records_per_root: int | None = 32,
) -> dict[str, Any]:
    resolved_output_root = resolve_project_path(output_root)
    written_tasks: list[dict[str, str]] = []

    for task in tasks:
        template_text = infer_drug_task_user_prompt_template(
            task,
            legacy_prompt_roots=legacy_prompt_roots,
            max_records_per_root=max_records_per_root,
        )
        payload = build_task_user_prompt_payload(task=task, template_text=template_text)
        output_path = resolved_output_root / f"{task}.json"
        save_json(output_path, payload)
        written_tasks.append(
            {
                "task": task,
                "output_path": serialize_project_path(output_path),
            }
        )

    summary = {
        "schema_version": TASK_USER_PROMPT_SCHEMA_VERSION,
        "num_tasks": len(written_tasks),
        "tasks": written_tasks,
    }
    summary_path = resolved_output_root / "manifest.json"
    save_json(summary_path, summary)
    return {
        "num_tasks": len(written_tasks),
        "summary_path": serialize_project_path(summary_path),
        "tasks": written_tasks,
    }
