from __future__ import annotations

from pathlib import Path

import pandas as pd

from trim.data.datasets import load_tdc_split
from trim.evaluation.metrics import compute_binary_classification_metrics
from trim.features.table_loader import build_feature_source_bundle
from trim.features.preprocessing import transform_feature_frame
from trim.utils.io import load_pickle, save_json


def evaluate_global_bundle(
    *,
    bundle_path: str | Path,
    split: str,
    dataset_root,
    output_dir: str | Path | None = None,
) -> dict[str, object]:
    bundle_path = Path(bundle_path)
    model_bundle = load_pickle(bundle_path)
    feature_bundle = build_feature_source_bundle(model_bundle["feature_config_paths"])

    task = str(model_bundle["task"])
    task_split = load_tdc_split(task, split, data_root=dataset_root)
    raw_feature_df = feature_bundle["feature_source"].load(task_split.smiles)
    _, transformed_df = transform_feature_frame(raw_feature_df, model_bundle["preprocessor"])
    x_matrix = transformed_df.to_numpy()

    model = model_bundle["model"]
    scores = model.predict_proba(x_matrix)[:, 1]
    predictions = model.predict(x_matrix)
    metrics = compute_binary_classification_metrics(task_split.labels, predictions, scores)

    payload = {
        "task": task,
        "split": split,
        "model_type": model_bundle["model_type"],
        "feature_set_name": model_bundle["feature_set_name"],
        "metrics": metrics,
    }

    if output_dir is not None:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        predictions_df = pd.DataFrame(
            {
                "smiles": task_split.smiles,
                "label": task_split.labels,
                "prediction": predictions,
                "score": scores,
                "scaffold": task_split.scaffolds,
            }
        )
        predictions_path = output_dir / f"{task}__{split}_predictions.csv"
        summary_path = output_dir / f"{task}__{split}_metrics.json"
        predictions_df.to_csv(predictions_path, index=False)
        payload["artifacts"] = {
            "predictions_csv": str(predictions_path.resolve()),
            "metrics_json": str(summary_path.resolve()),
        }
        save_json(summary_path, payload)

    return payload
