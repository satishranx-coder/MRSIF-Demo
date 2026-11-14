import streamlit as st
import pandas as pd
import re
import random

Page Configuration

st.set_page_config(
page_title="Offshore CV Scrutiny Matrix | Hydro/Geophys & Seismic",
page_icon="⚡",
layout="wide",
initial_sidebar_state="expanded"
)

Custom CSS styling for marine/industrial theme

st.markdown("""

.main {
background-color: #0d1117;
color: #e6edf3;
}
.stSidebar {
background-color: #161b22;
}
.metric-card {
background: #21262d;
border: 1px solid #30363d;
padding: 20px;
border-radius: 10px;
text-align: center;
box-shadow: 0 4px 6px rgba(0,0,0,0.3);
}
.badge {
display: inline-block;
padding: 4px 10px;
font-size: 0.85rem;
font-weight: 600;
border-radius: 12px;
margin: 2px;
}
.badge-tier1 { background-color: #1f6feb; color: white; }
.badge-spec { background-color: #238636; color: white; }
.badge-legacy { background-color: #da3633; color: white; }

""", unsafe_allow_html=True)

Application Header

st.title("⚓ Offshore Personnel Skill Expertise & Competency Matrix")
st.markdown("Automated CV Scrutiny & Demand Ranking for Hydrography, Geophysics, Seismic, and Oceanographic Applications.")

Sidebar Controls

st.sidebar.header("📁 Recruitment Portal")
uploaded_file = st.sidebar.file_uploader("Upload Candidate CV (PDF / DOCX)", type=["pdf", "docx", "txt"])

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Scoring Weights Configuration")
weight_exp = st.sidebar.slider("Experience Depth Weight", 1.0, 5.0, 2.5)
weight_soft = st.sidebar.slider("Software Recency Weight", 1.0, 5.0, 2.0)
weight_spec = st.sidebar.slider("Specialist Multiplier", 0.5, 2.0, 1.0)

Mock Parser Engine Function for Demonstration

def parse_cv_mock(filename):
# In production, this would use PyPDF2 / pdfplumber + spaCy NER or Regex
# Returning structured mock extraction based on file name or default high-end profile
text_lower = filename.lower()

if "junior" in text_lower or "entry" in text_lower:
    return {
        "name": "Alex Mercer (Junior Surveyor)",
        "discipline": "Hydrography & Bathymetry",
        "experience_years": 2.5,
        "software_tier1": ["QINSy", "Caris HIPS & SIPS (Legacy)"],
        "software_legacy": ["HydroPro"],
        "specialists": ["[USBL-CAL]"],
        "rank": 4,
        "tier": "Moderate Demand / Qualified Operator"
    }
elif "expert" in text_lower or "lead" in text_lower or "chief" in text_lower:
    return {
        "name": "Capt. Marcus Vance (Chief Surveyor / LBL Specialist)",
        "discipline": "Precision Acoustics & Deepwater Metrology",
        "experience_years": 14.0,
        "software_tier1": ["QINSy", "SonarWiz", "Fusion 2", "AutoCAD Civil 3D", "UXO Bentley"],
        "software_legacy": ["WinFrog"],
        "specialists": ["[SPARSE-LBL]", "[USBL-CAL]", "[INS-DVL-INTEG]", "[SUBSEA-METROLOGY]", "[CFIHOS-COMPLIANT]"],
        "rank": 10,
        "tier": "Maximum Demand / Elite Subject Matter Expert"
    }
else:
    # Standard Advanced Profile
    return {
        "name": "Elena Rostova",
        "discipline": "Geophysics & Seabed Mapping",
        "experience_years": 8.5,
        "software_tier1": ["SonarWiz", "QINSy", "Caris HIPS & SIPS", "AutoCAD Civil 3D"],
        "software_legacy": ["Chesapeake SonarWeb"],
        "specialists": ["[MBES-CAL-ATEX]", "[SBP-CHIRP]", "[CONST-SUPPORT]", "[ROV-IRM-VIDEO]"],
        "rank": 9,
        "tier": "Advanced Specialist / High Demand"
    }


Main Panel Workflow

