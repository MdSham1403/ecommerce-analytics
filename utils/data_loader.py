"""
data_loader.py — Load CSV, enrich columns, expose SQL interface via SQLite
"""

import pandas as pd
import sqlite3
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "ecommerce_orders.csv")
DB_PATH   = os.path.join(os.path.dirname(__file__), "..", "data", "ecommerce.db")


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, parse_dates=["order_date", "delivery_date"])

    # ── Derived columns ────────────────────────────────────────────────────────
    df["year"]        = df["order_date"].dt.year
    df["month"]       = df["order_date"].dt.month
    df["month_name"]  = df["order_date"].dt.strftime("%b")
    df["year_month"]  = df["order_date"].dt.to_period("M").astype(str)
    df["month_label"] = df["order_date"].dt.strftime("%b %Y")
    df["quarter"]     = df["order_date"].dt.to_period("Q").astype(str)
    df["week"]        = df["order_date"].dt.isocalendar().week.astype(int)
    df["profit_margin"] = (df["profit"] / df["revenue"].replace(0, 1) * 100).round(2)

    # ── Write to SQLite so the SQL explorer works ──────────────────────────────
    _write_db(df)

    return df


def _write_db(df: pd.DataFrame):
    """Persist DataFrame to SQLite for the SQL query explorer."""
    conn = sqlite3.connect(DB_PATH)
    df_sql = df.copy()
    df_sql["order_date"]   = df_sql["order_date"].astype(str)
    df_sql["delivery_date"] = df_sql["delivery_date"].astype(str)
    df_sql.to_sql("orders", conn, if_exists="replace", index=False)
    conn.close()


def run_sql(query: str) -> pd.DataFrame:
    """Execute arbitrary SQL against the SQLite DB and return a DataFrame."""
    conn = sqlite3.connect(DB_PATH)
    try:
        result = pd.read_sql_query(query, conn)
    finally:
        conn.close()
    return result
