import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import hashlib
import json
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# ====================================================================
# 1. UPGRADED NESTED COMPLIANCE SCHEMAS (MRSIF ADVANCED DATA CORE)
# ====================================================================
class MrsifUpdateHeader(BaseModel):
    thread_id: str = "TH-2026-9941A"
    timestamp_utc: str
    submitting_company_id: str = "VIKRA_OCEAN_TECH"

class AssetIdentityBlock(BaseModel):
    vehicle_global_id: str  # Hash of Manufacturer + Model + Serial
    imca_unique_id: str
    cfihos_equipment_class: str
    power_configuration_type: str

class NavSensor(BaseModel):
    sensor_id: str
    sensor_type: str
    cfihos_tag: str
    last_calibration_date: Optional[str] = None

class EmbeddedSubsystems(BaseModel):
    telemetry_primary_link: str = "FIBER_OPTIC"
    measured_latency_ms: float
    default_nav_sensors: List[NavSensor]
    imca_pilot_competency: str  # e.g., "IMCA-A-007 (900 hrs)"

class LiveInterventionPayload(BaseModel):
    mrsif_header: MrsifUpdateHeader
    asset_identity: AssetIdentityBlock
    subsystems: EmbeddedSubsystems
    functional_tag: str
    runtime_telemetry_stream: dict = Field(default_factory=dict)

# ====================================================================
# 2. PERMANENT REFERENCE LIBRARY & METADATA DICTIONARIES
# ====================================================================
CFIHOS_REFERENCE_LIBRARY = {
    "CFIHOS-10000284": {
        "class_name": "Actuated Valve Assembly",
        "properties": {
            "CFIHOS-30000561": {"name": "Maximum Operating Torque", "unit": "Nm", "default": 150.0},
            "CFIHOS-30000894": {"name": "Hydraulic Pressure Rating", "unit": "PSI", "default": 10000.0}
        }
    },
    "CFIHOS-10000115": {
        "class_name": "Subsea Manifold System",
        "properties": {
            "CFIHOS-30000144": {"name": "Header Nominal Diameter", "unit": "inch", "default": 8.0},
            "CFIHOS-30000912": {"name": "Branch Outlets Count", "unit": "Count", "default": 4}
        }
    }
}

ACTIVE_FIELD_TAGS = {
    "50-XV-0401": {"class_code": "CFIHOS-10000284", "serial": "EQ-XT04-VLV-01", "x": 50.0, "y": 0.0, "z": 500.0},
    "50-MF-010A": {"class_code": "CFIHOS-10000115", "serial": "EQ-GABON-MNF-0A", "x": 15.0, "y": -15.0, "z": 505.0}
}

