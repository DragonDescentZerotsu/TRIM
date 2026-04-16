from __future__ import annotations

from pathlib import Path
from typing import Any

from trim.reasoning.rewrite.candidates import REWRITE_CANDIDATE_SCHEMA_VERSION
from trim.utils.io import load_json
from trim.utils.paths import PROJECT_ROOT, resolve_project_path


DEFAULT_REWRITE_TEMPLATE_ROOT = PROJECT_ROOT / "prompt_templates" / "reasoning_sft"


def _load_template(mode: str, template_root: str | Path | None = None) -> str:
    root = DEFAULT_REWRITE_TEMPLATE_ROOT if template_root is None else resolve_project_path(template_root)
    mapping = {
        "global": "rewrite_global_reasoning.md",
        "local": "rewrite_local_reasoning.md",
        "hybrid": "rewrite_hybrid_reasoning.md",
    }
    if mode not in mapping:
        raise ValueError(f"Unsupported rewrite prompt mode: {mode}")
    template_path = Path(root) / mapping[mode]
    return template_path.read_text(encoding="utf-8")


def _replace_slots(template_text: str, replacements: dict[str, str]) -> str:
    rendered = template_text
    for key, value in replacements.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)
    return rendered


def _format_similarity(value: object) -> str:
    return f"{float(value):.3f}"


def _format_label_semantics(payload: Any) -> str:
    if isinstance(payload, dict):
        option = payload.get("option")
        text = payload.get("text")
        if option is not None and text is not None:
            return f"option ({option}): {text}"
    return str(payload)


def _flatten_local_neighbors(payload: dict[str, Any]) -> list[dict[str, Any]]:
    similarities = list(payload["neighbor_similarities"])
    drafts = dict(payload["local_per_neighbor_middle_draft"])

    positive_drafts = list(drafts.get("positive_neighbors", []))
    negative_drafts = list(drafts.get("negative_neighbors", []))
    flat_drafts = positive_drafts + negative_drafts

    if len(similarities) != len(flat_drafts):
        raise ValueError(
            "Mismatch between neighbor similarity rows and per-neighbor local middle drafts "
            f"({len(similarities)} vs {len(flat_drafts)})"
        )

    rows: list[dict[str, Any]] = []
    for similarity_row, draft_row in zip(similarities, flat_drafts, strict=True):
        rows.append(
            {
                "neighbor_role": str(similarity_row["neighbor_role"]),
                "similarity": float(similarity_row["similarity"]),
                "middle_draft": str(draft_row["middle_draft"]),
            }
        )
    return rows


def _extract_reasoning_text_from_json(payload: dict[str, Any]) -> str:
    for key in (
        "global_reasoning",
        "reasoning",
        "local_reasoning",
        "hybrid_reasoning",
        "final_reasoning",
        "final_cot",
    ):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    raise ValueError("Could not extract reasoning text from JSON payload")


def resolve_reasoning_text(value: str | Path | None) -> str | None:
    if value is None:
        return None

    candidate_path = Path(str(value)).expanduser()
    if candidate_path.exists():
        if candidate_path.suffix.lower() == ".json":
            return _extract_reasoning_text_from_json(load_json(candidate_path))
        return candidate_path.read_text(encoding="utf-8").strip()

    return str(value).strip()


def render_rewrite_prompt(
    *,
    candidate_payload: dict[str, Any],
    mode: str,
    template_root: str | Path | None = None,
    global_reasoning: str | None = None,
    local_reasoning: str | None = None,
    hybrid_reasoning: str | None = None,
) -> str:
    if candidate_payload.get("schema_version") != REWRITE_CANDIDATE_SCHEMA_VERSION:
        raise ValueError("Unsupported candidate schema version")

    template_text = _load_template(mode, template_root=template_root)

    if mode == "global":
        payload = candidate_payload["global_rewrite_input"]
        return _replace_slots(
            template_text,
            {
                "TASK_DESCRIPTION": str(payload["task_description"]),
                "TASK_PLAYBOOK": str(payload["task_playbook"]),
                "GLOBAL_MIDDLE_DRAFT": str(payload["global_middle_draft"]),
            },
        )

    if mode == "local":
        payload = candidate_payload["local_rewrite_input"]
        flattened_neighbors = _flatten_local_neighbors(payload)
        replacements = {
            "TASK_PLAYBOOK": str(payload["task_playbook"]),
            "TASK_DESCRIPTION": str(payload["task_description"]),
            "POSITIVE_LABEL_SEMANTICS": str(payload["positive_label_semantics"]),
            "NEGATIVE_LABEL_SEMANTICS": str(payload["negative_label_semantics"]),
            "LOCAL_PREDICTION": str(payload["local_prediction"]),
            "LOCAL_PREDICTION_SEMANTICS": str(
                payload.get("local_prediction_semantics", payload["local_prediction"])
            ),
        }
        for index, neighbor_row in enumerate(flattened_neighbors, start=1):
            replacements[f"NEIGHBOR_{index}_SIMILARITIES"] = _format_similarity(neighbor_row["similarity"])
            replacements[f"NEIGHBOR_{index}_LOCAL_MIDDLE_DRAFT"] = str(neighbor_row["middle_draft"])
        return _replace_slots(
            template_text,
            replacements,
        )

    if mode == "hybrid":
        if not global_reasoning or not local_reasoning:
            raise ValueError("Hybrid rewrite prompt requires both global_reasoning and local_reasoning")
        payload = candidate_payload["hybrid_rewrite_input"]
        return _replace_slots(
            template_text,
            {
                "SINGLE_MOLECULE_REASONING": global_reasoning,
                "MULTI_MOLECULE_COMPARISON_REASONING": local_reasoning,
                "GT_LABEL_SEMANTICS": _format_label_semantics(payload["gt_label_semantics"]),
            },
        )

    raise ValueError(f"Unsupported rewrite prompt mode: {mode}")
