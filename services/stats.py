"""services/stats.py — descriptive & inferential statistics (optimized for large data)."""
from __future__ import annotations

import numpy as np
import polars as pl
import duckdb
from scipy import stats as scipy_stats
import streamlit as st


def descriptive(_df: pl.DataFrame) -> pl.DataFrame:
    """Full descriptive stats for all numeric columns via DuckDB (memory-efficient)."""
    numeric_cols = [c for c in _df.columns if _df[c].dtype in (
        pl.Float32, pl.Float64, pl.Int8, pl.Int16, pl.Int32, pl.Int64,
        pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64
    )]
    if not numeric_cols:
        return pl.DataFrame()

    rows = []
    progress = st.progress(0)
    for idx, col in enumerate(numeric_cols):
        # Use DuckDB for efficient aggregation
        con = duckdb.connect(":memory:")
        con.register("tbl", _df.select([col]).to_pandas())
        
        q = f"""
        SELECT
            COUNT("{col}")   AS count,
            AVG("{col}")     AS mean,
            STDDEV("{col}")  AS std,
            MIN("{col}")     AS min,
            PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY "{col}") AS q25,
            MEDIAN("{col}")  AS median,
            PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY "{col}") AS q75,
            MAX("{col}")     AS max
        FROM tbl
        """
        res = con.execute(q).fetchone()
        con.close()
        
        if res:
            rows.append({
                "column": col,
                "count": int(res[0]) if res[0] else 0,
                "mean": round(float(res[1]), 4) if res[1] else None,
                "std": round(float(res[2]), 4) if res[2] else None,
                "min": float(res[3]) if res[3] else None,
                "q25": float(res[4]) if res[4] else None,
                "median": float(res[5]) if res[5] else None,
                "q75": float(res[6]) if res[6] else None,
                "max": float(res[7]) if res[7] else None,
                "range": float(res[7] - res[3]) if res[7] and res[3] else None,
            })
        
        progress.progress(min((idx + 1) / len(numeric_cols), 1.0))
    
    progress.empty()
    return pl.DataFrame(rows) if rows else pl.DataFrame()


def value_counts(_df: pl.DataFrame, column: str, limit: int = 20) -> pl.DataFrame:
    """Efficient value counts using DuckDB."""
    con = duckdb.connect(":memory:")
    con.register("tbl", _df.select([column]).to_pandas())
    q = f'SELECT "{column}", COUNT(*) AS count FROM tbl WHERE "{column}" IS NOT NULL GROUP BY "{column}" ORDER BY count DESC LIMIT {limit}'
    result = con.execute(q).pl()
    con.close()
    return result


def normality_test(series: pl.Series, sample_size: int = 5000) -> dict:
    """Test normality with optional sampling for large datasets."""
    arr = series.drop_nulls().to_numpy().astype(float)
    n = len(arr)
    
    if n < 8:
        return {"test": "N/A", "statistic": None, "p_value": None, "normal": None}
    
    # Sample if too large
    if n > sample_size:
        arr = np.random.choice(arr, sample_size, replace=False)
        test_name = f"Shapiro-Wilk (sample n={sample_size})"
        stat, p = scipy_stats.shapiro(arr)
    elif n <= 5000:
        test_name = "Shapiro-Wilk"
        stat, p = scipy_stats.shapiro(arr)
    else:
        test_name = "Kolmogorov-Smirnov"
        stat, p = scipy_stats.kstest(arr, "norm", args=(arr.mean(), arr.std()))
    
    return {
        "test": test_name,
        "statistic": round(float(stat), 4),
        "p_value": round(float(p), 4),
        "normal": p > 0.05
    }


def skew_kurtosis(series: pl.Series, sample_size: int = 10000) -> dict:
    """Compute skewness and kurtosis with sampling for large datasets."""
    arr = series.drop_nulls().to_numpy().astype(float)
    
    if len(arr) > sample_size:
        arr = np.random.choice(arr, sample_size, replace=False)
    
    return {
        "skewness": round(float(scipy_stats.skew(arr)), 4),
        "kurtosis": round(float(scipy_stats.kurtosis(arr)), 4),
    }


def column_profile(_df: pl.DataFrame, col: str) -> dict:
    """Deep profile of a single column (memory-efficient)."""
    s = _df[col]
    dtype = str(s.dtype)
    null_count = s.null_count()
    n = len(s)
    
    profile = {
        "dtype": dtype,
        "count": n,
        "nulls": null_count,
        "null_pct": round(null_count / n * 100, 2) if n else 0,
        "unique": s.n_unique(),
    }
    
    if s.dtype in (pl.Float32, pl.Float64, pl.Int8, pl.Int16, pl.Int32, pl.Int64,
                   pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64):
        arr = s.drop_nulls().to_numpy().astype(float)
        
        profile.update({
            "mean": round(float(np.mean(arr)), 4),
            "std": round(float(np.std(arr, ddof=1)), 4) if len(arr) > 1 else 0,
            "min": float(np.min(arr)),
            "max": float(np.max(arr)),
            "median": float(np.median(arr)),
        })
        profile.update(normality_test(s))
        profile.update(skew_kurtosis(s))
    
    return profile
