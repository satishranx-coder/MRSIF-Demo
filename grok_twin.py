import streamlit as st
import time

# Page config
st.set_page_config(
    page_title="MRSIF-ROV Tooling & Intervention Mission Assurance",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom dark theme CSS
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    .metric-card {
        background-color: #1a1f2e;
        padding: 16px;
        border-radius: 10px;
        border: 1px solid #2d3748;
        text-align: center;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #63b3ed;
    }
    .metric-label {
        font-size: 13px;
        color: #a0aec0;
        margin-top: 4px;
    }
    .warning-box {
        background-color: #744210;
        padding: 12px 16px;
        border-radius: 8px;
        border-left: 5px solid #ed8936;
        color: #fefcbf;
        margin-bottom: 16px;
        font-weight: 500;
    }
    .status-ready {
        color: #68d391;
        font-weight: bold;
    }
    .status-degraded {
        color: #ed8936;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "current_mode" not in st.session_state:
    st.session_state.current_mode = "Normal"

# ====================== HEADER ======================
st.markdown("### MRSIF-ROV Tooling & Intervention Mission Assurance")
st.caption("VODIS-governed ROV tooling & intervention · CFIHOS asset context · OSDU operational context")

# ====================== SIMULATION CONTROLS ======================
st.markdown("#### Simulation Controls")
col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])

with col_btn1:
    if st.button("🌊 Simulate Lateral Current", use_container_width=True):
        st.session_state.current_mode = "Lateral"
        st.rerun()

with col_btn2:
    if st.button("↺ Reset to Normal", use_container_width=True):
        st.session_state.current_mode = "Normal"
        st.rerun()

with col_btn3:
    mode_text = "Current Mode: **LATERAL DISTURBANCE**" if st.session_state.current_mode == "Lateral" else "Current Mode: **Normal (Forward)**"
    st.markdown(mode_text)

# ====================== DYNAMIC VALUES ======================
if st.session_state.current_mode == "Lateral":
    current_val = "1.8 kts (Lateral)"
    localization = 81
    point_cloud = 89
    target_error = 7.4
    alignment = 5.8
    tool_clearance = 48
    hydraulic = 3500
    ready_status = "DEGRADED"
    status_class = "status-degraded"
    show_warning = True
else:
    current_val = "1.2 kts (Forward)"
    localization = 94
    point_cloud = 96
    target_error = 3.2
    alignment = 2.4
    tool_clearance = 82
    hydraulic = 3500
    ready_status = "READY TO ADVANCE"
    status_class = "status-ready"
    show_warning = False

# ====================== WARNING ======================
if show_warning:
    st.markdown("""
    <div class="warning-box">
        ⚠️ Lateral current disturbance detected – station keeping degraded. Do not advance until conditions stabilize.
    </div>
    """, unsafe_allow_html=True)

# ====================== METRICS ROW ======================
st.markdown("#### Live Operational Metrics")

m1, m2, m3, m4, m5, m6, m7 = st.columns(7)

with m1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{current_val}</div>
        <div class="metric-label">Current</div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{localization}%</div>
        <div class="metric-label">Localization</div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{point_cloud}%</div>
        <div class="metric-label">Point Cloud</div>
    </div>
    """, unsafe_allow_html=True)

with m4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{target_error}%</div>
        <div class="metric-label">ROV / Target Error</div>
    </div>
    """, unsafe_allow_html=True)

with m5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{alignment}°</div>
        <div class="metric-label">TCP / TEP Alignment</div>
    </div>
    """, unsafe_allow_html=True)

with m6:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{tool_clearance} mm</div>
        <div class="metric-label">Tool Clearance</div>
    </div>
    """, unsafe_allow_html=True)

with m7:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{hydraulic} psi</div>
        <div class="metric-label">Hydraulic Supply</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# ====================== STATUS ======================
st.markdown(f"**Mission Status:** <span class='{status_class}'>{ready_status}</span>", unsafe_allow_html=True)

# ====================== MISSION STAGES ======================
st.markdown("---")
st.markdown("#### Mission Process – 600 m Hot Stab Valve Intervention")

stages = [
    "01 Mission Setup",
    "02 Approach Worksite",
    "03 Target Localization",
    "04 StationKeep Established",
    "05 Acquire Hot Stab",
    "06 TCP → TEP Alignment",
    "07 Hot Stab Insertion",
    "08 Hydraulic Function / Valve Open"
]

cols = st.columns(4)
for i, stage in enumerate(stages):
    with cols[i % 4]:
        if i == 0:
            st.success(f"{stage}  •  ACTIVE")
        else:
            st.info(f"{stage}  •  PENDING")

st.write("")
st.caption("MRSIF evidence rule: validate only what the deployed system can prove. Geometry, localization, vehicle capability, interface compatibility and verified mission outcome are accepted as evidence.")
st.caption("Simulated Demonstration • Created for technical evaluation")
