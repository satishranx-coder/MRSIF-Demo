import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
import random
import math
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Any

# ====================================================================
# 1. CORE DATA SCHEMAS (IOGP & CFIHOS COMPLIANT)
# ====================================================================
class HeaderBlock(BaseModel):
    thread_id: str = "TH-2026-9941A"
    submitting_company_id: str = "CO-VOT-984"

class AssetIdentityBlock(BaseModel):
    vehicle_global_id: str = "HASH-ROV-WC-MANTIS-01-SN4402"
    imca_unique_id: str = "IMCA-WC-9921"
    cfihos_equipment_class: str = "ROV_CLASS_III_WORK"

class TelemetryAndComms(BaseModel):
    primary_link: str = "FIBER_OPTIC"
    measured_latency_ms: float = 45.2

class CriticalSparesManifest(BaseModel):
    umbilical_termination_kit: str = "VERIFIED_ON_BOARD"
    thruster_motor_spare_count: int

class EmbeddedSubsystems(BaseModel):
    telemetry_and_comms: TelemetryAndComms
    critical_spares_manifest: CriticalSparesManifest

class CompleteMRSIFPayload(BaseModel):
    mrsif_update_header: HeaderBlock
    asset_identity_block: AssetIdentityBlock
    embedded_subsystems: EmbeddedSubsystems
    live_metocean_current_kts: float
    vehicle_drag_max_kts: float = 1.5

# ====================================================================
# 2. GENERATE ADVANCED 3D ENVIRONMENT (Bathymetry & Infrastructure)
# ====================================================================
@st.cache_data
def generate_bathymetry_seafloor():
    """Generates a realistic wave-like 3D seafloor grid terrain."""
    x = np.linspace(0, 100, 30)
    y = np.linspace(-30, 30, 30)
    X, Y = np.meshgrid(x, y)
    # Creating gentle terrain undulations centered around 125m depth
    Z = 125.0 + (np.sin(X / 15.0) * np.cos(Y / 10.0) * 1.8)
    return X, Y, Z

# Static layout of our CFIHOS field assets
SUBSEA_ASSETS = {
    "CFIHOS-PRD-MNFD-0042": {"x": 50.0, "y": 0.0, "z": 122.0, "type": "Manifold", "color": "#f59e0b"},
    "CFIHOS-WELL-HEAD-01": {"x": 15.0, "y": -15.0, "z": 125.0, "type": "Wellhead", "color": "#06b6d4"},
    "CFIHOS-WELL-HEAD-02": {"x": 15.0, "y": 15.0, "z": 124.0, "type": "Wellhead", "color": "#06b6d4"},
    "CFIHOS-FPSO-RISER-04": {"x": 90.0, "y": 0.0, "z": 118.0, "type": "Riser Base", "color": "#3b82f6"}
}

# ====================================================================
# 3. EXECUTIVE UI CONFIGURATION & STYLING
# ====================================================================
st.set_page_config(
    page_title="MRSIF | 3D FieldTwin Command Center",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom injection of smooth dark theme styles
st.markdown("""
    <style>
    .reportview-container { background: #0b0f19; }
    .stButton>button { width: 100%; font-weight: bold; }
    .gate-passed { color: #10b981; font-weight: bold; }
    .gate-failed { color: #ef4444; font-weight: bold; }
    </style>
""", unsafe_allowed_html=True)

st.title("🌐 MRSIF: 3D Subsea Command Surface")
st.caption("Active Digital Twin Environment Syncing OSDU Metocean Data & CFIHOS Asset Classes")
st.markdown("---")

# --- SIDEBAR CONTROL UNIT ---
st.sidebar.image("https://img.icons8.com/external-flatart-icons-flat-flatarticons/128/external-robotics-artificial-intelligence-flatart-icons-flat-flatarticons.png", width=60)
st.sidebar.title("Operational Controls")
st.sidebar.markdown("---")

st.sidebar.subheader("🌊 OSDU Metocean Feed")
metocean_current = st.sidebar.slider("Live Current Speed (kts)", 0.5, 3.0, 2.2, step=0.1)

st.sidebar.subheader("🛠️ Contractor Logistics")
spares_on_board = st.sidebar.slider("OEM Spares Verified (Layer 3)", 0, 4, 2)

st.sidebar.subheader("⚓ Vessel Positioning")
rov_altitude = st.sidebar.slider("ROV Flight Altitude (m)", 1.0, 10.0, 4.0, step=0.5)

# --- WORKSPACE LAYOUT ---
plot_col, panel_col = st.columns([2, 1])

with plot_col:
    plot_placeholder = st.empty()

with panel_col:
    st.subheader("🛡️ Gateway Logic Gates")
    gate_placeholder = st.empty()
    st.subheader("🧬 Pipeline Interface Payload")
    json_placeholder = st.empty()


# ====================================================================
# 4. DIGITAL TWIN SIMULATION RUN
# ====================================================================
# Initialize bathymetric background variables
X_floor, Y_floor, Z_floor = generate_bathymetry_seafloor()

# Instantiate compliance evaluation data structures
payload = CompleteMRSIFPayload(
    mrsif_update_header=HeaderBlock(),
    asset_identity_block=AssetIdentityBlock(),
    embedded_subsystems=EmbeddedSubsystems(
        telemetry_and_comms=TelemetryAndComms(),
        critical_spares_manifest=CriticalSparesManifest(
            thruster_motor_spare_count=spares_on_board
        )
    ),
    live_metocean_current_kts=metocean_current
)

# Run verification logic
metocean_passed = metocean_current <= payload.vehicle_drag_max_kts
spares_passed = spares_on_board >= 2
gate_status = metocean_passed and spares_passed

# Render interactive status panel cards
with gate_placeholder.container():
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"**Layer 3: OEM Fit-Check**")
        st.markdown(f"<span class='{'gate-passed' if spares_passed else 'gate-failed'}'>{'PASSED ✅' if spares_passed else 'FAILED ❌ (Low Spares)'}</span>", unsafe_allowed_html=True)
    with col_b:
        st.markdown(f"**Layer 4: Metocean Gate**")
        st.markdown(f"<span class='{'gate-passed' if metocean_passed else 'gate-failed'}'>{'PASSED ✅' if metocean_passed else 'FAILED ❌ (High Current)'}</span>", unsafe_allowed_html=True)
    
    st.markdown("---")
    if gate_status:
        st.success("🟢 GREEN GATE: MOBILIZATION APPROVED")
    else:
        st.error("🔴 RED GATE: MOBILIZATION BLOCKED")

