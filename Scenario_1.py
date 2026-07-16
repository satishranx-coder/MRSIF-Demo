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
# 2. UI CONFIGURATION
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

# Initialize Phase State machine
if 'operational_phase' not in st.session_state:
    st.session_state.operational_phase = "Phase 1: Project Initiation"
if 'deck_test_completed' not in st.session_state:
    st.session_state.deck_test_completed = False
if 'function_test_completed' not in st.session_state:
    st.session_state.function_test_completed = False

# ====================================================================
# 3. SIDEBAR TELEMETRY CONTROLS (Includes defining rov_altitude first!)
# ====================================================================
st.sidebar.image("https://img.icons8.com/external-flatart-icons-flat-flatarticons/128/external-robotics-artificial-intelligence-flatart-icons-flat-flatarticons.png", width=60)
st.sidebar.title("EPCI Gate Control")
st.sidebar.markdown("---")

# Live Environment Feeds
st.sidebar.subheader("🌊 OSDU Metocean Live")
metocean_current = st.sidebar.slider("Live Current Speed (kts)", 0.5, 3.0, 1.2, step=0.1)

# Dynamic Rigging
st.sidebar.subheader("🛠️ ROV Station Keeping")
auto_station_keeping = st.sidebar.checkbox("Activate Seabed Station Keeping (DVL/INS Lock)", value=True)
manipulator_readiness = st.sidebar.selectbox("Manipulator Calibrations", ["Verified 7-Function (Active)", "Out of Calibration"])

# Crew Rigging
st.sidebar.subheader("👤 Supervisor Log")
supervisor_id = st.sidebar.text_input("Lead Subsea Supervisor ID", value="SV-IMCA-4401")

# Vessel Positioning (Defined globally here so Plotly can access it immediately)
st.sidebar.subheader("⚓ Vessel Positioning")
rov_altitude = st.sidebar.slider("ROV Flight Altitude (m)", 1.0, 10.0, 4.0, step=0.5)

# ====================================================================
# 4. FIVE-STAGE PIPELINE WORKFLOW (THE DEMO TRAIL)
# ====================================================================

# Interactive Workflow Navigator Tabs
step_tabs = st.tabs([
    "📂 1. Project Initiation", 
    "🔬 2. Method Statements & Testing", 
    "🏗️ 3. Deck Test & Mobilization", 
    "🌐 4. Live Digital Twin Execution", 
    "📊 5. Deliverables & Sign-Off"
])

work_order = EPCIWorkOrder()

# --------------------------------------------------------------------
# TAB 1: PROJECT INITIATION (EPCI WORK ORDER GATES)
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
        f1 = st.checkbox("Verify Work Class ROV telemetry and communication paths", value=True)
        f2 = st.checkbox("Confirm 7-Function Manipulator joint and torque calibrations match ISO 13628-8 profiles", value=True)
        f3 = st.checkbox("Perform dry pressure testing on Dual Port Hot Stab system (Rated to 10,000 PSI)", value=True)
        
        if f1 and f2 and f3:
            st.session_state.function_test_completed = True
            st.success("✅ FUNCTION TESTS VERIFIED & ATTESTED BY CONTRACTOR SUPERVISOR")
