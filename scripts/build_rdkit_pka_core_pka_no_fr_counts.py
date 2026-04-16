#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


CORE_PKA_COLUMNS = (
    "pka__fraction_neutral",
    "pka__logd_estimate",
    "pka__num_acidic_sites",
    "pka__num_basic_sites",
    "pka__num_ionizable_sites",
    "pka__most_acidic_pka",
    "pka__most_basic_pka",
)

DEFAULT_INPUT = (
    "data/features/rdkit_descriptors_and_pka_easy_to_NLP_Lv1_no_fr_counts/"
    "tdc_no_conflict_labels_salt_removed_unique_smiles_rdkit_descriptors_and_pka_easy_to_NLP_Lv1_no_fr_counts.csv"
)
DEFAULT_OUTPUT = (
    "data/features/rdkit_descriptors_and_pka_easy_to_NLP_Lv1_core_pka_no_fr_counts/"
    "tdc_no_conflict_labels_salt_removed_unique_smiles_rdkit_descriptors_and_pka_easy_to_NLP_Lv1_core_pka_no_fr_counts.csv"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build a cached rdkit+pKa feature table that keeps all non-fr-count RDKit descriptors "
            "but only a small core set of pKa features."
        )
    )
    parser.add_argument("--input-csv", default=DEFAULT_INPUT)
    parser.add_argument("--output-csv", default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_csv = Path(args.input_csv)
    output_csv = Path(args.output_csv)

    frame = pd.read_csv(input_csv)
    present_core_pka = [column for column in CORE_PKA_COLUMNS if column in frame.columns]
    missing_core_pka = [column for column in CORE_PKA_COLUMNS if column not in frame.columns]

    keep_columns = [
        column
        for column in frame.columns
        if column == "smiles" or not str(column).startswith("pka__") or column in present_core_pka
    ]
    filtered = frame[keep_columns]

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    filtered.to_csv(output_csv, index=False)

    pka_columns = [column for column in frame.columns if str(column).startswith("pka__")]
    kept_pka_columns = [column for column in keep_columns if str(column).startswith("pka__")]
    print(f"input_csv={input_csv.resolve()}")
    print(f"output_csv={output_csv.resolve()}")
    print(f"num_total_features={len(frame.columns) - 1}")
    print(f"num_filtered_features={len(filtered.columns) - 1}")
    print(f"num_total_pka_features={len(pka_columns)}")
    print(f"num_kept_pka_features={len(kept_pka_columns)}")
    print(f"kept_pka_columns={kept_pka_columns}")
    if missing_core_pka:
        print(f"missing_core_pka_columns={missing_core_pka}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
