import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import hashlib
import json
from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from enum import Enum

# ====================================================================
# 1. ENUMS & MRSIF v3.0 CORE ENGINE SCHEMAS
# ====================================================================

class DeploymentStatus(str, Enum):
    APPROVED = "PASSED"
    DENIED = "FAILED"
    AUDIT_PENDING = "AUDIT_CLEARANCE_PENDING"

class ToolSpecs(BaseModel):
    """Subsea Vehicle Tool Specs (Layer 3 OEM Intelligence)."""
    tool_name: str
    rated_load_lbs: float  # e.g., 114,000 lbs (IOGP 334 baseline)
    interface_standard: str  # e.g., "API 17H"
    max_hydraulic_pressure_psi: float

class AsInstalledAssetConditions(BaseModel):
    """As-Installed Subsea Asset Conditions."""
    asset_name: str
    required_load_lbs: float  # e.g., 35,000 lbs
    interface_standard: str  # e.g., "API 17H"
    env_pressure_psi: float

class WorkScopeTelemetry(BaseModel):
    """Parses and validates $WORK_SCOPE_DATA real-time string structure."""
    type_of_vehicle: str = Field(..., description="Verified against IMCA class limits")
    type_of_tooling: str = Field(..., description="Cross-referenced against ISO 13628-8 interfaces")
    type_of_sensor: str = Field(..., description="Mapped to IOGP SSDM V2 requirements")
    work_scope_id: str = Field(..., description="Tied to the unique Work Ref No.")
    location_coord: str = Field(..., description="Precise CFIHOS asset tag layout")
    depth_range_meters: float = Field(..., description="Checked against hydrostatic pressure ratings")
    supervisor_id: str = Field(..., description="Logging personnel competency")
    date_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MRSIFExecutionEngine(BaseModel):
    work_ref_no: str
    vehicle_id: str
    owner_id: str
    last_audit_date: datetime
    is_audit_cleared: bool = False
    
    # Life-Saving Rules (Layer 0)
    hse_controls_bypassed: bool = False
    
    # Assets & Tools
    tool_specs: ToolSpecs
    asset_conditions: AsInstalledAssetConditions
    telemetry: Optional[WorkScopeTelemetry] = None

    @model_validator(mode="after")
    def verify_6month_audit(self) -> "MRSIFExecutionEngine":
        """Mandatory Audit Verification Gate."""
        now = datetime.now(timezone.utc)
        audit_dt = self.last_audit_date
        if audit_dt.tzinfo is None:
            audit_dt = audit_dt.replace(tzinfo=timezone.utc)
            
        audit_age_days = (now - audit_dt).days
        
        # Enforce 6-Month (180 Days) Mandatory Audit Window
        if audit_age_days > 180 or not self.is_audit_cleared:
            raise ValueError(
                f"[SECURITY LOCK] 6-Month Audit Document expired or missing for Vehicle {self.vehicle_id}. "
                f"$WORK_SCOPE_DATA rejected. Mobilization logic gate remains LOCKED."
            )
        return self

    def evaluate_pre_mobilization_gate(self) -> Dict[str, Any]:
        """Layer 3 OEM Tool Intelligence & IOGP Alert 334 Logic Check."""
        if self.hse_controls_bypassed:
            return {
                "status": DeploymentStatus.DENIED,
                "reason": "CRITICAL: Bypassed HSE Controls detected. Immediate mobilization deny.",
                "action": "MOBILIZATION DENIED ASHORE"
            }

        if self.tool_specs.interface_standard != self.asset_conditions.interface_standard:
            return {
                "status": DeploymentStatus.DENIED,
                "reason": f"Interface Mismatch: Tool ({self.tool_specs.interface_standard}) vs Asset ({self.asset_conditions.interface_standard})",
                "action": "MOBILIZATION DENIED ASHORE (Prevented NPT)"
            }

        if self.tool_specs.rated_load_lbs < self.asset_conditions.required_load_lbs:
            return {
                "status": DeploymentStatus.DENIED,
                "reason": f"IOGP 334 Spec Mismatch: Tool Rated Load ({self.tool_specs.rated_load_lbs} lbs) < Required Load ({self.asset_conditions.required_load_lbs} lbs)",
                "action": "MOBILIZATION DENIED ASHORE (Prevented NPT)"
            }

        if self.tool_specs.max_hydraulic_pressure_psi < self.asset_conditions.env_pressure_psi:
            return {
                "status": DeploymentStatus.DENIED,
                "reason": f"Pressure Rating Deficit: Tool Rating ({self.tool_specs.max_hydraulic_pressure_psi} PSI) < Env Pressure ({self.asset_conditions.env_pressure_psi} PSI)",
                "action": "MOBILIZATION DENIED ASHORE"
            }

        return {
            "status": DeploymentStatus.APPROVED,
            "reason": "All deterministic checks passed (Layer 0 HSE, Layer 3 OEM Tool Match, 6-Month Audit).",
            "action": "PROCEEDS TO VERIFIED DEPLOYMENT"
        }

    def sync_to_fieldtwin(self, execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generates FieldTwin GET/POST payload structure."""
        return {
            "work_ref_no": self.work_ref_no,
            "vehicle_id": self.vehicle_id,
            "deployment_status": execution_result["status"].value,
            "system_message": execution_result["reason"],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

# ====================================================================
# 2. NESTED COMPLIANCE SCHEMAS
# ====================================================================
class MrsifUpdateHeader(BaseModel):
    thread_id: str = "TH-2026-9941A"
    timestamp_utc: str
    submitting_company_id: str = "VIKRA_OCEAN_TECH"

class AssetIdentityBlock(BaseModel):
    vehicle_global_id: str
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
    imca_pilot_competency: str

class LiveInterventionPayload(BaseModel):
    mrsif_header: MrsifUpdateHeader
    asset_identity: AssetIdentityBlock
    subsystems: EmbeddedSubsystems
    functional_tag: str
    runtime_telemetry_stream: dict = Field(default_factory=dict)

# ====================================================================
# 3. REFERENCE DICTIONARIES
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

EASTING_ANCHOR = 350400.0   
NORTHING_ANCHOR = 2940200.0 

ACTIVE_FIELD_TAGS = {
    "50-XV-0401": {"class_code": "CFIHOS-10000284", "serial": "EQ-XT04-VLV-01", "x": EASTING_ANCHOR + 50.0, "y": NORTHING_ANCHOR + 0.0, "z": 508.5},
    "50-MF-010A": {"class_code": "CFIHOS-10000115", "serial": "EQ-GABON-MNF-0A", "x": EASTING_ANCHOR + 25.0, "y": NORTHING_ANCHOR - 15.0, "z": 515.2}
}

# ====================================================================
# 4. INTERFACE INITIALIZATION & REFINED PRESENTATION CSS
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
        .sidebar-brand-capsule {
            background-color: #1e293b !important;
            padding: 12px;
            border-radius: 6px;
            text-align: center;
            border: 1px solid #334155;
            margin-top: 10px;
            margin-bottom: 10px;
        }
        .sidebar-brand-capsule span {
            color: #f8fafc !important;
            font-family: 'Courier New', Courier, monospace !important;
            font-size: 18px !important;
            font-weight: bold !important;
            letter-spacing: 1px;
        }
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
        .metric-card h5, .metric-card h2, .metric-card p {
            color: #ffffff !important;
            opacity: 1.0 !important;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div style="background-color: #1e293b; padding: 25px 20px; border-radius: 8px; border-left: 6px solid #06b6d4; margin-bottom: 25px; text-align: center;">
        <h2 style="margin: 0; font-family: 'Courier New', monospace; color: #f1f5f9; letter-spacing: 1px;">
            VODIDS - MRSIFramework Version 3.0 Engine Integrated
        </h2>
    </div>
""", unsafe_allow_html=True)

