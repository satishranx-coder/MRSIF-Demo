import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
import random
import math

# --------------------------------------------------------------------
# 1. PAGE AND THEME CONFIGURATION
# --------------------------------------------------------------------
st.set_page_config(
    page_title="MRSIF | Subsea Intelligence Control Panel",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------------------------
# 2. SIDEBAR PANEL CONTROLS
# --------------------------------------------------------------------
st.sidebar.image("https://img.icons8.com/external-flatart-icons-flat-flatarticons/128/external-robotics-artificial-intelligence-flatart-icons-flat-flatarticons.png", width=70)
st.sidebar.title("MRSIF Control Panel")
st.sidebar.markdown("*Marine Robotics Subsea Intelligence Framework*")
st.sidebar.markdown("---")

st.sidebar.subheader("🛠️ Mission Configuration")
asset_type = st.sidebar.selectbox("Target Subsea Asset", ["Subsea Pipeline Alpha", "SPM Mooring Chains", "Hazira FPSO Riser"])
sensor_mode = st.sidebar.radio("Primary Sensor Fusion Array", ["DVL + INS + Sonar (Optimal)", "Sonar Only (Turbid Water Mode)", "DVL Only (Degraded Acoustic Link)"])

st.sidebar.subheader("⚙️ Simulation Settings")
refresh_rate = st.sidebar.slider("Data Stream Frequency (Hz)", 1, 5, 2)
sim_duration = st.sidebar.number_input("Demo Run Time (Seconds)", min_value=10, max_value=300, value=30)

# Initialize Session States to store dynamic history data across iterations
if 'telemetry_history' not in st.session_state:
    st.session_state.telemetry_history = []
if 'anomaly_logs' not in st.session_state:
    st.session_state.anomaly_logs = []

# --------------------------------------------------------------------
# 3. EXECUTIVE SCREEN HEADERS & VALUE METRICS
# --------------------------------------------------------------------
st.title("🤖 MRSIF: Marine Robotics Subsea Intelligence Framework")
st.subheader("Autonomous Inspection Mission Live Simulation Dashboard")
st.markdown("---")

# Row 1: High-level KPI summary cards (Using native st.container with borders)
col1, col2, col3, col4 = st.columns(4)
with col1:
    with st.container(border=True):
        st.metric(label="Edge Autonomy Status", value="ACTIVE", delta="Level 4 Autonomy")
with col2:
    with st.container(border=True):
        st.metric(label="Mission Efficiency Boost", value="+22.4%", delta="Optimized Pathing")
with col3:
    with st.container(border=True):
        st.metric(label="Estimated Vessel Cost Saved", value="$14,200", delta="-18 Hours ROV Time")
with col4:
    with st.container(border=True):
        st.metric(label="Data Compression at Edge", value="94.1%", delta="Reduced Uplink Burden")

st.write("\n")

# Row 2: Layout placeholders for main plots and real-time outputs
chart_col, log_col = st.columns([2, 1])

with chart_col:
    st.subheader("🌐 Real-time 3D Trajectory Mapping & Digital Twin")
    plot_placeholder = st.empty()

with log_col:
    st.subheader("🧠 Core Perception Intelligence Engine Logs")
    battery_placeholder = st.empty()
    log_placeholder = st.empty()

# --------------------------------------------------------------------
# 4. SIMULATION EXECUTION LOOP
# --------------------------------------------------------------------
if st.button("🚀 Start Live Software Demonstration"):
    st.session_state.telemetry_history = []  # Reset historical records
    st.session_state.anomaly_logs = []
    
    # Base baseline parameters for vector coordinates
    x, y, z = 0.0, 0.0, 120.0
    battery = 100.0
    
    steps = int(sim_duration * refresh_rate)
    
    for i in range(steps):
        # 1. Simulate sensor data packet generation with stochastic marine noise
        noise_factor = 0.1 if "Optimal" in sensor_mode else 0.3
        x += 2.0 + random.uniform(-noise_factor, noise_factor)
        y += math.sin(i * 0.2) * 1.5 + random.uniform(-noise_factor, noise_factor)
        z += random.uniform(-0.4, 0.4)
        battery -= (0.05 * refresh_rate)
        
        # 2. Append new coordinates payload into memory
        st.session_state.telemetry_history.append({"X": x, "Y": y, "Z": z})
        df = pd.DataFrame(st.session_state.telemetry_history)
        
        # 3. Simulate deep framework computer vision/anomaly detection logic
        rand_event = random.random()
        timestamp_str = time.strftime("%H:%M:%S")
        
        if rand_event > 0.93:
            st.session_state.anomaly_logs.insert(0, f"⚠️ [{timestamp_str}] CRITICAL ANOMALY: Structural Crack/Fatigue detected on {asset_type}. Confidence: {round(random.uniform(91, 98), 1)}%.")
            st.session_state.anomaly_logs.insert(0, f"🤖 [{timestamp_str}] DECISION CORE: Deviating from pre-planned survey path. Hover mode engaged for close-proximity 3D scanning.")
        elif rand_event < 0.04:
            st.session_state.anomaly_logs.insert(0, f"⚡ [{timestamp_str}] SYSTEM WARNING: High turbidity environment detected. Swapping weights to Sonar Perception profiling.")
            
        # 4. Render 3D Digital Twin visualization tracking space
        fig = go.Figure()
        
        # Draw the target asset track layout line
        pipeline_x = np.linspace(0, max(df["X"]) + 20, 100)
        pipeline_y = np.zeros(100)
        pipeline_z = np.full(100, 122.0)
        fig.add_trace(go.Scatter3d(
            x=pipeline_x, y=pipeline_y, z=pipeline_z,
            mode='lines', name='Target Subsea Asset Corridor',
            line=dict(color='rgba(148, 163, 184, 0.6)', width=6, dash='dash')
        ))
        
        # Draw the actual path navigated by the framework's intelligence tracking systems
        fig.add_trace(go.Scatter3d(
            x=df["X"], y=df["Y"], z=df["Z"],
            mode='lines+markers', name='MRSIF AUV Trajectory',
            marker=dict(size=4, color=df["Z"], colorscale='Viridis', opacity=0.8),
            line=dict(color='#2563eb', width=4)
        ))
        
        # Structure camera viewing perspectives dynamically
       fig.update_layout(
            margin=dict(l=0, r=0, b=0, t=0),
            scene=dict(
                xaxis=dict(title="Inspection Progress (X)", backgroundcolor="#0f172a", showbackground=True),
                yaxis=dict(title="Cross-Track Deviation (Y)", backgroundcolor="#0f172a", showbackground=True),
                zaxis=dict(title="Subsea Depth (Z)", autorange="reversed", backgroundcolor="#0f172a", showbackground=True)
            ),
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
            paper_bgcolor="#0f172a",
            plot_bgcolor="#0f172
            ),
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
            paper_bgcolor="#0f172a",
            plot_bgcolor="#0f172a"
        )
        
        plot_placeholder.plotly_chart(fig, use_container_width=True)
        
        # 5. Push real-time metrics data fields updates to UI dashboard columns
        with battery_placeholder.container():
            b_col1, b_col2 = st.columns(2)
            b_col1.metric("AUV Power Remaining", f"{round(battery, 1)}%")
            b_col2.metric("Current Node (XYZ)", f"{round(x,1)}, {round(y,1)}, {round(z,1)}")
        
        # Update raw processing log view using standard strings (no custom HTML spans)
        if st.session_state.anomaly_logs:
            log_text = "\n\n".join(st.session_state.anomaly_logs[:8])
        else:
            log_text = "Framework executing normal path surveillance routines. No anomalies recorded."
            
        log_placeholder.text_area("Live Events Window", value=log_text, height=320, disabled=True)
        
        time.sleep(1.0 / refresh_rate)
        
    st.success("🏁 Demonstration Mission simulation successfully completed.")
