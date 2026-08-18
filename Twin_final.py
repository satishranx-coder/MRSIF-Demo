
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
    initial_sidebar_state="collapsed",
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
    st.session_state.report_unlocked = False
    st.session_state.workspace_page = "OPERATIONS"
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
if "report_unlocked" not in st.session_state:
    st.session_state.report_unlocked = False
if "workspace_page" not in st.session_state:
    st.session_state.workspace_page = "OPERATIONS"

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
.block-container{max-width:1920px;padding:0.45rem 1rem 1rem 1rem;}
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


.ops-status-strip{
display:grid;grid-template-columns:1.35fr repeat(5,1fr);gap:6px;margin:7px 0 9px 0;
}
.ops-status{
background:#0b1722;border:1px solid #29465c;border-radius:9px;padding:7px 9px;min-height:48px;
}
.ops-status .k{font-size:8px;color:#829aaa;text-transform:uppercase;letter-spacing:.7px}
.ops-status .v{font-size:11px;color:#eef7fb;font-weight:800;margin-top:3px}
.ops-status .ok{color:#72f2a5}.ops-status .warn{color:#ffd079}.ops-status .live{color:#76dbff}
.compact-panel{background:#0d1824;border:1px solid #24384a;border-radius:10px;padding:8px}
.compact-row{display:flex;justify-content:space-between;gap:6px;padding:4px 0;border-bottom:1px solid rgba(36,56,74,.48);font-size:9px}
.compact-row:last-child{border-bottom:none}
.process-list{display:flex;flex-direction:column;gap:5px}
.process-step{display:grid;grid-template-columns:22px 1fr 54px;gap:6px;align-items:center;
border:1px solid #29465c;border-radius:7px;padding:6px 7px;background:#0b1722}
.process-step .pn{font-size:8px;color:#6f8999;font-weight:800}
.process-step .ptxt{font-size:8.5px;color:#8fa6b8;line-height:1.15}
.process-step.done{border-color:#2bd576;background:rgba(43,213,118,.05)}
.process-step.done .pn,.process-step.done .ptxt{color:#72f2a5}
.process-step.active{border-color:#33d1ff;background:rgba(51,209,255,.08)}
.process-step.active .pn,.process-step.active .ptxt{color:#e3f8ff}
.proc-status{font-size:7px;font-weight:800;text-align:center;border-radius:10px;padding:3px 4px;border:1px solid #3a5364;color:#8199a9}
.process-step.done .proc-status{border-color:#2bd576;color:#72f2a5}
.process-step.active .proc-status{border-color:#33d1ff;color:#76dbff}
.report-table{width:100%;border-collapse:collapse;font-size:9px}
.report-table th{color:#9fb4c3;text-align:left;border-bottom:1px solid #345065;padding:6px}
.report-table td{color:#dce9ef;border-bottom:1px solid rgba(52,80,101,.45);padding:6px;vertical-align:top}
.report-note{font-size:9px;color:#7f98a8;line-height:1.45}
div[role="radiogroup"]{gap:.35rem!important}

/* Final readability / report styling */
div[data-testid="stMarkdownContainer"] p,
div[data-testid="stMarkdownContainer"] li,
div[data-testid="stMarkdownContainer"] h1,
div[data-testid="stMarkdownContainer"] h2,
div[data-testid="stMarkdownContainer"] h3,
div[data-testid="stMarkdownContainer"] h4 {
    color:#e6f0f5 !important;
}
div[data-testid="stMetric"] {
    background:#0d1824 !important;
    border:1px solid #29465c !important;
    border-radius:10px !important;
    padding:10px !important;
}
div[data-testid="stMetric"] label,
div[data-testid="stMetric"] div {
    color:#eef7fb !important;
}
.report-shell{
    background:#0b1722;border:1px solid #29465c;border-radius:12px;padding:12px;color:#dce9ef;
}
.report-shell h3{color:#eef7fb;margin:0 0 8px 0;font-size:13px}
.report-shell p{color:#a9becb;font-size:9px;line-height:1.45}
.restart-note{
    border:1px solid #2f6681;border-left:4px solid #33d1ff;background:rgba(51,209,255,.06);
    border-radius:9px;padding:9px 10px;color:#cfe4ee;font-size:9px;line-height:1.45;margin-top:8px;
}
</style>
""", unsafe_allow_html=True)

mission = st.session_state.mission
limits = mission.get("accepted_limits", DEFAULT_MISSION["accepted_limits"])
stage = st.session_state.stage

# ============================================================
# MISSION MANAGER — compact, collapsed by default
# ============================================================
mission = st.session_state.mission
limits = mission.get("accepted_limits", DEFAULT_MISSION["accepted_limits"])
stage = st.session_state.stage

with st.expander("Mission Manager · Default mission already loaded", expanded=False):
    mm1, mm2, mm3 = st.columns([1.4,1,1])
    with mm1:
        st.write(f"**Active:** {mission.get('mission_name')}")
        st.caption(f"{mission.get('mission_id')} · {mission.get('water_depth_m')} m · {mission.get('vehicle')}")
    with mm2:
        if st.button("Reload Default Mission", use_container_width=True):
            load_mission_to_state(DEFAULT_MISSION.copy())
            st.rerun()
    with mm3:
        uploaded = st.file_uploader("Open Mission JSON", type=["json"], label_visibility="collapsed")
        if uploaded is not None:
            try:
                loaded = json.loads(uploaded.getvalue().decode("utf-8"))
                required = ["mission_id","mission_name","water_depth_m","vehicle","target_tag"]
                missing = [k for k in required if k not in loaded]
                if missing:
                    st.error("Mission file missing: " + ", ".join(missing))
                elif st.button("Open Uploaded Mission", use_container_width=True):
                    merged = DEFAULT_MISSION.copy()
                    merged.update(loaded)
                    merged["accepted_limits"] = {**DEFAULT_MISSION["accepted_limits"], **loaded.get("accepted_limits", {})}
                    merged["baseline"] = {**DEFAULT_MISSION["baseline"], **loaded.get("baseline", {})}
                    load_mission_to_state(merged)
                    st.rerun()
            except Exception as e:
                st.error(f"Invalid mission JSON: {e}")

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


def build_mission_report_html(mission, stage, gate_status):
    completed = []
    evidence_map = [
        "Mission scope, work reference, target, vehicle and acceptance basis loaded.",
        "Metocean conditions accepted and controlled ROV approach initiated.",
        "INS/USBL/DVL position solution established; photogrammetry target reference confirmed.",
        "DVL bottom lock and station-keeping reference accepted.",
        "Correct hot stab and target interface verified against asset context.",
        "Manipulator TCP aligned to TEP within angular, distance and clearance criteria.",
        "Hot stab insertion permitted after localization, tooling and geometric gates pass.",
        "Hydraulic pressure and flow applied; valve functional operation executed.",
        "Valve state, navigation and intervention evidence verified; tool withdrawal completed.",
        "Mission evidence accepted; work reference eligible for closure and handover.",
    ]
    for i, label in enumerate(STAGES):
        status = "COMPLETE" if (i < stage or stage >= 9) else ("IN PROGRESS" if i == stage else "PENDING")
        completed.append(f"<tr><td>{i+1:02d}</td><td>{label}</td><td>{status}</td><td>{evidence_map[i]}</td></tr>")

    gate_rows = "".join(
        f"<tr><td>{k}</td><td>{v[0]}</td></tr>" for k,v in gate_status.items()
    )

    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>MRSIF Mission Report</title>
<style>
body{{font-family:Arial,sans-serif;margin:36px;color:#183142}}
h1,h2{{color:#0b6787}} .meta{{background:#eef6f9;padding:12px;border-left:5px solid #0b9bc2}}
table{{border-collapse:collapse;width:100%;margin:14px 0;font-size:12px}}
th,td{{border:1px solid #c7d8e1;padding:7px;text-align:left;vertical-align:top}}
th{{background:#0b4968;color:white}} .note{{font-size:11px;color:#607886}}
</style></head><body>
<h1>VODIDS · MRSIF Mission Assurance Report</h1>
<div class="meta">
<b>Mission:</b> {mission.get('mission_name')}<br>
<b>Work Ref:</b> {mission.get('mission_id')}<br>
<b>Depth:</b> {mission.get('water_depth_m')} m<br>
<b>Vehicle:</b> {mission.get('vehicle')}<br>
<b>Target:</b> {mission.get('target_tag')}<br>
<b>CFIHOS Context:</b> {mission.get('cfihos_code','—')} · {mission.get('cfihos_class','—')}<br>
<b>Status:</b> MISSION ACCOMPLISHED / FINAL ACCEPTANCE PASSED
</div>

<h2>Localization Assurance</h2>
<table><tr><th>Reference</th><th>Status / Evidence</th></tr>
<tr><td>INS</td><td>{'STABLE' if st.session_state.ins_stable else 'HOLD'}</td></tr>
<tr><td>USBL</td><td>{'VALID' if st.session_state.usbl_fix_valid else 'INVALID'} · Fix age {st.session_state.usbl_age_s:.1f} s</td></tr>
<tr><td>DVL</td><td>{'BOTTOM LOCK' if st.session_state.dvl_bottom_lock else 'LOST'}</td></tr>
<tr><td>Depth + IMU</td><td>{'VALID' if (st.session_state.depth_sensor_valid and st.session_state.imu_valid) else 'HOLD'}</td></tr>
<tr><td>Photogrammetry</td><td>{'STRUCTURE MATCH CONFIRMED' if st.session_state.photo_structure_match else 'HOLD'}</td></tr>
<tr><td>CFIHOS Asset Identity</td><td>{'MATCHED' if st.session_state.cfihos_asset_match else 'HOLD'}</td></tr>
</table>

<h2>Mission Process Completion</h2>
<table><tr><th>#</th><th>Process</th><th>Status</th><th>Operational Evidence / Acceptance Basis</th></tr>
{''.join(completed)}</table>

<h2>Final Gate Record</h2>
<table><tr><th>Gate</th><th>Status</th></tr>{gate_rows}</table>

<h2>Final Intervention Data</h2>
<table>
<tr><th>Parameter</th><th>Final Value</th></tr>
<tr><td>Localization Confidence</td><td>{st.session_state.localization_pct}%</td></tr>
<tr><td>Point-Cloud Confidence</td><td>{st.session_state.pointcloud_pct}%</td></tr>
<tr><td>TCP/TEP Alignment</td><td>{st.session_state.alignment_deg:.1f}°</td></tr>
<tr><td>Manipulator Clearance</td><td>{st.session_state.clearance_mm} mm</td></tr>
<tr><td>Hydraulic Pressure</td><td>{st.session_state.hydraulic_psi} psi</td></tr>
<tr><td>Hydraulic Flow</td><td>{st.session_state.hydraulic_flow_lpm:.1f} L/min</td></tr>
<tr><td>Valve State</td><td>100% OPEN</td></tr>
</table>

<p class="note">Development demonstration only. This report does not represent OEM certification, live field telemetry, CFIHOS endorsement, OSDU endorsement, or completion of a real offshore intervention.</p>
</body></html>"""

# ============================================================
# HEADER / OPERATIONS CONSOLE
# ============================================================
st.markdown(f"""
<div class="topbar">
  <div class="brand">{logo_html()}
    <div>
      <div class="brand-title">MRSIF <span style="color:#33d1ff;">Mission Operations Console</span></div>
      <div class="brand-sub">VODIDS · governed subsea intervention · CFIHOS asset context · OSDU operational context</div>
    </div>
  </div>
  <div style="text-align:right">
    <div style="font-size:10px;color:{state_color};font-weight:800">{mission_state}</div>
    <div style="font-size:8px;color:#7890a1">SIMULATED DEMONSTRATION</div>
  </div>
</div>
""", unsafe_allow_html=True)

# Workspace navigation remains controlled by the mission workflow.
workspace_options = ["MISSION", "OPERATIONS"]
if st.session_state.report_unlocked:
    workspace_options += ["REPORT", "CLOSURE"]

if st.session_state.workspace_page not in workspace_options:
    st.session_state.workspace_page = "OPERATIONS"

page = st.radio(
    "Workspace",
    workspace_options,
    key="workspace_page",
    horizontal=True,
    label_visibility="collapsed",
)

if page == "MISSION":
    st.markdown(f"""
    <div class="mission-hero">
      <div class="hero-main"><div class="hero-label">Active Mission</div><div class="hero-value">{mission.get('mission_name')}</div></div>
      <div class="hero-item"><div class="hero-label">Work Ref</div><div class="hero-value">{mission.get('mission_id')}</div></div>
      <div class="hero-item"><div class="hero-label">Depth</div><div class="hero-value">{mission.get('water_depth_m')} m</div></div>
      <div class="hero-item"><div class="hero-label">Target</div><div class="hero-value">{mission.get('target_tag')}</div></div>
    </div>
    """, unsafe_allow_html=True)

    c1,c2,c3 = st.columns([1,1,1])
    with c1:
        st.markdown('<div class="panel"><div class="pt">Mission Definition</div>', unsafe_allow_html=True)
        for k,v in [
            ("Vehicle",mission.get("vehicle")),("Manipulator",mission.get("manipulator","—")),
            ("Asset Class",mission.get("cfihos_class","—")),("CFIHOS",mission.get("cfihos_code","—")),
            ("Interface",mission.get("interface_standard","—"))]:
            st.markdown(f'<div class="row"><span class="rk">{k}</span><span class="rv">{v}</span></div>',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="panel"><div class="pt">Acceptance Basis</div>',unsafe_allow_html=True)
        for k,v in [
            ("Localization",f'≥ {limits["localization_min_pct"]}%'),
            ("Point Cloud",f'≥ {limits["pointcloud_min_pct"]}%'),
            ("ROV/Target Error",f'≤ {limits["distance_error_max_pct"]}%'),
            ("TCP/TEP Alignment",f'≤ {limits["alignment_max_deg"]}°'),
            ("Clearance",f'≥ {limits["clearance_min_mm"]} mm')]:
            st.markdown(f'<div class="row"><span class="rk">{k}</span><span class="rv">{v}</span></div>',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="panel"><div class="pt">MRSIF Readiness</div>',unsafe_allow_html=True)
        for code,name in LAYER_NAMES:
            st.markdown(f'<div class="row"><span class="rk">{code} · {name}</span><span class="badge pass">READY</span></div>',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)

elif page == "OPERATIONS":
    # The system status is always visible above the twin.
    nav_ok = st.session_state.ins_stable and st.session_state.usbl_fix_valid and st.session_state.dvl_bottom_lock
    structure_ok = st.session_state.photo_structure_match and st.session_state.cfihos_asset_match

    st.markdown(f"""
    <div class="ops-status-strip">
      <div class="ops-status"><div class="k">Active Operation</div><div class="v">{STAGES[stage]}</div></div>
      <div class="ops-status"><div class="k">INS</div><div class="v {'ok' if st.session_state.ins_stable else 'warn'}">{'STABLE' if st.session_state.ins_stable else 'HOLD'}</div></div>
      <div class="ops-status"><div class="k">USBL</div><div class="v {'ok' if st.session_state.usbl_fix_valid else 'warn'}">{'UPDATED · '+format(st.session_state.usbl_age_s,'.1f')+' s' if st.session_state.usbl_fix_valid else 'INVALID'}</div></div>
      <div class="ops-status"><div class="k">DVL</div><div class="v {'ok' if st.session_state.dvl_bottom_lock else 'warn'}">{'BOTTOM LOCK' if st.session_state.dvl_bottom_lock else 'LOCK LOST'}</div></div>
      <div class="ops-status"><div class="k">Photogrammetry</div><div class="v {'ok' if st.session_state.photo_structure_match else 'warn'}">{'STRUCTURE CONFIRMED' if st.session_state.photo_structure_match else 'UNCONFIRMED'}</div></div>
      <div class="ops-status"><div class="k">CFIHOS Asset</div><div class="v {'ok' if st.session_state.cfihos_asset_match else 'warn'}">{'IDENTITY MATCHED' if st.session_state.cfihos_asset_match else 'MISMATCH'}</div></div>
    </div>
    """, unsafe_allow_html=True)

    # Digital Twin remains central; meaningful process completion and assurance stay at the sides.
    process_col, twin_col, assurance_col = st.columns([1.05,4.6,1.15], gap="small")

    with process_col:
        st.markdown('<div class="compact-panel"><div class="pt">Mission Process</div><div class="ps">Meaningful stage completion</div>', unsafe_allow_html=True)
        proc_html = '<div class="process-list">'
        for i,label in enumerate(STAGES):
            if i < stage:
                cls, stat = "done", "DONE"
            elif i == stage:
                cls, stat = "active", "ACTIVE"
            else:
                cls, stat = "", "PENDING"
            proc_html += f'<div class="process-step {cls}"><span class="pn">{i+1:02d}</span><span class="ptxt">{label}</span><span class="proc-status">{stat}</span></div>'
        proc_html += '</div>'
        st.markdown(proc_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="compact-panel">
          <div class="pt">Completion Evidence</div>
          <div class="compact-row"><span class="rk">Work Ref</span><span class="rv">{mission.get('mission_id')}</span></div>
          <div class="compact-row"><span class="rk">Target</span><span class="rv">{mission.get('target_tag')}</span></div>
          <div class="compact-row"><span class="rk">Vehicle</span><span class="rv">{mission.get('vehicle')}</span></div>
          <div class="compact-row"><span class="rk">CFIHOS</span><span class="rv">{mission.get('cfihos_code','—')}</span></div>
          <div class="compact-row"><span class="rk">Evidence</span><span class="badge {'pass' if stage>=8 else 'monitor'}">{'CAPTURED' if stage>=8 else 'BUILDING'}</span></div>
        </div>
        """, unsafe_allow_html=True)


    with twin_col:
        progress = stage / 9
        rov_x = 92 + progress * 300
        rov_y = 270
        valve_x, valve_y = 690, 290
        arm_factor = min(1.0,max(0.0,(stage-3)/3))
        sx, sy = rov_x+100, rov_y+15
        ex, ey = sx+44+40*arm_factor, sy+10
        wx, wy = ex+38+38*arm_factor, ey-2
        tx, ty = wx+28+38*arm_factor, wy
        if stage < 5: ty += 22
        elif not alignment_pass: ty -= 44

        stab_inserted = stage >= 6 and alignment_pass and tool_pass
        valve_pct = 100 if stage >= 7 and hydraulic_pass and stab_inserted else 0
        target_range = max(0.45, 9.0-stage*0.95)

        svg = f"""
        <div style="background:#06121c;border:1px solid #284156;border-radius:12px;padding:8px;font-family:Arial,sans-serif;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin:0 3px 6px 3px;">
            <div><b style="color:#eef7fb;font-size:13px;">Operational Digital Twin · {mission.get('mission_name')}</b>
            <span style="color:#718b9c;font-size:8px;margin-left:8px;">Engineering representation · simulated mission data</span></div>
            <span style="border:1px solid {state_color};color:{state_color};border-radius:12px;padding:4px 8px;font-size:8px;font-weight:800">{mission_state}</span>
          </div>
          <svg viewBox="0 0 960 555" width="100%" role="img" aria-label="ROV hot stab intervention and localization simulation">
            <defs>
              <linearGradient id="water3" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#123e5c"/><stop offset="62%" stop-color="#092538"/><stop offset="100%" stop-color="#051019"/></linearGradient>
              <linearGradient id="rov3" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#d4b849"/><stop offset="100%" stop-color="#987d1e"/></linearGradient>
              <pattern id="grid3" width="48" height="48" patternUnits="userSpaceOnUse"><path d="M48 0L0 0 0 48" fill="none" stroke="#2a4d62" stroke-width=".55"/></pattern>
            </defs>
            <rect width="960" height="555" rx="10" fill="url(#water3)"/><rect width="960" height="555" rx="10" fill="url(#grid3)" opacity=".42"/>

            <g font-family="Arial">
              <rect x="18" y="16" width="150" height="42" rx="7" fill="#071824" stroke="#31566e"/><text x="29" y="32" fill="#8fa6b8" font-size="8">DEPTH</text><text x="29" y="50" fill="#eef7fb" font-size="15" font-weight="700">{mission.get('water_depth_m')} m</text>
              <rect x="178" y="16" width="260" height="42" rx="7" fill="#071824" stroke="#31566e"/><text x="190" y="32" fill="#8fa6b8" font-size="8">MISSION STAGE</text><text x="190" y="50" fill="#eef7fb" font-size="13" font-weight="700">{stage+1}/10 · {STAGES[stage]}</text>
              <rect x="448" y="16" width="150" height="42" rx="7" fill="#071824" stroke="#31566e"/><text x="460" y="32" fill="#8fa6b8" font-size="8">TARGET RANGE</text><text x="460" y="50" fill="#eef7fb" font-size="15" font-weight="700">{target_range:.2f} m</text>
              <rect x="608" y="16" width="150" height="42" rx="7" fill="#071824" stroke="#31566e"/><text x="620" y="32" fill="#8fa6b8" font-size="8">TCP / TEP</text><text x="620" y="50" fill="{'#72f2a5' if alignment_pass else '#ffd079'}" font-size="15" font-weight="700">{st.session_state.alignment_deg:.1f}°</text>
              <rect x="768" y="16" width="174" height="42" rx="7" fill="#071824" stroke="#31566e"/><text x="780" y="32" fill="#8fa6b8" font-size="8">LOCALIZATION</text><text x="780" y="50" fill="#72f2a5" font-size="15" font-weight="700">{st.session_state.localization_pct}% · VALID</text>
            </g>

            <path d="M0 455 C120 430,220 470,345 446 S590 438,720 452 S855 438,960 454 L960 555 L0 555 Z" fill="#18382b"/>

            <!-- USBL update -->
            <line x1="165" y1="92" x2="{rov_x+74}" y2="{rov_y+34}" stroke="#76dbff" stroke-width="2.5" stroke-dasharray="9 6"/>
            <circle cx="165" cy="92" r="7" fill="#0a2538" stroke="#76dbff" stroke-width="2"/>
            <text x="180" y="89" fill="#9edfff" font-size="9">USBL ABSOLUTE POSITION UPDATE</text>
            <text x="180" y="103" fill="#7b96a7" font-size="8">Fix age {st.session_state.usbl_age_s:.1f} s · accepted into navigation solution</text>

            <!-- FLS localization cone -->
            <path d="M {rov_x+143} {rov_y-37} L 676 165 L 676 405 Z" fill="#4b8cff" opacity="{'.24' if st.session_state.fls_available else '.03'}"/>
            <text x="{rov_x+152}" y="{rov_y-49}" fill="#8ab3ff" font-size="9">FLS TARGET CONFIRMATION / DEGRADED-VISIBILITY SUPPORT</text>

            <!-- Valve frame and photogrammetry registered envelope -->
            <rect x="682" y="118" width="182" height="294" rx="8" fill="none" stroke="#33d1ff" stroke-width="2" stroke-dasharray="6 5"/>
            <g stroke="#a2b8c6" stroke-width="8" fill="none"><rect x="700" y="135" width="146" height="255" rx="3"/><line x1="700" y1="135" x2="730" y2="105"/><line x1="846" y1="135" x2="816" y2="105"/><line x1="730" y1="105" x2="816" y2="105"/><line x1="715" y1="215" x2="831" y2="215"/><line x1="715" y1="325" x2="831" y2="325"/></g>
            <text x="690" y="92" fill="#e4eef3" font-size="11" font-weight="700">SUBSEA VALVE / HOT-STAB PANEL</text>
            <circle cx="{valve_x}" cy="{valve_y}" r="29" fill="#122637" stroke="#ffbd4a" stroke-width="4"/><circle cx="{valve_x}" cy="{valve_y}" r="12" fill="#06111a" stroke="#ffbd4a" stroke-width="3"/>
            <text x="690" y="430" fill="#76dbff" font-size="8">PHOTOGRAMMETRY STRUCTURE REGISTRATION · CONFIRMED</text>
            <text x="690" y="444" fill="#7b96a7" font-size="8">Observed geometry ↔ CFIHOS {mission.get('cfihos_code','asset')}</text>

            <!-- ROV -->
            <g><rect x="{rov_x}" y="{rov_y-72}" width="148" height="106" rx="10" fill="url(#rov3)" stroke="#f1dd86" stroke-width="3"/><rect x="{rov_x+10}" y="{rov_y-57}" width="128" height="72" rx="4" fill="#102433" stroke="#c8d5dd" stroke-width="3"/><rect x="{rov_x+33}" y="{rov_y-94}" width="78" height="28" rx="4" fill="url(#rov3)" stroke="#f1dd86" stroke-width="2"/><circle cx="{rov_x+20}" cy="{rov_y-5}" r="16" fill="#06111a" stroke="#33d1ff" stroke-width="3"/><circle cx="{rov_x+128}" cy="{rov_y-5}" r="16" fill="#06111a" stroke="#33d1ff" stroke-width="3"/><text x="{rov_x+15}" y="{rov_y-52}" fill="#eef7fb" font-size="10" font-weight="700">{mission.get('vehicle')}</text></g>

            <!-- DVL beams -->
            <g stroke="#72f2a5" stroke-width="2" opacity=".78"><line x1="{rov_x+48}" y1="{rov_y+32}" x2="{rov_x+8}" y2="446"/><line x1="{rov_x+65}" y1="{rov_y+32}" x2="{rov_x+48}" y2="452"/><line x1="{rov_x+83}" y1="{rov_y+32}" x2="{rov_x+103}" y2="452"/><line x1="{rov_x+100}" y1="{rov_y+32}" x2="{rov_x+142}" y2="446"/></g>
            <text x="{rov_x+20}" y="474" fill="#8fe7b0" font-size="8">DVL BOTTOM LOCK · SETTLED</text>

            <!-- INS vector -->
            <line x1="{rov_x+74}" y1="{rov_y+34}" x2="{rov_x+142}" y2="{rov_y+34}" stroke="#ffcf75" stroke-width="3"/><polygon points="{rov_x+142},{rov_y+34} {rov_x+130},{rov_y+28} {rov_x+130},{rov_y+40}" fill="#ffcf75"/><text x="{rov_x+78}" y="{rov_y+55}" fill="#ffcf75" font-size="8">INS / IMU STABLE</text>

            <!-- Manipulator and hot stab -->
            <g fill="none" stroke="#72f2a5" stroke-linecap="round"><line x1="{sx}" y1="{sy}" x2="{ex}" y2="{ey}" stroke-width="14"/><line x1="{ex}" y1="{ey}" x2="{wx}" y2="{wy}" stroke-width="12"/><line x1="{wx}" y1="{wy}" x2="{tx}" y2="{ty}" stroke-width="9"/></g>
            <g fill="#0c1c28" stroke="#72f2a5" stroke-width="3"><circle cx="{sx}" cy="{sy}" r="9"/><circle cx="{ex}" cy="{ey}" r="9"/><circle cx="{wx}" cy="{wy}" r="8"/></g>
            <rect x="{tx-3}" y="{ty-7}" width="38" height="14" rx="5" fill="{'#72f2a5' if stab_inserted else '#ffbd4a'}" stroke="#fff" stroke-width="1.5"/><text x="{tx-12}" y="{ty-18}" fill="#72f2a5" font-size="9">TCP</text>
            <line x1="{tx+34}" y1="{ty}" x2="{valve_x-10}" y2="{valve_y}" stroke="{'#72f2a5' if stab_inserted else '#ffbd4a'}" stroke-width="4" stroke-dasharray="9 5"/>

            <!-- Bottom telemetry -->
            <rect x="18" y="493" width="924" height="45" rx="8" fill="#071824" stroke="#31566e"/>
            <g font-family="Arial"><text x="32" y="510" fill="#8fa6b8" font-size="8">HYDRAULIC</text><text x="32" y="528" fill="#eef7fb" font-size="13" font-weight="700">{st.session_state.hydraulic_psi if stage>=7 else 0} psi</text>
            <text x="185" y="510" fill="#8fa6b8" font-size="8">FLOW</text><text x="185" y="528" fill="#eef7fb" font-size="13" font-weight="700">{st.session_state.hydraulic_flow_lpm if stage>=7 else 0:.1f} L/min</text>
            <text x="315" y="510" fill="#8fa6b8" font-size="8">VALVE</text><text x="315" y="528" fill="{'#72f2a5' if valve_pct==100 else '#eef7fb'}" font-size="13" font-weight="700">{valve_pct}% OPEN</text>
            <text x="440" y="510" fill="#8fa6b8" font-size="8">POINT CLOUD</text><text x="440" y="528" fill="#eef7fb" font-size="13" font-weight="700">{st.session_state.pointcloud_pct}%</text>
            <text x="590" y="510" fill="#8fa6b8" font-size="8">CLEARANCE</text><text x="590" y="528" fill="#eef7fb" font-size="13" font-weight="700">{st.session_state.clearance_mm} mm</text>
            <text x="725" y="510" fill="#8fa6b8" font-size="8">ASSET</text><text x="725" y="528" fill="#72f2a5" font-size="13" font-weight="700">{mission.get('target_tag')}</text></g>
          </svg>
        </div>
        """
        components.html(svg,height=690,scrolling=False)

        with st.expander("Engineering / Demonstration Parameters · Active Mission Inputs", expanded=False):
            st.caption("These are simulation inputs supporting the Digital Twin and stage-gating logic.")
            ep1,ep2,ep3,ep4 = st.columns(4)
            with ep1:
                st.session_state.current_kts = st.number_input("Seafloor current (kts)",0.0,4.0,float(st.session_state.current_kts),0.1,key="op_current")
                st.session_state.visibility_m = st.number_input("Visibility (m)",0.0,20.0,float(st.session_state.visibility_m),0.5,key="op_visibility")
            with ep2:
                st.session_state.localization_pct = st.number_input("Localization confidence (%)",0,100,int(st.session_state.localization_pct),1,key="op_loc")
                st.session_state.pointcloud_pct = st.number_input("Point-cloud confidence (%)",0,100,int(st.session_state.pointcloud_pct),1,key="op_pc")
                st.session_state.usbl_age_s = st.number_input("USBL fix age (s)",0.0,60.0,float(st.session_state.usbl_age_s),0.1,key="op_usbl_age")
            with ep3:
                st.session_state.distance_error_pct = st.number_input("ROV-target error (%)",0.0,20.0,float(st.session_state.distance_error_pct),0.1,key="op_dist")
                st.session_state.clearance_mm = st.number_input("Manipulator clearance (mm)",0,500,int(st.session_state.clearance_mm),5,key="op_clear")
                st.session_state.alignment_deg = st.number_input("TCP/TEP alignment error (°)",0.0,20.0,float(st.session_state.alignment_deg),0.1,key="op_align")
            with ep4:
                st.session_state.hydraulic_psi = st.number_input("Hydraulic pressure (psi)",0,5000,int(st.session_state.hydraulic_psi),100,key="op_hyd")
                st.session_state.hydraulic_flow_lpm = st.number_input("Hydraulic flow (L/min)",0.0,30.0,float(st.session_state.hydraulic_flow_lpm),0.5,key="op_flow")
                st.session_state.tool_match = st.checkbox("Correct hot stab / interface",st.session_state.tool_match,key="op_tool")
                st.session_state.dvl_lock = st.checkbox("DVL navigation valid",st.session_state.dvl_lock,key="op_dvl_nav")
                st.session_state.fls_available = st.checkbox("FLS available",st.session_state.fls_available,key="op_fls")
                st.session_state.pilot_confirmed = st.checkbox("Pilot risk review confirmed",st.session_state.pilot_confirmed,key="op_pilot")
                st.session_state.ins_stable = st.checkbox("INS stable",st.session_state.ins_stable,key="op_ins")
                st.session_state.usbl_fix_valid = st.checkbox("USBL fix valid",st.session_state.usbl_fix_valid,key="op_usbl")
                st.session_state.dvl_bottom_lock = st.checkbox("DVL bottom lock settled",st.session_state.dvl_bottom_lock,key="op_dvl")
                st.session_state.photo_structure_match = st.checkbox("Photogrammetry structure match",st.session_state.photo_structure_match,key="op_photo")
                st.session_state.cfihos_asset_match = st.checkbox("CFIHOS asset identity matched",st.session_state.cfihos_asset_match,key="op_cfihos")


    with assurance_col:
        st.markdown('<div class="compact-panel"><div class="pt">Live Assurance</div><div class="ps">Active-stage gates only</div>',unsafe_allow_html=True)
        for label in ["Metocean","Point Cloud","Localization","Distance","Tool Match","Clearance","Alignment","Visibility/FLS","Pilot Review","Hydraulic"]:
            s,c = gate_status[label]
            st.markdown(f'<div class="compact-row"><span class="rk">{label}</span><span class="badge {c}">{s}</span></div>',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)

        st.markdown("<div style='height:6px'></div>",unsafe_allow_html=True)
        if stage_clear:
            st.markdown(f'<div class="decision passbox"><div class="bigstate">STAGE ACCEPTED</div>{STAGES[stage]}<br><br><b>Next:</b> Advance one stage.</div>',unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="decision"><div class="bigstate">HOLD</div><b>Resolve:</b> {", ".join(active_holds)}</div>',unsafe_allow_html=True)


elif page == "REPORT":
    if not st.session_state.report_unlocked:
        st.warning("Final report is locked. Complete the mission in OPERATIONS and press Final Acceptance & Generate Report.")
    else:
        completed_count = len(STAGES)
        total_count = len(STAGES)
        mission_complete_flag = True

        st.markdown(f"""
        <div class="mission-hero">
          <div class="hero-main"><div class="hero-label">VODIDS MRSIF Final Mission Report</div><div class="hero-value">{mission.get('mission_name')}</div></div>
          <div class="hero-item"><div class="hero-label">Work Ref</div><div class="hero-value">{mission.get('mission_id')}</div></div>
          <div class="hero-item"><div class="hero-label">Target</div><div class="hero-value">{mission.get('target_tag')}</div></div>
          <div class="hero-item"><div class="hero-label">Report Status</div><div class="hero-value" style="color:#72f2a5">FINAL ACCEPTED</div></div>
        </div>
        """, unsafe_allow_html=True)

        r1, r2 = st.columns([1.15, 2.85], gap="small")
        with r1:
            st.markdown('<div class="report-shell"><h3>Mission Summary</h3>', unsafe_allow_html=True)
            for k,v in [
                ("Mission", mission.get("mission_name")),
                ("Depth", f"{mission.get('water_depth_m')} m"),
                ("Vehicle", mission.get("vehicle")),
                ("Manipulator", mission.get("manipulator","—")),
                ("Target", mission.get("target_tag")),
                ("Asset Class", mission.get("cfihos_class","—")),
                ("CFIHOS Code", mission.get("cfihos_code","—")),
                ("Interface", mission.get("interface_standard","—")),
                ("Completion", f"{completed_count}/{total_count} processes"),
            ]:
                st.markdown(f'<div class="row"><span class="rk">{k}</span><span class="rv">{v}</span></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("<div style='height:7px'></div>", unsafe_allow_html=True)
            st.markdown('<div class="report-shell"><h3>Final Localization Basis</h3>', unsafe_allow_html=True)
            for k,v in [
                ("INS","STABLE"),
                ("USBL",f"VALID · {st.session_state.usbl_age_s:.1f} s"),
                ("DVL","BOTTOM LOCK"),
                ("Depth + IMU","VALID"),
                ("Photogrammetry","STRUCTURE MATCHED"),
                ("CFIHOS Identity","MATCHED"),
            ]:
                st.markdown(f'<div class="row"><span class="rk">{k}</span><span class="rv">{v}</span></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with r2:
            evidence_map = [
                "Mission profile and acceptance basis loaded.",
                "Metocean gate accepted and controlled approach completed.",
                "USBL/INS/DVL solution and photogrammetry target reference established.",
                "DVL bottom lock and station-keeping reference accepted.",
                "Correct hot stab / interface validated against target asset context.",
                "TCP aligned to TEP within angular and clearance limits.",
                "Hot stab insertion completed after all active gates passed.",
                "Hydraulic pressure/flow applied; valve function completed.",
                "Valve state, navigation, tooling and evidence verified; tool withdrawn.",
                "Final evidence accepted; mission eligible for closure and handover.",
            ]
            rows = ""
            for i,label in enumerate(STAGES):
                rows += f"<tr><td>{i+1:02d}</td><td>{label}</td><td style='color:#72f2a5;font-weight:700'>COMPLETE</td><td>{evidence_map[i]}</td></tr>"
            st.markdown(f"""
            <div class="report-shell">
              <h3>Process Completion Record</h3>
              <table class="report-table">
                <thead><tr><th>#</th><th>Process</th><th>Status</th><th>Operational Evidence</th></tr></thead>
                <tbody>{rows}</tbody>
              </table>
            </div>
            """, unsafe_allow_html=True)

        report_html = build_mission_report_html(mission, stage, gate_status)
        d1,d2,d3 = st.columns([1.2,1.2,2.6])
        with d1:
            st.download_button(
                "Download Final Mission Report",
                data=report_html.encode("utf-8"),
                file_name=f"{mission.get('mission_id')}_MRSIF_Final_Report.html",
                mime="text/html",
                use_container_width=True,
            )
        with d2:
            if st.button("Return to Operations", use_container_width=True):
                st.session_state.workspace_page = "OPERATIONS"
                st.rerun()
        with d3:
            st.markdown("""
            <div class="restart-note">
            To replay or start the demonstration again, return to <b>OPERATIONS</b>, open <b>Mission Manager</b> at the top,
            and click <b>Reload Default Mission</b>. This resets the mission, report lock and process state.
            </div>
            """, unsafe_allow_html=True)

elif page == "CLOSURE":
    if not st.session_state.report_unlocked:
        st.warning("Closure is locked until Final Acceptance is completed.")
    else:
        st.markdown("""
        <div class="report-shell">
          <h3>Mission Closure & Data Handover</h3>
          <p>The intervention has passed final acceptance. Mission evidence can now be packaged for client review,
          lifecycle records and data handover. The demonstration keeps the closure step separate from live execution
          so mission completion is never inferred merely from vehicle movement.</p>
        </div>
        """, unsafe_allow_html=True)
        c1,c2,c3 = st.columns(3)
        with c1:
            st.metric("Localization Confidence",f"{st.session_state.localization_pct}%")
            st.metric("Point-Cloud Confidence",f"{st.session_state.pointcloud_pct}%")
        with c2:
            st.metric("Final Alignment",f"{st.session_state.alignment_deg:.1f}°")
            st.metric("Final Clearance",f"{st.session_state.clearance_mm} mm")
        with c3:
            st.metric("Valve State","100% OPEN")
            st.metric("Asset",mission.get("target_tag"))

        st.markdown("""
        <div class="restart-note">
        To return to the demonstration, choose <b>OPERATIONS</b>. To start again from Mission Setup,
        use <b>Mission Manager → Reload Default Mission</b>.
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# OPERATIONS COMMAND BAR
# ============================================================
if page == "OPERATIONS":
    if stage < 9:
        cmd1,cmd2,cmd3 = st.columns([1,1.35,2.3])
        with cmd1:
            if st.button("Reset Mission", use_container_width=True):
                load_mission_to_state(st.session_state.mission)
                st.rerun()
        with cmd2:
            if st.button("Advance Mission →", use_container_width=True, disabled=not stage_clear):
                st.session_state.stage = min(9, stage+1)
                if st.session_state.stage >= 9:
                    st.session_state.mission_complete = True
                st.rerun()
        with cmd3:
            if stage_clear:
                st.info(f"{STAGES[stage]} accepted · review the Digital Twin and active gates, then advance one process.")
            else:
                st.warning(f"Advance inhibited · resolve: {', '.join(active_holds)}")
    else:
        fa1,fa2,fa3 = st.columns([1.1,1.8,2.2])
        with fa1:
            if st.button("Reload Mission", use_container_width=True):
                load_mission_to_state(st.session_state.mission)
                st.rerun()
        with fa2:
            if st.button("Final Acceptance & Generate Report", use_container_width=True):
                if stage_clear:
                    st.session_state.report_unlocked = True
                    st.session_state.workspace_page = "REPORT"
                    st.rerun()
                else:
                    st.warning(f"Final acceptance HOLD: {', '.join(active_holds)}")
        with fa3:
            st.success("Mission processes completed. Perform Final Acceptance to unlock the VODIDS mission report and closure package.")

ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
st.markdown(f'<div style="margin-top:9px;border-top:1px solid #1e3141;padding-top:7px;color:#6f8798;font-size:8px;display:flex;justify-content:space-between"><span>VODIDS · MRSIF v7.5 Final Share Demo</span><span>Simulation only · {ts}</span></div>', unsafe_allow_html=True)
