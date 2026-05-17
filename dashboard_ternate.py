"""
Dashboard Kinerja Cabang Ternate - PT. ASDP Indonesia Ferry (Persero)
Jalankan dengan: streamlit run dashboard_ternate.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import warnings
warnings.filterwarnings("ignore")

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Kinerja Cabang Ternate",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CUSTOM CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }

/* Main background */
.main { background-color: #0a0e1a; }
.stApp { background: linear-gradient(135deg, #0a0e1a 0%, #0d1b2e 50%, #071626 100%); }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1b2e 0%, #091522 100%);
    border-right: 1px solid rgba(0,180,255,0.15);
}

/* Metric cards */
.metric-card {
    background: linear-gradient(135deg, rgba(0,180,255,0.08) 0%, rgba(0,100,200,0.05) 100%);
    border: 1px solid rgba(0,180,255,0.2);
    border-radius: 16px;
    padding: 20px 24px;
    margin-bottom: 12px;
    transition: all 0.3s ease;
}
.metric-card:hover { border-color: rgba(0,180,255,0.5); transform: translateY(-2px); }
.metric-value { font-size: 1.8rem; font-weight: 800; color: #00b4ff; letter-spacing: -1px; }
.metric-label { font-size: 0.75rem; font-weight: 500; color: rgba(255,255,255,0.5); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px; }
.metric-delta { font-size: 0.85rem; font-weight: 600; margin-top: 4px; }
.delta-pos { color: #00e676; }
.delta-neg { color: #ff5252; }

/* Section headers */
.section-header {
    font-size: 1.1rem; font-weight: 700; color: #00b4ff;
    border-left: 3px solid #00b4ff; padding-left: 12px;
    margin: 24px 0 16px 0; letter-spacing: 0.5px;
}

/* Table styling */
.dataframe { font-size: 0.82rem !important; }

/* Badge */
.badge-profit { background: rgba(0,230,118,0.15); color: #00e676; border: 1px solid rgba(0,230,118,0.3); padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
.badge-loss   { background: rgba(255,82,82,0.15);  color: #ff5252; border: 1px solid rgba(255,82,82,0.3);  padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }

/* Plotly chart containers */
.stPlotlyChart { border-radius: 16px; overflow: hidden; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { background: rgba(0,20,50,0.5); border-radius: 12px; padding: 4px; gap: 4px; }
.stTabs [data-baseweb="tab"] { border-radius: 8px; color: rgba(255,255,255,0.5); font-weight: 500; }
.stTabs [aria-selected="true"] { background: rgba(0,180,255,0.2) !important; color: #00b4ff !important; }
</style>
""", unsafe_allow_html=True)

# ── CONSTANTS ─────────────────────────────────────────────────────────────────
EXCEL_PATH = "KINERJA_CABANG_TERNATE_APRIL_2026.xlsx"
MONTHS = ["JANUARI", "FEBRUARI", "MARET", "APRIL", "MEI", "JUNI", "JULI", "AGUSTUS", "SEPTEMBER", "OKTOBER", "NOPEMBER", "DESEMBER"]
COLORS = {
    "real25": "#4fc3f7",
    "rka26":  "#ffb74d",
    "real26": "#00e676",
    "biaya":  "#ff5252",
    "laba":   "#ce93d8",
}

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="rgba(255,255,255,0.85)", family="Plus Jakarta Sans"),
    margin=dict(l=10, r=10, t=40, b=10),
    legend=dict(bgcolor="rgba(0,0,0,0)", borderwidth=0),
    xaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.1)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.1)"),
)

def fmt_rupiah(v):
    """Format angka ke Rupiah miliar/juta."""
    if pd.isna(v) or v is None: return "Rp 0"
    v = float(v)
    if abs(v) >= 1e9:  return f"Rp {v/1e9:,.2f} M"
    if abs(v) >= 1e6:  return f"Rp {v/1e6:,.1f} Jt"
    return f"Rp {v:,.0f}"

def pct(v):
    if pd.isna(v) or v is None: return "–"
    return f"{float(v)*100:.1f}%"

# ── DATA LOADING ──────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_rekap_sd():
    """Sheet: Rekap spreadsheet sd APRIL 26 – data kumulatif."""
    df = pd.read_excel(EXCEL_PATH, sheet_name="Rekap spreadsheet sd APRIL 26", header=None)
    rows = []
    for i in range(3, len(df)):
        r = df.iloc[i]
        uraian = str(r[1]).strip() if pd.notna(r[1]) else ""
        if not uraian or uraian in ["nan", ""]: continue
        try:
            rows.append({
                "NO": r[0], "URAIAN": uraian,
                "PEND_REAL25": float(r[2]) if pd.notna(r[2]) else 0,
                "PEND_RKAC26": float(r[3]) if pd.notna(r[3]) else 0,
                "PEND_REAL26": float(r[4]) if pd.notna(r[4]) else 0,
                "BIAYA_REAL25": float(r[5]) if pd.notna(r[5]) else 0,
                "BIAYA_RKAC26": float(r[6]) if pd.notna(r[6]) else 0,
                "BIAYA_REAL26": float(r[7]) if pd.notna(r[7]) else 0,
                "LABA_REAL25": float(r[8]) if pd.notna(r[8]) else 0,
                "LABA_RKAC26": float(r[9]) if pd.notna(r[9]) else 0,
                "LABA_REAL26": float(r[10]) if pd.notna(r[10]) else 0,
            })
        except: continue
    return pd.DataFrame(rows)

