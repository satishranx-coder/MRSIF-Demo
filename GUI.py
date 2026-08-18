
import streamlit as st
import numpy as np
import plotly.graph_objects as go
from dataclasses import dataclass
from typing import Dict, List, Tuple
from datetime import datetime, timezone

# ============================================================
# VODIDS | MRSIF v4.0 — Mission Intelligence GUI Prototype
# ============================================================

st.set_page_config(
    page_title="VODIDS | MRSIF Mission Intelligence",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

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
logo_html = '<div class="logo-fallback">VODIDS</div>'
if Path("VODIDS.png").exists():
    # Streamlit image is rendered separately below; fallback still maintains layout.
    logo_html = '<div class="logo-fallback">VODIDS</div>'

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
    st.markdown('<div class="panel"><div class="panel-header"><div><div class="panel-title">Operational Digital Twin · Photogrammetry + ROV Localization</div><div class="panel-sub">Point cloud / target / tool engagement / vehicle reference frame</div></div><div class="badge info">LIVE MODEL</div></div>', unsafe_allow_html=True)

    # Synthetic terrain + target + ROV + manipulator approach
    x = np.linspace(-8, 8, 45)
    y = np.linspace(-6, 6, 35)
    X, Y = np.meshgrid(x, y)
    Z = -82.0 - 0.12*X - 0.08*np.sin(Y) - 0.45*np.exp(-((X+1.2)**2 + (Y-0.7)**2)/5.0)

    fig = go.Figure()
    fig.add_trace(go.Surface(
        x=X, y=Y, z=Z,
        colorscale="Viridis",
        opacity=0.38,
        showscale=False,
        hoverinfo="skip",
        name="Photogrammetry / Seabed"
    ))

    # Asset / TEP
    target = np.array([1.5, 0.5, -81.8])
    fig.add_trace(go.Scatter3d(
        x=[target[0]], y=[target[1]], z=[target[2]],
        mode="markers+text",
        marker=dict(size=8, color="#ffbd4a", symbol="diamond"),
        text=["TEP · 50-XV-0401"],
        textposition="top center",
        name="Tool Engagement Point"
    ))

    # ROV midship bottom centre reference point
    rov = np.array([-2.4, -0.8, -80.7])
    fig.add_trace(go.Scatter3d(
        x=[rov[0]], y=[rov[1]], z=[rov[2]],
        mode="markers+text",
        marker=dict(size=10, color="#33d1ff", symbol="square"),
        text=["ROV-RP"],
        textposition="bottom center",
        name="ROV Reference Point"
    ))

    # Approach line / manipulator TCP to TEP
    tcp = rov + np.array([0.7, 0.18, -0.35])
    fig.add_trace(go.Scatter3d(
        x=[rov[0], tcp[0], target[0]],
        y=[rov[1], tcp[1], target[1]],
        z=[rov[2], tcp[2], target[2]],
        mode="lines+markers",
        line=dict(color="#33d1ff", width=6),
        marker=dict(size=[4,7,4], color=["#33d1ff","#72f2a5","#ffbd4a"]),
        name="Manipulator / Approach Vector"
    ))

    # FLS cone reference
    fig.add_trace(go.Scatter3d(
        x=[rov[0], target[0]], y=[rov[1], target[1]], z=[rov[2], target[2]],
        mode="lines",
        line=dict(color="#4b8cff", width=2, dash="dash"),
        name="FLS / Target Reference"
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

    # Navigation confidence strip
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Localization", f"{localization_conf}%", "INS + DVL + IMU")
    k2.metric("Point Cloud", f"{pointcloud_conf}%", "Registered")
    k3.metric("Distance Error", f"{distance_error_pct:.1f}%", "Limit 5%")
    k4.metric("Clearance", f"{clearance_mm} mm", "Min 50 mm")
    k5.metric("Visibility", f"{visibility_m:.1f} m", "FLS backup" if degraded_visibility else "Visual + FLS")

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
