
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
    "sim_stage": 0,
    "sim_scenario": "Normal operation",
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


/* Safe KPI readability fix — presentation only */
.ops-kpi {
    background:#0c1824;
    border:1px solid #2b4356;
    border-radius:10px;
    padding:10px 9px;
    min-height:122px;
    box-sizing:border-box;
}
.ops-kpi-title {
    color:#a9bdcb;
    font-size:10px;
    font-weight:700;
    line-height:1.25;
    min-height:28px;
}
.ops-kpi-value {
    color:#ffffff;
    font-size:24px;
    font-weight:900;
    line-height:1.1;
    margin-top:7px;
}
.ops-kpi-status {
    color:#72f2a5;
    font-size:9px;
    font-weight:800;
    margin-top:8px;
    line-height:1.2;
}
.ops-kpi-note {
    color:#7f97aa;
    font-size:8.5px;
    line-height:1.2;
    margin-top:5px;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# 4. USER CONTROLS
# -----------------------------
SIM_STAGES = [
    "Mission Setup",
    "Approach Worksite",
    "Target Localization",
    "StationKeep Established",
    "Acquire Hot Stab",
    "TCP → TEP Alignment",
    "Hot Stab Insertion",
    "Hydraulic Function / Valve Open",
    "Verification & Withdrawal",
    "Mission Accomplished",
]

SIM_SCENARIOS = [
    "Normal operation",
    "Low visibility — FLS supported",
    "DVL bottom lock lost",
    "Wrong hot stab selected",
    "Excess seafloor current",
    "TCP / TEP misalignment",
    "Hydraulic pressure low",
    "Low visibility + FLS unavailable",
]

with st.expander("Mission Simulation Controls", expanded=False):
    s1, s2 = st.columns([1.2, 1])
    with s1:
        selected_scenario = st.selectbox(
            "Operational Scenario",
            SIM_SCENARIOS,
            index=SIM_SCENARIOS.index(st.session_state.sim_scenario)
            if st.session_state.sim_scenario in SIM_SCENARIOS else 0
        )
        st.session_state.sim_scenario = selected_scenario
        st.caption("Demo telemetry changes with the selected scenario. This is not OEM live data.")
    with s2:
        st.markdown("**Mission:** Hot Stab Valve Intervention")
        st.markdown("**Water Depth:** 600 m")
        st.markdown("**Reference Vehicle:** TechnipFMC Schilling HD-class WROV")
        st.markdown("**Manipulator Reference:** TITAN 4-class")
        st.markdown("**Visualization:** Engineering simulation, not OEM CAD")

    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        base_current = st.slider("Seafloor current (kts)", 0.3, 3.0, 1.2, 0.1)
        base_visibility = st.slider("Visibility (m)", 0.0, 10.0, 4.5, 0.5)
    with c2:
        base_localization_conf = st.slider("Localization confidence (%)", 0, 100, 94)
        base_pointcloud_conf = st.slider("Point-cloud confidence (%)", 0, 100, 96)
    with c3:
        base_distance_error_pct = st.slider("ROV/target distance error (%)", 0.0, 15.0, 3.2, 0.1)
        base_clearance_mm = st.slider("Manipulator clearance (mm)", 0, 250, 82, 2)
    with c4:
        base_tool_match = st.checkbox("Correct hot stab / interface", True)
        base_dvl_lock = st.checkbox("DVL bottom lock", True)
        base_fls_available = st.checkbox("FLS target confirmation", True)
        st.session_state.pilot_risk_confirmed = st.checkbox(
            "Pilot risk review confirmed", st.session_state.pilot_risk_confirmed
        )

stage = int(st.session_state.sim_stage)
scenario = st.session_state.sim_scenario

metocean_current = base_current
visibility_m = base_visibility
localization_conf = base_localization_conf
pointcloud_conf = base_pointcloud_conf
distance_error_pct = base_distance_error_pct
clearance_mm = base_clearance_mm
tool_match = base_tool_match
dvl_lock = base_dvl_lock
fls_available = base_fls_available

alignment_error_deg = max(0.8, 6.0 - stage * 0.65)
hydraulic_pressure_psi = 0 if stage < 6 else (3200 if stage == 6 else 3500)
hydraulic_flow_lpm = 0 if stage < 6 else (8.0 if stage == 6 else 11.5)
valve_open_pct = 0 if stage < 7 else 100
target_range_m = max(0.55, 9.0 - stage * 1.05)
evidence_capture = stage >= 6

if scenario == "Low visibility — FLS supported" and stage >= 2:
    visibility_m = 0.6
    fls_available = True
    localization_conf = min(localization_conf, 90)
elif scenario == "DVL bottom lock lost" and stage >= 2:
    dvl_lock = False
    localization_conf = 62
elif scenario == "Wrong hot stab selected" and stage >= 4:
    tool_match = False
elif scenario == "Excess seafloor current" and stage >= 1:
    metocean_current = 2.2
elif scenario == "TCP / TEP misalignment" and stage >= 5:
    alignment_error_deg = 9.5
    distance_error_pct = 7.8
elif scenario == "Hydraulic pressure low" and stage >= 6:
    hydraulic_pressure_psi = 1750
    hydraulic_flow_lpm = 3.0
elif scenario == "Low visibility + FLS unavailable" and stage >= 2:
    visibility_m = 0.4
    fls_available = False
    localization_conf = 58

if scenario in ("Normal operation", "Low visibility — FLS supported"):
    distance_error_pct = max(1.0, base_distance_error_pct - stage * 0.28)
    localization_conf = min(98, localization_conf + min(stage, 5))
    if stage >= 5:
        clearance_mm = max(clearance_mm, 76)

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
alignment_pass = alignment_error_deg <= 5.0
hydraulic_pass = (stage < 6) or hydraulic_pressure_psi >= 3000
tooling_pass = tool_match

simulation_gate_pass = all([
    tooling_pass, metocean_pass, pointcloud_pass, distance_pass,
    localization_pass, visibility_supported, clearance_pass,
    alignment_pass, hydraulic_pass
])

preconditions = {
    "Safety & HSE": metocean_pass,
    "Scope & Work Reference": True,
    "Asset / Vehicle Identity": True,
    "Tooling & Sensor Validation": tooling_pass,
    "Robotics / Execution Intelligence": all([
        pointcloud_pass, distance_pass, localization_pass,
        visibility_supported, clearance_pass, alignment_pass, hydraulic_pass
    ]),
    "Data Quality & Operational Evidence": evidence_capture or stage < 6,
    "Handover / Data Delivery": st.session_state.completion_verified,
}

readiness_pass = simulation_gate_pass and st.session_state.pilot_risk_confirmed

if st.session_state.completion_verified or stage >= len(SIM_STAGES)-1:
    mission_state = "MISSION ACCOMPLISHED"
    state_class = "pass"
elif stage >= 6 and simulation_gate_pass:
    mission_state = "INTERVENTION IN PROGRESS"
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
  <div class="mission-item"><div class="mission-label">Mission</div><div class="mission-value">600 m Hot Stab Valve Intervention</div></div>
  <div class="mission-item"><div class="mission-label">Asset</div><div class="mission-value">{CFIHOS_ASSET['tag']}</div></div>
  <div class="mission-item"><div class="mission-label">Vehicle</div><div class="mission-value">Schilling HD-class</div></div>
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

    # 600 m hot-stab intervention engineering simulation
    stage_progress = stage / (len(SIM_STAGES)-1)
    rov_x = 75 + stage_progress * 235
    rov_y = 230
    valve_x, valve_y = 548, 250

    arm_factor = min(1.0, max(0.0, (stage - 3) / 3.0))
    shoulder_x, shoulder_y = rov_x + 100, rov_y + 12
    elbow_x = shoulder_x + 45 + 42 * arm_factor
    elbow_y = shoulder_y + 14 - 8 * arm_factor
    wrist_x = elbow_x + 40 + 42 * arm_factor
    wrist_y = elbow_y - 2
    tcp_x = wrist_x + 28 + 40 * arm_factor
    tcp_y = wrist_y
    if scenario == "TCP / TEP misalignment" and stage >= 5:
        tcp_y -= 48

    stab_inserted = stage >= 6 and simulation_gate_pass
    stab_color = "#72f2a5" if stab_inserted else "#ffbd4a"
    gate_color = "#2bd576" if simulation_gate_pass else "#ffbd4a"
    fls_opacity = "0.30" if fls_available else "0.05"

    sim_svg = f"""
    <div style="border:1px solid #24384a;border-radius:12px;background:#07131e;padding:10px;">
      <div style="display:flex;justify-content:space-between;gap:12px;align-items:center;margin-bottom:8px;">
        <div>
          <div style="font-size:13px;font-weight:800;color:#eef7fb;">600 m Hot-Stab Valve Intervention Simulator</div>
          <div style="font-size:10px;color:#8fa6b8;">
            Schilling HD-class WROV engineering representation · TITAN 4-class manipulator · simulated telemetry
          </div>
        </div>
        <div style="padding:5px 9px;border:1px solid {gate_color};border-radius:18px;color:{gate_color};font-size:10px;font-weight:800;">
          {"GATE PASS" if simulation_gate_pass else "MRSIF HOLD"}
        </div>
      </div>
      <svg viewBox="0 0 700 390" width="100%" role="img"
           aria-label="Work class ROV hot stab intervention simulation">
        <defs>
          <linearGradient id="water" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#0d2a42"/>
            <stop offset="100%" stop-color="#06111a"/>
          </linearGradient>
          <pattern id="grid" width="35" height="35" patternUnits="userSpaceOnUse">
            <path d="M 35 0 L 0 0 0 35" fill="none" stroke="#234055" stroke-width="0.5"/>
          </pattern>
        </defs>
        <rect width="700" height="390" rx="12" fill="url(#water)"/>
        <rect width="700" height="390" rx="12" fill="url(#grid)" opacity="0.7"/>
        <text x="18" y="28" fill="#8fa6b8" font-size="12">SIMULATED DEPTH 600 m</text>
        <text x="18" y="48" fill="#8fa6b8" font-size="10">Scenario: {scenario}</text>

        <path d="M0 330 C110 315,220 340,330 326 S520 314,700 328 L700 390 L0 390 Z"
              fill="#183426" opacity="0.78"/>
        <text x="610" y="355" fill="#8fa6b8" font-size="10">SEABED</text>

        <!-- Subsea frame and valve -->
        <g stroke="#98aebd" stroke-width="6" fill="none">
          <rect x="520" y="135" width="120" height="178" rx="3"/>
          <line x1="520" y1="135" x2="548" y2="110"/>
          <line x1="640" y1="135" x2="612" y2="110"/>
          <line x1="548" y1="110" x2="612" y2="110"/>
        </g>
        <text x="528" y="98" fill="#dce8ef" font-size="11">SUBSEA VALVE PANEL</text>
        <circle cx="{valve_x}" cy="{valve_y}" r="24" fill="#14293a" stroke="#ffbd4a" stroke-width="4"/>
        <circle cx="{valve_x}" cy="{valve_y}" r="9" fill="#06111a" stroke="#ffbd4a" stroke-width="3"/>
        <text x="{valve_x-37}" y="{valve_y+43}" fill="#ffcf75" font-size="10">HOT-STAB TEP</text>

        <!-- Schilling HD-class engineering representation -->
        <g>
          <rect x="{rov_x}" y="{rov_y-62}" width="126" height="94" rx="10"
                fill="#d7b43d" stroke="#f4df89" stroke-width="3"/>
          <rect x="{rov_x+8}" y="{rov_y-49}" width="110" height="65" rx="4"
                fill="#102333" stroke="#d6e2e9" stroke-width="3"/>
          <rect x="{rov_x+28}" y="{rov_y-82}" width="70" height="25" rx="4"
                fill="#d7b43d" stroke="#f4df89" stroke-width="2"/>
          <circle cx="{rov_x+20}" cy="{rov_y-12}" r="14" fill="#07131e" stroke="#33d1ff" stroke-width="3"/>
          <circle cx="{rov_x+106}" cy="{rov_y-12}" r="14" fill="#07131e" stroke="#33d1ff" stroke-width="3"/>
          <circle cx="{rov_x+20}" cy="{rov_y-12}" r="5" fill="#33d1ff"/>
          <circle cx="{rov_x+106}" cy="{rov_y-12}" r="5" fill="#33d1ff"/>
          <text x="{rov_x+10}" y="{rov_y-34}" fill="#eef7fb" font-size="10" font-weight="700">SCHILLING HD-CLASS</text>
          <text x="{rov_x+30}" y="{rov_y-20}" fill="#8fa6b8" font-size="9">WROV SIMULATION</text>
        </g>

        <!-- FLS fan -->
        <path d="M {rov_x+122} {rov_y-26} L 505 175 L 505 300 Z"
              fill="#4b8cff" opacity="{fls_opacity}" stroke="#4b8cff" stroke-width="1"/>
        <text x="{rov_x+126}" y="{rov_y-36}" fill="#78a8ff" font-size="9">FLS</text>

        <!-- Manipulator -->
        <g fill="none" stroke="#72f2a5" stroke-linecap="round">
          <line x1="{shoulder_x}" y1="{shoulder_y}" x2="{elbow_x}" y2="{elbow_y}" stroke-width="12"/>
          <line x1="{elbow_x}" y1="{elbow_y}" x2="{wrist_x}" y2="{wrist_y}" stroke-width="10"/>
          <line x1="{wrist_x}" y1="{wrist_y}" x2="{tcp_x}" y2="{tcp_y}" stroke-width="8"/>
        </g>
        <g fill="#0b1824" stroke="#72f2a5" stroke-width="3">
          <circle cx="{shoulder_x}" cy="{shoulder_y}" r="8"/>
          <circle cx="{elbow_x}" cy="{elbow_y}" r="8"/>
          <circle cx="{wrist_x}" cy="{wrist_y}" r="7"/>
        </g>
        <circle cx="{tcp_x}" cy="{tcp_y}" r="6" fill="{stab_color}" stroke="#fff" stroke-width="2"/>
        <text x="{tcp_x-15}" y="{tcp_y-14}" fill="#72f2a5" font-size="9">TCP</text>
        <line x1="{tcp_x}" y1="{tcp_y}" x2="{valve_x}" y2="{valve_y}"
              stroke="{stab_color}" stroke-width="4" stroke-dasharray="8 5"/>

        <text x="18" y="300" fill="#8fa6b8" font-size="10">Target Range</text>
        <text x="18" y="320" fill="#eef7fb" font-size="15" font-weight="700">{target_range_m:.2f} m</text>
        <text x="125" y="300" fill="#8fa6b8" font-size="10">TCP/TEP Error</text>
        <text x="125" y="320" fill="#eef7fb" font-size="15" font-weight="700">{alignment_error_deg:.1f}°</text>
        <text x="245" y="300" fill="#8fa6b8" font-size="10">Hydraulic</text>
        <text x="245" y="320" fill="#eef7fb" font-size="15" font-weight="700">{hydraulic_pressure_psi:.0f} psi</text>
        <text x="365" y="300" fill="#8fa6b8" font-size="10">Valve</text>
        <text x="365" y="320" fill="#eef7fb" font-size="15" font-weight="700">{valve_open_pct:.0f}% OPEN</text>

        <rect x="16" y="344" width="668" height="30" rx="8" fill="#091621" stroke="#29465c"/>
        <text x="28" y="364" fill="#eef7fb" font-size="11">
          STAGE {stage+1}/{len(SIM_STAGES)} · {SIM_STAGES[stage]}
        </text>
      </svg>
    </div>
    """
    st.markdown(sim_svg, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Mission telemetry strip
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    k1, k2, k3, k4, k5 = st.columns(5)
    telemetry_cards = [
        ("ROV Localization", f"{localization_conf}%", "PASS" if localization_pass else "HOLD", "INS + DVL + IMU"),
        ("Point-Cloud Confidence", f"{pointcloud_conf}%", "REGISTERED" if pointcloud_pass else "REVALIDATE", "Photogrammetry reference"),
        ("TCP / TEP Alignment", f"{alignment_error_deg:.1f}°", "PASS" if alignment_pass else "HOLD", "Demo limit ≤ 5°"),
        ("Hydraulic Pressure", f"{hydraulic_pressure_psi:.0f} psi", "PASS" if hydraulic_pass else "HOLD", f"Flow {hydraulic_flow_lpm:.1f} L/min"),
        ("Valve State", f"{valve_open_pct:.0f}%", "VERIFIED" if stage >= 8 and simulation_gate_pass else "PENDING", "Open-position confirmation"),
    ]
    for col, (title, value, status, note) in zip([k1,k2,k3,k4,k5], telemetry_cards):
        with col:
            status_color = "#72f2a5" if status in ("PASS","REGISTERED","VERIFIED") else "#ffd079"
            st.markdown(f"""
            <div class="ops-kpi">
                <div class="ops-kpi-title">{title}</div>
                <div class="ops-kpi-value">{value}</div>
                <div class="ops-kpi-status" style="color:{status_color};">{status}</div>
                <div class="ops-kpi-note">{note}</div>
            </div>
            """, unsafe_allow_html=True)

# RIGHT — readiness + OSDU + decision
with right:
    checks = [
        ("CFIHOS tool/interface", tool_match),
        ("Point-cloud confidence", pointcloud_pass),
        ("ROV localization", localization_pass),
        ("Distance within 5%", distance_pass),
        ("TCP / TEP alignment ≤ 5°", alignment_pass),
        ("Manipulator clearance", clearance_pass),
        ("Metocean threshold", metocean_pass),
        ("Visibility/FLS support", visibility_supported),
        ("Hydraulic function", hydraulic_pass),
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
        if not distance_pass: hold_reasons.append("reposition ROV within 5% target tolerance")
        if not alignment_pass: hold_reasons.append("realign manipulator TCP to TEP within 5°")
        if not clearance_pass: hold_reasons.append("increase manipulator/tool clearance")
        if not metocean_pass: hold_reasons.append("current exceeds operational threshold")
        if not visibility_supported: hold_reasons.append("restore FLS or visual localization support")
        if not hydraulic_pass: hold_reasons.append("restore minimum hydraulic intervention pressure")
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
    if st.button("Reset Simulation", use_container_width=True):
        st.session_state.sim_stage = 0
        st.session_state.mission_executed = False
        st.session_state.completion_verified = False
        st.rerun()

with a2:
    can_advance = simulation_gate_pass and (st.session_state.pilot_risk_confirmed or stage < 4)
    if st.button(
        "Advance Simulation",
        use_container_width=True,
        disabled=(stage >= len(SIM_STAGES)-1 or not can_advance)
    ):
        st.session_state.sim_stage = min(stage + 1, len(SIM_STAGES)-1)
        if st.session_state.sim_stage >= 6:
            st.session_state.mission_executed = True
        if st.session_state.sim_stage >= 9:
            st.session_state.completion_verified = True
        st.rerun()

with a3:
    if st.button("Run Virtual Function Test", use_container_width=True):
        if simulation_gate_pass:
            st.success("Virtual function test passed: localization, point-cloud reference, TCP/TEP geometry, tooling and active mission gates validated.")
        else:
            st.warning("Virtual function test blocked by active MRSIF HOLD conditions.")

with a4:
    if stage >= 9 and simulation_gate_pass:
        st.success("MISSION ACCOMPLISHED · Evidence package ready for closure.")
    elif stage >= 6:
        st.info("Intervention active · Capturing navigation, FLS, manipulator, hydraulic and valve evidence.")
    elif not simulation_gate_pass:
        st.warning("MRSIF HOLD · Correct the active scenario condition before advancing.")
    else:
        st.info(f"Current stage: {SIM_STAGES[stage]}")

timeline = '<div style="display:grid;grid-template-columns:repeat(10,1fr);gap:4px;margin-top:10px;">'
for i, label in enumerate(SIM_STAGES):
    if i < stage:
        bg, border, color = "rgba(43,213,118,.10)", "#2bd576", "#72f2a5"
    elif i == stage:
        bg, border, color = "rgba(51,209,255,.12)", "#33d1ff", "#dff8ff"
    else:
        bg, border, color = "#0c1824", "#29465c", "#7f97aa"
    timeline += f"""<div style="background:{bg};border:1px solid {border};border-radius:8px;padding:6px 4px;text-align:center;min-height:52px;">
      <div style="font-size:9px;font-weight:800;color:{color};">S{i+1}</div>
      <div style="font-size:8px;line-height:1.15;color:{color};margin-top:3px;">{label}</div>
    </div>"""
timeline += '</div>'
st.markdown(timeline, unsafe_allow_html=True)

# -----------------------------
# 10. FOOTER / TRACEABILITY
# -----------------------------
ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
st.markdown(f"""
<div class="footerbar">
    <span>VODIDS · MRSIF v5.0 Hot-Stab Intervention Simulation</span>
    <span>CFIHOS-aligned asset context · OSDU-linked subsurface context · Audit timestamp {ts}</span>
</div>
""", unsafe_allow_html=True)
