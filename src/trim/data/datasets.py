from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from trim.data.scaffold_utils import murcko_scaffold_smiles
from trim.utils.paths import DEFAULT_PROCESSED_DATA_ROOT


DEFAULT_SMILES_FIELD = "drug"
DEFAULT_LABEL_FIELD = "Y"


@dataclass(frozen=True)
class BinaryTaskSplit:
    task: str
    split: str
    smiles: list[str]
    labels: list[int]
    scaffolds: list[str]

    def to_frame(self) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "smiles": self.smiles,
                "label": self.labels,
                "scaffold": self.scaffolds,
            }
        )

    def label_by_smiles(self) -> dict[str, int]:
        return {smiles: int(label) for smiles, label in zip(self.smiles, self.labels)}

    def scaffold_by_smiles(self) -> dict[str, str]:
        return {smiles: scaffold for smiles, scaffold in zip(self.smiles, self.scaffolds)}


def normalize_binary_label(value: Any) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str) and value.strip() in {"0", "1"}:
        return int(value.strip())
    raise ValueError(f"Unsupported binary label value: {value!r}")


def get_split_path(task: str, split: str, data_root: str | Path = DEFAULT_PROCESSED_DATA_ROOT) -> Path:
    path = Path(data_root) / split / f"{task}.jsonl"
    if not path.exists():
        raise FileNotFoundError(f"Missing dataset split: {path}")
    return path


def list_tasks(data_root: str | Path = DEFAULT_PROCESSED_DATA_ROOT) -> list[str]:
    train_dir = Path(data_root) / "train"
    if not train_dir.exists():
        raise FileNotFoundError(f"Missing train directory: {train_dir}")
    return sorted(path.stem for path in train_dir.glob("*.jsonl"))


def load_tdc_split(
    task: str,
    split: str,
    data_root: str | Path = DEFAULT_PROCESSED_DATA_ROOT,
    smiles_field: str = DEFAULT_SMILES_FIELD,
    label_field: str = DEFAULT_LABEL_FIELD,
) -> BinaryTaskSplit:
    split_path = get_split_path(task, split, data_root=data_root)
    smiles: list[str] = []
    labels: list[int] = []
    scaffolds: list[str] = []

    with split_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            record = json.loads(line)
            if smiles_field not in record:
                raise KeyError(f"Missing smiles field {smiles_field!r} at {split_path}:{line_number}")
            if label_field not in record:
                raise KeyError(f"Missing label field {label_field!r} at {split_path}:{line_number}")
            smiles_value = str(record[smiles_field])
            smiles.append(smiles_value)
            labels.append(normalize_binary_label(record[label_field]))
            scaffolds.append(murcko_scaffold_smiles(smiles_value))

    return BinaryTaskSplit(
        task=task,
        split=split,
        smiles=smiles,
        labels=labels,
        scaffolds=scaffolds,
    )