for key in ["f1", "f2", "f3", "d1", "d2", "d3"]:
    if key not in st.session_state:
        st.session_state[key] = False

# ====================================================================
# 5. CONTROL PANEL & SIDEBAR LAYOUT
# ====================================================================
try:
    st.sidebar.image("./VODIDS.png", use_container_width=True)
except Exception:
    pass

st.sidebar.markdown(
    """
    <div class="sidebar-brand-capsule">
        <span>VODIDS Ver 3.0 Engine</span>
    </div>
    """, 
    unsafe_allow_html=True
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎛️ TARGET NODE INGESTION")
selected_tag = st.sidebar.selectbox("Active Field Equipment Tag", list(ACTIVE_FIELD_TAGS.keys()))

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ MRSIF LOGIC GATE CONTROLS")
tool_rated_load = st.sidebar.number_input("Tool Rated Load (lbs) [IOGP 334]", value=114000.0, step=5000.0)
asset_required_load = st.sidebar.number_input("Asset Required Load (lbs)", value=35000.0, step=5000.0)
tool_interface = st.sidebar.selectbox("Tool Interface Standard", ["API 17H", "API 17D", "ISO 13628-8"])
asset_interface = st.sidebar.selectbox("Asset Interface Standard", ["API 17H", "API 17D", "ISO 13628-8"])

audit_cleared = st.sidebar.checkbox("6-Month Audit Document Cleared", value=True)
last_audit_date_input = st.sidebar.date_input("Last Audit Date", datetime(2026, 3, 1))
hse_bypassed = st.sidebar.checkbox("Layer 0: HSE Controls Bypassed", value=False)

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
# 6. DYNAMIC PYDANTIC & MRSIF ENGINE EXECUTION
# ====================================================================
tag_meta = ACTIVE_FIELD_TAGS[selected_tag]
class_code = tag_meta["class_code"]
class_definition = CFIHOS_REFERENCE_LIBRARY[class_code]

# Instantiate MRSIF v3.0 Core Engine
mrsif_gate_status = "PASSED"
mrsif_gate_details = {}
mrsif_fieldtwin_sync = {}

try:
    current_tool = ToolSpecs(
        tool_name="Subsea Intervention Unit",
        rated_load_lbs=tool_rated_load,
        interface_standard=tool_interface,
        max_hydraulic_pressure_psi=5000.0
    )
    current_asset = AsInstalledAssetConditions(
        asset_name=f"Subsea Asset {selected_tag}",
        required_load_lbs=asset_required_load,
        interface_standard=asset_interface,
        env_pressure_psi=float(measured_pressure)
    )
    
    mrsif_engine = MRSIFExecutionEngine(
        work_ref_no=f"WR-2026-{selected_tag}",
        vehicle_id=f"VOT-ROV-{tag_meta['serial']}",
        owner_id="VIKRA_OCEAN_TECH",
        last_audit_date=datetime.combine(last_audit_date_input, datetime.min.time()),
        is_audit_cleared=audit_cleared,
        hse_controls_bypassed=hse_bypassed,
        tool_specs=current_tool,
        asset_conditions=current_asset
    )
    
    mrsif_gate_details = mrsif_engine.evaluate_pre_mobilization_gate()
    mrsif_fieldtwin_sync = mrsif_engine.sync_to_fieldtwin(mrsif_gate_details)
    mrsif_gate_passed = mrsif_gate_details["status"] == DeploymentStatus.APPROVED
except Exception as err:
    mrsif_gate_passed = False
    mrsif_gate_details = {
        "status": DeploymentStatus.DENIED,
        "reason": f"EXCEPTIONAL LOCK: {str(err)}",
        "action": "MOBILIZATION DENIED ASHORE"
    }

header_block = MrsifUpdateHeader(
    timestamp_utc=datetime.now(timezone.utc).isoformat()
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
is_safe = metocean_passed and deck_test_completed and auto_dvl_lock and function_test_completed and mrsif_gate_passed

# ====================================================================
# 7. APPLICATION DISPLAY SURFACE
# ====================================================================
st.markdown("### 📊 Live System Verification Status Ledger")
status_col1, status_col2, status_col3 = st.columns(3)

with status_col1:
    card_style = "metric-card success" if metocean_passed else "metric-card error"
    st.markdown(f"""
        <div class="{card_style}">
            <h5 style='margin:0; font-family: sans-serif;'>Metocean Threshold</h5>
            <h2 style='margin:5px 0; font-family: monospace;'>{metocean_current} kts</h2>
            <p style='margin:0; font-size:12px;'>Limit: 1.5 kts Max Drag</p>
        </div>
    """, unsafe_allow_html=True)

with status_col2:
    card_style = "metric-card success" if mrsif_gate_passed else "metric-card error"
    status_msg = mrsif_gate_details.get("action", "LOCKED")
    st.markdown(f"""
        <div class="{card_style}">
            <h5 style='margin:0; font-family: sans-serif;'>MRSIF v3.0 Logic Gate</h5>
            <h2 style='margin:5px 0; font-family: monospace; font-size: 20px;'>{status_msg}</h2>
            <p style='margin:0; font-size:12px;'>{mrsif_gate_details.get('reason', '')}</p>
        </div>
    """, unsafe_allow_html=True)

with status_col3:
    card_style = "metric-card success" if is_safe else "metric-card error"
    status_text = "EXECUTION PERMITTED" if is_safe else "SAFETY SYSTEM LOCKED"
    st.markdown(f"""
        <div class="{card_style}">
            <h5 style='margin:0; font-family: sans-serif;'>Framework Integrity Gate</h5>
            <h2 style='margin:5px 0; font-family: monospace;'>{status_text}</h2>
            <p style='margin:0; font-size:12px;'>All Pre-requisites & Checks</p>
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
    st.markdown("### 📋 Runtime Hierarchical Schema & MRSIF Engine Parsing Loop")
    col_info, col_json = st.columns([1, 1])
    with col_info:
        st.markdown("#### Mapped Identity Parameters")
        st.write(f"* **Target Tag Assignment:** `{runtime_payload.functional_tag}`")
        st.write(f"* **Resolved Equipment Class:** `{runtime_payload.asset_identity.cfihos_equipment_class} ({class_definition['class_name']})`")
        st.write(f"* **Global Vehicle Verification ID:** `{runtime_payload.asset_identity.vehicle_global_id}`")
        st.write(f"* **IMCA Registry Link:** `{runtime_payload.asset_identity.imca_unique_id}`")
        
        st.markdown("#### MRSIF Gate Evaluation")
        st.write(f"* **Audit Cleared Status:** `{audit_cleared}`")
        st.write(f"* **Tool/Asset Interface:** `{tool_interface}` vs `{asset_interface}`")
        st.write(f"* **Tool Rated Load:** `{tool_rated_load} lbs` (Req: `{asset_required_load} lbs`)")

        st.markdown("#### Active Telemetry Registries")
        for prop_id, prop_data in class_definition["properties"].items():
            live_value = live_telemetry_map.get(prop_id, prop_data["default"])
            st.write(f"* `{prop_id}` **{prop_data['name']}:** `{live_value} {prop_data['unit']}`")
    with col_json:
        st.markdown("#### Live FieldTwin Handshake & Pydantic Payload")
        st.json({
            "mrsif_gate_evaluation": mrsif_gate_details,
            "fieldtwin_payload": mrsif_fieldtwin_sync,
            "runtime_payload": runtime_payload.model_dump()
        })

with step_tabs[1]:
    st.markdown("### 🔬 Mission Method Verification Logs")
    st.checkbox("Verify Work Class ROV telemetry and communication paths", key="f1")
    st.checkbox("Confirm 7-Function Manipulator joint and torque calibrations match ISO 13628-8 profiles", key="f2")
    st.checkbox("Perform dry pressure testing on Dual Port Hot Stab system (Rated to 10,000 PSI)", key="f3")
    if function_test_completed: 
        st.success("✅ PRE-MOBILIZATION TESTING CLEARED")

with step_tabs[2]:
    st.markdown("### 🏗️ Rigging & Mobilization Compliance Gates")
    if not function_test_completed:
        st.error("🔒 LOCKOUT: Complete Tab 2 Contractor Attestation before running mobilization deck telemetry routines.")
    else:
        st.checkbox("Run physical deck functional test on Dual Port Hot Stab manifold valves", key="d1")
        st.checkbox("Confirm hydraulic compensator oil levels are fully topped off", key="d2")
        st.checkbox("Verify ground fault monitoring systems (GFI) display clear green loops on power up", key="d3")
        if is_safe: 
            st.success("🚀 DEPLOYMENT COMPLIANCE CLEARANCE APPLIED")

with step_tabs[3]:
    st.markdown("### 🌐 Real-Time Spatial Grid Alignment (EPSG:32639 Target Mapping)")
    
    x_grid = np.linspace(EASTING_ANCHOR, EASTING_ANCHOR + 100, 40)
    y_grid = np.linspace(NORTHING_ANCHOR - 40, NORTHING_ANCHOR + 40, 40)
    X, Y = np.meshgrid(x_grid, y_grid)
    
    base_seabed_depth = 510.0 + ((X - EASTING_ANCHOR) * 0.05)
    trench_depression = 8.0 * np.exp(-((Y - NORTHING_ANCHOR) / 12.0)**2)
    Z = base_seabed_depth - trench_depression
    
    fig = go.Figure()
    
    fig.add_trace(go.Surface(
        x=X, y=Y, z=Z, 
        colorscale='Viridis', 
        opacity=0.7, 
        showscale=True,
        colorbar=dict(title=dict(text="Depth (m)", font=dict(color="#94a3b8")), tickfont=dict(color="#94a3b8"))
    ))
    
    geojson_features = []
    for tag, d in ACTIVE_FIELD_TAGS.items():
        is_current = (tag == selected_tag)
        m_color = "#10b981" if (is_safe and is_current) else "#ef4444" if is_current else "#38bdf8"
        
        fig.add_trace(go.Scatter3d(
            x=[d["x"]], y=[d["y"]], z=[d["z"]], 
            mode="markers+text", 
            name=f"Tag: {tag}",
            text=[f"📍 {tag}"], 
            textposition="top center",
            textfont=dict(color="#ffffff", size=11),
            marker=dict(size=12, color=m_color, symbol='diamond', line=dict(color='#ffffff', width=2))
        ))
        
        geojson_features.append({
            "type": "Feature",
            "properties": {"TagName": tag, "ClassCode": d["class_code"], "Depth_m": d["z"]},
            "geometry": {"type": "Point", "coordinates": [d["x"], d["y"]]}
        })
        
        if is_current:
            vehicle_alt = d["z"] - rov_altitude
            fig.add_trace(go.Scatter3d(
                x=[d["x"], d["x"]], y=[d["y"], d["y"]], z=[d["z"], vehicle_alt],
                mode="lines",
                name="Acoustic Link Vector",
                line=dict(color="#06b6d4", width=3, dash="dash")
            ))
            fig.add_trace(go.Scatter3d(
                x=[d["x"]], y=[d["y"]], z=[vehicle_alt],
                mode="markers",
                name="ROV Operational Center",
                marker=dict(size=9, color="#06b6d4", symbol='square')
            ))
            
            geojson_features.append({
                "type": "Feature",
                "properties": {"TagName": f"ROV_{tag}", "Altitude_m": rov_altitude, "Type": "Vehicle Operational Center"},
                "geometry": {"type": "Point", "coordinates": [d["x"], d["y"]]}
            })

    fig.update_layout(
        margin=dict(l=0, r=0, b=0, t=0), height=550,
        scene=dict(
            xaxis=dict(
                title=dict(text="UTM Easting (m)", font=dict(color="#94a3b8")), 
                backgroundcolor="#0b0f19", 
                gridcolor="#1e293b", 
                showbackground=True, 
                tickfont=dict(color="#94a3b8")
            ),
            yaxis=dict(
                title=dict(text="UTM Northing (m)", font=dict(color="#94a3b8")), 
                backgroundcolor="#0b0f19", 
                gridcolor="#1e293b", 
                showbackground=True, 
                tickfont=dict(color="#94a3b8")
            ),
            zaxis=dict(
                title=dict(text="Depth Profile (m)", font=dict(color="#94a3b8")), 
                autorange="reversed", 
                backgroundcolor="#0b0f19", 
                gridcolor="#1e293b", 
                showbackground=True, 
                tickfont=dict(color="#94a3b8")
            ),
            camera=dict(eye=dict(x=1.4, y=-1.4, z=1.0))
        ),
        paper_bgcolor="#0b0f19", plot_bgcolor="#0b0f19",
        legend=dict(font=dict(color="#94a3b8"), bgcolor="rgba(11,15,25,0.8)")
    )
    st.plotly_chart(fig, use_container_width=True)
    
    geojson_data = {
        "type": "FeatureCollection",
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::32639"}},
        "features": geojson_features
    }
    
    st.markdown("### 🌐 Native GIS Layer Engine Outgestion")
    st.download_button(
        label="🌍 Download Spatial Twin GIS Layer (.GeoJSON)",
        data=json.dumps(geojson_data, indent=2),
        file_name=f"MRSIF_SpatialTwin_{selected_tag}.geojson",
        mime="application/geo+json"
    )

with step_tabs[4]:
    st.markdown("### 📊 Consolidated Hierarchical Outgestion Package (CFIHOS/OSDU Format)")
    if not is_safe:
        st.warning("⚠️ System Hold: Compliance signatures and outgestion packages are locked until gate constraints are satisfied.")
    else:
        st.success("🏁 EXPORT STREAM STABILIZED: NESTED MODEL COMPLETELY DOCUMENTED")
        
        final_package = {
            "handover_format_version": "CFIHOS_V1.5 // OSDU_R3_COMPLIANT",
            "mrsif_gate_clearance": mrsif_gate_details,
            "fieldtwin_sync": mrsif_fieldtwin_sync,
            "compiled_payload": runtime_payload.model_dump()
        }
        
        st.json(final_package)
        
        st.markdown("### 📄 Formal Handover Documentation Processing")
        st.download_button(
            label="📥 Download Consolidated Handover Report (JSON)",
            data=json.dumps(final_package, indent=2),
            file_name=f"VODIDS_MRSIF_Handover_{selected_tag}.json",
            mime="application/json"
        )
