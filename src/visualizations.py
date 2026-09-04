"""Reproducible figures for the synthetic MRO portfolio project."""

from __future__ import annotations

from pathlib import Path
from typing import Mapping

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
import pandas as pd


BACKGROUND = "#0d1825"
PANEL = "#18283a"
TEXT = "#e8eef5"
MUTED = "#9aabba"
BLUE = "#5fa2ef"
GREEN = "#36cfa0"
YELLOW = "#f4b82f"
PINK = "#f66d85"
PURPLE = "#9a82ec"
GRID = "#304155"
PALETTE = [BLUE, GREEN, YELLOW, PINK, PURPLE, "#7d8a9d"]


def _style_axis(ax: plt.Axes, title: str) -> None:
    ax.set_facecolor(PANEL)
    ax.set_title(title, color=TEXT, fontsize=13, weight="bold", pad=12)
    ax.tick_params(colors=MUTED, labelsize=10)
    ax.xaxis.label.set_color(MUTED)
    ax.yaxis.label.set_color(MUTED)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.grid(axis="x", color=GRID, linewidth=0.7, alpha=0.55)


def _new_figure(rows: int = 1, columns: int = 2, *, height: float = 7.0):
    fig, axes = plt.subplots(rows, columns, figsize=(16, height), facecolor=BACKGROUND)
    return fig, np.atleast_1d(axes).ravel()


def _save(fig: plt.Figure, output_path: Path, title: str, subtitle: str = "") -> None:
    fig.suptitle(title, color=TEXT, fontsize=19, weight="bold", y=0.985)
    if subtitle:
        fig.text(0.5, 0.925, subtitle, ha="center", color=MUTED, fontsize=10)
    fig.tight_layout(rect=(0.02, 0.02, 0.98, 0.87))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=170, facecolor=BACKGROUND, bbox_inches="tight")
    plt.close(fig)


def save_kpi_dashboard(
    customer_orders: pd.DataFrame,
    supplier_orders: pd.DataFrame,
    output_path: Path,
) -> None:
    """Save an eight-card overview of the generated scenario."""

    metrics = [
        ("Customer orders", f"{len(customer_orders):,}", BLUE),
        ("Supplier orders", f"{len(supplier_orders):,}", BLUE),
        ("Simulated revenue", f"€{customer_orders['order_value'].sum() / 1e6:.1f}M", YELLOW),
        ("Simulated gross profit", f"€{customer_orders['gross_profit'].sum() / 1e6:.1f}M", YELLOW),
        ("Customer on time", f"{customer_orders['on_time'].mean():.1%}", GREEN),
        ("Supplier on time", f"{supplier_orders['on_time'].mean():.1%}", GREEN),
        ("Average basket", f"{customer_orders['basket_size'].mean():.2f}", PURPLE),
        ("Active customers", f"{customer_orders['customer_id'].nunique():,}", PINK),
    ]

    fig, axes = _new_figure(2, 4, height=6.8)
    for ax, (label, value, color) in zip(axes, metrics):
        ax.set_facecolor(PANEL)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_color(color)
            spine.set_linewidth(1.6)
        ax.add_patch(
            Rectangle(
                (0, 0.86),
                1,
                0.14,
                transform=ax.transAxes,
                facecolor=color,
                edgecolor="none",
            )
        )
        ax.text(
            0.5,
            0.56,
            value,
            transform=ax.transAxes,
            ha="center",
            va="center",
            color=color,
            fontsize=22,
            weight="bold",
        )
        ax.text(
            0.5,
            0.27,
            label,
            transform=ax.transAxes,
            ha="center",
            va="center",
            color=TEXT,
            fontsize=10.5,
            weight="bold",
        )

    _save(
        fig,
        output_path,
        "Synthetic B2B MRO Scenario — KPI Overview",
        "Generated data • 2022–2023 • portfolio demonstration",
    )


def save_customer_engagement(customer_orders: pd.DataFrame, output_path: Path) -> None:
    """Save basket, value, and return comparisons by generated segment."""

    by_level = customer_orders.groupby("technician_level").agg(
        avg_basket=("basket_size", "mean"),
        return_rate=("is_returned", "mean"),
    )
    by_work = customer_orders.groupby("work_situation")["order_value"].mean()

    fig, axes = _new_figure(1, 3, height=6.2)
    basket = by_level["avg_basket"].sort_values()
    axes[0].barh(basket.index, basket.values, color=[BLUE, GREEN, YELLOW])
    _style_axis(axes[0], "Average basket by technician level")
    axes[0].set_xlabel("Items per order")
    for index, value in enumerate(basket.values):
        axes[0].text(value + 0.05, index, f"{value:.2f}", va="center", color=TEXT)

    work_value = by_work.sort_values()
    axes[1].barh(work_value.index, work_value.values, color=[PURPLE, BLUE, PINK])
    _style_axis(axes[1], "Average order value by work situation")
    axes[1].set_xlabel("Euro per order")
    for index, value in enumerate(work_value.values):
        axes[1].text(value + 25, index, f"€{value:,.0f}", va="center", color=TEXT)

    returns = (by_level["return_rate"] * 100).sort_values()
    axes[2].barh(returns.index, returns.values, color=PINK)
    axes[2].axvline(returns.mean(), color=YELLOW, linestyle="--", linewidth=1.4)
    _style_axis(axes[2], "Return rate by technician level")
    axes[2].set_xlabel("Percent of orders")
    for index, value in enumerate(returns.values):
        axes[2].text(value + 0.03, index, f"{value:.2f}%", va="center", color=TEXT)

    _save(
        fig,
        output_path,
        "Customer Engagement — Scenario Results",
        "Segment differences partly reflect assumptions encoded in the generator",
    )


