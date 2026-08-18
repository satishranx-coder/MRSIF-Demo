
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import base64
import json
from datetime import datetime, timezone

# ============================================================
# VODIDS | MRSIF v7.0 — Mission Workspace
# ============================================================

st.set_page_config(
    page_title="VODIDS | MRSIF Mission Workspace",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

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

APPLICATIONS = [
    ("A01","Scope Intelligence"),("A02","Asset Identification"),
    ("A03","Vehicle Qualification"),("A04","Sensor Configuration"),
    ("A05","Tooling Compatibility"),("A06","Spatial Localization"),
    ("A07","Photogrammetry Intelligence"),("A08","Manipulator Validation"),
    ("A09","Environmental Assessment"),("A10","Execution Readiness"),
    ("A11","Live Mission Assurance"),("A12","Completion Verification"),
    ("A13","Data Handover"),
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

DEFAULT_MISSION = {
    "mission_id": "WR-2026-HS600",
    "mission_name": "600 m Hot Stab Valve Intervention",
    "client": "MRSIF Demonstration",
    "water_depth_m": 600,
    "vehicle": "Schilling HD-class WROV",
    "manipulator": "TITAN 4-class",
    "target_tag": "50-XV-0401",
    "cfihos_class": "Actuated Valve Assembly",
    "cfihos_code": "CFIHOS-10000284",
    "interface_standard": "API 17H",
    "required_torque_nm": 145,
    "pressure_rating_psi": 10000,
    "accepted_limits": {
        "current_max_kts": 1.5,
        "localization_min_pct": 85,
        "pointcloud_min_pct": 90,
        "distance_error_max_pct": 5.0,
        "clearance_min_mm": 50,
        "alignment_max_deg": 5.0,
        "hydraulic_min_psi": 3000,
    },
    "baseline": {
        "current_kts": 1.2,
        "visibility_m": 4.5,
        "localization_pct": 94,
        "pointcloud_pct": 96,
        "distance_error_pct": 3.2,
        "clearance_mm": 82,
        "alignment_deg": 2.4,
        "hydraulic_psi": 3500,
        "hydraulic_flow_lpm": 11.5,
        "tool_match": True,
        "dvl_lock": True,
        "fls_available": True,
        "pilot_confirmed": True,
        "ins_stable": True,
        "usbl_fix_valid": True,
        "usbl_age_s": 1.8,
        "dvl_bottom_lock": True,
        "depth_sensor_valid": True,
        "imu_valid": True,
        "photo_structure_match": True,
        "cfihos_asset_match": True,
    }
}

def logo_html(path="VODIDS.png"):
    p = Path(path)
    if not p.exists():
        return '<div class="logo-fallback">VODIDS</div>'
    try:
        b64 = base64.b64encode(p.read_bytes()).decode()
        return f'<img src="data:image/png;base64,{b64}" style="width:86px;height:54px;object-fit:contain;border-radius:8px;">'
    except Exception:
        return '<div class="logo-fallback">VODIDS</div>'

def load_mission_to_state(mission):
    st.session_state.mission = mission
    st.session_state.stage = 0
    st.session_state.mission_complete = False
    baseline = mission.get("baseline", {})
    for key, value in baseline.items():
        st.session_state[key] = value

# ---------- session ----------
if "mission" not in st.session_state:
    st.session_state.mission = DEFAULT_MISSION.copy()
if "stage" not in st.session_state:
    st.session_state.stage = 0
if "mission_complete" not in st.session_state:
    st.session_state.mission_complete = False

for key, value in DEFAULT_MISSION["baseline"].items():
    if key not in st.session_state:
        st.session_state[key] = value

# Backward compatibility for older deployed sessions / previous GUI versions.
if "hydraulic_flow_lpm" not in st.session_state:
    if "hydraulic_flow" in st.session_state:
        st.session_state.hydraulic_flow_lpm = st.session_state.hydraulic_flow
    else:
        st.session_state.hydraulic_flow_lpm = DEFAULT_MISSION["baseline"]["hydraulic_flow_lpm"]

for _k, _v in {
    "ins_stable": True,
    "usbl_fix_valid": True,
    "usbl_age_s": 1.8,
    "dvl_bottom_lock": True,
    "depth_sensor_valid": True,
    "imu_valid": True,
    "photo_structure_match": True,
    "cfihos_asset_match": True,
}.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ---------- style ----------
st.markdown("""
<style>
:root{
--bg:#071019;--panel:#0d1824;--panel2:#111f2e;--border:#24384a;
--text:#eef7fb;--muted:#8fa6b8;--cyan:#33d1ff;--green:#2bd576;
--amber:#ffbd4a;--red:#ff5f63;
}
.stApp{background:radial-gradient(circle at top,#102033 0%,#071019 52%,#050b11 100%);color:var(--text);}
.block-container{max-width:1800px;padding-top:.7rem;padding-bottom:1.5rem;}
#MainMenu,footer,header{visibility:hidden;}

.topbar{display:flex;justify-content:space-between;align-items:center;padding:13px 16px;
border:1px solid var(--border);border-radius:13px;background:#0c1824;margin-bottom:10px;}
.brand{display:flex;align-items:center;gap:12px}.brand-title{font-size:23px;font-weight:800;color:white}
.brand-sub{font-size:11px;color:var(--muted)}.logo-fallback{font-weight:800;color:var(--cyan)}

.mission-hero{display:grid;grid-template-columns:2.2fr 1fr 1fr 1fr;gap:8px;margin-bottom:10px}
.hero-main,.hero-item{background:#0d1824;border:1px solid var(--border);border-radius:10px;padding:11px 13px}
.hero-label{font-size:9px;color:var(--muted);letter-spacing:1px;text-transform:uppercase}
.hero-value{font-size:14px;color:#fff;font-weight:800;margin-top:3px}.hero-main .hero-value{font-size:18px}

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

.control-ribbon{display:grid;grid-template-columns:1.4fr repeat(4,1fr);gap:7px;margin:8px 0}
.ribbon-card{background:#0b1621;border:1px solid #29465c;border-radius:10px;padding:9px}
.ribbon-title{font-size:9px;color:#9fb4c3}.ribbon-value{font-size:16px;font-weight:900;color:#fff;margin-top:4px}
.ribbon-note{font-size:8px;color:#718a9c;margin-top:3px}

.decision{border-left:4px solid var(--amber);background:rgba(255,189,74,.07);padding:10px;border-radius:8px;font-size:10px;line-height:1.4}
.decision.passbox{border-left-color:var(--green);background:rgba(43,213,118,.07)}
.bigstate{font-size:18px;font-weight:900;margin-bottom:5px}

.stButton>button{background:#123048!important;color:#eef7fb!important;border:1px solid #2f6681!important;
border-radius:9px!important;min-height:42px!important;font-weight:800!important}
.stButton>button:hover{border-color:#33d1ff!important;background:#163b57!important}
.stButton>button:disabled{background:#17232e!important;color:#637a8b!important;border-color:#2b3e4e!important;opacity:1!important}
div[data-testid="stNumberInput"] label,
div[data-testid="stCheckbox"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stSlider"] label,
div[data-testid="stFileUploader"] label,
div[data-testid="stExpander"] label{
color:#eef7fb!important;font-weight:700!important;
}
div[data-testid="stNumberInput"] input{color:#eef7fb!important;background:#0b1621!important}
div[data-testid="stExpander"]{background:#0d1824!important;border:1px solid #24384a!important;border-radius:10px!important}
div[data-testid="stExpander"] summary{color:#eef7fb!important;background:#111f2e!important}

.loc-panel{background:#091621;border:1px solid #29465c;border-radius:10px;padding:9px;margin-top:8px}
.loc-title{font-size:10px;font-weight:800;color:#dff4ff;margin-bottom:7px;letter-spacing:.4px}
.loc-row{display:grid;grid-template-columns:1.35fr .75fr 1fr;gap:5px;align-items:center;padding:5px 0;border-bottom:1px solid rgba(41,70,92,.55);font-size:9px}
.loc-row:last-child{border-bottom:none}
.loc-name{color:#9db4c3}.loc-state{font-weight:800;text-align:center}.loc-evidence{color:#6f8999;text-align:right}
.loc-pass{color:#72f2a5}.loc-monitor{color:#76dbff}.loc-hold{color:#ffd079}
.progress-mini{display:grid;grid-template-columns:repeat(5,1fr);gap:3px;margin-top:7px}
.progress-mini div{border:1px solid #29465c;border-radius:6px;padding:4px;text-align:center;font-size:7px;color:#7892a3}
.progress-mini .done{border-color:#2bd576;color:#72f2a5;background:rgba(43,213,118,.07)}
.progress-mini .active{border-color:#33d1ff;color:#dff8ff;background:rgba(51,209,255,.09)}
.twin-note{font-size:8px;color:#7e98a8;margin-top:5px}

</style>
""", unsafe_allow_html=True)

mission = st.session_state.mission
limits = mission.get("accepted_limits", DEFAULT_MISSION["accepted_limits"])
stage = st.session_state.stage

# ============================================================
# SIDEBAR — Mission opening / selection
# ============================================================
with st.sidebar:
    st.markdown("## Mission Workspace")
    st.caption("A mission is loaded by default. Open another mission only when required.")

    st.markdown("### Active Mission")
    st.success(mission.get("mission_name", "Mission"))

    if st.button("Reload Default Demo Mission", use_container_width=True):
        load_mission_to_state(DEFAULT_MISSION.copy())
        st.rerun()

    uploaded = st.file_uploader(
        "Open Mission File (.json)",
        type=["json"],
        help="Optional. Upload a mission JSON to replace the default demonstration mission."
    )

    if uploaded is not None:
        try:
            loaded = json.loads(uploaded.getvalue().decode("utf-8"))
            required = ["mission_id","mission_name","water_depth_m","vehicle","target_tag"]
            missing = [k for k in required if k not in loaded]
            if missing:
                st.error("Mission file missing: " + ", ".join(missing))
            else:
                if st.button("Open Uploaded Mission", use_container_width=True):
                    # merge optional defaults to keep demo robust
                    merged = DEFAULT_MISSION.copy()
                    merged.update(loaded)
                    merged["accepted_limits"] = {
                        **DEFAULT_MISSION["accepted_limits"],
                        **loaded.get("accepted_limits", {})
                    }
                    merged["baseline"] = {
                        **DEFAULT_MISSION["baseline"],
                        **loaded.get("baseline", {})
                    }
                    load_mission_to_state(merged)
                    st.rerun()
        except Exception as e:
            st.error(f"Invalid mission JSON: {e}")

    st.markdown("---")
    st.markdown("### Mission Data")
    st.write(f"**Work Ref:** {mission.get('mission_id')}")
    st.write(f"**Depth:** {mission.get('water_depth_m')} m")
    st.write(f"**Vehicle:** {mission.get('vehicle')}")
    st.write(f"**Target:** {mission.get('target_tag')}")
    st.write(f"**Interface:** {mission.get('interface_standard','—')}")

# ============================================================
# OPERATIONAL CHECKS
# ============================================================
current_pass = st.session_state.current_kts <= limits["current_max_kts"]
pointcloud_pass = st.session_state.pointcloud_pct >= limits["pointcloud_min_pct"]
localization_pass = (
    st.session_state.localization_pct >= limits["localization_min_pct"]
    and st.session_state.dvl_lock
    and st.session_state.ins_stable
    and st.session_state.usbl_fix_valid
    and st.session_state.dvl_bottom_lock
    and st.session_state.depth_sensor_valid
    and st.session_state.imu_valid
    and st.session_state.photo_structure_match
    and st.session_state.cfihos_asset_match
)
distance_pass = st.session_state.distance_error_pct <= limits["distance_error_max_pct"]
clearance_pass = st.session_state.clearance_mm >= limits["clearance_min_mm"]
alignment_pass = st.session_state.alignment_deg <= limits["alignment_max_deg"]
visibility_pass = st.session_state.visibility_m >= 1.5 or st.session_state.fls_available
hydraulic_pass = st.session_state.hydraulic_psi >= limits["hydraulic_min_psi"]
tool_pass = st.session_state.tool_match
pilot_pass = st.session_state.pilot_confirmed

def stage_status(applies_from, condition, monitor_from=None):
    if monitor_from is None:
        monitor_from = applies_from
    if stage < monitor_from:
        return ("N/A","na")
    if stage < applies_from:
        return ("MONITOR","monitor")
    return ("PASS","pass") if condition else ("HOLD","hold")

gate_status = {
    "Metocean": stage_status(1,current_pass,0),
    "Point Cloud": stage_status(2,pointcloud_pass,1),
    "Localization": stage_status(2,localization_pass,1),
    "Distance": stage_status(2,distance_pass,1),
    "Tool Match": stage_status(4,tool_pass,3),
    "Clearance": stage_status(5,clearance_pass,4),
    "Alignment": stage_status(5,alignment_pass,4),
    "Visibility/FLS": stage_status(2,visibility_pass,1),
    "Pilot Review": stage_status(4,pilot_pass,3),
    "Hydraulic": stage_status(7,hydraulic_pass,6),
    "Evidence": ("PASS","pass") if stage >= 8 else (("MONITOR","monitor") if stage >= 6 else ("N/A","na")),
}

active_conditions = []
if stage >= 1:
    active_conditions += [current_pass]
if stage >= 2:
    active_conditions += [pointcloud_pass, localization_pass, distance_pass, visibility_pass]
if stage >= 4:
    active_conditions += [tool_pass, pilot_pass]
if stage >= 5:
    active_conditions += [clearance_pass, alignment_pass]
if stage >= 7:
    active_conditions += [hydraulic_pass]

stage_clear = all(active_conditions) if active_conditions else True

if stage >= 9:
    mission_state = "MISSION ACCOMPLISHED"
    state_color = "#72f2a5"
elif stage >= 6 and stage_clear:
    mission_state = "INTERVENTION IN PROGRESS"
    state_color = "#76dbff"
elif stage_clear:
    mission_state = "READY TO ADVANCE"
    state_color = "#72f2a5"
else:
    mission_state = "HOLD — ACTIVE GATE"
    state_color = "#ffd079"

# ============================================================
# HEADER / MISSION HERO
# ============================================================
st.markdown(f"""
<div class="topbar">
  <div class="brand">{logo_html()}
    <div>
      <div class="brand-title">MRSIF <span style="color:#33d1ff;">Mission Workspace</span></div>
      <div class="brand-sub">VODIDS · CFIHOS-aligned asset context · OSDU-linked operational data</div>
    </div>
  </div>
  <div style="font-size:10px;color:#8fa6b8;">SIMULATED DEMONSTRATION ENVIRONMENT</div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="mission-hero">
  <div class="hero-main">
    <div class="hero-label">Active Mission</div>
    <div class="hero-value">{mission.get('mission_name')}</div>
  </div>
  <div class="hero-item"><div class="hero-label">Work Ref</div><div class="hero-value">{mission.get('mission_id')}</div></div>
  <div class="hero-item"><div class="hero-label">Depth</div><div class="hero-value">{mission.get('water_depth_m')} m</div></div>
  <div class="hero-item"><div class="hero-label">Mission State</div><div class="hero-value" style="color:{state_color}">{mission_state}</div></div>
</div>
""", unsafe_allow_html=True)

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

# ============================================================
# MAIN WORKSPACE
# ============================================================
left, center, right = st.columns([0.78,3.55,0.95], gap="small")

with left:
    st.markdown('<div class="panel"><div class="ph"><div><div class="pt">7 MRSIF Core Layers</div><div class="ps">Mission governance stack</div></div></div>', unsafe_allow_html=True)
    layer_logic = [
        current_pass if stage>=1 else True,
        True,
        True,
        tool_pass if stage>=4 else True,
        stage_clear,
        True,
        stage>=9,
    ]
    for (code,name),ok in zip(LAYER_NAMES,layer_logic):
        if name=="Handover / Data Delivery" and stage<9:
            s,c = "LOCKED","na"
        else:
            s,c = ("PASS","pass") if ok else ("HOLD","hold")
        st.markdown(f'<div class="layer"><div class="lc">{code}</div><div class="ln">{name}</div><div class="badge {c}">{s}</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="panel"><div class="ph"><div><div class="pt">Mission / Asset Context</div><div class="ps">CFIHOS-aligned identity</div></div></div>', unsafe_allow_html=True)
    asset_rows = [
        ("Target Tag", mission.get("target_tag")),
        ("Asset Class", mission.get("cfihos_class","—")),
        ("CFIHOS Code", mission.get("cfihos_code","—")),
        ("Interface", mission.get("interface_standard","—")),
        ("Required Torque", f'{mission.get("required_torque_nm","—")} Nm'),
        ("Pressure Rating", f'{mission.get("pressure_rating_psi","—")} psi'),
        ("Vehicle", mission.get("vehicle")),
        ("Manipulator", mission.get("manipulator","—")),
    ]
    for k,v in asset_rows:
        st.markdown(f'<div class="row"><span class="rk">{k}</span><span class="rv">{v}</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with center:
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
    <div style="background:#06121c;border:1px solid #284156;border-radius:14px;padding:10px;font-family:Arial,sans-serif;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:7px;">
        <div>
          <b style="color:#eef7fb;font-size:13px;">Operational Digital Twin · {mission.get('mission_name')}</b><br>
          <span style="color:#8fa6b8;font-size:9px;">Engineering representation · simulated mission data · not OEM CAD</span>
        </div>
        <span style="padding:5px 9px;border-radius:14px;border:1px solid {state_color};color:{state_color};font-size:9px;font-weight:800;">
          {mission_state}
        </span>
      </div>
      <svg viewBox="0 0 900 540" width="100%" role="img" aria-label="ROV hot stab intervention and localization simulation">
        <defs>
          <linearGradient id="water2" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#123e5c"/><stop offset="58%" stop-color="#0a2538"/><stop offset="100%" stop-color="#051019"/>
          </linearGradient>
          <linearGradient id="rovbody" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stop-color="#d4b849"/><stop offset="100%" stop-color="#987d1e"/>
          </linearGradient>
          <pattern id="grid2" width="38" height="38" patternUnits="userSpaceOnUse">
            <path d="M38 0L0 0 0 38" fill="none" stroke="#2a4d62" stroke-width=".55"/>
          </pattern>
        </defs>
        <rect width="760" height="430" rx="12" fill="url(#water2)"/>
        <rect width="760" height="430" rx="12" fill="url(#grid2)" opacity=".48"/>

        <rect x="16" y="15" width="172" height="42" rx="8" fill="#071824" stroke="#31566e"/>
        <text x="28" y="33" fill="#8fa6b8" font-size="9">OPERATING DEPTH</text>
        <text x="28" y="49" fill="#eef7fb" font-size="15" font-weight="700">{mission.get('water_depth_m')} m</text>

        <rect x="197" y="15" width="228" height="42" rx="8" fill="#071824" stroke="#31566e"/>
        <text x="209" y="33" fill="#8fa6b8" font-size="9">MISSION STAGE</text>
        <text x="209" y="49" fill="#eef7fb" font-size="12" font-weight="700">{stage+1}/10 · {STAGES[stage]}</text>

        <rect x="434" y="15" width="145" height="42" rx="8" fill="#071824" stroke="#31566e"/>
        <text x="446" y="33" fill="#8fa6b8" font-size="9">TARGET RANGE</text>
        <text x="446" y="49" fill="#eef7fb" font-size="15" font-weight="700">{target_range:.2f} m</text>

        <rect x="588" y="15" width="155" height="42" rx="8" fill="#071824" stroke="#31566e"/>
        <text x="600" y="33" fill="#8fa6b8" font-size="9">TCP / TEP ERROR</text>
        <text x="600" y="49" fill="{'#72f2a5' if alignment_pass else '#ffd079'}" font-size="15" font-weight="700">{st.session_state.alignment_deg:.1f}°</text>

        <path d="M0 354 C85 338,160 366,250 350 S420 337,520 350 S660 340,760 354 L760 430 L0 430 Z" fill="#18382b"/>
        <text x="674" y="395" fill="#8fa6b8" font-size="9">SEABED REFERENCE</text>


        <!-- Navigation / localization evidence -->
        <g>
          <!-- USBL acoustic fix from surface reference (schematic) -->
          <line x1="120" y1="72" x2="{rov_x+74}" y2="{rov_y+34}" stroke="#76dbff" stroke-width="2" stroke-dasharray="8 6" opacity=".9"/>
          <circle cx="120" cy="72" r="7" fill="#0a2538" stroke="#76dbff" stroke-width="2"/>
          <text x="136" y="69" fill="#9edfff" font-size="9">USBL POSITION UPDATE</text>
          <text x="136" y="82" fill="#6f8999" font-size="8">Fix age {st.session_state.usbl_age_s:.1f} s · VALID</text>

          <!-- DVL seabed lock beams -->
          <line x1="{rov_x+54}" y1="{rov_y+32}" x2="{rov_x+24}" y2="345" stroke="#72f2a5" stroke-width="2" opacity=".72"/>
          <line x1="{rov_x+65}" y1="{rov_y+32}" x2="{rov_x+52}" y2="350" stroke="#72f2a5" stroke-width="2" opacity=".72"/>
          <line x1="{rov_x+82}" y1="{rov_y+32}" x2="{rov_x+94}" y2="350" stroke="#72f2a5" stroke-width="2" opacity=".72"/>
          <line x1="{rov_x+94}" y1="{rov_y+32}" x2="{rov_x+124}" y2="345" stroke="#72f2a5" stroke-width="2" opacity=".72"/>
          <text x="{rov_x+18}" y="366" fill="#8fe7b0" font-size="8">DVL BOTTOM LOCK · SETTLED</text>

          <!-- INS / IMU vector -->
          <line x1="{rov_x+74}" y1="{rov_y+34}" x2="{rov_x+128}" y2="{rov_y+34}" stroke="#ffcf75" stroke-width="3"/>
          <polygon points="{rov_x+128},{rov_y+34} {rov_x+117},{rov_y+29} {rov_x+117},{rov_y+39}" fill="#ffcf75"/>
          <text x="{rov_x+78}" y="{rov_y+53}" fill="#ffcf75" font-size="8">INS / IMU HEADING STABLE</text>

          <!-- Photogrammetry structure registration -->
          <rect x="548" y="102" width="175" height="244" rx="8" fill="none" stroke="#33d1ff" stroke-width="2" stroke-dasharray="5 5" opacity=".8"/>
          <text x="552" y="360" fill="#76dbff" font-size="8">PHOTOGRAMMETRY STRUCTURE MATCH · CONFIRMED</text>
          <text x="552" y="373" fill="#6f8999" font-size="8">Matched to CFIHOS {mission.get('cfihos_code','asset class')}</text>
        </g>

        <g stroke="#a2b8c6" stroke-width="7" fill="none">
          <rect x="573" y="112" width="132" height="218" rx="3"/>
          <line x1="573" y1="112" x2="600" y2="86"/><line x1="705" y1="112" x2="678" y2="86"/>
          <line x1="600" y1="86" x2="678" y2="86"/><line x1="590" y1="175" x2="688" y2="175"/>
          <line x1="590" y1="265" x2="688" y2="265"/>
        </g>
        <text x="582" y="76" fill="#e4eef3" font-size="11" font-weight="700">SUBSEA VALVE / HOT-STAB PANEL</text>
        <circle cx="{valve_x}" cy="{valve_y}" r="27" fill="#122637" stroke="#ffbd4a" stroke-width="4"/>
        <circle cx="{valve_x}" cy="{valve_y}" r="11" fill="#06111a" stroke="#ffbd4a" stroke-width="3"/>
        <text x="{valve_x-34}" y="{valve_y+47}" fill="#ffcf75" font-size="9" font-weight="700">TEP · {mission.get('target_tag')}</text>

        <g>
          <rect x="{rov_x}" y="{rov_y-72}" width="148" height="106" rx="10" fill="url(#rovbody)" stroke="#f1dd86" stroke-width="3"/>
          <rect x="{rov_x+10}" y="{rov_y-57}" width="128" height="72" rx="4" fill="#102433" stroke="#c8d5dd" stroke-width="3"/>
          <rect x="{rov_x+33}" y="{rov_y-94}" width="78" height="28" rx="4" fill="url(#rovbody)" stroke="#f1dd86" stroke-width="2"/>
          <circle cx="{rov_x+20}" cy="{rov_y-5}" r="16" fill="#06111a" stroke="#33d1ff" stroke-width="3"/>
          <circle cx="{rov_x+128}" cy="{rov_y-5}" r="16" fill="#06111a" stroke="#33d1ff" stroke-width="3"/>
          <text x="{rov_x+15}" y="{rov_y-52}" fill="#eef7fb" font-size="10" font-weight="700">{mission.get('vehicle')}</text>
          <text x="{rov_x+35}" y="{rov_y-20}" fill="#8fa6b8" font-size="8">ENGINEERING SIMULATION</text>
        </g>

        <path d="M {rov_x+143} {rov_y-37} L 555 150 L 555 315 Z"
              fill="#4b8cff" opacity="{'.26' if st.session_state.fls_available else '.03'}"/>
        <text x="{rov_x+150}" y="{rov_y-47}" fill="#8ab3ff" font-size="9">FLS SEARCH / LOCALIZATION</text>

        <g fill="none" stroke="#72f2a5" stroke-linecap="round">
          <line x1="{sx}" y1="{sy}" x2="{ex}" y2="{ey}" stroke-width="14"/>
          <line x1="{ex}" y1="{ey}" x2="{wx}" y2="{wy}" stroke-width="12"/>
          <line x1="{wx}" y1="{wy}" x2="{tx}" y2="{ty}" stroke-width="9"/>
        </g>
        <g fill="#0c1c28" stroke="#72f2a5" stroke-width="3">
          <circle cx="{sx}" cy="{sy}" r="9"/><circle cx="{ex}" cy="{ey}" r="9"/><circle cx="{wx}" cy="{wy}" r="8"/>
        </g>
        <rect x="{tx-3}" y="{ty-7}" width="38" height="14" rx="5"
              fill="{'#72f2a5' if stab_inserted else '#ffbd4a'}" stroke="#ffffff" stroke-width="1.5"/>
        <circle cx="{tx}" cy="{ty}" r="6" fill="{'#72f2a5' if stab_inserted else '#ffbd4a'}" stroke="#fff" stroke-width="2"/>
        <text x="{tx-14}" y="{ty-17}" fill="#72f2a5" font-size="9" font-weight="700">TCP</text>

        <line x1="{tx+34}" y1="{ty}" x2="{valve_x-10}" y2="{valve_y}"
              stroke="{'#72f2a5' if stab_inserted else '#ffbd4a'}" stroke-width="4" stroke-dasharray="9 5"/>

        <rect x="16" y="371" width="728" height="43" rx="9" fill="#071824" stroke="#31566e"/>
        <text x="30" y="390" fill="#8fa6b8" font-size="9">HYDRAULIC</text>
        <text x="30" y="406" fill="#eef7fb" font-size="13" font-weight="700">{st.session_state.hydraulic_psi if stage>=7 else 0} psi</text>
        <text x="172" y="390" fill="#8fa6b8" font-size="9">FLOW</text>
        <text x="172" y="406" fill="#eef7fb" font-size="13" font-weight="700">{st.session_state.hydraulic_flow_lpm if stage>=7 else 0:.1f} L/min</text>
        <text x="280" y="390" fill="#8fa6b8" font-size="9">VALVE STATE</text>
        <text x="280" y="406" fill="{'#72f2a5' if valve_pct==100 else '#eef7fb'}" font-size="13" font-weight="700">{valve_pct}% OPEN</text>
        <text x="420" y="390" fill="#8fa6b8" font-size="9">POINT CLOUD</text>
        <text x="420" y="406" fill="#eef7fb" font-size="13" font-weight="700">{st.session_state.pointcloud_pct}%</text>
        <text x="545" y="390" fill="#8fa6b8" font-size="9">LOCALIZATION</text>
        <text x="545" y="406" fill="#eef7fb" font-size="13" font-weight="700">{st.session_state.localization_pct}%</text>
      </svg>
    </div>
    """
    components.html(svg,height=790,scrolling=False)

    # Operational localization assurance — compact and evidence-based
    usbl_state = "VALID" if st.session_state.usbl_fix_valid else "HOLD"
    nav_state = "STABLE" if st.session_state.ins_stable else "HOLD"
    dvl_state = "SETTLED" if st.session_state.dvl_bottom_lock else "LOST"
    photo_state = "CONFIRMED" if st.session_state.photo_structure_match else "HOLD"
    cfihos_state = "MATCHED" if st.session_state.cfihos_asset_match else "HOLD"

    st.markdown(f"""
    <div class="loc-panel">
      <div class="loc-title">ROV LOCALIZATION ASSURANCE · WHY MRSIF ACCEPTS THE VEHICLE POSITION</div>
      <div class="loc-row"><span class="loc-name">INS Navigation Solution</span><span class="loc-state {'loc-pass' if st.session_state.ins_stable else 'loc-hold'}">{nav_state}</span><span class="loc-evidence">Heading / attitude propagated</span></div>
      <div class="loc-row"><span class="loc-name">USBL Absolute Position</span><span class="loc-state {'loc-pass' if st.session_state.usbl_fix_valid else 'loc-hold'}">{usbl_state}</span><span class="loc-evidence">Last update {st.session_state.usbl_age_s:.1f} s</span></div>
      <div class="loc-row"><span class="loc-name">DVL Seabed Lock</span><span class="loc-state {'loc-pass' if st.session_state.dvl_bottom_lock else 'loc-hold'}">{dvl_state}</span><span class="loc-evidence">Bottom-track velocity constraint</span></div>
      <div class="loc-row"><span class="loc-name">Depth + Internal IMU</span><span class="loc-state {'loc-pass' if (st.session_state.depth_sensor_valid and st.session_state.imu_valid) else 'loc-hold'}">VALID</span><span class="loc-evidence">Depth / roll / pitch reference</span></div>
      <div class="loc-row"><span class="loc-name">Photogrammetry Structure Registration</span><span class="loc-state {'loc-pass' if st.session_state.photo_structure_match else 'loc-hold'}">{photo_state}</span><span class="loc-evidence">Observed structure ↔ 3D reference</span></div>
      <div class="loc-row"><span class="loc-name">CFIHOS Asset Identity</span><span class="loc-state {'loc-pass' if st.session_state.cfihos_asset_match else 'loc-hold'}">{cfihos_state}</span><span class="loc-evidence">{mission.get('target_tag')} · {mission.get('cfihos_code')}</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="control-ribbon">
      <div class="ribbon-card">
        <div class="ribbon-title">Current Mission Stage</div>
        <div class="ribbon-value">{STAGES[stage]}</div>
        <div class="ribbon-note">Only active-stage gates can stop progression.</div>
      </div>
      <div class="ribbon-card"><div class="ribbon-title">Localization Confidence</div><div class="ribbon-value">{st.session_state.localization_pct}%</div><div class="ribbon-note">INS + USBL + DVL + IMU</div></div>
      <div class="ribbon-card"><div class="ribbon-title">Point-Cloud Match</div><div class="ribbon-value">{st.session_state.pointcloud_pct}%</div><div class="ribbon-note">Structure registration</div></div>
      <div class="ribbon-card"><div class="ribbon-title">TCP → TEP Alignment</div><div class="ribbon-value">{st.session_state.alignment_deg:.1f}°</div><div class="ribbon-note">Tool engagement geometry</div></div>
      <div class="ribbon-card"><div class="ribbon-title">Manipulator Clearance</div><div class="ribbon-value">{st.session_state.clearance_mm} mm</div><div class="ribbon-note">Collision envelope</div></div>
    </div>
    """, unsafe_allow_html=True)

with right:
    st.markdown('<div class="panel"><div class="ph"><div><div class="pt">Mission Acceptance</div><div class="ps">Only active-stage gates can stop the mission</div></div></div>', unsafe_allow_html=True)
    for label in ["Metocean","Point Cloud","Localization","Distance","Tool Match","Clearance","Alignment","Visibility/FLS","Pilot Review","Hydraulic","Evidence"]:
        s,c = gate_status[label]
        st.markdown(f'<div class="row"><span class="rk">{label}</span><span class="badge {c}">{s}</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Compact mission progress
    prog = '<div class="loc-panel"><div class="loc-title">MISSION PROGRESS</div><div class="progress-mini">'
    for i, label in enumerate(STAGES):
        if i < stage:
            cls = "done"
        elif i == stage:
            cls = "active"
        else:
            cls = ""
        short = f"S{i+1}"
        prog += f'<div class="{cls}" title="{label}">{short}</div>'
    prog += '</div><div class="twin-note">Advance one stage at a time after acceptance.</div></div>'
    st.markdown(prog, unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    active_holds = [k for k,(s,_) in gate_status.items() if s=="HOLD"]
    if stage_clear:
        st.markdown(f'<div class="decision passbox"><div class="bigstate">{mission_state}</div><b>{STAGES[stage]}</b> is accepted. Continue when ready.</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="decision"><div class="bigstate">{mission_state}</div><b>Resolve:</b> {", ".join(active_holds)}.</div>', unsafe_allow_html=True)

# ============================================================
# MISSION COMMAND BAR
# ============================================================
st.markdown("---")
cmd1,cmd2,cmd3,cmd4 = st.columns([1,1.2,1,1.3])

with cmd1:
    if st.button("Reset Mission", use_container_width=True):
        load_mission_to_state(st.session_state.mission)
        st.rerun()

with cmd2:
    if st.button("Advance Mission →", use_container_width=True, disabled=(not stage_clear or stage>=9)):
        st.session_state.stage = min(9, stage+1)
        if st.session_state.stage >= 9:
            st.session_state.mission_complete = True
        st.rerun()

with cmd3:
    if st.button("Stage Acceptance Test", use_container_width=True):
        if stage_clear:
            st.success(f"{STAGES[stage]} accepted.")
        else:
            st.warning(f"HOLD: {', '.join(active_holds)}")

with cmd4:
    if stage >= 9:
        st.success("MISSION ACCOMPLISHED · Handover unlocked.")
    elif stage_clear:
        st.info("Mission loaded and ready. Advance one stage at a time.")
    else:
        st.warning("Mission held by active validation gate.")

# ============================================================
# ENGINEERING PARAMETERS — tucked away, not the primary UI
# ============================================================
with st.expander("Engineering / Demonstration Parameters", expanded=False):
    st.caption("These values support the demonstration. They are not the primary mission-navigation interface.")
    p1,p2,p3,p4 = st.columns(4)
    with p1:
        st.session_state.current_kts = st.number_input("Seafloor current (kts)",0.0,4.0,float(st.session_state.current_kts),0.1)
        st.session_state.visibility_m = st.number_input("Visibility (m)",0.0,20.0,float(st.session_state.visibility_m),0.5)
    with p2:
        st.session_state.localization_pct = st.number_input("Localization confidence (%)",0,100,int(st.session_state.localization_pct),1)
        st.session_state.pointcloud_pct = st.number_input("Point-cloud confidence (%)",0,100,int(st.session_state.pointcloud_pct),1)
    with p3:
        st.session_state.distance_error_pct = st.number_input("ROV-target error (%)",0.0,20.0,float(st.session_state.distance_error_pct),0.1)
        st.session_state.clearance_mm = st.number_input("Manipulator clearance (mm)",0,500,int(st.session_state.clearance_mm),5)
        st.session_state.alignment_deg = st.number_input("TCP/TEP alignment error (°)",0.0,20.0,float(st.session_state.alignment_deg),0.1)
    with p4:
        st.session_state.hydraulic_psi = st.number_input("Hydraulic pressure (psi)",0,5000,int(st.session_state.hydraulic_psi),100)
        st.session_state.hydraulic_flow_lpm = st.number_input("Hydraulic flow (L/min)",0.0,30.0,float(st.session_state.hydraulic_flow_lpm),0.5)
        st.session_state.tool_match = st.checkbox("Correct hot stab / interface",st.session_state.tool_match)
        st.session_state.dvl_lock = st.checkbox("DVL bottom lock",st.session_state.dvl_lock)
        st.session_state.fls_available = st.checkbox("FLS available",st.session_state.fls_available)
        st.session_state.pilot_confirmed = st.checkbox("Pilot risk review confirmed",st.session_state.pilot_confirmed)
        st.session_state.ins_stable = st.checkbox("INS stable", st.session_state.ins_stable)
        st.session_state.usbl_fix_valid = st.checkbox("USBL fix valid", st.session_state.usbl_fix_valid)
        st.session_state.dvl_bottom_lock = st.checkbox("DVL bottom lock settled", st.session_state.dvl_bottom_lock)
        st.session_state.photo_structure_match = st.checkbox("Photogrammetry structure match", st.session_state.photo_structure_match)
        st.session_state.cfihos_asset_match = st.checkbox("CFIHOS asset identity matched", st.session_state.cfihos_asset_match)


# Timeline
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
st.markdown(timeline, unsafe_allow_html=True)

ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
st.markdown(f'<div style="margin-top:9px;border-top:1px solid #1e3141;padding-top:7px;color:#6f8798;font-size:8px;display:flex;justify-content:space-between"><span>VODIDS · MRSIF v7.2 Mission Workspace</span><span>Simulation only · {ts}</span></div>', unsafe_allow_html=True)
