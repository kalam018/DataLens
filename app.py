import streamlit as st

st.set_page_config(
    page_title="DataLens — Analyzer",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ──────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap');

    :root {
        --bg:        #0d0f14;
        --surface:   #161922;
        --border:    #252a35;
        --accent:    #00e5a0;
        --accent2:   #5b7fff;
        --danger:    #ff4f5e;
        --text:      #e8ecf2;
        --muted:     #7a8394;
    }

    html, body, [data-testid="stAppViewContainer"] {
        background: var(--bg) !important;
        color: var(--text) !important;
        font-family: 'Syne', sans-serif;
    }

    [data-testid="stSidebar"] {
        background: var(--surface) !important;
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebar"] * { color: var(--text) !important; }

    h1,h2,h3,h4 { font-family: 'Syne', sans-serif; font-weight: 800; }

    .stButton > button {
        background: var(--accent) !important;
        color: #0d0f14 !important;
        border: none !important;
        font-family: 'Space Mono', monospace !important;
        font-weight: 700 !important;
        border-radius: 4px !important;
        transition: opacity .2s;
    }
    .stButton > button:hover { opacity: .85; }

    .stDataFrame, [data-testid="stTable"] {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 6px;
    }

    .metric-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-left: 3px solid var(--accent);
        border-radius: 6px;
        padding: 1rem 1.25rem;
    }
    .metric-label { font-size: .75rem; color: var(--muted); font-family: 'Space Mono', monospace; letter-spacing: .08em; text-transform: uppercase; }
    .metric-value { font-size: 1.6rem; font-weight: 800; color: var(--accent); font-family: 'Syne', sans-serif; }

    div[data-testid="stSelectbox"] label,
    div[data-testid="stMultiSelect"] label,
    div[data-testid="stSlider"] label { color: var(--muted) !important; font-size: .8rem; font-family: 'Space Mono', monospace; }

    [data-testid="stFileUploader"] {
        border: 2px dashed var(--border) !important;
        border-radius: 8px !important;
        background: var(--surface) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar nav ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔬 DataLens")
    st.markdown("<span style='font-family:Space Mono,monospace;font-size:.7rem;color:#7a8394'>POWERED BY POLARS + DUCKDB</span>", unsafe_allow_html=True)
    st.divider()

    pages = {
        "🏠  Home": "pages/home.py",
        "📤  Upload": "pages/upload.py",
        "🧹  Cleaning": "pages/cleaning.py",
        "📊  Statistics": "pages/statistics.py",
        "📈  Dashboard": "pages/dashboard.py",
        "🔗  Correlation": "pages/correlation.py",
        "💾  Export": "pages/export.py",
    }

    selection = st.radio("Navigate", list(pages.keys()), label_visibility="collapsed")
    st.divider()

    if "df" in st.session_state and st.session_state.df is not None:
        df = st.session_state.df
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Rows</div><div class='metric-value'>{df.height:,}</div></div>", unsafe_allow_html=True)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='metric-card' style='border-left-color:#5b7fff'><div class='metric-label'>Columns</div><div class='metric-value'>{df.width:,}</div></div>", unsafe_allow_html=True)
    else:
        st.info("No dataset loaded yet.")

# ── Route to page ────────────────────────────────────────────────────────────
page_map = {
    "🏠  Home":       "pages.home",
    "📤  Upload":      "pages.upload",
    "🧹  Cleaning":    "pages.cleaning",
    "📊  Statistics":  "pages.statistics",
    "📈  Dashboard":   "pages.dashboard",
    "🔗  Correlation": "pages.correlation",
    "💾  Export":      "pages.export",
}

import importlib
mod = importlib.import_module(page_map[selection])
mod.render()
