"""pages/statistics.py — descriptive statistics & column profiling."""
from __future__ import annotations

import streamlit as st
import polars as pl
from services import stats as svc_stats
from services import charts


def render():
    st.markdown("## 📊 Statistics")

    if "df" not in st.session_state or st.session_state.df is None:
        st.warning("⬅ Upload a dataset first.")
        return

    df: pl.DataFrame = st.session_state.df

    tab1, tab2, tab3 = st.tabs(["Descriptive Summary", "Column Profile", "Value Counts"])

    # ── Tab 1: full descriptive table ─────────────────────────────────────────
    with tab1:
        with st.spinner("Computing…"):
            desc = svc_stats.descriptive(df)
        if desc.is_empty():
            st.info("No numeric columns found.")
        else:
            st.dataframe(
                desc.to_pandas().set_index("column").round(4),
                use_container_width=True,
            )

    # ── Tab 2: single column deep-dive ───────────────────────────────────────
    with tab2:
        numeric_cols = [c for c in df.columns if df[c].dtype in (
            pl.Float32, pl.Float64, pl.Int8, pl.Int16, pl.Int32, pl.Int64,
            pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64,
        )]
        if not numeric_cols:
            st.info("No numeric columns to profile.")
        else:
            col = st.selectbox("Select column", numeric_cols, key="profile_col")
            profile = svc_stats.column_profile(df, col)

            r1c1, r1c2, r1c3, r1c4 = st.columns(4)
            cards = [
                ("MEAN",    profile.get("mean",   "—"), "#00e5a0"),
                ("STD DEV", profile.get("std",    "—"), "#5b7fff"),
                ("SKEW",    profile.get("skewness","—"), "#f5a623"),
                ("KURT",    profile.get("kurtosis","—"), "#ff4f5e"),
            ]
            for card_col, (label, val, color) in zip([r1c1,r1c2,r1c3,r1c4], cards):
                v = round(float(val), 3) if isinstance(val, (int, float)) else val
                card_col.markdown(
                    f"<div class='metric-card' style='border-left-color:{color}'>"
                    f"<div class='metric-label'>{label}</div>"
                    f"<div class='metric-value' style='color:{color};font-size:1.3rem'>{v}</div></div>",
                    unsafe_allow_html=True,
                )

            st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

            # Normality test result
            if profile.get("test"):
                is_normal = profile.get("normal")
                label = "✅ Likely Normal" if is_normal else "⚠ Not Normal"
                color = "#00e5a0" if is_normal else "#ff4f5e"
                st.markdown(
                    f"<div class='metric-card' style='border-left-color:{color}'>"
                    f"<div class='metric-label'>{profile['test']} — p={profile['p_value']}</div>"
                    f"<div class='metric-value' style='color:{color};font-size:1rem'>{label}</div></div>",
                    unsafe_allow_html=True,
                )
                st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                bins = st.slider("Histogram bins", 10, 100, 40, key="hist_bins")
                st.plotly_chart(charts.histogram(df, col, bins), use_container_width=True)
            with c2:
                st.plotly_chart(charts.qq_plot(df[col]), use_container_width=True)

            st.plotly_chart(charts.box_plot(df, col), use_container_width=True)

    # ── Tab 3: value counts ───────────────────────────────────────────────────
    with tab3:
        cat_cols = [c for c in df.columns if df[c].dtype in (pl.Utf8, pl.Categorical, pl.Boolean)]
        all_cols = cat_cols + [c for c in df.columns if c not in cat_cols]
        col = st.selectbox("Select column", all_cols, key="vc_col")
        limit = st.slider("Top N values", 5, 50, 20, key="vc_limit")

        vc = svc_stats.value_counts(df, col, limit)
        c1, c2 = st.columns([1, 1])
        with c1:
            st.dataframe(vc.to_pandas(), use_container_width=True)
        with c2:
            if df[col].n_unique() <= 50:
                st.plotly_chart(charts.pie_chart(df, col, limit), use_container_width=True)
            else:
                pdf = vc.to_pandas()
                st.plotly_chart(
                    charts.bar_chart(vc, col, "count"),
                    use_container_width=True,
                )
