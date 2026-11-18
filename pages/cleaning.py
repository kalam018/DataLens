"""pages/cleaning.py — interactive data-cleaning page."""
from __future__ import annotations

import streamlit as st
import polars as pl
from services import cleaner


def _require_df() -> pl.DataFrame | None:
    if "df" not in st.session_state or st.session_state.df is None:
        st.warning("⬅ Upload a dataset first.")
        return None
    return st.session_state.df


def render():
    st.markdown("## 🧹 Data Cleaning")

    df = _require_df()
    if df is None:
        return

    st.markdown(f"<span style='font-family:Space Mono,monospace;color:#7a8394;font-size:.75rem'>{df.height:,} rows × {df.width} cols</span>", unsafe_allow_html=True)

    # ── Null overview ─────────────────────────────────────────────────────────
    with st.expander("🔍 Null Analysis", expanded=True):
        null_counts = {c: df[c].null_count() for c in df.columns}
        null_df = pl.DataFrame({"Column": list(null_counts.keys()), "Nulls": list(null_counts.values())})
        null_df = null_df.with_columns((pl.col("Nulls") / df.height * 100).round(1).alias("Null %"))
        null_df = null_df.filter(pl.col("Nulls") > 0)
        if null_df.is_empty():
            st.success("✅ No nulls found!")
        else:
            st.dataframe(null_df.to_pandas(), use_container_width=True)

    # ── Operations ────────────────────────────────────────────────────────────
    st.markdown("### Operations")

    op = st.selectbox("Choose operation", [
        "Drop rows with nulls",
        "Fill nulls — mean",
        "Fill nulls — median",
        "Fill nulls — constant",
        "Drop duplicate rows",
        "Drop columns",
        "Trim string whitespace",
        "Remove outliers (IQR)",
        "Cast column dtype",
        "Rename column",
    ])

    numeric_cols = [c for c in df.columns if df[c].dtype in (
        pl.Float32, pl.Float64, pl.Int8, pl.Int16, pl.Int32, pl.Int64,
        pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64,
    )]
    string_cols  = [c for c in df.columns if df[c].dtype == pl.Utf8]

    if op == "Drop rows with nulls":
        subset = st.multiselect("Subset columns (leave empty = all)", df.columns)
        if st.button("Apply"):
            df = cleaner.drop_nulls(df, subset or None)
            st.session_state.df = df
            st.success(f"Rows remaining: {df.height:,}")

    elif op == "Fill nulls — mean":
        cols = st.multiselect("Numeric columns", numeric_cols, default=numeric_cols[:1])
        if st.button("Apply"):
            df = cleaner.fill_nulls_mean(df, cols)
            st.session_state.df = df
            st.success("Filled with column means.")

    elif op == "Fill nulls — median":
        cols = st.multiselect("Numeric columns", numeric_cols, default=numeric_cols[:1])
        if st.button("Apply"):
            df = cleaner.fill_nulls_median(df, cols)
            st.session_state.df = df
            st.success("Filled with column medians.")

    elif op == "Fill nulls — constant":
        cols = st.multiselect("Columns", df.columns)
        val  = st.text_input("Constant value")
        if st.button("Apply") and cols and val:
            df = cleaner.fill_nulls_constant(df, cols, val)
            st.session_state.df = df
            st.success(f"Filled with '{val}'.")

    elif op == "Drop duplicate rows":
        subset = st.multiselect("Subset columns (leave empty = all)", df.columns)
        before = df.height
        if st.button("Apply"):
            df = cleaner.drop_duplicates(df, subset or None)
            st.session_state.df = df
            st.success(f"Removed {before - df.height:,} duplicate rows.")

    elif op == "Drop columns":
        cols = st.multiselect("Select columns to drop", df.columns)
        if st.button("Apply") and cols:
            df = cleaner.drop_columns(df, cols)
            st.session_state.df = df
            st.success(f"Dropped: {', '.join(cols)}")

    elif op == "Trim string whitespace":
        cols = st.multiselect("String columns", string_cols, default=string_cols[:1])
        if st.button("Apply") and cols:
            df = cleaner.trim_strings(df, cols)
            st.session_state.df = df
            st.success("Trimmed whitespace.")

    elif op == "Remove outliers (IQR)":
        col = st.selectbox("Numeric column", numeric_cols)
        factor = st.slider("IQR factor", 1.0, 3.0, 1.5, 0.1)
        before = df.height
        if st.button("Apply"):
            df = cleaner.remove_outliers_iqr(df, col, factor)
            st.session_state.df = df
            st.success(f"Removed {before - df.height:,} outlier rows.")

    elif op == "Cast column dtype":
        col   = st.selectbox("Column", df.columns)
        dtype = st.selectbox("Target dtype", ["Int32","Int64","Float32","Float64","Utf8","Boolean","Date","Datetime"])
        if st.button("Apply"):
            try:
                df = cleaner.cast_column(df, col, dtype)
                st.session_state.df = df
                st.success(f"Cast '{col}' to {dtype}.")
            except Exception as e:
                st.error(str(e))

    elif op == "Rename column":
        col     = st.selectbox("Column to rename", df.columns)
        new_name = st.text_input("New name")
        if st.button("Apply") and new_name:
            df = cleaner.rename_columns(df, {col: new_name})
            st.session_state.df = df
            st.success(f"Renamed '{col}' → '{new_name}'.")

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("↩ Reset to original"):
            st.session_state.df = st.session_state.df_raw.clone()
            st.success("Reset to original.")
    with col2:
        st.markdown(f"**Current shape:** `{st.session_state.df.height:,} × {st.session_state.df.width}`")

    # ── Preview ───────────────────────────────────────────────────────────────
    with st.expander("Preview cleaned data", expanded=False):
        st.dataframe(st.session_state.df.head(100).to_pandas(), use_container_width=True)
