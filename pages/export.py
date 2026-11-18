"""pages/export.py — export original data separately and download a real analysis report."""
from __future__ import annotations

import streamlit as st
import polars as pl
from services import exporter


def _saved_figures():
    return st.session_state.get("report_figures", [])


def render():
    st.markdown("## 💾 Export & Analysis Report")

    if "df" not in st.session_state or st.session_state.df is None:
        st.warning("⬅ Upload a dataset first.")
        return

    df: pl.DataFrame = st.session_state.df
    raw_df: pl.DataFrame = st.session_state.get("df_raw", df)
    fname = st.session_state.get("filename", "dataset.csv")

    st.markdown(
        f"<span style='color:#7a8394;font-family:Space Mono,monospace;font-size:.75rem'>"
        f"Source: {fname} · {raw_df.height:,} rows × {raw_df.width} cols</span>",
        unsafe_allow_html=True,
    )

    st.markdown("### 📊 DataLens Analysis Report")
    st.info(
        "The report is a separate PDF containing statistics, charts, and easy-to-understand "
        "interpretations. It does NOT replace or modify your original CSV."
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 📄 Original Dataset")
        st.caption("Downloads the uploaded dataset exactly as loaded, without report columns or interpretations.")
        original_data = st.session_state.get("original_file_bytes", exporter.to_csv(raw_df))
        st.download_button(
            "⬇ Download Original CSV",
            data=original_data,
            file_name=f"original_{fname.rsplit('.', 1)[0]}.csv",
            mime="text/csv",
            use_container_width=True,
            key="download_original_csv",
        )

    with c2:
        st.markdown("#### 📘 Analysis Report")
        st.caption("PDF with tables + embedded charts + interpretations + key findings.")
        if st.button("🧠 Generate Analysis Report", use_container_width=True, type="primary"):
            with st.spinner("Analyzing data and building PDF with charts…"):
                try:
                    pdf = exporter.analysis_report_pdf(
                        df=df,
                        filename=fname,
                        saved_figures=_saved_figures(),
                    )
                    st.session_state["analysis_report_pdf"] = pdf
                    st.success("Report created successfully. Charts are embedded in the PDF.")
                except Exception as e:
                    st.error(f"Report generation failed: {e}")

        if st.session_state.get("analysis_report_pdf"):
            st.download_button(
                "⬇ Download DataLens PDF Report",
                data=st.session_state["analysis_report_pdf"],
                file_name=f"DataLens_Analysis_Report_{fname.rsplit('.', 1)[0]}.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="download_analysis_pdf",
            )

    st.divider()
    st.markdown("### 📦 Optional Data Export")
    st.caption("These formats export the current working dataframe. Cleaning operations may change this dataframe; the original CSV above remains unchanged.")

    fmt = st.selectbox(
        "Choose data format",
        ["CSV", "Excel (.xlsx)", "Parquet", "JSON"],
        key="export_fmt",
    )
    if st.button("⬇ Export Current Working Data", use_container_width=True):
        try:
            if fmt == "CSV":
                data, fname2, mime = exporter.to_csv(df), "working_data.csv", "text/csv"
            elif fmt == "Excel (.xlsx)":
                data, fname2, mime = exporter.to_excel(df), "working_data.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            elif fmt == "Parquet":
                data, fname2, mime = exporter.to_parquet(df), "working_data.parquet", "application/octet-stream"
            else:
                data, fname2, mime = exporter.to_json(df), "working_data.json", "application/json"

            st.download_button(
                f"✅ Download {fname2}",
                data=data,
                file_name=fname2,
                mime=mime,
                key=f"working_download_{fmt}",
            )
        except Exception as e:
            st.error(f"Export failed: {e}")

    st.divider()
    with st.expander("Preview original dataset", expanded=False):
        st.dataframe(raw_df.head(50).to_pandas(), use_container_width=True)
