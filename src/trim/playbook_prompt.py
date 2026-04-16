from __future__ import annotations

import csv
import json
from pathlib import Path

from trim.reasoning.semantics.feature_semantics import build_feature_semantics_map
from trim.reasoning.semantics.task_semantics import load_task_label_semantics
from trim.utils.io import load_json
from trim.utils.paths import OUTPUTS_ROOT, PROJECT_ROOT, resolve_project_path


DEFAULT_FEATURE_CONFIG = (
    PROJECT_ROOT / "configs" / "features" / "rdkit_descriptors_and_pka_easy_to_NLP_Lv1_core_pka_no_fr_counts.json"
)
DEFAULT_TEMPLATE_PATH = PROJECT_ROOT / "prompt_templates" / "playbooks" / "deepresearch_threshold_playbook_prompt_template.md"
DEFAULT_OUTPUT_ROOT = OUTPUTS_ROOT / "playbook_research_prompts"
DEFAULT_TASK_MANIFEST_INDEX = (
    OUTPUTS_ROOT
    / "reasoning_agent_tools"
    / "manifests"
    / "fg_top_level+rdkit_descriptors_and_pka_easy_to_NLP_Lv1_core_pka_no_fr_counts"
    / "manifest_index.json"
)


def render_template(template_text: str, replacements: dict[str, str]) -> str:
    rendered = template_text
    for key, value in replacements.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)
    return rendered


def load_feature_names_from_config(config_path: str | Path) -> list[str]:
    resolved_config_path = resolve_project_path(config_path)
    payload = load_json(resolved_config_path)
    sources = payload.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError(f"Feature config must contain a non-empty 'sources' list: {resolved_config_path}")

    source = sources[0]
    if not isinstance(source, dict):
        raise ValueError(f"Feature source must be a JSON object: {resolved_config_path}")

    csv_path = resolve_project_path(str(source["csv_path"]))
    prefix = str(source.get("prefix", ""))
    smiles_column = str(source.get("smiles_column", "smiles"))

    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader)

    return [f"{prefix}{column}" for column in header if column != smiles_column]


def build_task_description(task: str, explicit_description: str | None = None) -> str:
    if explicit_description is not None and explicit_description.strip():
        return explicit_description.strip()

    semantics = load_task_label_semantics(task)
    if semantics is None:
        return f"task {task}"

    return (
        f"task {task}, where option (A) means {semantics[0]['text']} "
        f"and option (B) means {semantics[1]['text']}"
    )


def build_feature_list(feature_names: list[str]) -> str:
    semantics_map = build_feature_semantics_map(feature_names)
    lines: list[str] = []
    for feature_name in feature_names:
        semantics = semantics_map[feature_name]
        lines.append(
            (
                f"- {semantics['display_name']}: {semantics['description']}"
            )
        )
    return "\n".join(lines)


def default_output_path(task: str) -> Path:
    return DEFAULT_OUTPUT_ROOT / task / "deepresearch_threshold_playbook_prompt_filled.md"


def load_task_names_from_manifest_index(manifest_index_path: str | Path = DEFAULT_TASK_MANIFEST_INDEX) -> list[str]:
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


def render_playbook_research_prompt(
    *,
    task: str,
    task_description: str | None = None,
    feature_config: str | Path = DEFAULT_FEATURE_CONFIG,
    template_path: str | Path = DEFAULT_TEMPLATE_PATH,
) -> str:
    feature_names = load_feature_names_from_config(feature_config)
    if len(feature_names) != 36:
        raise ValueError(
            "Expected the default playbook feature scope to contain 36 dense RDKit/pKa features, "
            f"but found {len(feature_names)} from {resolve_project_path(feature_config)}"
        )

    rendered_task_description = build_task_description(task, explicit_description=task_description)
    feature_list = build_feature_list(feature_names)
    template_text = resolve_project_path(template_path).read_text(encoding="utf-8")
    return render_template(
        template_text,
        {
            "TASK_DESCRIPTION": rendered_task_description,
            "FEATURE_LIST": feature_list,
        },
    )


def render_playbook_research_prompts_for_tasks(
    *,
    tasks: list[str],
    output_root: str | Path = DEFAULT_OUTPUT_ROOT,
    feature_config: str | Path = DEFAULT_FEATURE_CONFIG,
    template_path: str | Path = DEFAULT_TEMPLATE_PATH,
) -> dict[str, object]:
    resolved_output_root = resolve_project_path(output_root)
    rendered_tasks: list[dict[str, str]] = []

    for task in tasks:
        rendered = render_playbook_research_prompt(
            task=task,
            feature_config=feature_config,
            template_path=template_path,
        )
        output_path = resolved_output_root / task / "deepresearch_threshold_playbook_prompt_filled.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")
        rendered_tasks.append(
            {
                "task": task,
                "output_path": str(output_path.resolve()),
            }
        )

    summary = {
        "num_tasks": len(rendered_tasks),
        "tasks": rendered_tasks,
    }
    summary_path = resolved_output_root / "render_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {
        "num_tasks": len(rendered_tasks),
        "summary_path": str(summary_path.resolve()),
        "tasks": rendered_tasks,
    }
