#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from trim.features.table_loader import build_feature_source_bundle
from trim.features.pair_features import build_pair_matrix, coerce_numeric_feature_frame
from trim.utils.io import load_json, load_pickle, save_json
from trim.utils.paths import resolve_project_path, serialize_project_path

try:
    from tqdm.auto import tqdm
except ImportError:

    def tqdm(iterable=None, **kwargs):
        return iterable


DEFAULT_MANIFEST_INDEX = (
    "outputs/reasoning_agent_tools/manifests/"
    "fg_top_level+rdkit_descriptors_and_pka_easy_to_NLP_Lv1_core_pka_no_fr_counts/manifest_index.json"
)
DEFAULT_OUTPUT_DIR = "outputs/metrics/local_pair_term_coverage_core_pka_no_fr_counts"
DEFAULT_DATASET_ROOT = "data/processed/tdc_no_conflict_labels_salt_removed"
DEFAULT_CACHE_ROOT = "data/cache/tdc_mol_fingerprints"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Measure how much local pair-EBM feature-term contribution mass is covered by top-k terms."
        )
    )
    parser.add_argument("--manifest-index", default=DEFAULT_MANIFEST_INDEX)
    parser.add_argument("--dataset-root", default=DEFAULT_DATASET_ROOT)
    parser.add_argument("--cache-root", default=DEFAULT_CACHE_ROOT)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--split",
        action="append",
        dest="splits",
        default=None,
        help="Split to analyze. Repeat for multiple splits. Defaults to train.",
    )
    parser.add_argument(
        "--task",
        action="append",
        dest="tasks",
        default=None,
        help="Task to analyze. Repeat for multiple tasks. Defaults to all tasks.",
    )
    parser.add_argument(
        "--k-values",
        default="1,2,3,4,5,6,8,10,12,15,20",
        help="Comma-separated top-k values for coverage summaries.",
    )
    parser.add_argument(
        "--thresholds",
        default="0.75,0.8,0.85,0.9,0.95",
        help="Comma-separated coverage thresholds for required-k summaries.",
    )
    parser.add_argument("--chunk-size", type=int, default=4096)
    parser.add_argument(
        "--max-pairs-per-group",
        type=int,
        default=None,
        help="Optional deterministic cap per task/split/model for quick smoke checks.",
    )
    return parser.parse_args()


def parse_int_list(value: str) -> list[int]:
    parsed = [int(item.strip()) for item in value.split(",") if item.strip()]
    if not parsed or min(parsed) < 1:
        raise ValueError(f"Expected positive integer list, got {value!r}")
    return sorted(set(parsed))


def parse_float_list(value: str) -> list[float]:
    parsed = [float(item.strip()) for item in value.split(",") if item.strip()]
    if not parsed or min(parsed) <= 0.0 or max(parsed) >= 1.0:
        raise ValueError(f"Expected thresholds in (0, 1), got {value!r}")
    return sorted(set(parsed))


def selected_task_rows(index_payload: dict[str, object], requested_tasks: list[str] | None) -> list[dict[str, object]]:
    rows = list(index_payload["tasks"])
    if requested_tasks is None:
        return rows
    requested = set(requested_tasks)
    selected = [row for row in rows if str(row["task"]) in requested]
    missing = sorted(requested.difference({str(row["task"]) for row in selected}))
    if missing:
        raise ValueError(f"Tasks not found in manifest index: {missing}")
    return selected


def feature_family(feature_name: str) -> str:
    if feature_name.startswith("fg_top_level__"):
        return "fg_top_level"
    if feature_name.startswith("rdkit_pka__pka__"):
        return "pka"
    if feature_name.startswith("rdkit_pka__rdkit__"):
        return "rdkit"
    return "other"


def pair_prediction_csv_path(bundle_path: Path, model_role: str, split: str) -> Path:
    prefix = "pos" if model_role == "positive_neighbor_model" else "neg"
    return bundle_path.parent / f"{prefix}_{split}_pair_predictions.csv"


