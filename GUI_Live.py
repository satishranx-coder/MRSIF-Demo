
import streamlit as st
import numpy as np
import plotly.graph_objects as go
from dataclasses import dataclass
from typing import Dict, List, Tuple
from datetime import datetime, timezone
from pathlib import Path
import base64

# ============================================================
# VODIDS | MRSIF v4.0 — Mission Intelligence GUI Prototype
# ============================================================

st.set_page_config(
    page_title="VODIDS | MRSIF Mission Intelligence",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def get_logo_html(path: str = "VODIDS.png") -> str:
    """Render the VODIDS logo in the custom top bar with a safe text fallback."""
    p = Path(path)
    if not p.exists():
        return '<div class="logo-fallback">VODIDS</div>'
    try:
        mime = "image/png"
        encoded = base64.b64encode(p.read_bytes()).decode("utf-8")
        return (
            f'<div style="width:92px;height:58px;border-radius:12px;overflow:hidden;'
            f'border:1px solid #2f6681;background:#081722;display:flex;align-items:center;'
            f'justify-content:center;">'
            f'<img src="data:{mime};base64,{encoded}" '
            f'style="width:100%;height:100%;object-fit:cover;object-position:center;" />'
            f'</div>'
        )
    except Exception:
        return '<div class="logo-fallback">VODIDS</div>'

# -----------------------------
# 1. CONFIGURATION
# -----------------------------
# Replace these labels with the exact approved MRSIF layer/application names
# when finalising the architecture.
MRSIF_CORE_LAYERS = [
    ("L0", "Safety & HSE"),
    ("L1", "Scope & Work Reference"),
    ("L2", "Asset / Vehicle Identity"),
    ("L3", "Tooling & Sensor Validation"),
    ("L4", "Robotics / Execution Intelligence"),
    ("L5", "Data Quality & Operational Evidence"),
    ("L6", "Handover / Data Delivery"),
]

MRSIF_APPLICATIONS = [
    ("A01", "Scope Intelligence"),
    ("A02", "Asset Identification"),
    ("A03", "Vehicle Qualification"),
    ("A04", "Sensor Configuration"),
    ("A05", "Tooling Compatibility"),
    ("A06", "Spatial Localization"),
    ("A07", "Photogrammetry Intelligence"),
    ("A08", "Manipulator Validation"),
    ("A09", "Environmental Assessment"),
    ("A10", "Execution Readiness"),
    ("A11", "Live Mission Assurance"),
    ("A12", "Completion Verification"),
    ("A13", "Data Handover"),
]

CFIHOS_ASSET = {
    "tag": "50-XV-0401",
    "class": "Actuated Valve Assembly",
    "class_code": "CFIHOS-10000284",
    "serial": "EQ-XT04-VLV-01",
    "interface": "API 17H",
    "required_torque_nm": 145.0,
    "pressure_rating_psi": 10000,
}

OSDU_CONTEXT = {
    "Bathymetry": "AVAILABLE",
    "Seabed Model": "AVAILABLE",
    "Survey Reference": "VERIFIED",
    "Environmental Dataset": "ACTIVE",
    "Historical Inspection": "AVAILABLE",
    "Photogrammetry Model": "ACTIVE",
}

# -----------------------------
# 2. SESSION STATE
# -----------------------------
defaults = {
    "function_test": True,
    "deck_test": True,
    "pilot_risk_confirmed": False,
    "mission_executed": False,
    "completion_verified": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# -----------------------------
# 3. STYLE
# -----------------------------
st.markdown("""
<style>
:root {
    --bg: #071019;
    --panel: #0d1824;
    --panel2: #111f2e;
    --border: #24384a;
    --text: #eef7fb;
    --muted: #8fa6b8;
    --cyan: #33d1ff;
    --blue: #4b8cff;
    --green: #2bd576;
    --amber: #ffbd4a;
    --red: #ff5f63;
}
html, body, [class*="css"] { font-family: Inter, Segoe UI, sans-serif; }
.stApp { background: radial-gradient(circle at top, #102033 0%, #071019 50%, #050b11 100%); color: var(--text); }
.block-container { max-width: 1800px; padding-top: 0.8rem; padding-bottom: 2rem; }

#MainMenu, footer, header { visibility: hidden; }

.topbar {
    display:flex; justify-content:space-between; align-items:center;
    padding:14px 18px; border:1px solid var(--border); border-radius:14px;
    background:linear-gradient(180deg, rgba(17,31,46,.98), rgba(9,20,31,.98));
    box-shadow:0 12px 32px rgba(0,0,0,.18); margin-bottom:10px;
}
.brand { display:flex; gap:14px; align-items:center; }
.logo-fallback {
    width:54px; height:54px; border-radius:13px; border:1px solid #2f6681;
    display:flex; align-items:center; justify-content:center; color:var(--cyan);
    font-weight:800; letter-spacing:1px; background:#081722;
}
.brand-title { font-size:24px; font-weight:800; letter-spacing:.6px; color:white; }
.brand-sub { font-size:12px; color:var(--muted); margin-top:2px; }
.top-status { display:flex; gap:12px; align-items:center; font-size:12px; }
.dot { width:9px; height:9px; display:inline-block; border-radius:50%; margin-right:6px; }
.dot.green { background:var(--green); box-shadow:0 0 12px rgba(43,213,118,.7); }
.dot.amber { background:var(--amber); box-shadow:0 0 12px rgba(255,189,74,.6); }
.dot.red { background:var(--red); box-shadow:0 0 12px rgba(255,95,99,.6); }

.mission-strip {
    display:grid; grid-template-columns:repeat(5,1fr); gap:8px; margin:8px 0 12px;
}
.mission-item {
    background:rgba(13,24,36,.92); border:1px solid var(--border); border-radius:10px;
    padding:10px 12px;
}
.mission-label { color:var(--muted); font-size:10px; letter-spacing:1.1px; text-transform:uppercase; }
.mission-value { color:#fff; font-size:14px; font-weight:700; margin-top:2px; }

.section-title {
    font-size:11px; font-weight:800; color:#9fc6d9; letter-spacing:1.5px;
    text-transform:uppercase; margin:3px 0 7px;
}
.app-strip {
    display:grid; grid-template-columns:repeat(13, 1fr); gap:4px; margin-bottom:10px;
}
.app-chip {
    min-height:49px; background:#0c1824; border:1px solid #26394a; border-radius:8px;
    padding:6px 5px; text-align:center; color:#8ea5b8; font-size:9px; line-height:1.15;
}
.app-chip.active {
    border-color:#33d1ff; color:white; background:linear-gradient(180deg,#123048,#0d2030);
    box-shadow:0 0 0 1px rgba(51,209,255,.12) inset;
}
.app-code { font-weight:800; color:#55d9ff; display:block; font-size:10px; margin-bottom:2px; }

.panel {
    background:linear-gradient(180deg, rgba(15,29,43,.97), rgba(9,20,31,.97));
    border:1px solid var(--border); border-radius:13px; padding:13px;
    min-height:100px;
}
.panel-header {
    display:flex; justify-content:space-between; align-items:center;
    border-bottom:1px solid #203447; padding-bottom:8px; margin-bottom:10px;
}
.panel-title { color:white; font-size:13px; font-weight:800; letter-spacing:.3px; }
.panel-sub { color:var(--muted); font-size:10px; }

.layer {
    display:grid; grid-template-columns:36px 1fr 54px; align-items:center; gap:7px;
    padding:8px 8px; border-bottom:1px solid rgba(37,58,76,.65);
}
.layer:last-child { border-bottom:none; }
.layer-code { color:#67dfff; font-weight:900; font-size:11px; }
.layer-name { color:#dbe8ef; font-size:11px; line-height:1.2; }
.badge {
    border-radius:20px; padding:3px 6px; text-align:center; font-size:9px; font-weight:800;
    border:1px solid transparent;
}
.pass { color:#72f2a5; border-color:rgba(43,213,118,.42); background:rgba(43,213,118,.08); }
.hold { color:#ffd079; border-color:rgba(255,189,74,.42); background:rgba(255,189,74,.08); }
.fail { color:#ff8d91; border-color:rgba(255,95,99,.42); background:rgba(255,95,99,.08); }
.info { color:#76dbff; border-color:rgba(51,209,255,.42); background:rgba(51,209,255,.08); }

.kpi-grid { display:grid; grid-template-columns:1fr 1fr; gap:8px; }
.kpi {
    background:#091621; border:1px solid #22384a; border-radius:10px; padding:9px;
}
.kpi-name { color:#8199aa; font-size:9px; text-transform:uppercase; letter-spacing:.8px; }
.kpi-value { color:white; font-size:18px; font-weight:800; margin-top:2px; }
.kpi-note { color:#6f8798; font-size:9px; margin-top:1px; }

.asset-row, .osdu-row {
    display:flex; justify-content:space-between; gap:10px;
    padding:5px 0; border-bottom:1px solid rgba(36,56,74,.55); font-size:10px;
}
.asset-row:last-child, .osdu-row:last-child { border-bottom:none; }
.asset-key, .osdu-key { color:#7f97aa; }
.asset-val { color:#e7f3f8; font-weight:700; text-align:right; }
.osdu-val { color:#65e3a0; font-weight:800; }

.decision {
    border-left:4px solid var(--amber); background:rgba(255,189,74,.07);
    padding:11px 12px; border-radius:8px; color:#eef7fb; font-size:11px; line-height:1.45;
}
.decision.passbox { border-left-color:var(--green); background:rgba(43,213,118,.07); }
.big-state {
    font-size:23px; font-weight:900; letter-spacing:.5px; margin:2px 0 5px;
}
.small { color:#91a8b9; font-size:10px; }

.footerbar {
    margin-top:10px; display:flex; justify-content:space-between; gap:10px;
    color:#6f8798; font-size:9px; border-top:1px solid #1e3141; padding-top:8px;
}
div[data-testid="stMetric"] {
    background:#0c1824; border:1px solid #24384a; padding:10px; border-radius:10px;
}

/* Streamlit control readability */
div[data-testid="stExpander"] {
    background: #0d1824 !important;
    border: 1px solid #24384a !important;
    border-radius: 12px !important;
}
div[data-testid="stExpander"] summary {
    color: #eef7fb !important;
    background: #111f2e !important;
    border-radius: 10px !important;
}
div[data-testid="stExpander"] summary:hover {
    background: #163047 !important;
}
div[data-testid="stExpander"] * {
    color: #eef7fb;
}
.stButton > button {
    background: linear-gradient(180deg,#15334a,#0e2334) !important;
    color: #eef7fb !important;
    border: 1px solid #2f6681 !important;
    border-radius: 10px !important;
    min-height: 44px !important;
    font-weight: 800 !important;
}
.stButton > button:hover {
    background: linear-gradient(180deg,#1d4865,#143149) !important;
    color: #ffffff !important;
    border-color: #33d1ff !important;
}
.stButton > button:disabled {
    background: #1a2631 !important;
    color: #748b9c !important;
    border: 1px solid #2a3d4c !important;
    opacity: 1 !important;
}
div[data-testid="stCheckbox"] label,
div[data-testid="stSlider"] label {
    color: #eef7fb !important;
}


/* MRSIF readable KPI cards */
.mrsif-kpi-grid {
    display:grid;
    grid-template-columns: repeat(5, minmax(0,1fr));
    gap:8px;
    margin-top:8px;
}
.mrsif-kpi {
    background:linear-gradient(180deg,#0d1a27,#0a1520);
    border:1px solid #29465c;
    border-radius:12px;
    padding:10px 10px 9px;
    min-height:112px;
    overflow:hidden;
}
.mrsif-kpi-title {
    color:#9db2c2;
    font-size:10px;
    font-weight:700;
    line-height:1.18;
    min-height:24px;
}
.mrsif-kpi-value {
    color:#f4fbff;
    font-size:27px;
    line-height:1.0;
    font-weight:900;
    margin-top:8px;
    letter-spacing:-0.4px;
}
.mrsif-kpi-unit {
    color:#8da3b4;
    font-size:10px;
    font-weight:700;
    margin-left:3px;
}
.mrsif-kpi-status {
    display:inline-block;
    margin-top:9px;
    padding:4px 7px;
    border-radius:14px;
    font-size:9px;
    font-weight:800;
    line-height:1.1;
    max-width:100%;
}
.mrsif-kpi-status.pass {
    color:#72f2a5;
    background:rgba(43,213,118,.10);
    border:1px solid rgba(43,213,118,.28);
}
.mrsif-kpi-status.hold {
    color:#ffd079;
    background:rgba(255,189,74,.10);
    border:1px solid rgba(255,189,74,.28);
}
.mrsif-kpi-note {
    color:#718a9c;
    font-size:8.5px;
    line-height:1.15;
    margin-top:6px;
}
@media (max-width: 1200px) {
  .mrsif-kpi-grid { grid-template-columns: repeat(3, minmax(0,1fr)); }
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# 4. USER CONTROLS
# -----------------------------
with st.expander("Mission Simulation Controls", expanded=False):
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metocean_current = st.slider("Seafloor current (kts)", 0.3, 3.0, 1.2, 0.1)
        visibility_m = st.slider("Visibility (m)", 0.0, 10.0, 4.5, 0.5)
    with c2:
        localization_conf = st.slider("Localization confidence (%)", 0, 100, 94)
        pointcloud_conf = st.slider("Point-cloud confidence (%)", 0, 100, 96)
    with c3:
        distance_error_pct = st.slider("ROV/target distance error (%)", 0.0, 15.0, 3.2, 0.1)
        clearance_mm = st.slider("Manipulator clearance (mm)", 0, 250, 82, 2)
    with c4:
        tool_match = st.checkbox("Correct tool/interface", True)
        dvl_lock = st.checkbox("DVL bottom lock", True)
        fls_available = st.checkbox("FLS target confirmation", True)
        st.session_state.pilot_risk_confirmed = st.checkbox(
            "Pilot risk review confirmed", st.session_state.pilot_risk_confirmed
        )

# -----------------------------
# 5. MRSIF DECISION LOGIC
# -----------------------------
metocean_pass = metocean_current <= 1.5
pointcloud_pass = pointcloud_conf >= 90
distance_pass = distance_error_pct <= 5.0
localization_pass = localization_conf >= 85 and dvl_lock
degraded_visibility = visibility_m < 1.5
visibility_supported = (not degraded_visibility) or fls_available
clearance_pass = clearance_mm >= 50

preconditions = {
    "Safety & HSE": True,
    "Scope & Work Reference": True,
    "Asset / Vehicle Identity": True,
    "Tooling & Sensor Validation": tool_match,
    "Robotics / Execution Intelligence": all([
        metocean_pass,
        pointcloud_pass,
        distance_pass,
        localization_pass,
        visibility_supported,
        clearance_pass
    ]),
    "Data Quality & Operational Evidence": True,
    "Handover / Data Delivery": st.session_state.completion_verified,
}

readiness_pass = all([
    tool_match,
    metocean_pass,
    pointcloud_pass,
    distance_pass,
    localization_pass,
    visibility_supported,
    clearance_pass,
    st.session_state.pilot_risk_confirmed,
])

if st.session_state.completion_verified:
    mission_state = "MISSION ACCOMPLISHED"
    state_class = "pass"
elif st.session_state.mission_executed:
    mission_state = "EXECUTION IN PROGRESS"
    state_class = "info"
elif readiness_pass:
    mission_state = "READY FOR INTERVENTION"
    state_class = "pass"
else:
    mission_state = "HOLD — VALIDATION REQUIRED"
    state_class = "hold"

# -----------------------------
# 6. HEADER
# -----------------------------
logo_html = get_logo_html("VODIDS.png")

st.markdown(f"""
<div class="topbar">
  <div class="brand">
    {logo_html}
    <div>
      <div class="brand-title">MRSIF <span style="color:#33d1ff;">Mission Intelligence</span></div>
      <div class="brand-sub">Marine Robotics & Subsea Intelligence Framework · VODIDS Operational Architecture</div>
    </div>
  </div>
  <div class="top-status">
    <span><span class="dot green"></span>CFIHOS CONNECTED</span>
    <span><span class="dot green"></span>OSDU CONTEXT ACTIVE</span>
    <span><span class="dot {'green' if localization_pass else 'amber'}"></span>NAVIGATION {'VALID' if localization_pass else 'CHECK'}</span>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="mission-strip">
  <div class="mission-item"><div class="mission-label">Work Ref</div><div class="mission-value">WR-2026-014</div></div>
  <div class="mission-item"><div class="mission-label">Mission</div><div class="mission-value">Subsea Tooling Validation</div></div>
  <div class="mission-item"><div class="mission-label">Asset</div><div class="mission-value">{CFIHOS_ASSET['tag']}</div></div>
  <div class="mission-item"><div class="mission-label">Vehicle</div><div class="mission-value">WROV-02</div></div>
  <div class="mission-item"><div class="mission-label">Mission State</div><div class="mission-value" style="color:{'#72f2a5' if state_class=='pass' else '#ffd079' if state_class=='hold' else '#76dbff'}">{mission_state}</div></div>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# 7. 13 APPLICATION LAYER STRIP
# -----------------------------
st.markdown('<div class="section-title">13 MRSIF Application Layers · CFIHOS-Aligned Operational Context</div>', unsafe_allow_html=True)

active_apps = {
    "A01": True, "A02": True, "A03": True, "A04": True, "A05": True,
    "A06": True, "A07": True, "A08": True, "A09": True,
    "A10": readiness_pass, "A11": st.session_state.mission_executed,
    "A12": st.session_state.completion_verified,
    "A13": st.session_state.completion_verified,
}
chips = ""
for code, name in MRSIF_APPLICATIONS:
    cls = "app-chip active" if active_apps.get(code, False) else "app-chip"
    chips += f'<div class="{cls}"><span class="app-code">{code}</span>{name}</div>'
st.markdown(f'<div class="app-strip">{chips}</div>', unsafe_allow_html=True)

# -----------------------------
# 8. MAIN MISSION CONTROL GRID
# -----------------------------
left, center, right = st.columns([1.05, 2.6, 1.2], gap="small")

# LEFT — 7 core layers + asset identity
with left:
    st.markdown('<div class="panel"><div class="panel-header"><div><div class="panel-title">7 MRSIF Core Layers</div><div class="panel-sub">Execution governance stack</div></div></div>', unsafe_allow_html=True)
    for code, name in MRSIF_CORE_LAYERS:
        ok = preconditions.get(name, False)
        if name == "Handover / Data Delivery" and not st.session_state.completion_verified:
            badge_text, badge_cls = "LOCKED", "hold"
        elif ok:
            badge_text, badge_cls = "PASS", "pass"
        else:
            badge_text, badge_cls = "HOLD", "hold"
        st.markdown(
            f'<div class="layer"><div class="layer-code">{code}</div><div class="layer-name">{name}</div><div class="badge {badge_cls}">{badge_text}</div></div>',
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="panel"><div class="panel-header"><div><div class="panel-title">CFIHOS Asset Intelligence</div><div class="panel-sub">Authoritative equipment context</div></div></div>', unsafe_allow_html=True)
    for k, v in [
        ("Target Tag", CFIHOS_ASSET["tag"]),
        ("Class", CFIHOS_ASSET["class"]),
        ("CFIHOS Code", CFIHOS_ASSET["class_code"]),
        ("Serial", CFIHOS_ASSET["serial"]),
        ("Interface", CFIHOS_ASSET["interface"]),
        ("Required Torque", f'{CFIHOS_ASSET["required_torque_nm"]:.0f} Nm'),
        ("Pressure Rating", f'{CFIHOS_ASSET["pressure_rating_psi"]:,} PSI'),
    ]:
        st.markdown(f'<div class="asset-row"><span class="asset-key">{k}</span><span class="asset-val">{v}</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# CENTER — digital twin
with center:
    st.markdown('<div class="panel"><div class="panel-header"><div><div class="panel-title">Operational Digital Twin · Photogrammetry + ROV Localization</div><div class="panel-sub">Demo worksite · photogrammetry seabed · subsea frame · ROV · manipulator · TEP/TCP · FLS localization</div></div><div class="badge info">LIVE MODEL</div></div>', unsafe_allow_html=True)

    # Operational subsea intervention demo:
    # seabed + subsea protection frame + valve target + ROV + manipulator + FLS cone
    x = np.linspace(-10, 10, 55)
    y = np.linspace(-7, 7, 45)
    X, Y = np.meshgrid(x, y)
    Z = -82.5 - 0.06*X - 0.06*np.sin(Y/1.8) - 0.18*np.cos(X/2.5)

    fig = go.Figure()

    # Photogrammetry-derived seabed surface
    fig.add_trace(go.Surface(
        x=X, y=Y, z=Z,
        colorscale="Viridis",
        opacity=0.34,
        showscale=False,
        hoverinfo="skip",
        name="Photogrammetry Seabed"
    ))

    # Subsea frame / intervention structure
    frame_x = [-0.8, 2.8]
    frame_y = [-1.5, 1.5]
    frame_z_top = -80.4
    frame_z_base = -82.1
    corners = [
        (-0.8,-1.5), (-0.8,1.5), (2.8,-1.5), (2.8,1.5)
    ]
    for fx, fy in corners:
        fig.add_trace(go.Scatter3d(
            x=[fx, fx], y=[fy, fy], z=[frame_z_base, frame_z_top],
            mode="lines",
            line=dict(color="#9bb6c8", width=8),
            showlegend=False,
            hoverinfo="skip"
        ))
    # top/bottom rails
    rails = [
        ([-0.8,2.8],[-1.5,-1.5]), ([-0.8,2.8],[1.5,1.5]),
        ([-0.8,-0.8],[-1.5,1.5]), ([2.8,2.8],[-1.5,1.5])
    ]
    for rx, ry in rails:
        fig.add_trace(go.Scatter3d(
            x=rx, y=ry, z=[frame_z_top, frame_z_top],
            mode="lines",
            line=dict(color="#9bb6c8", width=7),
            showlegend=False,
            hoverinfo="skip"
        ))
    fig.add_trace(go.Scatter3d(
        x=[1.0], y=[0.0], z=[frame_z_top+0.15],
        mode="markers+text",
        marker=dict(size=5, color="#9bb6c8"),
        text=["SUBSEA INTERVENTION FRAME"],
        textposition="top center",
        name="Subsea Frame"
    ))

    # Tool Engagement Point on frame
    target = np.array([1.9, 0.25, -80.55])
    fig.add_trace(go.Scatter3d(
        x=[target[0]], y=[target[1]], z=[target[2]],
        mode="markers+text",
        marker=dict(size=9, color="#ffbd4a", symbol="diamond"),
        text=["TEP · 50-XV-0401"],
        textposition="top center",
        name="Tool Engagement Point"
    ))

    # ROV reference and simple vehicle envelope
    rov = np.array([-3.3, -0.9, -80.25])
    rov_box = np.array([
        [-3.9,-1.45,-80.65],[-2.7,-1.45,-80.65],[-2.7,-0.35,-80.65],[-3.9,-0.35,-80.65],
        [-3.9,-1.45,-79.85],[-2.7,-1.45,-79.85],[-2.7,-0.35,-79.85],[-3.9,-0.35,-79.85]
    ])
    edges = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]
    for a,b in edges:
        fig.add_trace(go.Scatter3d(
            x=[rov_box[a,0],rov_box[b,0]],
            y=[rov_box[a,1],rov_box[b,1]],
            z=[rov_box[a,2],rov_box[b,2]],
            mode="lines",
            line=dict(color="#33d1ff", width=5),
            showlegend=False,
            hoverinfo="skip"
        ))
    fig.add_trace(go.Scatter3d(
        x=[rov[0]], y=[rov[1]], z=[rov[2]],
        mode="markers+text",
        marker=dict(size=8, color="#33d1ff", symbol="square"),
        text=["WROV-02 · ROV-RP"],
        textposition="bottom center",
        name="ROV Reference Point"
    ))

    # Manipulator kinematic chain
    shoulder = rov + np.array([0.45, 0.10, -0.12])
    elbow = shoulder + np.array([0.85, 0.18, -0.12])
    wrist = elbow + np.array([0.85, 0.20, -0.08])
    tcp = wrist + np.array([0.75, 0.22, -0.04])
    manip_pts = np.vstack([shoulder, elbow, wrist, tcp])
    fig.add_trace(go.Scatter3d(
        x=manip_pts[:,0], y=manip_pts[:,1], z=manip_pts[:,2],
        mode="lines+markers",
        line=dict(color="#72f2a5", width=9),
        marker=dict(size=[6,7,7,8], color="#72f2a5"),
        name="Manipulator / TCP"
    ))

    # Tool alignment path from TCP to TEP
    fig.add_trace(go.Scatter3d(
        x=[tcp[0], target[0]], y=[tcp[1], target[1]], z=[tcp[2], target[2]],
        mode="lines",
        line=dict(color="#ffbd4a", width=5, dash="dash"),
        name="Tool Approach Vector"
    ))

    # 5% operational tolerance bubble around target (visual approximation)
    phi = np.linspace(0, 2*np.pi, 28)
    theta = np.linspace(0, np.pi, 16)
    r = 0.28
    xs = target[0] + r*np.outer(np.cos(phi), np.sin(theta))
    ys = target[1] + r*np.outer(np.sin(phi), np.sin(theta))
    zs = target[2] + r*np.outer(np.ones_like(phi), np.cos(theta))
    fig.add_trace(go.Surface(
        x=xs, y=ys, z=zs,
        opacity=0.13,
        showscale=False,
        colorscale=[[0,"#ffbd4a"],[1,"#ffbd4a"]],
        hoverinfo="skip",
        name="Operational Tolerance Zone"
    ))

    # FLS acoustic reference fan / cone
    fls_origin = rov + np.array([0.55,0.0,0.12])
    fan_angles = np.linspace(-0.34,0.34,11)
    for ang in fan_angles:
        end = np.array([
            target[0],
            target[1] + 1.7*np.sin(ang),
            target[2] + 0.25*np.cos(ang)
        ])
        fig.add_trace(go.Scatter3d(
            x=[fls_origin[0], end[0]],
            y=[fls_origin[1], end[1]],
            z=[fls_origin[2], end[2]],
            mode="lines",
            line=dict(color="rgba(75,140,255,0.33)", width=2),
            showlegend=False,
            hoverinfo="skip"
        ))
    fig.add_trace(go.Scatter3d(
        x=[fls_origin[0], target[0]],
        y=[fls_origin[1], target[1]],
        z=[fls_origin[2], target[2]],
        mode="lines",
        line=dict(color="#4b8cff", width=3, dash="dot"),
        name="FLS Localization Reference"
    ))

    fig.update_layout(
        height=570,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="#0b1621",
        plot_bgcolor="#0b1621",
        legend=dict(
            bgcolor="rgba(8,18,28,.55)",
            font=dict(color="#b8cad6", size=10),
            orientation="h",
            yanchor="bottom", y=0.01,
            xanchor="left", x=0.01
        ),
        scene=dict(
            bgcolor="#0b1621",
            xaxis=dict(title="Local X (m)", gridcolor="#1f3344", color="#8ea5b8"),
            yaxis=dict(title="Local Y (m)", gridcolor="#1f3344", color="#8ea5b8"),
            zaxis=dict(title="Depth (m)", gridcolor="#1f3344", color="#8ea5b8", autorange="reversed"),
            camera=dict(eye=dict(x=1.6, y=-1.6, z=0.9))
        )
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

    # Navigation / geometry KPI strip
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    kpi_cards = [
        {
            "title": "ROV Localization Confidence",
            "value": f"{localization_conf}",
            "unit": "%",
            "status": "PASS" if localization_pass else "HOLD",
            "status_cls": "pass" if localization_pass else "hold",
            "note": "INS + DVL + IMU navigation solution"
        },
        {
            "title": "Photogrammetry Point-Cloud Confidence",
            "value": f"{pointcloud_conf}",
            "unit": "%",
            "status": "REGISTERED" if pointcloud_pass else "REVALIDATE",
            "status_cls": "pass" if pointcloud_pass else "hold",
            "note": "Registered operational 3D reference"
        },
        {
            "title": "ROV-to-Target Distance Error",
            "value": f"{distance_error_pct:.1f}",
            "unit": "%",
            "status": "WITHIN LIMIT" if distance_pass else "OUTSIDE LIMIT",
            "status_cls": "pass" if distance_pass else "hold",
            "note": "Mission tolerance limit ≤ 5%"
        },
        {
            "title": "Manipulator / Tool Clearance",
            "value": f"{clearance_mm}",
            "unit": "mm",
            "status": "CLEAR" if clearance_pass else "HOLD",
            "status_cls": "pass" if clearance_pass else "hold",
            "note": "Minimum demo clearance 50 mm"
        },
        {
            "title": "Visual / FLS Localization Support",
            "value": f"{visibility_m:.1f}",
            "unit": "m",
            "status": "FLS BACKUP" if degraded_visibility and fls_available else "VISUAL + FLS",
            "status_cls": "pass" if visibility_supported else "hold",
            "note": "Degraded-visibility support path"
        },
    ]

    cards_html = '<div class="mrsif-kpi-grid">'
    for card in kpi_cards:
        cards_html += f"""
        <div class="mrsif-kpi">
            <div class="mrsif-kpi-title">{card['title']}</div>
            <div class="mrsif-kpi-value">{card['value']}<span class="mrsif-kpi-unit">{card['unit']}</span></div>
            <div class="mrsif-kpi-status {card['status_cls']}">{card['status']}</div>
            <div class="mrsif-kpi-note">{card['note']}</div>
        </div>
        """
    cards_html += '</div>'
    st.markdown(cards_html, unsafe_allow_html=True)

# RIGHT — readiness + OSDU + decision
with right:
    checks = [
        ("CFIHOS tool/interface", tool_match),
        ("Point-cloud confidence", pointcloud_pass),
        ("ROV localization", localization_pass),
        ("Distance within 5%", distance_pass),
        ("Manipulator clearance", clearance_pass),
        ("Metocean threshold", metocean_pass),
        ("Visibility/FLS support", visibility_supported),
        ("Pilot risk confirmation", st.session_state.pilot_risk_confirmed),
    ]

    st.markdown('<div class="panel"><div class="panel-header"><div><div class="panel-title">Mission Validation</div><div class="panel-sub">PASS / HOLD control gates</div></div></div>', unsafe_allow_html=True)
    for label, ok in checks:
        st.markdown(
            f'<div class="asset-row"><span class="asset-key">{label}</span><span class="badge {"pass" if ok else "hold"}">{"PASS" if ok else "HOLD"}</span></div>',
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="panel"><div class="panel-header"><div><div class="panel-title">OSDU Data Context</div><div class="panel-sub">Subsurface / survey / spatial universe</div></div></div>', unsafe_allow_html=True)
    for k, v in OSDU_CONTEXT.items():
        st.markdown(f'<div class="osdu-row"><span class="osdu-key">{k}</span><span class="osdu-val">{v}</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    decision_cls = "decision passbox" if readiness_pass else "decision"
    if readiness_pass:
        decision_text = """
        <b>MRSIF RECOMMENDATION</b><br>
        Spatial, tooling, environmental and pilot-readiness gates are satisfied.<br><br>
        <b>Action:</b> Authorize controlled intervention and begin evidence capture.
        """
    else:
        hold_reasons = []
        if not tool_match: hold_reasons.append("verify tool/interface")
        if not pointcloud_pass: hold_reasons.append("improve point-cloud confidence")
        if not localization_pass: hold_reasons.append("reacquire ROV localization")
        if not distance_pass: hold_reasons.append("reposition within 5% tolerance")
        if not clearance_pass: hold_reasons.append("increase manipulator clearance")
        if not metocean_pass: hold_reasons.append("current exceeds operational threshold")
        if not visibility_supported: hold_reasons.append("FLS confirmation required")
        if not st.session_state.pilot_risk_confirmed: hold_reasons.append("pilot risk review pending")
        decision_text = f"""
        <b>MRSIF RECOMMENDATION</b><br>
        Intervention remains on HOLD.<br><br>
        <b>Resolve:</b> {", ".join(hold_reasons)}.
        """
    st.markdown(f'<div class="{decision_cls}"><div class="big-state">{mission_state}</div>{decision_text}</div>', unsafe_allow_html=True)

# -----------------------------
# 9. MISSION ACTION / CLOSURE
# -----------------------------
st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
a1, a2, a3, a4 = st.columns([1,1,1,1.2])

with a1:
    if st.button("Run Virtual Function Test", use_container_width=True):
        if readiness_pass:
            st.success("Virtual function test passed: TCP/TEP geometry and mission gates validated.")
        else:
            st.warning("Virtual function test blocked by HOLD conditions.")

with a2:
    if st.button("Authorize Intervention", use_container_width=True, disabled=not readiness_pass):
        st.session_state.mission_executed = True
        st.rerun()

with a3:
    if st.button("Verify Mission Completion", use_container_width=True, disabled=not st.session_state.mission_executed):
        st.session_state.completion_verified = True
        st.rerun()

with a4:
    if st.session_state.completion_verified:
        st.success("MISSION ACCOMPLISHED · Evidence package ready for closure.")
    elif st.session_state.mission_executed:
        st.info("Execution active · Capture video, sonar, navigation, tool and environmental evidence.")
    else:
        st.warning("Execution remains controlled by MRSIF readiness gates.")

# -----------------------------
# 10. FOOTER / TRACEABILITY
# -----------------------------
ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
st.markdown(f"""
<div class="footerbar">
    <span>VODIDS · MRSIF v4.0 Mission Intelligence GUI Prototype</span>
    <span>CFIHOS-aligned asset context · OSDU-linked subsurface context · Audit timestamp {ts}</span>
</div>
""", unsafe_allow_html=True)
