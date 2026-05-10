"""
Utility functions for MRO Supply Chain Analysis.
Reusable helpers separated from the notebook for clarity.
"""
import pandas as pd
import numpy as np


def compute_rfm(orders_df: pd.DataFrame, snapshot_date=None) -> pd.DataFrame:
    """
    Compute RFM scores for each customer.

    Parameters
    ----------
    orders_df : DataFrame with columns [customer_id, order_date, order_id, order_value]
    snapshot_date : reference date; defaults to max order_date + 1 day

    Returns
    -------
    DataFrame with columns [customer_id, recency, frequency, monetary,
                             R_score, F_score, M_score, RFM_total, segment]
    """
    if snapshot_date is None:
        snapshot_date = orders_df['order_date'].max() + pd.Timedelta(days=1)

    rfm = (
        orders_df
        .groupby('customer_id')
        .agg(
            recency   = ('order_date',  lambda x: (snapshot_date - x.max()).days),
            frequency = ('order_id',    'count'),
            monetary  = ('order_value', 'sum'),
        )
        .reset_index()
    )

    rfm['R_score'] = pd.qcut(rfm['recency'],   5, labels=[5,4,3,2,1]).astype(int)
    rfm['F_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1,2,3,4,5]).astype(int)
    rfm['M_score'] = pd.qcut(rfm['monetary'],  5, labels=[1,2,3,4,5]).astype(int)
    rfm['RFM_total'] = rfm[['R_score','F_score','M_score']].sum(axis=1)
    rfm['segment'] = rfm['RFM_total'].map(label_rfm_segment)
    return rfm


def label_rfm_segment(total: int) -> str:
    """Map RFM total score (3–15) to a business segment label."""
    if total >= 13: return 'Champion'
    if total >= 11: return 'Loyal'
    if total >= 9:  return 'Potential'
    if total >= 7:  return 'New Customer'
    if total >= 5:  return 'At Risk'
    return 'Lost'


def summarise_delivery(orders_df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    """
    Compute delivery KPIs grouped by a given column.

    Returns DataFrame with [group_col, ontime_pct, avg_delay_days, order_count]
    """
    return (
        orders_df
        .groupby(group_col)
        .agg(
            ontime_pct      = ('on_time',    lambda x: x.mean() * 100),
            avg_delay_days  = ('delay_days', 'mean'),
            order_count     = ('order_id',   'count'),
        )
        .round(2)
        .reset_index()
    )
