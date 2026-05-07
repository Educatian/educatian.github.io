"""
Streamlit starter for API -> NLP dashboard records.

Expected input:
  data/dashboard_records.jsonl

Run:
  streamlit run streamlit_dashboard_starter.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st


DATA_PATH = Path("data/dashboard_records.jsonl")


st.set_page_config(
    page_title="API -> NLP Dashboard",
    layout="wide",
)


@st.cache_data(show_spinner=False)
def load_records(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_json(path, lines=True)
    if "nlp" in df.columns:
        nlp = pd.json_normalize(df["nlp"]).add_prefix("nlp.")
        df = pd.concat([df.drop(columns=["nlp"]), nlp], axis=1)
    return df


df = load_records(DATA_PATH)

st.title("API -> NLP Dashboard")
st.caption("Reads prepared dashboard_records.jsonl. It does not call source APIs or run expensive NLP live.")

if df.empty:
    st.info(
        "No dashboard records found. Copy templates/dashboard-records-sample.jsonl "
        "to data/dashboard_records.jsonl for a demo, or run the collector/NLP pipeline first."
    )
    st.stop()

for col in ["source_id", "review_state", "nlp.priority", "nlp.confidence"]:
    if col not in df.columns:
        df[col] = None

with st.sidebar:
    st.header("Filters")
    sources = sorted([x for x in df["source_id"].dropna().unique()])
    selected_sources = st.multiselect("Source", sources, default=sources)
    priorities = sorted([x for x in df["nlp.priority"].dropna().unique()])
    selected_priorities = st.multiselect("Priority", priorities, default=priorities)
    min_conf = st.slider("Minimum NLP confidence", 0.0, 1.0, 0.0, 0.05)

filtered = df.copy()
if selected_sources:
    filtered = filtered[filtered["source_id"].isin(selected_sources)]
if selected_priorities:
    filtered = filtered[filtered["nlp.priority"].isin(selected_priorities)]
filtered = filtered[filtered["nlp.confidence"].fillna(0) >= min_conf]

tab_overview, tab_records, tab_review, tab_sources = st.tabs(
    ["Overview", "Records", "Review Queue", "Source Health"]
)

with tab_overview:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Records", len(filtered))
    c2.metric("Sources", filtered["source_id"].nunique())
    c3.metric("Needs review", int((filtered["review_state"] == "needs_review").sum()))
    c4.metric("Avg. confidence", f"{filtered['nlp.confidence'].fillna(0).mean():.2f}")

    st.subheader("Priority mix")
    if "nlp.priority" in filtered:
        st.bar_chart(filtered["nlp.priority"].fillna("unknown").value_counts())

with tab_records:
    st.subheader("Record explorer")
    visible_cols = [
        c for c in [
            "record_id",
            "source_id",
            "title",
            "source_url",
            "nlp.summary",
            "nlp.topic_labels",
            "nlp.confidence",
            "review_state",
        ] if c in filtered.columns
    ]
    st.dataframe(filtered[visible_cols], use_container_width=True, hide_index=True)

with tab_review:
    st.subheader("Review queue")
    priority_rank = {"high": 0, "medium": 1, "low": 2}
    queue = filtered.assign(
        priority_rank=filtered["nlp.priority"].map(priority_rank).fillna(9)
    ).sort_values(["priority_rank", "nlp.confidence"], ascending=[True, False])
    for _, row in queue.head(25).iterrows():
        with st.expander(f"{row.get('title', 'Untitled')} | {row.get('nlp.priority', 'unknown')}"):
            st.write(row.get("nlp.summary", "No summary."))
            st.caption(f"Reason: {row.get('nlp.review_reason', 'No reason provided')}")
            st.caption(f"Confidence: {row.get('nlp.confidence', 0):.2f}")
            st.link_button("Open source", row.get("source_url", "#"))

with tab_sources:
    st.subheader("Source health")
    health = (
        filtered.groupby("source_id", dropna=False)
        .agg(records=("record_id", "count"), avg_confidence=("nlp.confidence", "mean"))
        .reset_index()
    )
    st.dataframe(health, use_container_width=True, hide_index=True)