@st.cache_data(show_spinner=False)
def load_rekap_april():
    """Sheet: Rekap spreadsheet APRIL 26 – data bulan April saja."""
    df = pd.read_excel(EXCEL_PATH, sheet_name="Rekap spreadsheet APRIL 26", header=None)
    rows = []
    for i in range(3, len(df)):
        r = df.iloc[i]
        uraian = str(r[1]).strip() if pd.notna(r[1]) else ""
        if not uraian or uraian in ["nan", ""]: continue
        try:
            rows.append({
                "NO": r[0], "URAIAN": uraian,
                "PEND_REAL25": float(r[2]) if pd.notna(r[2]) else 0,
                "PEND_RKAC26": float(r[3]) if pd.notna(r[3]) else 0,
                "PEND_REAL26": float(r[4]) if pd.notna(r[4]) else 0,
                "BIAYA_REAL25": float(r[5]) if pd.notna(r[5]) else 0,
                "BIAYA_RKAC26": float(r[6]) if pd.notna(r[6]) else 0,
                "BIAYA_REAL26": float(r[7]) if pd.notna(r[7]) else 0,
                "LABA_REAL25": float(r[8]) if pd.notna(r[8]) else 0,
                "LABA_RKAC26": float(r[9]) if pd.notna(r[9]) else 0,
                "LABA_REAL26": float(r[10]) if pd.notna(r[10]) else 0,
            })
        except: continue
    return pd.DataFrame(rows)

@st.cache_data(show_spinner=False)
def load_rekap_bulanan():
    """Sheet REKAP – ambil tren bulanan Jan–Apr untuk semua kapal."""
    df = pd.read_excel(EXCEL_PATH, sheet_name="REKAP", header=None)
    # Header mulai baris 6 (index 6): col mapping per bulan
    # kolom: Jan(2,3,4), Feb(7,8,9), Mar(12,13,14), Apr(17,18,19)
    COL_MAP = {
        "JANUARI":  (2, 3, 4),
        "FEBRUARI": (7, 8, 9),
        "MARET":    (12, 13, 14),
        "APRIL":    (17, 18, 19),
    }
    records = []
    current_kapal = None
    for i in range(9, len(df)):
        r = df.iloc[i]
        # Detect kapal header
        cell0 = str(r[0]).strip() if pd.notna(r[0]) else ""
        cell1 = str(r[1]).strip() if pd.notna(r[1]) else ""
        if "KMP." in cell1 or "PELABUHAN" in cell1:
            current_kapal = cell1
            continue
        if current_kapal and cell1 in ["Pendapatan", "Biaya", "Laba/ Rugi"]:
            tipe = cell1
            for bulan, (c25, crka, c26) in COL_MAP.items():
                try:
                    records.append({
                        "Kapal": current_kapal, "Tipe": tipe, "Bulan": bulan,
                        "REAL_2025": float(r[c25]) if pd.notna(r[c25]) else 0,
                        "RKA_2026":  float(r[crka]) if pd.notna(r[crka]) else 0,
                        "REAL_2026": float(r[c26]) if pd.notna(r[c26]) else 0,
                    })
                except: pass
    return pd.DataFrame(records)

@st.cache_data(show_spinner=False)
def load_gab_sheet(sheet_name, segmen_label):
    """Load sheet gabungan (Gab Kapal, Gab Kapal Kom, Gab Pelabuhan)."""
    df = pd.read_excel(EXCEL_PATH, sheet_name=sheet_name, header=None)
    COL_MAP = {"JANUARI":(2,3,4),"FEBRUARI":(7,8,9),"MARET":(12,13,14),"APRIL":(17,18,19)}
    records = []
    for i in range(9, len(df)):
        r = df.iloc[i]
        keterangan = str(r[1]).strip() if pd.notna(r[1]) else ""
        if not keterangan or keterangan == "nan": continue
        for bulan, (c25, crka, c26) in COL_MAP.items():
            try:
                v25  = float(r[c25]) if pd.notna(r[c25]) else 0
                vrka = float(r[crka]) if pd.notna(r[crka]) else 0
                v26  = float(r[c26])  if pd.notna(r[c26])  else 0
                if v25 == 0 and vrka == 0 and v26 == 0: continue
                records.append({
                    "Segmen": segmen_label, "Keterangan": keterangan,
                    "Bulan": bulan,
                    "REAL_2025": v25, "RKA_2026": vrka, "REAL_2026": v26,
                })
            except: pass
    return pd.DataFrame(records)

@st.cache_data(show_spinner=False)
def load_kapal_detail(sheet_name):
    """Load detail per kapal – ambil kolom s/d April."""
    df = pd.read_excel(EXCEL_PATH, sheet_name=sheet_name, header=None)
    # S/D April ada di kolom 72,73,74 (index)
    COL_MAP = {"JANUARI":(2,3,4),"FEBRUARI":(7,8,9),"MARET":(12,13,14),"APRIL":(17,18,19)}
    records = []
    for i in range(9, len(df)):
        r = df.iloc[i]
        keterangan = str(r[1]).strip() if pd.notna(r[1]) else ""
        if not keterangan or keterangan == "nan": continue
        for bulan, (c25, crka, c26) in COL_MAP.items():
            try:
                v25  = float(r[c25]) if pd.notna(r[c25]) else 0
                vrka = float(r[crka]) if pd.notna(r[crka]) else 0
                v26  = float(r[c26])  if pd.notna(r[c26]) else 0
                records.append({
                    "Keterangan": keterangan, "Bulan": bulan,
                    "REAL_2025": v25, "RKA_2026": vrka, "REAL_2026": v26,
                })
            except: pass
    kapal_name = str(df.iloc[4, 0]).replace("SEGMEN : ", "").strip()
    return pd.DataFrame(records), kapal_name

