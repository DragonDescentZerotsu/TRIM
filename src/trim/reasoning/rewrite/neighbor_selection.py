from __future__ import annotations

import re
from collections.abc import Iterable


DEFAULT_LOCAL_SUMMARY_SOURCE_NEIGHBOR_INDICES: tuple[int, ...] = (1, 2, 3, 4, 5, 6)


def parse_source_neighbor_indices(value: object = None) -> tuple[int, ...]:
    if value is None:
        return DEFAULT_LOCAL_SUMMARY_SOURCE_NEIGHBOR_INDICES
    if isinstance(value, str):
        parts = [part.strip() for part in value.split(",")]
        raw_indices = [int(part) for part in parts if part]
    elif isinstance(value, Iterable):
        raw_indices = [int(part) for part in value]
    else:
        raise TypeError(f"Unsupported neighbor index specification: {value!r}")

    if not raw_indices:
        raise ValueError("At least one source neighbor index is required")
    if any(index < 1 for index in raw_indices):
        raise ValueError(f"Neighbor indices must be 1-based positive integers: {raw_indices!r}")
    if len(set(raw_indices)) != len(raw_indices):
        raise ValueError(f"Neighbor indices must be unique: {raw_indices!r}")
    return tuple(raw_indices)


def display_index_by_source_index(source_neighbor_indices: object = None) -> dict[int, int]:
    return {
        source_index: display_index
        for display_index, source_index in enumerate(
            parse_source_neighbor_indices(source_neighbor_indices),
            start=1,
        )
    }


def relabel_neighbor_mentions(text: str, *, source_to_display: dict[int, int]) -> str:
    if not source_to_display:
        return text

    pattern = re.compile(r"\b(Neighbors?)\s+([0-9]+)\b")

    def _replace(match: re.Match[str]) -> str:
        source_index = int(match.group(2))
        display_index = source_to_display.get(source_index)
        if display_index is None:
            return match.group(0)
        return f"{match.group(1)} {display_index}"

    return pattern.sub(_replace, text)


def format_neighbor_names(count: int) -> str:
    if count < 1:
        raise ValueError(f"Neighbor count must be positive, got {count}")
    names = [f"`Neighbor {index}`" for index in range(1, int(count) + 1)]
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    return f"{', '.join(names[:-1])}, and {names[-1]}"


def infer_neighbors_per_label(source_neighbor_indices: object = None) -> int:
    indices = parse_source_neighbor_indices(source_neighbor_indices)
    for neighbors_per_label in (1, 2, 3):
        expected = tuple(range(1, neighbors_per_label + 1)) + tuple(
            range(4, 4 + neighbors_per_label)
        )
        if indices == expected:
            return neighbors_per_label
    raise ValueError(
        "Cannot infer neighbors_per_label from source neighbor indices "
        f"{indices!r}; expected one of (1, 4), (1, 2, 4, 5), or (1, 2, 3, 4, 5, 6)"
    )
