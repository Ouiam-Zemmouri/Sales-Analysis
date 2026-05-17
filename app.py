import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import io
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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
    html, body, [class*="css"] { font-family: 'Inter', 'Segoe UI', sans-serif; }
    .main { background: #080c14; }
    [data-testid="stAppViewContainer"] { background: #080c14; }
    [data-testid="stHeader"] { background: transparent; }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    .title-banner {
        background: linear-gradient(135deg, #0d1321 0%, #111827 40%, #0a1628 100%);
        border: 1px solid rgba(99,179,237,0.25);
        border-top: 3px solid #63b3ed;
        border-radius: 16px;
        padding: 28px 40px;
        margin-bottom: 28px;
        text-align: center;
        box-shadow: 0 4px 40px rgba(99,179,237,0.08);
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
        box-shadow: 0 2px 20px rgba(0,0,0,0.3);
    }
    .kpi-label { color: #718096; font-size: 0.65rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 8px; }
    .kpi-value { color: #90cdf4; font-size: 1.55rem; font-weight: 700; line-height: 1.1; }
    .kpi-sub { color: #4a5568; font-size: 0.7rem; margin-top: 5px; }
    .section-header {
        color: #90cdf4; font-size: 0.78rem; font-weight: 700;
        text-transform: uppercase; letter-spacing: 2.5px;
        border-bottom: 1px solid rgba(99,179,237,0.2);
        padding-bottom: 8px; margin: 28px 0 18px 0;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 4px; background: #0d1321; border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 5px; }
    .stTabs [data-baseweb="tab"] { background: transparent; color: #4a5568; border-radius: 9px; font-weight: 600; font-size: 0.82rem; padding: 9px 20px; }
    .stTabs [aria-selected="true"] { background: linear-gradient(135deg, #1a365d, #2a4a7f) !important; color: #90cdf4 !important; }
    [data-testid="stSidebar"] { background: #060a10; border-right: 1px solid rgba(255,255,255,0.05); }
    .filter-label { color: #4a5568; font-size: 0.62rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.8px; margin: 16px 0 3px 0; }
    [data-baseweb="tag"] { background: rgba(99,179,237,0.15) !important; border: 1px solid rgba(99,179,237,0.3) !important; color: #90cdf4 !important; border-radius: 6px !important; }
    ::-webkit-scrollbar { width: 4px; height: 4px; }
    ::-webkit-scrollbar-track { background: #0d1321; }
    ::-webkit-scrollbar-thumb { background: #2d3748; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONSTANTS
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

COLORS = {
    "primary": "#63b3ed", "accent": "#90cdf4", "red": "#fc8181",
    "blue": "#63b3ed", "green": "#68d391", "gold": "#f6ad55",
    "purple": "#b794f4", "teal": "#4fd1c5", "bg": "#080c14", "card": "#0d1321",
}

CHART_LAYOUT = dict(
    paper_bgcolor="#080c14", plot_bgcolor="#0a0f1a",
    font=dict(color="#718096", family="Inter, Segoe UI", size=12),
    margin=dict(t=55, b=45, l=55, r=25),
    legend=dict(bgcolor="rgba(13,19,33,0.9)", bordercolor="rgba(99,179,237,0.15)", borderwidth=1, font=dict(color="#a0aec0", size=11)),
    xaxis=dict(gridcolor="rgba(255,255,255,0.04)", zeroline=False, tickfont=dict(color="#4a5568", size=11)),
    yaxis=dict(gridcolor="rgba(255,255,255,0.04)", zeroline=False, tickfont=dict(color="#4a5568", size=11)),
    title_font=dict(color="#90cdf4", size=13, family="Inter"),
    hoverlabel=dict(bgcolor="#0d1321", bordercolor="rgba(99,179,237,0.3)", font=dict(color="#e2e8f0", size=12)),
)

# ─────────────────────────────────────────────
# OPTIMIZED DATA LOADING
# ─────────────────────────────────────────────

def make_session():
    """HTTP session with retry logic and timeout."""
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    return session


def download_file(url: str, session: requests.Session) -> bytes | None:
    """Download file bytes with timeout. Returns None on failure."""
    try:
        resp = session.get(url, timeout=30)
        resp.raise_for_status()
        return resp.content
    except Exception as e:
        return None


def clean_df(df: pd.DataFrame, month_name: str) -> pd.DataFrame:
    """Standardize column types and add Month Name."""
    df.columns = df.columns.str.strip()
    df = df[df["ENTITIES"].notna()].copy()

    month_num = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,
                 "Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}
    df["Month"] = pd.to_numeric(df.get("Month", pd.Series(dtype=float)), errors="coerce").fillna(0).astype(int)
    if df["Month"].eq(0).all():
        df["Month"] = month_num.get(month_name, 0)

    numeric_cols = [
        "QTY Km","RC Needs Kg","CC Needs Kg","ES mm","AV INDEX",
        "LME SALES €/kg","BASIC LME  €/kg","TOTAL AMOUNT €",
        "UNIT PRICE €/km","ADDED VALUE €/km","REAL COPPER Kg/km",
        "COMMERCIAL COPPER Kg/km","LME Sales copper €","LME Basic sales copper €"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    str_cols = ["ENTITIES","FAMILY","GROUPS","Fixation","SPOOL TYPE","RM","LME PROJECTS","MATCH"]
    for col in str_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    month_map = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
                 7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
    df["Month Name"] = df["Month"].map(month_map).fillna(month_name)
    return df


# KEY FIX: cache by URL hash so re-runs don't re-download
@st.cache_data(ttl=7200, show_spinner=False)
def download_and_parse(url: str, sheet: str, month_name: str) -> pd.DataFrame | None:
    """Download + parse ONE monthly Excel file. Cached independently per file."""
    session = make_session()
    content = download_file(url, session)
    if content is None:
        return None
    try:
        bio = io.BytesIO(content)
        try:
            df = pd.read_excel(bio, sheet_name=sheet, header=4, engine="openpyxl")
        except Exception:
            bio.seek(0)
            xl = pd.ExcelFile(bio, engine="openpyxl")
            sheet_name = next((s for s in xl.sheet_names if "COPPER" in s.upper()), xl.sheet_names[0])
            df = pd.read_excel(xl, sheet_name=sheet_name, header=4, engine="openpyxl")
        return clean_df(df, month_name)
    except Exception:
        return None


def load_all_data() -> pd.DataFrame:
    """Load all months with per-file progress. Each file is cached separately."""
    frames = []
    errors = []

    progress = st.sidebar.progress(0, text="Chargement des données…")
    total = len(MONTHLY_FILES)

    for i, (month_name, info) in enumerate(MONTHLY_FILES.items()):
        progress.progress((i) / total, text=f"Chargement {month_name}…")
        df = download_and_parse(info["url"], info["sheet"], month_name)
        if df is not None and not df.empty:
            frames.append(df)
        else:
            errors.append(month_name)

    progress.progress(1.0, text="✅ Données chargées")
    progress.empty()

    if errors:
        st.sidebar.warning(f"⚠️ Mois non chargés : {', '.join(errors)}")

    if not frames:
        st.error("❌ Aucune donnée chargée. Vérifiez les fichiers GitHub.")
        st.stop()

    return pd.concat(frames, ignore_index=True)


# ─────────────────────────────────────────────
# SAFE SLIDER HELPER
# ─────────────────────────────────────────────
def safe_slider(label_html: str, series: pd.Series, key: str):
    """Render a range slider safely, handling NaN / flat ranges."""
    clean = series.dropna()
    if clean.empty:
        st.markdown(label_html, unsafe_allow_html=True)
        st.caption("Aucune donnée")
        return (0.0, 0.0)

    vmin, vmax = float(clean.min()), float(clean.max())
    if vmin == vmax:
        vmax = vmin + 0.0001   # avoid Streamlit crash on flat range

    st.markdown(label_html, unsafe_allow_html=True)
    return st.slider("", vmin, vmax, (vmin, vmax), key=key, label_visibility="collapsed")


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 20px 0 12px 0;">
        <img src="https://raw.githubusercontent.com/Ouiam-Zemmouri/LME_Sales-Analysis/main/COFICAB.png"
             style="max-width:155px; border-radius:10px; filter: drop-shadow(0 4px 12px rgba(99,179,237,0.15));" />
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("## 🔍 Filtres")

    # ── Load data (cached per file) ──
    df_raw = load_all_data()

    def make_select(label, col, df):
        if col not in df.columns:
            return []
        all_vals = sorted(df[col].dropna().astype(str).unique().tolist())
        st.markdown(f'<p class="filter-label">{label}</p>', unsafe_allow_html=True)
        sel = st.multiselect("", all_vals, default=[], key=f"sel_{col}",
                             placeholder="Tous", label_visibility="collapsed")
        return sel if sel else all_vals

    cs_col = "CROSS SECTION mm" if "CROSS SECTION mm" in df_raw.columns else "ES mm"

    f_entity   = make_select("Entity",           "ENTITIES",     df_raw)
    f_month    = make_select("Month",             "Month Name",   df_raw)
    f_rm       = make_select("RM",                "RM",           df_raw)
    f_family   = make_select("Product Family",    "FAMILY",       df_raw)
    f_group    = make_select("Groups",            "GROUPS",       df_raw)
    f_cs       = make_select("Cross Section mm",  cs_col,         df_raw)
    f_fix      = make_select("Fixation",          "Fixation",     df_raw)
    f_spool    = make_select("Spool Type",        "SPOOL TYPE",   df_raw)
    f_lme_proj = make_select("LME Projects",      "LME PROJECTS", df_raw)

    # Safe sliders — no crash on NaN or flat range
    f_lme   = safe_slider('<p class="filter-label">LME Sales €/kg</p>',   df_raw["LME SALES €/kg"],  "lme_sl")
    f_basic = safe_slider('<p class="filter-label">Basic LME €/kg</p>',   df_raw["BASIC LME  €/kg"], "basic_sl")

    st.markdown("---")

# ─────────────────────────────────────────────
# APPLY FILTERS
# ─────────────────────────────────────────────
def isin_safe(series, values):
    return series.astype(str).isin(values)

mask = (
    isin_safe(df_raw["ENTITIES"],   f_entity) &
    isin_safe(df_raw["Month Name"], f_month)  &
    isin_safe(df_raw["RM"],         f_rm)     &
    isin_safe(df_raw["FAMILY"],     f_family) &
    isin_safe(df_raw["GROUPS"],     f_group)  &
    isin_safe(df_raw[cs_col],       f_cs)     &
    isin_safe(df_raw["Fixation"],   f_fix)    &
    isin_safe(df_raw["SPOOL TYPE"], f_spool)  &
    isin_safe(df_raw["LME PROJECTS"], f_lme_proj) &
    df_raw["LME SALES €/kg"].between(f_lme[0],   f_lme[1],   inclusive="both") &
    df_raw["BASIC LME  €/kg"].between(f_basic[0], f_basic[1], inclusive="both")
)
df = df_raw[mask].copy()

# Guard: show warning if nothing passes filter
if df.empty:
    st.warning("⚠️ Aucune donnée avec les filtres sélectionnés. Essayez de réinitialiser les filtres.")
    st.stop()

# ─────────────────────────────────────────────
# KPI CALCULATIONS
# ─────────────────────────────────────────────
total_qty_km    = df["QTY Km"].sum()
total_ca        = df["TOTAL AMOUNT €"].sum()
total_rc_kg     = df["RC Needs Kg"].sum()
total_cc_kg     = df["CC Needs Kg"].sum() if "CC Needs Kg" in df.columns else 0
total_es        = df["ES mm"].sum()
total_av        = df["AV INDEX"].sum()
total_tonnage_t = total_rc_kg / 1000

avg_lme         = df["LME SALES €/kg"].mean()
avg_basic_lme   = df["BASIC LME  €/kg"].mean()
avg_es          = total_es / total_qty_km if total_qty_km else 0
avg_rc_kg_km    = total_rc_kg / total_qty_km if total_qty_km else 0
avg_cc_kg_km    = total_cc_kg / total_qty_km if total_qty_km else 0
avg_av_km       = total_av / total_qty_km if total_qty_km else 0
avg_ca_km       = df["UNIT PRICE €/km"].mean() if "UNIT PRICE €/km" in df.columns else 0

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
st.markdown('<div class="title-banner"><h1>SALES ANALYSIS 2026</h1></div>', unsafe_allow_html=True)

# Row count info
st.caption(f"📊 **{len(df):,}** lignes · **{df['ENTITIES'].nunique()}** entité(s) · **{df['Month Name'].nunique()}** mois")

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 KPI Summary", "📈 LME Overview", "🏭 Fixation Analysis", "🔬 Deep Dive", "📋 Raw Data"
])

month_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

# ════════════════════════════════════════════
# TAB 1 – KPI SUMMARY
# ════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-header">📊 Global KPIs</div>', unsafe_allow_html=True)

    kpis_row1 = [
        ("CA Total (€)",        f"€{total_ca/1e6:.2f}M",        "Chiffre d'Affaires"),
        ("Qty Total (km)",      f"{total_qty_km:,.0f}",          "km vendus"),
        ("Tonnage RC (T)",      f"{total_tonnage_t:,.1f}",       "Real Copper"),
        ("Avg LME All-In",      f"{avg_lme:.4f} €/kg",          "LME moyen"),
        ("Avg Basic LME €/kg",  f"{avg_basic_lme:.4f}",          "LME basic moyen"),
    ]
    for col, (label, val, sub) in zip(st.columns(5), kpis_row1):
        col.markdown(f'<div class="kpi-card"><div class="kpi-label">{label}</div><div class="kpi-value">{val}</div><div class="kpi-sub">{sub}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    kpis_row2 = [
        ("Avg ES mm",    f"{avg_es:.3f}",       "Cross-section moyen"),
        ("Avg RC Kg/km", f"{avg_rc_kg_km:.3f}", "Real Copper Kg/km"),
        ("Avg CC Kg/km", f"{avg_cc_kg_km:.3f}", "Comm. Copper Kg/km"),
        ("Avg AV €/km",  f"€{avg_av_km:.2f}",  "Added Value / km"),
    ]
    for col, (label, val, sub) in zip(st.columns(4), kpis_row2):
        col.markdown(f'<div class="kpi-card"><div class="kpi-label">{label}</div><div class="kpi-value">{val}</div><div class="kpi-sub">{sub}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns(2)
    ent_data = df.groupby("ENTITIES").agg(CA=("TOTAL AMOUNT €","sum"), Qty_Km=("QTY Km","sum")).reset_index()

    with col_left:
        fig = px.bar(ent_data, x="ENTITIES", y="CA", color="ENTITIES",
                     text_auto=".2s", title="Chiffre d'Affaires par Entité (€)",
                     color_discrete_sequence=[COLORS["primary"], COLORS["gold"]])
        fig.update_layout(**CHART_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        fig2 = px.bar(ent_data, x="ENTITIES", y="Qty_Km", color="ENTITIES",
                      text_auto=".2s", title="Quantité par Entité (km)",
                      color_discrete_sequence=[COLORS["teal"], COLORS["purple"]])
        fig2.update_layout(**CHART_LAYOUT)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-header">📐 ES mm & Cross Section par Entité</div>', unsafe_allow_html=True)
    es_entity = (
        df.groupby("ENTITIES")
          .apply(lambda g: pd.Series({
              "Total ES mm":       g["ES mm"].sum(),
              "Total Qty km":      g["QTY Km"].sum(),
              "Avg Cross Section": g["ES mm"].sum() / g["QTY Km"].sum() if g["QTY Km"].sum() else 0,
              "Avg RC Kg/km":      g["RC Needs Kg"].sum() / g["QTY Km"].sum() if g["QTY Km"].sum() else 0,
              "Avg CC Kg/km":      g["CC Needs Kg"].sum() / g["QTY Km"].sum() if g["QTY Km"].sum() and "CC Needs Kg" in g else 0,
              "Avg AV €/km":       g["AV INDEX"].sum() / g["QTY Km"].sum() if g["QTY Km"].sum() else 0,
          }))
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


# ════════════════════════════════════════════
# TAB 2 – LME OVERVIEW
# ════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-header">📈 LME Sales — Évolution Mensuelle</div>', unsafe_allow_html=True)

    monthly = (
        df.groupby(["Month","Month Name","ENTITIES"])
          .agg(LME_Sales=("LME SALES €/kg","mean"), LME_Min=("LME SALES €/kg","min"),
               LME_Max=("LME SALES €/kg","max"), Basic_LME=("BASIC LME  €/kg","mean"),
               Basic_Min=("BASIC LME  €/kg","min"), Basic_Max=("BASIC LME  €/kg","max"),
               Qty_Km=("QTY Km","sum"), CA=("TOTAL AMOUNT €","sum"))
          .reset_index()
    )
    monthly["Month Name"] = pd.Categorical(monthly["Month Name"], categories=month_order, ordered=True)
    monthly = monthly.sort_values(["Month Name","ENTITIES"])

    band_fills = {"COFICAB Kenitra": "rgba(99,179,237,0.10)",  "COFICAB Maroc": "rgba(246,173,85,0.10)"}
    ent_colors = {"COFICAB Kenitra": COLORS["primary"],         "COFICAB Maroc": COLORS["gold"]}
    ent_cols2  = {"COFICAB Kenitra": COLORS["teal"],            "COFICAB Maroc": COLORS["purple"]}

    col_g1, col_g2 = st.columns(2)

    def make_line_band(monthly_df, y_col, y_min_col, y_max_col, colors, fills, title, symbol="circle"):
        fig = go.Figure()
        for ent, grp in monthly_df.groupby("ENTITIES"):
            c = colors.get(ent, COLORS["primary"])
            fill = fills.get(ent, "rgba(99,179,237,0.10)")
            fig.add_trace(go.Scatter(
                x=list(grp["Month Name"]) + list(grp["Month Name"])[::-1],
                y=list(grp[y_max_col]) + list(grp[y_min_col])[::-1],
                fill="toself", fillcolor=fill, line=dict(color="rgba(0,0,0,0)"),
                showlegend=False, hoverinfo="skip",
            ))
            fig.add_trace(go.Scatter(
                x=grp["Month Name"], y=grp[y_col],
                mode="lines+markers+text", name=ent,
                line=dict(color=c, width=2.5),
                marker=dict(size=9, symbol=symbol, line=dict(width=2, color=c)),
                text=[f"{v:.4f}" for v in grp[y_col]],
                textposition="top center", textfont=dict(size=9, color=c),
            ))
        fig.update_layout(**CHART_LAYOUT, title=title)
        return fig

    with col_g1:
        st.markdown("##### All-In LME (€/kg) — Avg · Min · Max")
        st.plotly_chart(make_line_band(monthly, "LME_Sales","LME_Min","LME_Max",
                                       ent_colors, band_fills, "LME All-In €/kg"),
                        use_container_width=True)
    with col_g2:
        st.markdown("##### Basic LME (€/kg) — Avg · Min · Max")
        st.plotly_chart(make_line_band(monthly, "Basic_LME","Basic_Min","Basic_Max",
                                       ent_cols2, band_fills, "Basic LME €/kg", symbol="diamond"),
                        use_container_width=True)

    # All-In vs Basic combined
    st.markdown('<div class="section-header">📊 All-In vs Basic — Vue Combinée</div>', unsafe_allow_html=True)
    monthly_all = (
        df.groupby(["Month","Month Name"])
          .agg(LME_Sales=("LME SALES €/kg","mean"), Basic_LME=("BASIC LME  €/kg","mean"))
          .reset_index()
    )
    monthly_all["Month Name"] = pd.Categorical(monthly_all["Month Name"], categories=month_order, ordered=True)
    monthly_all = monthly_all.sort_values("Month Name")

    fig3 = go.Figure()
    for col_name, color, symbol, pos in [
        ("LME_Sales",  COLORS["primary"], "circle",  "top center"),
        ("Basic_LME",  COLORS["gold"],    "diamond", "bottom center"),
    ]:
        label = "LME All-In €/kg" if "Sales" in col_name else "Basic LME €/kg"
        fig3.add_trace(go.Scatter(
            x=monthly_all["Month Name"], y=monthly_all[col_name],
            name=label, mode="lines+markers+text",
            line=dict(color=color, width=3),
            marker=dict(size=11, symbol=symbol, line=dict(width=2, color=color)),
            text=[f"<b>{v:.4f}</b>" for v in monthly_all[col_name]],
            textposition=pos, textfont=dict(size=10, color=color),
        ))
    fig3.update_layout(**CHART_LAYOUT, title="LME All-In vs Basic — Comparaison Mensuelle")
    st.plotly_chart(fig3, use_container_width=True)

    # By Fixation
    st.markdown('<div class="section-header">🔧 LME par Fixation</div>', unsafe_allow_html=True)
    by_fix_month = (
        df.groupby(["Month","Month Name","Fixation"])
          .agg(LME_Sales=("LME SALES €/kg","mean"), Qty_Km=("QTY Km","sum"))
          .reset_index()
    )
    by_fix_month["Month Name"] = pd.Categorical(by_fix_month["Month Name"], categories=month_order, ordered=True)
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
                line=dict(color=c, width=2.5), marker=dict(size=9),
                text=[f"{v:.4f}" for v in grp["LME_Sales"]],
                textposition="top center", textfont=dict(size=8, color=c),
            ))
        fig_fx.update_layout(**CHART_LAYOUT, title="LME All-In €/kg par Fixation")
        st.plotly_chart(fig_fx, use_container_width=True)

    with col_fx2:
        fig_fx2 = go.Figure()
        for fix, grp in by_fix_month.groupby("Fixation"):
            c = fix_colors.get(fix, COLORS["purple"])
            fig_fx2.add_trace(go.Bar(
                x=grp["Month Name"], y=grp["Qty_Km"], name=fix,
                marker_color=c, opacity=0.85,
                text=[f"{v/1000:.1f}K" for v in grp["Qty_Km"]], textposition="auto",
            ))
        fig_fx2.update_layout(**CHART_LAYOUT, barmode="group", title="Qty (km) par Fixation")
        st.plotly_chart(fig_fx2, use_container_width=True)

    # By Group
    st.markdown('<div class="section-header">📦 Performance par Groupe Client</div>', unsafe_allow_html=True)
    grp_data = (
        df.groupby("GROUPS")
          .agg(LME_Sales=("LME SALES €/kg","mean"), Basic_LME=("BASIC LME  €/kg","mean"),
               Qty_Km=("QTY Km","sum"), CA=("TOTAL AMOUNT €","sum"))
          .reset_index().sort_values("CA", ascending=False)
    )
    fig_grp = go.Figure()
    for y_col, color, name in [("LME_Sales", COLORS["primary"], "LME All-In €/kg"),
                                 ("Basic_LME",  COLORS["gold"],    "Basic LME €/kg")]:
        fig_grp.add_trace(go.Bar(
            x=grp_data["GROUPS"], y=grp_data[y_col], name=name,
            marker_color=color, opacity=0.9,
            text=[f"{v:.4f}" for v in grp_data[y_col]], textposition="auto",
        ))
    fig_grp.update_layout(**CHART_LAYOUT, barmode="group", title="LME Moyen par Groupe Client")
    st.plotly_chart(fig_grp, use_container_width=True)


# ════════════════════════════════════════════
# TAB 3 – FIXATION ANALYSIS
# ════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header">🔧 Répartition par Fixation (M-1 · 3M-1 · 3M-2)</div>', unsafe_allow_html=True)

    fix_cols_ui = st.columns(len(fix_data) + 1)
    for i, row in fix_data.iterrows():
        pct = row["Qty_Km"] / total_qty_km * 100 if total_qty_km else 0
        fix_cols_ui[i].markdown(
            f'<div class="kpi-card"><div class="kpi-label">{row["Fixation"]}</div>'
            f'<div class="kpi-value">{row["Tonnage_T"]:,.1f} T</div>'
            f'<div class="kpi-sub">{row["Qty_Km"]:,.0f} km · {pct:.1f}%</div></div>',
            unsafe_allow_html=True
        )
    fix_cols_ui[-1].markdown(
        f'<div class="kpi-card" style="border-left-color:#90cdf4;">'
        f'<div class="kpi-label">⚡ TOTAL</div>'
        f'<div class="kpi-value">{total_tonnage_t:,.1f} T</div>'
        f'<div class="kpi-sub">{total_qty_km:,.0f} km · 100%</div></div>',
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)
    colA, colB, colC = st.columns(3)
    donut_colors = [
        [COLORS["red"],    COLORS["blue"],   COLORS["gold"]],
        [COLORS["teal"],   COLORS["purple"], COLORS["green"]],
        [COLORS["gold"],   COLORS["red"],    COLORS["blue"]],
    ]
    donut_configs = [
        ("Tonnage_T", "Tonnage (T) par Fixation"),
        ("Qty_Km",    "Quantité (km) par Fixation"),
        ("CA",        "CA (€) par Fixation"),
    ]
    for col_ui, (val_col, title), colors in zip([colA, colB, colC], donut_configs, donut_colors):
        fig_d = px.pie(fix_data, values=val_col, names="Fixation", hole=0.55,
                       title=title, color_discrete_sequence=colors)
        fig_d.update_traces(textposition="outside", textinfo="label+percent")
        fig_d.update_layout(**CHART_LAYOUT)
        col_ui.plotly_chart(fig_d, use_container_width=True)

    fix_entity = (
        df.groupby(["Fixation","ENTITIES"])
          .agg(Tonnage_T=("RC Needs Kg", lambda x: x.sum()/1000),
               Qty_Km=("QTY Km","sum"), CA=("TOTAL AMOUNT €","sum"))
          .reset_index()
    )
    fig_fix_ent = px.bar(fix_entity, x="Fixation", y="Tonnage_T", color="ENTITIES",
                         barmode="group", text_auto=".1f",
                         title="Tonnage (T) par Fixation & Entité",
                         color_discrete_sequence=[COLORS["red"], COLORS["blue"]],
                         labels={"Tonnage_T": "Tonnage (T)"})
    fig_fix_ent.update_layout(**CHART_LAYOUT)
    st.plotly_chart(fig_fix_ent, use_container_width=True)

    st.markdown('<div class="section-header">📋 Tableau de Synthèse Fixation</div>', unsafe_allow_html=True)
    fix_summary = (
        df.groupby("Fixation")
          .agg(**{
              "Tonnage (T)":    ("RC Needs Kg", lambda x: round(x.sum()/1000, 2)),
              "Qty (km)":       ("QTY Km", lambda x: round(x.sum(), 2)),
              "CA €":           ("TOTAL AMOUNT €", lambda x: round(x.sum(), 2)),
              "Avg LME All-In": ("LME SALES €/kg", lambda x: round(x.mean(), 4)),
              "Avg Basic LME":  ("BASIC LME  €/kg", lambda x: round(x.mean(), 4)),
          })
          .reset_index()
    )
    total_row = pd.DataFrame([{"Fixation":"TOTAL","Tonnage (T)":round(total_tonnage_t,2),
                                "Qty (km)":round(total_qty_km,2),"CA €":round(total_ca,2),
                                "Avg LME All-In":round(avg_lme,4),"Avg Basic LME":round(avg_basic_lme,4)}])
    fix_summary = pd.concat([fix_summary, total_row], ignore_index=True)
    st.dataframe(
        fix_summary.style
            .format({"Tonnage (T)": "{:,.2f}", "Qty (km)": "{:,.2f}",
                     "CA €": "€{:,.2f}", "Avg LME All-In": "{:.4f}", "Avg Basic LME": "{:.4f}"})
            .set_properties(**{"background-color": "#1a1f2e", "color": "#aab4c8"}),
        use_container_width=True, hide_index=True
    )


# ════════════════════════════════════════════
# TAB 4 – DEEP DIVE
# ════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header">🔬 Analyse par Famille</div>', unsafe_allow_html=True)

    fam_data = (
        df.groupby("FAMILY")
          .agg(CA=("TOTAL AMOUNT €","sum"), Qty_Km=("QTY Km","sum"),
               Tonnage_T=("RC Needs Kg", lambda x: x.sum()/1000),
               Avg_LME=("LME SALES €/kg","mean"))
          .reset_index().sort_values("CA", ascending=False).head(15)
    )
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        fig_fam = px.bar(fam_data, x="FAMILY", y="CA", title="CA (€) par Famille — Top 15",
                         color="CA", color_continuous_scale=["#0a0f1a","#63b3ed"], text_auto=".2s")
        fig_fam.update_layout(**CHART_LAYOUT, coloraxis_showscale=False, xaxis_tickangle=-45)
        st.plotly_chart(fig_fam, use_container_width=True)
    with col_f2:
        fig_fam2 = px.bar(fam_data, x="FAMILY", y="Tonnage_T", title="Tonnage (T) par Famille — Top 15",
                          color="Tonnage_T", color_continuous_scale=["#0a0f1a","#4fd1c5"], text_auto=".1f")
        fig_fam2.update_layout(**CHART_LAYOUT, coloraxis_showscale=False, xaxis_tickangle=-45)
        st.plotly_chart(fig_fam2, use_container_width=True)

    st.markdown('<div class="section-header">🧱 Matière Première (RM)</div>', unsafe_allow_html=True)
    rm_data = (
        df.groupby("RM")
          .agg(Qty_Km=("QTY Km","sum"), CA=("TOTAL AMOUNT €","sum"),
               Tonnage_T=("RC Needs Kg", lambda x: x.sum()/1000))
          .reset_index()
    )
    col_r1, col_r2 = st.columns(2)
    for col_ui, val_col, title, colors in [
        (col_r1, "Qty_Km",    "Qty (km) par RM",      [COLORS["red"],COLORS["blue"],COLORS["gold"],COLORS["teal"]]),
        (col_r2, "Tonnage_T", "Tonnage (T) par RM",   [COLORS["purple"],COLORS["green"],COLORS["red"],COLORS["blue"]]),
    ]:
        fig_rm = px.pie(rm_data, values=val_col, names="RM", hole=0.5, title=title,
                        color_discrete_sequence=colors)
        fig_rm.update_layout(**CHART_LAYOUT)
        col_ui.plotly_chart(fig_rm, use_container_width=True)

    st.markdown('<div class="section-header">🪝 Analyse par Type de Bobine</div>', unsafe_allow_html=True)
    spool_data = (
        df.groupby(["SPOOL TYPE","ENTITIES"])
          .agg(Qty_Km=("QTY Km","sum"), CA=("TOTAL AMOUNT €","sum"))
          .reset_index()
    )
    fig_spool = px.bar(spool_data, x="SPOOL TYPE", y="Qty_Km", color="ENTITIES",
                       barmode="group", text_auto=".2s",
                       title="Quantité (km) par Spool Type & Entité",
                       color_discrete_sequence=[COLORS["red"], COLORS["blue"]])
    fig_spool.update_layout(**CHART_LAYOUT)
    st.plotly_chart(fig_spool, use_container_width=True)


# ════════════════════════════════════════════
# TAB 5 – RAW DATA
# ════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-header">📋 Données Filtrées</div>', unsafe_allow_html=True)

    search_query = st.text_input("", placeholder="🔍  Rechercher dans toutes les colonnes",
                                 label_visibility="collapsed")

    all_cols = list(df.columns)
    default_cols = ["ENTITIES","Month Name","GROUPS","FAMILY","Fixation","QTY Km",
                    "RC Needs Kg","CC Needs Kg","LME SALES €/kg","BASIC LME  €/kg",
                    "TOTAL AMOUNT €","UNIT PRICE €/km","ES mm","AV INDEX","SPOOL TYPE","RM"]
    sel_cols = st.multiselect("Colonnes à afficher", all_cols,
                              default=[c for c in default_cols if c in all_cols])

    display_df = df[sel_cols].reset_index(drop=True) if sel_cols else df.reset_index(drop=True)

    # Limit search to string columns to avoid slow apply
    if search_query:
        str_cols_only = display_df.select_dtypes(include="object").columns
        if len(str_cols_only):
            mask_s = display_df[str_cols_only].apply(
                lambda col: col.str.contains(search_query, case=False, na=False)
            ).any(axis=1)
            display_df = display_df[mask_s]

    st.caption(f"**{len(display_df):,}** lignes affichées")
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
