import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="LME Sales Analysis 2026",
    page_icon="🥇",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ── GLOBAL ── */
    html, body, [class*="css"] {
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
    .main { background: #080c14; }
    [data-testid="stAppViewContainer"] { background: #080c14; }
    [data-testid="stHeader"] { background: transparent; }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

    /* ── TITLE BANNER ── */
    .title-banner {
        background: linear-gradient(135deg, #0d1321 0%, #111827 40%, #0a1628 100%);
        border: 1px solid rgba(99,179,237,0.25);
        border-top: 3px solid #63b3ed;
        border-radius: 16px;
        padding: 28px 40px;
        margin-bottom: 28px;
        text-align: center;
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 40px rgba(99,179,237,0.08);
    }
    .title-banner::before {
        content: '';
        position: absolute;
        top: -60px; right: -60px;
        width: 200px; height: 200px;
        background: radial-gradient(circle, rgba(99,179,237,0.06) 0%, transparent 70%);
        border-radius: 50%;
    }
    .title-banner h1 {
        color: #f0f4f8;
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: 4px;
        margin: 0;
        text-transform: uppercase;
        background: linear-gradient(90deg, #63b3ed, #90cdf4, #63b3ed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* ── KPI CARDS ── */
    .kpi-card {
        background: linear-gradient(145deg, #0d1321, #111827);
        border: 1px solid rgba(255,255,255,0.07);
        border-left: 3px solid #63b3ed;
        border-radius: 12px;
        padding: 18px 16px;
        text-align: center;
        height: 115px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        transition: all 0.2s ease;
        box-shadow: 0 2px 20px rgba(0,0,0,0.3);
    }
    .kpi-card:hover {
        border-left-color: #90cdf4;
        box-shadow: 0 4px 30px rgba(99,179,237,0.12);
        transform: translateY(-2px);
    }
    .kpi-label {
        color: #718096;
        font-size: 0.65rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 8px;
    }
    .kpi-value {
        color: #90cdf4;
        font-size: 1.55rem;
        font-weight: 700;
        line-height: 1.1;
    }
    .kpi-sub {
        color: #4a5568;
        font-size: 0.7rem;
        margin-top: 5px;
        font-weight: 400;
    }

    /* ── SECTION HEADERS ── */
    .section-header {
        color: #90cdf4;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2.5px;
        border-bottom: 1px solid rgba(99,179,237,0.2);
        padding-bottom: 8px;
        margin: 28px 0 18px 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* ── TABS ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: #0d1321;
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 5px;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #4a5568;
        border-radius: 9px;
        font-weight: 600;
        font-size: 0.82rem;
        padding: 9px 20px;
        letter-spacing: 0.3px;
        transition: all 0.2s;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #90cdf4;
        background: rgba(99,179,237,0.06);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #1a365d, #2a4a7f) !important;
        color: #90cdf4 !important;
        box-shadow: 0 2px 12px rgba(99,179,237,0.2);
    }

    /* ── SIDEBAR ── */
    [data-testid="stSidebar"] {
        background: #060a10;
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    [data-testid="stSidebar"] .css-1d391kg { padding: 0.8rem; }

    /* ── FILTER LABELS ── */
    .filter-label {
        color: #4a5568;
        font-size: 0.62rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.8px;
        margin: 16px 0 3px 0;
    }

    /* ── SELECTBOX in sidebar ── */
    [data-testid="stSidebar"] .stSelectbox > div > div,
    [data-testid="stSidebar"] .stMultiSelect > div > div {
        background: #0d1321 !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 8px !important;
        color: #cbd5e0 !important;
        font-size: 0.85rem !important;
        transition: border-color 0.2s;
    }
    [data-testid="stSidebar"] .stSelectbox > div > div:hover,
    [data-testid="stSidebar"] .stMultiSelect > div > div:hover {
        border-color: rgba(99,179,237,0.4) !important;
    }

    /* ── SLIDER ── */
    [data-testid="stSidebar"] .stSlider [data-baseweb="slider"] {
        padding: 0 4px;
    }
    [data-testid="stSidebar"] .stSlider [data-baseweb="thumb"] {
        background: #63b3ed !important;
    }

    /* ── SIDEBAR DIVIDER ── */
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.05);
        margin: 16px 0;
    }

    /* ── FILTERS TITLE ── */
    [data-testid="stSidebar"] h2 {
        color: #4a5568 !important;
        font-size: 0.7rem !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
        font-weight: 700 !important;
    }

    /* ── DATAFRAME ── */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.05);
    }

    /* ── SEARCH INPUT ── */
    .stTextInput > div > div > input {
        background: #0d1321 !important;
        border: 1px solid rgba(99,179,237,0.2) !important;
        border-radius: 10px !important;
        color: #e2e8f0 !important;
        font-size: 0.9rem !important;
        padding: 12px 16px !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #63b3ed !important;
        box-shadow: 0 0 0 3px rgba(99,179,237,0.1) !important;
    }

    /* ── PLOTLY CHARTS background ── */
    .js-plotly-plot { border-radius: 12px; overflow: hidden; }

    /* ── MULTISELECT tags ── */
    [data-baseweb="tag"] {
        background: rgba(99,179,237,0.15) !important;
        border: 1px solid rgba(99,179,237,0.3) !important;
        color: #90cdf4 !important;
        border-radius: 6px !important;
    }

    /* ── CAPTION ── */
    .stCaption { color: #4a5568 !important; font-size: 0.75rem !important; }

    /* ── SCROLLBAR ── */
    ::-webkit-scrollbar { width: 4px; height: 4px; }
    ::-webkit-scrollbar-track { background: #0d1321; }
    ::-webkit-scrollbar-thumb { background: #2d3748; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #63b3ed; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DATA LOADING — 4 fichiers mensuels GitHub
# ─────────────────────────────────────────────
GITHUB_BASE = "https://raw.githubusercontent.com/Ouiam-Zemmouri/LME_Sales-Analysis/main/"

MONTHLY_FILES = {
    "Jan": {
        "url":   GITHUB_BASE + "COPPER%20ANALYSIS%2001.2026%20COF%20KT%20COF%20MA%202.xlsx",
        "sheet": "COPPER ANALYSIS 01.2026",
    },
    "Feb": {
        "url":   GITHUB_BASE + "COPPER%20ANALYSIS%2002.2026%20COF%20KT%20COF%20MA%201.xlsx",
        "sheet": "COPPER ANALYSIS 02.2026",
    },
    "Mar": {
        "url":   GITHUB_BASE + "COPPER%20ANALYSIS%2003.2026%20COF%20KT%20COF%20MA%201.xlsx",
        "sheet": "COPPER ANALYSIS 03.2026",
    },
    "Apr": {
        "url":   GITHUB_BASE + "COPPER%20ANALYSIS%2004.2026%20COF%20KT%20COF%20MA.xlsx",
        "sheet": "COPPER ANALYSIS 04.2026",
    },
}

def clean_df(df, month_name):
    """Clean and standardize a monthly dataframe."""
    df.columns = df.columns.str.strip()
    df = df[df["ENTITIES"].notna()].copy()
    df["Month"] = pd.to_numeric(df["Month"], errors="coerce").fillna(0).astype(int)
    # If Month column is 0 or missing, infer from file month name
    month_num = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,
                 "Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}
    if df["Month"].eq(0).all():
        df["Month"] = month_num.get(month_name, 0)
    for col in ["QTY Km","RC Needs Kg","CC Needs Kg","ES mm","AV INDEX",
                "LME SALES €/kg","BASIC LME  €/kg","TOTAL AMOUNT €",
                "UNIT PRICE €/km","ADDED VALUE €/km","REAL COPPER Kg/km",
                "COMMERCIAL COPPER Kg/km","LME Sales copper €","LME Basic sales copper €"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    for col in ["ENTITIES","FAMILY","GROUPS","Fixation","SPOOL TYPE","RM","LME PROJECTS","MATCH"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    month_map = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
                 7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
    df["Month Name"] = df["Month"].map(month_map).fillna(month_name)
    return df

@st.cache_data(ttl=3600)
def load_all_data() -> pd.DataFrame:
    frames = []
    for month_name, info in MONTHLY_FILES.items():
        try:
            try:
                df = pd.read_excel(info["url"], sheet_name=info["sheet"],
                                   header=4, engine="openpyxl")
            except Exception:
                xl = pd.ExcelFile(info["url"], engine="openpyxl")
                sheet = next((s for s in xl.sheet_names if "COPPER" in s.upper()), xl.sheet_names[0])
                df = pd.read_excel(xl, sheet_name=sheet, header=4, engine="openpyxl")
            df = clean_df(df, month_name)
            frames.append(df)
        except Exception as e:
            pass  # silently skip failed months
    if not frames:
        st.error("❌ No data could be loaded. Check GitHub file names.")
        st.stop()
    return pd.concat(frames, ignore_index=True)


# ─────────────────────────────────────────────
# SIDEBAR – File source + Filters
# ─────────────────────────────────────────────
with st.sidebar:
    # COFICAB Logo from GitHub
    st.markdown("""
    <div style="text-align:center; padding: 20px 0 12px 0;">
        <img src=https://raw.githubusercontent.com/Ouiam-Zemmouri/LME_Sales-Analysis/main/COFICAB.png
             style="max-width:155px; border-radius:10px;
                    filter: drop-shadow(0 4px 12px rgba(99,179,237,0.15));" />
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("## 🔍 Filters")

    # Load all 4 months silently from GitHub
    df_raw = load_all_data()


    def make_select(label, col, df):
        all_vals = sorted(df[col].dropna().astype(str).unique().tolist())
        st.markdown(f'<p class="filter-label">{label}</p>', unsafe_allow_html=True)
        sel = st.multiselect("", all_vals, default=[], key=f"sel_{col}",
                             placeholder="All", label_visibility="collapsed")
        return sel if sel else all_vals

    cs_col_name = "CROSS SECTION mm" if "CROSS SECTION mm" in df_raw.columns else "ES mm"

    f_entity   = make_select("Entity",           "ENTITIES",   df_raw)
    f_month    = make_select("Month",             "Month Name", df_raw)
    f_rm       = make_select("RM",                "RM",         df_raw)
    f_family   = make_select("Product Family",    "FAMILY",     df_raw)
    f_group    = make_select("Groups",            "GROUPS",     df_raw)
    f_cs       = make_select("Cross Section mm",  cs_col_name,  df_raw)
    f_fix      = make_select("Fixation",          "Fixation",   df_raw)
    f_spool    = make_select("Spool Type",        "SPOOL TYPE", df_raw)
    f_lme_proj = make_select("LME Projects",      "LME PROJECTS", df_raw)

    st.markdown('<p class="filter-label">LME Sales €/kg</p>', unsafe_allow_html=True)
    lme_min, lme_max = float(df_raw["LME SALES €/kg"].min()), float(df_raw["LME SALES €/kg"].max())
    f_lme = st.slider("", lme_min, lme_max, (lme_min, lme_max), key="lme_sl", label_visibility="collapsed")

    st.markdown('<p class="filter-label">Basic LME €/kg</p>', unsafe_allow_html=True)
    basic_min, basic_max = float(df_raw["BASIC LME  €/kg"].min()), float(df_raw["BASIC LME  €/kg"].max())
    f_basic = st.slider("", basic_min, basic_max, (basic_min, basic_max), key="basic_sl", label_visibility="collapsed")

    st.markdown("---")


# ─────────────────────────────────────────────
# APPLY FILTERS
# ─────────────────────────────────────────────
cs_col = "CROSS SECTION mm" if "CROSS SECTION mm" in df_raw.columns else "ES mm"
df = df_raw[
    df_raw["ENTITIES"].astype(str).isin(f_entity) &
    df_raw["Month Name"].astype(str).isin(f_month) &
    df_raw["RM"].astype(str).isin(f_rm) &
    df_raw["FAMILY"].astype(str).isin(f_family) &
    df_raw["GROUPS"].astype(str).isin(f_group) &
    df_raw[cs_col].astype(str).isin(f_cs) &
    df_raw["Fixation"].astype(str).isin(f_fix) &
    df_raw["SPOOL TYPE"].astype(str).isin(f_spool) &
    df_raw["LME PROJECTS"].astype(str).isin(f_lme_proj) &
    df_raw["LME SALES €/kg"].between(f_lme[0], f_lme[1]) &
    df_raw["BASIC LME  €/kg"].between(f_basic[0], f_basic[1])
].copy()

# ─────────────────────────────────────────────
# KPI CALCULATIONS
# ─────────────────────────────────────────────
total_qty_km     = df["QTY Km"].sum()
total_ca         = df["TOTAL AMOUNT €"].sum()
total_rc_kg      = df["RC Needs Kg"].sum()
total_cc_kg      = df["CC Needs Kg"].sum() if "CC Needs Kg" in df.columns else 0
total_es         = df["ES mm"].sum()
total_av         = df["AV INDEX"].sum()

avg_ca_km        = df["UNIT PRICE €/km"].mean() if "UNIT PRICE €/km" in df.columns else 0
avg_es           = total_es / total_qty_km if total_qty_km else 0
avg_cs           = total_es / total_qty_km if total_qty_km else 0   # cross section avg
avg_rc_kg_km     = total_rc_kg / total_qty_km if total_qty_km else 0
avg_cc_kg_km     = total_cc_kg / total_qty_km if total_qty_km else 0
avg_lme          = df["LME SALES €/kg"].mean()
avg_basic_lme    = df["BASIC LME  €/kg"].mean()
avg_av_km        = total_av / total_qty_km if total_qty_km else 0
total_tonnage_t  = total_rc_kg / 1000

# Fixation breakdown
fix_data = (
    df.groupby("Fixation")
      .agg(Tonnage_T=("RC Needs Kg", lambda x: x.sum() / 1000),
           Qty_Km=("QTY Km", "sum"),
           CA=("TOTAL AMOUNT €", "sum"))
      .reset_index()
)

# ─────────────────────────────────────────────
# TITLE BANNER
# ─────────────────────────────────────────────
st.markdown("""
<div class="title-banner">
  <h1>SALES ANALYSIS 2026</h1>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# NAVIGATION TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 KPI Summary",
    "📈 LME Overview",
    "🏭 Fixation Analysis",
    "🔬 Deep Dive",
    "📋 Raw Data"
])

COLORS = {
    "primary":  "#63b3ed",   # steel blue
    "accent":   "#90cdf4",   # light blue
    "red":      "#fc8181",   # soft coral
    "blue":     "#63b3ed",   # steel blue
    "green":    "#68d391",   # mint green
    "gold":     "#f6ad55",   # amber
    "purple":   "#b794f4",   # lavender
    "teal":     "#4fd1c5",   # teal
    "bg":       "#080c14",   # deep navy bg
    "card":     "#0d1321",   # card bg
    "border":   "rgba(99,179,237,0.15)",
}
CHART_LAYOUT = dict(
    paper_bgcolor="#080c14",
    plot_bgcolor="#0a0f1a",
    font=dict(color="#718096", family="Inter, Segoe UI", size=12),
    margin=dict(t=55, b=45, l=55, r=25),
    legend=dict(
        bgcolor="rgba(13,19,33,0.9)",
        bordercolor="rgba(99,179,237,0.15)",
        borderwidth=1,
        font=dict(color="#a0aec0", size=11),
    ),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.04)",
        zeroline=False,
        tickfont=dict(color="#4a5568", size=11),
        linecolor="rgba(255,255,255,0.06)",
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.04)",
        zeroline=False,
        tickfont=dict(color="#4a5568", size=11),
        linecolor="rgba(255,255,255,0.06)",
    ),
    title_font=dict(color="#90cdf4", size=13, family="Inter"),
    hoverlabel=dict(
        bgcolor="#0d1321",
        bordercolor="rgba(99,179,237,0.3)",
        font=dict(color="#e2e8f0", size=12),
    ),
)


# ═══════════════════════════════════════════════════════════
# TAB 1 – KPI SUMMARY (now first tab)
# ═══════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-header">📊 Global KPIs</div>', unsafe_allow_html=True)

    k1, k2, k3, k4, k5 = st.columns(5)
    kpis_row1 = [
        ("CA Total (€)", f"€{total_ca/1e6:.2f}M", "Chiffre d'Affaires"),
        ("Qty Total (km)", f"{total_qty_km:,.0f}", "km vendus"),
        ("Tonnage RC (T)", f"{total_tonnage_t:,.1f}", "Real Copper"),
        ("Avg LME All-In", f"{avg_lme:.4f} €/kg", "LME moyen"),
        ("Avg Basic LME €/kg", f"{avg_basic_lme:.4f}", "LME basic moyen"),
    ]
    for col, (label, val, sub) in zip([k1,k2,k3,k4,k5], kpis_row1):
        col.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-label">{label}</div>
          <div class="kpi-value">{val}</div>
          <div class="kpi-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    k6, k7, k8, k9, k10 = st.columns(5)
    kpis_row2 = [
        ("Avg ES mm",    f"{avg_es:.3f}",          "Sous-total ES mm / km"),
        ("Avg RC Kg/km", f"{avg_rc_kg_km:.3f}",    "Real Copper Kg/km"),
        ("Avg CC Kg/km", f"{avg_cc_kg_km:.3f}",    "Commercial Copper Kg/km"),
        ("Avg AV €/km",  f"€{avg_av_km:.2f}",      "Added Value / km"),
    ]
    for col, (label, val, sub) in zip([k6,k7,k8,k9,k10], kpis_row2):
        col.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-label">{label}</div>
          <div class="kpi-value">{val}</div>
          <div class="kpi-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    k11, k12, k13, k14 = st.columns(4)
    kpis_row3 = [
        ("Avg Basic LME €/kg", f"{avg_basic_lme:.4f}", "LME basic moyen"),
    ]
    for col, (label, val, sub) in zip([k11,k12,k13,k14], kpis_row3):
        col.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-label">{label}</div>
          <div class="kpi-value">{val}</div>
          <div class="kpi-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns(2)
    with col_left:
        ent_data = (df.groupby("ENTITIES")
                      .agg(CA=("TOTAL AMOUNT €","sum"), Qty_Km=("QTY Km","sum"))
                      .reset_index())
        fig_ent = px.bar(ent_data, x="ENTITIES", y="CA", color="ENTITIES",
                         text_auto=".2s", title="Chiffre d'Affaires par Entité (€)",
                         color_discrete_sequence=[COLORS["primary"], COLORS["gold"]])
        fig_ent.update_layout(**CHART_LAYOUT)
        st.plotly_chart(fig_ent, use_container_width=True)

    with col_right:
        fig_qty = px.bar(ent_data, x="ENTITIES", y="Qty_Km", color="ENTITIES",
                         text_auto=".2s", title="Quantité par Entité (km)",
                         color_discrete_sequence=[COLORS["teal"], COLORS["purple"]])
        fig_qty.update_layout(**CHART_LAYOUT)
        st.plotly_chart(fig_qty, use_container_width=True)

    st.markdown('<div class="section-header">📐 ES mm & Cross Section Summary</div>',
                unsafe_allow_html=True)
    es_entity = (
        df.groupby("ENTITIES")
          .agg(
              **{"Total ES mm":      ("ES mm", "sum"),
                 "Total Qty km":     ("QTY Km", "sum"),
                 "Avg Cross Section":("ES mm", lambda x: x.sum() / df.loc[x.index, "QTY Km"].sum()),
                 "Avg RC Kg/km":     ("RC Needs Kg", lambda x: x.sum() / df.loc[x.index, "QTY Km"].sum()),
                 "Avg CC Kg/km":     ("CC Needs Kg", lambda x: x.sum() / df.loc[x.index, "QTY Km"].sum()),
                 "Avg AV €/km":      ("AV INDEX", lambda x: x.sum() / df.loc[x.index, "QTY Km"].sum()),
              }
          )
          .reset_index()
    )
    st.dataframe(
        es_entity.style
            .format({"Total ES mm": "{:,.3f}", "Total Qty km": "{:,.2f}",
                     "Avg Cross Section": "{:.3f}", "Avg RC Kg/km": "{:.3f}",
                     "Avg CC Kg/km": "{:.3f}", "Avg AV €/km": "€{:.2f}"})
            .set_properties(**{"background-color": "#0d1321", "color": "#a0aec0"}),
        use_container_width=True, hide_index=True
    )


# ═══════════════════════════════════════════════════════════
# TAB 2 – LME OVERVIEW (detailed multi-month)
# ═══════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-header">📈 LME Sales Evolution — Monthly Detail</div>',
                unsafe_allow_html=True)

    # Month order for proper x-axis sorting
    month_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

    # Aggregate per month per entity
    monthly = (
        df.groupby(["Month","Month Name","ENTITIES"])
          .agg(
              LME_Sales=("LME SALES €/kg", "mean"),
              LME_Min=("LME SALES €/kg", "min"),
              LME_Max=("LME SALES €/kg", "max"),
              Basic_LME=("BASIC LME  €/kg", "mean"),
              Basic_Min=("BASIC LME  €/kg", "min"),
              Basic_Max=("BASIC LME  €/kg", "max"),
              Qty_Km=("QTY Km", "sum"),
              CA=("TOTAL AMOUNT €", "sum"),
          )
          .reset_index()
    )
    monthly["Month Name"] = pd.Categorical(monthly["Month Name"], categories=month_order, ordered=True)
    monthly = monthly.sort_values(["Month Name","ENTITIES"])

    # ── Chart 1: All-In with min/max band per entity
    col_g1, col_g2 = st.columns(2)

    # Fixed rgba fill colors per entity
    band_fills_allin  = {"COFICAB Kenitra": "rgba(99,179,237,0.10)",  "COFICAB Maroc": "rgba(246,173,85,0.10)"}
    band_fills_basic  = {"COFICAB Kenitra": "rgba(79,209,197,0.10)",  "COFICAB Maroc": "rgba(183,148,244,0.10)"}
    ent_colors        = {"COFICAB Kenitra": COLORS["primary"],         "COFICAB Maroc": COLORS["gold"]}
    ent_colors2       = {"COFICAB Kenitra": COLORS["teal"],            "COFICAB Maroc": COLORS["purple"]}

    with col_g1:
        st.markdown("##### All-In LME Sales (€/kg) — Avg · Min · Max per Month")
        fig1 = go.Figure()
        for ent, grp in monthly.groupby("ENTITIES"):
            c    = ent_colors.get(ent, COLORS["primary"])
            fill = band_fills_allin.get(ent, "rgba(99,179,237,0.10)")
            # Shaded band min-max
            fig1.add_trace(go.Scatter(
                x=list(grp["Month Name"]) + list(grp["Month Name"])[::-1],
                y=list(grp["LME_Max"]) + list(grp["LME_Min"])[::-1],
                fill="toself", fillcolor=fill,
                line=dict(color="rgba(0,0,0,0)"),
                showlegend=False, hoverinfo="skip",
            ))
            # Avg line
            fig1.add_trace(go.Scatter(
                x=grp["Month Name"], y=grp["LME_Sales"],
                mode="lines+markers+text",
                name=ent,
                line=dict(color=c, width=2.5),
                marker=dict(size=9, symbol="circle", line=dict(width=2, color=c)),
                text=[f"{v:.4f}" for v in grp["LME_Sales"]],
                textposition="top center",
                textfont=dict(size=9, color=c),
                hovertemplate=(
                    f"<b>{ent}</b><br>"
                    "Month: %{x}<br>"
                    "Avg: %{y:.4f} €/kg<br>"
                    "<extra></extra>"
                ),
            ))
        fig1.update_layout(**CHART_LAYOUT, title="LME All-In €/kg — Evolution with Value Labels")
        st.plotly_chart(fig1, use_container_width=True)

    with col_g2:
        st.markdown("##### Basic LME (€/kg) — Avg · Min · Max per Month")
        fig2 = go.Figure()
        for ent, grp in monthly.groupby("ENTITIES"):
            c    = ent_colors2.get(ent, COLORS["teal"])
            fill = band_fills_basic.get(ent, "rgba(79,209,197,0.10)")
            fig2.add_trace(go.Scatter(
                x=list(grp["Month Name"]) + list(grp["Month Name"])[::-1],
                y=list(grp["Basic_Max"]) + list(grp["Basic_Min"])[::-1],
                fill="toself", fillcolor=fill,
                line=dict(color="rgba(0,0,0,0)"),
                showlegend=False, hoverinfo="skip",
            ))
            fig2.add_trace(go.Scatter(
                x=grp["Month Name"], y=grp["Basic_LME"],
                mode="lines+markers+text",
                name=ent,
                line=dict(color=c, width=2.5),
                marker=dict(size=9, symbol="diamond", line=dict(width=2, color=c)),
                text=[f"{v:.4f}" for v in grp["Basic_LME"]],
                textposition="top center",
                textfont=dict(size=9, color=c),
                hovertemplate=(
                    f"<b>{ent}</b><br>"
                    "Month: %{x}<br>"
                    "Basic LME: %{y:.4f} €/kg<br>"
                    "<extra></extra>"
                ),
            ))
        fig2.update_layout(**CHART_LAYOUT, title="Basic LME €/kg — Evolution with Value Labels")
        st.plotly_chart(fig2, use_container_width=True)

    # ── Chart 2: All-In vs Basic combined overview
    st.markdown('<div class="section-header">📊 All-In vs Basic — Combined Monthly View</div>',
                unsafe_allow_html=True)
    monthly_all = (
        df.groupby(["Month","Month Name"])
          .agg(LME_Sales=("LME SALES €/kg","mean"), Basic_LME=("BASIC LME  €/kg","mean"),
               LME_Std=("LME SALES €/kg","std"), Basic_Std=("BASIC LME  €/kg","std"))
          .reset_index()
    )
    monthly_all["Month Name"] = pd.Categorical(monthly_all["Month Name"], categories=month_order, ordered=True)
    monthly_all = monthly_all.sort_values("Month Name")

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=monthly_all["Month Name"], y=monthly_all["LME_Sales"],
        name="LME All-In €/kg", mode="lines+markers+text",
        line=dict(color=COLORS["primary"], width=3),
        marker=dict(size=11, symbol="circle", line=dict(width=2, color=COLORS["primary"])),
        text=[f"<b>{v:.4f}</b>" for v in monthly_all["LME_Sales"]],
        textposition="top center", textfont=dict(size=10, color=COLORS["primary"]),
        fill="tozeroy", fillcolor="rgba(99,179,237,0.05)",
    ))
    fig3.add_trace(go.Scatter(
        x=monthly_all["Month Name"], y=monthly_all["Basic_LME"],
        name="Basic LME €/kg", mode="lines+markers+text",
        line=dict(color=COLORS["gold"], width=3, dash="dot"),
        marker=dict(size=11, symbol="diamond", line=dict(width=2, color=COLORS["gold"])),
        text=[f"<b>{v:.4f}</b>" for v in monthly_all["Basic_LME"]],
        textposition="bottom center", textfont=dict(size=10, color=COLORS["gold"]),
        fill="tozeroy", fillcolor="rgba(246,173,85,0.05)",
    ))
    fig3.update_layout(**CHART_LAYOUT,
                       title="LME All-In vs Basic LME — Monthly Comparison (All Entities Combined)")
    st.plotly_chart(fig3, use_container_width=True)

    # ── Chart 3: LME by Fixation over months
    st.markdown('<div class="section-header">🔧 LME Evolution by Fixation</div>',
                unsafe_allow_html=True)
    by_fix_month = (
        df.groupby(["Month","Month Name","Fixation"])
          .agg(LME_Sales=("LME SALES €/kg","mean"), Basic_LME=("BASIC LME  €/kg","mean"),
               Qty_Km=("QTY Km","sum"))
          .reset_index()
    )
    by_fix_month["Month Name"] = pd.Categorical(by_fix_month["Month Name"],
                                                 categories=month_order, ordered=True)
    by_fix_month = by_fix_month.sort_values("Month Name")

    fix_colors = {"M-1": COLORS["primary"], "3M-1": COLORS["gold"], "3M-2": COLORS["teal"]}
    col_fx1, col_fx2 = st.columns(2)
    with col_fx1:
        fig_fx = go.Figure()
        for fix, grp in by_fix_month.groupby("Fixation"):
            c = fix_colors.get(fix, COLORS["purple"])
            fig_fx.add_trace(go.Scatter(
                x=grp["Month Name"], y=grp["LME_Sales"],
                mode="lines+markers+text", name=fix,
                line=dict(color=c, width=2.5),
                marker=dict(size=9),
                text=[f"{v:.4f}" for v in grp["LME_Sales"]],
                textposition="top center", textfont=dict(size=8, color=c),
            ))
        fig_fx.update_layout(**CHART_LAYOUT, title="LME All-In €/kg by Fixation")
        st.plotly_chart(fig_fx, use_container_width=True)

    with col_fx2:
        fig_fx2 = go.Figure()
        for fix, grp in by_fix_month.groupby("Fixation"):
            c = fix_colors.get(fix, COLORS["purple"])
            fig_fx2.add_trace(go.Bar(
                x=grp["Month Name"], y=grp["Qty_Km"],
                name=fix, marker_color=c, opacity=0.85,
                text=[f"{v/1000:.1f}K" for v in grp["Qty_Km"]],
                textposition="auto",
            ))
        fig_fx2.update_layout(**CHART_LAYOUT, barmode="group",
                               title="Qty (km) by Fixation per Month")
        st.plotly_chart(fig_fx2, use_container_width=True)

    # ── LME by Group bar
    st.markdown('<div class="section-header">📦 LME Performance by Customer Group</div>',
                unsafe_allow_html=True)
    grp_data = (
        df.groupby("GROUPS")
          .agg(LME_Sales=("LME SALES €/kg","mean"),
               Basic_LME=("BASIC LME  €/kg","mean"),
               Qty_Km=("QTY Km","sum"),
               CA=("TOTAL AMOUNT €","sum"))
          .reset_index()
          .sort_values("CA", ascending=False)
    )
    fig_grp = go.Figure()
    fig_grp.add_trace(go.Bar(
        x=grp_data["GROUPS"], y=grp_data["LME_Sales"],
        name="LME All-In €/kg", marker_color=COLORS["primary"], opacity=0.9,
        text=[f"{v:.4f}" for v in grp_data["LME_Sales"]], textposition="auto",
    ))
    fig_grp.add_trace(go.Bar(
        x=grp_data["GROUPS"], y=grp_data["Basic_LME"],
        name="Basic LME €/kg", marker_color=COLORS["gold"], opacity=0.9,
        text=[f"{v:.4f}" for v in grp_data["Basic_LME"]], textposition="auto",
    ))
    fig_grp.update_layout(**CHART_LAYOUT, barmode="group",
                          title="Average LME Prices by Customer Group")
    st.plotly_chart(fig_grp, use_container_width=True)


# ═══════════════════════════════════════════════════════════
# TAB 3 – FIXATION ANALYSIS
# ═══════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header">🔧 Fixation Breakdown (M-1 · 3M-1 · 3M-2)</div>',
                unsafe_allow_html=True)

    # KPI row for fixation
    fix_cols = st.columns(len(fix_data) + 1)
    for i, row in fix_data.iterrows():
        pct = row["Qty_Km"] / total_qty_km * 100 if total_qty_km else 0
        fix_cols[i].markdown(f"""
        <div class="kpi-card">
          <div class="kpi-label">{row['Fixation']}</div>
          <div class="kpi-value">{row['Tonnage_T']:,.1f} T</div>
          <div class="kpi-sub">{row['Qty_Km']:,.0f} km · {pct:.1f}%</div>
        </div>""", unsafe_allow_html=True)
    # Total card
    fix_cols[-1].markdown(f"""
    <div class="kpi-card" style="border-left-color:#90cdf4; box-shadow:0 4px 30px rgba(99,179,237,0.18);">
      <div class="kpi-label">⚡ TOTAL</div>
      <div class="kpi-value">{total_tonnage_t:,.1f} T</div>
      <div class="kpi-sub">{total_qty_km:,.0f} km · 100%</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    colA, colB, colC = st.columns(3)

    with colA:
        # Donut – Tonnage by Fixation
        fig_donut = px.pie(
            fix_data, values="Tonnage_T", names="Fixation",
            hole=0.55, title="Tonnage (T) by Fixation",
            color_discrete_sequence=[COLORS["red"], COLORS["blue"], COLORS["gold"]],
        )
        fig_donut.update_traces(textposition="outside", textinfo="label+percent")
        fig_donut.update_layout(**CHART_LAYOUT)
        st.plotly_chart(fig_donut, use_container_width=True)

    with colB:
        # Donut – Qty km by Fixation
        fig_donut2 = px.pie(
            fix_data, values="Qty_Km", names="Fixation",
            hole=0.55, title="Quantity (km) by Fixation",
            color_discrete_sequence=[COLORS["teal"], COLORS["purple"], COLORS["green"]],
        )
        fig_donut2.update_traces(textposition="outside", textinfo="label+percent")
        fig_donut2.update_layout(**CHART_LAYOUT)
        st.plotly_chart(fig_donut2, use_container_width=True)

    with colC:
        # Donut – CA by Fixation
        fig_donut3 = px.pie(
            fix_data, values="CA", names="Fixation",
            hole=0.55, title="CA (€) by Fixation",
            color_discrete_sequence=[COLORS["gold"], COLORS["red"], COLORS["blue"]],
        )
        fig_donut3.update_traces(textposition="outside", textinfo="label+percent")
        fig_donut3.update_layout(**CHART_LAYOUT)
        st.plotly_chart(fig_donut3, use_container_width=True)

    # Fixation by Entity
    fix_entity = (
        df.groupby(["Fixation","ENTITIES"])
          .agg(Tonnage_T=("RC Needs Kg", lambda x: x.sum()/1000),
               Qty_Km=("QTY Km","sum"),
               CA=("TOTAL AMOUNT €","sum"))
          .reset_index()
    )
    fig_fix_ent = px.bar(
        fix_entity, x="Fixation", y="Tonnage_T",
        color="ENTITIES", barmode="group",
        text_auto=".1f",
        title="Tonnage (T) by Fixation & Entity",
        color_discrete_sequence=[COLORS["red"], COLORS["blue"]],
        labels={"Tonnage_T": "Tonnage (T)"},
    )
    fig_fix_ent.update_layout(**CHART_LAYOUT)
    st.plotly_chart(fig_fix_ent, use_container_width=True)

    # Summary table
    st.markdown('<div class="section-header">📋 Fixation Detail Table</div>', unsafe_allow_html=True)
    fix_summary = (
        df.groupby("Fixation")
          .agg(
              **{"Tonnage (T)":    ("RC Needs Kg", lambda x: round(x.sum()/1000, 2)),
                 "Qty (km)":       ("QTY Km", lambda x: round(x.sum(), 2)),
                 "CA €":           ("TOTAL AMOUNT €", lambda x: round(x.sum(), 2)),
                 "Avg LME All-In": ("LME SALES €/kg", lambda x: round(x.mean(), 4)),
                 "Avg Basic LME":  ("BASIC LME  €/kg", lambda x: round(x.mean(), 4)),
              }
          )
          .reset_index()
    )
    # Add total row
    total_row = pd.DataFrame([{
        "Fixation": "TOTAL",
        "Tonnage (T)": round(total_tonnage_t, 2),
        "Qty (km)": round(total_qty_km, 2),
        "CA €": round(total_ca, 2),
        "Avg LME All-In": round(avg_lme, 4),
        "Avg Basic LME": round(avg_basic_lme, 4),
    }])
    fix_summary = pd.concat([fix_summary, total_row], ignore_index=True)
    st.dataframe(
        fix_summary.style
            .format({"Tonnage (T)": "{:,.2f}", "Qty (km)": "{:,.2f}",
                     "CA €": "€{:,.2f}", "Avg LME All-In": "{:.4f}",
                     "Avg Basic LME": "{:.4f}"})
            .highlight_max(subset=["Tonnage (T)","Qty (km)","CA €"], color="#e74c3c33")
            .set_properties(**{"background-color": "#1a1f2e", "color": "#aab4c8"}),
        use_container_width=True, hide_index=True
    )


# ═══════════════════════════════════════════════════════════
# TAB 3 – KPI SUMMARY (REMOVED - now tab1)
# ═══════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════
# TAB 4 – DEEP DIVE
# ═══════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header">🔬 Deep Dive Analysis</div>', unsafe_allow_html=True)

    # By Family
    fam_data = (
        df.groupby("FAMILY")
          .agg(
              CA=("TOTAL AMOUNT €","sum"),
              Qty_Km=("QTY Km","sum"),
              Tonnage_T=("RC Needs Kg", lambda x: x.sum()/1000),
              Avg_LME=("LME SALES €/kg","mean"),
          )
          .reset_index()
          .sort_values("CA", ascending=False)
          .head(15)
    )
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        fig_fam = px.bar(
            fam_data, x="FAMILY", y="CA",
            title="CA (€) by Family — Top 15",
            color="CA", color_continuous_scale=["#0a0f1a","#63b3ed"],
            text_auto=".2s",
        )
        fig_fam.update_layout(**CHART_LAYOUT, coloraxis_showscale=False,
                               xaxis_tickangle=-45)
        st.plotly_chart(fig_fam, use_container_width=True)
    with col_f2:
        fig_fam2 = px.bar(
            fam_data, x="FAMILY", y="Tonnage_T",
            title="Tonnage (T) by Family — Top 15",
            color="Tonnage_T", color_continuous_scale=["#0a0f1a","#4fd1c5"],
            text_auto=".1f",
        )
        fig_fam2.update_layout(**CHART_LAYOUT, coloraxis_showscale=False,
                                xaxis_tickangle=-45)
        st.plotly_chart(fig_fam2, use_container_width=True)

    # RM breakdown
    st.markdown('<div class="section-header">🧱 Raw Material (RM) Breakdown</div>',
                unsafe_allow_html=True)
    rm_data = (
        df.groupby("RM")
          .agg(Qty_Km=("QTY Km","sum"), CA=("TOTAL AMOUNT €","sum"),
               Tonnage_T=("RC Needs Kg", lambda x: x.sum()/1000))
          .reset_index()
    )
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        fig_rm = px.pie(rm_data, values="Qty_Km", names="RM",
                        hole=0.5, title="Qty (km) by RM",
                        color_discrete_sequence=[COLORS["red"],COLORS["blue"],
                                                 COLORS["gold"],COLORS["teal"]])
        fig_rm.update_layout(**CHART_LAYOUT)
        st.plotly_chart(fig_rm, use_container_width=True)
    with col_r2:
        fig_rm2 = px.pie(rm_data, values="Tonnage_T", names="RM",
                         hole=0.5, title="Tonnage (T) by RM",
                         color_discrete_sequence=[COLORS["purple"],COLORS["green"],
                                                  COLORS["red"],COLORS["blue"]])
        fig_rm2.update_layout(**CHART_LAYOUT)
        st.plotly_chart(fig_rm2, use_container_width=True)

    # Spool type
    st.markdown('<div class="section-header">🪝 Spool Type Analysis</div>',
                unsafe_allow_html=True)
    spool_data = (
        df.groupby(["SPOOL TYPE","ENTITIES"])
          .agg(Qty_Km=("QTY Km","sum"), CA=("TOTAL AMOUNT €","sum"))
          .reset_index()
    )
    fig_spool = px.bar(
        spool_data, x="SPOOL TYPE", y="Qty_Km", color="ENTITIES",
        barmode="group", text_auto=".2s",
        title="Quantity (km) by Spool Type & Entity",
        color_discrete_sequence=[COLORS["red"], COLORS["blue"]],
    )
    fig_spool.update_layout(**CHART_LAYOUT)
    st.plotly_chart(fig_spool, use_container_width=True)

# ═══════════════════════════════════════════════════════════
# TAB 5 – RAW DATA
# ═══════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-header">📋 Filtered Dataset</div>', unsafe_allow_html=True)

    # Search bar
    search_query = st.text_input(
        "",
        placeholder="🔍  Search across all columns",
        label_visibility="collapsed"
    )

    # Column selector
    all_cols = list(df.columns)
    default_cols = ["ENTITIES","Month Name","GROUPS","FAMILY","Fixation","QTY Km",
                    "RC Needs Kg","CC Needs Kg","LME SALES €/kg","BASIC LME  €/kg",
                    "TOTAL AMOUNT €","UNIT PRICE €/km","ES mm","AV INDEX","SPOOL TYPE","RM"]
    sel_cols = st.multiselect("Select columns to display", all_cols,
                               default=[c for c in default_cols if c in all_cols])

    # Apply search
    display_df = df[sel_cols].reset_index(drop=True) if sel_cols else df.reset_index(drop=True)
    if search_query:
        mask = display_df.apply(
            lambda col: col.astype(str).str.contains(search_query, case=False, na=False)
        ).any(axis=1)
        display_df = display_df[mask]

    # Result count
    st.caption(f"**{len(display_df):,}** rows displayed")

    st.dataframe(display_df, use_container_width=True, height=500)

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; color:#444; font-size:0.75rem; margin-top:40px; padding:16px;
            border-top:1px solid #2d3561;">
  LME Sales Analysis 2026 · COFICAB Kenitra & COFICAB Maroc
</div>
""", unsafe_allow_html=True)

