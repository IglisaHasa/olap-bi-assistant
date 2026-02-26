"""
OLAP Business Intelligence Assistant
Tier 2 Capstone Project - Streamlit Application
"""

import json
import re
import streamlit as st
import pandas as pd
import plotly.express as px
from groq import Groq

from prompts import SYSTEM_PROMPT, WELCOME_MESSAGE, ERROR_RESPONSE
from data_utils import (
    load_data,
    get_dataset_summary,
    execute_pandas_code,
    format_currency_columns,
    get_operation_badge,
    SAMPLE_QUERIES,
)

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="OLAP BI Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
    .metric-card {
        background: #f0f4ff;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 8px;
    }
    .operation-badge {
        display: inline-block;
        background: #4f46e5;
        color: white;
        border-radius: 12px;
        padding: 2px 12px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-bottom: 6px;
    }
    .insight-box {
        background: #fffbeb;
        border-left: 4px solid #f59e0b;
        border-radius: 6px;
        padding: 10px 14px;
        margin: 8px 0;
    }
    .followup-btn {
        margin: 3px 0;
    }
    .stChatMessage [data-testid="stMarkdownContainer"] p { margin-bottom: 4px; }
</style>
""",
    unsafe_allow_html=True,
)

# ── Load data ──────────────────────────────────────────────────────────────────
df = load_data()
summary = get_dataset_summary(df)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/combo-chart.png", width=60)
    st.title("OLAP BI Assistant")
    st.caption("Global Retail Sales • 2022–2024")

    st.divider()

    # Dataset KPIs
    st.subheader("📈 Dataset Overview")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Records", summary["total_records"])
        st.metric("Revenue", summary["total_revenue"])
    with col2:
        st.metric("Profit", summary["total_profit"])
        st.metric("Avg Margin", summary["avg_profit_margin"])

    st.caption(f"📅 {summary['date_range']}")

    st.divider()

    # Filters
    st.subheader("🔧 Quick Filters")
    sel_years = st.multiselect("Year", summary["years"], default=summary["years"])
    sel_regions = st.multiselect("Region", summary["regions"], default=summary["regions"])
    sel_categories = st.multiselect("Category", summary["categories"], default=summary["categories"])

    # Apply filters to base df
    df_filtered = df[
        df["year"].isin(sel_years)
        & df["region"].isin(sel_regions)
        & df["category"].isin(sel_categories)
    ]
    st.caption(f"Filtered: **{len(df_filtered):,}** records")

    st.divider()

    # Sample queries
    st.subheader("💡 Sample Queries")
    for q in SAMPLE_QUERIES[:6]:
        if st.button(q, key=f"sq_{q}", use_container_width=True):
            st.session_state["pending_query"] = q

    st.divider()
    st.caption("Built with Streamlit + Groq LLaMA")


# ── Groq client ───────────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    try:
        return Groq(api_key=st.secrets["GROQ_API_KEY"])
    except Exception:
        return None


client = get_client()

# ── Session state ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # Groq chat history


# ── LLM call ──────────────────────────────────────────────────────────────────
def call_llm(user_query: str) -> dict:
    """Send query to Groq and return parsed JSON response."""
    if client is None:
        st.error("⚠️ Groq API key not configured. Add it to `.streamlit/secrets.toml`.")
        return ERROR_RESPONSE

    try:
        messages = (
            [{"role": "system", "content": SYSTEM_PROMPT}]
            + st.session_state.chat_history
            + [{"role": "user", "content": user_query}]
        )

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=1500,
        )
        raw = response.choices[0].message.content.strip()

        # Extract JSON from code block if present
        json_match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", raw)
        json_str = json_match.group(1) if json_match else raw

        result = json.loads(json_str)

        # Update chat history
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        st.session_state.chat_history.append({"role": "assistant", "content": raw})

        return result

    except json.JSONDecodeError:
        return ERROR_RESPONSE
    except Exception as e:
        st.error(f"API Error: {e}")
        return ERROR_RESPONSE


# ── Chart renderer ─────────────────────────────────────────────────────────────
def render_chart(chart_type: str, config: dict, result_df: pd.DataFrame):
    """Render a Plotly chart based on LLM-specified type and config."""
    x = config.get("x")
    y = config.get("y")
    color = config.get("color")
    title = config.get("title", "")

    if x not in result_df.columns:
        x = result_df.columns[0]
    if y not in result_df.columns:
        # Pick first numeric column
        num_cols = result_df.select_dtypes("number").columns.tolist()
        y = num_cols[0] if num_cols else result_df.columns[-1]
    if color and color not in result_df.columns:
        color = None

    try:
        if chart_type == "bar":
            fig = px.bar(result_df, x=x, y=y, color=color, title=title,
                         color_discrete_sequence=px.colors.qualitative.Plotly)
        elif chart_type == "line":
            fig = px.line(result_df, x=x, y=y, color=color, title=title, markers=True)
        elif chart_type == "pie":
            fig = px.pie(result_df, names=x, values=y, title=title)
        else:
            return  # "table" or "none" — handled separately

        fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            font_family="Inter, sans-serif",
            title_font_size=15,
            margin=dict(t=50, b=30, l=20, r=20),
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning(f"Could not render chart: {e}")


# ── Result renderer ────────────────────────────────────────────────────────────
def render_result(llm_response: dict, result_df: pd.DataFrame):
    """Display operation badge, chart, table, insight, and follow-ups."""
    operation = llm_response.get("operation", "")
    description = llm_response.get("description", "")
    chart_type = llm_response.get("chart_type", "table")
    chart_config = llm_response.get("chart_config", {})
    insight = llm_response.get("insight", "")
    follow_ups = llm_response.get("follow_ups", [])

    # Badge + description
    badge = get_operation_badge(operation)
    st.markdown(
        f'<span class="operation-badge">{badge}</span><br><small>{description}</small>',
        unsafe_allow_html=True,
    )

    # Chart or table
    if chart_type in ("bar", "line", "pie"):
        render_chart(chart_type, chart_config, result_df)

    # Always show data table
    with st.expander("📋 View Data Table", expanded=(chart_type == "table")):
        st.dataframe(
            format_currency_columns(result_df),
            use_container_width=True,
            hide_index=True,
        )

    # Insight
    if insight:
        st.markdown(
            f'<div class="insight-box">💡 <b>Insight:</b> {insight}</div>',
            unsafe_allow_html=True,
        )

    # Follow-up suggestions
    if follow_ups:
        st.markdown("**🔮 Suggested follow-ups:**")
        for fq in follow_ups:
            if st.button(f"→ {fq}", key=f"fu_{fq}_{len(st.session_state.messages)}",
                         use_container_width=False):
                st.session_state["pending_query"] = fq


# ── Main area ──────────────────────────────────────────────────────────────────
st.title("📊 OLAP Business Intelligence Assistant")
st.caption("Ask business questions in plain English. I'll run the analysis and show you results.")

# Show welcome on first load
if not st.session_state.messages:
    st.markdown(WELCOME_MESSAGE)

# Render chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "user":
            st.markdown(msg["content"])
        else:
            # Assistant message contains pre-rendered result stored as metadata
            st.markdown(msg.get("text", ""))
            if "result_df" in msg and msg["result_df"] is not None:
                render_result(msg["llm_response"], msg["result_df"])

# ── Chat input ─────────────────────────────────────────────────────────────────
# Handle pending query from sidebar buttons or follow-up buttons
pending = st.session_state.pop("pending_query", None)
user_input = st.chat_input("Ask a question about the data…") or pending

if user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Call LLM & execute code
    with st.chat_message("assistant"):
        with st.spinner("Analyzing…"):
            llm_response = call_llm(user_input)
            pandas_code = llm_response.get("pandas_code", "df_result = df.head(10)")

            # Execute against filtered dataframe
            result_df, error = execute_pandas_code(pandas_code, df_filtered)

            if error:
                st.warning(f"⚠️ Code execution error: {error}\n\nShowing sample data instead.")
                result_df = df_filtered.head(10)

            summary_text = llm_response.get("description", "Analysis complete.")
            st.markdown(f"*{summary_text}*")
            render_result(llm_response, result_df)

    # Persist assistant message
    st.session_state.messages.append(
        {
            "role": "assistant",
            "text": f"*{summary_text}*",
            "llm_response": llm_response,
            "result_df": result_df,
        }
    )

# ── Footer ─────────────────────────────────────────────────────────────────────
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("📊 OLAP BI Assistant • Tier 2 Capstone")
with col2:
    st.caption(f"🗄️ {len(df_filtered):,} records in scope")
with col3:
    if st.button("🗑️ Clear conversation", use_container_width=False):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.rerun()
