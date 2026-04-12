from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Any


def ensure_directory(path_like: str | Path) -> Path:
    path = Path(path_like)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_json(path_like: str | Path, payload: dict[str, Any]) -> Path:
    path = Path(path_like)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
    return path


def load_json(path_like: str | Path) -> dict[str, Any]:
    with Path(path_like).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object at {path_like}, got {type(payload).__name__}")
    return payload


def save_pickle(path_like: str | Path, payload: Any) -> Path:
    path = Path(path_like)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        pickle.dump(payload, handle)
    return path


def load_pickle(path_like: str | Path) -> Any:
    with Path(path_like).open("rb") as handle:
        return pickle.load(handle)

