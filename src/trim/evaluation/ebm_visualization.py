from __future__ import annotations

import csv
import math
import tempfile
from pathlib import Path

import numpy as np


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


def export_global_curves(
    *,
    bundle: dict[str, object],
    output_dir: str | Path,
    top_k: int = 12,
    title_prefix: str = "",
) -> dict[str, str]:
    configure_matplotlib_cache()
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import StrMethodFormatter

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    model = bundle["model"]
    feature_columns = list(bundle["feature_columns"])
    top_indices = _select_top_term_indices(model, top_k)

    summary_rows: list[dict[str, object]] = []

    num_plots = len(top_indices)
    num_cols = 3 if num_plots >= 3 else max(1, num_plots)
    num_rows = math.ceil(num_plots / num_cols)
    fig, axes = plt.subplots(num_rows, num_cols, figsize=(6 * num_cols, 3.8 * num_rows), squeeze=False)
    axes_flat = axes.flatten()
    for ax in axes_flat[num_plots:]:
        ax.axis("off")

    importances = _term_importances(model)
    global_explanation = model.explain_global()

    for rank, term_index in enumerate(top_indices, start=1):
        ax = axes_flat[rank - 1]
        feature_index = int(model.term_features_[term_index][0])
        feature_name = feature_columns[feature_index]
        detail = global_explanation.data(term_index)
        names = list(detail["names"])
        scores = list(detail["scores"])
        lower_bounds = list(detail.get("lower_bounds", names[:-1]))
        upper_bounds = list(detail.get("upper_bounds", names[1:]))

        x_values = list(range(len(scores)))
        labels = [format_interval(lower_bounds[i], upper_bounds[i]) for i in range(len(scores))]

        ax.plot(x_values, scores, marker="o", linewidth=1.5, markersize=2.5)
        ax.axhline(0.0, color="#666666", linewidth=0.8, linestyle="--")
        ax.set_title(
            f"{rank}. {feature_name}\nimportance={importances[term_index]:.4f}",
            fontsize=10,
        )
        ax.set_xlabel("Bin")
        ax.set_ylabel("Contribution score")
        ax.yaxis.set_major_formatter(StrMethodFormatter("{x:.3f}"))
        if len(labels) <= 12:
            ax.set_xticks(x_values)
            ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
        ax.grid(alpha=0.2)

        strongest_negative_index = int(np.argmin(scores))
        strongest_positive_index = int(np.argmax(scores))
        summary_rows.append(
            {
                "rank": rank,
                "term_index": term_index,
                "feature_name": feature_name,
                "importance": float(importances[term_index]),
                "strongest_negative_interval": labels[strongest_negative_index],
                "strongest_negative_score": float(scores[strongest_negative_index]),
                "strongest_positive_interval": labels[strongest_positive_index],
                "strongest_positive_score": float(scores[strongest_positive_index]),
            }
        )

    fig.tight_layout()
    png_path = output_dir / "global_top_feature_curves.png"
    fig.savefig(png_path, dpi=180, bbox_inches="tight")
    plt.close(fig)

    csv_path = output_dir / "global_top_feature_summary.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary_rows[0].keys()))
        writer.writeheader()
        writer.writerows(summary_rows)

    return {
        "summary_csv": str(csv_path.resolve()),
        "figure_png": str(png_path.resolve()),
    }


def export_pair_heatmaps(
    *,
    bundle: dict[str, object],
    output_dir: str | Path,
    top_k: int = 9,
) -> dict[str, str]:
    configure_matplotlib_cache()
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FormatStrFormatter

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    model = bundle["model"]
    pair_columns = list(bundle["pair_columns"])
    top_indices = _select_top_term_indices(model, top_k)
    importances = _term_importances(model)
    global_explanation = model.explain_global()

    summary_rows: list[dict[str, object]] = []
    num_plots = len(top_indices)
    num_cols = 3 if num_plots >= 3 else max(1, num_plots)
    num_rows = math.ceil(num_plots / num_cols)
    fig, axes = plt.subplots(num_rows, num_cols, figsize=(6 * num_cols, 4.8 * num_rows), squeeze=False)
    axes_flat = axes.flatten()
    for ax in axes_flat[num_plots:]:
        ax.axis("off")

    for rank, term_index in enumerate(top_indices, start=1):
        ax = axes_flat[rank - 1]
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

        if len(left_names) >= 3:
            x_ticks = np.linspace(0, scores.shape[0] - 1, num=min(5, scores.shape[0]), dtype=int)
            x_labels = []
            for tick in x_ticks:
                upper_index = min(tick + 1, len(left_names) - 1)
                x_labels.append(format_interval(left_names[tick], left_names[upper_index]))
            ax.set_xticks(x_ticks)
            ax.set_xticklabels(x_labels, rotation=45, ha="right", fontsize=7)

        if len(right_names) >= 3:
            y_ticks = np.linspace(0, scores.shape[1] - 1, num=min(5, scores.shape[1]), dtype=int)
            y_labels = []
            for tick in y_ticks:
                upper_index = min(tick + 1, len(right_names) - 1)
                y_labels.append(format_interval(right_names[tick], right_names[upper_index]))
            ax.set_yticks(y_ticks)
            ax.set_yticklabels(y_labels, fontsize=7)

        strongest_positive = np.unravel_index(int(np.nanargmax(scores)), scores.shape)
        strongest_negative = np.unravel_index(int(np.nanargmin(scores)), scores.shape)

        summary_rows.append(
            {
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
        )

        colorbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        colorbar.ax.yaxis.set_major_formatter(FormatStrFormatter("%.3f"))

    fig.tight_layout()
    bundle_stem = str(bundle["model_type"])
    png_path = output_dir / f"{bundle_stem}_top_interaction_heatmaps.png"
    fig.savefig(png_path, dpi=180, bbox_inches="tight")
    plt.close(fig)

    csv_path = output_dir / f"{bundle_stem}_top_interaction_summary.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary_rows[0].keys()))
        writer.writeheader()
        writer.writerows(summary_rows)

    return {
        "summary_csv": str(csv_path.resolve()),
        "figure_png": str(png_path.resolve()),
    }
