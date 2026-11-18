"""pages/dashboard.py — interactive chart builder."""
from __future__ import annotations

import streamlit as st
import polars as pl
from services import charts


def _save_report_figure(title, fig, interpretation):
    """Keep a copy of a displayed chart so the PDF report can embed it."""
    items = st.session_state.setdefault("report_figures", [])
    # Replace an existing chart with the same title instead of duplicating it.
    items[:] = [x for x in items if x[0] != title]
    items.append((title, fig, interpretation))


def render():
    st.markdown("## 📈 Dashboard")

    if "df" not in st.session_state or st.session_state.df is None:
        st.warning("⬅ Upload a dataset first.")
        return

    df: pl.DataFrame = st.session_state.df

    numeric_cols = [c for c in df.columns if df[c].dtype in (
        pl.Float32, pl.Float64, pl.Int8, pl.Int16, pl.Int32, pl.Int64,
        pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64,
    )]
    all_cols = df.columns

    st.markdown("### Chart Builder")

    chart_type = st.selectbox("Chart type", [
        "Histogram", "Box Plot", "Scatter", "Bar Chart", "Line Chart"
    ])

    if chart_type == "Histogram":
        col  = st.selectbox("Column", numeric_cols)
        bins = st.slider("Bins", 10, 100, 40)
        fig  = charts.histogram(df, col, bins)
        st.plotly_chart(fig, use_container_width=True)
        _save_report_figure(
            f"Histogram — {col}", fig,
            f"This histogram shows the distribution of {col}. It helps identify the typical range, concentration, and unusual values."
        )

    elif chart_type == "Box Plot":
        col      = st.selectbox("Value column", numeric_cols)
        cat_cols = [c for c in df.columns if df[c].dtype in (pl.Utf8, pl.Categorical) and df[c].n_unique() <= 30]
        group    = st.selectbox("Group by (optional)", ["—"] + cat_cols)
        fig      = charts.box_plot(df, col, group if group != "—" else None)
        st.plotly_chart(fig, use_container_width=True)
        _save_report_figure(
            f"Box Plot — {col}", fig,
            f"This box plot summarizes the spread of {col}. The box represents the middle portion of observations and the points outside the main range may indicate unusual values."
        )

    elif chart_type == "Scatter":
        c1, c2 = st.columns(2)
        with c1:
            x_col = st.selectbox("X axis", numeric_cols, key="sc_x")
        with c2:
            y_col = st.selectbox("Y axis", numeric_cols, index=min(1, len(numeric_cols)-1), key="sc_y")
        cat_cols = [c for c in df.columns if df[c].dtype in (pl.Utf8, pl.Categorical) and df[c].n_unique() <= 20]
        color   = st.selectbox("Color by (optional)", ["—"] + cat_cols)
        trendline = st.checkbox("Add trendline (OLS)")

        # Sample for performance
        plot_df = df.sample(min(5000, df.height), seed=42) if df.height > 5000 else df
        fig = charts.scatter(plot_df, x_col, y_col,
                             color if color != "—" else None, trendline)
        if df.height > 5000:
            st.caption(f"ℹ Showing a random sample of 5,000 / {df.height:,} rows for performance.")
        st.plotly_chart(fig, use_container_width=True)
        _save_report_figure(
            f"{x_col} vs {y_col}", fig,
            f"This scatter plot shows the relationship between {x_col} and {y_col}. A visible upward or downward pattern indicates an association, but does not by itself prove causation."
        )

    elif chart_type == "Bar Chart":
        cat_cols = [c for c in df.columns if df[c].dtype in (pl.Utf8, pl.Categorical, pl.Boolean)
                    and df[c].n_unique() <= 100]
        if not cat_cols:
            st.info("No categorical columns with ≤100 unique values found.")
            return
        x_col = st.selectbox("Category (X)", cat_cols)
        y_col = st.selectbox("Value (Y)", numeric_cols)

        con = __import__("duckdb").connect()
        con.register("tbl", df.to_pandas())
        agg_fn = st.selectbox("Aggregation", ["SUM","AVG","COUNT","MIN","MAX"])
        q = f'SELECT "{x_col}", {agg_fn}("{y_col}") AS value FROM tbl GROUP BY "{x_col}" ORDER BY value DESC LIMIT 30'
        agg_df = pl.from_pandas(con.execute(q).df())
        fig = charts.bar_chart(agg_df, x_col, "value")
        st.plotly_chart(fig, use_container_width=True)
        _save_report_figure(
            f"{y_col} by {x_col}", fig,
            f"This bar chart compares {y_col} across the categories in {x_col}. Larger bars represent larger aggregated values."
        )

    elif chart_type == "Line Chart":
        x_col  = st.selectbox("X axis (time/ordered)", all_cols)
        y_cols = st.multiselect("Y columns", numeric_cols, default=numeric_cols[:1])
        if y_cols:
            plot_df = df.sort(x_col) if df.height > 1 else df
            plot_df = plot_df.sample(min(2000, plot_df.height), seed=42) if plot_df.height > 2000 else plot_df
            fig = charts.line_chart(plot_df, x_col, y_cols)
            st.plotly_chart(fig, use_container_width=True)
            _save_report_figure(
                f"Line — {', '.join(y_cols)}", fig,
                f"This line chart shows how {', '.join(y_cols)} changes across {x_col}."
            )

    # ── DuckDB query sandbox ──────────────────────────────────────────────────
    st.divider()
    st.markdown("### 🦆 SQL Query Sandbox")
    st.markdown("<span style='color:#7a8394;font-family:Space Mono,monospace;font-size:.75rem'>Table name: <b>tbl</b></span>", unsafe_allow_html=True)
    query = st.text_area("DuckDB SQL", value='SELECT * FROM tbl LIMIT 20', height=100)
    if st.button("Run Query"):
        try:
            import duckdb
            con2 = duckdb.connect()
            con2.register("tbl", df.to_pandas())
            result = con2.execute(query).pl()
            st.dataframe(result.to_pandas(), use_container_width=True)
            st.caption(f"{result.height:,} rows returned.")
        except Exception as e:
            st.error(str(e))
