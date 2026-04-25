from __future__ import annotations

import csv
import math
import tempfile
from pathlib import Path

import numpy as np

from trim.utils.paths import resolve_project_path, serialize_project_path


def configure_matplotlib_cache() -> None:
    matplotlib_cache_dir = Path(tempfile.gettempdir()) / "trim_matplotlib"
    matplotlib_cache_dir.mkdir(parents=True, exist_ok=True)
    import os

    os.environ.setdefault("MPLCONFIGDIR", str(matplotlib_cache_dir))


def format_compact_number(value: object, *, decimals: int = 3) -> str:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return str(value)

    if math.isnan(numeric):
        return "nan"
    if math.isinf(numeric):
        return "inf" if numeric > 0 else "-inf"

    formatted = f"{numeric:.{decimals}f}".rstrip("0").rstrip(".")
    if formatted == "-0":
        return "0"
    return formatted


def format_interval(lower: object, upper: object) -> str:
    return f"[{format_compact_number(lower)}, {format_compact_number(upper)})"


def _safe_float(value: object) -> float:
    return float(value)


def _term_importances(model) -> np.ndarray:
    importances = model.term_importances()
    return np.asarray(importances, dtype=float)


def _select_top_term_indices(model, top_k: int) -> list[int]:
    importances = _term_importances(model)
    ranked = np.argsort(importances)[::-1]
    return [int(index) for index in ranked[:top_k]]


def _chunk_items(items: list[int], chunk_size: int) -> list[list[int]]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    return [items[index : index + chunk_size] for index in range(0, len(items), chunk_size)]


def _normalize_prefixes(prefixes: list[str] | None) -> tuple[str, ...]:
    if not prefixes:
        return ()
    return tuple(str(prefix) for prefix in prefixes if str(prefix))


def _matches_prefix(value: str, prefixes: tuple[str, ...]) -> bool:
    return not prefixes or value.startswith(prefixes)


def _select_axis_tick_positions(length: int, *, max_ticks: int) -> list[int]:
    if length <= 0:
        return []
    if length <= max_ticks:
        return list(range(length))
    ticks = np.linspace(0, length - 1, num=max_ticks, dtype=int)
    return sorted({int(tick) for tick in ticks})


def _set_interval_tick_labels(
    ax,
    *,
    labels: list[str],
    axis: str,
    max_ticks: int,
    rotation: int = 0,
    fontsize: int = 8,
) -> None:
    ticks = _select_axis_tick_positions(len(labels), max_ticks=max_ticks)
    tick_labels = [labels[tick] for tick in ticks]
    if axis == "x":
        ax.set_xticks(ticks)
        ax.set_xticklabels(tick_labels, rotation=rotation, ha="right" if rotation else "center", fontsize=fontsize)
    elif axis == "y":
        ax.set_yticks(ticks)
        ax.set_yticklabels(tick_labels, fontsize=fontsize)
    else:
        raise ValueError(f"Unsupported axis: {axis}")


def _global_bin_edges_and_labels(detail: dict[str, object]) -> tuple[list[float] | None, list[str], list[str]]:
    names = detail.get("names", [])
    scores = detail.get("scores", [])
    numeric_names = None
    try:
        numeric_names = [float(value) for value in names]
    except (TypeError, ValueError):
        numeric_names = None

    if numeric_names is not None and len(numeric_names) == len(scores) + 1:
        interval_labels = [
            format_interval(numeric_names[index], numeric_names[index + 1])
            for index in range(len(scores))
        ]
        midpoint_labels = [
            format_compact_number((numeric_names[index] + numeric_names[index + 1]) / 2.0)
            for index in range(len(scores))
        ]
        return numeric_names, interval_labels, midpoint_labels

    if numeric_names is not None and len(numeric_names) == len(scores):
        midpoint_labels = [format_compact_number(value) for value in numeric_names]
        return None, midpoint_labels, midpoint_labels

    string_names = [str(value) for value in names]
    return None, string_names, string_names


