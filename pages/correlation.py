"""pages/correlation.py — correlation & association analysis."""
from __future__ import annotations

import streamlit as st
import polars as pl
from services import correlation, charts


def render():
    st.markdown("## 🔗 Correlation Analysis")

    if "df" not in st.session_state or st.session_state.df is None:
        st.warning("⬅ Upload a dataset first.")
        return

    df: pl.DataFrame = st.session_state.df

    numeric_cols = [c for c in df.columns if df[c].dtype in (
        pl.Float32, pl.Float64, pl.Int8, pl.Int16, pl.Int32, pl.Int64,
        pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64,
    )]

    if len(numeric_cols) < 2:
        st.warning("Need at least 2 numeric columns.")
        return

    tab1, tab2, tab3 = st.tabs(["Pearson", "Spearman", "Categorical"])

    # ── Tab 1: Pearson ───────────────────────────────────────────────────────
    with tab1:
        with st.spinner("Computing Pearson correlation…"):
            corr = correlation.pearson_matrix(df)
        if corr.is_empty():
            st.info("No numeric columns.")
        else:
            c1, c2 = st.columns([1.2, 1])
            with c1:
                st.plotly_chart(charts.heatmap_correlation(corr), use_container_width=True)
            with c2:
                st.markdown("**Top Pairs**")
                pairs = correlation.top_pairs(corr, n=15, abs_threshold=0.1)
                for pair in pairs:
                    color = "#00e5a0" if pair["correlation"] > 0 else "#ff4f5e"
                    st.markdown(
                        f"<div style='padding:.5rem;background:#161922;border-left:3px solid {color};border-radius:4px;margin-bottom:.5rem'>"
                        f"<div style='font-family:Space Mono,monospace;font-size:.75rem;color:#7a8394'>{pair['col_a']} ↔ {pair['col_b']}</div>"
                        f"<div style='font-size:1.1rem;color:{color};font-weight:800'>{pair['correlation']:.3f}</div></div>",
                        unsafe_allow_html=True,
                    )

    # ── Tab 2: Spearman ──────────────────────────────────────────────────────
    with tab2:
        with st.spinner("Computing Spearman correlation…"):
            corr_sp = correlation.spearman_matrix(df)
        if corr_sp.is_empty():
            st.info("No numeric columns.")
        else:
            c1, c2 = st.columns([1.2, 1])
            with c1:
                st.plotly_chart(charts.heatmap_correlation(corr_sp), use_container_width=True)
            with c2:
                st.markdown("**Top Pairs** (rank-based)")
                pairs = correlation.top_pairs(corr_sp, n=15, abs_threshold=0.1)
                for pair in pairs:
                    color = "#00e5a0" if pair["correlation"] > 0 else "#ff4f5e"
                    st.markdown(
                        f"<div style='padding:.5rem;background:#161922;border-left:3px solid {color};border-radius:4px;margin-bottom:.5rem'>"
                        f"<div style='font-family:Space Mono,monospace;font-size:.75rem;color:#7a8394'>{pair['col_a']} ↔ {pair['col_b']}</div>"
                        f"<div style='font-size:1.1rem;color:{color};font-weight:800'>{pair['correlation']:.3f}</div></div>",
                        unsafe_allow_html=True,
                    )

    # ── Tab 3: Categorical ───────────────────────────────────────────────────
    with tab3:
        cat_cols = [c for c in df.columns if df[c].dtype in (pl.Utf8, pl.Categorical, pl.Boolean)]
        if len(cat_cols) < 2:
            st.info("Need at least 2 categorical columns.")
        else:
            c1, c2 = st.selectbox("Column A", cat_cols), st.selectbox("Column B", cat_cols, key="cat_b")
            if c1 == c2:
                st.warning("Select different columns.")
            else:
                with st.spinner("Computing association…"):
                    cramers = correlation.cramers_v(df, c1, c2)
                    chi2_res = correlation.chi_square_test(df, c1, c2)

                st.markdown(
                    f"<div class='metric-card'><div class='metric-label'>Cramér's V</div>"
                    f"<div class='metric-value' style='color:#00e5a0'>{cramers:.3f}</div></div>",
                    unsafe_allow_html=True,
                )
                st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)

                c_chi, c_p, c_dof = st.columns(3)
                c_chi.metric("χ² Statistic", f"{chi2_res['chi2']:.3f}")
                c_p.metric("p-value", f"{chi2_res['p_value']:.4f}")
                c_dof.metric("DoF", chi2_res['dof'])

                st.markdown("**Contingency Table**")
                pdf = df.select([c1, c2]).to_pandas()
                ct = pdf.groupby([c1, c2]).size().unstack(fill_value=0)
                st.dataframe(ct, use_container_width=True)
