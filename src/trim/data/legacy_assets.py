from __future__ import annotations

import os
from pathlib import Path

from trim.utils.paths import (
    DEFAULT_FG_FEATURE_ROOT,
    DEFAULT_PROCESSED_DATA_ROOT,
    DEFAULT_RDKIT_PKA_FEATURE_ROOT,
    DEFAULT_SIMILARITY_CACHE_ROOT,
    LEGACY_FG_FEATURE_CSV,
    LEGACY_PROCESSED_DATA_ROOT,
    LEGACY_RDKIT_PKA_FEATURE_ROOT,
    LEGACY_SIMILARITY_CACHE_ROOT,
)


def ensure_symlink(link_path: str | Path, target_path: str | Path, *, force: bool = False) -> Path:
    link = Path(link_path)
    target = Path(target_path)
    link.parent.mkdir(parents=True, exist_ok=True)

    if link.exists() or link.is_symlink():
        if link.is_symlink() and link.resolve() == target.resolve():
            return link
        if not force:
            raise FileExistsError(f"{link} already exists. Use force=True to replace it.")
        if link.is_dir() and not link.is_symlink():
            raise IsADirectoryError(f"Refusing to replace non-symlink directory {link}")
        link.unlink()

    os.symlink(target, link, target_is_directory=target.is_dir())
    return link


def prepare_legacy_assets(*, force: bool = False) -> dict[str, str]:
    created: dict[str, str] = {}

    created["processed_data"] = str(
        ensure_symlink(DEFAULT_PROCESSED_DATA_ROOT, LEGACY_PROCESSED_DATA_ROOT, force=force)
    )
    created["rdkit_pka_feature_dir"] = str(
        ensure_symlink(DEFAULT_RDKIT_PKA_FEATURE_ROOT, LEGACY_RDKIT_PKA_FEATURE_ROOT, force=force)
    )

    DEFAULT_FG_FEATURE_ROOT.mkdir(parents=True, exist_ok=True)
    fg_target = DEFAULT_FG_FEATURE_ROOT / LEGACY_FG_FEATURE_CSV.name
    created["fg_feature_csv"] = str(ensure_symlink(fg_target, LEGACY_FG_FEATURE_CSV, force=force))

    created["similarity_cache"] = str(
        ensure_symlink(DEFAULT_SIMILARITY_CACHE_ROOT, LEGACY_SIMILARITY_CACHE_ROOT, force=force)
    )
    return created

