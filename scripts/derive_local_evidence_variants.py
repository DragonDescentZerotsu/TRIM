#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
from pathlib import Path
import sys
from typing import Any

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from trim.reasoning.evidence.local_evidence import (
    DEFAULT_RANDOM_TOP_TERM_MAX,
    DEFAULT_RANDOM_TOP_TERM_MIN,
    _build_local_summary_middle_draft,
    _build_neighbor_middle_draft,
    _displayed_term_sum_payload,
    _resolve_label_semantics,
    _stable_rng,
)
from trim.utils.io import load_json, save_json
from trim.utils.paths import resolve_project_path, serialize_project_path


DEFAULT_INPUT_ROOT = "outputs/reasoning_evidence/local/all_tasks_core_pka_no_fr_counts"
DEFAULT_RANDOM_OUTPUT_ROOT = "outputs/reasoning_evidence/local/all_tasks_core_pka_no_fr_counts_random_k_3_6_seed17"
DEFAULT_SHUFFLED_OUTPUT_ROOT = "outputs/reasoning_evidence/local/all_tasks_core_pka_no_fr_counts_top6_shuffled_seed17"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Derive local reasoning-evidence variants from an existing ranked top-k local evidence root. "
            "This avoids re-running pair EBM scoring when the variant only removes or reorders already-exported terms."
        )
    )
    parser.add_argument("--input-root", default=DEFAULT_INPUT_ROOT)
    parser.add_argument("--variant", choices=["random_k_ranked", "top_k_shuffled", "both"], default="both")
    parser.add_argument("--random-output-root", default=DEFAULT_RANDOM_OUTPUT_ROOT)
    parser.add_argument("--shuffled-output-root", default=DEFAULT_SHUFFLED_OUTPUT_ROOT)
    parser.add_argument("--random-seed", type=int, default=17)
    parser.add_argument("--random-top-term-min", type=int, default=DEFAULT_RANDOM_TOP_TERM_MIN)
    parser.add_argument("--random-top-term-max", type=int, default=DEFAULT_RANDOM_TOP_TERM_MAX)
    parser.add_argument("--shuffled-top-term-k", type=int, default=6)
    parser.add_argument("--task", action="append", dest="tasks", default=None)
    parser.add_argument("--split", action="append", dest="splits", default=None)
    parser.add_argument("--prompt-root", default=None)
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow writing into an existing non-empty variant root.",
    )
    return parser.parse_args()


def _selected_tasks(input_root: Path, requested_tasks: list[str] | None) -> list[str]:
    available = sorted(path.name for path in input_root.iterdir() if path.is_dir())
    if requested_tasks is None:
        return available
    requested = set(requested_tasks)
    selected = [task for task in available if task in requested]
    missing = sorted(requested.difference(selected))
    if missing:
        raise ValueError(f"Tasks not found under {input_root}: {missing}")
    return selected


def _selected_splits(task_dir: Path, requested_splits: list[str] | None) -> list[str]:
    available = sorted(path.name for path in task_dir.iterdir() if path.is_dir())
    if requested_splits is None:
        return available
    requested = set(requested_splits)
    selected = [split for split in available if split in requested]
    missing = sorted(requested.difference(selected))
    if missing:
        raise ValueError(f"Splits not found under {task_dir}: {missing}")
    return selected


def _assert_can_write_root(path: Path, *, overwrite: bool) -> None:
    if not path.exists():
        return
    if overwrite:
        return
    try:
        next(path.iterdir())
    except StopIteration:
        return
    raise FileExistsError(f"Output root already exists and is non-empty: {path}. Use --overwrite to update it.")


def _label_semantics_from_record(record: dict[str, Any], prompt_root: str | Path | None) -> dict[int, dict[str, str]]:
    return _resolve_label_semantics(str(record["task"]), prompt_root=prompt_root)


def _ranked_source_terms(neighbor_evidence: dict[str, Any]) -> list[dict[str, Any]]:
    return sorted(
        [copy.deepcopy(dict(term)) for term in neighbor_evidence.get("top_pair_terms", [])],
        key=lambda term: int(term["contribution_rank"]),
    )


def _variant_rng(
    *,
    record: dict[str, Any],
    neighbor_evidence: dict[str, Any],
    row_index: int,
    random_seed: int,
) -> Any:
    return _stable_rng(
        random_seed=random_seed,
        parts=[
            record.get("task", ""),
            record.get("split", ""),
            record.get("sample_index", ""),
            record.get("smiles", ""),
            neighbor_evidence.get("neighbor_smiles", ""),
            neighbor_evidence.get("neighbor_label", ""),
            row_index,
            neighbor_evidence.get("pair_model_type", ""),
        ],
    )