def _resolve_global_term_indices(
    *,
    model,
    feature_columns: list[str],
    top_k: int,
    selected_feature_names: list[str] | None = None,
    selected_feature_prefixes: list[str] | None = None,
) -> list[int]:
    if not selected_feature_names and not selected_feature_prefixes:
        return _select_top_term_indices(model, top_k)

    prefixes = _normalize_prefixes(selected_feature_prefixes)
    selected_name_set = {str(name) for name in selected_feature_names or []}

    selected_indices: list[int] = []
    seen_terms: set[int] = set()
    for term_index, term_features in enumerate(model.term_features_):
        if len(term_features) != 1:
            continue
        feature_index = int(term_features[0])
        feature_name = feature_columns[feature_index]
        if feature_name in selected_name_set or _matches_prefix(feature_name, prefixes):
            if term_index not in seen_terms:
                selected_indices.append(int(term_index))
                seen_terms.add(int(term_index))
    return selected_indices


def _resolve_pair_term_indices(
    *,
    model,
    pair_columns: list[str],
    top_k: int,
    selected_feature_names: list[str] | None = None,
    selected_feature_prefixes: list[str] | None = None,
) -> list[int]:
    if not selected_feature_names and not selected_feature_prefixes:
        return _select_top_term_indices(model, top_k)

    prefixes = _normalize_prefixes(selected_feature_prefixes)
    selected_name_set = {str(name) for name in selected_feature_names or []}

    selected_indices: list[int] = []
    seen_terms: set[int] = set()
    for term_index, term_features in enumerate(model.term_features_):
        if len(term_features) != 2:
            continue
        left_feature_index = int(term_features[0])
        base_name = pair_columns[left_feature_index]
        raw_feature_name = base_name.removesuffix("__base")
        if raw_feature_name in selected_name_set or _matches_prefix(raw_feature_name, prefixes):
            if term_index not in seen_terms:
                selected_indices.append(int(term_index))
                seen_terms.add(int(term_index))
    return selected_indices


def _write_summary_csv(csv_path: Path, rows: list[dict[str, object]]) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _render_global_term(
    *,
    ax,
    model,
    feature_columns: list[str],
    global_explanation,
    importances: np.ndarray,
    term_index: int,
    rank: int,
) -> dict[str, object]:
    from matplotlib.ticker import StrMethodFormatter

    feature_index = int(model.term_features_[term_index][0])
    feature_name = feature_columns[feature_index]
    detail = global_explanation.data(term_index)
    scores = list(detail["scores"])
    _, interval_labels, midpoint_labels = _global_bin_edges_and_labels(detail)

    x_values = list(range(len(scores)))

    ax.plot(x_values, scores, marker="o", linewidth=1.5, markersize=2.5)
    ax.axhline(0.0, color="#666666", linewidth=0.8, linestyle="--")
    ax.set_title(
        f"{rank}. {feature_name}\nimportance={importances[term_index]:.4f}",
        fontsize=10,
    )
    ax.set_xlabel("Bin midpoint value")
    ax.set_ylabel("Contribution score")
    ax.yaxis.set_major_formatter(StrMethodFormatter("{x:.3f}"))
    _set_interval_tick_labels(ax, labels=midpoint_labels, axis="x", max_ticks=8, rotation=45, fontsize=8)
    ax.grid(alpha=0.2)

    strongest_negative_index = int(np.argmin(scores))
    strongest_positive_index = int(np.argmax(scores))
    return {
        "rank": rank,
        "term_index": term_index,
        "feature_name": feature_name,
        "importance": float(importances[term_index]),
        "strongest_negative_interval": interval_labels[strongest_negative_index],
        "strongest_negative_score": float(scores[strongest_negative_index]),
        "strongest_positive_interval": interval_labels[strongest_positive_index],
        "strongest_positive_score": float(scores[strongest_positive_index]),
    }


