import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
import random
import math
import hashlib
import json
from pydantic import BaseModel
from datetime import datetime

# ====================================================================
# 1. OPERATION ARCHITECTURE OBJECT SCHEMAS
# ====================================================================
class EPCIWorkOrder(BaseModel):
    work_order_id: str = "WO-CHEV-GABON-009"
    client: str = "Chevron Oil Field"
    platform: str = "Chevron-1"
    subsea_asset: str = "XMAS Tree (XT-04)"
    location: str = "Gabon, West Africa"
    water_depth_m: float = 500.0
    task_description: str = "Hot Stab Valve Opening Operation"  # <-- ADD THIS LINE
    tooling_standard: str = "ISO 13628-8 Hot Stab Type A"
    max_current_limit_kts: float = 1.5
    
SUBSEA_ASSETS = {
    "CHEV-1_XMAS_TREE_XT04": {"x": 50.0, "y": 0.0, "z": 500.0, "type": "XMAS Tree Valve", "color": "#f59e0b"},
    "MANIFOLD-GABON-A": {"x": 15.0, "y": -15.0, "z": 505.0, "type": "Subsea Manifold", "color": "#06b6d4"},
    "EXPORT-RISER-BASE": {"x": 90.0, "y": 0.0, "z": 495.0, "type": "Riser Connector", "color": "#3b82f6"}
}

