from __future__ import annotations

from pathlib import Path

import pandas as pd

from trim.evaluation.metrics import compute_binary_classification_metrics
from trim.features.table_loader import load_task_feature_matrices
from trim.models.global_ebm import build_ebm_params, build_global_ebm
from trim.utils.io import save_json, save_pickle
from trim.utils.paths import serialize_project_path


def train_global_task(
    *,
    task: str,
    feature_bundle: dict[str, object],
    dataset_root,
    train_split_name: str = "train",
    valid_split_name: str = "valid",
    smiles_key: str = "drug",
    label_key: str = "Y",
    ebm_params: dict[str, object] | None = None,
    scale_features: bool = False,
    drop_any_nan_columns: bool = False,
    output_dir: str | Path = "outputs/models/global_ebm/default_experiment",
) -> dict[str, object]:
    ebm_params = dict(ebm_params or build_ebm_params())

    matrices = load_task_feature_matrices(
        task=task,
        dataset_root=dataset_root,
        train_split_name=train_split_name,
        valid_split_name=valid_split_name,
        smiles_key=smiles_key,
        label_key=label_key,
        feature_source=feature_bundle["feature_source"],
        scale_features=scale_features,
        drop_any_nan_columns=drop_any_nan_columns,
    )

    x_train = matrices["x_train"]
    y_train = matrices["y_train"]
    x_valid = matrices["x_valid"]
    y_valid = matrices["y_valid"]
    train_split = matrices["train_split"]
    valid_split = matrices["valid_split"]
    surviving_columns = matrices["surviving_columns"]
    preprocessor = matrices["preprocessor"]

    model = build_global_ebm(**ebm_params)
    model.fit(x_train, y_train)

    train_scores = model.predict_proba(x_train)[:, 1]
    valid_scores = model.predict_proba(x_valid)[:, 1]
    train_predictions = model.predict(x_train)
    valid_predictions = model.predict(x_valid)

    train_metrics = compute_binary_classification_metrics(y_train, train_predictions, train_scores)
    valid_metrics = compute_binary_classification_metrics(y_valid, valid_predictions, valid_scores)

    experiment_dir = Path(output_dir)
    task_output_dir = experiment_dir / task / str(feature_bundle["feature_set_name"])
    task_output_dir.mkdir(parents=True, exist_ok=True)

    train_predictions_df = pd.DataFrame(
        {
            "smiles": train_split.smiles,
            "label": y_train,
            "prediction": train_predictions,
            "score": train_scores,
            "scaffold": train_split.scaffolds,
        }
    )
    valid_predictions_df = pd.DataFrame(
        {
            "smiles": valid_split.smiles,
            "label": y_valid,
            "prediction": valid_predictions,
            "score": valid_scores,
            "scaffold": valid_split.scaffolds,
        }
    )
    train_predictions_csv = task_output_dir / "train_predictions.csv"
    valid_predictions_csv = task_output_dir / "valid_predictions.csv"
    train_predictions_df.to_csv(train_predictions_csv, index=False)
    valid_predictions_df.to_csv(valid_predictions_csv, index=False)

    model_bundle = {
        "task": task,
        "model_type": "global_ebm",
        "feature_set_name": feature_bundle["feature_set_name"],
        "feature_config_paths": feature_bundle["config_paths"],
        "feature_source": feature_bundle["feature_source"].describe(),
        "feature_columns": surviving_columns,
        "preprocessor": preprocessor,
        "ebm_params": ebm_params,
        "model": model,
        "metrics": {"train": train_metrics, "valid": valid_metrics},
    }
    model_bundle_path = task_output_dir / "model_bundle.pkl"
    save_pickle(model_bundle_path, model_bundle)

    summary = {
        "task": task,
        "model_type": "global_ebm",
        "experiment_name": experiment_dir.name,
        "experiment_dir": serialize_project_path(experiment_dir),
        "dataset_root": serialize_project_path(Path(dataset_root)),
        "train_split": train_split_name,
        "valid_split": valid_split_name,
        "feature_set_name": feature_bundle["feature_set_name"],
        "feature_config_paths": feature_bundle["config_paths"],
        "loaded_feature_configs": feature_bundle["loaded_configs"],
        "feature_source": feature_bundle["feature_source"].describe(),
        "num_surviving_features": len(surviving_columns),
        "surviving_feature_names": surviving_columns,
        "ebm_params": ebm_params,
        "scale_features": scale_features,
        "drop_any_nan_columns": drop_any_nan_columns,
        "final_model_metrics": {"train": train_metrics, "valid": valid_metrics},
        "artifacts": {
            "train_predictions_csv": serialize_project_path(train_predictions_csv),
            "valid_predictions_csv": serialize_project_path(valid_predictions_csv),
            "model_bundle_pkl": serialize_project_path(model_bundle_path),
        },
    }
    save_json(task_output_dir / "train_summary.json", summary)
    return summary