def save_delivery_performance(customer_orders: pd.DataFrame, output_path: Path) -> None:
    """Save city on-time rates and the simulated delay distribution."""

    city_rates = (customer_orders.groupby("city")["on_time"].mean() * 100).sort_values()
    late_delays = customer_orders.loc[customer_orders["on_time"].eq(0), "delay_days"]

    fig, axes = _new_figure(1, 2, height=6.4)
    axes[0].barh(city_rates.index, city_rates.values, color=PINK)
    axes[0].axvline(city_rates.mean(), color=YELLOW, linestyle="--", linewidth=1.4)
    _style_axis(axes[0], "Customer-order on-time rate by city")
    axes[0].set_xlabel("Percent on time")
    for index, value in enumerate(city_rates.values):
        axes[0].text(value + 0.15, index, f"{value:.1f}%", va="center", color=TEXT)

    delay_counts = late_delays.value_counts().sort_index()
    axes[1].bar(delay_counts.index, delay_counts.values, color=PINK, width=0.8)
    axes[1].axvline(late_delays.mean(), color=YELLOW, linestyle="--", linewidth=1.5)
    _style_axis(axes[1], "Delay distribution among late orders")
    axes[1].set_xlabel("Days late")
    axes[1].set_ylabel("Orders")
    axes[1].text(
        late_delays.mean() + 0.15,
        delay_counts.max() * 0.84,
        f"Mean: {late_delays.mean():.1f} days",
        color=YELLOW,
    )

    _save(
        fig,
        output_path,
        "Customer-Order Delivery Performance",
        "A common delay process is used across cities; differences are sampling variation",
    )


def save_supplier_performance(
    supplier_orders: pd.DataFrame,
    supplier_master: pd.DataFrame,
    output_path: Path,
) -> None:
    """Save assumed country scores and supplier-level procurement exposure."""

    country_scores = (
        supplier_master.groupby("supplier_country")["reliability_score"].mean() * 100
    ).sort_values()
    supplier_exposure = supplier_orders.groupby("supplier_id").agg(
        procurement_value=("order_value", "sum"),
        service_score=("reliability_score", "first"),
        purchase_orders=("sup_order_id", "count"),
    )
    supplier_exposure["service_score"] *= 100
    supplier_exposure["procurement_value_m"] = supplier_exposure["procurement_value"] / 1e6
    review_rule = supplier_exposure["service_score"].lt(80)

    fig, axes = _new_figure(1, 2, height=6.4)
    axes[0].barh(country_scores.index, country_scores.values, color=GREEN)
    axes[0].axvline(80, color=YELLOW, linestyle="--", linewidth=1.4)
    _style_axis(axes[0], "Assumed service score by country")
    axes[0].set_xlabel("Scenario score (%)")
    for index, value in enumerate(country_scores.values):
        axes[0].text(value + 0.2, index, f"{value:.1f}%", va="center", color=TEXT)

    colors = np.where(review_rule, PINK, GREEN)
    sizes = supplier_exposure["purchase_orders"] * 2.5
    axes[1].scatter(
        supplier_exposure["service_score"],
        supplier_exposure["procurement_value_m"],
        s=sizes,
        c=colors,
        alpha=0.72,
        edgecolors="none",
    )
    axes[1].axvline(80, color=YELLOW, linestyle="--", linewidth=1.2)
    _style_axis(axes[1], "Supplier service score and procurement exposure")
    axes[1].set_xlabel("Assumed service score (%)")
    axes[1].set_ylabel("Procurement value (€M)")

    _save(
        fig,
        output_path,
        "Scenario Supplier Service & Procurement Exposure",
        "Scores are modelling inputs, not country or supplier performance evidence",
    )


