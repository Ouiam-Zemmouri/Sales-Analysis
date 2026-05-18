import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="LME Sales Analysis 2026", page_icon="🥇", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main, [data-testid="stAppViewContainer"] { background: #080c14; }
    [data-testid="stHeader"] { background: transparent; }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    .title-banner {
        background: linear-gradient(135deg, #0d1321 0%, #111827 40%, #0a1628 100%);
        border: 1px solid rgba(99,179,237,0.25); border-top: 3px solid #63b3ed;
        border-radius: 16px; padding: 28px 40px; margin-bottom: 28px; text-align: center;
        box-shadow: 0 4px 40px rgba(99,179,237,0.08);
    }
    .title-banner h1 {
        font-size: 2.1rem; font-weight: 800; letter-spacing: 4px; margin: 0;
        text-transform: uppercase;
        background: linear-gradient(90deg, #63b3ed, #90cdf4, #63b3ed);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    }
    .kpi-card {
        background: linear-gradient(145deg, #0d1321, #111827);
        border: 1px solid rgba(255,255,255,0.07); border-left: 3px solid #63b3ed;
        border-radius: 12px; padding: 18px 16px; text-align: center;
        height: 115px; display: flex; flex-direction: column; justify-content: center;
        box-shadow: 0 2px 20px rgba(0,0,0,0.3);
    }
    .kpi-label { color: #718096; font-size: 0.65rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 8px; }
    .kpi-value { color: #90cdf4; font-size: 1.55rem; font-weight: 700; line-height: 1.1; }
    .kpi-sub   { color: #4a5568; font-size: 0.7rem; margin-top: 5px; }
    .section-header {
        color: #90cdf4; font-size: 0.78rem; font-weight: 700; text-transform: uppercase;
        letter-spacing: 2.5px; border-bottom: 1px solid rgba(99,179,237,0.2);
        padding-bottom: 8px; margin: 28px 0 18px 0;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 4px; background: #0d1321; border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 5px; }
    .stTabs [data-baseweb="tab"] { background: transparent; color: #4a5568; border-radius: 9px; font-weight: 600; font-size: 0.82rem; padding: 9px 20px; }
    .stTabs [aria-selected="true"] { background: linear-gradient(135deg,#1a365d,#2a4a7f) !important; color: #90cdf4 !important; }
    [data-testid="stSidebar"] { background: #060a10; border-right: 1px solid rgba(255,255,255,0.05); }
    .filter-label { color: #4a5568; font-size: 0.62rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.8px; margin: 16px 0 3px 0; }
    [data-baseweb="tag"] { background: rgba(99,179,237,0.15) !important; border: 1px solid rgba(99,179,237,0.3) !important; color: #90cdf4 !important; border-radius: 6px !important; }
    ::-webkit-scrollbar { width: 4px; height: 4px; }
    ::-webkit-scrollbar-track { background: #0d1321; }
    ::-webkit-scrollbar-thumb { background: #2d3748; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #63b3ed; }
</style>
""", unsafe_allow_html=True)

# ── COLORS & LAYOUT ──
C = dict(primary="#63b3ed", gold="#f6ad55", teal="#4fd1c5", purple="#b794f4",
         red="#fc8181", green="#68d391", blue="#63b3ed")
LAY = dict(
    paper_bgcolor="#080c14", plot_bgcolor="#0a0f1a",
    font=dict(color="#718096", family="Inter", size=12),
    margin=dict(t=55, b=45, l=55, r=25),
    legend=dict(bgcolor="rgba(13,19,33,0.9)", bordercolor="rgba(99,179,237,0.15)", borderwidth=1, font=dict(color="#a0aec0", size=11)),
    xaxis=dict(gridcolor="rgba(255,255,255,0.04)", zeroline=False, tickfont=dict(color="#4a5568", size=11)),
    yaxis=dict(gridcolor="rgba(255,255,255,0.04)", zeroline=False, tickfont=dict(color="#4a5568", size=11)),
    title_font=dict(color="#90cdf4", size=13, family="Inter"),
    hoverlabel=dict(bgcolor="#0d1321", bordercolor="rgba(99,179,237,0.3)", font=dict(color="#e2e8f0", size=12)),
)

# ── LOAD DATA (1.3 MB CSV — instantané) ──
@st.cache_data
def load_data():
    # Try multiple encodings to be safe
    for enc in ["utf-8", "utf-8-sig", "latin-1"]:
        try:
            df = pd.read_csv("lme_dashboard_data.csv", encoding=enc)
            break
        except Exception:
            continue
    # Strip BOM and spaces from column names
    df.columns = df.columns.str.strip().str.lstrip("\ufeff")
    # Normalize any leftover renamed columns
    rename_map = {
        "QTY_Km":        "QTY Km",
        "RC_Needs_Kg":   "RC Needs Kg",
        "CC_Needs_Kg":   "CC Needs Kg",
        "ES_mm":         "ES mm",
        "AV_INDEX":      "AV INDEX",
        "TOTAL_AMOUNT":  "TOTAL AMOUNT €",
        "LME_SALES_avg": "LME SALES €/kg",
        "BASIC_LME_avg": "BASIC LME  €/kg",
        "UNIT_PRICE_avg":"UNIT PRICE €/km",
        "AV_avg":        "ADDED VALUE €/km",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
    return df

df_raw = load_data()

# ── SIDEBAR FILTERS ──
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:20px 0 12px 0;">
        <img src="https://raw.githubusercontent.com/Ouiam-Zemmouri/LME_Sales-Analysis/main/COFICAB.png"
             style="max-width:155px;border-radius:10px;" />
    </div>""", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("## 🔍 Filtres")

    MONTH_ORDER = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

    def ms(label, col):
        if col not in df_raw.columns:
            return []
        if col == "Month Name":
            all_vals = [m for m in MONTH_ORDER if m in df_raw[col].astype(str).values]
        else:
            all_vals = sorted(df_raw[col].dropna().astype(str).unique())
        st.markdown(f'<p class="filter-label">{label}</p>', unsafe_allow_html=True)
        sel = st.multiselect("", all_vals, default=[], key=f"f_{col}", placeholder="Tous", label_visibility="collapsed")
        return sel if sel else list(all_vals)

    f_entity = ms("Entity",          "ENTITIES")
    f_month  = ms("Month",           "Month Name")
    f_rm     = ms("RM",              "RM")
    f_family = ms("Product Family",  "FAMILY")
    f_group  = ms("Groups",          "GROUPS")
    f_fix    = ms("Fixation",        "Fixation")
    f_spool  = ms("Spool Type",      "SPOOL TYPE")
    f_lmeprj = ms("LME Projects",    "LME PROJECTS")

    def safe_slider(label, col):
        s = df_raw[col].dropna()
        if s.empty: return (0.0, 0.0)
        vmin, vmax = float(s.min()), float(s.max())
        if vmin == vmax: vmax += 0.0001
        st.markdown(f'<p class="filter-label">{label}</p>', unsafe_allow_html=True)
        return st.slider("", vmin, vmax, (vmin, vmax), key=f"sl_{col}", label_visibility="collapsed")

    f_lme   = safe_slider("LME Sales €/kg",  "LME SALES €/kg")
    f_basic = safe_slider("Basic LME €/kg",  "BASIC LME  €/kg")
    st.markdown("---")

# ── APPLY FILTERS ──
def isin_s(s, v): return s.astype(str).isin(v)

df = df_raw[
    isin_s(df_raw["ENTITIES"],    f_entity) &
    isin_s(df_raw["Month Name"],  f_month)  &
    isin_s(df_raw["RM"],          f_rm)     &
    isin_s(df_raw["FAMILY"],      f_family) &
    isin_s(df_raw["GROUPS"],      f_group)  &
    isin_s(df_raw["Fixation"],    f_fix)    &
    isin_s(df_raw["SPOOL TYPE"],  f_spool)  &
    isin_s(df_raw["LME PROJECTS"],f_lmeprj) &
    df_raw["LME SALES €/kg"].between(f_lme[0],   f_lme[1])   &
    df_raw["BASIC LME  €/kg"].between(f_basic[0], f_basic[1])
].copy()

if df.empty:
    st.warning("⚠️ Aucune donnée avec ces filtres.")
    st.stop()

# ── KPIs ──
total_qty      = df["QTY Km"].sum()
total_ca       = df["TOTAL AMOUNT €"].sum()
total_rc       = df["RC Needs Kg"].sum()
total_cc       = df["CC Needs Kg"].sum() if "CC Needs Kg" in df.columns else 0
total_tonnage  = total_rc / 1000
avg_lme        = df["LME SALES €/kg"].mean()
avg_basic      = df["BASIC LME  €/kg"].mean()
avg_es         = df["ES mm"].sum() / total_qty if total_qty else 0
avg_rc_km      = total_rc / total_qty if total_qty else 0
avg_cc_km      = total_cc / total_qty if total_qty else 0
avg_av_km      = df["AV INDEX"].sum() / total_qty if total_qty else 0

fix_data = (df.groupby("Fixation")
              .agg(Tonnage_T=("RC Needs Kg", lambda x: x.sum()/1000),
                   Qty_Km=("QTY Km","sum"), CA=("TOTAL AMOUNT €","sum"))
              .reset_index())

month_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

# ── TITLE ──
st.markdown('<div class="title-banner"><h1>SALES ANALYSIS 2026</h1></div>', unsafe_allow_html=True)
st.caption(f"📊 **{len(df):,}** groupes · **{df['ENTITIES'].nunique()}** entité(s) · **{df['Month Name'].nunique()}** mois")

# ════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 KPI Summary","📈 LME Overview","🏭 Fixation","🔬 Deep Dive","📋 Données"])

def kpi(col, label, val, sub):
    col.markdown(f'<div class="kpi-card"><div class="kpi-label">{label}</div><div class="kpi-value">{val}</div><div class="kpi-sub">{sub}</div></div>', unsafe_allow_html=True)

# ── TAB 1 ──
with tab1:
    st.markdown('<div class="section-header">📊 Global KPIs</div>', unsafe_allow_html=True)
    c1,c2,c3,c4,c5 = st.columns(5)
    kpi(c1,"CA Total (€)",      f"€{total_ca/1e6:.2f}M",    "Chiffre d'Affaires")
    kpi(c2,"Qty Total (km)",    f"{total_qty:,.0f}",         "km vendus")
    kpi(c3,"Tonnage RC (T)",    f"{total_tonnage:,.1f}",     "Real Copper")
    kpi(c4,"Avg LME All-In",   f"{avg_lme:.4f} €/kg",      "LME moyen")
    kpi(c5,"Avg Basic LME",    f"{avg_basic:.4f} €/kg",    "LME basic moyen")

    st.markdown("<br>", unsafe_allow_html=True)
    c6,c7,c8,c9 = st.columns(4)
    kpi(c6,"Avg ES mm",     f"{avg_es:.3f}",      "Cross-section moyen")
    kpi(c7,"Avg RC Kg/km",  f"{avg_rc_km:.3f}",   "Real Copper Kg/km")
    kpi(c8,"Avg CC Kg/km",  f"{avg_cc_km:.3f}",   "Comm. Copper Kg/km")
    kpi(c9,"Avg AV €/km",   f"€{avg_av_km:.2f}",  "Added Value / km")

    st.markdown("<br>", unsafe_allow_html=True)
    ent = df.groupby("ENTITIES").agg(CA=("TOTAL AMOUNT €","sum"), Qty=("QTY Km","sum")).reset_index()
    cl, cr = st.columns(2)
    with cl:
        fig = px.bar(ent, x="ENTITIES", y="CA", color="ENTITIES", text_auto=".2s",
                     title="CA par Entité (€)", color_discrete_sequence=[C["primary"],C["gold"]])
        fig.update_layout(**LAY); st.plotly_chart(fig, use_container_width=True)
    with cr:
        fig2 = px.bar(ent, x="ENTITIES", y="Qty", color="ENTITIES", text_auto=".2s",
                      title="Quantité par Entité (km)", color_discrete_sequence=[C["teal"],C["purple"]])
        fig2.update_layout(**LAY); st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-header">📐 ES mm & Cross Section par Entité</div>', unsafe_allow_html=True)
    es_ent = (df.groupby("ENTITIES")
                .apply(lambda g: pd.Series({
                    "Total ES mm":       g["ES mm"].sum(),
                    "Total Qty km":      g["QTY Km"].sum(),
                    "Avg Cross Section": g["ES mm"].sum()/g["QTY Km"].sum() if g["QTY Km"].sum() else 0,
                    "Avg RC Kg/km":      g["RC Needs Kg"].sum()/g["QTY Km"].sum() if g["QTY Km"].sum() else 0,
                    "Avg CC Kg/km":      g["CC Needs Kg"].sum()/g["QTY Km"].sum() if g["QTY Km"].sum() else 0,
                    "Avg AV €/km":       g["AV INDEX"].sum()/g["QTY Km"].sum() if g["QTY Km"].sum() else 0,
                })).reset_index())
    st.dataframe(es_ent.style
        .format({"Total ES mm":"{:,.3f}","Total Qty km":"{:,.2f}","Avg Cross Section":"{:.3f}",
                 "Avg RC Kg/km":"{:.3f}","Avg CC Kg/km":"{:.3f}","Avg AV €/km":"€{:.2f}"})
        .set_properties(**{"background-color":"#0d1321","color":"#a0aec0"}),
        use_container_width=True, hide_index=True)

# ── TAB 2 ──
with tab2:
    st.markdown('<div class="section-header">📈 LME — Évolution Mensuelle</div>', unsafe_allow_html=True)
    monthly = (df.groupby(["Month","Month Name","ENTITIES"])
                 .agg(LME_Sales=("LME SALES €/kg","mean"), LME_Min=("LME SALES €/kg","min"),
                      LME_Max=("LME SALES €/kg","max"),   Basic_LME=("BASIC LME  €/kg","mean"),
                      Basic_Min=("BASIC LME  €/kg","min"),Basic_Max=("BASIC LME  €/kg","max"),
                      Qty_Km=("QTY Km","sum"), CA=("TOTAL AMOUNT €","sum"))
                 .reset_index())
    monthly["Month Name"] = pd.Categorical(monthly["Month Name"], categories=month_order, ordered=True)
    monthly = monthly.sort_values(["Month Name","ENTITIES"])

    ent_c  = {"COFICAB Kenitra": C["primary"], "COFICAB Maroc": C["gold"]}
    ent_c2 = {"COFICAB Kenitra": C["teal"],    "COFICAB Maroc": C["purple"]}
    fills  = {"COFICAB Kenitra": "rgba(99,179,237,0.10)", "COFICAB Maroc": "rgba(246,173,85,0.10)"}

    def band_chart(mdf, y, ymin, ymax, colors, fills, title, sym="circle"):
        fig = go.Figure()
        for ent, grp in mdf.groupby("ENTITIES"):
            c = colors.get(ent, C["primary"]); f = fills.get(ent, "rgba(99,179,237,0.10)")
            fig.add_trace(go.Scatter(
                x=list(grp["Month Name"])+list(grp["Month Name"])[::-1],
                y=list(grp[ymax])+list(grp[ymin])[::-1],
                fill="toself", fillcolor=f, line=dict(color="rgba(0,0,0,0)"),
                showlegend=False, hoverinfo="skip"))
            fig.add_trace(go.Scatter(
                x=grp["Month Name"], y=grp[y], mode="lines+markers+text", name=ent,
                line=dict(color=c, width=2.5),
                marker=dict(size=9, symbol=sym, line=dict(width=2, color=c)),
                text=[f"{v:.4f}" for v in grp[y]],
                textposition="top center", textfont=dict(size=9, color=c)))
        fig.update_layout(**LAY, title=title)
        return fig

    cl, cr = st.columns(2)
    with cl:
        st.markdown("##### All-In LME (€/kg)")
        st.plotly_chart(band_chart(monthly,"LME_Sales","LME_Min","LME_Max",ent_c,fills,"LME All-In €/kg"), use_container_width=True)
    with cr:
        st.markdown("##### Basic LME (€/kg)")
        st.plotly_chart(band_chart(monthly,"Basic_LME","Basic_Min","Basic_Max",ent_c2,fills,"Basic LME €/kg","diamond"), use_container_width=True)

    st.markdown('<div class="section-header">📊 All-In vs Basic — Vue Combinée</div>', unsafe_allow_html=True)
    mall = (df.groupby(["Month","Month Name"])
              .agg(LME_Sales=("LME SALES €/kg","mean"), Basic_LME=("BASIC LME  €/kg","mean"))
              .reset_index())
    mall["Month Name"] = pd.Categorical(mall["Month Name"], categories=month_order, ordered=True)
    mall = mall.sort_values("Month Name")
    fig3 = go.Figure()
    for col_n, color, sym, pos, name in [
        ("LME_Sales", C["primary"], "circle",  "top center",    "LME All-In €/kg"),
        ("Basic_LME", C["gold"],    "diamond", "bottom center", "Basic LME €/kg"),
    ]:
        fig3.add_trace(go.Scatter(
            x=mall["Month Name"], y=mall[col_n], name=name, mode="lines+markers+text",
            line=dict(color=color, width=3),
            marker=dict(size=11, symbol=sym, line=dict(width=2, color=color)),
            text=[f"<b>{v:.4f}</b>" for v in mall[col_n]],
            textposition=pos, textfont=dict(size=10, color=color)))
    fig3.update_layout(**LAY, title="LME All-In vs Basic — Comparaison Mensuelle")
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown('<div class="section-header">🔧 LME par Fixation</div>', unsafe_allow_html=True)
    bfm = (df.groupby(["Month","Month Name","Fixation"])
             .agg(LME_Sales=("LME SALES €/kg","mean"), Qty_Km=("QTY Km","sum"))
             .reset_index())
    bfm["Month Name"] = pd.Categorical(bfm["Month Name"], categories=month_order, ordered=True)
    bfm = bfm.sort_values("Month Name")
    fix_c = {"M-1": C["primary"], "3M-1": C["gold"], "3M-2": C["teal"]}

    cl2, cr2 = st.columns(2)
    with cl2:
        figfx = go.Figure()
        for fix, grp in bfm.groupby("Fixation"):
            cc = fix_c.get(fix, C["purple"])
            figfx.add_trace(go.Scatter(x=grp["Month Name"], y=grp["LME_Sales"],
                mode="lines+markers+text", name=fix, line=dict(color=cc,width=2.5), marker=dict(size=9),
                text=[f"{v:.4f}" for v in grp["LME_Sales"]], textposition="top center", textfont=dict(size=8, color=cc)))
        figfx.update_layout(**LAY, title="LME All-In €/kg par Fixation")
        st.plotly_chart(figfx, use_container_width=True)
    with cr2:
        figfx2 = go.Figure()
        for fix, grp in bfm.groupby("Fixation"):
            cc = fix_c.get(fix, C["purple"])
            figfx2.add_trace(go.Bar(x=grp["Month Name"], y=grp["Qty_Km"], name=fix,
                marker_color=cc, opacity=0.85,
                text=[f"{v/1000:.1f}K" for v in grp["Qty_Km"]], textposition="auto"))
        figfx2.update_layout(**LAY, barmode="group", title="Qty (km) par Fixation")
        st.plotly_chart(figfx2, use_container_width=True)

    st.markdown('<div class="section-header">📦 Performance par Groupe Client</div>', unsafe_allow_html=True)
    gd = (df.groupby("GROUPS").agg(LME_Sales=("LME SALES €/kg","mean"),
           Basic_LME=("BASIC LME  €/kg","mean"), CA=("TOTAL AMOUNT €","sum"))
           .reset_index().sort_values("CA", ascending=False))
    figgrp = go.Figure()
    # Couleurs professionnelles : bleu acier + vert émeraude
    bar_colors = [("#2563EB", "#1E40AF"), ("#059669", "#047857")]
    for (yc, name), (col_main, col_border) in zip(
        [("LME_Sales","LME All-In €/kg"), ("Basic_LME","Basic LME €/kg")],
        bar_colors
    ):
        figgrp.add_trace(go.Bar(
            x=gd["GROUPS"], y=gd[yc], name=name,
            marker=dict(
                color=col_main,
                line=dict(color=col_border, width=1),
                opacity=0.92,
            ),
            text=[f"{v:.4f}" for v in gd[yc]],
            textposition="outside",
            textfont=dict(size=9, color="#cbd5e0"),
        ))

    all_vals = list(gd["LME_Sales"]) + list(gd["Basic_LME"])
    y_max = max(all_vals) * 1.06

    figgrp.update_layout(
        **LAY,
        barmode="group",
        title="LME Moyen par Groupe Client",
        yaxis=dict(
            range=[0, y_max],
            dtick=0.5,                          # graduations tous les 0.5
            gridcolor="rgba(255,255,255,0.06)",
            zeroline=False,
            tickfont=dict(color="#718096", size=11),
            title="€/kg",
            title_font=dict(color="#718096", size=11),
        ),
        xaxis=dict(
            tickangle=-35,
            tickfont=dict(color="#a0aec0", size=10),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="right",  x=1,
            bgcolor="rgba(13,19,33,0.8)",
            bordercolor="rgba(99,179,237,0.2)",
            borderwidth=1,
            font=dict(color="#a0aec0", size=11),
        ),
        height=500,
    )
    st.plotly_chart(figgrp, use_container_width=True)

# ── TAB 3 ──
with tab3:
    st.markdown('<div class="section-header">🔧 Répartition par Fixation</div>', unsafe_allow_html=True)
    fcols = st.columns(len(fix_data)+1)
    for i, row in fix_data.iterrows():
        pct = row["Qty_Km"]/total_qty*100 if total_qty else 0
        fcols[i].markdown(
            f'<div class="kpi-card"><div class="kpi-label">{row["Fixation"]}</div>'
            f'<div class="kpi-value">{row["Tonnage_T"]:,.1f} T</div>'
            f'<div class="kpi-sub">{row["Qty_Km"]:,.0f} km · {pct:.1f}%</div></div>',
            unsafe_allow_html=True)
    fcols[-1].markdown(
        f'<div class="kpi-card" style="border-left-color:#90cdf4;">'
        f'<div class="kpi-label">⚡ TOTAL</div>'
        f'<div class="kpi-value">{total_tonnage:,.1f} T</div>'
        f'<div class="kpi-sub">{total_qty:,.0f} km · 100%</div></div>',
        unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    colA, colB, colC = st.columns(3)
    for col_ui, val_col, title, colors in [
        (colA,"Tonnage_T","Tonnage (T)",[C["red"],C["blue"],C["gold"]]),
        (colB,"Qty_Km","Quantité (km)",[C["teal"],C["purple"],C["green"]]),
        (colC,"CA","CA (€)",[C["gold"],C["red"],C["blue"]]),
    ]:
        fd = px.pie(fix_data, values=val_col, names="Fixation", hole=0.55, title=title, color_discrete_sequence=colors)
        fd.update_traces(textposition="outside", textinfo="label+percent")
        fd.update_layout(**LAY)
        col_ui.plotly_chart(fd, use_container_width=True)

    fe = (df.groupby(["Fixation","ENTITIES"])
            .agg(Tonnage_T=("RC Needs Kg",lambda x:x.sum()/1000), Qty_Km=("QTY Km","sum"), CA=("TOTAL AMOUNT €","sum"))
            .reset_index())
    figfe = px.bar(fe, x="Fixation", y="Tonnage_T", color="ENTITIES", barmode="group", text_auto=".1f",
                   title="Tonnage (T) par Fixation & Entité", color_discrete_sequence=[C["red"],C["blue"]],
                   labels={"Tonnage_T":"Tonnage (T)"})
    figfe.update_layout(**LAY)
    st.plotly_chart(figfe, use_container_width=True)

    st.markdown('<div class="section-header">📋 Tableau Fixation</div>', unsafe_allow_html=True)
    fs = (df.groupby("Fixation").agg(**{
        "Tonnage (T)":   ("RC Needs Kg",   lambda x: round(x.sum()/1000,2)),
        "Qty (km)":      ("QTY Km",        lambda x: round(x.sum(),2)),
        "CA €":          ("TOTAL AMOUNT €", lambda x: round(x.sum(),2)),
        "Avg LME All-In":("LME SALES €/kg", lambda x: round(x.mean(),4)),
        "Avg Basic LME": ("BASIC LME  €/kg",lambda x: round(x.mean(),4)),
    }).reset_index())
    fs = pd.concat([fs, pd.DataFrame([{"Fixation":"TOTAL","Tonnage (T)":round(total_tonnage,2),
        "Qty (km)":round(total_qty,2),"CA €":round(total_ca,2),
        "Avg LME All-In":round(avg_lme,4),"Avg Basic LME":round(avg_basic,4)}])], ignore_index=True)
    st.dataframe(fs.style
        .format({"Tonnage (T)":"{:,.2f}","Qty (km)":"{:,.2f}","CA €":"€{:,.2f}",
                 "Avg LME All-In":"{:.4f}","Avg Basic LME":"{:.4f}"})
        .set_properties(**{"background-color":"#1a1f2e","color":"#aab4c8"}),
        use_container_width=True, hide_index=True)

# ── TAB 4 ──
with tab4:
    st.markdown('<div class="section-header">🔬 Analyse par Family & CS</div>', unsafe_allow_html=True)

    # Dimension selector
    dim_col = st.radio("Grouper par", ["FAMILY & CS", "FAMILY"], horizontal=True, key="dim_radio")
    top_n   = st.slider("Nombre de références à afficher", 5, 30, 15, key="topn_slider")

    if dim_col not in df.columns:
        st.warning(f"Colonne '{dim_col}' absente du CSV.")
    else:
        fam = (df.groupby(dim_col).agg(
                    CA=("TOTAL AMOUNT €","sum"),
                    Qty_Km=("QTY Km","sum"),
                    Tonnage_T=("RC Needs Kg", lambda x: x.sum()/1000))
               .reset_index()
               .sort_values("CA", ascending=False)
               .head(top_n))

        cl, cr = st.columns(2)
        with cl:
            fig = px.bar(fam, x=dim_col, y="CA",
                         title=f"CA (€) — Top {top_n} {dim_col}",
                         color="CA", color_continuous_scale=["#0a0f1a","#63b3ed"],
                         text_auto=".2s")
            fig.update_layout(**LAY, coloraxis_showscale=False, xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        with cr:
            fig2 = px.bar(fam, x=dim_col, y="Tonnage_T",
                          title=f"Tonnage (T) — Top {top_n} {dim_col}",
                          color="Tonnage_T", color_continuous_scale=["#0a0f1a","#4fd1c5"],
                          text_auto=".1f")
            fig2.update_layout(**LAY, coloraxis_showscale=False, xaxis_tickangle=-45)
            st.plotly_chart(fig2, use_container_width=True)

        # Table détail
        st.markdown('<div class="section-header">📋 Détail par référence</div>', unsafe_allow_html=True)
        fam_detail = (df.groupby(dim_col).agg(
                CA=("TOTAL AMOUNT €","sum"),
                Qty_Km=("QTY Km","sum"),
                Tonnage_T=("RC Needs Kg", lambda x: x.sum()/1000),
                Avg_LME=("LME SALES €/kg","mean"),
                Avg_Basic=("BASIC LME  €/kg","mean"))
            .reset_index()
            .sort_values("CA", ascending=False))
        st.dataframe(
            fam_detail.style
                .format({"CA":"€{:,.0f}","Qty_Km":"{:,.1f}","Tonnage_T":"{:,.1f}",
                         "Avg_LME":"{:.4f}","Avg_Basic":"{:.4f}"})
                .set_properties(**{"background-color":"#0d1321","color":"#a0aec0"}),
            use_container_width=True, hide_index=True, height=400)

    st.markdown('<div class="section-header">🧱 Matière Première (RM)</div>', unsafe_allow_html=True)
    rm = df.groupby("RM").agg(Qty_Km=("QTY Km","sum"),Tonnage_T=("RC Needs Kg",lambda x:x.sum()/1000)).reset_index()
    cl2,cr2 = st.columns(2)
    for col_ui, vc, title, colors in [
        (cl2,"Qty_Km","Qty (km) par RM",[C["red"],C["blue"],C["gold"],C["teal"]]),
        (cr2,"Tonnage_T","Tonnage (T) par RM",[C["purple"],C["green"],C["red"],C["blue"]]),
    ]:
        fig_rm = px.pie(rm,values=vc,names="RM",hole=0.5,title=title,color_discrete_sequence=colors)
        fig_rm.update_layout(**LAY)
        col_ui.plotly_chart(fig_rm,use_container_width=True)

    st.markdown('<div class="section-header">🪝 Analyse Spool Type</div>', unsafe_allow_html=True)
    sp = df.groupby(["SPOOL TYPE","ENTITIES"]).agg(Qty_Km=("QTY Km","sum")).reset_index()
    figsp = px.bar(sp,x="SPOOL TYPE",y="Qty_Km",color="ENTITIES",barmode="group",text_auto=".2s",
                   title="Quantité (km) par Spool Type & Entité",color_discrete_sequence=[C["red"],C["blue"]])
    figsp.update_layout(**LAY)
    st.plotly_chart(figsp,use_container_width=True)

# ── TAB 5 ──
with tab5:
    st.markdown('<div class="section-header">📋 Données Filtrées</div>', unsafe_allow_html=True)
    search = st.text_input("","", placeholder="🔍 Rechercher…", label_visibility="collapsed")
    cols_sel = st.multiselect("Colonnes", list(df.columns), default=list(df.columns))
    disp = df[cols_sel].reset_index(drop=True) if cols_sel else df.reset_index(drop=True)
    if search:
        str_c = disp.select_dtypes("object").columns
        mask = disp[str_c].apply(lambda c: c.str.contains(search,case=False,na=False)).any(axis=1)
        disp = disp[mask]
    st.caption(f"**{len(disp):,}** lignes")
    st.dataframe(disp, use_container_width=True, height=500)

st.markdown("""
<div style="text-align:center;color:#444;font-size:0.75rem;margin-top:40px;padding:16px;border-top:1px solid #2d3561;">
  LME Sales Analysis 2026 · COFICAB Kenitra & COFICAB Maroc
</div>""", unsafe_allow_html=True)