# Display the parsed compliance schema payload
json_placeholder.json(payload.model_dump())

# --------------------------------------------------------------------
# 5. RENDER GEOSPATIAL 3D COMMAND MAP (PLOTLY ENGINE)
# --------------------------------------------------------------------
fig = go.Figure()

# Plot A: Seafloor Bathymetry Mesh
fig.add_trace(go.Surface(
    x=X_floor, y=Y_floor, z=Z_floor,
    colorscale='Icefire',
    opacity=0.35,
    showscale=False,
    name="Seafloor Bathymetry"
))

# Plot B: Asset Infrastructure Models (Rendering Blocks)
for tag, data in SUBSEA_ASSETS.items():
    # Enforce active visual color indicator based on dynamic gate validation status
    marker_color = "#10b981" if gate_status else "#ef4444" if tag == "CFIHOS-PRD-MNFD-0042" else data["color"]
    
    fig.add_trace(go.Scatter3d(
        x=[data["x"]], y=[data["y"]], z=[data["z"]],
        mode="markers+text",
        name=f"{data['type']} ({tag})",
        text=[f"{data['type']}\n{tag}"],
        textposition="top center",
        marker=dict(size=14, color=marker_color, symbol='cube', line=dict(color='#ffffff', width=1))
    ))

# Plot C: Subsea Field Pipelines (Flowline Corridors)
# Pipeline 1: Wellhead 01 to Manifold
fig.add_trace(go.Scatter3d(
    x=[15.0, 50.0], y=[-15.0, 0.0], z=[125.0, 122.0],
    mode='lines', name="Flowline A (Static)",
    line=dict(color='#475569', width=6, dash='solid')
))
# Pipeline 2: Wellhead 02 to Manifold
fig.add_trace(go.Scatter3d(
    x=[15.0, 50.0], y=[15.0, 0.0], z=[124.0, 122.0],
    mode='lines', name="Flowline B (Static)",
    line=dict(color='#475569', width=6, dash='solid')
))
# Pipeline 3: Manifold to FPSO Riser Base
fig.add_trace(go.Scatter3d(
    x=[50.0, 90.0], y=[0.0, 0.0], z=[122.0, 118.0],
    mode='lines', name="Export Pipeline Corridor",
    line=dict(color='#0284c7', width=8, dash='solid')
))

# Plot D: Simulated ROV Operational Inspection Path
# The ROV flies along the Export Pipeline Corridor at a set altitude
path_x = np.linspace(15.0, 85.0, 30)
path_y = np.sin(path_x / 8.0) * 2.5
path_z = np.full(30, 122.0 - rov_altitude)

fig.add_trace(go.Scatter3d(
    x=path_x, y=path_y, z=path_z,
    mode='lines+markers',
    name="ROV Inspection Path",
    marker=dict(size=5, color='#10b981' if gate_status else '#ef4444'),
    line=dict(color='#10b981' if gate_status else '#ef4444', width=4)
))

# Configure 3D View Angles, Labels, and Styles (Decoupled Plotly Layout API)
fig.update_layout(
    margin=dict(l=0, r=0, b=0, t=0),
    height=650,
    scene=dict(
        xaxis=dict(title="UTM X Alignment (m)", backgroundcolor="#0b0f19", gridcolor="#1e293b", showbackground=True),
        yaxis=dict(title="UTM Y Deviation (m)", backgroundcolor="#0b0f19", gridcolor="#1e293b", showbackground=True),
        zaxis=dict(title="True Depth (m)", autorange="reversed", backgroundcolor="#0b0f19", gridcolor="#1e293b", showbackground=True),
        camera=dict(
            eye=dict(x=1.3, y=1.3, z=0.9)  # Isometric overhead cinematic view
        )
    ),
    paper_bgcolor="#0b0f19",
    plot_bgcolor="#0b0f19",
    legend=dict(yanchor="top", y=0.95, xanchor="left", x=0.02, font=dict(color="#94a3b8"))
)

plot_placeholder.plotly_chart(fig, use_container_width=True)
