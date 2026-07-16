import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
import random
import math
import hashlib
import json
from pydantic import BaseModel, Field
from datetime import datetime

# ====================================================================
# 1. CORE OPERATIONAL SCHEMAS & CONFIGURATIONS
# ====================================================================
class EPCIWorkOrder(BaseModel):
    work_order_id: str = "WO-CHEV-GABON-009"
    client: str = "Chevron Oil Field"
    platform: str = "Chevron-1"
    subsea_asset: str = "XMAS Tree (XT-04)"
    location: str = "Gabon, West Africa"
    water_depth_m: float = 500.0
    task_description: str = "Hot Stab Valve Opening Operation"
    tooling_standard: str = "ISO 13628-8 / API 17H Type A (Dual Port)"
    max_current_limit_kts: float = 1.5

# Static layout of our West Africa Subsea Field
SUBSEA_ASSETS = {
    "CHEV-1_XMAS_TREE_XT04": {"x": 50.0, "y": 0.0, "z": 500.0, "type": "XMAS Tree Valve", "color": "#f59e0b"},
    "MANIFOLD-GABON-A": {"x": 15.0, "y": -15.0, "z": 505.0, "type": "Subsea Manifold", "color": "#06b6d4"},
    "EXPORT-FLOWLINE-01": {"x": 90.0, "y": 0.0, "z": 495.0, "type": "Riser Connector", "color": "#3b82f6"}
}

