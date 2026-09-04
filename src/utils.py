"""Reusable helpers for the synthetic MRO supply-chain analysis."""

from __future__ import annotations

import pandas as pd


def label_rfm_segment(total_score: int) -> str:
    """Map an RFM score from 3 to 15 to a descriptive portfolio segment."""

    if total_score >= 13:
        return "Champion"
    if total_score >= 11:
        return "Loyal"
    if total_score >= 9:
        return "Potential"
    if total_score >= 7:
        return "New Customer"
    if total_score >= 5:
        return "At Risk"
    return "Lost"


def compute_rfm(
    orders: pd.DataFrame,
    snapshot_date: pd.Timestamp | None = None,
) -> pd.DataFrame:
    """Calculate customer-level recency, frequency, monetary value, and segments."""

    required = {"customer_id", "order_date", "order_id", "order_value"}
    missing = required.difference(orders.columns)
    if missing:
        raise ValueError(f"Missing RFM columns: {sorted(missing)}")

    analysis_orders = orders.copy()
    analysis_orders["order_date"] = pd.to_datetime(
        analysis_orders["order_date"], errors="raise"
    )
    if snapshot_date is None:
        snapshot_date = analysis_orders["order_date"].max() + pd.Timedelta(days=1)
    snapshot_date = pd.Timestamp(snapshot_date)

    rfm = (
        analysis_orders.groupby("customer_id")
        .agg(
            recency=("order_date", lambda dates: (snapshot_date - dates.max()).days),
            frequency=("order_id", "count"),
            monetary=("order_value", "sum"),
        )
        .reset_index()
    )

    rfm["R_score"] = pd.qcut(rfm["recency"], 5, labels=[5, 4, 3, 2, 1]).astype(int)
    rfm["F_score"] = pd.qcut(
        rfm["frequency"].rank(method="first"),
        5,
        labels=[1, 2, 3, 4, 5],
    ).astype(int)
    rfm["M_score"] = pd.qcut(rfm["monetary"], 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["RFM_total"] = rfm[["R_score", "F_score", "M_score"]].sum(axis=1)
    rfm["segment"] = rfm["RFM_total"].map(label_rfm_segment)
    return rfm


def summarise_delivery(orders: pd.DataFrame, group_column: str) -> pd.DataFrame:
    """Return order count, on-time rate, and delay by a selected dimension."""

    required = {group_column, "on_time", "delay_days", "order_id"}
    missing = required.difference(orders.columns)
    if missing:
        raise ValueError(f"Missing delivery columns: {sorted(missing)}")

    summary = (
        orders.groupby(group_column)
        .agg(
            order_count=("order_id", "count"),
            on_time_rate=("on_time", "mean"),
            avg_delay_days=("delay_days", "mean"),
        )
        .reset_index()
    )
    summary["on_time_rate"] = (summary["on_time_rate"] * 100).round(1)
    summary["avg_delay_days"] = summary["avg_delay_days"].round(2)
    return summary
