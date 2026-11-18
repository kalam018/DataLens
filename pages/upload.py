"""pages/upload.py — dataset ingestion page."""
from __future__ import annotations

import streamlit as st
import polars as pl
from services.loader import load_uploaded, schema_summary


def render():
    st.markdown("## 📤 Upload Dataset")
    st.markdown("<p style='color:#7a8394;font-family:Space Mono,monospace;font-size:.8rem'>Supported: CSV · XLSX · Parquet · JSON</p>", unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Drop your file here",
        type=["csv", "xlsx", "xls", "parquet", "json"],
        label_visibility="collapsed",
    )

    if uploaded:
        with st.spinner("Loading…"):
            try:
                # Keep the original uploaded bytes separately. This allows the
                # "Download Original CSV" button to return the source file
                # without adding/removing/changing any dataset values.
                uploaded_bytes = uploaded.getvalue()
                df = load_uploaded(uploaded)
                st.session_state["df"] = df
                st.session_state["df_raw"] = df.clone()
                st.session_state["original_file_bytes"] = uploaded_bytes
                st.session_state["filename"] = uploaded.name
            except Exception as e:
                st.error(f"Failed to load file: {e}")
                return

    if "df" not in st.session_state or st.session_state.df is None:
        st.info("Upload a dataset to get started.")
        return

    df: pl.DataFrame = st.session_state.df
    fname = st.session_state.get("filename", "dataset")

    # ── Summary cards ─────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    for col, label, val, color in [
        (c1, "ROWS",    f"{df.height:,}",  "#00e5a0"),
        (c2, "COLUMNS", f"{df.width:,}",   "#5b7fff"),
        (c3, "NULLS",   f"{df.null_count().sum_horizontal()[0]:,}", "#ff4f5e"),
        (c4, "FILE",    fname[:18],         "#f5a623"),
    ]:
        col.markdown(
            f"<div class='metric-card' style='border-left-color:{color}'>"
            f"<div class='metric-label'>{label}</div>"
            f"<div class='metric-value' style='color:{color};font-size:1.3rem'>{val}</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # ── Preview ───────────────────────────────────────────────────────────────
    tab1, tab2 = st.tabs(["📋 Preview", "🗂 Schema"])

    with tab1:
        n_rows = st.slider("Rows to preview", 5, min(500, df.height), 20, key="preview_rows")
        st.dataframe(df.head(n_rows).to_pandas(), use_container_width=True, height=400)

    with tab2:
        schema = schema_summary(df)
        st.dataframe(schema, use_container_width=True)