def save_product_analysis(supplier_orders: pd.DataFrame, output_path: Path) -> None:
    """Save category procurement value and simulated supplier on-time rates."""

    categories = supplier_orders.groupby("category").agg(
        procurement_value=("order_value", "sum"),
        on_time_rate=("on_time", "mean"),
    )
    categories["procurement_value_m"] = categories["procurement_value"] / 1e6
    categories["on_time_rate"] *= 100

    fig, axes = _new_figure(1, 2, height=6.6)
    value = categories["procurement_value_m"].sort_values()
    axes[0].barh(value.index, value.values, color=PURPLE)
    _style_axis(axes[0], "Simulated procurement value by category")
    axes[0].set_xlabel("Procurement value (€M)")
    for index, amount in enumerate(value.values):
        axes[0].text(amount + 0.25, index, f"€{amount:.1f}M", va="center", color=TEXT)

    on_time = categories["on_time_rate"].sort_values()
    axes[1].barh(on_time.index, on_time.values, color=GREEN)
    axes[1].axvline(on_time.mean(), color=YELLOW, linestyle="--", linewidth=1.4)
    _style_axis(axes[1], "Supplier-order on-time rate by category")
    axes[1].set_xlabel("Percent on time")
    for index, rate in enumerate(on_time.values):
        axes[1].text(rate + 0.08, index, f"{rate:.1f}%", va="center", color=TEXT)

    _save(
        fig,
        output_path,
        "Product & Procurement — Scenario Results",
        "Category results reflect generated product mix and supplier orders",
    )


def save_rfm_analysis(rfm_scores: pd.DataFrame, output_path: Path) -> None:
    """Save customer counts and generated value by descriptive RFM segment."""

    segment_summary = rfm_scores.groupby("segment").agg(
        customers=("customer_id", "count"),
        total_value=("monetary", "sum"),
    )
    segment_summary["total_value_m"] = segment_summary["total_value"] / 1e6
    segment_order = [
        segment
        for segment in ["Lost", "At Risk", "New Customer", "Potential", "Loyal", "Champion"]
        if segment in segment_summary.index
    ]
    segment_summary = segment_summary.reindex(segment_order)

    fig, axes = _new_figure(1, 2, height=6.2)
    axes[0].barh(segment_summary.index, segment_summary["customers"], color=PALETTE[: len(segment_summary)])
    _style_axis(axes[0], "Customers by descriptive RFM segment")
    axes[0].set_xlabel("Customers")
    for index, value in enumerate(segment_summary["customers"]):
        axes[0].text(value + 1, index, f"{value}", va="center", color=TEXT)

    axes[1].barh(segment_summary.index, segment_summary["total_value_m"], color=PALETTE[: len(segment_summary)])
    _style_axis(axes[1], "Simulated value by RFM segment")
    axes[1].set_xlabel("Value (€M)")
    for index, value in enumerate(segment_summary["total_value_m"]):
        axes[1].text(value + 0.08, index, f"€{value:.2f}M", va="center", color=TEXT)

    _save(
        fig,
        output_path,
        "RFM Customer Segmentation",
        "Rule-based prioritisation; not a churn prediction",
    )


def save_clustering(
    rfm_scores: pd.DataFrame,
    silhouette_scores: Mapping[int, float],
    output_path: Path,
) -> None:
    """Save cluster profiles and silhouette comparison for candidate k values."""

    fig, axes = _new_figure(1, 2, height=6.4)
    cluster_values = sorted(rfm_scores["cluster"].unique())
    for cluster, color in zip(cluster_values, PALETTE):
        group = rfm_scores.loc[rfm_scores["cluster"].eq(cluster)]
        axes[0].scatter(
            group["frequency"],
            group["monetary"] / 1_000,
            s=28,
            alpha=0.68,
            color=color,
            label=f"Cluster {cluster}",
            edgecolors="none",
        )
    _style_axis(axes[0], "Frequency and monetary value by cluster")
    axes[0].set_xlabel("Order frequency")
    axes[0].set_ylabel("Simulated customer value (€k)")
    legend = axes[0].legend(frameon=False)
    plt.setp(legend.get_texts(), color=TEXT)

    counts = list(silhouette_scores)
    scores = [silhouette_scores[count] for count in counts]
    best_k = max(silhouette_scores, key=silhouette_scores.get)
    colors = [YELLOW if count == best_k else BLUE for count in counts]
    axes[1].bar(counts, scores, color=colors, width=0.5)
    _style_axis(axes[1], "Silhouette comparison")
    axes[1].set_xlabel("Number of clusters (k)")
    axes[1].set_ylabel("Silhouette score")
    axes[1].set_xticks(counts)
    axes[1].set_ylim(0, max(scores) * 1.25)
    for count, score in zip(counts, scores):
        axes[1].text(count, score + 0.006, f"{score:.3f}", ha="center", color=TEXT)

    _save(
        fig,
        output_path,
        "Exploratory K-Means Customer Segmentation",
        f"Best candidate tested: k={best_k}; modest separation requires cautious interpretation",
    )
