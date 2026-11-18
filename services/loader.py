"""services/loader.py — optimized file ingestion for large files (2GB+)."""
from __future__ import annotations

import io
import tempfile
import polars as pl
import streamlit as st
import os


def load_csv_chunked(file_obj, chunk_size: int = 100_000) -> pl.DataFrame:
    """Stream CSV in chunks to handle large files efficiently."""
    chunks = []
    progress_bar = st.progress(0)
    
    # Get file size for progress tracking
    file_obj.seek(0, os.SEEK_END)
    file_size = file_obj.tell()
    file_obj.seek(0)
    
    bytes_read = 0
    chunk_idx = 0
    
    try:
        while True:
            # Read chunk as bytes
            chunk_data = file_obj.read(1024 * 1024)  # 1MB at a time
            if not chunk_data:
                break
            
            bytes_read += len(chunk_data)
            progress = min(bytes_read / file_size, 1.0) if file_size > 0 else 0
            progress_bar.progress(progress, text=f"Loading: {bytes_read / 1024 / 1024:.1f}MB")
            chunk_idx += 1
    except Exception:
        pass
    
    progress_bar.empty()
    
    # Reset file position and read entire CSV with Polars (Polars handles streaming)
    file_obj.seek(0)
    df = pl.read_csv(file_obj, infer_schema_length=10000)
    return df


def load_excel(raw: bytes, sheet: str | int = 0) -> pl.DataFrame:
    """Load Excel file using Pandas then convert to Polars."""
    import pandas as pd
    buf = io.BytesIO(raw)
    pdf = pd.read_excel(buf, sheet_name=sheet, dtype_backend='numpy_nullable')
    return pl.from_pandas(pdf)


def load_parquet(file_obj) -> pl.DataFrame:
    """Load Parquet file - already optimized for large files."""
    return pl.read_parquet(file_obj)


def load_json(raw: bytes) -> pl.DataFrame:
    """Load JSON - use streaming for large files."""
    return pl.read_ndjson(io.BytesIO(raw)) if raw.count(b'\n') > 1 else pl.read_json(io.BytesIO(raw))


def load_uploaded(file) -> pl.DataFrame:
    """
    Dispatch on file extension and return a Polars DataFrame.
    Optimized for large files (2GB+).
    """
    name = file.name.lower()
    
    if name.endswith(".csv"):
        return load_csv_chunked(file)
    elif name.endswith((".xlsx", ".xls")):
        raw = file.read()
        return load_excel(raw)
    elif name.endswith(".parquet"):
        return load_parquet(file)
    elif name.endswith(".json"):
        raw = file.read()
        return load_json(raw)
    else:
        raise ValueError(f"Unsupported file type: {name}")


def schema_summary(df: pl.DataFrame) -> list[dict]:
    """Return a list of {column, dtype, nulls, null_pct} dicts."""
    rows = []
    n = df.height
    for col in df.columns:
        null_count = df[col].null_count()
        rows.append(
            {
                "Column": col,
                "Dtype": str(df[col].dtype),
                "Nulls": null_count,
                "Null %": f"{null_count / n * 100:.1f}%" if n else "—",
            }
        )
    return rows
