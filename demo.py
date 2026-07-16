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

# Enforce clean custom styling for a modern corporate dashboard look
st.markdown("""
    <style>
    .metric-box {
        background-color: #1e293b;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #334155;
    }
    .status-normal { color: #10b981; font-weight: bold; }
    .status-anomaly { color: #ef4444; font-weight: bold; }
    .status-alert { color: #f59e0b; font-weight: bold; }
    </style>
""", unsafe_allowed_html=True)

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

# Row 1: High-level KPI summary cards for investor impact
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown('<div class="metric-box">', unsafe_allowed_html=True)
    st.metric(label="Edge Autonomy Status", value="ACTIVE", delta="Level 4 Autonomy")
    st.markdown('</div>', unsafe_allowed_html=True)
with col2:
    st.markdown('<div class="metric-box">', unsafe_allowed_html=True)
    st.metric(label="Mission Efficiency Boost", value="+22.4%", delta="Optimized Pathing")
    st.markdown('</div>', unsafe_allowed_html=True)
with col3:
    st.markdown('<div class="metric-box">', unsafe_allowed_html=True)
    st.metric(label="Estimated Vessel Cost Saved", value="$14,200", delta="-18 Hours Tethered ROV Time")
    st.markdown('</div>', unsafe_allowed_html=True)
with col4:
    st.markdown('<div class="metric-box">', unsafe_allowed_html=True)
    st.metric(label="Data Compression at Edge", value="94.1%", delta="Reduced Acoustic Uplink Burden")
    st.markdown('</div>', unsafe_allowed_html=True)

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
            log_entry = f"⚠️ [{timestamp_str}] <span class='status-anomaly'>CRITICAL ANOMALY:</span> Structural Crack/Fatigue detected on {asset_type}. Confidence: {round(random.uniform(91, 98),1)}%."
            st.session_state.anomaly_logs.insert(0, log_entry)
            st.session_state.anomaly_logs.insert(0, f"🤖 [{timestamp_str}] <span class='status-alert'>DECISION CORE:</span> Deviating from pre-planned survey path. Hover mode engaged for close-proximity 3D scanning.")
        elif rand_event < 0.04:
            log_entry = f"⚡ [{timestamp_str}] <span class='status-alert'>SYSTEM WARNING:</span> High turbidity environment detected. Swapping weights to Sonar Perception profiling."
            st.session_state.anomaly_logs.insert(0, log_entry)
            
        # 4. Render 3D Digital Twin visualization tracking space
        fig = go.Figure()
        
        # Draw the target asset track layout line (e.g. simulated seafloor pipeline trajectory)
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
                xaxis_title="Inspection Progress (X)",
                yaxis_title="Cross-Track Deviation (Y)",
                zaxis_title="Subsea Depth (Z)",
                zaxis=dict(autorange="reversed"), # Depth increases downward
                backgroundcolor="#0f172a"
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
        
        # Update raw processing log view
        log_html = "".join([f"<p style='margin-bottom:8px;'>{log}</p>" for log in st.session_state.anomaly_logs[:8]])
        if not log_html:
            log_html = "<p style='color:#64748b;'>Framework executing normal path surveillance routines. No anomalies recorded.</p>"
            
        log_placeholder.markdown(f"""
            <div style="background-color: #0f172a; padding: 15px; border-radius: 8px; border: 1px solid #334155; height: 320px; overflow-y: auto; font-family: monospace; font-size: 13px;">
                {log_html}
            </div>
        """, unsafe_allowed_html=True)
        
        time.sleep(1.0 / refresh_rate)
        
    st.success("🏁 Demonstration Mission simulation successfully completed.")
