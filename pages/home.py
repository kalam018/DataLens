"""pages/home.py — DataLens landing/home page."""
from __future__ import annotations

import streamlit as st


def render():
    # Hero section
    st.markdown(
        """
        <div style="padding: 2.5rem 0 1rem 0;">
            <div style="font-family:Space Mono,monospace;color:#00e5a0;font-size:.75rem;letter-spacing:.12em;text-transform:uppercase;">
                DATA ANALYSIS WORKSPACE
            </div>
            <h1 style="font-size:3.4rem;line-height:1.05;margin:.5rem 0 1rem 0;">
                Turn raw data into<br><span style="color:#00e5a0;">clear insights.</span>
            </h1>
            <p style="max-width:760px;color:#a7afbd;font-size:1.05rem;line-height:1.7;">
                DataLens is an interactive data-analysis workspace for uploading,
                cleaning, exploring, visualizing and exporting datasets — all from one place.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Quick start
    st.markdown("### 🚀 Get started")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            """
            <div class="metric-card" style="min-height:155px;">
                <div style="font-size:1.8rem;">📤</div>
                <h3 style="margin:.4rem 0;">1. Upload</h3>
                <p style="color:#7a8394;font-size:.9rem;line-height:1.5;">
                    Import CSV, Excel, JSON or Parquet files and preview their structure.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
            <div class="metric-card" style="min-height:155px;border-left-color:#5b7fff;">
                <div style="font-size:1.8rem;">🧹</div>
                <h3 style="margin:.4rem 0;">2. Prepare</h3>
                <p style="color:#7a8394;font-size:.9rem;line-height:1.5;">
                    Handle missing values, duplicates, outliers, data types and columns.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            """
            <div class="metric-card" style="min-height:155px;border-left-color:#f5a623;">
                <div style="font-size:1.8rem;">📊</div>
                <h3 style="margin:.4rem 0;">3. Analyze</h3>
                <p style="color:#7a8394;font-size:.9rem;line-height:1.5;">
                    Explore statistics, charts, correlations and relationships in your data.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # Feature overview
    st.markdown("### 🧰 What you can do")
    features = [
        ("📤", "Data Upload", "Load CSV, XLSX, XLS, Parquet and JSON datasets."),
        ("🧹", "Data Cleaning", "Treat nulls, duplicates and outliers and convert data types."),
        ("📊", "Statistics", "Inspect descriptive statistics and distribution plots."),
        ("📈", "Dashboard", "Build interactive histograms, box plots, scatter, bar and line charts."),
        ("🔗", "Correlation", "Explore numerical and categorical relationships."),
        ("💾", "Export", "Download your processed dataset in common formats."),
    ]

    for start in range(0, len(features), 3):
        cols = st.columns(3)
        for col, (icon, title, description) in zip(cols, features[start:start + 3]):
            with col:
                st.markdown(
                    f"""
                    <div style="background:#161922;border:1px solid #252a35;border-radius:6px;padding:1rem 1.1rem;margin-bottom:1rem;min-height:120px;">
                        <div style="font-size:1.4rem;">{icon}</div>
                        <div style="font-weight:800;margin:.35rem 0;">{title}</div>
                        <div style="color:#7a8394;font-size:.82rem;line-height:1.5;">{description}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # About Us
    st.markdown("### 👥 About Us")

    st.markdown(
        """
        <div style="background:#161922;border:1px solid #252a35;border-radius:6px;padding:1.2rem 1.3rem;margin-bottom:1rem;">
            <div style="font-size:1.2rem;font-weight:800;margin-bottom:.5rem;">🎓 Our Academic Team</div>
            <div style="color:#a7afbd;font-size:.92rem;line-height:1.7;">
                We are students of <strong style="color:#e2e8f0;">SRM</strong>, pursuing
                <strong style="color:#e2e8f0;">M.Sc. Applied Data Science</strong>.
                DataLens is our group project developed as an interactive data-analysis workspace.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    team = [
        ("01", "M Muthu Sivasubramanian", "RA2532014010068"),
        ("02", "SL Dharsan", "RA2532014010072"),
        ("03", "S Joshwa", "RA2532014010092"),
        ("04", "K Abdul Kalam", "RA2532014010120"),
    ]

    for start in range(0, len(team), 2):
        cols = st.columns(2)
        for col, (number, name, roll_no) in zip(cols, team[start:start + 2]):
            with col:
                st.markdown(
                    f"""
                    <div style="background:#161922;border:1px solid #252a35;border-radius:6px;padding:1rem 1.1rem;margin-bottom:1rem;min-height:105px;">
                        <div style="color:#00e5a0;font-size:.7rem;font-weight:800;letter-spacing:.05em;">TEAM MEMBER {number}</div>
                        <div style="font-weight:800;margin:.4rem 0 .25rem 0;color:#f1f5f9;">{name}</div>
                        <div style="color:#7a8394;font-size:.82rem;">Roll No: {roll_no}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.markdown(
        """
        <div style="margin-top:.25rem;padding:1.1rem 1.2rem;border:1px solid #252a35;border-radius:6px;background:#161922;text-align:center;">
            <div style="font-size:1.5rem;margin-bottom:.35rem;">👨‍🏫</div>
            <div style="font-weight:800;color:#f1f5f9;">Our Respected Guide</div>
            <div style="color:#d8dee9;margin-top:.35rem;font-weight:600;">Mr. Venkata Subramanian J</div>
            <div style="color:#7a8394;font-size:.82rem;margin-top:.2rem;">Assistant Professor</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Current dataset status
    st.markdown("### 📌 Current workspace")
    if "df" in st.session_state and st.session_state.df is not None:
        df = st.session_state.df
        filename = st.session_state.get("filename", "Current dataset")
        c1, c2, c3 = st.columns(3)
        c1.metric("Dataset", filename)
        c2.metric("Rows", f"{df.height:,}")
        c3.metric("Columns", f"{df.width:,}")
        st.success("Your dataset is loaded. Use the sidebar to continue with cleaning or analysis.")
    else:
        st.info("No dataset is loaded yet. Open **Upload** from the sidebar to begin.")

    st.markdown(
        """
        <div style="margin-top:2rem;padding:1rem 1.2rem;border:1px solid #252a35;border-radius:6px;background:#161922;color:#7a8394;font-family:Space Mono,monospace;font-size:.72rem;">
            DataLens · Powered by Polars + DuckDB · Interactive analysis with Streamlit
        </div>
        """,
        unsafe_allow_html=True,
    )
