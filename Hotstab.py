
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import base64
from datetime import datetime, timezone

st.set_page_config(
    page_title="VODIDS | MRSIF Acceptance Demo",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# MRSIF v6.0 — 600 m Hot-Stab Intervention Acceptance Demo
# ============================================================

STAGES = [
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

LAYER_NAMES = [
    ("L0", "Safety & HSE"),
    ("L1", "Scope & Work Reference"),
    ("L2", "Asset / Vehicle Identity"),
    ("L3", "Tooling & Sensor Validation"),
    ("L4", "Robotics / Execution Intelligence"),
    ("L5", "Data Quality & Operational Evidence"),
    ("L6", "Handover / Data Delivery"),
]

APPLICATIONS = [
    ("A01","Scope Intelligence"),("A02","Asset Identification"),
    ("A03","Vehicle Qualification"),("A04","Sensor Configuration"),
    ("A05","Tooling Compatibility"),("A06","Spatial Localization"),
    ("A07","Photogrammetry Intelligence"),("A08","Manipulator Validation"),
    ("A09","Environmental Assessment"),("A10","Execution Readiness"),
    ("A11","Live Mission Assurance"),("A12","Completion Verification"),
    ("A13","Data Handover"),
]

ASSET = {
    "tag": "50-XV-0401",
    "class": "Actuated Valve Assembly",
    "cfihos": "CFIHOS-10000284",
    "interface": "API 17H",
    "required_torque_nm": 145,
    "pressure_rating_psi": 10000,
}

def logo_html(path="VODIDS.png"):
    p = Path(path)
    if not p.exists():
        return '<div class="logo-fallback">VODIDS</div>'
    try:
        b64 = base64.b64encode(p.read_bytes()).decode()
        return f'<img src="data:image/png;base64,{b64}" style="width:82px;height:52px;object-fit:contain;border-radius:8px;">'
    except Exception:
        return '<div class="logo-fallback">VODIDS</div>'

# ---------- session ----------
defaults = {
    "stage": 0,
    "accepted_loaded": False,
    "pilot_confirmed": False,
    "mission_started": False,
    "mission_complete": False,
    "current_kts": 1.2,
    "visibility_m": 4.5,
    "localization_pct": 94,
    "pointcloud_pct": 96,
    "distance_error_pct": 3.2,
    "clearance_mm": 82,
    "alignment_deg": 2.4,
    "hydraulic_psi": 3500,
    "hydraulic_flow": 11.5,
    "tool_match": True,
    "dvl_lock": True,
    "fls_available": True,
}
for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---------- style ----------
st.markdown("""
<style>
:root{
--bg:#071019;--panel:#0d1824;--panel2:#111f2e;--border:#24384a;
--text:#eef7fb;--muted:#8fa6b8;--cyan:#33d1ff;--green:#2bd576;
--amber:#ffbd4a;--red:#ff5f63;
}
.stApp{background:radial-gradient(circle at top,#102033 0%,#071019 52%,#050b11 100%);color:var(--text);}
.block-container{max-width:1800px;padding-top:.75rem;padding-bottom:1.5rem;}
#MainMenu,footer,header{visibility:hidden;}
.topbar{display:flex;justify-content:space-between;align-items:center;padding:13px 16px;
border:1px solid var(--border);border-radius:13px;background:#0c1824;margin-bottom:10px;}
.brand{display:flex;align-items:center;gap:12px}.brand-title{font-size:23px;font-weight:800;color:white}
.brand-sub{font-size:11px;color:var(--muted)}.logo-fallback{font-weight:800;color:var(--cyan)}
.mission-strip{display:grid;grid-template-columns:repeat(5,1fr);gap:7px;margin-bottom:10px}
.mi{background:#0d1824;border:1px solid var(--border);border-radius:9px;padding:9px 11px}
.ml{font-size:9px;color:var(--muted);text-transform:uppercase;letter-spacing:1px}
.mv{font-size:13px;font-weight:800;color:#fff;margin-top:2px}
.apps{display:grid;grid-template-columns:repeat(13,1fr);gap:4px;margin-bottom:10px}
.app{background:#0c1824;border:1px solid #26394a;border-radius:7px;padding:5px;text-align:center;
font-size:8px;color:#839bab;min-height:42px}
.app.active{border-color:#33d1ff;color:#eef7fb;background:#10263a}.ac{display:block;color:#55d9ff;font-weight:800}
.panel{background:#0d1824;border:1px solid var(--border);border-radius:12px;padding:11px}
.ph{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #203447;padding-bottom:7px;margin-bottom:8px}
.pt{font-size:12px;font-weight:800}.ps{font-size:9px;color:var(--muted)}
.row{display:flex;justify-content:space-between;gap:8px;padding:6px 0;border-bottom:1px solid rgba(36,56,74,.55);font-size:10px}
.row:last-child{border-bottom:none}.rk{color:#8aa1b2}.rv{color:#edf7fb;font-weight:700;text-align:right}
.badge{padding:3px 7px;border-radius:14px;font-size:8px;font-weight:800;border:1px solid}
.pass{color:#72f2a5;border-color:#2bd576;background:rgba(43,213,118,.08)}
.hold{color:#ffd079;border-color:#ffbd4a;background:rgba(255,189,74,.08)}
.na{color:#8fa6b8;border-color:#4a5c69;background:rgba(143,166,184,.05)}
.monitor{color:#76dbff;border-color:#33d1ff;background:rgba(51,209,255,.07)}
.layer{display:grid;grid-template-columns:34px 1fr 52px;gap:6px;align-items:center;padding:7px 0;border-bottom:1px solid #203447}
.layer:last-child{border-bottom:none}.lc{color:#55d9ff;font-weight:800;font-size:10px}.ln{font-size:10px}
.ops-kpi{background:#0b1621;border:1px solid #29465c;border-radius:10px;padding:9px;min-height:110px}
.ops-kpi-title{color:#a9bdcb;font-size:9px;min-height:24px}.ops-kpi-value{color:white;font-size:22px;font-weight:900;margin-top:6px}
.ops-kpi-status{font-size:8px;font-weight:800;margin-top:7px}.ops-kpi-note{font-size:8px;color:#7f97aa;margin-top:4px}
.decision{border-left:4px solid var(--amber);background:rgba(255,189,74,.07);padding:10px;border-radius:8px;font-size:10px;line-height:1.4}
.decision.passbox{border-left-color:var(--green);background:rgba(43,213,118,.07)}
.bigstate{font-size:19px;font-weight:900;margin-bottom:5px}
.stButton>button{background:#123048!important;color:#eef7fb!important;border:1px solid #2f6681!important;
border-radius:9px!important;min-height:42px!important;font-weight:800!important}
.stButton>button:hover{border-color:#33d1ff!important;background:#163b57!important}
.stButton>button:disabled{background:#17232e!important;color:#637a8b!important;border-color:#2b3e4e!important;opacity:1!important}
div[data-testid="stExpander"]{background:#0d1824!important;border:1px solid #24384a!important;border-radius:10px!important}
div[data-testid="stExpander"] summary{color:#eef7fb!important;background:#111f2e!important}
</style>
""", unsafe_allow_html=True)

stage = st.session_state.stage

# ---------- acceptance control ----------
with st.expander("Mission Acceptance & Simulation Controls", expanded=True):
    c0,c1,c2,c3 = st.columns([1,1,1,1])
    with c0:
        if st.button("Load Accepted Mission", use_container_width=True):
            st.session_state.current_kts = 1.2
            st.session_state.visibility_m = 4.5
            st.session_state.localization_pct = 94
            st.session_state.pointcloud_pct = 96
            st.session_state.distance_error_pct = 3.2
            st.session_state.clearance_mm = 82
            st.session_state.alignment_deg = 2.4
            st.session_state.hydraulic_psi = 3500
            st.session_state.hydraulic_flow = 11.5
            st.session_state.tool_match = True
            st.session_state.dvl_lock = True
            st.session_state.fls_available = True
            st.session_state.pilot_confirmed = True
            st.session_state.accepted_loaded = True
            st.session_state.stage = 0
            st.session_state.mission_started = False
            st.session_state.mission_complete = False
            st.rerun()
    with c1:
        st.session_state.current_kts = st.number_input("Seafloor current (kts)",0.0,4.0,float(st.session_state.current_kts),0.1)
        st.session_state.visibility_m = st.number_input("Visibility (m)",0.0,20.0,float(st.session_state.visibility_m),0.5)
    with c2:
        st.session_state.localization_pct = st.number_input("Localization confidence (%)",0,100,int(st.session_state.localization_pct),1)
        st.session_state.pointcloud_pct = st.number_input("Point-cloud confidence (%)",0,100,int(st.session_state.pointcloud_pct),1)
    with c3:
        st.session_state.distance_error_pct = st.number_input("ROV-target error (%)",0.0,20.0,float(st.session_state.distance_error_pct),0.1)
        st.session_state.clearance_mm = st.number_input("Manipulator clearance (mm)",0,500,int(st.session_state.clearance_mm),5)

    d1,d2,d3,d4 = st.columns(4)
    with d1:
        st.session_state.alignment_deg = st.number_input("TCP/TEP alignment error (°)",0.0,20.0,float(st.session_state.alignment_deg),0.1)
        st.session_state.tool_match = st.checkbox("Correct hot stab / interface",st.session_state.tool_match)
    with d2:
        st.session_state.dvl_lock = st.checkbox("DVL bottom lock",st.session_state.dvl_lock)
        st.session_state.fls_available = st.checkbox("FLS confirmation available",st.session_state.fls_available)
    with d3:
        st.session_state.hydraulic_psi = st.number_input("Hydraulic pressure (psi)",0,5000,int(st.session_state.hydraulic_psi),100)
        st.session_state.hydraulic_flow = st.number_input("Hydraulic flow (L/min)",0.0,30.0,float(st.session_state.hydraulic_flow),0.5)
    with d4:
        st.session_state.pilot_confirmed = st.checkbox("Pilot risk review confirmed",st.session_state.pilot_confirmed)
        st.markdown("**Accepted Demo Criteria**")
        st.caption("Current ≤1.5 kts · Point cloud ≥90% · Localization ≥85% + DVL · Distance ≤5% · Clearance ≥50 mm · Alignment ≤5° · Hydraulic ≥3000 psi when required")

# ---------- raw checks ----------
current_pass = st.session_state.current_kts <= 1.5
pointcloud_pass = st.session_state.pointcloud_pct >= 90
localization_pass = st.session_state.localization_pct >= 85 and st.session_state.dvl_lock
distance_pass = st.session_state.distance_error_pct <= 5.0
clearance_pass = st.session_state.clearance_mm >= 50
alignment_pass = st.session_state.alignment_deg <= 5.0
visibility_pass = st.session_state.visibility_m >= 1.5 or st.session_state.fls_available
hydraulic_pass = st.session_state.hydraulic_psi >= 3000
tool_pass = st.session_state.tool_match
pilot_pass = st.session_state.pilot_confirmed

# ---------- stage-aware gate evaluation ----------
def status(label, applies_from, monitor_from=None, condition=True):
    if stage < (monitor_from if monitor_from is not None else applies_from):
        return ("N/A","na")
    if monitor_from is not None and stage < applies_from:
        return ("MONITOR","monitor")
    return ("PASS","pass") if condition else ("HOLD","hold")

gate_status = {
    "Metocean": status("Metocean",1,0,current_pass),
    "Point Cloud": status("Point Cloud",2,1,pointcloud_pass),
    "Localization": status("Localization",2,1,localization_pass),
    "Distance": status("Distance",2,1,distance_pass),
    "Tool Match": status("Tool Match",4,3,tool_pass),
    "Clearance": status("Clearance",5,4,clearance_pass),
    "Alignment": status("Alignment",5,4,alignment_pass),
    "Visibility/FLS": status("Visibility/FLS",2,1,visibility_pass),
    "Pilot Review": status("Pilot Review",4,3,pilot_pass),
    "Hydraulic": status("Hydraulic",7,6,hydraulic_pass),
    "Evidence": ("PASS","pass") if stage >= 8 else (("MONITOR","monitor") if stage >= 6 else ("N/A","na")),
}

# A gate can block only when it is operationally active.
active_conditions = []
if stage >= 1: active_conditions += [current_pass]
if stage >= 2: active_conditions += [pointcloud_pass, localization_pass, distance_pass, visibility_pass]
if stage >= 4: active_conditions += [tool_pass, pilot_pass]
if stage >= 5: active_conditions += [clearance_pass, alignment_pass]
if stage >= 7: active_conditions += [hydraulic_pass]
stage_clear = all(active_conditions) if active_conditions else True

# ---------- mission state ----------
if stage >= 9:
    mission_state = "MISSION ACCOMPLISHED"
    state_color = "#72f2a5"
elif stage >= 6 and stage_clear:
    mission_state = "INTERVENTION IN PROGRESS"
    state_color = "#76dbff"
elif stage_clear:
    mission_state = "STAGE ACCEPTED — READY TO ADVANCE"
    state_color = "#72f2a5"
else:
    mission_state = "HOLD — ACTIVE GATE NOT ACCEPTED"
    state_color = "#ffd079"

# ---------- header ----------
st.markdown(f"""
<div class="topbar">
  <div class="brand">{logo_html()}
    <div><div class="brand-title">MRSIF <span style="color:#33d1ff;">Mission Acceptance Demo</span></div>
    <div class="brand-sub">600 m Hot-Stab Valve Intervention · VODIDS Operational Intelligence</div></div>
  </div>
  <div style="font-size:11px;color:#8fa6b8;">CFIHOS ALIGNED · OSDU CONTEXT · SIMULATED TELEMETRY</div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="mission-strip">
<div class="mi"><div class="ml">Work Ref</div><div class="mv">WR-2026-HS600</div></div>
<div class="mi"><div class="ml">Mission</div><div class="mv">Hot Stab Valve Intervention</div></div>
<div class="mi"><div class="ml">Depth</div><div class="mv">600 m</div></div>
<div class="mi"><div class="ml">Reference Vehicle</div><div class="mv">Schilling HD-class WROV</div></div>
<div class="mi"><div class="ml">Mission State</div><div class="mv" style="color:{state_color}">{mission_state}</div></div>
</div>
""", unsafe_allow_html=True)

# ---------- apps ----------
apps_html = '<div class="apps">'
for i,(code,name) in enumerate(APPLICATIONS):
    active = (
        i <= 4 or
        (i <= 8 and stage >= 2) or
        (i == 9 and stage >= 4) or
        (i == 10 and stage >= 6) or
        (i >= 11 and stage >= 8)
    )
    apps_html += f'<div class="app {"active" if active else ""}"><span class="ac">{code}</span>{name}</div>'
apps_html += '</div>'
st.markdown(apps_html, unsafe_allow_html=True)

# ---------- main columns ----------
left, center, right = st.columns([1.05,2.55,1.25], gap="small")

with left:
    st.markdown('<div class="panel"><div class="ph"><div><div class="pt">7 MRSIF Core Layers</div><div class="ps">Stage-aware governance</div></div></div>', unsafe_allow_html=True)
    layer_logic = [
        current_pass if stage>=1 else True,
        True,
        True,
        tool_pass if stage>=4 else True,
        stage_clear,
        True if stage<8 else True,
        True if stage>=9 else False,
    ]
    for (code,name),ok in zip(LAYER_NAMES,layer_logic):
        if name=="Handover / Data Delivery" and stage<9:
            s,c = "LOCKED","na"
        else:
            s,c = ("PASS","pass") if ok else ("HOLD","hold")
        st.markdown(f'<div class="layer"><div class="lc">{code}</div><div class="ln">{name}</div><div class="badge {c}">{s}</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="panel"><div class="ph"><div><div class="pt">CFIHOS Asset Intelligence</div><div class="ps">Subsea component context</div></div></div>', unsafe_allow_html=True)
    for k,v in [("Target Tag",ASSET["tag"]),("Class",ASSET["class"]),("CFIHOS",ASSET["cfihos"]),
                ("Interface",ASSET["interface"]),("Required Torque",f'{ASSET["required_torque_nm"]} Nm'),
                ("Pressure Rating",f'{ASSET["pressure_rating_psi"]:,} psi')]:
        st.markdown(f'<div class="row"><span class="rk">{k}</span><span class="rv">{v}</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with center:
    # Position changes per mission stage.
    progress = stage / 9
    rov_x = 78 + progress * 230
    rov_y = 222
    valve_x, valve_y = 560, 245
    arm_factor = min(1.0,max(0.0,(stage-3)/3))
    sx, sy = rov_x+100, rov_y+15
    ex, ey = sx+44+40*arm_factor, sy+10
    wx, wy = ex+38+38*arm_factor, ey-2
    tx, ty = wx+28+38*arm_factor, wy
    if stage < 5:
        ty += 22
    elif not alignment_pass:
        ty -= 44

    stab_inserted = stage >= 6 and alignment_pass and tool_pass
    valve_pct = 100 if stage >= 7 and hydraulic_pass and stab_inserted else 0
    target_range = max(0.45, 9.0-stage*0.95)

    svg = f"""
    <div style="background:#07131e;border:1px solid #24384a;border-radius:12px;padding:9px;font-family:Arial,sans-serif;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
        <div><b style="color:#eef7fb;font-size:13px;">600 m Hot-Stab Intervention — Accepted Mission Demo</b><br>
        <span style="color:#8fa6b8;font-size:9px;">Engineering representation · not OEM CAD · simulated operational data</span></div>
        <span style="color:{state_color};font-size:10px;font-weight:800;">{mission_state}</span>
      </div>
      <svg viewBox="0 0 700 390" width="100%" role="img" aria-label="ROV hot stab mission simulation">
        <defs>
          <linearGradient id="w" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#103450"/><stop offset="100%" stop-color="#06111a"/></linearGradient>
          <pattern id="g" width="35" height="35" patternUnits="userSpaceOnUse"><path d="M35 0L0 0 0 35" fill="none" stroke="#234055" stroke-width=".5"/></pattern>
        </defs>
        <rect width="700" height="390" rx="10" fill="url(#w)"/><rect width="700" height="390" rx="10" fill="url(#g)" opacity=".6"/>
        <text x="18" y="27" fill="#8fa6b8" font-size="11">DEPTH 600 m · STAGE {stage+1}/10 · {STAGES[stage]}</text>
        <path d="M0 330 C120 314,220 341,330 326 S520 315,700 328 L700 390 L0 390 Z" fill="#173627" opacity=".85"/>
        <text x="610" y="355" fill="#8fa6b8" font-size="10">SEABED</text>

        <!-- valve frame -->
        <g stroke="#9db2c0" stroke-width="6" fill="none"><rect x="525" y="125" width="120" height="185"/><line x1="525" y1="125" x2="550" y2="100"/><line x1="645" y1="125" x2="620" y2="100"/><line x1="550" y1="100" x2="620" y2="100"/></g>
        <text x="530" y="90" fill="#dbe8ef" font-size="11">SUBSEA VALVE PANEL</text>
        <circle cx="{valve_x}" cy="{valve_y}" r="24" fill="#122637" stroke="#ffbd4a" stroke-width="4"/>
        <circle cx="{valve_x}" cy="{valve_y}" r="9" fill="#06111a" stroke="#ffbd4a" stroke-width="3"/>
        <text x="527" y="286" fill="#ffcf75" font-size="9">HOT-STAB TEP</text>

        <!-- ROV -->
        <g>
          <rect x="{rov_x}" y="{rov_y-62}" width="126" height="94" rx="10" fill="#d7b43d" stroke="#f4df89" stroke-width="3"/>
          <rect x="{rov_x+8}" y="{rov_y-49}" width="110" height="65" rx="4" fill="#102333" stroke="#d6e2e9" stroke-width="3"/>
          <rect x="{rov_x+27}" y="{rov_y-82}" width="72" height="25" rx="4" fill="#d7b43d" stroke="#f4df89" stroke-width="2"/>
          <circle cx="{rov_x+20}" cy="{rov_y-12}" r="14" fill="#07131e" stroke="#33d1ff" stroke-width="3"/>
          <circle cx="{rov_x+106}" cy="{rov_y-12}" r="14" fill="#07131e" stroke="#33d1ff" stroke-width="3"/>
          <text x="{rov_x+10}" y="{rov_y-33}" fill="#eef7fb" font-size="10" font-weight="700">SCHILLING HD-CLASS</text>
          <text x="{rov_x+31}" y="{rov_y-19}" fill="#8fa6b8" font-size="8">WROV SIMULATION</text>
        </g>

        <!-- FLS -->
        <path d="M {rov_x+122} {rov_y-25} L 510 170 L 510 300 Z" fill="#4b8cff" opacity="{'.28' if st.session_state.fls_available else '.04'}"/>
        <text x="{rov_x+126}" y="{rov_y-35}" fill="#78a8ff" font-size="9">FLS</text>

        <!-- manipulator -->
        <g fill="none" stroke="#72f2a5" stroke-linecap="round">
          <line x1="{sx}" y1="{sy}" x2="{ex}" y2="{ey}" stroke-width="12"/>
          <line x1="{ex}" y1="{ey}" x2="{wx}" y2="{wy}" stroke-width="10"/>
          <line x1="{wx}" y1="{wy}" x2="{tx}" y2="{ty}" stroke-width="8"/>
        </g>
        <g fill="#0b1824" stroke="#72f2a5" stroke-width="3"><circle cx="{sx}" cy="{sy}" r="8"/><circle cx="{ex}" cy="{ey}" r="8"/><circle cx="{wx}" cy="{wy}" r="7"/></g>
        <circle cx="{tx}" cy="{ty}" r="6" fill="{'#72f2a5' if stab_inserted else '#ffbd4a'}" stroke="#fff" stroke-width="2"/>
        <text x="{tx-15}" y="{ty-14}" fill="#72f2a5" font-size="9">TCP</text>
        <line x1="{tx}" y1="{ty}" x2="{valve_x}" y2="{valve_y}" stroke="{'#72f2a5' if stab_inserted else '#ffbd4a'}" stroke-width="4" stroke-dasharray="8 5"/>

        <rect x="16" y="340" width="668" height="32" rx="8" fill="#091621" stroke="#29465c"/>
        <text x="28" y="360" fill="#eef7fb" font-size="10">Range {target_range:.2f} m · Alignment {st.session_state.alignment_deg:.1f}° · Hydraulic {st.session_state.hydraulic_psi if stage>=7 else 0} psi · Valve {valve_pct}% OPEN</text>
      </svg>
    </div>
    """
    components.html(svg,height=610,scrolling=False)

    st.markdown("<div style='height:7px'></div>",unsafe_allow_html=True)
    k1,k2,k3,k4,k5 = st.columns(5)
    cards = [
        ("Localization",f"{st.session_state.localization_pct}%","PASS" if localization_pass else "HOLD","INS + DVL + IMU"),
        ("Point Cloud",f"{st.session_state.pointcloud_pct}%","PASS" if pointcloud_pass else "HOLD","Photogrammetry"),
        ("Distance Error",f"{st.session_state.distance_error_pct:.1f}%","PASS" if distance_pass else "HOLD","Limit ≤5%"),
        ("TCP/TEP Alignment",f"{st.session_state.alignment_deg:.1f}°","PASS" if alignment_pass else "HOLD","Active from Stage 6"),
        ("Hydraulic",f"{st.session_state.hydraulic_psi if stage>=7 else 0} psi","PASS" if (stage<7 or hydraulic_pass) else "HOLD","Active from Stage 8"),
    ]
    for col,(t,v,s,n) in zip([k1,k2,k3,k4,k5],cards):
        with col:
            st.markdown(f'<div class="ops-kpi"><div class="ops-kpi-title">{t}</div><div class="ops-kpi-value">{v}</div><div class="ops-kpi-status" style="color:{"#72f2a5" if s=="PASS" else "#ffd079"}">{s}</div><div class="ops-kpi-note">{n}</div></div>',unsafe_allow_html=True)

with right:
    st.markdown('<div class="panel"><div class="ph"><div><div class="pt">Stage Acceptance Gates</div><div class="ps">N/A → MONITOR → PASS/HOLD</div></div></div>',unsafe_allow_html=True)
    for label in ["Metocean","Point Cloud","Localization","Distance","Tool Match","Clearance","Alignment","Visibility/FLS","Pilot Review","Hydraulic","Evidence"]:
        s,c = gate_status[label]
        st.markdown(f'<div class="row"><span class="rk">{label}</span><span class="badge {c}">{s}</span></div>',unsafe_allow_html=True)
    st.markdown('</div>',unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>",unsafe_allow_html=True)
    active_holds = [k for k,(s,_) in gate_status.items() if s=="HOLD"]
    if stage_clear:
        decision = f'<div class="decision passbox"><div class="bigstate">{mission_state}</div>All active gates for <b>{STAGES[stage]}</b> are accepted. Mission may advance.</div>'
    else:
        decision = f'<div class="decision"><div class="bigstate">{mission_state}</div><b>Resolve:</b> {", ".join(active_holds)}.</div>'
    st.markdown(decision,unsafe_allow_html=True)

# ---------- mission controls ----------
st.markdown("<div style='height:10px'></div>",unsafe_allow_html=True)
b1,b2,b3,b4 = st.columns([1,1,1,1.3])

with b1:
    if st.button("Reset Mission",use_container_width=True):
        st.session_state.stage = 0
        st.session_state.mission_started = False
        st.session_state.mission_complete = False
        st.rerun()

with b2:
    if st.button("Advance Mission",use_container_width=True,disabled=(not stage_clear or stage>=9)):
        st.session_state.stage = min(9,stage+1)
        if st.session_state.stage >= 6:
            st.session_state.mission_started = True
        if st.session_state.stage >= 9:
            st.session_state.mission_complete = True
        st.rerun()

with b3:
    if st.button("Run Stage Acceptance Test",use_container_width=True):
        if stage_clear:
            st.success(f"{STAGES[stage]} acceptance test PASSED.")
        else:
            st.warning(f"{STAGES[stage]} acceptance test HOLD: {', '.join(active_holds)}.")

with b4:
    if stage>=9:
        st.success("MISSION ACCOMPLISHED · Completion evidence accepted · Handover unlocked.")
    elif stage_clear:
        st.info(f"Accepted stage: {STAGES[stage]} · Ready to advance.")
    else:
        st.warning("Mission blocked by active acceptance gate.")

# ---------- timeline ----------
timeline = '<div style="display:grid;grid-template-columns:repeat(10,1fr);gap:4px;margin-top:10px;">'
for i,label in enumerate(STAGES):
    if i < stage:
        bg,border,color = "rgba(43,213,118,.10)","#2bd576","#72f2a5"
    elif i == stage:
        bg,border,color = "rgba(51,209,255,.12)","#33d1ff","#dff8ff"
    else:
        bg,border,color = "#0c1824","#29465c","#7f97aa"
    timeline += f'<div style="background:{bg};border:1px solid {border};border-radius:7px;padding:5px;text-align:center;min-height:48px;"><div style="font-size:8px;font-weight:800;color:{color}">S{i+1}</div><div style="font-size:7.5px;color:{color};margin-top:3px">{label}</div></div>'
timeline += '</div>'
st.markdown(timeline,unsafe_allow_html=True)

ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
st.markdown(f'<div style="margin-top:9px;border-top:1px solid #1e3141;padding-top:7px;color:#6f8798;font-size:8px;display:flex;justify-content:space-between"><span>VODIDS · MRSIF v6.0 Acceptance Demo</span><span>Simulation only · {ts}</span></div>',unsafe_allow_html=True)
