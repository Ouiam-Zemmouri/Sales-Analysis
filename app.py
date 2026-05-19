import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Sales Analysis 2026",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
.main,[data-testid="stAppViewContainer"]{background:#0b1628;}
[data-testid="stHeader"]{background:transparent;}
.block-container{padding-top:1.5rem;padding-bottom:2rem;}

.title-banner{
  background:linear-gradient(135deg,#0d1e3a 0%,#122040 50%,#0d1e3a 100%);
  border:1px solid rgba(184,115,51,0.25);border-top:3px solid #b87333;
  border-radius:16px;padding:30px 40px;margin-bottom:28px;text-align:center;
  box-shadow:0 6px 60px rgba(184,115,51,0.08);
}
.title-banner h1{
  font-size:2rem;font-weight:800;letter-spacing:5px;margin:0;text-transform:uppercase;
  background:linear-gradient(90deg,#b87333,#d4956a,#f5cba7,#d4956a,#b87333);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
}
.title-banner p{color:#8faac8;font-size:0.8rem;margin:8px 0 0 0;letter-spacing:2px;}

.kpi-card{
  background:linear-gradient(145deg,#0d1e3a,#112244);
  border:1px solid rgba(255,255,255,0.05);border-left:3px solid #b87333;
  border-radius:12px;padding:18px 14px;text-align:center;
  height:118px;display:flex;flex-direction:column;justify-content:center;
  box-shadow:0 2px 24px rgba(0,0,0,0.4);transition:all 0.2s ease;
}
.kpi-card:hover{transform:translateY(-2px);box-shadow:0 6px 32px rgba(184,115,51,0.12);}
.kpi-label{color:#4a6080;font-size:0.6rem;font-weight:700;text-transform:uppercase;letter-spacing:2px;margin-bottom:8px;}
.kpi-value{font-size:1.5rem;font-weight:700;line-height:1.1;}
.kpi-sub{color:#2d4060;font-size:0.67rem;margin-top:5px;} .kpi-unit{margin-top:4px;}

.section-header{
  color:#b87333;font-size:0.72rem;font-weight:700;text-transform:uppercase;letter-spacing:3px;
  border-bottom:1px solid rgba(184,115,51,0.2);padding-bottom:8px;margin:28px 0 18px 0;
}

.stTabs [data-baseweb="tab-list"]{gap:4px;background:#0d1e3a;border:1px solid rgba(184,115,51,0.12);border-radius:12px;padding:5px;}
.stTabs [data-baseweb="tab"]{background:transparent;color:#3a5070;border-radius:9px;font-weight:600;font-size:0.82rem;padding:9px 22px;}
.stTabs [data-baseweb="tab"]:hover{color:#d4956a;background:rgba(184,115,51,0.06);}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,#1a2e4a,#1e3660) !important;color:#d4956a !important;box-shadow:0 2px 12px rgba(184,115,51,0.15);}

[data-testid="stSidebar"]{background:#080f1e;border-right:1px solid rgba(184,115,51,0.08);}
.filter-label{color:#3a5070;font-size:0.58rem;font-weight:700;text-transform:uppercase;letter-spacing:2px;margin:14px 0 3px 0;}

[data-baseweb="tag"]{background:rgba(184,115,51,0.15) !important;border:1px solid rgba(184,115,51,0.3) !important;color:#d4956a !important;border-radius:6px !important;}
::-webkit-scrollbar{width:3px;height:3px;}
::-webkit-scrollbar-track{background:#0d1e3a;}
::-webkit-scrollbar-thumb{background:#1e3660;border-radius:4px;}
::-webkit-scrollbar-thumb:hover{background:#b87333;}
.stDataFrame{border-radius:10px;overflow:hidden;border:1px solid rgba(184,115,51,0.1);}
.stCaption{color:#3a5070 !important;font-size:0.75rem !important;}
</style>
""", unsafe_allow_html=True)

# ── TOKENS ──
NAVY   = "#0b1628";  NAVY_MD = "#0d1e3a"; NAVY_LT = "#1a2e4a"
COPPER = "#b87333";  COP_LT  = "#d4956a"; COP_XL  = "#f5cba7"
BLUE   = "#2b6cb0";  TEAL    = "#0ea5a0"; GOLD    = "#d4a017"
WHITE  = "#e8edf5";  SLATE   = "#8faac8"; ICE     = "#c8d8ea"

ENT_C  = [BLUE, COPPER]
FIX_C  = {"M-1": BLUE, "3M-1": COPPER, "3M-2": TEAL}
MONTH_ORDER = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

LAY = dict(
    paper_bgcolor=NAVY, plot_bgcolor="#090e1c",
    font=dict(color="#4a6080", family="Inter", size=12),
    margin=dict(t=55, b=45, l=60, r=25),
    legend=dict(bgcolor="rgba(13,30,58,0.95)", bordercolor="rgba(184,115,51,0.2)",
                borderwidth=1, font=dict(color=SLATE, size=11)),
    xaxis=dict(gridcolor="rgba(255,255,255,0.03)", zeroline=False,
               tickfont=dict(color="#3a5070", size=11), linecolor="rgba(255,255,255,0.04)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.03)", zeroline=False,
               tickfont=dict(color="#3a5070", size=11), linecolor="rgba(255,255,255,0.04)"),
    title_font=dict(color=COP_LT, size=13, family="Inter"),
    hoverlabel=dict(bgcolor=NAVY_MD, bordercolor="rgba(184,115,51,0.35)",
                    font=dict(color=ICE, size=12)),
)

# ── LOAD DATA — new clean CSV ──
@st.cache_data(ttl=1)
def load_data():
    import os, glob
    # Find any CSV in the repo
    candidates = glob.glob("*.csv") + glob.glob("**/*.csv", recursive=False)
    for fname in ["lme_data.csv", "lme_data_final.csv", "lme_dashboard_data.csv"] + candidates:
        if os.path.exists(fname):
            df = pd.read_csv(fname, encoding="utf-8")
            df.columns = df.columns.str.strip().str.lstrip("\ufeff")
            # Normalize ALL possible old column names
            rename_map = {
                "ENTITIES":"ENTITY","Month Name":"MONTH_NAME","Month":"MONTH",
                "QTY Km":"QTY_KM","RC Needs Kg":"RC_KG","CC Needs Kg":"CC_KG",
                "ES mm":"ES_MM","AV INDEX":"AV_INDEX","TOTAL AMOUNT €":"TOTAL_AMOUNT",
                "LME SALES €/kg":"LME_SALES","BASIC LME  €/kg":"BASIC_LME",
                "UNIT PRICE €/km":"UNIT_PRICE","ADDED VALUE €/km":"ADDED_VALUE",
                "Fixation":"FIXATION","SPOOL TYPE":"SPOOL_TYPE","LME PROJECTS":"LME_PROJECTS",
                "CROSS SECTION mm":"CROSS_SECTION_MM","FAMILY & CS":"FAMILY_CS",
                "QTY_Km":"QTY_KM","RC_Needs_Kg":"RC_KG","CC_Needs_Kg":"CC_KG",
                "ES_mm":"ES_MM","TOTAL_AMOUNT":"TOTAL_AMOUNT",
                "LME_SALES_avg":"LME_SALES","BASIC_LME_avg":"BASIC_LME",
            }
            df = df.rename(columns={k:v for k,v in rename_map.items() if k in df.columns})
            
            # Fix ENTITY: if it contains commas it's the old broken column — rebuild from scratch
            if "ENTITY" in df.columns:
                df["ENTITY"] = df["ENTITY"].astype(str).str.split(",").str[0].str.strip()
            
            return df
    st.error("❌ No CSV data file found in repository.")
    st.stop()

df_raw = load_data()

# ── SIDEBAR ──
with st.sidebar:
    st.markdown("""<div style="text-align:center;padding:20px 0 14px;">
        <img src="https://raw.githubusercontent.com/Ouiam-Zemmouri/LME_Sales-Analysis/main/COFICAB.png"
             style="max-width:148px;border-radius:10px;
                    filter:drop-shadow(0 4px 14px rgba(184,115,51,0.25));"/>
    </div>""", unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.markdown("## 🔍 Filters")

    def mf(label, col, order=None):
        if col not in df_raw.columns: return []
        uniq = df_raw[col].dropna().astype(str).unique().tolist()
        vals = [v for v in order if v in uniq] if order else sorted(uniq)
        st.markdown(f'<p class="filter-label">{label}</p>', unsafe_allow_html=True)
        sel = st.multiselect("", vals, default=[], key=f"flt_{col}",
                             placeholder="All", label_visibility="collapsed")
        return sel if sel else vals

    def ms(label, col):
        if col not in df_raw.columns: return (0.0,1.0)
        s = df_raw[col].dropna()
        if s.empty: return (0.0,1.0)
        mn,mx = float(s.min()), float(s.max())
        if mn==mx: mx+=0.001
        st.markdown(f'<p class="filter-label">{label}</p>', unsafe_allow_html=True)
        return st.slider("",mn,mx,(mn,mx),key=f"sld_{col}",label_visibility="collapsed")

    # Entity: force only real entity values
    ent_vals = sorted(df_raw["ENTITY"].dropna().astype(str).unique().tolist())
    st.markdown('<p class="filter-label">Entity</p>', unsafe_allow_html=True)
    sel_ent = st.multiselect("", ent_vals, default=[], key="flt_ENTITY",
                              placeholder="All", label_visibility="collapsed")
    f_entity = sel_ent if sel_ent else ent_vals

    f_month  = mf("Month",          "MONTH_NAME", order=MONTH_ORDER)
    f_rm     = mf("Raw Material",   "RM")
    f_family = mf("Product Family", "FAMILY")
    f_group  = mf("Customer Group", "GROUPS")
    f_fix    = mf("Fixation",       "FIXATION")
    f_spool  = mf("Spool Type",     "SPOOL_TYPE")
    f_lmeprj = mf("LME Projects",   "LME_PROJECTS")
    st.markdown("---")

# ── PRE-FILTER (without LME sliders) to compute dynamic ranges ──
def ins(s,v): return s.astype(str).isin([str(x) for x in v])

df_pre = df_raw[
    ins(df_raw["ENTITY"],       f_entity)  &
    ins(df_raw["MONTH_NAME"],   f_month)   &
    ins(df_raw["RM"],           f_rm)      &
    ins(df_raw["FAMILY"],       f_family)  &
    ins(df_raw["GROUPS"],       f_group)   &
    ins(df_raw["FIXATION"],     f_fix)     &
    ins(df_raw["SPOOL_TYPE"],   f_spool)   &
    ins(df_raw["LME_PROJECTS"], f_lmeprj)
].copy()

# ── DYNAMIC MULTISELECT for LME values ──
with st.sidebar:
    def dyn_lme_select(label, col, data):
        vals = sorted(data[col].dropna().round(4).unique().tolist())
        vals_str = [str(v) for v in vals]
        st.markdown(f'<p class="filter-label">{label}</p>', unsafe_allow_html=True)
        sel = st.multiselect("", vals_str, default=[],
                             key=f"lme_ms_{col}", placeholder="All values",
                             label_visibility="collapsed")
        return [float(v) for v in sel] if sel else vals

    f_lme   = dyn_lme_select("LME Sales (€/kg)",  "LME_SALES",  df_pre)
    f_basic = dyn_lme_select("Basic LME (€/kg)",  "BASIC_LME",  df_pre)
    st.markdown("---")

# ── FULL FILTER ──
df = df_pre[
    df_pre["LME_SALES"].round(4).isin([round(v,4) for v in f_lme]) &
    df_pre["BASIC_LME"].round(4).isin([round(v,4) for v in f_basic])
].copy()

if df.empty:
    st.warning("⚠️ No data matches the selected filters. Please reset your filters.")
    st.stop()

# ── KPIs ──
TQ  = df["QTY_KM"].sum()
TCA = df["TOTAL_AMOUNT"].sum()
TRC = df["RC_KG"].sum()
TCC = df["CC_KG"].sum() if "CC_KG" in df.columns else 0
TON = TRC/1000
ALM = df["LME_SALES"].mean()
BLM = df["BASIC_LME"].mean()
AES = df["ES_MM"].sum()/TQ if TQ else 0
ARC = TRC/TQ if TQ else 0
ACC = TCC/TQ if TQ else 0
AAV = df["AV_INDEX"].sum()/TQ if TQ else 0

fix_agg = df.groupby("FIXATION").agg(
    Tonnage_T=("RC_KG",lambda x:x.sum()/1000),
    Qty_Km=("QTY_KM","sum"), CA=("TOTAL_AMOUNT","sum")).reset_index()

def kpi(col, label, val, unit=None, color=COPPER):
    col.markdown(f"""<div class="kpi-card" style="border-left-color:{color};">
      <div class="kpi-label" style="color:{color};">{label}</div>
      <div class="kpi-value" style="color:#e8edf5;">{val}</div>
      </div>""", unsafe_allow_html=True)

def sec(icon, title):
    st.markdown(f'<div class="section-header">{icon}&nbsp; {title}</div>', unsafe_allow_html=True)

def alay(fig, **kw):
    fig.update_layout(**{**LAY, **kw}); return fig

# ── TITLE ──
st.markdown("""<div class="title-banner">
  <h1>⚡ Sales Analysis 2026</h1>
  <p>COFICAB Kenitra · COFICAB Maroc</p>
</div>""", unsafe_allow_html=True)
st.caption(f"📊 **{len(df):,}** records · **{df['ENTITY'].nunique()}** entit{'y' if df['ENTITY'].nunique()==1 else 'ies'} · **{df['MONTH_NAME'].nunique()}** month(s)")

tab1,tab2,tab3,tab4,tab5,tab6,tab7,tab8 = st.tabs([
    "📊 KPI Summary","📈 LME Overview","🏭 Fixation Analysis","🔬 Deep Dive",
    "💰 Profitability","🌍 Customer Portfolio","🎯 Executive Summary","📋 Raw Data"])

# ════ TAB 1 ════
with tab1:
    sec("📊","Global Performance Indicators")
    c1,c2,c3,c4,c5 = st.columns(5)
    kpi(c1,"Total Revenue (€)",    f"{TCA/1e6:.2f}M",   "EUR",         COPPER)
    kpi(c2,"Total Volume (km)",     f"{TQ/1e6:.2f}M",    "km",          BLUE)
    kpi(c3,"RC Tonnage (T)",        f"{TON:,.0f}",       "Tonnes",      TEAL)
    kpi(c4,"Avg All-In LME (€/kg)", f"{ALM:.2f}",       "€/kg",        COP_LT)
    kpi(c5,"Avg Basic LME (€/kg)",  f"{BLM:.2f}",       "€/kg",        GOLD)

    st.markdown("<br>", unsafe_allow_html=True)
    c6,c7,c8,c9 = st.columns(4)
    kpi(c6,"Avg Cross Section (mm)", f"{AES:.2f}",      "mm",          SLATE)
    kpi(c7,"Avg RC (kg/km)",         f"{ARC:.2f}",      "kg/km",       COPPER)
    kpi(c8,"Avg CC (kg/km)",         f"{ACC:.2f}",      "kg/km",       BLUE)
    kpi(c9,"Avg Added Value (€/km)", f"{AAV:.2f}",      "€/km",        TEAL)

    st.markdown("<br>", unsafe_allow_html=True)
    sec("🏢","Revenue & Volume by Entity")
    ent = df.groupby("ENTITY").agg(CA=("TOTAL_AMOUNT","sum"),Qty=("QTY_KM","sum")).reset_index()
    cl,cr = st.columns(2)
    with cl:
        fig = go.Figure()
        for i,row in ent.iterrows():
            c = ENT_C[i%2]
            fig.add_trace(go.Bar(name=row["ENTITY"],x=[row["ENTITY"]],y=[row["CA"]],
                marker=dict(color=c,opacity=0.9,line=dict(color=c,width=1)),
                text=[f"€{row['CA']/1e6:.2f}M"],textposition="outside",
                textfont=dict(color=c,size=13)))
        alay(fig,title="Revenue by Entity (€)",showlegend=False)
        st.plotly_chart(fig,use_container_width=True)
    with cr:
        fig2 = go.Figure()
        c2s = [TEAL,GOLD]
        for i,row in ent.iterrows():
            c = c2s[i%2]
            fig2.add_trace(go.Bar(name=row["ENTITY"],x=[row["ENTITY"]],y=[row["Qty"]],
                marker=dict(color=c,opacity=0.9,line=dict(color=c,width=1)),
                text=[f"{row['Qty']:,.0f} km"],textposition="outside",
                textfont=dict(color=c,size=13)))
        alay(fig2,title="Volume by Entity (km)",showlegend=False)
        st.plotly_chart(fig2,use_container_width=True)

    sec("📐","Cross Section Summary by Entity")
    es_ent = df.groupby("ENTITY").apply(lambda g: pd.Series({
        "Total Qty (km)":        g["QTY_KM"].sum(),
        "Avg Cross Section (mm)":g["ES_MM"].sum()/g["QTY_KM"].sum() if g["QTY_KM"].sum() else 0,
        "Avg RC (kg/km)":        g["RC_KG"].sum()/g["QTY_KM"].sum() if g["QTY_KM"].sum() else 0,
        "Avg CC (kg/km)":        g["CC_KG"].sum()/g["QTY_KM"].sum() if g["QTY_KM"].sum() else 0,
        "Avg Added Value (€/km)":g["AV_INDEX"].sum()/g["QTY_KM"].sum() if g["QTY_KM"].sum() else 0,
    })).reset_index()
    st.dataframe(es_ent.style
        .format({"Total Qty (km)":"{:,.2f}","Avg Cross Section (mm)":"{:.2f}",
                 "Avg RC (kg/km)":"{:.2f}","Avg CC (kg/km)":"{:.2f}",
                 "Avg Added Value (€/km)":"€{:.2f}"})
        .set_properties(**{"background-color":NAVY_MD,"color":ICE}),
        use_container_width=True, hide_index=True)

# ════ TAB 2 ════
with tab2:
    sec("📈","Monthly LME Evolution")
    monthly = df.groupby(["MONTH","MONTH_NAME","ENTITY"]).agg(
        LME_Sales=("LME_SALES","mean"), LME_Min=("LME_SALES","min"), LME_Max=("LME_SALES","max"),
        Basic_LME=("BASIC_LME","mean"), Basic_Min=("BASIC_LME","min"), Basic_Max=("BASIC_LME","max"),
        Qty_Km=("QTY_KM","sum"), CA=("TOTAL_AMOUNT","sum")).reset_index()
    monthly["MONTH_NAME"] = pd.Categorical(monthly["MONTH_NAME"],categories=MONTH_ORDER,ordered=True)
    monthly = monthly.sort_values(["MONTH_NAME","ENTITY"])

    ec1 = {"COFICAB Kenitra":BLUE, "COFICAB Maroc":COPPER}
    ec2 = {"COFICAB Kenitra":TEAL, "COFICAB Maroc":GOLD}
    fl1 = {"COFICAB Kenitra":"rgba(43,108,176,0.08)","COFICAB Maroc":"rgba(184,115,51,0.08)"}
    fl2 = {"COFICAB Kenitra":"rgba(14,165,160,0.08)","COFICAB Maroc":"rgba(212,160,23,0.08)"}

    def band(mdf,y,ymn,ymx,cols,fills,title,sym="circle"):
        fig = go.Figure()
        for ent,grp in mdf.groupby("ENTITY"):
            c=cols.get(ent,COPPER); f=fills.get(ent,"rgba(184,115,51,0.08)")
            fig.add_trace(go.Scatter(
                x=list(grp["MONTH_NAME"])+list(grp["MONTH_NAME"])[::-1],
                y=list(grp[ymx])+list(grp[ymn])[::-1],
                fill="toself",fillcolor=f,line=dict(color="rgba(0,0,0,0)"),
                showlegend=False,hoverinfo="skip"))
            fig.add_trace(go.Scatter(
                x=grp["MONTH_NAME"],y=grp[y],mode="lines+markers+text",name=ent,
                line=dict(color=c,width=2.5),
                marker=dict(size=10,symbol=sym,color=c,line=dict(width=2,color="rgba(255,255,255,0.25)")),
                text=[f"{v:.4f}" for v in grp[y]],
                textposition="top center",textfont=dict(size=9,color=c)))
        alay(fig,title=title); return fig

    cl,cr = st.columns(2)
    with cl:
        st.markdown("##### All-In LME Sales (€/kg)")
        st.plotly_chart(band(monthly,"LME_Sales","LME_Min","LME_Max",ec1,fl1,"All-In LME €/kg — Monthly Trend"),use_container_width=True)
    with cr:
        st.markdown("##### Basic LME (€/kg)")
        st.plotly_chart(band(monthly,"Basic_LME","Basic_Min","Basic_Max",ec2,fl2,"Basic LME €/kg — Monthly Trend","diamond"),use_container_width=True)

    sec("📊","All-In vs Basic — Combined Monthly View")
    mall = df.groupby(["MONTH","MONTH_NAME"]).agg(
        LME_Sales=("LME_SALES","mean"),Basic_LME=("BASIC_LME","mean")).reset_index()
    mall["MONTH_NAME"] = pd.Categorical(mall["MONTH_NAME"],categories=MONTH_ORDER,ordered=True)
    mall = mall.sort_values("MONTH_NAME")
    fig3 = go.Figure()
    for cn,color,sym,pos,name,fill in [
        ("LME_Sales",BLUE,  "circle", "top center",   "All-In LME €/kg","rgba(43,108,176,0.07)"),
        ("Basic_LME",COPPER,"diamond","bottom center", "Basic LME €/kg", "rgba(184,115,51,0.07)"),
    ]:
        fig3.add_trace(go.Scatter(
            x=mall["MONTH_NAME"],y=mall[cn],name=name,mode="lines+markers+text",
            line=dict(color=color,width=3),
            marker=dict(size=11,symbol=sym,color=color,line=dict(width=2,color="rgba(255,255,255,0.2)")),
            fill="tozeroy",fillcolor=fill,
            text=[f"<b>{v:.4f}</b>" for v in mall[cn]],
            textposition=pos,textfont=dict(size=10,color=color)))
    alay(fig3,title="All-In LME vs Basic LME — Monthly Comparison (All Entities)")
    st.plotly_chart(fig3,use_container_width=True)

    sec("🔧","LME by Fixation Type")
    bfm = df.groupby(["MONTH","MONTH_NAME","FIXATION"]).agg(
        LME_Sales=("LME_SALES","mean"),Qty_Km=("QTY_KM","sum")).reset_index()
    bfm["MONTH_NAME"] = pd.Categorical(bfm["MONTH_NAME"],categories=MONTH_ORDER,ordered=True)
    bfm = bfm.sort_values("MONTH_NAME")
    cl2,cr2 = st.columns(2)
    with cl2:
        figfx = go.Figure()
        for fix,grp in bfm.groupby("FIXATION"):
            cc=FIX_C.get(fix,SLATE)
            figfx.add_trace(go.Scatter(x=grp["MONTH_NAME"],y=grp["LME_Sales"],
                mode="lines+markers+text",name=fix,line=dict(color=cc,width=2.5),
                marker=dict(size=9,color=cc,line=dict(width=2,color="rgba(255,255,255,0.2)")),
                text=[f"{v:.4f}" for v in grp["LME_Sales"]],
                textposition="top center",textfont=dict(size=8,color=cc)))
        alay(figfx,title="All-In LME €/kg by Fixation Type")
        st.plotly_chart(figfx,use_container_width=True)
    with cr2:
        figfx2 = go.Figure()
        for fix,grp in bfm.groupby("FIXATION"):
            cc=FIX_C.get(fix,SLATE)
            figfx2.add_trace(go.Bar(x=grp["MONTH_NAME"],y=grp["Qty_Km"],name=fix,
                marker=dict(color=cc,opacity=0.88,line=dict(color=cc,width=1)),
                text=[f"{v/1000:.1f}K" for v in grp["Qty_Km"]],textposition="auto"))
        alay(figfx2,barmode="group",title="Volume (km) by Fixation Type")
        st.plotly_chart(figfx2,use_container_width=True)

    sec("📦","LME Performance by Customer Group")
    gd = df.groupby("GROUPS").agg(LME_Sales=("LME_SALES","mean"),Basic_LME=("BASIC_LME","mean"),
          CA=("TOTAL_AMOUNT","sum")).reset_index().sort_values("CA",ascending=False)
    figgrp = go.Figure()
    figgrp.add_trace(go.Bar(x=gd["GROUPS"],y=gd["LME_Sales"],name="All-In LME €/kg",
        marker=dict(color=BLUE,opacity=0.92,line=dict(color="#1e4d8c",width=1)),
        text=[f"{v:.4f}" for v in gd["LME_Sales"]],textposition="outside",
        textfont=dict(size=8,color=ICE)))
    figgrp.add_trace(go.Bar(x=gd["GROUPS"],y=gd["Basic_LME"],name="Basic LME €/kg",
        marker=dict(color=COPPER,opacity=0.92,line=dict(color="#8a5520",width=1)),
        text=[f"{v:.4f}" for v in gd["Basic_LME"]],textposition="outside",
        textfont=dict(size=8,color=COP_XL)))
    y_max = max(list(gd["LME_Sales"])+list(gd["Basic_LME"]))*1.10
    alay(figgrp,barmode="group",title="Average LME Prices by Customer Group",height=500)
    figgrp.update_yaxes(range=[0,y_max],dtick=0.5,
        gridcolor="rgba(255,255,255,0.03)",zeroline=False,
        tickfont=dict(color="#3a5070"),title_text="€/kg")
    figgrp.update_xaxes(tickangle=-35,tickfont=dict(color=SLATE,size=10))
    figgrp.update_layout(legend=dict(orientation="h",yanchor="bottom",y=1.02,
        xanchor="right",x=1,bgcolor="rgba(13,30,58,0.9)",
        bordercolor="rgba(184,115,51,0.2)",borderwidth=1,font=dict(color=SLATE,size=11)))
    st.plotly_chart(figgrp,use_container_width=True)

# ════ TAB 3 ════
with tab3:
    sec("🔧","Fixation Breakdown — M-1 · 3M-1 · 3M-2")
    fix_kc=[COPPER,BLUE,TEAL,GOLD]
    fcols = st.columns(len(fix_agg)+1)
    for i,row in fix_agg.iterrows():
        pct=row["Qty_Km"]/TQ*100 if TQ else 0; cc=fix_kc[i%len(fix_kc)]
        fcols[i].markdown(f"""<div class="kpi-card" style="border-left-color:{cc};">
          <div class="kpi-label" style="color:{cc};">{row['FIXATION']}</div>
          <div class="kpi-value" style="color:#e8edf5;">{row['Tonnage_T']:,.0f}</div>
          <div class="kpi-sub" style="color:{cc};opacity:0.6;font-size:0.65rem;">{row['Qty_Km']:,.0f} km · {pct:.1f}%</div>
          </div>""",unsafe_allow_html=True)
    fcols[-1].markdown(f"""<div class="kpi-card" style="border-left-color:{GOLD};">
      <div class="kpi-label" style="color:{GOLD};">⚡ TOTAL</div>
      <div class="kpi-value" style="color:#e8edf5;">{TON:,.0f}</div>
      <div class="kpi-sub" style="color:{GOLD};opacity:0.6;font-size:0.65rem;">{TQ:,.0f} km · 100%</div>
      </div>""",unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)
    colA,colB,colC = st.columns(3)
    for col_ui,(vc,title,colors) in zip([colA,colB,colC],[
        ("Tonnage_T","Tonnage (T) by Fixation",[COPPER,BLUE,TEAL]),
        ("Qty_Km",   "Volume (km) by Fixation",[BLUE,TEAL,GOLD]),
        ("CA",       "Revenue (€) by Fixation", [TEAL,COPPER,BLUE]),
    ]):
        fd=px.pie(fix_agg,values=vc,names="FIXATION",hole=0.58,title=title,color_discrete_sequence=colors)
        fd.update_traces(textposition="outside",textinfo="label+percent",
                         marker=dict(line=dict(color=NAVY,width=2)))
        alay(fd); col_ui.plotly_chart(fd,use_container_width=True)

    fe=df.groupby(["FIXATION","ENTITY"]).agg(
        Tonnage_T=("RC_KG",lambda x:x.sum()/1000),Qty_Km=("QTY_KM","sum"),CA=("TOTAL_AMOUNT","sum")).reset_index()
    figfe=px.bar(fe,x="FIXATION",y="Tonnage_T",color="ENTITY",barmode="group",text_auto=".1f",
                 title="Tonnage (T) by Fixation & Entity",color_discrete_sequence=ENT_C,labels={"Tonnage_T":"Tonnage (T)"})
    alay(figfe); st.plotly_chart(figfe,use_container_width=True)

    sec("📋","Fixation Detail Table")
    fs=df.groupby("FIXATION").agg(**{
        "Tonnage (T)":   ("RC_KG",lambda x:round(x.sum()/1000,2)),
        "Volume (km)":   ("QTY_KM",lambda x:round(x.sum(),2)),
        "Revenue (€)":   ("TOTAL_AMOUNT",lambda x:round(x.sum(),2)),
        "Avg All-In LME":("LME_SALES",lambda x:round(x.mean(),4)),
        "Avg Basic LME": ("BASIC_LME",lambda x:round(x.mean(),4)),
    }).reset_index()
    fs=pd.concat([fs,pd.DataFrame([{"FIXATION":"TOTAL","Tonnage (T)":round(TON,2),
        "Volume (km)":round(TQ,2),"Revenue (€)":round(TCA,2),
        "Avg All-In LME":round(ALM,4),"Avg Basic LME":round(BLM,4)}])],ignore_index=True)
    st.dataframe(fs.style
        .format({"Tonnage (T)":"{:,.0f}","Volume (km)":"{:,.0f}","Revenue (€)":"€{:,.2f}",
                 "Avg All-In LME":"{:.2f}","Avg Basic LME":"{:.2f}"})
        .set_properties(**{"background-color":NAVY_MD,"color":ICE}),
        use_container_width=True,hide_index=True)

# ════ TAB 4 ════
with tab4:
    sec("🔬","Product Analysis — Family & Cross Section")
    dim_col = st.radio("Group by",["FAMILY_CS","FAMILY","CROSS_SECTION_MM"],horizontal=True,key="dim_r")
    top_n   = st.slider("Top N references",5,30,15,key="topn_s")
    dim_lbl = {"FAMILY_CS":"Family & CS","FAMILY":"Family","CROSS_SECTION_MM":"Cross Section"}.get(dim_col,"Family & CS")

    if dim_col not in df.columns:
        st.warning(f"Column '{dim_col}' not found.")
    else:
        fam=df.groupby(dim_col).agg(CA=("TOTAL_AMOUNT","sum"),Qty_Km=("QTY_KM","sum"),
            Tonnage_T=("RC_KG",lambda x:x.sum()/1000)).reset_index().sort_values("CA",ascending=False).head(top_n)
        cl,cr=st.columns(2)
        with cl:
            fig_f=px.bar(fam,x=dim_col,y="CA",title=f"Revenue (€) — Top {top_n} {dim_lbl}",
                color="CA",color_continuous_scale=[NAVY,"#0d1e3a",NAVY_LT,BLUE,"#60a5fa"],text_auto=".2s")
            alay(fig_f,coloraxis_showscale=False,xaxis_tickangle=-45)
            st.plotly_chart(fig_f,use_container_width=True)
        with cr:
            fig_f2=px.bar(fam,x=dim_col,y="Tonnage_T",title=f"Tonnage (T) — Top {top_n} {dim_lbl}",
                color="Tonnage_T",color_continuous_scale=[NAVY,"#1a1000","#8a5520",COPPER,COP_LT],text_auto=".1f")
            alay(fig_f2,coloraxis_showscale=False,xaxis_tickangle=-45)
            st.plotly_chart(fig_f2,use_container_width=True)

        sec("📋",f"Full {dim_lbl} Reference Table")
        fd2=df.groupby(dim_col).agg(CA=("TOTAL_AMOUNT","sum"),Qty_Km=("QTY_KM","sum"),
            Tonnage_T=("RC_KG",lambda x:x.sum()/1000),
            Avg_LME=("LME_SALES","mean"),Avg_Basic=("BASIC_LME","mean")).reset_index().sort_values("CA",ascending=False)
        fd2.columns=[dim_lbl,"Revenue (€)","Volume (km)","Tonnage (T)","Avg All-In LME","Avg Basic LME"]
        st.dataframe(fd2.style
            .format({"Revenue (€)":"€{:,.2f}","Volume (km)":"{:,.0f}","Tonnage (T)":"{:,.0f}",
                     "Avg All-In LME":"{:.2f}","Avg Basic LME":"{:.2f}"})
            .set_properties(**{"background-color":NAVY_MD,"color":ICE}),
            use_container_width=True,hide_index=True,height=400)

    sec("🧱","Raw Material (RM) Breakdown")
    rm=df.groupby("RM").agg(Qty_Km=("QTY_KM","sum"),Tonnage_T=("RC_KG",lambda x:x.sum()/1000)).reset_index()
    cl2,cr2=st.columns(2)
    for col_ui,vc,title,colors in [
        (cl2,"Qty_Km",   "Volume (km) by Raw Material",[BLUE,TEAL,COPPER,GOLD]),
        (cr2,"Tonnage_T","Tonnage (T) by Raw Material",[COPPER,TEAL,BLUE,GOLD]),
    ]:
        frm=px.pie(rm,values=vc,names="RM",hole=0.55,title=title,color_discrete_sequence=colors)
        frm.update_traces(marker=dict(line=dict(color=NAVY,width=2)))
        alay(frm); col_ui.plotly_chart(frm,use_container_width=True)

    sec("🪝","Spool Type Analysis by Entity")
    sp=df.groupby(["SPOOL_TYPE","ENTITY"]).agg(Qty_Km=("QTY_KM","sum")).reset_index()
    figsp=px.bar(sp,x="SPOOL_TYPE",y="Qty_Km",color="ENTITY",barmode="group",text_auto=".2s",
                 title="Volume (km) by Spool Type & Entity",
                 color_discrete_sequence=ENT_C,labels={"Qty_Km":"Volume (km)"})
    alay(figsp); st.plotly_chart(figsp,use_container_width=True)

# ════ TAB 8 ════
with tab8:
    sec("📋","Filtered Dataset")
    search=st.text_input("","",placeholder="🔍  Search across all columns...",label_visibility="collapsed")
    cols_sel=st.multiselect("Select columns",list(df.columns),default=list(df.columns))
    disp=df[cols_sel].reset_index(drop=True) if cols_sel else df.reset_index(drop=True)
    if search:
        sc=disp.select_dtypes("object").columns
        if len(sc):
            mk=disp[sc].apply(lambda c:c.str.contains(search,case=False,na=False)).any(axis=1)
            disp=disp[mk]
    st.caption(f"**{len(disp):,}** rows displayed")
    st.dataframe(disp,use_container_width=True,height=520)

st.markdown(f"""<div style="text-align:center;color:#1a2e4a;font-size:0.72rem;
  margin-top:48px;padding:16px;border-top:1px solid rgba(184,115,51,0.12);">
  LME Sales Analysis 2026 &nbsp;·&nbsp; COFICAB Kenitra &amp; COFICAB Maroc &nbsp;·&nbsp; Confidential
</div>""",unsafe_allow_html=True)

# ════════════════════════════════════════════
# TAB 5 — PROFITABILITY ANALYSIS
# ════════════════════════════════════════════
with tab5:
    sec("💰","Profitability Analysis")

    # ── KPIs
    spread_avg = ALM - BLM
    av_total   = df["AV_INDEX"].sum()
    av_per_km  = AAV
    rev_per_ton= TCA / TON if TON else 0

    c1,c2,c3,c4 = st.columns(4)
    kpi(c1,"Avg Spread All-In vs Basic (€/kg)", f"{spread_avg:.2f}", "€/kg", COPPER)
    kpi(c2,"Total Added Value (€)",             f"€{av_total/1e6:.2f}M",  "EUR",  BLUE)
    kpi(c3,"Avg Added Value (€/km)",            f"{av_per_km:.2f}",       "€/km", TEAL)
    kpi(c4,"Revenue per Tonne (€/T)",           f"€{rev_per_ton:,.0f}",   "€/T",  GOLD)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Spread evolution by month
    sec("📉","LME Spread (All-In vs Basic) — Monthly Evolution")
    spread_m = df.groupby(["MONTH","MONTH_NAME"]).agg(
        Spread=("LME_SALES","mean"), Basic=("BASIC_LME","mean")).reset_index()
    spread_m["Spread_diff"] = spread_m["Spread"] - spread_m["Basic"]
    spread_m["MONTH_NAME"]  = pd.Categorical(spread_m["MONTH_NAME"], categories=MONTH_ORDER, ordered=True)
    spread_m = spread_m.sort_values("MONTH_NAME")

    fig_sp = go.Figure()
    fig_sp.add_trace(go.Bar(
        x=spread_m["MONTH_NAME"], y=spread_m["Spread_diff"],
        name="Spread (All-In − Basic)",
        marker=dict(color=[COPPER if v>=0 else "#f43f5e" for v in spread_m["Spread_diff"]],
                    opacity=0.9, line=dict(width=1)),
        text=[f"{v:.2f}" for v in spread_m["Spread_diff"]],
        textposition="outside", textfont=dict(color=ICE, size=11)))
    fig_sp.add_trace(go.Scatter(
        x=spread_m["MONTH_NAME"], y=spread_m["Spread_diff"],
        mode="lines+markers", name="Trend",
        line=dict(color=BLUE, width=2, dash="dot"),
        marker=dict(size=8, color=BLUE)))
    alay(fig_sp, title="Monthly LME Spread (All-In − Basic €/kg)", height=380)
    st.plotly_chart(fig_sp, use_container_width=True)

    # ── Added Value by Group & Entity
    sec("📊","Added Value (€/km) by Customer Group & Entity")
    cl, cr = st.columns(2)

    with cl:
        av_group = df.groupby("GROUPS").agg(
            AV_km=("AV_INDEX","sum"), QTY=("QTY_KM","sum"),
            CA=("TOTAL_AMOUNT","sum")).reset_index()
        av_group["AV_per_km"] = av_group["AV_km"] / av_group["QTY"]
        av_group = av_group.sort_values("AV_per_km", ascending=True).tail(15)

        fig_av = go.Figure(go.Bar(
            x=av_group["AV_per_km"], y=av_group["GROUPS"],
            orientation="h",
            marker=dict(
                color=av_group["AV_per_km"],
                colorscale=[[0,NAVY_MD],[0.5,BLUE],[1,COPPER]],
                showscale=False, line=dict(width=0)),
            text=[f"€{v:.2f}" for v in av_group["AV_per_km"]],
            textposition="outside", textfont=dict(color=ICE, size=10)))
        alay(fig_av, title="Added Value (€/km) — Top 15 Customer Groups", height=450,
             xaxis=dict(title="€/km", gridcolor="rgba(255,255,255,0.03)",
                        tickfont=dict(color="#3a5070")),
             yaxis=dict(tickfont=dict(color=ICE, size=10), gridcolor="rgba(255,255,255,0.02)"))
        st.plotly_chart(fig_av, use_container_width=True)

    with cr:
        av_fam = df.groupby("FAMILY").agg(
            AV_km=("AV_INDEX","sum"), QTY=("QTY_KM","sum")).reset_index()
        av_fam["AV_per_km"] = av_fam["AV_km"] / av_fam["QTY"]
        av_fam = av_fam.sort_values("AV_per_km", ascending=False).head(15)

        fig_avf = px.bar(av_fam, x="FAMILY", y="AV_per_km",
            title="Added Value (€/km) — Top 15 Product Families",
            color="AV_per_km",
            color_continuous_scale=[NAVY_MD, BLUE, COPPER],
            text_auto=".2f", labels={"AV_per_km":"€/km"})
        alay(fig_avf, coloraxis_showscale=False, xaxis_tickangle=-45)
        st.plotly_chart(fig_avf, use_container_width=True)

    # ── Profitability by Fixation × Month
    sec("🔧","Spread & Added Value by Fixation Type")
    fix_prof = df.groupby(["MONTH_NAME","FIXATION"]).agg(
        LME=("LME_SALES","mean"), Basic=("BASIC_LME","mean"),
        AV=("AV_INDEX","sum"), QTY=("QTY_KM","sum")).reset_index()
    fix_prof["Spread"]   = fix_prof["LME"] - fix_prof["Basic"]
    fix_prof["AV_km"]    = fix_prof["AV"] / fix_prof["QTY"]
    fix_prof["MONTH_NAME"] = pd.Categorical(fix_prof["MONTH_NAME"], categories=MONTH_ORDER, ordered=True)
    fix_prof = fix_prof.sort_values("MONTH_NAME")

    cl2, cr2 = st.columns(2)
    with cl2:
        fig_fsp = go.Figure()
        for fix, grp in fix_prof.groupby("FIXATION"):
            cc = FIX_C.get(fix, SLATE)
            fig_fsp.add_trace(go.Scatter(
                x=grp["MONTH_NAME"], y=grp["Spread"],
                mode="lines+markers+text", name=fix,
                line=dict(color=cc, width=2.5),
                marker=dict(size=9, color=cc),
                text=[f"{v:.2f}" for v in grp["Spread"]],
                textposition="top center", textfont=dict(size=9, color=cc)))
        alay(fig_fsp, title="LME Spread (€/kg) by Fixation Type")
        st.plotly_chart(fig_fsp, use_container_width=True)

    with cr2:
        fig_favk = go.Figure()
        for fix, grp in fix_prof.groupby("FIXATION"):
            cc = FIX_C.get(fix, SLATE)
            fig_favk.add_trace(go.Scatter(
                x=grp["MONTH_NAME"], y=grp["AV_km"],
                mode="lines+markers+text", name=fix,
                line=dict(color=cc, width=2.5),
                marker=dict(size=9, color=cc),
                text=[f"{v:.2f}" for v in grp["AV_km"]],
                textposition="top center", textfont=dict(size=9, color=cc)))
        alay(fig_favk, title="Added Value (€/km) by Fixation Type")
        st.plotly_chart(fig_favk, use_container_width=True)


# ════════════════════════════════════════════
# TAB 6 — CUSTOMER PORTFOLIO
# ════════════════════════════════════════════
with tab6:
    sec("🌍","Customer Portfolio Analysis")

    # ── Pareto 80/20
    sec("📊","Pareto Analysis — Revenue Concentration")
    pareto = df.groupby("GROUPS").agg(
        CA=("TOTAL_AMOUNT","sum"), Qty=("QTY_KM","sum"),
        Tonnage=("RC_KG",lambda x:x.sum()/1000)).reset_index()
    pareto = pareto.sort_values("CA", ascending=False).reset_index(drop=True)
    pareto["CA_cum_pct"] = pareto["CA"].cumsum() / pareto["CA"].sum() * 100
    pareto["CA_pct"]     = pareto["CA"] / pareto["CA"].sum() * 100
    pareto["Rank"]       = pareto.index + 1

    fig_par = go.Figure()
    fig_par.add_trace(go.Bar(
        x=pareto["GROUPS"], y=pareto["CA_pct"],
        name="Revenue Share (%)",
        marker=dict(
            color=pareto["CA_pct"],
            colorscale=[[0,NAVY_LT],[0.4,BLUE],[1,COPPER]],
            showscale=False, line=dict(width=0)),
        text=[f"{v:.1f}%" for v in pareto["CA_pct"]],
        textposition="outside", textfont=dict(color=ICE, size=9)))
    fig_par.add_trace(go.Scatter(
        x=pareto["GROUPS"], y=pareto["CA_cum_pct"],
        name="Cumulative %", yaxis="y2",
        mode="lines+markers",
        line=dict(color=COPPER, width=2.5),
        marker=dict(size=7, color=COPPER)))
    alay(fig_par,
        title="Customer Revenue Concentration — Pareto Analysis",
        height=450,
        yaxis=dict(title="Revenue Share (%)", gridcolor="rgba(255,255,255,0.03)",
                   tickfont=dict(color="#3a5070")),
        yaxis2=dict(title="Cumulative %", overlaying="y", side="right",
                    range=[0,105], ticksuffix="%",
                    gridcolor="rgba(0,0,0,0)", tickfont=dict(color=COPPER)),
        xaxis=dict(tickangle=-35, tickfont=dict(color=SLATE, size=10)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    # Add 80% reference line
    fig_par.add_hline(y=80, yref="y2", line_dash="dash",
                      line_color="rgba(244,63,94,0.6)", line_width=1.5,
                      annotation_text="80%", annotation_font_color="#f43f5e")
    st.plotly_chart(fig_par, use_container_width=True)

    # ── Heatmap customers × months
    sec("🌡️","Revenue Heatmap — Customer Groups × Months")
    hmap = df.groupby(["GROUPS","MONTH_NAME"]).agg(CA=("TOTAL_AMOUNT","sum")).reset_index()
    hmap_pivot = hmap.pivot(index="GROUPS", columns="MONTH_NAME", values="CA").fillna(0)
    # Sort months
    cols_sorted = [m for m in MONTH_ORDER if m in hmap_pivot.columns]
    hmap_pivot  = hmap_pivot[cols_sorted]
    # Sort groups by total
    hmap_pivot  = hmap_pivot.loc[hmap_pivot.sum(axis=1).sort_values(ascending=False).index]

    fig_hm = go.Figure(go.Heatmap(
        z=hmap_pivot.values / 1e6,
        x=hmap_pivot.columns.tolist(),
        y=hmap_pivot.index.tolist(),
        colorscale=[[0,NAVY_MD],[0.3,NAVY_LT],[0.6,BLUE],[1,COPPER]],
        text=[[f"€{v:.2f}M" for v in row] for row in hmap_pivot.values/1e6],
        texttemplate="%{text}",
        textfont=dict(color=WHITE, size=10),
        hoverongaps=False,
        colorbar=dict(title="Revenue (M€)", tickfont=dict(color=SLATE))))
    alay(fig_hm, title="Revenue (M€) — Customer Groups × Months", height=600,
         xaxis=dict(tickfont=dict(color=ICE, size=12)),
         yaxis=dict(tickfont=dict(color=ICE, size=10)))
    st.plotly_chart(fig_hm, use_container_width=True)

    # ── Customer ranking table
    sec("🏆","Customer Ranking — Full Scorecard")
    rank = df.groupby("GROUPS").agg(
        Revenue=("TOTAL_AMOUNT","sum"),
        Volume_km=("QTY_KM","sum"),
        Tonnage_T=("RC_KG",lambda x:x.sum()/1000),
        Avg_LME=("LME_SALES","mean"),
        Avg_Basic=("BASIC_LME","mean"),
        Avg_AV=("AV_INDEX",lambda x: x.sum()/df.loc[x.index,"QTY_KM"].sum()
                if df.loc[x.index,"QTY_KM"].sum() else 0),
    ).reset_index().sort_values("Revenue", ascending=False).reset_index(drop=True)
    rank.index = rank.index + 1
    rank["Revenue Share (%)"] = (rank["Revenue"] / rank["Revenue"].sum() * 100).round(1)
    rank["Spread (€/kg)"]     = (rank["Avg_LME"] - rank["Avg_Basic"]).round(2)
    rank = rank.rename(columns={
        "GROUPS":"Customer Group","Revenue":"Revenue (€)","Volume_km":"Volume (km)",
        "Tonnage_T":"Tonnage (T)","Avg_LME":"Avg All-In LME","Avg_Basic":"Avg Basic LME",
        "Avg_AV":"Avg AV (€/km)"})
    st.dataframe(rank[[
        "Customer Group","Revenue (€)","Revenue Share (%)","Volume (km)",
        "Tonnage (T)","Avg All-In LME","Avg Basic LME","Spread (€/kg)","Avg AV (€/km)"
    ]].style
        .format({"Revenue (€)":"€{:,.0f}","Revenue Share (%)":"{:.1f}%",
                 "Volume (km)":"{:,.0f}","Tonnage (T)":"{:,.0f}",
                 "Avg All-In LME":"{:.2f}","Avg Basic LME":"{:.2f}",
                 "Spread (€/kg)":"{:.2f}","Avg AV (€/km)":"€{:.2f}"})
        .set_properties(**{"background-color":NAVY_MD,"color":ICE})
        .bar(subset=["Revenue Share (%)"], color="rgba(184,115,51,0.3)"),
        use_container_width=True, height=500)


# ════════════════════════════════════════════
# TAB 7 — EXECUTIVE SUMMARY
# ════════════════════════════════════════════
with tab7:
    sec("🎯","Executive Summary — Sales Performance 2026")

    # ── Monthly scorecard
    scorecard = df.groupby(["MONTH","MONTH_NAME"]).agg(
        Revenue=("TOTAL_AMOUNT","sum"),
        Volume=("QTY_KM","sum"),
        Tonnage=("RC_KG",lambda x:x.sum()/1000),
        LME=("LME_SALES","mean"),
        Basic=("BASIC_LME","mean"),
        AV=("AV_INDEX","sum"),
        QTY=("QTY_KM","sum"),
    ).reset_index()
    scorecard["Spread"]     = scorecard["LME"] - scorecard["Basic"]
    scorecard["AV_km"]      = scorecard["AV"] / scorecard["QTY"]
    scorecard["Rev_share"]  = scorecard["Revenue"] / scorecard["Revenue"].sum() * 100
    scorecard["MONTH_NAME"] = pd.Categorical(scorecard["MONTH_NAME"], categories=MONTH_ORDER, ordered=True)
    scorecard = scorecard.sort_values("MONTH_NAME")

    # ── 4 sparkline KPIs
    sec("📅","Monthly Scorecard")
    fig_sc = go.Figure()
    metrics = [
        ("Revenue (M€)",  scorecard["Revenue"]/1e6,   COPPER, "y1"),
        ("Volume (Mkm)",  scorecard["Volume"]/1e6,    BLUE,   "y2"),
        ("LME (€/kg)",    scorecard["LME"],           TEAL,   "y3"),
        ("Spread (€/kg)", scorecard["Spread"],        GOLD,   "y4"),
    ]
    # Use subplots via make_subplots for clean sparklines
    from plotly.subplots import make_subplots
    fig_sc = make_subplots(rows=2, cols=2,
        subplot_titles=["Revenue (M€)","Volume (M km)","All-In LME (€/kg)","LME Spread (€/kg)"],
        vertical_spacing=0.18, horizontal_spacing=0.1)

    def sparkline(x, y, color, row, col, name):
        fig_sc.add_trace(go.Scatter(
            x=x, y=y, mode="lines+markers+text", name=name,
            line=dict(color=color, width=3),
            marker=dict(size=10, color=color,
                        line=dict(width=2, color="rgba(255,255,255,0.2)")),
            text=[f"{v:.2f}" for v in y],
            textposition="top center", textfont=dict(size=9, color=color),
            fill="tozeroy", fillcolor=f"rgba(43,108,176,0.07)"),
            row=row, col=col)

    sparkline(scorecard["MONTH_NAME"], scorecard["Revenue"]/1e6,   COPPER, 1, 1, "Revenue")
    sparkline(scorecard["MONTH_NAME"], scorecard["Volume"]/1e6,    BLUE,   1, 2, "Volume")
    sparkline(scorecard["MONTH_NAME"], scorecard["LME"],           TEAL,   2, 1, "LME")
    sparkline(scorecard["MONTH_NAME"], scorecard["Spread"],        GOLD,   2, 2, "Spread")

    fig_sc.update_layout(
        paper_bgcolor=NAVY, plot_bgcolor="#090e1c",
        font=dict(color="#4a6080", family="Inter", size=12),
        showlegend=False, height=550,
        margin=dict(t=55, b=30, l=40, r=40),
        hoverlabel=dict(bgcolor=NAVY_MD, font=dict(color=ICE)),
    )
    for ann in fig_sc.layout.annotations:
        ann.font.color = COP_LT
        ann.font.size  = 12
    fig_sc.update_xaxes(gridcolor="rgba(255,255,255,0.03)", tickfont=dict(color="#3a5070"))
    fig_sc.update_yaxes(gridcolor="rgba(255,255,255,0.03)", tickfont=dict(color="#3a5070"),
                        zeroline=False)
    st.plotly_chart(fig_sc, use_container_width=True)

    # ── Monthly summary table
    sec("📋","Monthly Performance Table")
    sc_display = scorecard[["MONTH_NAME","Revenue","Volume","Tonnage","LME","Basic","Spread","AV_km","Rev_share"]].copy()
    sc_display.columns = ["Month","Revenue (€)","Volume (km)","Tonnage (T)",
                           "All-In LME","Basic LME","Spread (€/kg)","Added Value (€/km)","Rev Share (%)"]
    # Add MoM growth
    sc_display["MoM Growth (%)"] = sc_display["Revenue (€)"].pct_change().mul(100).round(1)

    st.dataframe(sc_display.style
        .format({"Revenue (€)":"€{:,.0f}","Volume (km)":"{:,.0f}","Tonnage (T)":"{:,.0f}",
                 "All-In LME":"{:.2f}","Basic LME":"{:.2f}","Spread (€/kg)":"{:.2f}",
                 "Added Value (€/km)":"€{:.2f}","Rev Share (%)":"{:.1f}%",
                 "MoM Growth (%)":"{:+.1f}%"})
        .set_properties(**{"background-color":NAVY_MD,"color":ICE})
        .map(lambda v: f"color: #10b981" if isinstance(v, float) and v > 0 else (f"color: #f43f5e" if isinstance(v, float) and v < 0 else ""),
                  subset=["MoM Growth (%)"]),
        use_container_width=True, hide_index=True)

    # ── Entity comparison radar
    sec("🔄","Entity Performance Comparison")
    cl, cr = st.columns(2)
    with cl:
        ent_comp = df.groupby("ENTITY").agg(
            Revenue=("TOTAL_AMOUNT","sum"),
            Volume=("QTY_KM","sum"),
            Tonnage=("RC_KG",lambda x:x.sum()/1000),
            LME=("LME_SALES","mean"),
            AV=("AV_INDEX","sum"),
            QTY=("QTY_KM","sum"),
        ).reset_index()
        ent_comp["AV_km"] = ent_comp["AV"] / ent_comp["QTY"]

        fig_ent = go.Figure()
        colors_e = [BLUE, COPPER]
        for i, row in ent_comp.iterrows():
            fig_ent.add_trace(go.Bar(
                name=row["ENTITY"],
                x=["Revenue (M€)","Volume (Mkm)","Tonnage (T)","LME (€/kg)","AV (€/km)"],
                y=[row["Revenue"]/1e6, row["Volume"]/1e6,
                   row["Tonnage"], row["LME"], row["AV_km"]],
                marker=dict(color=colors_e[i%2], opacity=0.88),
            ))
        alay(fig_ent, barmode="group", title="Entity KPI Comparison")
        st.plotly_chart(fig_ent, use_container_width=True)

    with cr:
        # Revenue split by entity per month
        ent_month = df.groupby(["MONTH_NAME","ENTITY"]).agg(
            Revenue=("TOTAL_AMOUNT","sum")).reset_index()
        ent_month["MONTH_NAME"] = pd.Categorical(ent_month["MONTH_NAME"],
                                                  categories=MONTH_ORDER, ordered=True)
        ent_month = ent_month.sort_values("MONTH_NAME")
        fig_em = px.bar(ent_month, x="MONTH_NAME", y="Revenue", color="ENTITY",
                        barmode="stack", title="Monthly Revenue Stack by Entity",
                        color_discrete_sequence=[BLUE, COPPER],
                        text_auto=".2s", labels={"Revenue":"Revenue (€)","MONTH_NAME":"Month"})
        alay(fig_em)
        st.plotly_chart(fig_em, use_container_width=True)