def resolve_raw_feature_columns(bundle: dict[str, object]) -> list[str]:
    pair_columns = [str(column) for column in bundle.get("pair_columns", [])]
    if pair_columns:
        base_columns = [column.removesuffix("__base") for column in pair_columns[0::2]]
        if all(base_columns):
            return base_columns
    return [str(column) for column in bundle["raw_feature_columns"]]


def load_pair_matrix_from_prediction_csv(
    *,
    csv_path: Path,
    feature_source,
    raw_feature_columns: list[str],
    max_pairs: int | None,
) -> tuple[np.ndarray, np.ndarray]:
    metadata = pd.read_csv(csv_path)
    if max_pairs is not None and len(metadata) > max_pairs:
        metadata = metadata.iloc[:max_pairs].reset_index(drop=True)
    query_smiles = metadata["query_smiles"].astype(str).tolist()
    neighbor_smiles = metadata["neighbor_smiles"].astype(str).tolist()
    query_df = coerce_numeric_feature_frame(feature_source.load(query_smiles))[raw_feature_columns].reset_index(
        drop=True
    )
    neighbor_df = coerce_numeric_feature_frame(feature_source.load(neighbor_smiles))[raw_feature_columns].reset_index(
        drop=True
    )
    pair_matrix = build_pair_matrix(
        query_values=query_df.to_numpy(dtype=float),
        neighbor_values=neighbor_df.to_numpy(dtype=float),
    )
    return pair_matrix, metadata["query_label"].to_numpy(dtype=int)


def update_quantile_summary(prefix: str, values: np.ndarray, row: dict[str, object]) -> None:
    finite = values[np.isfinite(values)]
    if finite.size == 0:
        for suffix in ["mean", "p10", "p25", "p50", "p75", "p90", "p95"]:
            row[f"{prefix}_{suffix}"] = math.nan
        return
    row[f"{prefix}_mean"] = float(np.mean(finite))
    for quantile in [10, 25, 50, 75, 90, 95]:
        row[f"{prefix}_p{quantile}"] = float(np.percentile(finite, quantile))


def summarize_group(
    *,
    group: pd.DataFrame,
    task: str,
    split: str,
    model_role: str,
    query_label: int | str,
    k_values: list[int],
    thresholds: list[float],
) -> dict[str, object]:
    row: dict[str, object] = {
        "task": task,
        "split": split,
        "model_role": model_role,
        "query_label": query_label,
        "n_pairs": int(len(group)),
        "zero_abs_pairs": int((group["total_abs_contribution"] <= 0.0).sum()),
    }
    nonzero = group[group["total_abs_contribution"] > 0.0]
    for k in k_values:
        column = f"coverage_top_{k}"
        values = nonzero[column].to_numpy(dtype=float) if column in nonzero else np.asarray([], dtype=float)
        update_quantile_summary(column, values, row)
        for threshold in thresholds:
            if values.size:
                row[f"frac_top_{k}_ge_{int(threshold * 100)}"] = float(np.mean(values >= threshold))
            else:
                row[f"frac_top_{k}_ge_{int(threshold * 100)}"] = math.nan
    for threshold in thresholds:
        column = f"k_for_{int(threshold * 100)}"
        values = nonzero[column].to_numpy(dtype=float) if column in nonzero else np.asarray([], dtype=float)
        update_quantile_summary(column, values, row)
    return row