# ── HELPER: WATERFALL CHART ───────────────────────────────────────────────────
def waterfall_chart(labels, values, title):
    colors = ["#00e676" if v >= 0 else "#ff5252" for v in values]
    fig = go.Figure(go.Bar(x=labels, y=values, marker_color=colors,
                           text=[fmt_rupiah(v) for v in values], textposition="outside",
                           textfont_size=10))
    fig.update_layout(**PLOTLY_LAYOUT, title=dict(text=title, font_size=13), height=320)
    return fig

# ── HELPER: LINE TREND CHART ─────────────────────────────────────────────────
def trend_line(df_pivot, title, y_col25, y_rka, y_col26, months=None):
    if months is None: months = MONTHS[:4]
    fig = go.Figure()
    if y_col25 in df_pivot.columns:
        fig.add_trace(go.Scatter(x=months, y=df_pivot[y_col25].values,
            name="Real 2025", line=dict(color=COLORS["real25"], width=2, dash="dot"), mode="lines+markers"))
    if y_rka in df_pivot.columns:
        fig.add_trace(go.Scatter(x=months, y=df_pivot[y_rka].values,
            name="RKA 2026", line=dict(color=COLORS["rka26"], width=2, dash="dash"), mode="lines+markers"))
    if y_col26 in df_pivot.columns:
        fig.add_trace(go.Scatter(x=months, y=df_pivot[y_col26].values,
            name="Real 2026", line=dict(color=COLORS["real26"], width=2.5), mode="lines+markers",
            fill="tozeroy", fillcolor="rgba(0,230,118,0.06)"))
    fig.update_layout(**PLOTLY_LAYOUT, title=dict(text=title, font_size=13), height=300,
                      yaxis_tickformat=".2s")
    return fig

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 16px 0'>
        <div style='font-size:2.5rem'>⚓</div>
        <div style='font-size:1.1rem; font-weight:800; color:#00b4ff; letter-spacing:1px'>ASDP TERNATE</div>
        <div style='font-size:0.72rem; color:rgba(255,255,255,0.4); margin-top:4px'>KINERJA KEUANGAN 2025/2026</div>
    </div>
    <hr style='border-color:rgba(0,180,255,0.15); margin: 8px 0 20px'>
    """, unsafe_allow_html=True)

    menu = st.radio("📊 MENU NAVIGASI", [
        "🏠 Ringkasan Gabungan",
        "🚢 Gabungan Kapal",
        "⚓ Detail Per Kapal",
        "🏗️ Gabungan Pelabuhan",
        "📈 Analisis Tren",
    ], label_visibility="visible")

    st.markdown("<hr style='border-color:rgba(0,180,255,0.1); margin:20px 0'>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:0.7rem; color:rgba(255,255,255,0.3); text-align:center'>
        PT. ASDP Indonesia Ferry (Persero)<br>
        Regional IV · Cabang Ternate<br>
        <b style='color:rgba(0,180,255,0.6)'>Periode: s/d April 2026</b>
    </div>
    """, unsafe_allow_html=True)

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
with st.spinner("Memuat data..."):
    df_sd    = load_rekap_sd()
    df_april = load_rekap_april()

# ── TOTAL ROW HELPERS ─────────────────────────────────────────────────────────
def get_total(df, uraian_keyword):
    row = df[df["URAIAN"].str.contains(uraian_keyword, case=False, na=False)]
    if not row.empty: return row.iloc[0]
    return None

def get_total_safe(df, keywords, col):
    for kw in keywords:
        r = get_total(df, kw)
        if r is not None:
            try: return float(r[col])
            except: pass
    return 0.0

