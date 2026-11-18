"""services/correlation.py — correlation & association analysis."""
from __future__ import annotations

import polars as pl
import numpy as np
import duckdb
from scipy import stats as scipy_stats
import streamlit as st


@st.cache_data(show_spinner=False)
def pearson_matrix(_df: pl.DataFrame) -> pl.DataFrame:
    numeric_cols = [
        c for c in _df.columns
        if _df[c].dtype in (
            pl.Float32, pl.Float64, pl.Int8, pl.Int16, pl.Int32, pl.Int64,
            pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64,
        )
    ]
    if len(numeric_cols) < 2:
        return pl.DataFrame()
    sub = _df.select(numeric_cols).to_pandas()
    corr = sub.corr(method="pearson")
    return pl.from_pandas(corr.reset_index(drop=True)).rename(
        {old: new for old, new in zip(pl.from_pandas(corr.reset_index(drop=True)).columns, numeric_cols)}
    )


@st.cache_data(show_spinner=False)
def spearman_matrix(_df: pl.DataFrame) -> pl.DataFrame:
    numeric_cols = [
        c for c in _df.columns
        if _df[c].dtype in (
            pl.Float32, pl.Float64, pl.Int8, pl.Int16, pl.Int32, pl.Int64,
            pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64,
        )
    ]
    if len(numeric_cols) < 2:
        return pl.DataFrame()
    sub = _df.select(numeric_cols).to_pandas()
    corr = sub.corr(method="spearman")
    return pl.from_pandas(corr.reset_index(drop=True)).rename(
        {old: new for old, new in zip(pl.from_pandas(corr.reset_index(drop=True)).columns, numeric_cols)}
    )


def top_pairs(_corr: pl.DataFrame, n: int = 10, abs_threshold: float = 0.0) -> list[dict]:
    cols = _corr.columns
    arr = _corr.to_numpy()
    pairs = []
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            v = arr[i, j]
            if not np.isnan(v) and abs(v) >= abs_threshold:
                pairs.append({"col_a": cols[i], "col_b": cols[j], "correlation": round(float(v), 4)})
    pairs.sort(key=lambda x: abs(x["correlation"]), reverse=True)
    return pairs[:n]


def chi_square_test(_df: pl.DataFrame, col_a: str, col_b: str) -> dict:
    pdf = _df.select([col_a, col_b]).to_pandas()
    ct = pdf.groupby([col_a, col_b]).size().unstack(fill_value=0)
    chi2, p, dof, _ = scipy_stats.chi2_contingency(ct.values)
    return {"chi2": round(float(chi2), 4), "p_value": round(float(p), 4), "dof": int(dof)}


def cramers_v(_df: pl.DataFrame, col_a: str, col_b: str) -> float:
    res = chi_square_test(_df, col_a, col_b)
    n = _df.height
    k = min(_df[col_a].n_unique(), _df[col_b].n_unique())
    v = np.sqrt(res["chi2"] / (n * (k - 1))) if k > 1 else 0
    return round(float(v), 4)