# ====================================================================
# 2. UI CONFIGURATION & STATE INITIALIZATION
# ====================================================================
st.set_page_config(
    page_title="MRSIF | Chevron West Africa Command",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🛡️ MRSIF Command Console | Chevron West Africa Operations")
st.caption("Active EPCI Lifecycle Portal: Asset - Chevron-1 (Gabon Field) | Standard: ISO 13628-8 Hot Stab")
st.markdown("---")

# Persistent State Initializer to stop tab switching from wiping inputs
for state_key in ["f1", "f2", "f3", "d1", "d2", "d3"]:
    if state_key not in st.session_state:
        st.session_state[state_key] = False

# ====================================================================
# 3. SIDEBAR TELEMETRY CONTROLS
# ====================================================================
st.sidebar.image("https://img.icons8.com/external-flatart-icons-flat-flatarticons/128/external-robotics-artificial-intelligence-flatart-icons-flat-flatarticons.png", width=60)
st.sidebar.title("EPCI Gate Control")
st.sidebar.markdown("---")

st.sidebar.subheader("🌊 OSDU Metocean Live")
metocean_current = st.sidebar.slider("Live Current Speed (kts)", 0.5, 3.0, 1.2, step=0.1)

st.sidebar.subheader("🛠️ ROV Station Keeping")
auto_station_keeping = st.sidebar.checkbox("Activate Seabed Station Keeping (DVL/INS Lock)", value=True)
manipulator_readiness = st.sidebar.selectbox("Manipulator Calibrations", ["Verified 7-Function (Active)", "Out of Calibration"])

st.sidebar.subheader("👤 Supervisor Log")
supervisor_id = st.sidebar.text_input("Lead Subsea Supervisor ID", value="SV-IMCA-4401")

st.sidebar.subheader("⚓ Vessel Positioning")
rov_altitude = st.sidebar.slider("ROV Flight Altitude (m)", 1.0, 10.0, 4.0, step=0.5)

# ====================================================================
# 4. GLOBAL CALCULATIONS
# ====================================================================
work_order = EPCIWorkOrder()

# Compute gate passes globally so all tabs see the same reality
function_test_completed = st.session_state.f1 and st.session_state.f2 and st.session_state.f3
deck_test_completed = st.session_state.d1 and st.session_state.d2 and st.session_state.d3

metocean_passed = metocean_current <= work_order.max_current_limit_kts
manipulator_passed = "Active" in manipulator_readiness

is_safe = metocean_passed and manipulator_passed and deck_test_completed and auto_station_keeping and function_test_completed

# ====================================================================
# 5. FIVE-STAGE PIPELINE WORKFLOW (THE DEMO TRAIL)
# ====================================================================
step_tabs = st.tabs([
    "📂 1. Project Initiation", 
    "🔬 2. Method Statements & Testing", 
    "🏗️ 3. Deck Test & Mobilization", 
    "🌐 4. Live Digital Twin Execution", 
    "📊 5. Deliverables & Handover"
])

# --------------------------------------------------------------------
# TAB 1: PROJECT INITIATION
# --------------------------------------------------------------------
with step_tabs[0]:
    st.subheader("📋 Client Work Order Ingestion")
    col_info, col_json = st.columns([2, 1])
    with col_info:
        st.markdown(f"**Work Order Reference:** `{work_order.work_order_id}`")
        st.markdown(f"**Operator/Client:** `{work_order.client}` (Gabon, West Africa Field)")
        st.markdown(f"**Operational Target:** `{work_order.subsea_asset}` located on `{work_order.platform}`")
        st.markdown(f"**Interface Specification:** `{work_order.tooling_standard}`")
        st.markdown(f"**Hydrostatic Target Depth:** `{work_order.water_depth_m}m` (Seabed Profile: **Clayey Sand**)")
        st.info("💡 Note: Client specifies maximum operational currents must not exceed 1.5 kts for Hot Stab manipulation.")
    with col_json:
        st.markdown("**Structured OSDU Ingestion Payload**")
        st.json(work_order.model_dump())

# --------------------------------------------------------------------
# TAB 2: METHOD STATEMENTS & FUNCTION TESTING
# --------------------------------------------------------------------
with step_tabs[1]:
    st.subheader("🔬 ROV, Tooling & Manipulator Function Test Review")
    st.write("Before proceeding to deck mobilization, the Subsea Contractor must programmatically check and log the operational method statements and simulated function trials.")
    
    col_checks, col_doc = st.columns(2)
    with col_checks:
        st.markdown("### Mandatory Pre-Mobilization Function Log")
        # Bind checkboxes explicitly to session state keys to persist across tabs
        st.checkbox("Verify Work Class ROV telemetry and communication paths", key="f1")
        st.checkbox("Confirm 7-Function Manipulator joint and torque calibrations match ISO 13628-8 profiles", key="f2")
        st.checkbox("Perform dry pressure testing on Dual Port Hot Stab system (Rated to 10,000 PSI)", key="f3")
        
        if function_test_completed:
            st.success("✅ FUNCTION TESTS VERIFIED & ATTESTED BY CONTRACTOR SUPERVISOR")
        else:
            st.warning("⚠️ Pending Contractor Function Testing Approvals.")

    with col_doc:
        st.markdown("### 📝 Tooling Method Statement")
        st.info("""
        **Procedure 22.4 - Hot Stab Valve Actuation:**
        1. Deploy ROV with ISO 13628-8 Type A Dual Port Hot Stab secured in the utility holster.
        2. Establish steady seafloor hover using DVL/INS station-keeping algorithms to offset current loads.
        3. Utilize the 7-Function manipulator to extract the Hot Stab and execute parallel alignment with the receptacle.
        4. Engage Hot Stab. Inject hydraulic fluid regulated up to 3,000 PSI to actuate the 500m depth valve on XMAS Tree XT-04.
        """)

# --------------------------------------------------------------------
# TAB 3: DECK TEST & MOBILIZATION
# --------------------------------------------------------------------
with step_tabs[2]:
    st.subheader("🏗️ Deck Test Verification Panel")
    st.write("Perform physical deck functional checks on mobilization of the tooling and system prior to subsea deployment.")

    if not function_test_completed:
        st.error("❌ Blocked: Complete Step 2 (Method Statements & Testing) before unlocking Deck Mobilization.")
    else:
        col_deck, col_permit = st.columns(2)
        with col_deck:
            st.markdown("### 🎛️ Wet/Dry Deck System Checklist")
            st.checkbox("Run physical deck functional test on Dual Port Hot Stab manifold valves", key="d1")
            st.checkbox("Confirm hydraulic compensator oil levels are fully topped off", key="d2")
            st.checkbox("Verify ground fault monitoring systems (GFI) display clear green loops on power up", key="d3")
            
            if deck_test_completed:
                st.success("✅ DECK TEST COMPLETED SUCCESSFULLY")
            else:
                st.warning("⚠️ Deck check execution required.")

        with col_permit:
            st.markdown("### 🔑 Live Gatekeeper Validation")
            st.write(f"**Layer 3 (Deck Test Status):** {'🟢 PASSED' if deck_test_completed else '🔴 PENDING'}")
            st.write(f"**Layer 4 (Metocean Limit Check):** {'🟢 PASSED' if metocean_passed else '🔴 BREACHED'}")
            st.write(f"**Layer 0 (Station Keeping & Manipulators):** {'🟢 PASSED' if auto_station_keeping and manipulator_passed else '🔴 ERROR'}")
            
            if is_safe:
                permit_data = {"work_order": work_order.work_order_id, "status": "APPROVED", "timestamp": datetime.now().isoformat()}
                serialized_data = json.dumps(permit_data, sort_keys=True).encode('utf-8')
                cryptographic_token = f"MRSIF-PERMIT-SIG-{hashlib.sha256(serialized_data).hexdigest()[:24].upper()}"
                
                st.success("🚀 DEPLOYMENT PERMIT ISSUED")
                st.code(cryptographic_token, language="bash")
            else:
                st.error("🚫 MOBILIZATION SYSTEM LOCKED OUT")
                st.warning("Ensure Metocean currents are safe (< 1.5 kts) and all checklists are fully checked off.")

# --------------------------------------------------------------------
# TAB 4: LIVE DIGITAL TWIN WORKSPACE
# --------------------------------------------------------------------
with step_tabs[3]:
    st.subheader("🌐 Chevron-1 Subsea Workspace Spatial Twin")
    
    # 3D Plotly Grid Generation
    X_floor = np.linspace(0, 100, 30)
    Y_floor = np.linspace(-30, 30, 30)
    X, Y = np.meshgrid(X_floor, Y_floor)
    Z = 500.0 + (np.sin(X / 15.0) * np.cos(Y / 10.0) * 1.5)

    fig = go.Figure()
    fig.add_trace(go.Surface(x=X, y=Y, z=Z, colorscale='Turbid', opacity=0.4, showscale=False, name="Clayey Sand Seafloor"))
    
    for tag, d in SUBSEA_ASSETS.items():
        m_color = "#10b981" if is_safe else "#ef4444" if "XMAS_TREE" in tag else d["color"]
        fig.add_trace(go.Scatter3d(
            x=[d["x"]], y=[d["y"]], z=[d["z"]],
            mode="markers+text", name=f"{d['type']}",
            text=[f"{d['type']}\n{tag}"], textposition="top center",
            marker=dict(size=14, color=m_color, symbol='circle', line=dict(color='#ffffff', width=1))
        ))

    fig.add_trace(go.Scatter3d(x=[15.0, 50.0], y=[-15.0, 0.0], z=[505.0, 500.0], mode='lines', name="Flowline Corridor (Static)", line=dict(color='#475569', width=6)))
    fig.add_trace(go.Scatter3d(x=[50.0, 90.0], y=[0.0, 0.0], z=[500.0, 495.0], mode='lines', name="Export Corridor", line=dict(color='#0284c7', width=6)))

    path_x = np.linspace(10.0, 50.0, 20)
    path_y = np.sin(path_x / 5.0) * 2.0
    path_z = np.full(20, 500.0 - rov_altitude)
    
    fig.add_trace(go.Scatter3d(
        x=path_x, y=path_y, z=path_z,
        mode='lines+markers', name="Active ROV Mission Track",
        marker=dict(size=5, color='#10b981' if is_safe else '#ef4444'),
        line=dict(color='#10b981' if is_safe else '#ef4444', width=4)
    ))

    fig.update_layout(
        margin=dict(l=0, r=0, b=0, t=0), height=550,
        scene=dict(
            xaxis=dict(title="UTM East (m)", backgroundcolor="#0b0f19", gridcolor="#1e293b", showbackground=True),
            yaxis=dict(title="UTM North (m)", backgroundcolor="#0b0f19", gridcolor="#1e293b", showbackground=True),
            zaxis=dict(title="Seabed Depth (m)", autorange="reversed", backgroundcolor="#0b0f19", gridcolor="#1e293b", showbackground=True),
            camera=dict(eye=dict(x=1.3, y=1.3, z=0.9))
        ),
        paper_bgcolor="#0b0f19", plot_bgcolor="#0b0f19",
        legend=dict(yanchor="top", y=0.95, xanchor="left", x=0.02, font=dict(color="#94a3b8"))
    )
    
    st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------------------------
# TAB 5: DELIVERABLES & SIGN-OFF
# --------------------------------------------------------------------
with step_tabs[4]:
    st.subheader("📊 Execution Deliverables & Handover Package")
    st.write("Upon successful operation, the MRSIF gateway compiles the telemetry logs, visual assets, and manipulator feedback to submit to Chevron.")
    
    if not is_safe:
        st.warning("⚠️ Operations must be executed under approved environmental and test gates before deliverables are unlocked.")
    else:
        st.success("🏁 OPERATION COMPLETED SUCCESSFULLY. EXPORTING DOCUMENTATION.")
        
        col_log1, col_log2 = st.columns(2)
        with col_log1:
            st.markdown("### 🗄 ... Telemetry Feedback Packet")
            telemetry_export = {
                "work_order_reference": work_order.work_order_id,
                "valve_actuation_status": "100% OPENED (500m Depth)",
                "hot_stab_standard": "ISO 13628-8 Type A",
                "regulated_insertion_pressure_psi": 3150.0,
                "station_keeping_drift_m": 0.04,
                "manipulator_torque_nm": 145.2,
                "vessel_current_at_execution_kts": metocean_current
            }
            st.json(telemetry_export)
            
        with col_log2:
            st.markdown("### 🎥 Deliverable Metadata Check")
            st.info("📹 **Subsea Live Video Feed:** CHEV1_XT04_VALVE_ACTUATION.MP4 (Verified)")
            st.info("🦾 **Manipulator Feedback:** Telemetry-Synchronized Joint Angles Log (Verified)")
            st.info("🔌 **Hot Stab Log:** Hydraulic fluid pressure profiles logged.")
            st.markdown("---")
            st.markdown(f"**Lead Subsea Supervisor Certification Stamp:** `{supervisor_id}`")
