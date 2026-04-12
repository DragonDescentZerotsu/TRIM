# TRIM

TRIM is the new standalone project for scaffold-split TDC molecular classification. The current phase focuses on a pure-ML system with:

- a migrated global single-molecule EBM
- cached descriptor / FG / similarity assets owned through TRIM-local paths
- retrieval and pairwise-local infrastructure for the next phase of positive-neighbor / negative-neighbor EBMs

The main entrypoints are:

- `scripts/prepare_legacy_assets.py`
- `scripts/train_global_ebm.py`
- `scripts/evaluate_global_ebm.py`
- `scripts/train_pair_pos.py`
- `scripts/train_pair_neg.py`
- `scripts/run_local_only.py`
- `scripts/run_hybrid.py`

Project-local outputs are written under `outputs/`.