# ── PAGE: RINGKASAN GABUNGAN ──────────────────────────────────────────────────
if "Ringkasan" in menu:
    st.markdown("""
    <div style='padding: 8px 0 24px'>
        <h1 style='font-size:1.8rem; font-weight:800; color:#fff; margin:0'>
            📊 Ringkasan Kinerja Gabungan
        </h1>
        <p style='color:rgba(255,255,255,0.45); font-size:0.85rem; margin-top:4px'>
            PT. ASDP Indonesia Ferry (Persero) · Cabang Ternate · s/d April 2026
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── TOTAL KESELURUHAN ─────────────────────────────────────────────────────
    tot_sd  = df_sd[df_sd["URAIAN"].str.contains("TOTAL KESELURUHAN", case=False, na=False)]
    tot_apr = df_april[df_april["URAIAN"].str.contains("TOTAL KESELURUHAN", case=False, na=False)]

    def safe_val(df_rows, col):
        if not df_rows.empty:
            v = df_rows.iloc[0][col]
            try: return float(v)
            except: return 0.0
        return 0.0

    kpi_data = [
        ("💰 Pendapatan Real s/d April",
         safe_val(tot_sd, "PEND_REAL26"), safe_val(tot_sd, "PEND_RKAC26"), safe_val(tot_sd, "PEND_REAL25")),
        ("📉 Biaya Real s/d April",
         safe_val(tot_sd, "BIAYA_REAL26"), safe_val(tot_sd, "BIAYA_RKAC26"), safe_val(tot_sd, "BIAYA_REAL25")),
        ("📈 Laba/Rugi Real s/d April",
         safe_val(tot_sd, "LABA_REAL26"), safe_val(tot_sd, "LABA_RKAC26"), safe_val(tot_sd, "LABA_REAL25")),
        ("💰 Pendapatan April 2026",
         safe_val(tot_apr, "PEND_REAL26"), safe_val(tot_apr, "PEND_RKAC26"), safe_val(tot_apr, "PEND_REAL25")),
    ]

    cols = st.columns(4)
    for col, (label, real26, rkac, real25) in zip(cols, kpi_data):
        ach  = (real26 / rkac * 100) if rkac else 0
        grw  = ((real26 - real25) / abs(real25) * 100) if real25 else 0
        delta_class = "delta-pos" if grw >= 0 else "delta-neg"
        delta_icon  = "▲" if grw >= 0 else "▼"
        with col:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>{label}</div>
                <div class='metric-value'>{fmt_rupiah(real26)}</div>
                <div class='metric-delta {delta_class}'>{delta_icon} {abs(grw):.1f}% vs Real 2025</div>
                <div style='font-size:0.75rem; color:rgba(255,255,255,0.35); margin-top:2px'>
                    Ach: {ach:.1f}% · RKA: {fmt_rupiah(rkac)}
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div class='section-header'>KINERJA s/d APRIL — SEGMEN UTAMA</div>", unsafe_allow_html=True)

    # Bar chart segmen
    segmen_filter = {
        "Penyeberangan": "TOTAL PENYEBERANGAN",
        "Pelabuhan":     "TOTAL PELABUHAN",
        "UAJ":           "UAJ",
        "Overhead":      "OVERHEAD",
    }
    seg_rows = []
    for name, kw in segmen_filter.items():
        r = df_sd[df_sd["URAIAN"].str.contains(kw, case=False, na=False)]
        if not r.empty:
            seg_rows.append({
                "Segmen": name,
                "Pendapatan": float(r.iloc[0]["PEND_REAL26"]) if pd.notna(r.iloc[0]["PEND_REAL26"]) else 0,
                "Biaya":      float(r.iloc[0]["BIAYA_REAL26"]) if pd.notna(r.iloc[0]["BIAYA_REAL26"]) else 0,
                "Laba/Rugi":  float(r.iloc[0]["LABA_REAL26"]) if pd.notna(r.iloc[0]["LABA_REAL26"]) else 0,
            })

    if seg_rows:
        df_seg = pd.DataFrame(seg_rows)
        col1, col2 = st.columns([3, 2])
        with col1:
            fig = go.Figure()
            fig.add_trace(go.Bar(name="Pendapatan", x=df_seg["Segmen"], y=df_seg["Pendapatan"],
                                 marker_color=COLORS["real26"], opacity=0.9))
            fig.add_trace(go.Bar(name="Biaya", x=df_seg["Segmen"], y=df_seg["Biaya"],
                                 marker_color=COLORS["biaya"], opacity=0.9))
            fig.update_layout(**PLOTLY_LAYOUT, title="Pendapatan vs Biaya per Segmen (s/d April 2026)",
                              barmode="group", height=350, yaxis_tickformat=".2s")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig2 = go.Figure()
            colors_laba = [COLORS["real26"] if v >= 0 else COLORS["biaya"] for v in df_seg["Laba/Rugi"]]
            fig2.add_trace(go.Bar(x=df_seg["Segmen"], y=df_seg["Laba/Rugi"],
                                  marker_color=colors_laba, text=[fmt_rupiah(v) for v in df_seg["Laba/Rugi"]],
                                  textposition="outside", textfont_size=9))
            fig2.update_layout(**PLOTLY_LAYOUT, title="Laba/Rugi per Segmen", height=350, yaxis_tickformat=".2s")
            st.plotly_chart(fig2, use_container_width=True)

    # Table ringkasan
    st.markdown("<div class='section-header'>TABEL REKAP s/d APRIL 2026</div>", unsafe_allow_html=True)
    df_show = df_sd[["URAIAN", "PEND_REAL25", "PEND_RKAC26", "PEND_REAL26",
                      "BIAYA_REAL26", "LABA_REAL25", "LABA_RKAC26", "LABA_REAL26"]].copy()
    df_show.columns = ["Uraian","Pend Real '25","Pend RKAC '26","Pend Real '26",
                       "Biaya Real '26","Laba Real '25","Laba RKAC '26","Laba Real '26"]
    for c in df_show.columns[1:]:
        df_show[c] = df_show[c].apply(lambda x: fmt_rupiah(x) if pd.notna(x) else "-")
    st.dataframe(df_show, use_container_width=True, height=400,
                 column_config={"Uraian": st.column_config.TextColumn(width="large")})

# ── PAGE: GABUNGAN KAPAL ──────────────────────────────────────────────────────
elif "Gabungan Kapal" in menu:
    st.markdown("<h1 style='font-size:1.8rem;font-weight:800;color:#fff'>🚢 Gabungan Kinerja Kapal</h1>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["⛴️ Semua Kapal (Perintis & Komersil)", "📊 Komersil Saja"])

    # ── Tab 1: Semua kapal dari Rekap spreadsheet ──────────────────────────
    with tab1:
        # Filter rows kapal saja
        df_kapal = df_sd[df_sd["URAIAN"].str.startswith("KMP.")].copy()
        df_kapal = df_kapal[df_kapal["PEND_REAL26"] != 0].reset_index(drop=True)

        if not df_kapal.empty:
            col1, col2 = st.columns([2, 1])
            with col1:
                fig = go.Figure()
                fig.add_trace(go.Bar(name="Real 2025", x=df_kapal["URAIAN"], y=df_kapal["PEND_REAL25"],
                                     marker_color=COLORS["real25"], opacity=0.7))
                fig.add_trace(go.Bar(name="RKA 2026", x=df_kapal["URAIAN"], y=df_kapal["PEND_RKAC26"],
                                     marker_color=COLORS["rka26"], opacity=0.7))
                fig.add_trace(go.Bar(name="Real 2026", x=df_kapal["URAIAN"], y=df_kapal["PEND_REAL26"],
                                     marker_color=COLORS["real26"]))
                fig.update_layout(**PLOTLY_LAYOUT, title="Pendapatan Per Kapal (s/d April)",
                                  barmode="group", height=380, xaxis_tickangle=-35, yaxis_tickformat=".2s")
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Pie laba/rugi
                laba_pos = df_kapal[df_kapal["LABA_REAL26"] > 0]
                laba_neg = df_kapal[df_kapal["LABA_REAL26"] < 0]
                fig_pie = go.Figure(go.Pie(
                    labels=["Kapal Profit", "Kapal Rugi"],
                    values=[len(laba_pos), len(laba_neg)],
                    hole=0.6,
                    marker_colors=[COLORS["real26"], COLORS["biaya"]],
                ))
                fig_pie.update_layout(**PLOTLY_LAYOUT, title="Proporsi Kapal", height=380,
                                      annotations=[dict(text=f"{len(df_kapal)}<br>Kapal", x=0.5, y=0.5,
                                                        font_size=16, showarrow=False, font_color="#fff")])
                st.plotly_chart(fig_pie, use_container_width=True)

            # Table per kapal
            st.markdown("<div class='section-header'>DETAIL KINERJA PER KAPAL</div>", unsafe_allow_html=True)
            df_tbl = df_kapal[["URAIAN","PEND_REAL26","BIAYA_REAL26","LABA_REAL26",
                                "PEND_RKAC26","LABA_RKAC26"]].copy()
            df_tbl["Ach (%)"] = (df_tbl["PEND_REAL26"] / df_tbl["PEND_RKAC26"] * 100).round(1)
            df_tbl["Status"] = df_tbl["LABA_REAL26"].apply(lambda x: "✅ Profit" if x > 0 else "❌ Rugi")
            for c in ["PEND_REAL26","BIAYA_REAL26","LABA_REAL26","PEND_RKAC26","LABA_RKAC26"]:
                df_tbl[c] = df_tbl[c].apply(fmt_rupiah)
            df_tbl.columns = ["Kapal","Pend Real '26","Biaya Real '26","Laba Real '26",
                               "Pend RKA '26","Laba RKA '26","Ach (%)","Status"]
            st.dataframe(df_tbl, use_container_width=True, height=420)

    with tab2:
        df_kom_detail = df_sd[df_sd["URAIAN"].str.contains("Komersil", case=False, na=False)].copy()
        df_kom_detail = df_kom_detail[df_kom_detail["PEND_REAL26"] != 0].reset_index(drop=True)
        if not df_kom_detail.empty:
            fig = go.Figure()
            fig.add_trace(go.Bar(name="Pendapatan", x=df_kom_detail["URAIAN"],
                                 y=df_kom_detail["PEND_REAL26"], marker_color=COLORS["real26"]))
            fig.add_trace(go.Bar(name="Biaya", x=df_kom_detail["URAIAN"],
                                 y=df_kom_detail["BIAYA_REAL26"], marker_color=COLORS["biaya"]))
            fig.update_layout(**PLOTLY_LAYOUT, title="Pendapatan vs Biaya – Kapal Komersil (s/d April 2026)",
                              barmode="group", height=380, xaxis_tickangle=-30, yaxis_tickformat=".2s")
            st.plotly_chart(fig, use_container_width=True)

            fig2 = go.Figure()
            colors_l = [COLORS["real26"] if v >= 0 else COLORS["biaya"] for v in df_kom_detail["LABA_REAL26"]]
            fig2.add_trace(go.Bar(x=df_kom_detail["URAIAN"], y=df_kom_detail["LABA_REAL26"],
                                  marker_color=colors_l, text=[fmt_rupiah(v) for v in df_kom_detail["LABA_REAL26"]],
                                  textposition="outside", textfont_size=9))
            fig2.update_layout(**PLOTLY_LAYOUT, title="Laba/Rugi Kapal Komersil (s/d April 2026)",
                              height=350, xaxis_tickangle=-30, yaxis_tickformat=".2s")
            st.plotly_chart(fig2, use_container_width=True)

# ── PAGE: DETAIL PER KAPAL ────────────────────────────────────────────────────
elif "Detail Per Kapal" in menu:
    st.markdown("<h1 style='font-size:1.8rem;font-weight:800;color:#fff'>⚓ Detail Kinerja Per Kapal</h1>", unsafe_allow_html=True)

    KAPAL_SHEETS = {
        "KMP. BARONANG (Komersil)":      "Baronang Kom OK",
        "KMP. TUNA (Komersil)":          "Tuna Kom OK",
        "KMP. BOBARA (Komersil)":        "Bobara Kom OK",
        "KMP. GORANGO (Komersil)":       "Gorango Kom OK",
        "KMP. NGAFI (Komersil)":         "Ngafi Kom OK",
        "KMP. MAMING (Komersil)":        "Maming Kom ok",
        "KMP. LEMA (Komersil)":          "Lema Kom OK",
        "KMP. PORTLINK VIII (Komersil)": "Portlink VIII Kom",
        "KMP. DALENTE WOBA (Komersil)":  "Dalente Kom",
        "KMP. KERAPU II (Komersil)":     "Kerapu II Kom OK",
        "KMP. RANAKA (Komersil)":        "Ranaka Kom",
        "KMP. LABUHAN HAJI (Komersil)":  "Labuhan Haji Kom",
        "KMP. ARIWANGAN (Perintis)":     "Ariwangan Tis",
        "KMP. KERAPU II (Perintis)":     "Kerapu II Tis OK",
        "KMP. PULAU SAGORI (Perintis)":  "P. Sagori Tis OK",
        "KMP. GORANGO (Perintis)":       "Gorango Tis OK",
        "KMP. NGAFI (Perintis)":         "Ngafi Tis ok",
        "KMP. LOMPA (Perintis)":         "Lompa Tis OK",
        "KMP. KOLORAI (Perintis)":       "Kolorai Tis OK",
    }

    selected = st.selectbox("🚢 Pilih Kapal", list(KAPAL_SHEETS.keys()))
    sheet_nm = KAPAL_SHEETS[selected]

    try:
        with st.spinner(f"Memuat data {selected}..."):
            df_detail, kapal_lbl = load_kapal_detail(sheet_nm)

        if df_detail.empty:
            st.info("Data tidak tersedia untuk kapal ini.")
        else:
            # Summary KPIs dari rekap
            row_sd = df_sd[df_sd["URAIAN"].str.contains(selected.split("(")[0].strip(), case=False, na=False)]
            if not row_sd.empty:
                r = row_sd.iloc[0]
                c1, c2, c3, c4 = st.columns(4)
                kpis = [
                    ("Pendapatan Real '26", r["PEND_REAL26"], r["PEND_RKAC26"]),
                    ("Biaya Real '26",      r["BIAYA_REAL26"], r["BIAYA_RKAC26"]),
                    ("Laba/Rugi Real '26",  r["LABA_REAL26"], r["LABA_RKAC26"]),
                    ("Pendapatan Real '25", r["PEND_REAL25"], r["PEND_REAL26"]),
                ]
                for col, (lbl, v26, base) in zip([c1,c2,c3,c4], kpis):
                    ach = (float(v26)/float(base)*100) if base and float(base) != 0 else 0
                    delta_cls = "delta-pos" if float(v26) >= 0 else "delta-neg"
                    with col:
                        st.markdown(f"""
                        <div class='metric-card'>
                            <div class='metric-label'>{lbl}</div>
                            <div class='metric-value'>{fmt_rupiah(v26)}</div>
                            <div class='metric-delta {delta_cls}'>Ach: {ach:.1f}%</div>
                        </div>""", unsafe_allow_html=True)

            # Trend bulanan dari detail sheet
            months_avail = ["JANUARI","FEBRUARI","MARET","APRIL"]
            pend_vals, biaya_vals, laba_vals = [], [], []
            rka_pend, rka_biaya = [], []

            for m in months_avail:
                dm = df_detail[df_detail["Bulan"] == m]
                # Cari baris Pendapatan Usaha & Beban
                pend_row  = dm[dm["Keterangan"].str.contains("PENDAPATAN USAHA|JUMLAH PENDAPATAN", case=False, na=False)]
                biaya_row = dm[dm["Keterangan"].str.contains("JUMLAH BEBAN|BEBAN USAHA|JUMLAH BIAYA|TOTAL BEBAN", case=False, na=False)]

                if not pend_row.empty:
                    pend_vals.append(float(pend_row.iloc[-1]["REAL_2026"]))
                    rka_pend.append(float(pend_row.iloc[-1]["RKA_2026"]))
                else:
                    pend_vals.append(0); rka_pend.append(0)

                if not biaya_row.empty:
                    biaya_vals.append(float(biaya_row.iloc[-1]["REAL_2026"]))
                    rka_biaya.append(float(biaya_row.iloc[-1]["RKA_2026"]))
                else:
                    biaya_vals.append(0); rka_biaya.append(0)

                laba_vals.append(pend_vals[-1] - biaya_vals[-1])

            col1, col2 = st.columns(2)
            with col1:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=months_avail, y=rka_pend, name="RKA 2026",
                    line=dict(color=COLORS["rka26"], dash="dash", width=2), mode="lines+markers"))
                fig.add_trace(go.Scatter(x=months_avail, y=pend_vals, name="Real 2026",
                    line=dict(color=COLORS["real26"], width=2.5), mode="lines+markers",
                    fill="tozeroy", fillcolor="rgba(0,230,118,0.06)"))
                fig.update_layout(**PLOTLY_LAYOUT, title="Tren Pendapatan Bulanan", height=300, yaxis_tickformat=".2s")
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                fig2 = go.Figure()
                bar_colors = [COLORS["real26"] if v >= 0 else COLORS["biaya"] for v in laba_vals]
                fig2.add_trace(go.Bar(x=months_avail, y=laba_vals, marker_color=bar_colors,
                    text=[fmt_rupiah(v) for v in laba_vals], textposition="outside", textfont_size=9))
                fig2.update_layout(**PLOTLY_LAYOUT, title="Laba/Rugi Bulanan", height=300, yaxis_tickformat=".2s")
                st.plotly_chart(fig2, use_container_width=True)

            # Rincian akun
            st.markdown("<div class='section-header'>RINCIAN AKUN – APRIL 2026</div>", unsafe_allow_html=True)
            df_apr_detail = df_detail[df_detail["Bulan"] == "APRIL"].copy()
            df_apr_display = df_apr_detail[["Keterangan","REAL_2025","RKA_2026","REAL_2026"]].copy()
            df_apr_display["Ach (%)"] = (df_apr_display["REAL_2026"] / df_apr_display["RKA_2026"] * 100).round(1)
            for c in ["REAL_2025","RKA_2026","REAL_2026"]:
                df_apr_display[c] = df_apr_display[c].apply(fmt_rupiah)
            df_apr_display.columns = ["Keterangan","Real 2025","RKA 2026","Real 2026","Ach (%)"]
            df_apr_display = df_apr_display[df_apr_display["Real 2026"] != "Rp 0"]
            st.dataframe(df_apr_display, use_container_width=True, height=450)

    except Exception as e:
        st.error(f"Gagal memuat data kapal: {e}")

# ── PAGE: GABUNGAN PELABUHAN ──────────────────────────────────────────────────
elif "Pelabuhan" in menu:
    st.markdown("<h1 style='font-size:1.8rem;font-weight:800;color:#fff'>🏗️ Kinerja Pelabuhan</h1>", unsafe_allow_html=True)

    PELABUHAN_SHEETS = {
        "BASTIONG":  "Bastiong",
        "SIDANGOLI": "Sidangoli",
        "RUM":       "Rum",
    }

    # Summary dari rekap
    st.markdown("<div class='section-header'>RINGKASAN KINERJA PELABUHAN (s/d April 2026)</div>", unsafe_allow_html=True)
    pel_data = []
    for pel, kw in [("Bastiong","BASTIONG"),("Sidangole","SIDANGOLE"),("Rum","RUM")]:
        r = df_sd[df_sd["URAIAN"].str.contains(kw, case=False, na=False)]
        if not r.empty:
            pel_data.append({
                "Pelabuhan": pel,
                "Pend Real '26": float(r.iloc[0]["PEND_REAL26"]),
                "Biaya Real '26": float(r.iloc[0]["BIAYA_REAL26"]),
                "Laba Real '26": float(r.iloc[0]["LABA_REAL26"]),
                "Pend RKAC '26": float(r.iloc[0]["PEND_RKAC26"]),
            })

    if pel_data:
        df_pel = pd.DataFrame(pel_data)
        c1, c2 = st.columns(2)
        with c1:
            fig = go.Figure()
            fig.add_trace(go.Bar(name="Pendapatan", x=df_pel["Pelabuhan"],
                                 y=df_pel["Pend Real '26"], marker_color=COLORS["real26"]))
            fig.add_trace(go.Bar(name="Biaya", x=df_pel["Pelabuhan"],
                                 y=df_pel["Biaya Real '26"], marker_color=COLORS["biaya"]))
            fig.update_layout(**PLOTLY_LAYOUT, title="Pendapatan vs Biaya Pelabuhan",
                              barmode="group", height=340, yaxis_tickformat=".2s")
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            colors_l = [COLORS["real26"] if v >= 0 else COLORS["biaya"] for v in df_pel["Laba Real '26"]]
            fig2 = go.Figure(go.Bar(x=df_pel["Pelabuhan"], y=df_pel["Laba Real '26"],
                                    marker_color=colors_l,
                                    text=[fmt_rupiah(v) for v in df_pel["Laba Real '26"]],
                                    textposition="outside"))
            fig2.update_layout(**PLOTLY_LAYOUT, title="Laba/Rugi Pelabuhan", height=340, yaxis_tickformat=".2s")
            st.plotly_chart(fig2, use_container_width=True)

        # KPI cards
        cols = st.columns(3)
        for col, row in zip(cols, pel_data):
            ach = (row["Pend Real '26"] / row["Pend RKAC '26"] * 100) if row["Pend RKAC '26"] else 0
            status_cls = "delta-pos" if row["Laba Real '26"] >= 0 else "delta-neg"
            with col:
                st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-label'>🏗️ {row['Pelabuhan']}</div>
                    <div class='metric-value'>{fmt_rupiah(row['Pend Real \'26'])}</div>
                    <div style='font-size:0.8rem;color:rgba(255,255,255,0.5);margin-top:4px'>
                        Biaya: {fmt_rupiah(row['Biaya Real \'26'])}
                    </div>
                    <div class='metric-delta {status_cls}'>
                        L/R: {fmt_rupiah(row['Laba Real \'26'])} · Ach: {ach:.1f}%
                    </div>
                </div>""", unsafe_allow_html=True)

    # Detail per pelabuhan
    st.markdown("<div class='section-header'>DETAIL AKUN PELABUHAN</div>", unsafe_allow_html=True)
    sel_pel = st.selectbox("Pilih Pelabuhan", list(PELABUHAN_SHEETS.keys()))
    try:
        with st.spinner(f"Memuat data Pelabuhan {sel_pel}..."):
            df_p, p_lbl = load_kapal_detail(PELABUHAN_SHEETS[sel_pel])
        if not df_p.empty:
            months_avail = ["JANUARI","FEBRUARI","MARET","APRIL"]
            pend_vals = []
            for m in months_avail:
                dm = df_p[df_p["Bulan"] == m]
                pr = dm[dm["Keterangan"].str.contains("JUMLAH PENDAPATAN|PENDAPATAN USAHA", case=False, na=False)]
                pend_vals.append(float(pr.iloc[-1]["REAL_2026"]) if not pr.empty else 0)

            fig3 = go.Figure(go.Scatter(x=months_avail, y=pend_vals, mode="lines+markers",
                line=dict(color=COLORS["real26"], width=2.5),
                fill="tozeroy", fillcolor="rgba(0,230,118,0.06)"))
            fig3.update_layout(**PLOTLY_LAYOUT, title=f"Tren Pendapatan – {sel_pel}", height=280, yaxis_tickformat=".2s")
            st.plotly_chart(fig3, use_container_width=True)

            df_p_apr = df_p[(df_p["Bulan"] == "APRIL") & (df_p["REAL_2026"] != 0)][["Keterangan","REAL_2025","RKA_2026","REAL_2026"]].copy()
            for c in ["REAL_2025","RKA_2026","REAL_2026"]:
                df_p_apr[c] = df_p_apr[c].apply(fmt_rupiah)
            df_p_apr.columns = ["Keterangan","Real 2025","RKA 2026","Real 2026"]
            st.dataframe(df_p_apr, use_container_width=True, height=400)
    except Exception as e:
        st.error(f"Gagal memuat detail pelabuhan: {e}")

