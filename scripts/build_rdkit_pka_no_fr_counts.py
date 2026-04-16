#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


DEFAULT_INPUT = (
    "data/features/rdkit_descriptors_and_pka_easy_to_NLP_Lv1/"
    "tdc_no_conflict_labels_salt_removed_unique_smiles_rdkit_descriptors_and_pka_easy_to_NLP_Lv1.csv"
)
DEFAULT_OUTPUT = (
    "data/features/rdkit_descriptors_and_pka_easy_to_NLP_Lv1_no_fr_counts/"
    "tdc_no_conflict_labels_salt_removed_unique_smiles_rdkit_descriptors_and_pka_easy_to_NLP_Lv1_no_fr_counts.csv"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a cached rdkit+pKa feature table with all rdkit__fr_* columns removed."
    )
    parser.add_argument("--input-csv", default=DEFAULT_INPUT)
    parser.add_argument("--output-csv", default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_csv = Path(args.input_csv)
    output_csv = Path(args.output_csv)

    frame = pd.read_csv(input_csv)
    keep_columns = [
        column
        for column in frame.columns
        if column == "smiles" or not str(column).startswith("rdkit__fr_")
    ]
    filtered = frame[keep_columns]

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    filtered.to_csv(output_csv, index=False)

    num_total_features = len(frame.columns) - 1
    num_filtered_features = len(filtered.columns) - 1
    num_removed_features = num_total_features - num_filtered_features
    print(f"input_csv={input_csv.resolve()}")
    print(f"output_csv={output_csv.resolve()}")
    print(f"num_total_features={num_total_features}")
    print(f"num_filtered_features={num_filtered_features}")
    print(f"num_removed_features={num_removed_features}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
