from __future__ import annotations

from pathlib import Path
from typing import Any

from trim.reasoning.rewrite.candidates import REWRITE_CANDIDATE_SCHEMA_VERSION
from trim.reasoning.rewrite.neighbor_selection import (
    display_index_by_source_index,
    format_neighbor_names,
    parse_source_neighbor_indices,
    relabel_neighbor_mentions,
)
from trim.utils.io import load_json
from trim.utils.paths import PROJECT_ROOT, resolve_project_path


DEFAULT_REWRITE_TEMPLATE_ROOT = PROJECT_ROOT / "prompt_templates" / "reasoning_sft"


def _load_template(mode: str, template_root: str | Path | None = None) -> str:
    root = DEFAULT_REWRITE_TEMPLATE_ROOT if template_root is None else resolve_project_path(template_root)
    mapping = {
        "global": "rewrite_global_reasoning.md",
        "local": "rewrite_local_reasoning.md",
        "local_neighbor": "rewrite_local_neighbor_reasoning.md",
        "local_summary": "rewrite_local_summary_reasoning.md",
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


def _find_local_neighbor(payload: dict[str, Any], *, neighbor_index: int) -> dict[str, Any]:
    neighbors = list(payload["neighbors"])
    for neighbor in neighbors:
        if int(neighbor["neighbor_index"]) == int(neighbor_index):
            return dict(neighbor)
    raise IndexError(f"Neighbor index {neighbor_index} not found in local per-neighbor rewrite input")


def _local_neighbors_by_index(payload: dict[str, Any]) -> dict[int, dict[str, Any]]:
    return {int(neighbor["neighbor_index"]): dict(neighbor) for neighbor in payload["neighbors"]}


def _prediction_semantics_from_output(parsed_output: dict[str, Any]) -> str:
    prediction = parsed_output.get("neighbor_prediction")
    if not isinstance(prediction, dict):
        raise ValueError("Neighbor rewrite output is missing neighbor_prediction object")
    option = prediction.get("option")
    text = prediction.get("text")
    if option is None or text is None:
        raise ValueError("Neighbor rewrite output prediction must contain option and text")
    return f"option ({option}): {text}"


def _prediction_option_from_output(parsed_output: dict[str, Any]) -> str:
    prediction = parsed_output.get("neighbor_prediction")
    if not isinstance(prediction, dict):
        raise ValueError("Neighbor rewrite output is missing neighbor_prediction object")
    option = prediction.get("option")
    if option not in {"A", "B"}:
        raise ValueError(f"Neighbor rewrite output prediction has invalid option: {option!r}")
    return str(option)


def _format_neighbor_vote_count(votes_by_option: dict[str, list[int]]) -> str:
    def _format_indices(indices: list[int]) -> str:
        if not indices:
            return "none"
        return ", ".join(f"Neighbor {index}" for index in indices)

    a_indices = votes_by_option.get("A", [])
    b_indices = votes_by_option.get("B", [])
    return (
        f"option (A): {len(a_indices)} neighbor(s) ({_format_indices(a_indices)}); "
        f"option (B): {len(b_indices)} neighbor(s) ({_format_indices(b_indices)})"
    )


def _format_selected_neighbor_comparisons(rows: list[dict[str, str]]) -> str:
    blocks: list[str] = []
    for row in rows:
        blocks.append(
            "\n".join(
                [
                    f"Neighbor {row['display_index']}",
                    f"Neighbor label: {row['label_semantics']}",
                    f"Similarity to query: {row['similarity']}",
                    f"Neighbor-level prediction: {row['prediction_semantics']}",
                    f"Evidence strength: {row['evidence_strength']}",
                    f"Reasoning: {row['reasoning']}",
                ]
            )
        )
    return "\n\n".join(blocks)


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
    neighbor_index: int | None = None,
    local_neighbor_outputs: dict[int, dict[str, Any]] | None = None,
    summary_source_neighbor_indices: object = None,
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

    if mode == "local_neighbor":
        if neighbor_index is None:
            raise ValueError("local_neighbor rewrite prompt requires neighbor_index")
        payload = candidate_payload["local_per_neighbor_rewrite_input"]
        neighbor = _find_local_neighbor(payload, neighbor_index=int(neighbor_index))
        resolved_neighbor_index = int(neighbor["neighbor_index"])
        return _replace_slots(
            template_text,
            {
                "TASK_PLAYBOOK": str(payload["task_playbook"]),
                "TASK_DESCRIPTION": str(payload["task_description"]),
                "POSITIVE_LABEL_SEMANTICS": str(payload["positive_label_semantics"]),
                "NEGATIVE_LABEL_SEMANTICS": str(payload["negative_label_semantics"]),
                "NEIGHBOR_INDEX": str(resolved_neighbor_index),
                "NEIGHBOR_INDEX_JSON": str(resolved_neighbor_index),
                "NEIGHBOR_LABEL_SEMANTICS": str(neighbor["neighbor_label_semantics"]),
                "NEIGHBOR_SIMILARITY": _format_similarity(neighbor["neighbor_similarity"]),
                "NEIGHBOR_MIDDLE_DRAFT": str(neighbor["middle_draft"]),
                "NEIGHBOR_PREDICTION_SEMANTICS": str(neighbor["pair_teacher"]["pair_prediction_semantics"]),
                "NEIGHBOR_EVIDENCE_STRENGTH": str(
                    neighbor["evidence_strength"]["teacher_aligned_evidence_strength"]
                ),
            },
        )

    if mode == "local_summary":
        if local_neighbor_outputs is None:
            raise ValueError("local_summary rewrite prompt requires local_neighbor_outputs")
        payload = candidate_payload["local_per_neighbor_rewrite_input"]
        local_payload = candidate_payload["local_rewrite_input"]
        neighbors_by_index = _local_neighbors_by_index(payload)
        source_neighbor_indices = parse_source_neighbor_indices(summary_source_neighbor_indices)
        source_to_display = display_index_by_source_index(source_neighbor_indices)
        replacements = {
            "POSITIVE_LABEL_SEMANTICS": str(payload["positive_label_semantics"]),
            "NEGATIVE_LABEL_SEMANTICS": str(payload["negative_label_semantics"]),
            "LOCAL_TEACHER_PREDICTION_SEMANTICS": str(local_payload["local_prediction_semantics"]),
            "SELECTED_NEIGHBOR_COUNT": str(len(source_neighbor_indices)),
            "SELECTED_NEIGHBOR_NAMES": format_neighbor_names(len(source_neighbor_indices)),
        }
        votes_by_option: dict[str, list[int]] = {"A": [], "B": []}
        comparison_rows: list[dict[str, str]] = []
        for display_index, source_index in enumerate(source_neighbor_indices, start=1):
            if source_index not in neighbors_by_index:
                raise ValueError(f"local_summary missing candidate neighbor {source_index}")
            if source_index not in local_neighbor_outputs:
                raise ValueError(f"local_summary missing neighbor rewrite output {source_index}")
            neighbor = neighbors_by_index[source_index]
            output_payload = local_neighbor_outputs[source_index]
            parsed_output = output_payload.get("parsed_output", output_payload)
            if not isinstance(parsed_output, dict):
                raise ValueError(f"Neighbor {source_index} output must be a JSON object")
            reasoning = str(parsed_output.get("reasoning", "") or "").strip()
            if not reasoning:
                raise ValueError(f"Neighbor {source_index} output is missing reasoning")
            votes_by_option[_prediction_option_from_output(parsed_output)].append(display_index)
            relabeled_reasoning = relabel_neighbor_mentions(
                reasoning,
                source_to_display=source_to_display,
            )
            comparison_rows.append(
                {
                    "display_index": str(display_index),
                    "source_index": str(source_index),
                    "label_semantics": str(neighbor["neighbor_label_semantics"]),
                    "similarity": _format_similarity(neighbor["neighbor_similarity"]),
                    "prediction_semantics": _prediction_semantics_from_output(parsed_output),
                    "evidence_strength": str(parsed_output["evidence_strength"]),
                    "reasoning": relabeled_reasoning,
                }
            )
        replacements["NEIGHBOR_PREDICTION_VOTE_COUNT"] = _format_neighbor_vote_count(votes_by_option)
        replacements["SELECTED_NEIGHBOR_COMPARISONS"] = _format_selected_neighbor_comparisons(
            comparison_rows
        )
        return _replace_slots(template_text, replacements)

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
