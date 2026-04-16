#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


DROP_RDKIT_COLUMNS = (
    "rdkit__NHOHCount",
    "rdkit__NOCount",
)

DEFAULT_INPUT = (
    "data/features/rdkit_descriptors_and_pka_easy_to_NLP_Lv1_core_pka_no_fr_counts/"
    "tdc_no_conflict_labels_salt_removed_unique_smiles_rdkit_descriptors_and_pka_easy_to_NLP_Lv1_core_pka_no_fr_counts.csv"
)
DEFAULT_OUTPUT = (
    "data/features/rdkit_descriptors_and_pka_easy_to_NLP_Lv1_core_pka_no_fr_no_nhoh_no_count/"
    "tdc_no_conflict_labels_salt_removed_unique_smiles_rdkit_descriptors_and_pka_easy_to_NLP_Lv1_core_pka_no_fr_no_nhoh_no_count.csv"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build a cached rdkit+pKa feature table from the default core-pKa no-fr version, "
            "while dropping rdkit__NHOHCount and rdkit__NOCount."
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
    dropped_present = [column for column in DROP_RDKIT_COLUMNS if column in frame.columns]
    missing_requested = [column for column in DROP_RDKIT_COLUMNS if column not in frame.columns]

    keep_columns = [
        column
        for column in frame.columns
        if column == "smiles" or column not in set(dropped_present)
    ]
    filtered = frame[keep_columns]

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    filtered.to_csv(output_csv, index=False)

    print(f"input_csv={input_csv.resolve()}")
    print(f"output_csv={output_csv.resolve()}")
    print(f"num_total_features={len(frame.columns) - 1}")
    print(f"num_filtered_features={len(filtered.columns) - 1}")
    print(f"dropped_rdkit_columns={dropped_present}")
    if missing_requested:
        print(f"missing_requested_drop_columns={missing_requested}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
