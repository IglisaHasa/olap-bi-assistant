"""
Data utility functions for the OLAP Streamlit App
"""

import pandas as pd
import streamlit as st
import os


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load and cache the Global Retail Sales dataset."""
    data_path = os.path.join(os.path.dirname(__file__), "data", "global_retail_sales.csv")
    df = pd.read_csv(data_path, parse_dates=["order_date"])
    return df


def get_dataset_summary(df: pd.DataFrame) -> dict:
    """Return a summary of the dataset for the sidebar."""
    return {
        "total_records": f"{len(df):,}",
        "total_revenue": f"${df['revenue'].sum():,.0f}",
        "total_profit": f"${df['profit'].sum():,.0f}",
        "avg_profit_margin": f"{df['profit_margin'].mean():.1f}%",
        "date_range": f"{df['order_date'].min().strftime('%b %Y')} – {df['order_date'].max().strftime('%b %Y')}",
        "regions": sorted(df["region"].unique().tolist()),
        "categories": sorted(df["category"].unique().tolist()),
        "years": sorted(df["year"].unique().tolist()),
    }


def execute_pandas_code(code: str, df: pd.DataFrame):
    """
    Safely execute the LLM-generated pandas code.
    Returns (df_result, error_message).
    """
    local_vars = {"df": df.copy(), "pd": pd}
    try:
        exec(code, {"pd": pd}, local_vars)
        df_result = local_vars.get("df_result", None)
        if df_result is None:
            return None, "No df_result was created by the code."
        if not isinstance(df_result, pd.DataFrame):
            return None, f"df_result is not a DataFrame (got {type(df_result).__name__})."
        return df_result, None
    except Exception as e:
        return None, str(e)


def format_currency_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Format currency-like columns for display."""
    currency_cols = [c for c in df.columns if c in ("revenue", "cost", "profit", "unit_price")]
    df_display = df.copy()
    for col in currency_cols:
        df_display[col] = df_display[col].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "")
    pct_cols = [c for c in df.columns if "margin" in c.lower() or "pct" in c.lower()]
    for col in pct_cols:
        df_display[col] = df_display[col].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "")
    return df_display


def get_operation_badge(operation: str) -> str:
    """Return a colored badge label for an OLAP operation."""
    badges = {
        "slice": "🔪 Slice",
        "dice": "🎲 Dice",
        "group_summarize": "📊 Group & Summarize",
        "drill_down": "🔍 Drill-Down",
        "roll_up": "⬆️ Roll-Up",
        "compare": "⚖️ Compare",
        "overview": "📋 Overview",
        "error": "⚠️ Error",
    }
    return badges.get(operation, f"🔷 {operation.replace('_', ' ').title()}")


SAMPLE_QUERIES = [
    "What is total revenue by region?",
    "Show Electronics sales in Europe",
    "Break down 2024 revenue by quarter",
    "Compare 2023 vs 2024 total revenue by region",
    "Which category has the highest profit margin?",
    "Show Q4 2024 data for Corporate segment",
    "Top 5 countries by profit",
    "Monthly revenue trend for 2024",
    "What percentage of revenue comes from each region?",
    "Which subcategory is performing worst?",
]
