from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from trim.data.datasets import load_tdc_split
from trim.data.scaffold_utils import murcko_scaffold_smiles
from trim.utils.io import load_pickle
from trim.utils.paths import DEFAULT_SIMILARITY_CACHE_ROOT


@dataclass(frozen=True)
class NeighborRecord:
    smiles: str
    label: int
    similarity: float
    scaffold: str


def _parse_similarity_entry(entry: dict[str, object]) -> dict[str, dict[str, object]]:
    ref_dict: dict[str, dict[str, object]] = {}
    for label_name, label_value in (("label_0", 0), ("label_1", 1)):
        for score, ref_smiles in entry[label_name]:
            ref_dict[str(ref_smiles)] = {"score": float(score), "label": label_value}
    return ref_dict


class CachedSimilarityRetriever:
    def __init__(
        self,
        *,
        cache_root: str | Path = DEFAULT_SIMILARITY_CACHE_ROOT,
        morgan_weight: float = 0.8,
        feature_morgan_weight: float = 0.2,
        data_root=None,
    ):
        self.cache_root = Path(cache_root)
        self.morgan_weight = float(morgan_weight)
        self.feature_morgan_weight = float(feature_morgan_weight)
        self.data_root = data_root
        self._cache: dict[tuple[str, str, str], dict[str, object]] = {}
        self._train_metadata: dict[str, dict[str, dict[str, object]]] = {}
        self._candidate_cache: dict[tuple[str, str, str], list[NeighborRecord]] = {}

    def _load_similarity_file(self, task: str, family: str, split: str) -> dict[str, object]:
        cache_key = (task, family, split)
        if cache_key not in self._cache:
            path = self.cache_root / family / "by_task" / task / f"{split}_similarity.pkl"
            self._cache[cache_key] = load_pickle(path)
        return self._cache[cache_key]

    def _load_train_metadata(self, task: str) -> dict[str, dict[str, object]]:
        if task not in self._train_metadata:
            train_split = load_tdc_split(task, "train", data_root=self.data_root)
            self._train_metadata[task] = {
                smiles: {"label": int(label), "scaffold": scaffold}
                for smiles, label, scaffold in zip(
                    train_split.smiles,
                    train_split.labels,
                    train_split.scaffolds,
                )
            }
        return self._train_metadata[task]

    def get_neighbors(
        self,
        *,
        task: str,
        query_smiles: str,
        split: str,
        desired_label: int | None,
        top_k: int,
        exclude_same_scaffold: bool = False,
        query_scaffold: str | None = None,
    ) -> list[NeighborRecord]:
        cache_key = (task, split, query_smiles)
        if cache_key not in self._candidate_cache:
            morgan = self._load_similarity_file(task, "Morgan_similarity", split)
            feat_morgan = self._load_similarity_file(task, "Feature_Morgan_similarity", split)
            if query_smiles not in morgan or query_smiles not in feat_morgan:
                raise KeyError(f"Missing similarity entry for {task} {split} query {query_smiles}")

            m_refs = _parse_similarity_entry(morgan[query_smiles])
            f_refs = _parse_similarity_entry(feat_morgan[query_smiles])
            train_metadata = self._load_train_metadata(task)

            scored_neighbors: list[NeighborRecord] = []
            for ref_smiles in set(m_refs) | set(f_refs):
                m_score = float(m_refs.get(ref_smiles, {}).get("score", 0.0))
                f_score = float(f_refs.get(ref_smiles, {}).get("score", 0.0))
                ref_label = m_refs.get(ref_smiles, {}).get("label")
                if ref_label is None:
                    ref_label = f_refs.get(ref_smiles, {}).get("label")
                if ref_label is None:
                    continue
                if ref_smiles not in train_metadata:
                    continue

                scored_neighbors.append(
                    NeighborRecord(
                        smiles=ref_smiles,
                        label=int(ref_label),
                        similarity=(self.morgan_weight * m_score) + (self.feature_morgan_weight * f_score),
                        scaffold=str(train_metadata[ref_smiles]["scaffold"]),
                    )
                )

            scored_neighbors.sort(key=lambda item: item.similarity, reverse=True)
            self._candidate_cache[cache_key] = scored_neighbors

        if query_scaffold is None:
            query_scaffold = murcko_scaffold_smiles(query_smiles)

        filtered_neighbors: list[NeighborRecord] = []
        for neighbor in self._candidate_cache[cache_key]:
            if desired_label is not None and int(neighbor.label) != int(desired_label):
                continue
            if exclude_same_scaffold and query_scaffold == neighbor.scaffold:
                continue
            filtered_neighbors.append(neighbor)
            if len(filtered_neighbors) >= top_k:
                break
        return filtered_neighbors