# ====================================================================
# 3. INTERFACE INITIALIZATION & LAYOUT
# ====================================================================
st.set_page_config(
    page_title="MRSIF | Connected CFIHOS Engine",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        .reportview-container { background: #0b0f19; }
        .stMarkdown h1, h2, h3 { color: #f1f5f9 !important; font-family: 'Courier New', Courier, monospace; }
        div[data-testid="stMetricValue"] { font-size: 32px !important; font-family: 'Courier New', Courier, monospace; font-weight: bold; }
        .stTabs [aria-selected="true"] { background-color: #0284c7 !important; color: white !important; }
        
        .metric-card {
            background-color: #1e293b;
            padding: 15px;
            border-radius: 6px;
            border-left: 5px solid #06b6d4;
            margin-bottom: 10px;
        }
        .metric-card.error { border-left: 5px solid #ef4444; }
        .metric-card.success { border-left: 5px solid #10b981; }
    </style>
""", unsafe_allow_html=True)

# Main Screen Corporate Row: Logo on left, single designated text string on right
banner_bg = st.container()
with banner_bg:
    col_logo, col_text = st.columns([1, 3])
    with col_logo:
        st.markdown('<div style="background-color: #1e293b; padding: 10px 10px 10px 20px; border-radius: 8px 0px 0px 8px; height: 160px; display: flex; align-items: center; justify-content: center;">', unsafe_allow_html=True)
        try:
            st.image("./VODIDS.png", width=140)
        except Exception as e:
            st.caption("📷 Left Logo Engine Active")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_text:
        st.markdown("""
            <div style="background-color: #1e293b; padding: 20px; border-radius: 0px 8px 8px 0px; height: 160px; display: flex; align-items: center; vertical-align: middle;">
                <h2 style="margin: 0; font-family: 'Courier New', monospace; color: #f1f5f9; letter-spacing: 1px;">
                    VODIDS - MRSIFramework Version 1.2
                </h2>
            </div>
        """, unsafe_allow_html=True)

with col_logo:
    st.markdown('<div style="margin-top: -160px; position: relative; z-index: 999;"></div>', unsafe_allow_html=True)

st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

for key in ["f1", "f2", "f3", "d1", "d2", "d3"]:
    if key not in st.session_state:
        st.session_state[key] = False

# ====================================================================
# 4. CONTROL PANEL & LIVE SENSOR INPUTS (LEFT SIDEBAR ONLY WORD DISPLAY)
# ====================================================================
st.sidebar.markdown(
    """
    <div style="text-align: center; padding-bottom: 10px;">
        <h2 style="margin: 0; font-family: 'Courier New', monospace; color: #06b6d4; letter-spacing: 2px;">VODIDS Ver 1.2</h2>
    </div>
    """, 
    unsafe_allow_html=True
)
st.sidebar.markdown("---")
st.sidebar.markdown("### 🎛️ TARGET NODE INGESTION")
selected_tag = st.sidebar.selectbox("Active Field Equipment Tag", list(ACTIVE_FIELD_TAGS.keys()))

st.sidebar.markdown("---")
st.sidebar.markdown("**🌊 ENVIRONMENTAL ASSESSMENTS**")
metocean_current = st.sidebar.slider("Live Seafloor Current Velocity (kts)", 0.5, 3.0, 1.2, step=0.1)

st.sidebar.markdown("**🦾 INTERVENTION SENSOR STREAMS**")
measured_torque = st.sidebar.slider("Manipulator Delivered Torque (Nm)", 0.0, 200.0, 142.5, step=0.5)
measured_pressure = st.sidebar.slider("Hot Stab Line Hydrostatic (PSI)", 0, 5000, 3150, step=50)
measured_latency = st.sidebar.slider("Telemetry Link Latency (ms)", 5.0, 120.0, 22.4, step=0.1)
auto_dvl_lock = st.sidebar.checkbox("Engage DVL Seafloor Tracking", value=True)
rov_altitude = st.sidebar.slider("Vehicle Altitude Off-Seabed (m)", 1.0, 10.0, 4.0, step=0.5)

# ====================================================================
# 5. DYNAMIC HIERARCHICAL PYDANTIC OBJECT CONSTRUCTION
# ====================================================================
tag_meta = ACTIVE_FIELD_TAGS[selected_tag]
class_code = tag_meta["class_code"]
class_definition = CFIHOS_REFERENCE_LIBRARY[class_code]

header_block = MrsifUpdateHeader(
    timestamp_utc=datetime.utcnow().isoformat() + "Z"
)

vehicle_string = f"VOT-WORKCLASS-ROV-{tag_meta['serial']}"
vehicle_hash = hashlib.sha256(vehicle_string.encode('utf-8')).hexdigest()[:16].upper()
identity_block = AssetIdentityBlock(
    vehicle_global_id=f"VVID-{vehicle_hash}",
    imca_unique_id="IMCA-ROV-WCLASS-9942",
    cfihos_equipment_class=class_code,
    power_configuration_type="3000V_AC_SURFACE_UMBILICAL"
)

nav_sensors = [
    NavSensor(sensor_id="SN-DVL-8821", sensor_type="Doppler Velocity Log", cfihos_tag="50-NX-601", last_calibration_date="2026-03-12"),
    NavSensor(sensor_id="SN-INS-0441", sensor_type="Inertial Navigation System", cfihos_tag="50-NX-602", last_calibration_date="2026-05-19")
]

subsystems_block = EmbeddedSubsystems(
    measured_latency_ms=measured_latency,
    default_nav_sensors=nav_sensors,
    imca_pilot_competency="IMCA-Class-1-Senior (1250 Hrs)"
)

live_telemetry_map = {
    "CFIHOS-30000561": measured_torque,    
    "CFIHOS-30000894": measured_pressure,  
}

runtime_payload = LiveInterventionPayload(
    mrsif_header=header_block,
    asset_identity=identity_block,
    subsystems=subsystems_block,
    functional_tag=selected_tag,
    runtime_telemetry_stream=live_telemetry_map
)

function_test_completed = st.session_state.f1 and st.session_state.f2 and st.session_state.f3
deck_test_completed = st.session_state.d1 and st.session_state.d2 and st.session_state.d3
metocean_passed = metocean_current <= 1.5
is_safe = metocean_passed and deck_test_completed and auto_dvl_lock and function_test_completed

# ====================================================================
# 6. APPLICATION DISPLAY SURFACE
# ====================================================================
st.markdown("### 📊 Live System Verification Status Ledger")
status_col1, status_col2, status_col3 = st.columns(3)

with status_col1:
    card_style = "metric-card success" if metocean_passed else "metric-card error"
    st.markdown(f"""
        <div class="{card_style}">
            <h5 style='margin:0; color:#94a3b8;'>Metocean Threshold</h5>
            <h2 style='margin:5px 0; color:#f1f5f9;'>{metocean_current} kts</h2>
            <p style='margin:0; font-size:12px; color:#94a3b8;'>Limit: 1.5 kts Max Drag</p>
        </div>
    """, unsafe_allow_html=True)

with status_col2:
    torque_limit = class_definition["properties"].get("CFIHOS-30000561", {}).get("default", 150.0)
    torque_passed = measured_torque <= torque_limit if class_code == "CFIHOS-10000284" else True
    card_style = "metric-card success" if torque_passed else "metric-card error"
    st.markdown(f"""
        <div class="{card_style}">
            <h5 style='margin:0; color:#94a3b8;'>Intervention Delivery Torque</h5>
            <h2 style='margin:5px 0; color:#f1f5f9;'>{measured_torque if class_code == "CFIHOS-10000284" else 'N/A'} Nm</h2>
            <p style='margin:0; font-size:12px; color:#94a3b8;'>CFIHOS Limit: {torque_limit} Nm</p>
        </div>
    """, unsafe_allow_html=True)

with status_col3:
    card_style = "metric-card success" if is_safe else "metric-card error"
    status_text = "EXECUTION PERMITTED" if is_safe else "SAFETY SYSTEM LOCKED"
    st.markdown(f"""
        <div class="{card_style}">
            <h5 style='margin:0; color:#94a3b8;'>Framework Integrity Gate</h5>
            <h2 style='margin:5px 0; color:#f1f5f9;'>{status_text}</h2>
            <p style='margin:0; font-size:12px; color:#94a3b8;'>All Pre-requisites & Checks</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

step_tabs = st.tabs([
    "📂 1. Hierarchical Class Mapping", 
    "🔬 2. Subsea Contractor Attestation", 
    "🏗️ 3. Physical Readiness Gates", 
    "🌐 4. Live Spatial Twin Vector", 
    "📊 5. Unified Nested Handover Package"
])

with step_tabs[0]:
    st.markdown("### 📋 Runtime Hierarchical Schema Parsing Loop")
    col_info, col_json = st.columns([1, 1])
    with col_info:
        st.markdown("#### Mapped Identity Parameters")
        st.markdown(f"* **Target Tag Assignment:** `{runtime_payload.functional_tag}`")
        st.markdown(f"* **Resolved Equipment Class:** `{runtime_payload.asset_identity.cfihos_equipment_class} ({class_definition['class_name']})`")
        st.markdown(f"* **Global Vehicle Verification ID:** `{runtime_payload.asset_identity.vehicle_global_id}`")
        st.markdown(f"* **IMCA Registry Link:** `{runtime_payload.asset_identity.imca_unique_id}`")
        
        st.markdown("#### System Link Telemetry")
        st.markdown(f"* **Primary Control Tether:** `{runtime_payload.subsystems.telemetry_primary_link}`")
        st.markdown(f"* **Runtime Ping Latency:** `{runtime_payload.subsystems.measured_latency_ms} ms`")
        st.markdown(f"* **Pilot Competency Profile:** `{runtime_payload.subsystems.imca_pilot_competency}`")

        st.markdown("#### Active Telemetry Registries")
        for prop_id, prop_data in class_definition["properties"].items():
            live_value = live_telemetry_map.get(prop_id, prop_data["default"])
            st.markdown(f"* `{prop_id}` **{prop_data['name']}:** `{live_value} {prop_data['unit']}`")
    with col_json:
        st.markdown("#### Live Pydantic Nested Object Payload")
        st.json(runtime_payload.model_dump())

with step_tabs[1]:
    st.markdown("### 🔬 Mission Method Verification Logs")
    st.checkbox("Verify Work Class ROV telemetry and communication paths", key="f1")
    st.checkbox("Confirm 7-Function Manipulator joint and torque calibrations match ISO 13628-8 profiles", key="f2")
    st.checkbox("Perform dry pressure testing on Dual Port Hot Stab system (Rated to 10,000 PSI)", key="f3")
    if function_test_completed: st.success("✅ PRE-MOBILIZATION TESTING CLEARED")

with step_tabs[2]:
    st.markdown("### 🏗️ Rigging & Mobilization Compliance Gates")
    if not function_test_completed:
        st.error("🔒 LOCKOUT: Complete Tab 2 Contractor Attestation before running mobilization deck telemetry routines.")
    else:
        st.checkbox("Run physical deck functional test on Dual Port Hot Stab manifold valves", key="d1")
        st.checkbox("Confirm hydraulic compensator oil levels are fully topped off", key="d2")
        st.checkbox("Verify ground fault monitoring systems (GFI) display clear green loops on power up", key="d3")
        if is_safe: st.success("🚀 DEPLOYMENT COMPLIANCE CLEARANCE APPLIED")

with step_tabs[3]:
    st.markdown(f"### 🌐 Real-Time Spatial Grid Alignment Target: {runtime_payload.functional_tag}")
    X_floor = np.linspace(0, 100, 25)
    Y_floor = np.linspace(-30, 30, 25)
    X, Y = np.meshgrid(X_floor, Y_floor)
    Z = 500.0 + (np.sin(X / 15.0) * np.cos(Y / 10.0) * 1.5)

    fig = go.Figure()
    fig.add_trace(go.Surface(x=X, y=Y, z=Z, colorscale='Turbid', opacity=0.35, showscale=False))
    
    for tag, d in ACTIVE_FIELD_TAGS.items():
        m_color = "#10b981" if is_safe and tag == selected_tag else "#ef4444" if tag == selected_tag else "#64748b"
        fig.add_trace(go.Scatter3d(
            x=[d["x"]], y=[d["y"]], z=[d["z"]], mode="markers+text", name=f"Tag: {tag}",
            text=[f"{tag}\n{CFIHOS_REFERENCE_LIBRARY[d['class_code']]['class_name']}"], textposition="top center",
            marker=dict(size=14, color=m_color, line=dict(color='#ffffff', width=1))
        ))

    fig.update_layout(
        margin=dict(l=0, r=0, b=0, t=0), height=500,
        scene=dict(
            xaxis=dict(title="UTM East (m)", backgroundcolor="#0b0f19", gridcolor="#1e293b", showbackground=True),
            yaxis=dict(title="UTM North (m)", backgroundcolor="#0b0f19", gridcolor="#1e293b", showbackground=True),
            zaxis=dict(title="Depth Profile (m)", autorange="reversed", backgroundcolor="#0b0f19", gridcolor="#1e293b", showbackground=True),
            camera=dict(eye=dict(x=1.2, y=1.2, z=0.8))
        ),
        paper_bgcolor="#0b0f19", plot_bgcolor="#0b0f19",
        legend=dict(font=dict(color="#94a3b8"))
    )
    st.plotly_chart(fig, use_container_width=True)

with step_tabs[4]:
    st.markdown("### 📊 Consolidated Hierarchical Outgestion Package (CFIHOS/OSDU Format)")
    if not is_safe:
        st.warning("⚠️ System Hold: Compliance signatures and outgestion packages are locked until gate constraints are satisfied.")
    else:
        st.success("🏁 EXPORT STREAM STABILIZED: NESTED MODEL COMPLETELY DOCUMENTED")
        st.json({
            "handover_format_version": "CFIHOS_V1.5 // OSDU_R3_COMPLIANT",
            "compiled_payload": runtime_payload.model_dump()
        })
