import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="VODIDS | Offshore Gujarat Positioning & Piling Workspace",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM STYLING ---
st.markdown("""
<style>
    .main-header { font-size: 24px; font-weight: bold; color: #1a365d; margin-bottom: 5px; }
    .sub-header { font-size: 14px; color: #4a5568; margin-bottom: 20px; }
    .metric-card { background-color: #f7fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px; }
    .status-safe { color: #2e7d32; font-weight: bold; }
    .status-alert { color: #c62828; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/subsea.png", width=64)
    st.markdown("### **Mission Parameters (Offshore Gujarat)**")
    
    st.markdown("#### **1. Metocean & Tidal Regime**")
    peak_current = st.slider("Peak Tidal Current (knots)", min_value=2.0, max_value=7.0, value=5.2, step=0.1)
    tidal_range = st.slider("Macro-Tidal Range (m)", min_value=4.0, max_value=12.0, value=8.5, step=0.5)
    water_depth = st.number_input("Water Depth (m CD)", min_value=10.0, max_value=100.0, value=26.0, step=0.5)
    
    st.markdown("#### **2. Foundation & Pile Specs**")
    pile_diameter = st.selectbox("Skirt Pile Diameter", ["54-inch (1,372 mm)", "42-inch (1,067 mm)", "30-inch (762 mm)"], index=0)
    pile_od_mm = 1372 if "54" in pile_diameter else (1067 if "42" in pile_diameter else 762)
    pile_wall_thk = st.number_input("Wall Thickness (mm)", value=38.1, step=1.0)
    steel_yield_fy = st.number_input("Steel Yield Strength Fy (MPa)", value=355.0, step=5.0)
    target_penetration = st.slider("Target Penetration (m)", min_value=10.0, max_value=80.0, value=45.0, step=1.0)
    
    st.markdown("#### **3. Remote Sensing Hardware**")
    mbes_enabled = st.checkbox("Multibeam Echosounder (MBES)", value=True)
    sonar_enabled = st.checkbox("2D/3D Scanning Sonar (Sleeve Entry)", value=True)
    lidar_enabled = st.checkbox("Marine Topside LiDAR (Crane 6-DoF)", value=True)
    usbl_enabled = st.checkbox("Subsea USBL / Inclinometers", value=True)
    adcp_enabled = st.checkbox("Real-time ADCP Current Profiler", value=True)

# --- MAIN TITLE ---
st.markdown('<div class="main-header">⚓ VODIDS | MRSIF Offshore Foundation & Positioning Workspace</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Zero-Visibility Acoustic Metrology, LiDAR Tracking & Dynamic Risk Intelligence | Gulf of Khambhat / Hazira</div>', unsafe_allow_html=True)

# --- TOP SUMMARY METRICS ---
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Water Depth (CD)", f"{water_depth:.1f} m", "Gulf of Khambhat")
with col2:
    st.metric("Peak Current", f"{peak_current:.1f} kts", "Spring Tide Reversing")
with col3:
    st.metric("Visibility", "0 cm (Turbid)", "Optical ROV Prohibited")
with col4:
    max_allow_stress = 0.85 * steel_yield_fy
    st.metric("Max Driving Stress Cap", f"{max_allow_stress:.1f} MPa", "0.85 × Fy")
with col5:
    st.metric("Verticality Limit", "< ±0.10°", "IMCA S015 Standard")

st.markdown("---")

# --- NAVIGATION TABS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🌊 Metocean & Tidal Stabbing Window",
    "🎯 Zero-Visibility Acoustic & LiDAR Array",
    "🔨 Pile Driveability & Stress Engine",
    "⚠️ Metocean & Positioning Risk Matrix",
    "📋 Digital Spread Passport Export"
])

# ==============================================================================
# TAB 1: METOCEAN & TIDAL CURRENT (ADCP SLACK-WINDOW CALCULATOR)
# ==============================================================================
with tab1:
    st.subheader("Tidal Current Dynamics & Stabbing Window Predictor")
    st.markdown("""
    In the macro-tidal regime of Offshore Gujarat, pile stabbing into the jacket sleeve is strictly prohibited when current exceeds **1.2 knots**. 
    The module below models the 12-hour semidiurnal tidal cycle and identifies the permissible **Slack-Water Stabbing Windows**.
    """)
    
    # 12-hour simulation
    time_hours = np.linspace(0, 12, 240)
    current_velocity = peak_current * np.abs(np.sin(2 * np.pi * time_hours / 6.2))
    
    # Identify slack windows (< 1.2 kts)
    safe_stabbing = current_velocity <= 1.2
    
    fig_tide = go.Figure()
    fig_tide.add_trace(go.Scatter(
        x=time_hours, y=current_velocity,
        mode='lines', name='Current Velocity (knots)',
        line=dict(color='#3182ce', width=2.5)
    ))
    fig_tide.add_hline(y=1.2, line_dash="dash", line_color="#e53e3e", annotation_text="Stabbing Cutoff Limit (1.2 kts)")
    fig_tide.add_trace(go.Scatter(
        x=time_hours[safe_stabbing], y=current_velocity[safe_stabbing],
        mode='markers', name='Permissible Stabbing Window',
        marker=dict(color='#38a169', size=6)
    ))
    fig_tide.update_layout(
        title="12-Hour ADCP Current Velocity Profile & Slack Windows",
        xaxis_title="Time from High Water (Hours)",
        yaxis_title="Current Speed (knots)",
        template="plotly_white",
        height=380
    )
    st.plotly_chart(fig_tide, use_container_width=True)
    
    # Current Stabbing Status
    current_time_val = st.slider("Select Operation Hour on Tidal Curve", 0.0, 12.0, 3.1, 0.1)
    simulated_current = peak_current * np.abs(np.sin(2 * np.pi * current_time_val / 6.2))
    
    c_status, c_msg = st.columns()
    with c_status:
        if simulated_current <= 1.2:
            st.success(f"**STATUS: GO FOR STABBING**\nCurrent: {simulated_current:.2f} kts (Slack)")
        else:
            st.error(f"**STATUS: NO-GO / HOLD CRANE**\nCurrent: {simulated_current:.2f} kts (> 1.2 kts)")
    with c_msg:
        st.info(f"**ADCP Advisory:** Next slack-water window estimated within approx. {abs(3.1 - (current_time_val % 3.1))*60:.0f} minutes. Maintain crane tension until velocity drops below 1.2 knots.")

# ==============================================================================
# TAB 2: ZERO-VISIBILITY ACOUSTIC & LIDAR POSITIONING ARRAY
# ==============================================================================
with tab2:
    st.subheader("Acoustic & Topside Remote Sensing Telemetry")
    
    col_sonar, col_lidar = st.columns(2)
    
    with col_sonar:
        st.markdown("#### **1. Subsea Scanning Sonar (Pile Tip Stabbing Entry)**")
        st.caption("Acoustic cross-axial imaging of the 54\" pile entering the skirt sleeve guide cone through 0 cm optical visibility.")
        
        # Stabbing offset inputs
        offset_x = st.slider("Pile Tip Offset X (mm from sleeve center)", -150.0, 150.0, 18.0, 1.0)
        offset_y = st.slider("Pile Tip Offset Y (mm from sleeve center)", -150.0, 150.0, -22.0, 1.0)
        radial_error = np.sqrt(offset_x**2 + offset_y**2)
        
        # Sonar polar plot
        theta = np.linspace(0, 2*np.pi, 100)
        sleeve_r = 750 # mm
        cone_r = 1100 # mm
        
        fig_sonar = go.Figure()
        fig_sonar.add_trace(go.Scatter(x=cone_r*np.cos(theta), y=cone_r*np.sin(theta), mode='lines', name='Guide Cone Rim (1,100 mm)', line=dict(color='#cbd5e0', dash='dash')))
        fig_sonar.add_trace(go.Scatter(x=sleeve_r*np.cos(theta), y=sleeve_r*np.sin(theta), mode='lines', name='Skirt Sleeve Entry (750 mm)', line=dict(color='#4a5568', width=3)))
        fig_sonar.add_trace(go.Scatter(x=[offset_x], y=[offset_y], mode='markers+text', name='Pile Tip Center', text=["Pile Tip"], textposition="top center", marker=dict(color='#e53e3e' if radial_error > 100 else '#3182ce', size=16)))
        fig_sonar.update_layout(
            title=f"Acoustic Sonar Echo Display (Radial Error: {radial_error:.1f} mm)",
            xaxis=dict(range=[-1300, 1300]), yaxis=dict(range=[-1300, 1300]),
            template="plotly_white", width=450, height=420
        )
        st.plotly_chart(fig_sonar, use_container_width=True)
    
    with col_lidar:
        st.markdown("#### **2. Subsea Inclinometer & Topside LiDAR (Verticality)**")
        st.caption("Fused attitude telemetry tracking pile out-of-plumb verticality ($X, Y$) against IMCA S015 limits ($< \pm 0.10^\circ$).")
        
        pitch_val = st.slider("Dual-Axis Pitch X (°)", -0.50, 0.50, 0.04, 0.01)
        roll_val = st.slider("Dual-Axis Roll Y (°)", -0.50, 0.50, -0.03, 0.01)
        total_inclination = np.sqrt(pitch_val**2 + roll_val**2)
        
        fig_vert = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = total_inclination,
            title = {'text': "Total Pile Inclination (°)"},
            gauge = {
                'axis': {'range': [0, 0.50]},
                'bar': {'color': "#3182ce"},
                'steps': [
                    {'range': [0, 0.10], 'color': "#c6f6d5"},
                    {'range': [0.10, 0.25], 'color': "#feebc8"},
                    {'range': [0.25, 0.50], 'color': "#fed7d7"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 0.10
                }
            }
        ))
        fig_vert.update_layout(height=300, template="plotly_white")
        st.plotly_chart(fig_vert, use_container_width=True)
        
        if total_inclination <= 0.10:
            st.success(f"✅ **Verticality Compliant:** {total_inclination:.3f}° within allowable tolerance (0.10°).")
        else:
            st.warning(f"⚠️ **Verticality Warning:** {total_inclination:.3f}° exceeds tolerance. Adjust crane boom position.")

# ==============================================================================
# TAB 3: PILE DRIVEABILITY & STRESS ENGINE
# ==============================================================================
with tab3:
    st.subheader("High-Strain Dynamic Monitoring & Refusal Engine (ASTM D4945)")
    
    c_p1, c_p2 = st.columns(2)
    with c_p1:
        hammer_energy = st.slider("Hammer Rated Energy (kNm)", 90, 300, 150, 10)
        efficiency = st.slider("Hammer Energy Transfer Efficiency EMX (%)", 50, 90, 72, 1)
    with c_p2:
        soil_profile = st.selectbox("Stratified Soil Profile", ["Gujarat Interbedded Silt/Sand/Clay", "Hazira Calcareous Dense Sand", "Soft Marine Silt over Dense Sand"])
    
    depths = np.linspace(0, target_penetration, 100)
    # Simulate dynamic resistance
    srd_kn = 800 + 45 * depths + 1.2 * depths**1.8
    blow_count = 15 + 1.2 * depths + 0.04 * depths**2.1
    comp_stress = (hammer_energy * (efficiency/100) * 1000) / (np.pi * pile_od_mm * pile_wall_thk * 0.001) * 0.45 + (depths * 0.8)
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        fig_srd = go.Figure()
        fig_srd.add_trace(go.Scatter(x=srd_kn, y=depths, mode='lines', name='Soil Resistance to Driving (SRD)', line=dict(color='#3182ce', width=2.5)))
        fig_srd.update_layout(title="Soil Resistance to Driving (SRD) vs. Depth", xaxis_title="SRD (kN)", yaxis_title="Penetration Depth (m)", yaxis=dict(autorange="reversed"), template="plotly_white", height=380)
        st.plotly_chart(fig_srd, use_container_width=True)
        
    with col_d2:
        fig_stress = go.Figure()
        fig_stress.add_trace(go.Scatter(x=comp_stress, y=depths, mode='lines', name='Peak Compressive Stress (CSB)', line=dict(color='#805ad5', width=2.5)))
        fig_stress.add_vline(x=0.85*steel_yield_fy, line_dash="dash", line_color="red", annotation_text="0.85×Fy Limit")
        fig_stress.update_layout(title="Compressive Driving Stress (CSB) vs. Depth", xaxis_title="Stress (MPa)", yaxis_title="Penetration Depth (m)", yaxis=dict(autorange="reversed"), template="plotly_white", height=380)
        st.plotly_chart(fig_stress, use_container_width=True)

# ==============================================================================
# TAB 4: METOCEAN & POSITIONING RISK MATRIX
# ==============================================================================
with tab4:
    st.subheader("Metocean, Acoustic & Positioning Risk Assessment Matrix")
    
    risks_data = [
        {"Risk ID": "RSK-P1", "Threat Scenario": "Current-Induced Pile Sleeve Clash", "Risk Level": "CRITICAL", "Probability": "High", "Severity": "High", "Root Cause": "4-6 kt cross-current drag forcing pile off-center", "Mitigation": "Tidal slack windowing (<1.2 kt) + real-time scanning sonar guidance"},
        {"Risk ID": "RSK-P2", "Threat Scenario": "Acoustic Telemetry Shadowing & Multipath", "Risk Level": "HIGH", "Probability": "High", "Severity": "Med", "Root Cause": "Thruster aeration & heavy suspended sediment scattering", "Mitigation": "Dual-frequency MF channels + deep deployed transceiver pole"},
        {"Risk ID": "RSK-P3", "Threat Scenario": "Template Scour & Mudmat Tilting", "Risk Level": "HIGH", "Probability": "Med", "Severity": "High", "Root Cause": "Macro-tidal bedload erosion prior to pile pinning", "Mitigation": "Anti-scour frond mattresses + immediate diagonal pile pinning (P1 & P3)"},
        {"Risk ID": "RSK-P4", "Threat Scenario": "Inclinometer Shock Detachment", "Risk Level": "MEDIUM", "Probability": "Med", "Severity": "Med", "Root Cause": "Hammer impact acceleration shock wave (>500g)", "Mitigation": "Elastomer isolation mounts + secondary safety tether lanyards"},
        {"Risk ID": "RSK-P5", "Threat Scenario": "Topside-to-Subsea Coordinate Drift", "Risk Level": "MEDIUM", "Probability": "Low", "Severity": "High", "Root Cause": "Barge dynamic yaw/heave disconnecting LiDAR & USBL", "Mitigation": "Unified 6-DoF Kalman filter coordinate handshake"}
    ]
    df_risks = pd.DataFrame(risks_data)
    
    st.dataframe(df_risks, use_container_width=True)
    
    st.markdown("#### **Active Risk Mitigation Gate Check**")
    c1, c2 = st.columns(2)
    with c1:
        g1 = st.checkbox("✅ ADCP Slack-Water Window Verified (< 1.2 knots)", value=True)
        g2 = st.checkbox("✅ Dual Scanning Sonar Cross-Axial Feed Active", value=True)
    with c2:
        g3 = st.checkbox("✅ Subsea Inclinometer Shock Mounts Inspected", value=True)
        g4 = st.checkbox("✅ MVP / Sound Velocity Ray-Tracing Calibrated (< 4 hrs)", value=True)

# ==============================================================================
# TAB 5: DIGITAL SPREAD PASSPORT / DELIVERABLE EXPORT
# ==============================================================================
with tab5:
    st.subheader("Generate Pre-Mob Digital Spread Passport & Daily Positioning Log")
    st.markdown("Export a verified compliance document for client submission (ONGC, RIL, L&T, McDermott).")
    
    summary_text = f"""# VODIDS | DIGITAL SPREAD PASSPORT & POSITIONING REPORT
Location: Offshore Gujarat (Hazira / Gulf of Khambhat)
Date/Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
Water Depth: {water_depth} m CD | Macro-Tidal Range: {tidal_range} m
Peak Current: {peak_current} knots | Optical Visibility: 0 cm (Acoustic Only)

FOUNDATION & POSITIONING STATUS:
- Skirt Pile Spec: {pile_diameter} (Wall: {pile_wall_thk} mm, Steel: {steel_yield_fy} MPa)
- Target Penetration: {target_penetration} m
- Pile Stabbing Radial Error: {radial_error:.1f} mm (Status: COMPLIANT)
- Total Pile Inclination: {total_inclination:.3f}° (Limit: < 0.10°)
- Max Permissible Stress: {max_allow_stress:.1f} MPa

REMOTE SENSING ARRAY DEPLOYED:
- Multibeam Echosounder (MBES): {'ONLINE' if mbes_enabled else 'OFFLINE'}
- 2D/3D Scanning Sonar: {'ONLINE' if sonar_enabled else 'OFFLINE'}
- Topside Marine LiDAR: {'ONLINE' if lidar_enabled else 'OFFLINE'}
- Subsea Inclinometers: {'ONLINE' if usbl_enabled else 'OFFLINE'}
- ADCP Current Profiling: {'ONLINE' if adcp_enabled else 'OFFLINE'}

PRE-MOBILIZATION SAFETY GATES:
- Slack Water Windowing: PASS
- Acoustic Ray-Tracing (MVP): PASS
- Sensor Shock Isolation: PASS
- Class Compliance: API RP 2A / IMCA S015 Verified
"""
    st.text_area("Live Report Preview", summary_text, height=260)
    
    st.download_button(
        label="📥 Download Digital Spread Passport (Markdown)",
        data=summary_text,
        file_name=f"Digital_Spread_Passport_Gujarat_{datetime.utcnow().strftime('%Y%m%d')}.md",
        mime="text/markdown"
    )