def _render_pair_term(
    *,
    ax,
    model,
    pair_columns: list[str],
    global_explanation,
    importances: np.ndarray,
    term_index: int,
    rank: int,
) -> dict[str, object]:
    from matplotlib.ticker import FormatStrFormatter

    left_feature_index, right_feature_index = [int(value) for value in model.term_features_[term_index]]
    base_name = pair_columns[left_feature_index]
    delta_name = pair_columns[right_feature_index]
    raw_feature_name = base_name.removesuffix("__base")

    detail = global_explanation.data(term_index)
    left_names = list(detail["left_names"])
    right_names = list(detail["right_names"])
    scores = np.asarray(detail["scores"], dtype=float)

    im = ax.imshow(scores.T, aspect="auto", origin="lower", cmap="coolwarm")
    ax.set_title(f"{rank}. {raw_feature_name}\nimportance={importances[term_index]:.4f}", fontsize=10)
    ax.set_xlabel(base_name)
    ax.set_ylabel(delta_name)

    if len(left_names) >= 2:
        x_labels = [
            format_interval(left_names[tick], left_names[min(tick + 1, len(left_names) - 1)])
            for tick in range(len(left_names) - 1)
        ]
        _set_interval_tick_labels(ax, labels=x_labels, axis="x", max_ticks=5, rotation=45, fontsize=7)

    if len(right_names) >= 2:
        y_labels = [
            format_interval(right_names[tick], right_names[min(tick + 1, len(right_names) - 1)])
            for tick in range(len(right_names) - 1)
        ]
        _set_interval_tick_labels(ax, labels=y_labels, axis="y", max_ticks=5, fontsize=7)

    strongest_positive = np.unravel_index(int(np.nanargmax(scores)), scores.shape)
    strongest_negative = np.unravel_index(int(np.nanargmin(scores)), scores.shape)

    summary_row = {
        "rank": rank,
        "term_index": term_index,
        "raw_feature_name": raw_feature_name,
        "base_feature_name": base_name,
        "delta_feature_name": delta_name,
        "importance": float(importances[term_index]),
        "strongest_positive_base_interval": format_interval(
            left_names[strongest_positive[0]],
            left_names[min(strongest_positive[0] + 1, len(left_names) - 1)],
        ),
        "strongest_positive_delta_interval": format_interval(
            right_names[strongest_positive[1]],
            right_names[min(strongest_positive[1] + 1, len(right_names) - 1)],
        ),
        "strongest_positive_score": float(scores[strongest_positive]),
        "strongest_negative_base_interval": format_interval(
            left_names[strongest_negative[0]],
            left_names[min(strongest_negative[0] + 1, len(left_names) - 1)],
        ),
        "strongest_negative_delta_interval": format_interval(
            right_names[strongest_negative[1]],
            right_names[min(strongest_negative[1] + 1, len(right_names) - 1)],
        ),
        "strongest_negative_score": float(scores[strongest_negative]),
    }

    colorbar = ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    colorbar.ax.yaxis.set_major_formatter(FormatStrFormatter("%.3f"))
    return summary_row


def export_global_curves(
    *,
    bundle: dict[str, object],
    output_dir: str | Path,
    top_k: int = 12,
    title_prefix: str = "",
    selected_feature_names: list[str] | None = None,
    selected_feature_prefixes: list[str] | None = None,
    plots_per_figure: int = 12,
) -> dict[str, object]:
    configure_matplotlib_cache()
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    model = bundle["model"]
    feature_columns = list(bundle["feature_columns"])
    selected_indices = _resolve_global_term_indices(
        model=model,
        feature_columns=feature_columns,
        top_k=top_k,
        selected_feature_names=selected_feature_names,
        selected_feature_prefixes=selected_feature_prefixes,
    )
    if not selected_indices:
        raise ValueError("No global EBM terms matched the requested feature filters")

    summary_rows: list[dict[str, object]] = []

    importances = _term_importances(model)
    global_explanation = model.explain_global()

    figure_paths: list[str] = []
    pages = _chunk_items(selected_indices, plots_per_figure)
    for page_index, term_indices in enumerate(pages, start=1):
        num_plots = len(term_indices)
        num_cols = 3 if num_plots >= 3 else max(1, num_plots)
        num_rows = math.ceil(num_plots / num_cols)
        fig, axes = plt.subplots(num_rows, num_cols, figsize=(6 * num_cols, 3.8 * num_rows), squeeze=False)
        axes_flat = axes.flatten()
        for ax in axes_flat[num_plots:]:
            ax.axis("off")

        for page_rank, term_index in enumerate(term_indices, start=1):
            rank = (page_index - 1) * plots_per_figure + page_rank
            ax = axes_flat[page_rank - 1]
            summary_rows.append(
                _render_global_term(
                    ax=ax,
                    model=model,
                    feature_columns=feature_columns,
                    global_explanation=global_explanation,
                    importances=importances,
                    term_index=term_index,
                    rank=rank,
                )
            )

        fig.tight_layout()
        if page_index == 1 and len(pages) == 1:
            png_path = output_dir / "global_feature_curves.png"
        else:
            png_path = output_dir / f"global_feature_curves_page_{page_index:02d}.png"
        fig.savefig(png_path, dpi=180, bbox_inches="tight")
        plt.close(fig)
        figure_paths.append(serialize_project_path(png_path))

    csv_path = output_dir / "global_feature_summary.csv"
    _write_summary_csv(csv_path, summary_rows)

    return {"summary_csv": serialize_project_path(csv_path), "figure_pngs": figure_paths}