# ====================================================================
# 2. EXECUTIVE INTERFACE CONFIGURATION
# ====================================================================
st.set_page_config(
    page_title="MRSIF | Chevron Command Surface",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Corporate CSS Injection to give a ruggedized control center appearance
st.markdown("""
    <style>
        .reportview-container { background: #0b0f19; }
        .stMarkdown h1, h2, h3 { color: #f1f5f9 !important; font-family: 'Courier New', Courier, monospace; }
        div[data-testid="stMetricValue"] { font-size: 32px !important; font-family: 'Courier New', Courier, monospace; font-weight: bold; }
        .stTabs [data-baseweb="tab-list"] { gap: 8px; }
        .stTabs [data-baseweb="tab"] {
            background-color: #1e293b;
            border-radius: 4px 4px 0px 0px;
            padding: 10px 20px;
            color: #94a3b8;
            font-weight: bold;
        }
        .stTabs [aria-selected="true"] { background-color: #0284c7 !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

# Application Banner Headers
st.title("🛡️ MRSIF | DEEPWATER OPERATIONAL COMMAND SURFACE")
st.caption("Contract Architecture Reference: Chevron-1 Field Development // Gabon Block West Africa")
st.markdown("---")

# Session State Cache Loops
for key in ["f1", "f2", "f3", "d1", "d2", "d3"]:
    if key not in st.session_state:
        st.session_state[key] = False

# ====================================================================
# 3. HIGH-FIDELITY SIDEBAR CONTROL DECK
# ====================================================================
st.sidebar.image("https://img.icons8.com/external-flatart-icons-flat-flatarticons/128/external-robotics-artificial-intelligence-flatart-icons-flat-flatarticons.png", width=55)
st.sidebar.markdown("### 🎛️ SIMULATION TELEMETRY")
st.sidebar.markdown("---")

st.sidebar.markdown("**🌐 1. METOCEAN TELEMETRY FEED**")
metocean_current = st.sidebar.slider("Live Seafloor Current Velocity (kts)", 0.5, 3.0, 1.2, step=0.1)

st.sidebar.markdown("**🦾 2. VEHICLE KINEMATICS**")
auto_station_keeping = st.sidebar.checkbox("Engage Hydroacoustic DVL Seafloor Lock", value=True)
manipulator_readiness = st.sidebar.selectbox("Manipulator Feedback Calibration Loop", ["Verified 7-Function (Active)", "Out of Calibration"])

st.sidebar.markdown("**⚓ 3. POSITIONING CALIBRATIONS**")
rov_altitude = st.sidebar.slider("Vehicle Altitude Off-Seabed (m)", 1.0, 10.0, 4.0, step=0.5)
supervisor_id = st.sidebar.text_input("Subsea Supervisor IMCA Sign-off ID", value="SV-IMCA-4401")

# ====================================================================
# 4. DETERMINISTIC LOGIC RESOLUTIONS
# ====================================================================
work_order = EPCIWorkOrder()

function_test_completed = st.session_state.f1 and st.session_state.f2 and st.session_state.f3
deck_test_completed = st.session_state.d1 and st.session_state.d2 and st.session_state.d3
metocean_passed = metocean_current <= work_order.max_current_limit_kts
manipulator_passed = "Active" in manipulator_readiness

is_safe = metocean_passed and manipulator_passed and deck_test_completed and auto_station_keeping and function_test_completed

# ====================================================================
# 5. HIGH-LEVEL INDUSTRIAL DASHBOARD COMPONENT STRUCTURE
# ====================================================================

# Top Row: Real-Time Executive KPI Scoreboard Cards
kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
with kpi_col1:
    st.metric("Target Water Depth", f"{work_order.water_depth_m} Meters", "OSDU Profile")
with kpi_col2:
    current_delta = round(work_order.max_current_limit_kts - metocean_current, 2)
    st.metric("Current Clearance", f"{metocean_current} kts", f"{current_delta} kts Margin", delta_color="normal" if current_delta >= 0 else "inverse")
with kpi_col3:
    st.metric("Subsea Interface Spec", "ISO 13628-8", "API 17H Type A")
with kpi_col4:
    if is_safe:
        st.metric("System Safety Gate", "GREEN GATE", "GO / DEPLOY", delta_color="normal")
    else:
        st.metric("System Safety Gate", "RED LOCKED", "SYSTEM OVERRIDE", delta_color="inverse")

st.markdown("---")

# Main Operations Tab Layout Split
step_tabs = st.tabs([
    "📂 1. Project Ingestion", 
    "🔬 2. Subsea Contractor Attestation", 
    "🏗️ 3. Physical Deck Checks", 
    "🌐 4. Live Spatial Twin View", 
    "📊 5. Export Deliverable Handover"
])

# TAB 1: INGESTION GATES
with step_tabs[0]:
    st.markdown("### 📋 Automated OSDU / EPCI Work Order Verification")
    col_info, col_json = st.columns([2, 1])
    with col_info:
        st.markdown(f"**Contract Scope Identified:** `{work_order.task_description}`")
        st.markdown(f"**Asset Owner / Location:** `{work_order.client}` // `{work_order.location}`")
        st.markdown(f"**Operational Target Core:** `{work_order.subsea_asset}` tethered to host platform `{work_order.platform}`")
        st.info("💡 Data Architecture Rule: Safety systems automatically lock out valve commands if live metocean parameters breach the 1.5 kts vehicle drag threshold.")
    with col_json:
        st.markdown("**Structured System Ingestion Payload**")
        st.json(work_order.model_dump())

# TAB 2: METHOD STATEMENTS
with step_tabs[1]:
    st.markdown("### 🔬 Contractor Method Statements & Sim Benchmarks")
    col_checks, col_doc = st.columns(2)
    with col_checks:
        st.markdown("**Subsea Contractor Task Attestations**")
        st.checkbox("Verify Work Class ROV telemetry and communication paths", key="f1")
        st.checkbox("Confirm 7-Function Manipulator joint and torque calibrations match ISO 13628-8 profiles", key="f2")
        st.checkbox("Perform dry pressure testing on Dual Port Hot Stab system (Rated to 10,000 PSI)", key="f3")
        
        if function_test_completed:
            st.success("🏁 LAYER 2 TESTING COMPLETELY VERIFIED BY CONTRACTOR")
        else:
            st.warning("⚠️ Awaiting mandatory contractor system validation benchmarks.")
    with col_doc:
        st.markdown("**Standard Operating Procedure Reference**")
        st.info("""
        **VOT-SOP-22-4 (Hot Stab Valve Actuation):**
        * Confirm subsea interface receptacle is completely free of marine growth.
        * Stabilize vessel position within a tight 0.5m drift zone using high-frequency acoustics.
        * Maintain manipulator tool orientation parallel to alignment pins. Torque up to 145 Nm for absolute latch validation.
        """)

# TAB 3: DECK TEST
with step_tabs[2]:
    st.markdown("### 🏗️ Rigging & Deck Mobilization Gates")
    if not function_test_completed:
        st.error("🔒 LOCKOUT EXECUTED: Complete Tab 2 Contractor Attestation before accessing Deck Verification dashboards.")
    else:
        col_deck, col_permit = st.columns(2)
        with col_deck:
            st.markdown("**Mobilization Rigging Verification**")
            st.checkbox("Run physical deck functional test on Dual Port Hot Stab manifold valves", key="d1")
            st.checkbox("Confirm hydraulic compensator oil levels are fully topped off", key="d2")
            st.checkbox("Verify ground fault monitoring systems (GFI) display clear green loops on power up", key="d3")
            
            if deck_test_completed:
                st.success("✅ ALL PHYSICAL DECK TELEMETRY REGISTERED AND LOCKED INTO STORAGE")
        with col_permit:
            st.markdown("**Active Cryptographic Validation Portal**")
            st.write(f"Contractor Attestation: {'🟢 VERIFIED' if function_test_completed else '🔴 PENDING'}")
            st.write(f"Physical Deck Log: {'🟢 VERIFIED' if deck_test_completed else '🔴 PENDING'}")
            st.write(f"Hydrographic Environmental Hazard: {'🟢 SAFE RANGE' if metocean_passed else '🔴 CONDITIONAL CRITICAL'}")
            
            if is_safe:
                permit_data = {"work_order": work_order.work_order_id, "status": "APPROVED", "timestamp": datetime.now().isoformat()}
                cryptographic_token = f"MRSIF-PERMIT-SIG-{hashlib.sha256(json.dumps(permit_data, sort_keys=True).encode('utf-8')).hexdigest()[:24].upper()}"
                st.success("🚀 DEPLOYMENT COMPLIANCE CLEARANCE APPLIED")
                st.code(cryptographic_token, language="bash")
            else:
                st.error("🚫 SAFETY OVERRIDE ACTIVE: MOBILIZATION SYSTEM LOCKED DOWN")

# TAB 4: LIVE SPATIAL TWIN
with step_tabs[3]:
    st.markdown("### 🌐 Chevron-1 Subsea Spatial Twin Environment")
    
    X_floor = np.linspace(0, 100, 30)
    Y_floor = np.linspace(-30, 30, 30)
    X, Y = np.meshgrid(X_floor, Y_floor)
    Z = 500.0 + (np.sin(X / 15.0) * np.cos(Y / 10.0) * 1.5)

    fig = go.Figure()
    fig.add_trace(go.Surface(x=X, y=Y, z=Z, colorscale='Turbid', opacity=0.35, showscale=False, name="Seafloor Mesh"))
    
    for tag, d in SUBSEA_ASSETS.items():
        m_color = "#10b981" if is_safe else "#ef4444" if "XMAS_TREE" in tag else d["color"]
        fig.add_trace(go.Scatter3d(
            x=[d["x"]], y=[d["y"]], z=[d["z"]], mode="markers+text", name=f"{d['type']}",
            text=[f"{d['type']}\n{tag}"], textposition="top center",
            marker=dict(size=14, color=m_color, symbol='circle', line=dict(color='#ffffff', width=1))
        ))

    fig.add_trace(go.Scatter3d(x=[15.0, 50.0], y=[-15.0, 0.0], z=[505.0, 500.0], mode='lines', name="Flowline Corridor", line=dict(color='#475569', width=6)))
    fig.add_trace(go.Scatter3d(x=[50.0, 90.0], y=[0.0, 0.0], z=[500.0, 495.0], mode='lines', name="Export Corridor", line=dict(color='#0284c7', width=6)))

    path_x = np.linspace(10.0, 50.0, 20)
    path_y = np.sin(path_x / 5.0) * 2.0
    path_z = np.full(20, 500.0 - rov_altitude)
    
    fig.add_trace(go.Scatter3d(
        x=path_x, y=path_y, z=path_z, mode='lines+markers', name="Active ROV Route Vector",
        marker=dict(size=5, color='#10b981' if is_safe else '#ef4444'),
        line=dict(color='#10b981' if is_safe else '#ef4444', width=4)
    ))

    fig.update_layout(
        margin=dict(l=0, r=0, b=0, t=0), height=550,
        scene=dict(
            xaxis=dict(title="UTM East (m)", backgroundcolor="#0b0f19", gridcolor="#1e293b", showbackground=True),
            yaxis=dict(title="UTM North (m)", backgroundcolor="#0b0f19", gridcolor="#1e293b", showbackground=True),
            zaxis=dict(title="Depth Profile (m)", autorange="reversed", backgroundcolor="#0b0f19", gridcolor="#1e293b", showbackground=True),
            camera=dict(eye=dict(x=1.3, y=1.3, z=0.9))
        ),
        paper_bgcolor="#0b0f19", plot_bgcolor="#0b0f19",
        legend=dict(yanchor="top", y=0.95, xanchor="left", x=0.02, font=dict(color="#94a3b8"))
    )
    st.plotly_chart(fig, use_container_width=True)

# TAB 5: DELIVERABLES
with step_tabs[4]:
    st.markdown("### 📊 Operational Telemetry Handover Package")
    if not is_safe:
        st.warning("⚠️ System Lock: Telemetry logs are unavailable until the subsea deployment permit is formally generated.")
    else:
        st.success("🏁 MISSION METRICS ARCHIVED SUCCESSFULLY")
        col_log1, col_log2 = st.columns(2)
        with col_log1:
            st.markdown("**Real-Time Actuation Telemetry Package**")
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
            st.markdown("**As-Built Verification Metadata Assets**")
            st.info("📹 **Video Asset:** CHEV1_XT04_VALVE_ACTUATION.MP4 (Logged in Registry)")
            st.info("🦾 **Manipulator Log:** High-Fidelity Torque Vector Arrays (Secured)")
            st.info("🔌 **Hot Stab Log:** Hydraulic fluid flow signature profiles logged.")
            st.markdown("---")
            st.markdown(f"**Lead Supervisor Signature Validation Loop:** `{supervisor_id}`")
