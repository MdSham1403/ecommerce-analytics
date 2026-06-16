"""
kpi.py — Compute KPI metrics with period-over-period delta
"""

import pandas as pd


def _fmt_inr(value: float) -> str:
    """Format a number in Indian Rupee notation (Lakhs / Crores)."""
    if value >= 1_00_00_000:
        return f"₹{value/1_00_00_000:.1f} Cr"
    elif value >= 1_00_000:
        return f"₹{value/1_00_000:.1f} L"
    elif value >= 1_000:
        return f"₹{value/1_000:.1f} K"
    return f"₹{value:.0f}"


def _delta_str(current: float, previous: float) -> tuple[str, bool]:
    if previous == 0:
        return "", True
    pct = (current - previous) / abs(previous) * 100
    arrow = "▲" if pct >= 0 else "▼"
    positive = pct >= 0
    return f"{arrow} {abs(pct):.1f}% vs prev period", positive


def compute_kpis(df: pd.DataFrame, df_full: pd.DataFrame) -> dict:
    """
    Compute KPIs for filtered df.
    Compares against the most recent prior period of same length.
    """
    rev  = df["revenue"].sum()
    prof = df["profit"].sum()
    ords = len(df)
    aov  = rev / ords if ords else 0
    delivered    = (df["order_status"] == "Delivered").sum()
    delivery_pct = delivered / ords * 100 if ords else 0

    # ── Prior period (same date range, one period back) ────────────────────────
    min_date = df["order_date"].min()
    max_date = df["order_date"].max()
    span     = (max_date - min_date)

    prev_end   = min_date - pd.Timedelta(days=1)
    prev_start = prev_end - span
    df_prev    = df_full[
        (df_full["order_date"] >= prev_start) &
        (df_full["order_date"] <= prev_end)
    ]

    prev_rev  = df_prev["revenue"].sum() if not df_prev.empty else 0
    prev_prof = df_prev["profit"].sum()  if not df_prev.empty else 0
    prev_ords = len(df_prev)             if not df_prev.empty else 0
    prev_aov  = (prev_rev / prev_ords)  if prev_ords else 0

    rev_d,  rev_pos  = _delta_str(rev,  prev_rev)
    prof_d, prof_pos = _delta_str(prof, prev_prof)
    ords_d, ords_pos = _delta_str(ords, prev_ords)
    aov_d,  aov_pos  = _delta_str(aov,  prev_aov)

    return {
        "revenue":       _fmt_inr(rev),
        "revenue_delta": rev_d,
        "revenue_pos":   rev_pos,
        "profit":        _fmt_inr(prof),
        "profit_delta":  prof_d,
        "profit_pos":    prof_pos,
        "orders":        f"{ords:,}",
        "orders_delta":  ords_d,
        "orders_pos":    ords_pos,
        "aov":           _fmt_inr(aov),
        "aov_delta":     aov_d,
        "aov_pos":       aov_pos,
        "delivery_rate": f"{delivery_pct:.1f}%",
    }