def export_pair_heatmaps(
    *,
    bundle: dict[str, object],
    output_dir: str | Path,
    top_k: int = 9,
    selected_feature_names: list[str] | None = None,
    selected_feature_prefixes: list[str] | None = None,
    plots_per_figure: int = 9,
) -> dict[str, object]:
    configure_matplotlib_cache()
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    model = bundle["model"]
    pair_columns = list(bundle["pair_columns"])
    selected_indices = _resolve_pair_term_indices(
        model=model,
        pair_columns=pair_columns,
        top_k=top_k,
        selected_feature_names=selected_feature_names,
        selected_feature_prefixes=selected_feature_prefixes,
    )
    if not selected_indices:
        raise ValueError("No pairwise EBM terms matched the requested feature filters")
    importances = _term_importances(model)
    global_explanation = model.explain_global()

    summary_rows: list[dict[str, object]] = []
    figure_paths: list[str] = []
    bundle_stem = str(bundle["model_type"])
    pages = _chunk_items(selected_indices, plots_per_figure)
    for page_index, term_indices in enumerate(pages, start=1):
        num_plots = len(term_indices)
        num_cols = 3 if num_plots >= 3 else max(1, num_plots)
        num_rows = math.ceil(num_plots / num_cols)
        fig, axes = plt.subplots(num_rows, num_cols, figsize=(6 * num_cols, 4.8 * num_rows), squeeze=False)
        axes_flat = axes.flatten()
        for ax in axes_flat[num_plots:]:
            ax.axis("off")

        for page_rank, term_index in enumerate(term_indices, start=1):
            rank = (page_index - 1) * plots_per_figure + page_rank
            ax = axes_flat[page_rank - 1]
            summary_rows.append(
                _render_pair_term(
                    ax=ax,
                    model=model,
                    pair_columns=pair_columns,
                    global_explanation=global_explanation,
                    importances=importances,
                    term_index=term_index,
                    rank=rank,
                )
            )

        fig.tight_layout()
        if len(pages) == 1:
            png_path = output_dir / f"{bundle_stem}_interaction_heatmaps.png"
        else:
            png_path = output_dir / f"{bundle_stem}_interaction_heatmaps_page_{page_index:02d}.png"
        fig.savefig(png_path, dpi=180, bbox_inches="tight")
        plt.close(fig)
        figure_paths.append(serialize_project_path(png_path))

    csv_path = output_dir / f"{bundle_stem}_interaction_summary.csv"
    _write_summary_csv(csv_path, summary_rows)

    return {"summary_csv": serialize_project_path(csv_path), "figure_pngs": figure_paths}