def analyze_pair_matrix(
    *,
    model,
    pair_matrix: np.ndarray,
    raw_feature_columns: list[str],
    task: str,
    split: str,
    model_role: str,
    query_labels: np.ndarray,
    k_values: list[int],
    thresholds: list[float],
    chunk_size: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    max_k = min(max(k_values), len(raw_feature_columns))
    effective_k_values = [k for k in k_values if k <= len(raw_feature_columns)]
    coverage_rows: list[dict[str, object]] = []
    top_feature_counter: Counter[tuple[int, str, str]] = Counter()

    for start in tqdm(range(0, pair_matrix.shape[0], chunk_size), desc=f"{task} {split} {model_role} eval_terms"):
        stop = min(start + chunk_size, pair_matrix.shape[0])
        term_matrix = np.asarray(model.eval_terms(pair_matrix[start:stop]), dtype=float)
        abs_terms = np.abs(term_matrix)
        total_abs = abs_terms.sum(axis=1)
        order = np.argsort(-abs_terms, axis=1)
        sorted_abs = np.take_along_axis(abs_terms, order[:, :max_k], axis=1)
        cumulative = np.cumsum(sorted_abs, axis=1)

        for local_index in range(stop - start):
            global_index = start + local_index
            total = float(total_abs[local_index])
            row: dict[str, object] = {
                "task": task,
                "split": split,
                "model_role": model_role,
                "query_label": int(query_labels[global_index]),
                "pair_index": int(global_index),
                "total_abs_contribution": total,
            }
            if total > 0.0:
                for k in effective_k_values:
                    row[f"coverage_top_{k}"] = float(cumulative[local_index, k - 1] / total)
                full_sorted = np.sort(abs_terms[local_index])[::-1]
                full_cumulative = np.cumsum(full_sorted)
                for threshold in thresholds:
                    needed = int(np.searchsorted(full_cumulative, threshold * total, side="left") + 1)
                    row[f"k_for_{int(threshold * 100)}"] = needed
            else:
                for k in effective_k_values:
                    row[f"coverage_top_{k}"] = math.nan
                for threshold in thresholds:
                    row[f"k_for_{int(threshold * 100)}"] = 0

            for rank, feature_index in enumerate(order[local_index, :max_k], start=1):
                feature_name = raw_feature_columns[int(feature_index)]
                top_feature_counter[(rank, feature_name, feature_family(feature_name))] += 1
            coverage_rows.append(row)

    coverage_df = pd.DataFrame(coverage_rows)
    feature_rows = [
        {
            "task": task,
            "split": split,
            "model_role": model_role,
            "rank": rank,
            "feature_name": feature_name,
            "feature_family": family,
            "count": count,
        }
        for (rank, feature_name, family), count in top_feature_counter.most_common()
    ]
    return coverage_df, pd.DataFrame(feature_rows)


def main() -> int:
    args = parse_args()
    manifest_index_path = resolve_project_path(args.manifest_index)
    index_payload = load_json(manifest_index_path)
    task_rows = selected_task_rows(index_payload, args.tasks)
    splits = args.splits or ["train"]
    k_values = parse_int_list(args.k_values)
    thresholds = parse_float_list(args.thresholds)
    output_dir = resolve_project_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    all_coverage_frames: list[pd.DataFrame] = []
    all_feature_frames: list[pd.DataFrame] = []
    summary_rows: list[dict[str, object]] = []

    for task_row in tqdm(task_rows, desc="Tasks"):
        task = str(task_row["task"])
        manifest = load_json(resolve_project_path(task_row["manifest_path"]))
        bundle_paths = {
            str(name): resolve_project_path(path)
            for name, path in dict(manifest["bundle_paths"]).items()
        }
        local_tool = dict(manifest["local_tool"])

        pos_bundle = load_pickle(bundle_paths["pos_bundle_path"])
        neg_bundle = load_pickle(bundle_paths["neg_bundle_path"])
        feature_bundle = build_feature_source_bundle(pos_bundle["feature_config_paths"])
        feature_source = feature_bundle["feature_source"]

        for split in splits:
            for model_role, bundle, bundle_path in [
                ("positive_neighbor_model", pos_bundle, bundle_paths["pos_bundle_path"]),
                ("negative_neighbor_model", neg_bundle, bundle_paths["neg_bundle_path"]),
            ]:
                raw_feature_columns = resolve_raw_feature_columns(bundle)
                csv_path = pair_prediction_csv_path(Path(bundle_path), model_role, split)
                if not csv_path.exists():
                    raise FileNotFoundError(
                        f"Expected saved pair prediction metadata at {csv_path}. "
                        "Run pair training/evaluation for this split first, or analyze train/valid."
                    )
                pair_matrix, query_labels = load_pair_matrix_from_prediction_csv(
                    csv_path=csv_path,
                    feature_source=feature_source,
                    raw_feature_columns=raw_feature_columns,
                    max_pairs=args.max_pairs_per_group,
                )
                coverage_df, feature_df = analyze_pair_matrix(
                    model=bundle["model"],
                    pair_matrix=pair_matrix,
                    raw_feature_columns=raw_feature_columns,
                    task=task,
                    split=split,
                    model_role=model_role,
                    query_labels=query_labels,
                    k_values=k_values,
                    thresholds=thresholds,
                    chunk_size=args.chunk_size,
                )
                all_coverage_frames.append(coverage_df)
                all_feature_frames.append(feature_df)

                for query_label, group in coverage_df.groupby("query_label"):
                    summary_rows.append(
                        summarize_group(
                            group=group,
                            task=task,
                            split=split,
                            model_role=model_role,
                            query_label=int(query_label),
                            k_values=k_values,
                            thresholds=thresholds,
                        )
                    )
                summary_rows.append(
                    summarize_group(
                        group=coverage_df,
                        task=task,
                        split=split,
                        model_role=model_role,
                        query_label="all",
                        k_values=k_values,
                        thresholds=thresholds,
                    )
                )

    coverage_all = pd.concat(all_coverage_frames, ignore_index=True) if all_coverage_frames else pd.DataFrame()
    feature_all = pd.concat(all_feature_frames, ignore_index=True) if all_feature_frames else pd.DataFrame()
    summary_df = pd.DataFrame(summary_rows)

    if not coverage_all.empty:
        for keys in [
            ["split", "model_role", "query_label"],
            ["split", "query_label"],
            ["split", "model_role"],
            ["split"],
        ]:
            for group_key, group in coverage_all.groupby(keys):
                if not isinstance(group_key, tuple):
                    group_key = (group_key,)
                row = {
                    "task": "ALL_TASKS",
                    **{key: value for key, value in zip(keys, group_key)},
                }
                if "model_role" not in row:
                    row["model_role"] = "all"
                if "query_label" not in row:
                    row["query_label"] = "all"
                summary_rows.append(
                    summarize_group(
                        group=group,
                        task=str(row["task"]),
                        split=str(row["split"]),
                        model_role=str(row["model_role"]),
                        query_label=row["query_label"],
                        k_values=k_values,
                        thresholds=thresholds,
                    )
                )
        summary_df = pd.DataFrame(summary_rows)

    coverage_path = output_dir / "pair_term_coverage_rows.csv"
    summary_path = output_dir / "pair_term_coverage_summary.csv"
    feature_path = output_dir / "top_feature_frequency.csv"
    manifest_path = output_dir / "summary.json"

    coverage_all.to_csv(coverage_path, index=False)
    summary_df.to_csv(summary_path, index=False)
    feature_all.to_csv(feature_path, index=False)
    manifest_payload = {
        "schema_version": "trim_local_pair_term_coverage_v1",
        "manifest_index": serialize_project_path(manifest_index_path),
        "splits": splits,
        "tasks": [str(row["task"]) for row in task_rows],
        "k_values": k_values,
        "thresholds": thresholds,
        "coverage_rows_csv": serialize_project_path(coverage_path),
        "summary_csv": serialize_project_path(summary_path),
        "top_feature_frequency_csv": serialize_project_path(feature_path),
        "num_pairs": int(len(coverage_all)),
        "num_summary_rows": int(len(summary_df)),
    }
    save_json(manifest_path, manifest_payload)
    print(summary_df.tail(20).to_string(index=False))
    print(f"\nWrote {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
