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

.main { background-color: #0a0e1a; }
.stApp { background: linear-gradient(135deg, #0a0e1a 0%, #0d1b2e 50%, #071626 100%); }

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1b2e 0%, #091522 100%);
    border-right: 1px solid rgba(0,180,255,0.15);
}

/* KPI Cards – warna berbeda per tipe */
.kpi-card {
    border-radius: 16px;
    padding: 20px 22px 16px;
    margin-bottom: 10px;
    position: relative;
    overflow: hidden;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}
.kpi-card:hover { transform: translateY(-3px); box-shadow: 0 8px 32px rgba(0,0,0,0.4); }
.kpi-card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 3px;
    border-radius: 16px 16px 0 0;
}

/* Pendapatan bulan – hijau */
.kpi-pend-bulan {
    background: linear-gradient(135deg, rgba(0,230,118,0.10) 0%, rgba(0,180,90,0.05) 100%);
    border: 1px solid rgba(0,230,118,0.25);
}
.kpi-pend-bulan::before { background: linear-gradient(90deg, #00e676, #00c853); }

/* Laba bulan – ungu */
.kpi-laba-bulan {
    background: linear-gradient(135deg, rgba(206,147,216,0.12) 0%, rgba(156,39,176,0.05) 100%);
    border: 1px solid rgba(206,147,216,0.25);
}
.kpi-laba-bulan::before { background: linear-gradient(90deg, #ce93d8, #ab47bc); }

/* Pendapatan sd – biru */
.kpi-pend-sd {
    background: linear-gradient(135deg, rgba(79,195,247,0.10) 0%, rgba(0,150,200,0.05) 100%);
    border: 1px solid rgba(79,195,247,0.25);
}
.kpi-pend-sd::before { background: linear-gradient(90deg, #4fc3f7, #0288d1); }

/* Laba sd – oranye */
.kpi-laba-sd {
    background: linear-gradient(135deg, rgba(255,183,77,0.12) 0%, rgba(255,130,0,0.05) 100%);
    border: 1px solid rgba(255,183,77,0.25);
}
.kpi-laba-sd::before { background: linear-gradient(90deg, #ffb74d, #ef6c00); }

/* Rugi – merah */
.kpi-laba-bulan.rugi, .kpi-laba-sd.rugi {
    background: linear-gradient(135deg, rgba(255,82,82,0.12) 0%, rgba(180,0,0,0.05) 100%);
    border: 1px solid rgba(255,82,82,0.25);
}
.kpi-laba-bulan.rugi::before, .kpi-laba-sd.rugi::before {
    background: linear-gradient(90deg, #ff5252, #b71c1c);
}

.kpi-icon { font-size: 1.6rem; margin-bottom: 6px; }
.kpi-label { font-size: 0.7rem; font-weight: 600; color: rgba(255,255,255,0.45); text-transform: uppercase; letter-spacing: 1.2px; margin-bottom: 6px; }
.kpi-value { font-size: 1.55rem; font-weight: 800; letter-spacing: -0.5px; line-height: 1.1; }
.kpi-pend-bulan .kpi-value  { color: #00e676; }
.kpi-laba-bulan .kpi-value  { color: #ce93d8; }
.kpi-laba-bulan.rugi .kpi-value { color: #ff5252; }
.kpi-pend-sd .kpi-value     { color: #4fc3f7; }
.kpi-laba-sd .kpi-value     { color: #ffb74d; }
.kpi-laba-sd.rugi .kpi-value { color: #ff5252; }
.kpi-sub { font-size: 0.75rem; color: rgba(255,255,255,0.35); margin-top: 6px; }
.kpi-delta { font-size: 0.8rem; font-weight: 600; margin-top: 4px; }
.delta-pos { color: #00e676; }
.delta-neg { color: #ff5252; }

/* Metric card generic */
.metric-card {
    background: linear-gradient(135deg, rgba(0,180,255,0.08) 0%, rgba(0,100,200,0.05) 100%);
    border: 1px solid rgba(0,180,255,0.2);
    border-radius: 16px;
    padding: 20px 24px;
    margin-bottom: 12px;
    transition: all 0.3s ease;
}
.metric-card:hover { border-color: rgba(0,180,255,0.5); transform: translateY(-2px); }
.metric-value { font-size: 1.5rem; font-weight: 800; color: #00b4ff; letter-spacing: -1px; }
.metric-label { font-size: 0.75rem; font-weight: 500; color: rgba(255,255,255,0.5); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px; }
.metric-delta { font-size: 0.85rem; font-weight: 600; margin-top: 4px; }

.section-header {
    font-size: 1.05rem; font-weight: 700; color: #00b4ff;
    border-left: 3px solid #00b4ff; padding-left: 12px;
    margin: 28px 0 16px 0; letter-spacing: 0.5px;
}

/* Kapal card */
.kapal-card {
    background: linear-gradient(135deg, rgba(0,20,50,0.8) 0%, rgba(0,10,30,0.9) 100%);
    border: 1px solid rgba(0,180,255,0.15);
    border-radius: 14px;
    padding: 16px 18px;
    margin-bottom: 10px;
    transition: border-color 0.2s;
}
.kapal-card:hover { border-color: rgba(0,180,255,0.4); }
.kapal-name { font-size: 0.85rem; font-weight: 700; color: #4fc3f7; margin-bottom: 8px; }
.kapal-row { display: flex; justify-content: space-between; font-size: 0.78rem; margin-bottom: 3px; }
.kapal-key { color: rgba(255,255,255,0.45); }
.kapal-val { font-weight: 600; }
.badge-profit { background: rgba(0,230,118,0.15); color: #00e676; border: 1px solid rgba(0,230,118,0.3); padding: 2px 10px; border-radius: 20px; font-size: 0.72rem; font-weight: 600; }
.badge-loss   { background: rgba(255,82,82,0.15);  color: #ff5252; border: 1px solid rgba(255,82,82,0.3);  padding: 2px 10px; border-radius: 20px; font-size: 0.72rem; font-weight: 600; }

.stPlotlyChart { border-radius: 16px; overflow: hidden; }
.stTabs [data-baseweb="tab-list"] { background: rgba(0,20,50,0.5); border-radius: 12px; padding: 4px; gap: 4px; }
.stTabs [data-baseweb="tab"] { border-radius: 8px; color: rgba(255,255,255,0.5); font-weight: 500; }
.stTabs [aria-selected="true"] { background: rgba(0,180,255,0.2) !important; color: #00b4ff !important; }
</style>
""", unsafe_allow_html=True)

# ── CONSTANTS ─────────────────────────────────────────────────────────────────
EXCEL_PATH = "KINERJA_CABANG_TERNATE_APRIL_2026.xlsx"

COLORS = {
    "real25": "#4fc3f7",
    "rka26":  "#ffb74d",
    "real26": "#00e676",
    "biaya":  "#ff5252",
    "laba":   "#ce93d8",
    "kom":    "#00b4ff",
    "tis":    "#ffb74d",
}

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="rgba(255,255,255,0.85)", family="Plus Jakarta Sans"),
    margin=dict(l=10, r=10, t=44, b=10),
    legend=dict(bgcolor="rgba(0,0,0,0)", borderwidth=0),
    xaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.1)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.1)"),
)

def pl(**overrides):
    """Return PLOTLY_LAYOUT dengan override aman (menghindari duplicate keyword)."""
    layout = dict(PLOTLY_LAYOUT)
    layout.update(overrides)
    return layout

def fmt_rupiah(v):
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
    """Load sheet gabungan (Gab Kapal, Gab Kapal Kom, Gab Pelabuhan).
    Struktur sama dengan Rekap sd/bulan: row per baris akun, kolom bulanan."""
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
    """
    Load detail per kapal/pelabuhan.
    PERBAIKAN: Menggunakan logika kolom yang SAMA dengan load_gab_sheet dan
    load_rekap_sd (COL_MAP Jan-Apr dengan indeks 2-4, 7-9, 12-14, 17-19).
    """
    df = pd.read_excel(EXCEL_PATH, sheet_name=sheet_name, header=None)
    # Sama persis dengan load_gab_sheet
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
                records.append({
                    "Keterangan": keterangan, "Bulan": bulan,
                    "REAL_2025": v25, "RKA_2026": vrka, "REAL_2026": v26,
                })
            except: pass
    # Ambil nama kapal dari baris header sheet (baris 4 atau 5)
    kapal_name = ""
    for ri in range(0, 8):
        try:
            cell = str(df.iloc[ri, 1]).strip()
            if cell and cell != "nan" and ("KMP." in cell.upper() or "PELABUHAN" in cell.upper() or len(cell) > 3):
                kapal_name = cell
                break
        except: pass
    if not kapal_name:
        kapal_name = sheet_name
    return pd.DataFrame(records), kapal_name

# ── HELPER CHARTS ──────────────────────────────────────────────────────────
def pie_segmen(labels, values, colors_list, title, height=320):
    """Pie chart donut untuk segmen komersil/perintis."""
    # Filter nilai > 0
    filtered = [(l, v, c) for l, v, c in zip(labels, values, colors_list) if v > 0]
    if not filtered:
        return None
    fl, fv, fc = zip(*filtered)
    fig = go.Figure(go.Pie(
        labels=fl, values=fv,
        hole=0.55,
        marker=dict(colors=list(fc), line=dict(color="rgba(0,0,0,0.3)", width=1.5)),
        textinfo="label+percent",
        textfont_size=11,
        insidetextorientation="radial",
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text=title, font_size=13),
        height=height,
        showlegend=False,
    )
    return fig

def waterfall_chart(labels, values, title):
    colors = ["#00e676" if v >= 0 else "#ff5252" for v in values]
    fig = go.Figure(go.Bar(x=labels, y=values, marker_color=colors,
                           text=[fmt_rupiah(v) for v in values], textposition="outside",
                           textfont_size=10))
    fig.update_layout(**PLOTLY_LAYOUT, title=dict(text=title, font_size=13), height=320)
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

def safe_val(df_rows, col):
    if not df_rows.empty:
        v = df_rows.iloc[0][col]
        try: return float(v)
        except: return 0.0
    return 0.0

def get_total(df, uraian_keyword):
    row = df[df["URAIAN"].str.contains(uraian_keyword, case=False, na=False)]
    if not row.empty: return row.iloc[0]
    return None

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: RINGKASAN GABUNGAN
# ══════════════════════════════════════════════════════════════════════════════
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

    # ── KPI CARDS: urutan = Pend Bulan | Laba Bulan | Pend s/d | Laba s/d ──
    tot_sd   = df_sd[df_sd["URAIAN"].str.contains("TOTAL KESELURUHAN", case=False, na=False)]
    tot_apr  = df_april[df_april["URAIAN"].str.contains("TOTAL KESELURUHAN", case=False, na=False)]

    pend_bulan = safe_val(tot_apr, "PEND_REAL26")
    laba_bulan = safe_val(tot_apr, "LABA_REAL26")
    pend_sd    = safe_val(tot_sd,  "PEND_REAL26")
    laba_sd    = safe_val(tot_sd,  "LABA_REAL26")

    pend_bulan_rka = safe_val(tot_apr, "PEND_RKAC26")
    laba_bulan_rka = safe_val(tot_apr, "LABA_RKAC26")
    pend_sd_rka    = safe_val(tot_sd,  "PEND_RKAC26")
    laba_sd_rka    = safe_val(tot_sd,  "LABA_RKAC26")

    pend_bulan_25 = safe_val(tot_apr, "PEND_REAL25")
    laba_bulan_25 = safe_val(tot_apr, "LABA_REAL25")
    pend_sd_25    = safe_val(tot_sd,  "PEND_REAL25")
    laba_sd_25    = safe_val(tot_sd,  "LABA_REAL25")

    def ach_str(real, rka): return f"{real/rka*100:.1f}%" if rka else "–"
    def grw_str(real, prev):
        if not prev: return "–"
        g = (real - prev) / abs(prev) * 100
        icon = "▲" if g >= 0 else "▼"
        cls  = "delta-pos" if g >= 0 else "delta-neg"
        return f"<span class='{cls}'>{icon} {abs(g):.1f}% vs 2025</span>"

    laba_bulan_cls = "rugi" if laba_bulan < 0 else ""
    laba_sd_cls    = "rugi" if laba_sd    < 0 else ""

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class='kpi-card kpi-pend-bulan'>
            <div class='kpi-icon'>💰</div>
            <div class='kpi-label'>Pendapatan Bulan Ini (April)</div>
            <div class='kpi-value'>{fmt_rupiah(pend_bulan)}</div>
            <div class='kpi-sub'>RKA: {fmt_rupiah(pend_bulan_rka)} · Ach: {ach_str(pend_bulan, pend_bulan_rka)}</div>
            <div class='kpi-delta'>{grw_str(pend_bulan, pend_bulan_25)}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class='kpi-card kpi-laba-bulan {laba_bulan_cls}'>
            <div class='kpi-icon'>{'📈' if laba_bulan >= 0 else '📉'}</div>
            <div class='kpi-label'>Laba Bulan Ini (April)</div>
            <div class='kpi-value'>{fmt_rupiah(laba_bulan)}</div>
            <div class='kpi-sub'>RKA: {fmt_rupiah(laba_bulan_rka)} · Ach: {ach_str(laba_bulan, laba_bulan_rka)}</div>
            <div class='kpi-delta'>{grw_str(laba_bulan, laba_bulan_25)}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class='kpi-card kpi-pend-sd'>
            <div class='kpi-icon'>🏦</div>
            <div class='kpi-label'>Pendapatan s/d April 2026</div>
            <div class='kpi-value'>{fmt_rupiah(pend_sd)}</div>
            <div class='kpi-sub'>RKA: {fmt_rupiah(pend_sd_rka)} · Ach: {ach_str(pend_sd, pend_sd_rka)}</div>
            <div class='kpi-delta'>{grw_str(pend_sd, pend_sd_25)}</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class='kpi-card kpi-laba-sd {laba_sd_cls}'>
            <div class='kpi-icon'>{'✅' if laba_sd >= 0 else '⚠️'}</div>
            <div class='kpi-label'>Laba s/d April 2026</div>
            <div class='kpi-value'>{fmt_rupiah(laba_sd)}</div>
            <div class='kpi-sub'>RKA: {fmt_rupiah(laba_sd_rka)} · Ach: {ach_str(laba_sd, laba_sd_rka)}</div>
            <div class='kpi-delta'>{grw_str(laba_sd, laba_sd_25)}</div>
        </div>""", unsafe_allow_html=True)

    # ── PENDAPATAN PER KAPAL (menggantikan Omzet Penjualan Tiket) ────────────
    st.markdown("<div class='section-header'>PENDAPATAN PER KAPAL</div>", unsafe_allow_html=True)

    # Ambil baris kapal dari rekap sd
    df_kapal_all = df_sd[df_sd["URAIAN"].str.startswith("KMP.")].copy()
    df_kapal_all = df_kapal_all[df_kapal_all["PEND_REAL26"] != 0].reset_index(drop=True)

    # Pisahkan komersil vs perintis berdasarkan kolom URAIAN
    df_kom = df_kapal_all[df_kapal_all["URAIAN"].str.contains("Kom|Komersil", case=False, na=False)].copy()
    df_tis = df_kapal_all[df_kapal_all["URAIAN"].str.contains("Tis|Perintis", case=False, na=False)].copy()

    col_bar, col_pies = st.columns([3, 2])

    with col_bar:
        # Bar chart pendapatan per kapal
        fig_bar = go.Figure()
        if not df_kom.empty:
            fig_bar.add_trace(go.Bar(
                name="Komersil", x=df_kom["URAIAN"], y=df_kom["PEND_REAL26"],
                marker_color=COLORS["kom"], opacity=0.9,
                customdata=np.stack([df_kom["BIAYA_REAL26"], df_kom["LABA_REAL26"]], axis=-1),
                hovertemplate="<b>%{x}</b><br>Pendapatan: %{y:,.0f}<br>Biaya: %{customdata[0]:,.0f}<br>Laba: %{customdata[1]:,.0f}<extra></extra>"
            ))
        if not df_tis.empty:
            fig_bar.add_trace(go.Bar(
                name="Perintis", x=df_tis["URAIAN"], y=df_tis["PEND_REAL26"],
                marker_color=COLORS["tis"], opacity=0.9,
                customdata=np.stack([df_tis["BIAYA_REAL26"], df_tis["LABA_REAL26"]], axis=-1),
                hovertemplate="<b>%{x}</b><br>Pendapatan: %{y:,.0f}<br>Biaya: %{customdata[0]:,.0f}<br>Laba: %{customdata[1]:,.0f}<extra></extra>"
            ))
        fig_bar.update_layout(
            **PLOTLY_LAYOUT,
            title="Pendapatan Real 2026 per Kapal (s/d April)",
            barmode="group", height=400,
            xaxis_tickangle=-35, yaxis_tickformat=".2s"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_pies:
        # Pie Komersil – proporsi pendapatan
        st.markdown("<p style='color:rgba(255,255,255,0.5);font-size:0.78rem;font-weight:600;text-align:center;margin:0'>KOMERSIL – Proporsi Pendapatan</p>", unsafe_allow_html=True)
        if not df_kom.empty:
            fig_pie_kom = go.Figure(go.Pie(
                labels=[u.replace("KMP. ", "").split(" (")[0] for u in df_kom["URAIAN"]],
                values=df_kom["PEND_REAL26"],
                hole=0.5,
                marker=dict(
                    colors=px.colors.qualitative.Set2[:len(df_kom)],
                    line=dict(color="rgba(0,0,0,0.3)", width=1.5)
                ),
                textinfo="label+percent",
                textfont_size=9,
            ))
            fig_pie_kom.update_layout(**pl(height=195, showlegend=False, margin=dict(l=4,r=4,t=8,b=4)))
            st.plotly_chart(fig_pie_kom, use_container_width=True)
        else:
            st.info("Tidak ada data komersil")

        st.markdown("<p style='color:rgba(255,255,255,0.5);font-size:0.78rem;font-weight:600;text-align:center;margin:0'>PERINTIS – Proporsi Pendapatan</p>", unsafe_allow_html=True)
        if not df_tis.empty:
            fig_pie_tis = go.Figure(go.Pie(
                labels=[u.replace("KMP. ", "").split(" (")[0] for u in df_tis["URAIAN"]],
                values=df_tis["PEND_REAL26"],
                hole=0.5,
                marker=dict(
                    colors=px.colors.qualitative.Pastel[:len(df_tis)],
                    line=dict(color="rgba(0,0,0,0.3)", width=1.5)
                ),
                textinfo="label+percent",
                textfont_size=9,
            ))
            fig_pie_tis.update_layout(**pl(height=195, showlegend=False, margin=dict(l=4,r=4,t=8,b=4)))
            st.plotly_chart(fig_pie_tis, use_container_width=True)
        else:
            st.info("Tidak ada data perintis")

    # ── Tabel Pendapatan + Biaya + Laba per Kapal ────────────────────────────
    st.markdown("<div class='section-header'>RINCIAN BIAYA & LABA PER KAPAL</div>", unsafe_allow_html=True)

    tab_kom, tab_tis = st.tabs(["⛴️ Kapal Komersil", "🚢 Kapal Perintis"])

    def render_kapal_table(df_k, label_segmen):
        if df_k.empty:
            st.info(f"Tidak ada data {label_segmen}")
            return
        col_a, col_b = st.columns(2)
        with col_a:
            # Bar: Pendapatan vs Biaya
            fig = go.Figure()
            fig.add_trace(go.Bar(name="Pendapatan", x=df_k["URAIAN"],
                                 y=df_k["PEND_REAL26"], marker_color=COLORS["real26"]))
            fig.add_trace(go.Bar(name="Biaya", x=df_k["URAIAN"],
                                 y=df_k["BIAYA_REAL26"], marker_color=COLORS["biaya"]))
            fig.update_layout(**PLOTLY_LAYOUT,
                              title=f"Pendapatan vs Biaya – {label_segmen}",
                              barmode="group", height=320,
                              xaxis_tickangle=-30, yaxis_tickformat=".2s")
            st.plotly_chart(fig, use_container_width=True)
        with col_b:
            # Bar: Laba/Rugi
            colors_l = [COLORS["real26"] if v >= 0 else COLORS["biaya"] for v in df_k["LABA_REAL26"]]
            fig2 = go.Figure(go.Bar(
                x=df_k["URAIAN"], y=df_k["LABA_REAL26"],
                marker_color=colors_l,
                text=[fmt_rupiah(v) for v in df_k["LABA_REAL26"]],
                textposition="outside", textfont_size=9
            ))
            fig2.update_layout(**PLOTLY_LAYOUT,
                               title=f"Laba Bersih – {label_segmen}",
                               height=320, xaxis_tickangle=-30, yaxis_tickformat=".2s")
            st.plotly_chart(fig2, use_container_width=True)

        # Tabel detail
        df_tbl = df_k[["URAIAN","PEND_REAL26","BIAYA_REAL26","LABA_REAL26","PEND_RKAC26","LABA_RKAC26"]].copy()
        df_tbl["Ach (%)"] = (df_tbl["PEND_REAL26"] / df_tbl["PEND_RKAC26"].replace(0, np.nan) * 100).round(1)
        df_tbl["Status"]  = df_tbl["LABA_REAL26"].apply(lambda x: "✅ Profit" if x > 0 else "❌ Rugi")
        for c in ["PEND_REAL26","BIAYA_REAL26","LABA_REAL26","PEND_RKAC26","LABA_RKAC26"]:
            df_tbl[c] = df_tbl[c].apply(fmt_rupiah)
        df_tbl.columns = ["Kapal","Pend Real '26","Biaya Real '26","Laba Real '26",
                           "Pend RKA '26","Laba RKA '26","Ach (%)","Status"]
        st.dataframe(df_tbl, use_container_width=True, height=300)

    with tab_kom:
        render_kapal_table(df_kom, "Komersil")
    with tab_tis:
        render_kapal_table(df_tis, "Perintis")

    # ── PENDAPATAN PELABUHAN ──────────────────────────────────────────────────
    st.markdown("<div class='section-header'>PENDAPATAN PELABUHAN</div>", unsafe_allow_html=True)

    pel_data = []
    for pel, kw in [("Bastiong","BASTIONG"),("Sidangole","SIDANGOLE"),("Rum","RUM")]:
        r = df_sd[df_sd["URAIAN"].str.contains(kw, case=False, na=False)]
        if not r.empty:
            pel_data.append({
                "Pelabuhan":        pel,
                "Pend Real '26":    float(r.iloc[0]["PEND_REAL26"]),
                "Biaya Real '26":   float(r.iloc[0]["BIAYA_REAL26"]),
                "Laba Real '26":    float(r.iloc[0]["LABA_REAL26"]),
                "Pend RKAC '26":    float(r.iloc[0]["PEND_RKAC26"]),
            })

    if pel_data:
        df_pel = pd.DataFrame(pel_data)

        cp1, cp2, cp3 = st.columns(3)

        with cp1:
            # Pie pendapatan pelabuhan
            fig_pp = go.Figure(go.Pie(
                labels=df_pel["Pelabuhan"],
                values=df_pel["Pend Real '26"],
                hole=0.55,
                marker=dict(
                    colors=["#00b4ff","#00e676","#ffb74d"],
                    line=dict(color="rgba(0,0,0,0.3)", width=1.5)
                ),
                textinfo="label+percent",
                textfont_size=12,
            ))
            fig_pp.update_layout(
                **PLOTLY_LAYOUT,
                title="Proporsi Pendapatan Pelabuhan",
                height=300, showlegend=False,
                annotations=[dict(text="Pendapatan", x=0.5, y=0.5,
                                  font_size=11, showarrow=False,
                                  font_color="rgba(255,255,255,0.6)")]
            )
            st.plotly_chart(fig_pp, use_container_width=True)

        with cp2:
            # Pie biaya pelabuhan
            fig_pb = go.Figure(go.Pie(
                labels=df_pel["Pelabuhan"],
                values=df_pel["Biaya Real '26"],
                hole=0.55,
                marker=dict(
                    colors=["#ff5252","#ff8a65","#ef9a9a"],
                    line=dict(color="rgba(0,0,0,0.3)", width=1.5)
                ),
                textinfo="label+percent",
                textfont_size=12,
            ))
            fig_pb.update_layout(
                **PLOTLY_LAYOUT,
                title="Proporsi Biaya Pelabuhan",
                height=300, showlegend=False,
                annotations=[dict(text="Biaya", x=0.5, y=0.5,
                                  font_size=11, showarrow=False,
                                  font_color="rgba(255,255,255,0.6)")]
            )
            st.plotly_chart(fig_pb, use_container_width=True)

        with cp3:
            # Bar laba/rugi pelabuhan
            colors_l = [COLORS["real26"] if v >= 0 else COLORS["biaya"] for v in df_pel["Laba Real '26"]]
            fig_pl = go.Figure(go.Bar(
                x=df_pel["Pelabuhan"], y=df_pel["Laba Real '26"],
                marker_color=colors_l,
                text=[fmt_rupiah(v) for v in df_pel["Laba Real '26"]],
                textposition="outside", textfont_size=11
            ))
            fig_pl.update_layout(**PLOTLY_LAYOUT, title="Laba/Rugi per Pelabuhan",
                                 height=300, yaxis_tickformat=".2s")
            st.plotly_chart(fig_pl, use_container_width=True)

        # KPI cards pelabuhan
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

    # ── Tabel Rekap ──────────────────────────────────────────────────────────
    st.markdown("<div class='section-header'>TABEL REKAP s/d APRIL 2026</div>", unsafe_allow_html=True)
    df_show = df_sd[["URAIAN","PEND_REAL25","PEND_RKAC26","PEND_REAL26",
                      "BIAYA_REAL26","LABA_REAL25","LABA_RKAC26","LABA_REAL26"]].copy()
    df_show.columns = ["Uraian","Pend Real '25","Pend RKAC '26","Pend Real '26",
                       "Biaya Real '26","Laba Real '25","Laba RKAC '26","Laba Real '26"]
    for c in df_show.columns[1:]:
        df_show[c] = df_show[c].apply(lambda x: fmt_rupiah(x) if pd.notna(x) else "-")
    st.dataframe(df_show, use_container_width=True, height=400,
                 column_config={"Uraian": st.column_config.TextColumn(width="large")})

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: GABUNGAN KAPAL
# ══════════════════════════════════════════════════════════════════════════════
elif "Gabungan Kapal" in menu:
    st.markdown("<h1 style='font-size:1.8rem;font-weight:800;color:#fff'>🚢 Gabungan Kinerja Kapal</h1>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["⛴️ Semua Kapal (Perintis & Komersil)", "📊 Komersil Saja"])

    with tab1:
        df_kapal = df_sd[df_sd["URAIAN"].str.startswith("KMP.")].copy()
        df_kapal = df_kapal[df_kapal["PEND_REAL26"] != 0].reset_index(drop=True)

        if not df_kapal.empty:
            col1, col2 = st.columns([3, 2])
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

            st.markdown("<div class='section-header'>DETAIL KINERJA PER KAPAL</div>", unsafe_allow_html=True)
            df_tbl = df_kapal[["URAIAN","PEND_REAL26","BIAYA_REAL26","LABA_REAL26",
                                "PEND_RKAC26","LABA_RKAC26"]].copy()
            df_tbl["Ach (%)"] = (df_tbl["PEND_REAL26"] / df_tbl["PEND_RKAC26"].replace(0, np.nan) * 100).round(1)
            df_tbl["Status"] = df_tbl["LABA_REAL26"].apply(lambda x: "✅ Profit" if x > 0 else "❌ Rugi")
            for c in ["PEND_REAL26","BIAYA_REAL26","LABA_REAL26","PEND_RKAC26","LABA_RKAC26"]:
                df_tbl[c] = df_tbl[c].apply(fmt_rupiah)
            df_tbl.columns = ["Kapal","Pend Real '26","Biaya Real '26","Laba Real '26",
                               "Pend RKA '26","Laba RKA '26","Ach (%)","Status"]
            st.dataframe(df_tbl, use_container_width=True, height=420)

    with tab2:
        df_kom_detail = df_sd[df_sd["URAIAN"].str.contains("Komersil|Kom", case=False, na=False)].copy()
        df_kom_detail = df_kom_detail[df_kom_detail["URAIAN"].str.startswith("KMP.")].copy()
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

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DETAIL PER KAPAL
# ══════════════════════════════════════════════════════════════════════════════
elif "Detail Per Kapal" in menu:
    st.markdown("<h1 style='font-size:1.8rem;font-weight:800;color:#fff'>⚓ Detail Kinerja Per Kapal</h1>", unsafe_allow_html=True)

    # Nama sheet disesuaikan dengan 47 sheet yang ada di file Excel
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
            st.warning("Data tidak tersedia untuk kapal ini.")
        else:
            # ── KPI dari rekap sd ──
            # Coba cocokkan dengan berbagai variasi nama
            kapal_base = selected.split("(")[0].strip().replace("KMP. ", "").strip()
            segmen_kw  = "Komersil" if "Komersil" in selected else "Perintis"
            row_sd = df_sd[
                df_sd["URAIAN"].str.contains(kapal_base, case=False, na=False) &
                df_sd["URAIAN"].str.contains(segmen_kw, case=False, na=False)
            ]
            if row_sd.empty:
                # Fallback: cari hanya nama kapal
                row_sd = df_sd[df_sd["URAIAN"].str.contains(kapal_base, case=False, na=False)]

            if not row_sd.empty:
                r = row_sd.iloc[0]
                c1, c2, c3, c4 = st.columns(4)
                kpis = [
                    ("💰 Pendapatan Real '26", float(r["PEND_REAL26"]), float(r["PEND_RKAC26"])),
                    ("📉 Biaya Real '26",      float(r["BIAYA_REAL26"]), float(r["BIAYA_RKAC26"])),
                    ("📈 Laba/Rugi Real '26",  float(r["LABA_REAL26"]), float(r["LABA_RKAC26"])),
                    ("📊 Pendapatan Real '25", float(r["PEND_REAL25"]), float(r["PEND_REAL26"])),
                ]
                for col, (lbl, v26, base) in zip([c1,c2,c3,c4], kpis):
                    ach = (v26/base*100) if base and base != 0 else 0
                    delta_cls = "delta-pos" if v26 >= 0 else "delta-neg"
                    with col:
                        st.markdown(f"""
                        <div class='metric-card'>
                            <div class='metric-label'>{lbl}</div>
                            <div class='metric-value'>{fmt_rupiah(v26)}</div>
                            <div class='metric-delta {delta_cls}'>Ach: {ach:.1f}%</div>
                        </div>""", unsafe_allow_html=True)

            # ── Trend bulanan ──
            months_avail = ["JANUARI","FEBRUARI","MARET","APRIL"]
            pend_vals, biaya_vals, laba_vals = [], [], []
            rka_pend, rka_biaya = [], []

            PEND_KEYWORDS  = ["PENDAPATAN USAHA","JUMLAH PENDAPATAN","TOTAL PENDAPATAN"]
            BIAYA_KEYWORDS = ["JUMLAH BEBAN","BEBAN USAHA","JUMLAH BIAYA","TOTAL BEBAN","JUMLAH PENGELUARAN"]

            for m in months_avail:
                dm = df_detail[df_detail["Bulan"] == m]
                pend_row  = dm[dm["Keterangan"].str.upper().str.contains("|".join(PEND_KEYWORDS),  na=False)]
                biaya_row = dm[dm["Keterangan"].str.upper().str.contains("|".join(BIAYA_KEYWORDS), na=False)]

                pv = float(pend_row.iloc[-1]["REAL_2026"])  if not pend_row.empty  else 0
                bv = float(biaya_row.iloc[-1]["REAL_2026"]) if not biaya_row.empty else 0
                rp = float(pend_row.iloc[-1]["RKA_2026"])   if not pend_row.empty  else 0
                rb = float(biaya_row.iloc[-1]["RKA_2026"])  if not biaya_row.empty else 0

                pend_vals.append(pv); biaya_vals.append(bv)
                rka_pend.append(rp);  rka_biaya.append(rb)
                laba_vals.append(pv - bv)

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
                bar_colors = [COLORS["real26"] if v >= 0 else COLORS["biaya"] for v in laba_vals]
                fig2 = go.Figure(go.Bar(x=months_avail, y=laba_vals, marker_color=bar_colors,
                    text=[fmt_rupiah(v) for v in laba_vals], textposition="outside", textfont_size=9))
                fig2.update_layout(**PLOTLY_LAYOUT, title="Laba/Rugi Bulanan", height=300, yaxis_tickformat=".2s")
                st.plotly_chart(fig2, use_container_width=True)

            # ── Rincian Akun ──
            st.markdown("<div class='section-header'>RINCIAN AKUN – APRIL 2026</div>", unsafe_allow_html=True)
            df_apr_detail = df_detail[df_detail["Bulan"] == "APRIL"].copy()

            # Filter: tampilkan baris yang minimal ada satu nilai ≠ 0
            mask = (df_apr_detail["REAL_2025"] != 0) | (df_apr_detail["RKA_2026"] != 0) | (df_apr_detail["REAL_2026"] != 0)
            df_apr_display = df_apr_detail[mask][["Keterangan","REAL_2025","RKA_2026","REAL_2026"]].copy()
            df_apr_display["Ach (%)"] = (
                df_apr_display["REAL_2026"] /
                df_apr_display["RKA_2026"].replace(0, np.nan) * 100
            ).round(1)
            for c in ["REAL_2025","RKA_2026","REAL_2026"]:
                df_apr_display[c] = df_apr_display[c].apply(fmt_rupiah)
            df_apr_display.columns = ["Keterangan","Real 2025","RKA 2026","Real 2026","Ach (%)"]
            st.dataframe(df_apr_display, use_container_width=True, height=450)

    except Exception as e:
        st.error(f"Gagal memuat data kapal: {e}")
        st.info("Pastikan nama sheet di KAPAL_SHEETS sesuai dengan file Excel.")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: GABUNGAN PELABUHAN
# ══════════════════════════════════════════════════════════════════════════════
elif "Pelabuhan" in menu:
    st.markdown("<h1 style='font-size:1.8rem;font-weight:800;color:#fff'>🏗️ Kinerja Pelabuhan</h1>", unsafe_allow_html=True)

    PELABUHAN_SHEETS = {
        "BASTIONG":  "Bastiong",
        "SIDANGOLI": "Sidangoli",
        "RUM":       "Rum",
    }

    # ── Summary dari rekap ───────────────────────────────────────────────────
    st.markdown("<div class='section-header'>RINGKASAN KINERJA PELABUHAN (s/d April 2026)</div>", unsafe_allow_html=True)
    pel_data = []
    for pel, kw in [("Bastiong","BASTIONG"),("Sidangole","SIDANGOLE"),("Rum","RUM")]:
        r = df_sd[df_sd["URAIAN"].str.contains(kw, case=False, na=False)]
        if not r.empty:
            pel_data.append({
                "Pelabuhan":      pel,
                "Pend Real '26":  float(r.iloc[0]["PEND_REAL26"]),
                "Biaya Real '26": float(r.iloc[0]["BIAYA_REAL26"]),
                "Laba Real '26":  float(r.iloc[0]["LABA_REAL26"]),
                "Pend RKAC '26":  float(r.iloc[0]["PEND_RKAC26"]),
            })

    if pel_data:
        df_pel = pd.DataFrame(pel_data)

        cp1, cp2, cp3 = st.columns(3)

        with cp1:
            fig_pp = go.Figure(go.Pie(
                labels=df_pel["Pelabuhan"],
                values=df_pel["Pend Real '26"],
                hole=0.55,
                marker=dict(colors=["#00b4ff","#00e676","#ffb74d"],
                            line=dict(color="rgba(0,0,0,0.3)", width=1.5)),
                textinfo="label+percent", textfont_size=12,
            ))
            fig_pp.update_layout(**PLOTLY_LAYOUT, title="Proporsi Pendapatan",
                                 height=300, showlegend=False,
                                 annotations=[dict(text="Pendapatan", x=0.5, y=0.5,
                                                   font_size=11, showarrow=False,
                                                   font_color="rgba(255,255,255,0.6)")])
            st.plotly_chart(fig_pp, use_container_width=True)

        with cp2:
            fig_pb = go.Figure(go.Pie(
                labels=df_pel["Pelabuhan"],
                values=df_pel["Biaya Real '26"],
                hole=0.55,
                marker=dict(colors=["#ff5252","#ff8a65","#ef9a9a"],
                            line=dict(color="rgba(0,0,0,0.3)", width=1.5)),
                textinfo="label+percent", textfont_size=12,
            ))
            fig_pb.update_layout(**PLOTLY_LAYOUT, title="Proporsi Biaya",
                                 height=300, showlegend=False,
                                 annotations=[dict(text="Biaya", x=0.5, y=0.5,
                                                   font_size=11, showarrow=False,
                                                   font_color="rgba(255,255,255,0.6)")])
            st.plotly_chart(fig_pb, use_container_width=True)

        with cp3:
            colors_l = [COLORS["real26"] if v >= 0 else COLORS["biaya"] for v in df_pel["Laba Real '26"]]
            fig_pl = go.Figure(go.Bar(
                x=df_pel["Pelabuhan"], y=df_pel["Laba Real '26"],
                marker_color=colors_l,
                text=[fmt_rupiah(v) for v in df_pel["Laba Real '26"]],
                textposition="outside", textfont_size=12
            ))
            fig_pl.update_layout(**PLOTLY_LAYOUT, title="Laba/Rugi Pelabuhan",
                                 height=300, yaxis_tickformat=".2s")
            st.plotly_chart(fig_pl, use_container_width=True)

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

    # ── Detail per pelabuhan ──────────────────────────────────────────────────
    st.markdown("<div class='section-header'>DETAIL AKUN PELABUHAN</div>", unsafe_allow_html=True)
    sel_pel = st.selectbox("Pilih Pelabuhan", list(PELABUHAN_SHEETS.keys()))
    try:
        with st.spinner(f"Memuat data Pelabuhan {sel_pel}..."):
            # PERBAIKAN: gunakan load_kapal_detail (logika sudah diperbaiki = sama dg rekap)
            df_p, p_lbl = load_kapal_detail(PELABUHAN_SHEETS[sel_pel])

        if not df_p.empty:
            months_avail = ["JANUARI","FEBRUARI","MARET","APRIL"]
            PEND_KEYWORDS  = ["PENDAPATAN USAHA","JUMLAH PENDAPATAN","TOTAL PENDAPATAN"]
            BIAYA_KEYWORDS = ["JUMLAH BEBAN","BEBAN USAHA","JUMLAH BIAYA","TOTAL BEBAN"]

            pend_vals, biaya_vals = [], []
            for m in months_avail:
                dm = df_p[df_p["Bulan"] == m]
                pr = dm[dm["Keterangan"].str.upper().str.contains("|".join(PEND_KEYWORDS), na=False)]
                br = dm[dm["Keterangan"].str.upper().str.contains("|".join(BIAYA_KEYWORDS), na=False)]
                pend_vals.append(float(pr.iloc[-1]["REAL_2026"])  if not pr.empty else 0)
                biaya_vals.append(float(br.iloc[-1]["REAL_2026"]) if not br.empty else 0)

            laba_vals_p = [p - b for p, b in zip(pend_vals, biaya_vals)]

            col_a, col_b = st.columns(2)
            with col_a:
                fig3 = go.Figure()
                fig3.add_trace(go.Scatter(x=months_avail, y=pend_vals, name="Pendapatan",
                    mode="lines+markers", line=dict(color=COLORS["real26"], width=2.5),
                    fill="tozeroy", fillcolor="rgba(0,230,118,0.06)"))
                fig3.add_trace(go.Scatter(x=months_avail, y=biaya_vals, name="Biaya",
                    mode="lines+markers", line=dict(color=COLORS["biaya"], width=2, dash="dot")))
                fig3.update_layout(**PLOTLY_LAYOUT, title=f"Tren Pendapatan & Biaya – {sel_pel}",
                                   height=280, yaxis_tickformat=".2s")
                st.plotly_chart(fig3, use_container_width=True)

            with col_b:
                bar_c = [COLORS["real26"] if v >= 0 else COLORS["biaya"] for v in laba_vals_p]
                fig4 = go.Figure(go.Bar(x=months_avail, y=laba_vals_p, marker_color=bar_c,
                    text=[fmt_rupiah(v) for v in laba_vals_p], textposition="outside", textfont_size=9))
                fig4.update_layout(**PLOTLY_LAYOUT, title=f"Laba/Rugi – {sel_pel}", height=280, yaxis_tickformat=".2s")
                st.plotly_chart(fig4, use_container_width=True)

            # Tabel rincian April
            df_p_apr = df_p[df_p["Bulan"] == "APRIL"].copy()
            mask = (df_p_apr["REAL_2025"] != 0) | (df_p_apr["RKA_2026"] != 0) | (df_p_apr["REAL_2026"] != 0)
            df_p_apr = df_p_apr[mask][["Keterangan","REAL_2025","RKA_2026","REAL_2026"]].copy()
            df_p_apr["Ach (%)"] = (
                df_p_apr["REAL_2026"] / df_p_apr["RKA_2026"].replace(0, np.nan) * 100
            ).round(1)
            for c in ["REAL_2025","RKA_2026","REAL_2026"]:
                df_p_apr[c] = df_p_apr[c].apply(fmt_rupiah)
            df_p_apr.columns = ["Keterangan","Real 2025","RKA 2026","Real 2026","Ach (%)"]
            st.dataframe(df_p_apr, use_container_width=True, height=400)
        else:
            st.warning("Data tidak ditemukan untuk pelabuhan ini.")
    except Exception as e:
        st.error(f"Gagal memuat detail pelabuhan: {e}")
        st.info("Pastikan nama sheet di PELABUHAN_SHEETS sesuai dengan file Excel.")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ANALISIS TREN
# ══════════════════════════════════════════════════════════════════════════════
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
        df_total = df_trend[df_trend["Tipe"].isin(["Pendapatan","Biaya","Laba/ Rugi"])].groupby(
            ["Bulan","Tipe"])[["REAL_2025","RKA_2026","REAL_2026"]].sum().reset_index()
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

        st.markdown("<div class='section-header'>TREN PENDAPATAN PER KAPAL</div>", unsafe_allow_html=True)
        all_kapal = sorted(df_trend["Kapal"].unique())
        selected_kapal = st.multiselect("Pilih Kapal:", all_kapal, default=all_kapal[:5] if len(all_kapal) >= 5 else all_kapal)

        if selected_kapal:
            df_k_pend = df_trend[(df_trend["Tipe"] == "Pendapatan") & (df_trend["Kapal"].isin(selected_kapal))].copy()
            df_k_pend["BulanOrder"] = df_k_pend["Bulan"].map({m:i for i,m in enumerate(months_avail)})
            df_k_pend = df_k_pend.sort_values("BulanOrder")

            palette = px.colors.qualitative.Set2
            fig3 = go.Figure()
            for i, k in enumerate(selected_kapal):
                dk = df_k_pend[df_k_pend["Kapal"] == k]
                fig3.add_trace(go.Scatter(x=dk["Bulan"], y=dk["REAL_2026"], name=k[:25],
                    line=dict(color=palette[i % len(palette)], width=2), mode="lines+markers"))
            fig3.update_layout(**PLOTLY_LAYOUT, title="Tren Pendapatan Real 2026 per Kapal", height=380, yaxis_tickformat=".2s")
            st.plotly_chart(fig3, use_container_width=True)

            df_k_ach = df_trend[(df_trend["Tipe"] == "Pendapatan") & (df_trend["Kapal"].isin(selected_kapal))].copy()
            df_k_ach["Ach (%)"] = (df_k_ach["REAL_2026"] / df_k_ach["RKA_2026"].replace(0, np.nan) * 100).round(1)
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
