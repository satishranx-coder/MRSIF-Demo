
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
from datetime import datetime
import base64

# ============================================================
# MRSIF LIVE MISSION ASSURANCE
# Generic Marine Robotics & Survey Risk / Mission Intelligence
# Default demonstration: Vikra ROVITO - Jetty Structural Inspection
# ============================================================

st.set_page_config(
    page_title="MRSIF Live Mission Assurance",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------
# Constants / source-backed ROVITO profile
# -----------------------------
ROVITO = {
    "name": "Vikra ROVITO",
    "depth_rating_m": 100,
    "rated_speed_kn": 2.0,
    "max_speed_kn": 4.0,
    "thrusters": 6,
    "tether_m": 150,
    "cameras": "2 × 2MP 1080P + offline 4K camera",
    "lights": "4 × 1500 lm",
    "payload_kg": 1.5,
    "weight_kg": 9.5,
    "communication": "Tethered",
}

APPLICATIONS = {
    "Jetty / Pile Structural Inspection": {
        "asset": "Jetty Pile J-14",
        "default_depth": 8.0,
        "default_visibility": 0.8,
        "default_current": 1.2,
        "default_marine_growth": "Heavy",
        "default_position_required": True,
        "default_fls": True,
        "default_usbl": True,
        "default_spare_fls": False,
        "mission_goal": "100% visual structural coverage of designated pile / brace zones.",
    },
    "Desalination Intake / Outfall Inspection": {
        "asset": "Seawater Intake / Outfall Structure",
        "default_depth": 14.0,
        "default_visibility": 0.5,
        "default_current": 1.5,
        "default_marine_growth": "Moderate",
        "default_position_required": True,
        "default_fls": True,
        "default_usbl": True,
        "default_spare_fls": False,
        "mission_goal": "Inspect intake/outfall structure and obstruction condition with visual/FLS evidence.",
    },
    "Pipeline Internal Inspection": {
        "asset": "Internal Pipeline / Culvert",
        "default_depth": 6.0,
        "default_visibility": 0.3,
        "default_current": 0.4,
        "default_marine_growth": "Low",
        "default_position_required": False,
        "default_fls": True,
        "default_usbl": False,
        "default_spare_fls": False,
        "mission_goal": "Internal visual condition assessment with safe recovery path and inspection coverage.",
    },
    "Tank / Confined Water Inspection": {
        "asset": "Submerged Tank / Chamber",
        "default_depth": 5.0,
        "default_visibility": 1.0,
        "default_current": 0.1,
        "default_marine_growth": "Low",
        "default_position_required": False,
        "default_fls": False,
        "default_usbl": False,
        "default_spare_fls": False,
        "mission_goal": "Inspect submerged internal surfaces and document defects / obstructions.",
    },
}

RISK_LABELS = [
    "Vehicle Depth Capability",
    "Tether / Required Range",
    "Visibility",
    "Current Exposure",
    "Structure Collision",
    "Tether Entanglement",
    "Visual Inspection",
    "FLS Dependency",
    "Positioning Confidence",
    "Recovery Path",
    "Video Evidence",
]

# -----------------------------
# Session state
# -----------------------------
if "application" not in st.session_state:
    st.session_state.application = "Jetty / Pile Structural Inspection"

def apply_defaults(app_name):
    app = APPLICATIONS[app_name]
    st.session_state.water_depth = app["default_depth"]
    st.session_state.visibility = app["default_visibility"]
    st.session_state.current = app["default_current"]
    st.session_state.marine_growth = app["default_marine_growth"]
    st.session_state.position_required = app["default_position_required"]
    st.session_state.fls_available = app["default_fls"]
    st.session_state.usbl_available = app["default_usbl"]
    st.session_state.spare_fls = app["default_spare_fls"]
    st.session_state.video_recording = True
    st.session_state.tether_margin_m = 25
    st.session_state.recovery_path_clear = True
    st.session_state.failure = "None"
    st.session_state.coverage = 0
    st.session_state.mission_started = False

for k,v in {
    "water_depth": 8.0,
    "visibility": 0.8,
    "current": 1.2,
    "marine_growth": "Heavy",
    "position_required": True,
    "fls_available": True,
    "usbl_available": True,
    "spare_fls": False,
    "video_recording": True,
    "tether_margin_m": 25,
    "recovery_path_clear": True,
    "failure": "None",
    "coverage": 0,
    "mission_started": False,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# -----------------------------
# Helpers
# -----------------------------
def image_data_uri(path):
    p = Path(path)
    if not p.exists():
        return ""
    mime = "image/png" if p.suffix.lower() == ".png" else "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()

ROV_IMAGE_PATH = "/mnt/data/8ef6d004-8afa-4188-b74c-abd68b5741d1.png"
ROV_IMG = image_data_uri(ROV_IMAGE_PATH)

def status_badge(status):
    cls = {
        "PASS": "pass",
        "NORMAL": "pass",
        "DEGRADED": "deg",
        "MONITOR": "mon",
        "HOLD": "hold",
        "UNBYPASSABLE": "hard",
        "N/A": "na",
    }.get(status, "na")
    return f'<span class="badge {cls}">{status}</span>'

def compute_risks():
    app = st.session_state.application
    depth_ok = st.session_state.water_depth <= ROVITO["depth_rating_m"]

    # required tether estimate: water depth + operational reach + contingency
    required_tether = st.session_state.water_depth + 25
    tether_ok = required_tether <= ROVITO["tether_m"]

    vis = st.session_state.visibility
    current = st.session_state.current
    fls = st.session_state.fls_available
    usbl = st.session_state.usbl_available
    pos_req = st.session_state.position_required
    recovery = st.session_state.recovery_path_clear
    video = st.session_state.video_recording

    risks = {}

    risks["Vehicle Depth Capability"] = "PASS" if depth_ok else "UNBYPASSABLE"
    risks["Tether / Required Range"] = "PASS" if tether_ok else "UNBYPASSABLE"

    if vis >= 3.0:
        risks["Visibility"] = "PASS"
    elif vis >= 1.0:
        risks["Visibility"] = "DEGRADED"
    else:
        risks["Visibility"] = "HOLD" if not fls else "DEGRADED"

    # generic conservative current logic for demonstration only
    if current <= 0.8:
        risks["Current Exposure"] = "PASS"
    elif current <= 1.5:
        risks["Current Exposure"] = "MONITOR"
    else:
        risks["Current Exposure"] = "HOLD"

    if app == "Jetty / Pile Structural Inspection":
        risks["Structure Collision"] = "MONITOR" if current <= 1.0 else "DEGRADED"
        risks["Tether Entanglement"] = "DEGRADED"
    elif app == "Pipeline Internal Inspection":
        risks["Structure Collision"] = "DEGRADED"
        risks["Tether Entanglement"] = "HOLD" if not recovery else "DEGRADED"
    elif app == "Desalination Intake / Outfall Inspection":
        risks["Structure Collision"] = "MONITOR"
        risks["Tether Entanglement"] = "DEGRADED"
    else:
        risks["Structure Collision"] = "MONITOR"
        risks["Tether Entanglement"] = "MONITOR"

    if video:
        risks["Visual Inspection"] = "PASS" if vis >= 1.0 else ("DEGRADED" if fls else "HOLD")
        risks["Video Evidence"] = "PASS"
    else:
        risks["Visual Inspection"] = "HOLD"
        risks["Video Evidence"] = "UNBYPASSABLE"

    if app in ["Pipeline Internal Inspection", "Desalination Intake / Outfall Inspection"]:
        risks["FLS Dependency"] = "UNBYPASSABLE" if vis < 1.0 and not fls else ("MONITOR" if fls else "N/A")
    else:
        risks["FLS Dependency"] = "UNBYPASSABLE" if vis < 0.8 and not fls else ("MONITOR" if fls else "N/A")

    if pos_req:
        risks["Positioning Confidence"] = "PASS" if usbl else "UNBYPASSABLE"
    else:
        risks["Positioning Confidence"] = "PASS" if usbl else "N/A"

    risks["Recovery Path"] = "PASS" if recovery else "UNBYPASSABLE"

    # Injected failures override
    failure = st.session_state.failure
    if failure == "FLS Failure":
        risks["FLS Dependency"] = "UNBYPASSABLE" if vis < 1.0 else "DEGRADED"
    elif failure == "USBL Failure":
        risks["Positioning Confidence"] = "UNBYPASSABLE" if pos_req else "DEGRADED"
    elif failure == "Video Recorder Failure":
        risks["Video Evidence"] = "UNBYPASSABLE"
        risks["Visual Inspection"] = "HOLD"
    elif failure == "Tether Snag":
        risks["Tether Entanglement"] = "UNBYPASSABLE"
        risks["Recovery Path"] = "HOLD"
    elif failure == "Camera Failure":
        risks["Visual Inspection"] = "UNBYPASSABLE"
        risks["Video Evidence"] = "HOLD"
    elif failure == "High Current Event":
        risks["Current Exposure"] = "UNBYPASSABLE"

    return risks, required_tether

def downtime_index(risks):
    weights = {
        "PASS": 0,
        "NORMAL": 0,
        "N/A": 0,
        "MONITOR": 8,
        "DEGRADED": 14,
        "HOLD": 22,
        "UNBYPASSABLE": 30,
    }
    raw = sum(weights.get(v, 0) for v in risks.values())
    # normalize by a reasonable upper bound
    score = min(100, round(raw / (len(risks) * 30) * 100))

    # Adjust if spare mitigates FLS dependency
    if st.session_state.failure == "FLS Failure" and st.session_state.spare_fls:
        score = max(0, score - 18)

    if score <= 20:
        band = "LOW"
    elif score <= 40:
        band = "MANAGEABLE"
    elif score <= 60:
        band = "ELEVATED"
    elif score <= 80:
        band = "HIGH"
    else:
        band = "MISSION CRITICAL"
    return score, band

def mission_state(risks):
    if any(v == "UNBYPASSABLE" for v in risks.values()):
        return "HOLD — UNBYPASSABLE FACTOR"
    if any(v == "HOLD" for v in risks.values()):
        return "HOLD — VALIDATION REQUIRED"
    if any(v in ["DEGRADED", "MONITOR"] for v in risks.values()):
        return "MISSION CONTINUE — DEGRADED / MONITOR"
    return "READY / NOMINAL"

# -----------------------------
# CSS
# -----------------------------
st.markdown("""
<style>
:root{
--bg:#071019;--panel:#0d1824;--panel2:#111f2e;--border:#24384a;
--text:#edf7fb;--muted:#8ba3b4;--cyan:#33d1ff;--green:#2bd576;
--amber:#ffbd4a;--red:#ff5f63;--purple:#a98cff;
}
.stApp{background:radial-gradient(circle at top,#102033 0%,#071019 50%,#050b11 100%);color:var(--text);}
.block-container{max-width:1900px;padding:.55rem 1rem 1rem 1rem;}
#MainMenu,footer,header{visibility:hidden;}
.topbar{display:flex;justify-content:space-between;align-items:center;background:#0b1722;border:1px solid var(--border);border-radius:12px;padding:10px 12px;margin-bottom:7px}
.title{font-size:21px;font-weight:900}.sub{font-size:9px;color:var(--muted);margin-top:2px}
.state{font-size:10px;font-weight:900;border:1px solid #31566e;border-radius:12px;padding:6px 9px}
.panel{background:#0d1824;border:1px solid var(--border);border-radius:11px;padding:9px}
.panel-title{font-size:11px;font-weight:900;color:#eef7fb;margin-bottom:5px}
.panel-sub{font-size:8px;color:#7891a2;margin-bottom:7px}
.row{display:flex;justify-content:space-between;gap:5px;padding:5px 0;border-bottom:1px solid rgba(36,56,74,.5);font-size:8.5px}
.row:last-child{border-bottom:none}.k{color:#8da6b6}.v{color:#eef7fb;font-weight:800;text-align:right}
.badge{font-size:7px;font-weight:900;border:1px solid;border-radius:9px;padding:2px 5px}
.pass{color:#72f2a5;border-color:#2bd576}.mon{color:#76dbff;border-color:#33d1ff}
.deg{color:#ffd079;border-color:#ffbd4a}.hold{color:#ffb06b;border-color:#ff7a3d}
.hard{color:#ff8a8e;border-color:#ff5f63;background:rgba(255,95,99,.07)}.na{color:#8196a4;border-color:#50616d}
.metric-grid{display:grid;grid-template-columns:repeat(6,1fr);gap:5px;margin-bottom:7px}
.metric{background:#0b1722;border:1px solid #29465c;border-radius:8px;padding:7px}
.mk{font-size:7px;color:#7892a3;text-transform:uppercase}.mv{font-size:13px;font-weight:900;color:#fff;margin-top:2px}.mn{font-size:7px;color:#6d8493;margin-top:2px}
.dti{background:#091621;border:1px solid #29465c;border-radius:10px;padding:9px;margin-top:7px}
.dti-bar{height:13px;border-radius:8px;background:#142533;overflow:hidden;border:1px solid #29465c}
.dti-fill{height:100%;background:linear-gradient(90deg,#2bd576,#ffbd4a,#ff5f63)}
.process{display:flex;gap:4px;flex-wrap:wrap;margin-top:5px}
.proc{border:1px solid #2b4456;border-radius:7px;padding:4px 6px;font-size:7.5px;color:#7892a3}
.proc.active{color:#dff8ff;border-color:#33d1ff;background:rgba(51,209,255,.07)}
div[data-testid="stSelectbox"] label,
div[data-testid="stSlider"] label,
div[data-testid="stCheckbox"] label,
div[data-testid="stNumberInput"] label,
div[data-testid="stRadio"] label {color:#eef7fb!important;font-weight:700!important}
.stButton>button{background:#123048!important;color:#eef7fb!important;border:1px solid #2f6681!important;border-radius:8px!important;font-weight:800!important}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Controls
# -----------------------------
st.markdown("""
<div class="topbar">
  <div>
    <div class="title">MRSIF · Live Marine Robotics Mission Assurance</div>
    <div class="sub">Generic framework · mission context → robot/survey capability → risk simulation → unbypassable factors → downtime intelligence → evidence</div>
  </div>
  <div class="state">DEMONSTRATION MODE · REPRESENTATIVE INPUTS</div>
</div>
""", unsafe_allow_html=True)

c1,c2,c3,c4 = st.columns([1.6,1,1,1])
with c1:
    new_app = st.selectbox("Application", list(APPLICATIONS.keys()), index=list(APPLICATIONS.keys()).index(st.session_state.application))
    if new_app != st.session_state.application:
        st.session_state.application = new_app
        apply_defaults(new_app)
        st.rerun()
with c2:
    st.session_state.water_depth = st.number_input("Water depth (m)", 0.0, 120.0, float(st.session_state.water_depth), 0.5)
with c3:
    st.session_state.visibility = st.number_input("Visibility (m)", 0.0, 20.0, float(st.session_state.visibility), 0.1)
with c4:
    st.session_state.current = st.number_input("Current (kn)", 0.0, 4.0, float(st.session_state.current), 0.1)

with st.expander("Mission Environment / Configuration Inputs", expanded=False):
    e1,e2,e3,e4 = st.columns(4)
    with e1:
        st.session_state.marine_growth = st.selectbox("Marine growth", ["Low","Moderate","Heavy"], index=["Low","Moderate","Heavy"].index(st.session_state.marine_growth))
        st.session_state.tether_margin_m = st.number_input("Tether contingency margin (m)", 0, 100, int(st.session_state.tether_margin_m), 5)
    with e2:
        st.session_state.position_required = st.checkbox("Georeferenced positioning required", st.session_state.position_required)
        st.session_state.usbl_available = st.checkbox("USBL / underwater positioning available", st.session_state.usbl_available)
    with e3:
        st.session_state.fls_available = st.checkbox("FLS available", st.session_state.fls_available)
        st.session_state.spare_fls = st.checkbox("Spare FLS onboard", st.session_state.spare_fls)
    with e4:
        st.session_state.video_recording = st.checkbox("Digital video recording healthy", st.session_state.video_recording)
        st.session_state.recovery_path_clear = st.checkbox("Recovery path clear", st.session_state.recovery_path_clear)

risks, required_tether = compute_risks()
mdi, mdi_band = downtime_index(risks)
mstate = mission_state(risks)

# -----------------------------
# Main mission cards
# -----------------------------
app = APPLICATIONS[st.session_state.application]

st.markdown(f"""
<div class="metric-grid">
  <div class="metric"><div class="mk">Mission</div><div class="mv">{st.session_state.application}</div><div class="mn">{app['asset']}</div></div>
  <div class="metric"><div class="mk">Vehicle</div><div class="mv">{ROVITO['name']}</div><div class="mn">100 m depth · 6 thrusters</div></div>
  <div class="metric"><div class="mk">Required Tether</div><div class="mv">{required_tether:.0f} m</div><div class="mn">ROVITO available: {ROVITO['tether_m']} m</div></div>
  <div class="metric"><div class="mk">Visibility</div><div class="mv">{st.session_state.visibility:.1f} m</div><div class="mn">{'FLS support active' if st.session_state.fls_available else 'No FLS support'}</div></div>
  <div class="metric"><div class="mk">Positioning</div><div class="mv">{'REQUIRED' if st.session_state.position_required else 'OPTIONAL'}</div><div class="mn">{'USBL available' if st.session_state.usbl_available else 'USBL unavailable'}</div></div>
  <div class="metric"><div class="mk">MRSIF State</div><div class="mv">{mstate}</div><div class="mn">Contextual mission decision</div></div>
</div>
""", unsafe_allow_html=True)

left, center, right = st.columns([1.15,3.3,1.25], gap="small")

# -----------------------------
# Left panel: mission / capability
# -----------------------------
with left:
    st.markdown('<div class="panel"><div class="panel-title">Mission Context</div><div class="panel-sub">MRSIF learns the actual operating problem first</div>', unsafe_allow_html=True)
    for k,v in [
        ("Application", st.session_state.application),
        ("Asset", app["asset"]),
        ("Goal", app["mission_goal"]),
        ("Depth", f"{st.session_state.water_depth:.1f} m"),
        ("Current", f"{st.session_state.current:.1f} kn"),
        ("Visibility", f"{st.session_state.visibility:.1f} m"),
        ("Marine Growth", st.session_state.marine_growth),
    ]:
        st.markdown(f'<div class="row"><span class="k">{k}</span><span class="v">{v}</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="panel"><div class="panel-title">ROVITO Capability Profile</div><div class="panel-sub">Source-backed Vikra vehicle capability</div>', unsafe_allow_html=True)
    for k,v in [
        ("Depth Rating", f"{ROVITO['depth_rating_m']} m"),
        ("Rated / Max Speed", f"{ROVITO['rated_speed_kn']} / {ROVITO['max_speed_kn']} kn"),
        ("Thrusters", ROVITO["thrusters"]),
        ("Tether", f"{ROVITO['tether_m']} m"),
        ("Payload", f"{ROVITO['payload_kg']} kg"),
        ("Cameras", ROVITO["cameras"]),
        ("Lights", ROVITO["lights"]),
        ("Communication", ROVITO["communication"]),
    ]:
        st.markdown(f'<div class="row"><span class="k">{k}</span><span class="v">{v}</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Center: visual mission scene
# -----------------------------
with center:
    progress = st.session_state.coverage / 100.0
    # Position depends on application
    if st.session_state.application == "Jetty / Pile Structural Inspection":
        scene_title = "Jetty Structural Inspection"
        asset_svg = """
        <g stroke="#9fb5c2" stroke-width="10" fill="none">
          <line x1="675" y1="95" x2="675" y2="430"/>
          <line x1="760" y1="95" x2="760" y2="430"/>
          <line x1="675" y1="150" x2="760" y2="150"/>
          <line x1="675" y1="265" x2="760" y2="265"/>
        </g>
        <text x="650" y="75" fill="#eef7fb" font-size="13" font-weight="700">JETTY PILE / BRACE</text>
        """
        rov_x = 125 + progress*350
        rov_y = 260
    elif st.session_state.application == "Desalination Intake / Outfall Inspection":
        scene_title = "Desalination Intake / Outfall Inspection"
        asset_svg = """
        <rect x="670" y="175" width="150" height="180" rx="8" fill="#102333" stroke="#9fb5c2" stroke-width="5"/>
        <g stroke="#6c8999" stroke-width="5">
          <line x1="690" y1="195" x2="690" y2="335"/><line x1="720" y1="195" x2="720" y2="335"/>
          <line x1="750" y1="195" x2="750" y2="335"/><line x1="780" y1="195" x2="780" y2="335"/>
        </g>
        <text x="655" y="150" fill="#eef7fb" font-size="13" font-weight="700">INTAKE / OUTFALL STRUCTURE</text>
        """
        rov_x = 115 + progress*360
        rov_y = 275
    elif st.session_state.application == "Pipeline Internal Inspection":
        scene_title = "Pipeline Internal Inspection"
        asset_svg = """
        <rect x="90" y="145" width="735" height="245" rx="120" fill="#0a1721" stroke="#6b8796" stroke-width="8"/>
        <line x1="110" y1="268" x2="805" y2="268" stroke="#304a5a" stroke-width="2" stroke-dasharray="8 8"/>
        <text x="625" y="128" fill="#eef7fb" font-size="13" font-weight="700">PIPELINE / CULVERT INTERNAL</text>
        """
        rov_x = 145 + progress*430
        rov_y = 275
    else:
        scene_title = "Tank / Confined Water Inspection"
        asset_svg = """
        <rect x="610" y="105" width="220" height="300" rx="18" fill="#0b1822" stroke="#6b8796" stroke-width="7"/>
        <text x="620" y="85" fill="#eef7fb" font-size="13" font-weight="700">TANK / CHAMBER</text>
        """
        rov_x = 130 + progress*330
        rov_y = 270

    fls_opacity = 0.23 if st.session_state.fls_available and st.session_state.failure != "FLS Failure" else 0.02
    usbl_color = "#72f2a5" if st.session_state.usbl_available and st.session_state.failure != "USBL Failure" else "#ff5f63"

    svg = f"""
    <div style="background:#06121c;border:1px solid #284156;border-radius:12px;padding:8px;font-family:Arial,sans-serif;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px;">
        <div><b style="color:#eef7fb;font-size:13px;">Operational Mission Model · {scene_title}</b>
        <span style="color:#718b9c;font-size:8px;margin-left:8px;">Representative MRSIF demonstration using ROVITO capability</span></div>
        <span style="color:#72f2a5;font-size:9px;font-weight:800">{st.session_state.coverage}% COVERAGE</span>
      </div>
      <svg viewBox="0 0 900 520" width="100%">
        <defs>
          <linearGradient id="sea" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#123b58"/><stop offset="65%" stop-color="#092436"/><stop offset="100%" stop-color="#061019"/>
          </linearGradient>
          <pattern id="grid" width="42" height="42" patternUnits="userSpaceOnUse">
            <path d="M42 0L0 0 0 42" fill="none" stroke="#294a5c" stroke-width=".55"/>
          </pattern>
        </defs>
        <rect width="900" height="520" rx="10" fill="url(#sea)"/><rect width="900" height="520" rx="10" fill="url(#grid)" opacity=".4"/>

        <rect x="18" y="15" width="160" height="42" rx="7" fill="#071824" stroke="#31566e"/>
        <text x="30" y="31" fill="#8fa6b8" font-size="8">DEPTH</text>
        <text x="30" y="50" fill="#eef7fb" font-size="15" font-weight="700">{st.session_state.water_depth:.1f} m</text>

        <rect x="188" y="15" width="160" height="42" rx="7" fill="#071824" stroke="#31566e"/>
        <text x="200" y="31" fill="#8fa6b8" font-size="8">CURRENT</text>
        <text x="200" y="50" fill="#eef7fb" font-size="15" font-weight="700">{st.session_state.current:.1f} kn</text>

        <rect x="358" y="15" width="160" height="42" rx="7" fill="#071824" stroke="#31566e"/>
        <text x="370" y="31" fill="#8fa6b8" font-size="8">VISIBILITY</text>
        <text x="370" y="50" fill="#eef7fb" font-size="15" font-weight="700">{st.session_state.visibility:.1f} m</text>

        <rect x="528" y="15" width="160" height="42" rx="7" fill="#071824" stroke="#31566e"/>
        <text x="540" y="31" fill="#8fa6b8" font-size="8">POSITIONING</text>
        <text x="540" y="50" fill="{usbl_color}" font-size="13" font-weight="700">{'VALID' if st.session_state.usbl_available and st.session_state.failure != 'USBL Failure' else 'UNAVAILABLE'}</text>

        <rect x="698" y="15" width="184" height="42" rx="7" fill="#071824" stroke="#31566e"/>
        <text x="710" y="31" fill="#8fa6b8" font-size="8">FAILURE INJECTION</text>
        <text x="710" y="50" fill="{'#ff8a8e' if st.session_state.failure != 'None' else '#72f2a5'}" font-size="12" font-weight="700">{st.session_state.failure}</text>

        <path d="M0 445 C120 425,235 458,345 440 S590 430,720 445 S840 432,900 445 L900 520 L0 520 Z" fill="#17382b"/>

        {asset_svg}

        <!-- USBL conceptual position update -->
        <line x1="105" y1="90" x2="{rov_x+75}" y2="{rov_y+25}" stroke="{usbl_color}" stroke-width="2" stroke-dasharray="8 6"/>
        <circle cx="105" cy="90" r="7" fill="#0a2538" stroke="{usbl_color}" stroke-width="2"/>
        <text x="120" y="88" fill="{usbl_color}" font-size="8">SURVEY POSITION REFERENCE</text>

        <!-- FLS cone -->
        <path d="M {rov_x+140} {rov_y-20} L 650 165 L 650 375 Z" fill="#4b8cff" opacity="{fls_opacity}"/>
        <text x="{rov_x+145}" y="{rov_y-35}" fill="#8ab3ff" font-size="8">FLS FIELD / TARGET SUPPORT</text>

        <!-- simplified ROVITO with embedded actual photo -->
        <rect x="{rov_x}" y="{rov_y-70}" width="155" height="120" rx="12" fill="#0b1621" stroke="#33d1ff" stroke-width="2"/>
        <image href="{ROV_IMG}" x="{rov_x+8}" y="{rov_y-62}" width="139" height="96" preserveAspectRatio="xMidYMid meet"/>
        <text x="{rov_x+20}" y="{rov_y+43}" fill="#eef7fb" font-size="10" font-weight="700">VIKRA ROVITO</text>

        <!-- tether -->
        <path d="M {rov_x} {rov_y+5} C {rov_x-90} {rov_y+20}, 120 360, 35 380" fill="none" stroke="#ffd36e" stroke-width="4"/>
        <text x="45" y="402" fill="#ffd36e" font-size="8">TETHER / RECOVERY PATH</text>

        <!-- coverage indicator -->
        <rect x="18" y="474" width="864" height="28" rx="7" fill="#071824" stroke="#31566e"/>
        <rect x="20" y="476" width="{8.60*st.session_state.coverage}" height="24" rx="6" fill="#2bd576" opacity=".8"/>
        <text x="32" y="493" fill="#eef7fb" font-size="9" font-weight="700">INSPECTION COVERAGE · {st.session_state.coverage}%</text>
      </svg>
    </div>
    """
    components.html(svg, height=660, scrolling=False)

    # Mission simulation controls directly under model
    b1,b2,b3,b4 = st.columns([1,1.2,1,1.7])
    with b1:
        if st.button("Start / Reset Mission", use_container_width=True):
            st.session_state.coverage = 0
            st.session_state.failure = "None"
            st.session_state.mission_started = True
            st.rerun()
    with b2:
        if st.button("Advance Inspection +10%", use_container_width=True, disabled=any(v in ["HOLD","UNBYPASSABLE"] for v in risks.values())):
            st.session_state.coverage = min(100, st.session_state.coverage + 10)
            st.session_state.mission_started = True
            st.rerun()
    with b3:
        if st.button("Clear Failure", use_container_width=True):
            st.session_state.failure = "None"
            st.rerun()
    with b4:
        st.session_state.failure = st.selectbox(
            "Inject Failure",
            ["None","FLS Failure","USBL Failure","Video Recorder Failure","Tether Snag","Camera Failure","High Current Event"],
            index=["None","FLS Failure","USBL Failure","Video Recorder Failure","Tether Snag","Camera Failure","High Current Event"].index(st.session_state.failure)
        )

# -----------------------------
# Right panel: live risk / downtime
# -----------------------------
with right:
    st.markdown('<div class="panel"><div class="panel-title">MRSIF Live Risk Intelligence</div><div class="panel-sub">Mission-specific, not a generic checklist</div>', unsafe_allow_html=True)
    for label in RISK_LABELS:
        st.markdown(f'<div class="row"><span class="k">{label}</span>{status_badge(risks[label])}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    ubfs = [k for k,v in risks.items() if v == "UNBYPASSABLE"]
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="panel"><div class="panel-title">Unbypassable Factors</div>', unsafe_allow_html=True)
    if ubfs:
        for item in ubfs:
            st.markdown(f'<div class="row"><span class="k">{item}</span><span class="badge hard">UBF</span></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="row"><span class="k">No active unbypassable factor</span><span class="badge pass">CLEAR</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="dti">
      <div class="panel-title">MRSIF Downtime Index</div>
      <div style="display:flex;justify-content:space-between;align-items:end">
        <div style="font-size:27px;font-weight:900;color:#eef7fb">{mdi}</div>
        <div style="font-size:9px;font-weight:900;color:{'#72f2a5' if mdi<=40 else '#ffd079' if mdi<=60 else '#ff8a8e'}">{mdi_band}</div>
      </div>
      <div class="dti-bar"><div class="dti-fill" style="width:{mdi}%"></div></div>
      <div style="font-size:7.5px;color:#718a9c;margin-top:5px">Illustrative MRSIF exposure score based on active mission dependencies, degradation, HOLD conditions and unbypassable factors.</div>
    </div>
    """, unsafe_allow_html=True)

    # Failure specific downtime explanation
    if st.session_state.failure == "FLS Failure":
        if st.session_state.spare_fls:
            st.info("FLS failure detected. Spare onboard reduces expected recovery exposure. Recover → replace → function test → revalidate → resume.")
        else:
            st.warning("FLS failure detected with no spare onboard. If FLS is unbypassable for the active mission, replacement mobilization can dominate NPT.")
    elif st.session_state.failure == "USBL Failure":
        if st.session_state.position_required:
            st.warning("USBL is required for this mission's georeferenced deliverable. Positioning loss becomes unbypassable until restored.")
        else:
            st.info("USBL loss is degraded/bypassable because absolute positioning is not required by the current mission.")
    elif st.session_state.failure == "Tether Snag":
        st.error("Tether snag affects both execution and recovery. MRSIF places the mission on HOLD until a safe recovery path is restored.")
    elif st.session_state.failure == "Video Recorder Failure":
        st.error("Inspection evidence cannot be completed without required recording. Mission is held until evidence capture is restored.")
    elif st.session_state.failure == "Camera Failure":
        st.error("Primary visual inspection capability lost. Mission cannot claim completion without a valid inspection source.")
    elif st.session_state.failure == "High Current Event":
        st.error("Environmental condition exceeds the demonstration operating envelope. Recover / hold until conditions return within limits.")

# -----------------------------
# Generic MRSIF context / standards
# -----------------------------
st.markdown("---")
s1,s2,s3 = st.columns([1.25,1.25,2.5])
with s1:
    st.markdown('<div class="panel"><div class="panel-title">Active Context Layers</div>', unsafe_allow_html=True)
    for name, status in [
        ("Client Requirements","ACTIVE"),
        ("ROV OEM / Vehicle Limits","ACTIVE"),
        ("HSE / Operational Rules","ACTIVE"),
        ("CFIHOS Asset Context","OPTIONAL / APPLICATION-DEPENDENT"),
        ("OSDU Data Context","OPTIONAL / APPLICATION-DEPENDENT"),
        ("Survey / Positioning Requirements","ACTIVE" if st.session_state.position_required else "AS REQUIRED"),
    ]:
        st.markdown(f'<div class="row"><span class="k">{name}</span><span class="v">{status}</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with s2:
    st.markdown('<div class="panel"><div class="panel-title">MRSIF Principle</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:9px;color:#a9becb;line-height:1.5">
    MRSIF is generic. Standards, asset models, survey requirements and OEM limits are blended only when the mission requires them.
    The framework does not invent sensor or tool telemetry. It evaluates available evidence, dependencies, bypass options, recovery exposure and mission completion.
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with s3:
    st.markdown('<div class="panel"><div class="panel-title">Mission Intelligence Loop</div>', unsafe_allow_html=True)
    process = ["Mission Requirement","Asset / Environment","Robot + Survey Capability","Risk Simulation","Unbypassable Factors","Downtime Exposure","Execution","Evidence","Lessons Learned"]
    html = '<div class="process">'
    for i,p in enumerate(process):
        cls = "active" if i <= 6 else ""
        html += f'<div class="proc {cls}">{i+1:02d} · {p}</div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.caption("MRSIF Live Mission Assurance · Demonstration logic only. Environmental thresholds and downtime scoring are representative and must be replaced by project-approved engineering limits, OEM data, client requirements and validated field experience for production use.")