def export_combined_ebm_pdf(
    *,
    output_pdf_path: str | Path,
    global_bundle: dict[str, object] | None = None,
    pair_bundles: list[dict[str, object]] | None = None,
    global_top_k: int = 12,
    pair_top_k: int = 9,
    selected_feature_names: list[str] | None = None,
    selected_feature_prefixes: list[str] | None = None,
    num_cols: int = 3,
) -> dict[str, object]:
    configure_matplotlib_cache()
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    output_pdf_path = Path(output_pdf_path)
    output_pdf_path.parent.mkdir(parents=True, exist_ok=True)

    sections: list[dict[str, object]] = []
    if global_bundle is not None:
        model = global_bundle["model"]
        feature_columns = list(global_bundle["feature_columns"])
        term_indices = _resolve_global_term_indices(
            model=model,
            feature_columns=feature_columns,
            top_k=global_top_k,
            selected_feature_names=selected_feature_names,
            selected_feature_prefixes=selected_feature_prefixes,
        )
        sections.append(
            {
                "kind": "global",
                "title": "Global EBM",
                "bundle": global_bundle,
                "term_indices": term_indices,
                "summary_csv": output_pdf_path.parent / "global" / "global_feature_summary.csv",
                "rows_per_plot": 3.8,
            }
        )

    for pair_bundle in pair_bundles or []:
        model = pair_bundle["model"]
        pair_columns = list(pair_bundle["pair_columns"])
        term_indices = _resolve_pair_term_indices(
            model=model,
            pair_columns=pair_columns,
            top_k=pair_top_k,
            selected_feature_names=selected_feature_names,
            selected_feature_prefixes=selected_feature_prefixes,
        )
        model_type = str(pair_bundle["model_type"])
        title = "Local Pair EBM: Positive Neighbors" if model_type == "pair_ebm_pos" else "Local Pair EBM: Negative Neighbors"
        sections.append(
            {
                "kind": "pair",
                "title": title,
                "bundle": pair_bundle,
                "term_indices": term_indices,
                "summary_csv": output_pdf_path.parent / model_type / f"{model_type}_interaction_summary.csv",
                "rows_per_plot": 4.8,
            }
        )

    if not sections:
        raise ValueError("At least one global or pairwise bundle is required")

    section_height_ratios: list[float] = []
    for section in sections:
        num_rows = max(1, math.ceil(len(section["term_indices"]) / num_cols))
        if len(section["term_indices"]) == 0:
            raise ValueError(f"No EBM terms matched for section: {section['title']}")
        section["num_rows"] = num_rows
        section_height_ratios.append(0.8 + float(section["rows_per_plot"]) * num_rows)

    fig_width = 6.2 * num_cols
    fig_height = sum(section_height_ratios)
    fig = plt.figure(figsize=(fig_width, fig_height))
    outer_grid = fig.add_gridspec(len(sections), 1, height_ratios=section_height_ratios, hspace=0.18)

    payload_sections: list[dict[str, object]] = []
    for section_index, section in enumerate(sections):
        num_rows = int(section["num_rows"])
        row_height = float(section["rows_per_plot"])
        bundle = section["bundle"]
        model = bundle["model"]
        global_explanation = model.explain_global()
        importances = _term_importances(model)
        subgrid = outer_grid[section_index].subgridspec(
            num_rows + 1,
            num_cols,
            height_ratios=[0.35] + [row_height] * num_rows,
            hspace=0.55,
            wspace=0.35,
        )
        title_ax = fig.add_subplot(subgrid[0, :])
        title_ax.axis("off")
        title_ax.text(0.5, 0.5, str(section["title"]), ha="center", va="center", fontsize=18, fontweight="bold")

        summary_rows: list[dict[str, object]] = []
        for plot_index, term_index in enumerate(section["term_indices"]):
            row_index = plot_index // num_cols + 1
            col_index = plot_index % num_cols
            ax = fig.add_subplot(subgrid[row_index, col_index])
            rank = plot_index + 1
            if section["kind"] == "global":
                summary_rows.append(
                    _render_global_term(
                        ax=ax,
                        model=model,
                        feature_columns=list(bundle["feature_columns"]),
                        global_explanation=global_explanation,
                        importances=importances,
                        term_index=int(term_index),
                        rank=rank,
                    )
                )
            else:
                summary_rows.append(
                    _render_pair_term(
                        ax=ax,
                        model=model,
                        pair_columns=list(bundle["pair_columns"]),
                        global_explanation=global_explanation,
                        importances=importances,
                        term_index=int(term_index),
                        rank=rank,
                    )
                )

        remaining = num_rows * num_cols - len(section["term_indices"])
        for blank_index in range(remaining):
            row_index = (len(section["term_indices"]) + blank_index) // num_cols + 1
            col_index = (len(section["term_indices"]) + blank_index) % num_cols
            blank_ax = fig.add_subplot(subgrid[row_index, col_index])
            blank_ax.axis("off")

        section_summary_csv = resolve_project_path(section["summary_csv"])
        _write_summary_csv(section_summary_csv, summary_rows)
        payload_sections.append(
            {
                "title": section["title"],
                "summary_csv": serialize_project_path(section_summary_csv),
                "num_terms": len(section["term_indices"]),
            }
        )

    fig.savefig(output_pdf_path, format="pdf", bbox_inches="tight")
    plt.close(fig)

    return {
        "pdf_path": serialize_project_path(output_pdf_path),
        "sections": payload_sections,
    }
