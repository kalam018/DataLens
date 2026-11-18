"""services/cleaner.py — data-cleaning operations on Polars DataFrames."""
from __future__ import annotations

import polars as pl


def drop_nulls(df: pl.DataFrame, subset: list[str] | None = None) -> pl.DataFrame:
    return df.drop_nulls(subset=subset)


def fill_nulls_mean(df: pl.DataFrame, columns: list[str]) -> pl.DataFrame:
    exprs = []
    for col in columns:
        if df[col].dtype in (pl.Float32, pl.Float64, pl.Int32, pl.Int64, pl.Int16, pl.Int8, pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64):
            mean_val = df[col].mean()
            exprs.append(pl.col(col).fill_null(mean_val))
    return df.with_columns(exprs) if exprs else df


def fill_nulls_median(df: pl.DataFrame, columns: list[str]) -> pl.DataFrame:
    exprs = []
    for col in columns:
        if df[col].dtype in (pl.Float32, pl.Float64, pl.Int32, pl.Int64, pl.Int16, pl.Int8, pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64):
            med_val = df[col].median()
            exprs.append(pl.col(col).fill_null(med_val))
    return df.with_columns(exprs) if exprs else df


def fill_nulls_constant(df: pl.DataFrame, columns: list[str], value) -> pl.DataFrame:
    exprs = [pl.col(c).fill_null(value) for c in columns]
    return df.with_columns(exprs)


def drop_duplicates(df: pl.DataFrame, subset: list[str] | None = None) -> pl.DataFrame:
    return df.unique(subset=subset, maintain_order=True)


def rename_columns(df: pl.DataFrame, mapping: dict[str, str]) -> pl.DataFrame:
    return df.rename(mapping)


def drop_columns(df: pl.DataFrame, columns: list[str]) -> pl.DataFrame:
    return df.drop(columns)


def cast_column(df: pl.DataFrame, column: str, dtype: str) -> pl.DataFrame:
    dtype_map = {
        "Int32": pl.Int32, "Int64": pl.Int64,
        "Float32": pl.Float32, "Float64": pl.Float64,
        "Utf8": pl.Utf8, "Boolean": pl.Boolean,
        "Date": pl.Date, "Datetime": pl.Datetime,
    }
    if dtype not in dtype_map:
        raise ValueError(f"Unknown dtype: {dtype}")
    return df.with_columns(pl.col(column).cast(dtype_map[dtype]))


def remove_outliers_iqr(df: pl.DataFrame, column: str, factor: float = 1.5) -> pl.DataFrame:
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1
    low, high = q1 - factor * iqr, q3 + factor * iqr
    return df.filter((pl.col(column) >= low) & (pl.col(column) <= high))


def trim_strings(df: pl.DataFrame, columns: list[str]) -> pl.DataFrame:
    exprs = [pl.col(c).str.strip_chars() for c in columns]
    return df.with_columns(exprs)