# ── PAGE: ANALISIS TREN ───────────────────────────────────────────────────────
elif "Tren" in menu:
    st.markdown("<h1 style='font-size:1.8rem;font-weight:800;color:#fff'>📈 Analisis Tren Bulanan</h1>", unsafe_allow_html=True)

    try:
        with st.spinner("Memuat data tren..."):
            df_trend = load_rekap_bulanan()
    except Exception as e:
        st.error(f"Gagal memuat data tren: {e}")
        st.stop()

    if df_trend.empty:
        st.warning("Data tren tidak tersedia.")
    else:
        months_avail = ["JANUARI","FEBRUARI","MARET","APRIL"]

        # Agregat total per bulan
        df_total = df_trend[df_trend["Tipe"].isin(["Pendapatan","Biaya","Laba/ Rugi"])].groupby(["Bulan","Tipe"])[["REAL_2025","RKA_2026","REAL_2026"]].sum().reset_index()

        # Sort bulan
        df_total["BulanOrder"] = df_total["Bulan"].map({m:i for i,m in enumerate(months_avail)})
        df_total = df_total.sort_values("BulanOrder")

        col1, col2 = st.columns(2)
        with col1:
            df_pend = df_total[df_total["Tipe"] == "Pendapatan"]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df_pend["Bulan"], y=df_pend["REAL_2025"], name="Real 2025",
                line=dict(color=COLORS["real25"], width=2, dash="dot"), mode="lines+markers"))
            fig.add_trace(go.Scatter(x=df_pend["Bulan"], y=df_pend["RKA_2026"], name="RKA 2026",
                line=dict(color=COLORS["rka26"], width=2, dash="dash"), mode="lines+markers"))
            fig.add_trace(go.Scatter(x=df_pend["Bulan"], y=df_pend["REAL_2026"], name="Real 2026",
                line=dict(color=COLORS["real26"], width=2.5), mode="lines+markers",
                fill="tozeroy", fillcolor="rgba(0,230,118,0.06)"))
            fig.update_layout(**PLOTLY_LAYOUT, title="Tren Pendapatan Total (Jan–Apr)", height=320, yaxis_tickformat=".2s")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            df_laba = df_total[df_total["Tipe"] == "Laba/ Rugi"]
            bar_c = [COLORS["real26"] if v >= 0 else COLORS["biaya"] for v in df_laba["REAL_2026"]]
            fig2 = go.Figure(go.Bar(x=df_laba["Bulan"], y=df_laba["REAL_2026"], marker_color=bar_c,
                text=[fmt_rupiah(v) for v in df_laba["REAL_2026"]], textposition="outside", textfont_size=10))
            fig2.update_layout(**PLOTLY_LAYOUT, title="Laba/Rugi Total Bulanan", height=320, yaxis_tickformat=".2s")
            st.plotly_chart(fig2, use_container_width=True)

        # Per-kapal trend
        st.markdown("<div class='section-header'>TREN PENDAPATAN PER KAPAL</div>", unsafe_allow_html=True)
        all_kapal = sorted(df_trend["Kapal"].unique())
        selected_kapal = st.multiselect("Pilih Kapal:", all_kapal, default=all_kapal[:5] if len(all_kapal) >= 5 else all_kapal)

        if selected_kapal:
            df_k_pend = df_trend[(df_trend["Tipe"] == "Pendapatan") & (df_trend["Kapal"].isin(selected_kapal))]
            df_k_pend["BulanOrder"] = df_k_pend["Bulan"].map({m:i for i,m in enumerate(months_avail)})
            df_k_pend = df_k_pend.sort_values("BulanOrder")

            palette = px.colors.qualitative.Set2
            fig3 = go.Figure()
            for i, k in enumerate(selected_kapal):
                dk = df_k_pend[df_k_pend["Kapal"] == k]
                clr = palette[i % len(palette)]
                fig3.add_trace(go.Scatter(x=dk["Bulan"], y=dk["REAL_2026"], name=k[:25],
                    line=dict(color=clr, width=2), mode="lines+markers"))
            fig3.update_layout(**PLOTLY_LAYOUT, title="Tren Pendapatan Real 2026 per Kapal", height=380, yaxis_tickformat=".2s")
            st.plotly_chart(fig3, use_container_width=True)

            # Achievement (ach) per kapal per bulan
            df_k_ach = df_trend[(df_trend["Tipe"] == "Pendapatan") & (df_trend["Kapal"].isin(selected_kapal))].copy()
            df_k_ach["Ach (%)"] = (df_k_ach["REAL_2026"] / df_k_ach["RKA_2026"] * 100).round(1)
            df_k_ach = df_k_ach[["Kapal","Bulan","Ach (%)","REAL_2026","RKA_2026"]].copy()
            df_k_ach["REAL_2026"] = df_k_ach["REAL_2026"].apply(fmt_rupiah)
            df_k_ach["RKA_2026"]  = df_k_ach["RKA_2026"].apply(fmt_rupiah)
            df_k_ach.columns = ["Kapal","Bulan","Ach (%)","Real 2026","RKA 2026"]
            st.dataframe(df_k_ach, use_container_width=True, height=350)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; padding: 32px 0 16px; color:rgba(255,255,255,0.2); font-size:0.72rem'>
    PT. ASDP Indonesia Ferry (Persero) · Regional IV · Cabang Ternate ·
    Rekap Kinerja Keuangan April 2026 · Dashboard dibuat otomatis dari data Excel
</div>
""", unsafe_allow_html=True)