def _select_terms(
    *,
    variant: str,
    source_terms: list[dict[str, Any]],
    rng: Any,
    random_top_term_min: int,
    random_top_term_max: int,
    shuffled_top_term_k: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if variant == "random_k_ranked":
        sampled_count = rng.randint(int(random_top_term_min), int(random_top_term_max))
        selected = source_terms[:sampled_count]
        selection = {
            "mode": "random_k_ranked",
            "requested_min_terms": int(random_top_term_min),
            "requested_max_terms": int(random_top_term_max),
            "sampled_term_count": int(sampled_count),
            "selected_term_count": int(len(selected)),
            "preserves_ranked_order": True,
            "source_top_pair_term_count": int(len(source_terms)),
        }
    elif variant == "top_k_shuffled":
        selected = source_terms[: int(shuffled_top_term_k)]
        rng.shuffle(selected)
        selection = {
            "mode": "top_k_shuffled",
            "requested_top_term_k": int(shuffled_top_term_k),
            "selected_term_count": int(len(selected)),
            "preserves_ranked_order": False,
            "source_top_pair_term_count": int(len(source_terms)),
        }
    else:
        raise ValueError(f"Unsupported variant: {variant}")

    normalized_terms = []
    for display_order, term in enumerate(selected, start=1):
        term = dict(term)
        term["display_order"] = int(display_order)
        normalized_terms.append(term)
    return normalized_terms, selection


def _update_neighbor_evidence(
    *,
    record: dict[str, Any],
    neighbor_evidence: dict[str, Any],
    row_index: int,
    variant: str,
    label_semantics: dict[int, dict[str, str]],
    random_seed: int,
    random_top_term_min: int,
    random_top_term_max: int,
    shuffled_top_term_k: int,
) -> dict[str, Any]:
    updated = copy.deepcopy(neighbor_evidence)
    source_terms = _ranked_source_terms(updated)
    rng = _variant_rng(
        record=record,
        neighbor_evidence=updated,
        row_index=row_index,
        random_seed=random_seed,
    )
    selected_terms, selection = _select_terms(
        variant=variant,
        source_terms=source_terms,
        rng=rng,
        random_top_term_min=random_top_term_min,
        random_top_term_max=random_top_term_max,
        shuffled_top_term_k=shuffled_top_term_k,
    )
    displayed_payload = _displayed_term_sum_payload(
        top_pair_terms=selected_terms,
        total_abs_feature_contribution=float(updated["total_abs_feature_contribution"]),
        label_semantics=label_semantics,
    )
    updated.update(displayed_payload)
    updated["displayed_teacher_agreement"] = int(updated["pair_prediction"]) == int(
        updated["displayed_feature_prediction"]
    )
    updated["teacher_aligned_evidence_strength"] = (
        str(updated["feature_evidence_strength"])
        if bool(updated["teacher_feature_agreement"]) and bool(updated["displayed_teacher_agreement"])
        else "low"
    )
    updated["term_selection"] = selection
    updated["top_pair_terms"] = selected_terms
    return updated


def _variant_record(
    *,
    source_record: dict[str, Any],
    variant: str,
    random_seed: int,
    random_top_term_min: int,
    random_top_term_max: int,
    shuffled_top_term_k: int,
    prompt_root: str | Path | None,
) -> dict[str, Any]:
    record = copy.deepcopy(source_record)
    label_semantics = _label_semantics_from_record(record, prompt_root)
    selection_summary = {
        "mode": variant,
        "top_term_k": int(shuffled_top_term_k if variant == "top_k_shuffled" else random_top_term_max),
        "random_top_term_min": int(random_top_term_min),
        "random_top_term_max": int(random_top_term_max),
        "random_seed": int(random_seed),
        "derived_from_source_local_evidence": True,
    }

    evidence = dict(record["local_per_neighbor_decision_evidence"])
    updated_evidence: dict[str, Any] = {
        "num_positive_neighbors": int(evidence["num_positive_neighbors"]),
        "num_negative_neighbors": int(evidence["num_negative_neighbors"]),
    }
    updated_middle: dict[str, list[dict[str, Any]]] = {}

    row_index_by_group = {"positive_neighbors": 0, "negative_neighbors": 0}
    for group_name in ("positive_neighbors", "negative_neighbors"):
        updated_rows = []
        updated_drafts = []
        for row in list(evidence.get(group_name, [])):
            row_index = row_index_by_group[group_name]
            row_index_by_group[group_name] += 1
            updated_row = _update_neighbor_evidence(
                record=record,
                neighbor_evidence=dict(row),
                row_index=row_index,
                variant=variant,
                label_semantics=label_semantics,
                random_seed=random_seed,
                random_top_term_min=random_top_term_min,
                random_top_term_max=random_top_term_max,
                shuffled_top_term_k=shuffled_top_term_k,
            )
            updated_rows.append(updated_row)
            updated_drafts.append(
                _build_neighbor_middle_draft(
                    neighbor_evidence=updated_row,
                    label_semantics=label_semantics,
                )
            )
        updated_evidence[group_name] = updated_rows
        updated_middle[group_name] = updated_drafts

    record["local_term_selection"] = selection_summary
    record["local_per_neighbor_decision_evidence"] = updated_evidence
    record["local_per_neighbor_middle_draft"] = updated_middle
    record["local_summary_middle_draft"] = _build_local_summary_middle_draft(
        pos_evidence=updated_evidence["positive_neighbors"],
        neg_evidence=updated_evidence["negative_neighbors"],
        local_score=float(record["local_score"]),
        s_pos=record.get("s_pos"),
        s_neg=record.get("s_neg"),
        local_prediction=int(record["local_prediction"]),
        label_semantics=label_semantics,
    )
    return record


def _derive_split(
    *,
    input_dir: Path,
    output_dir: Path,
    variant: str,
    random_seed: int,
    random_top_term_min: int,
    random_top_term_max: int,
    shuffled_top_term_k: int,
    prompt_root: str | Path | None,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    sample_paths = sorted(input_dir.glob("sample_*.json"))
    for sample_path in sample_paths:
        source_record = load_json(sample_path)
        record = _variant_record(
            source_record=source_record,
            variant=variant,
            random_seed=random_seed,
            random_top_term_min=random_top_term_min,
            random_top_term_max=random_top_term_max,
            shuffled_top_term_k=shuffled_top_term_k,
            prompt_root=prompt_root,
        )
        save_json(output_dir / sample_path.name, record)

    manifest_path = input_dir / "manifest.json"
    manifest = load_json(manifest_path) if manifest_path.exists() else {}
    manifest.update(
        {
            "artifacts": {"output_dir": serialize_project_path(output_dir)},
            "local_term_selection": {
                "mode": variant,
                "top_term_k": int(shuffled_top_term_k if variant == "top_k_shuffled" else random_top_term_max),
                "random_top_term_min": int(random_top_term_min),
                "random_top_term_max": int(random_top_term_max),
                "random_seed": int(random_seed),
                "derived_from_source_local_evidence": True,
                "source_dir": serialize_project_path(input_dir),
            },
            "num_records": int(len(sample_paths)),
            "sample_indices": [
                int(path.stem.removeprefix("sample_"))
                for path in sample_paths
            ],
        }
    )
    save_json(output_dir / "manifest.json", manifest)
    return {
        "input_dir": serialize_project_path(input_dir),
        "output_dir": serialize_project_path(output_dir),
        "num_records": int(len(sample_paths)),
    }


def _derive_variant(
    *,
    input_root: Path,
    output_root: Path,
    variant: str,
    tasks: list[str],
    requested_splits: list[str] | None,
    random_seed: int,
    random_top_term_min: int,
    random_top_term_max: int,
    shuffled_top_term_k: int,
    prompt_root: str | Path | None,
) -> dict[str, Any]:
    rows = []
    for task in tasks:
        task_dir = input_root / task
        for split in _selected_splits(task_dir, requested_splits):
            rows.append(
                {
                    "task": task,
                    "split": split,
                    **_derive_split(
                        input_dir=task_dir / split,
                        output_dir=output_root / task / split,
                        variant=variant,
                        random_seed=random_seed,
                        random_top_term_min=random_top_term_min,
                        random_top_term_max=random_top_term_max,
                        shuffled_top_term_k=shuffled_top_term_k,
                        prompt_root=prompt_root,
                    ),
                }
            )

    summary = {
        "schema_version": "trim_local_evidence_variant_summary_v1",
        "variant": variant,
        "input_root": serialize_project_path(input_root),
        "output_root": serialize_project_path(output_root),
        "random_seed": int(random_seed),
        "random_top_term_min": int(random_top_term_min),
        "random_top_term_max": int(random_top_term_max),
        "shuffled_top_term_k": int(shuffled_top_term_k),
        "tasks": tasks,
        "splits": requested_splits or "all",
        "num_rows": int(len(rows)),
        "num_records": int(sum(int(row["num_records"]) for row in rows)),
        "rows": rows,
    }
    save_json(output_root / "summary.json", summary)
    return summary


def main() -> int:
    args = parse_args()
    input_root = resolve_project_path(args.input_root)
    tasks = _selected_tasks(input_root, args.tasks)

    variants: list[tuple[str, Path]] = []
    if args.variant in {"random_k_ranked", "both"}:
        variants.append(("random_k_ranked", resolve_project_path(args.random_output_root)))
    if args.variant in {"top_k_shuffled", "both"}:
        variants.append(("top_k_shuffled", resolve_project_path(args.shuffled_output_root)))

    for variant, output_root in variants:
        if output_root == input_root:
            raise ValueError(f"Refusing to write variant {variant} into the input root: {output_root}")
        _assert_can_write_root(output_root, overwrite=args.overwrite)

    summaries = []
    for variant, output_root in variants:
        summaries.append(
            _derive_variant(
                input_root=input_root,
                output_root=output_root,
                variant=variant,
                tasks=tasks,
                requested_splits=args.splits,
                random_seed=args.random_seed,
                random_top_term_min=args.random_top_term_min,
                random_top_term_max=args.random_top_term_max,
                shuffled_top_term_k=args.shuffled_top_term_k,
                prompt_root=args.prompt_root,
            )
        )

    for summary in summaries:
        print(
            f"{summary['variant']}: wrote {summary['num_records']} records to {summary['output_root']}",
            flush=True,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
