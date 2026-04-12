from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = PROJECT_ROOT / "src"
CONFIGS_ROOT = PROJECT_ROOT / "configs"
DATA_ROOT = PROJECT_ROOT / "data"
OUTPUTS_ROOT = PROJECT_ROOT / "outputs"

DEFAULT_PROCESSED_DATA_ROOT = DATA_ROOT / "processed" / "tdc_no_conflict_labels_salt_removed"
DEFAULT_RDKIT_PKA_FEATURE_ROOT = DATA_ROOT / "features" / "rdkit_descriptors_and_pka_easy_to_NLP_Lv1"
DEFAULT_FG_FEATURE_ROOT = DATA_ROOT / "features" / "fg_top_level"
DEFAULT_SIMILARITY_CACHE_ROOT = DATA_ROOT / "cache" / "tdc_mol_fingerprints"

LEGACY_PROCESSED_DATA_ROOT = Path(
    "/data1/tianang/Projects/Intern-S1/DataPrepare/TDC_no_conflict_labels_salt_removed"
)
LEGACY_RDKIT_PKA_FEATURE_ROOT = Path(
    "/data1/tianang/Projects/Intern-S1/DataPrepare/mol_features_for_tree/"
    "rdkit_descriptors_and_pka_easy_to_NLP_Lv1"
)
LEGACY_FG_FEATURE_CSV = Path(
    "/data1/tianang/Projects/AccFG/FG_feature_extraction/extracted_FG_features/"
    "tdc_no_conflict_labels_salt_removed_unique_smiles_top_level_fg_vectors.csv"
)
LEGACY_SIMILARITY_CACHE_ROOT = Path(
    "/data1/tianang/Projects/Intern-S1/DataPrepare/TDC_mol_fingerprints"
)


def resolve_project_path(path_like: str | Path) -> Path:
    path = Path(path_like).expanduser()
    if path.is_absolute():
        return path
    return (PROJECT_ROOT / path).resolve()