if uploaded_file is not None:
with st.spinner("Analyzing CV text, extracting software versions, and verifying specialist tags..."):
# Simulate parsing delay
import time
time.sleep(1.2)

    data = parse_cv_mock(uploaded_file.name)
    
    # Display Candidate Overview
    st.success(f"Successfully processed CV: **{uploaded_file.name}**")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <h4>Candidate Rank</h4>
                <h1 style="color: #58a6ff; margin:0;">{data['rank']} / 10</h1>
                <p style="font-size: 0.8rem; color: #8b949e; margin-top:5px;">Market Demand Score</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <h4>Active Experience</h4>
                <h1 style="color: #3fb950; margin:0;">{data['experience_years']} Yrs</h1>
                <p style="font-size: 0.8rem; color: #8b949e; margin-top:5px;">Offshore Acquisition/QC</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <h4>Software Suites</h4>
                <h1 style="color: #d29922; margin:0;">{len(data['software_tier1']) + len(data['software_legacy'])}</h1>
                <p style="font-size: 0.8rem; color: #8b949e; margin-top:5px;">Identified Packages</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown(f"""
            <div class="metric-card">
                <h4>Specialist Tags</h4>
                <h1 style="color: #bc8cff; margin:0;">{len(data['specialists'])}</h1>
                <p style="font-size: 0.8rem; color: #8b949e; margin-top:5px;">Niche Competencies</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    # Detailed Breakdown Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Competency Breakdown", "💻 Software & Recency Index", "🏷️ Specialist Tags & Certifications"])
    
    with tab1:
        st.subheader(f"Evaluation Profile: {data['name']}")
        st.write(f"**Primary Discipline:** {data['discipline']}")
        st.write(f"**Calculated Tier:** `{data['tier']}`")
        
        st.markdown("### Scoring Criteria Breakdown")
        progress_exp = min(data['experience_years'] / 15.0, 1.0)
        st.progress(progress_exp, text=f"Experience Depth ({data['experience_years']} Years)")
        
        progress_soft = len(data['software_tier1']) / 5.0
        st.progress(progress_soft, text=f"Current Market Software Currency ({len(data['software_tier1'])} Tier-1 packages)")
        
        progress_spec = len(data['specialists']) / 5.0
        st.progress(progress_spec, text=f"Specialist Tag Weight ({len(data['specialists'])} Niche Tags)")

    with tab2:
        st.subheader("Software Portfolio & Market Alignment")
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("#### ✅ Current Market Standard (Tier 1)")
            for sw in data['software_tier1']:
                st.markdown(f"<span class='badge badge-tier1'>{sw}</span>", unsafe_allow_html=True)
        with col_b:
            st.markdown("#### ⚠️ Legacy / Older Packages")
            if data['software_legacy']:
                for sw in data['software_legacy']:
                    st.markdown(f"<span class='badge badge-legacy'>{sw}</span>", unsafe_allow_html=True)
            else:
                st.info("No legacy software flagged in CV.")

    with tab3:
        st.subheader("Identified Domain Specialist Tags")
        st.markdown("The following subsea operational and engineering tags were extracted from the candidate's project history:")
        
        for spec in data['specialists']:
            st.markdown(f"<span class='badge badge-spec' style='font-size: 1rem; padding: 8px 15px;'>{spec}</span>", unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### Recruiter Action & Recommendation")
        if data['rank'] >= 8:
            st.success("**Recommendation:** **FAST-TRACK INTERVIEW.** This candidate possesses elite technical capabilities and current-generation software fluency. Recommended for immediate client submission.")
        elif data['rank'] >= 5:
            st.warning("**Recommendation:** **MID-LEVEL DEPLOYMENT.** Solid candidate suitable for standard acquisition or routine processing tasks under senior supervision.")
        else:
            st.error("**Recommendation:** **REVIEW REQUIRED.** Candidate relies heavily on legacy packages or has limited active offshore tenure.")


else:
# Landing state when no file is uploaded
st.info("👈 Please upload a candidate CV using the sidebar file uploader to generate the automated competency matrix and demand ranking.")

st.markdown("### 🌟 Example Pre-configured Scenarios for Testing")
st.write("You can test the parsing engine behavior by uploading files with specific naming conventions:")
st.markdown("- Upload a file containing `expert` or `chief` in the filename to test an elite **Rank 10 / Sparse LBL Specialist** profile.")
st.markdown("- Upload a file containing `junior` to test an entry-level **Rank 4** profile.")
st.markdown("- Upload any other file name to test an advanced **Rank 9 / Geophysics & Seabed Mapping** profile.")
