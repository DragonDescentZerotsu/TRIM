from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .paths import PROJECT_ROOT


def load_json_config(path_like: str | Path) -> Any:
    path = Path(path_like)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)

