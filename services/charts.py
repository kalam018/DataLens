"""services/charts.py — Plotly chart builders (optimized for large datasets)."""
from __future__ import annotations

import polars as pl
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import streamlit as st

# ── Theme ────────────────────────────────────────────────────────────────────
BG       = "#0d0f14"
SURFACE  = "#161922"
BORDER   = "#252a35"
ACCENT   = "#00e5a0"
ACCENT2  = "#5b7fff"
DANGER   = "#ff4f5e"
MUTED    = "#7a8394"
TEXT     = "#e8ecf2"

PALETTE  = [ACCENT, ACCENT2, DANGER, "#f5a623", "#bd10e0", "#7ed321", "#417505"]

LAYOUT_BASE = dict(
    paper_bgcolor=BG,
    plot_bgcolor=SURFACE,
    font=dict(family="Syne, sans-serif", color=TEXT, size=12),
    xaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER),
    yaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER),
    margin=dict(l=40, r=20, t=50, b=40),
    colorway=PALETTE,
)

SAMPLE_SIZE = 10000  # Max points to render in charts


def _sample_for_viz(df: pl.DataFrame, max_rows: int = SAMPLE_SIZE) -> pl.DataFrame:
    """Intelligently sample large datasets for visualization."""
    if df.height <= max_rows:
        return df
    return df.sample(n=max_rows, seed=42, with_replacement=False)


def histogram(df: pl.DataFrame, column: str, bins: int = 40) -> go.Figure:
    arr = df[column].drop_nulls().to_numpy()
    
    # For large arrays, use histogram instead of scatter
    if len(arr) > SAMPLE_SIZE:
        arr = np.random.choice(arr, SAMPLE_SIZE, replace=False)
    
    fig = go.Figure(go.Histogram(x=arr, nbinsx=bins, marker_color=ACCENT, opacity=0.85))
    fig.update_layout(title=f"Distribution — {column}", **LAYOUT_BASE)
    return fig


def box_plot(df: pl.DataFrame, column: str, group_by: str | None = None) -> go.Figure:
    plot_df = _sample_for_viz(df)
    pdf = plot_df.to_pandas()
    kwargs = dict(y=column, color=group_by) if group_by else dict(y=column)
    fig = px.box(pdf, **kwargs, color_discrete_sequence=PALETTE)
    fig.update_layout(title=f"Box Plot — {column}", **LAYOUT_BASE)
    return fig


def scatter(df: pl.DataFrame, x: str, y: str, color: str | None = None, trendline: bool = False) -> go.Figure:
    plot_df = _sample_for_viz(df)
    pdf = plot_df.to_pandas()
    kwargs = dict(x=x, y=y, color=color, opacity=0.7)
    if trendline:
        kwargs["trendline"] = "ols"
        kwargs["trendline_color_override"] = DANGER
    fig = px.scatter(pdf, **kwargs, color_discrete_sequence=PALETTE)
    fig.update_layout(title=f"{x} vs {y}", **LAYOUT_BASE)
    return fig


def bar_chart(df: pl.DataFrame, x: str, y: str, orientation: str = "v") -> go.Figure:
    plot_df = _sample_for_viz(df, max_rows=500)  # Limit bars to prevent crowding
    pdf = plot_df.to_pandas()
    fig = px.bar(pdf, x=x, y=y, orientation=orientation, color_discrete_sequence=PALETTE)
    fig.update_layout(title=f"{y} by {x}", **LAYOUT_BASE)
    return fig


def line_chart(df: pl.DataFrame, x: str, y: list[str]) -> go.Figure:
    plot_df = _sample_for_viz(df)
    pdf = plot_df.to_pandas()
    fig = px.line(pdf, x=x, y=y, color_discrete_sequence=PALETTE)
    fig.update_layout(title=f"Line — {', '.join(y)}", **LAYOUT_BASE)
    return fig


def heatmap_correlation(corr_df: pl.DataFrame) -> go.Figure:
    cols = corr_df.columns
    z = corr_df.to_numpy()
    fig = go.Figure(go.Heatmap(
        z=z, x=cols, y=cols,
        colorscale=[[0, DANGER], [0.5, SURFACE], [1, ACCENT]],
        zmid=0, zmin=-1, zmax=1,
        text=np.round(z, 2),
        texttemplate="%{text}",
        textfont=dict(size=10),
    ))
    fig.update_layout(title="Correlation Matrix", **LAYOUT_BASE, height=600)
    return fig


def pie_chart(df: pl.DataFrame, column: str, limit: int = 10) -> go.Figure:
    vc = df[column].value_counts().sort("count", descending=True).head(limit)
    fig = go.Figure(go.Pie(
        labels=vc[column].to_list(),
        values=vc["count"].to_list(),
        hole=0.45,
        marker=dict(colors=PALETTE),
    ))
    fig.update_layout(title=f"{column} — Top {limit}", **LAYOUT_BASE)
    return fig


def qq_plot(series: pl.Series) -> go.Figure:
    from scipy import stats as sp_stats
    
    arr = series.drop_nulls().to_numpy().astype(float)
    
    # Sample if too large
    if len(arr) > SAMPLE_SIZE:
        arr = np.random.choice(arr, SAMPLE_SIZE, replace=False)
    
    (osm, osr), _ = sp_stats.probplot(arr)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=osm, y=osr, mode="markers", marker=dict(color=ACCENT, size=5), name="Data"))
    lo, hi = min(osm), max(osm)
    slope, intercept, *_ = sp_stats.linregress(osm, osr)
    fig.add_trace(go.Scatter(x=[lo, hi], y=[slope * lo + intercept, slope * hi + intercept],
                             mode="lines", line=dict(color=DANGER, dash="dash"), name="Normal"))
    fig.update_layout(title=f"Q-Q Plot — {series.name}", **LAYOUT_BASE)
    return fig
