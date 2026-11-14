import streamlit as st
import re
import pandas as pd
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="Ruvira Offshore - CV Scrutiny & Competency Matrix",
    page_icon="⚓",
    layout="wide"
)

# Custom Styling & Branding Header
st.markdown("""
    <style>
    .logo-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: linear-gradient(90deg, #0F2537 0%, #1E3A5F 100%);
        padding: 20px 30px;
        border-radius: 10px;
        color: white;
        margin-bottom: 25px;
    }
    </style>
    <div class="logo-container">
        <div>
            <h1 style="margin:0; font-size: 26px; color: #FFFFFF;">⚓ RUVIRA OFFSHORE</h1>
            <p style="margin:0; font-size: 14px; color: #CBD5E1;">Global Marine Robotics, Hydrography & Subsea Engineering Recruitment Portal</p>
        </div>
        <div style="text-align: right; font-size: 13px; color: #94A3B8;">
            <b>Matrix Version:</b> v2.4 (Market-Demand Adaptive)<br>
            <b>Date:</b> """ + datetime.now().strftime("%B %d, %Y") + """
        </div>
    </div>
""", unsafe_allow_html=True)

# Helper function to extract text from PDF
def extract_pdf_text(uploaded_file):
    try:
        import pypdf
        reader = pypdf.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception:
        return uploaded_file.getvalue().decode("latin-1", errors="ignore")

# Role Requirements Definition & Weighting Rules
ROLE_CRITERIA = {
    "Senior LBL / Subsea Positioning Engineer": {
        "required_tags": ["SPARSE-LBL", "USBL-CAL", "INS-DVL-INTEG"],
        "required_software": ["qinsy", "fusion 2", "eiva", "navisuite"],
        "min_exp": 8,
        "weight_multiplier": 1.5
    },
    "Hydrographic & Geophysical Surveyor": {
        "required_tags": ["MBES-CAL-ATEX", "SBP-CHIRP", "SSS-HIGHRES"],
        "required_software": ["qinsy", "sonarwiz", "hypack", "qimera", "caris"],
        "min_exp": 4,
        "weight_multiplier": 1.2
    },
    "Offshore Construction Support Surveyor": {
        "required_tags": ["CONST-SUPPORT", "ROV-IRM-VIDEO", "SUBSEA-METROLOGY"],
        "required_software": ["eiva", "navipac", "autocad", "beamworx"],
        "min_exp": 5,
        "weight_multiplier": 1.3
    },
    "Uncrewed Marine Systems (USV/AUV) Operator": {
        "required_tags": ["USV-COMMAND", "AUV-OPS", "AMPHIBIOUS-CRAWLER"],
        "required_software": ["qinsy", "ros 2", "python", "navis"],
        "min_exp": 3,
        "weight_multiplier": 1.4
    }
}

TIER_1_SOFTWARE = [
    "qinsy", "eiva", "navisuite", "caris", "hips", "sips", 
    "sonarwiz", "kingdom", "qimera", "starfix", "fusion 2", 
    "autocad civil 3d", "microstation", "uxo bentley", "opensite", "beamworx", "navaq"
]

LEGACY_SOFTWARE = [
    "hydropro", "triton isis", "sonarweb", "winfrog", "starfix 3"
]

SPECIALIST_TAGS = {
    "SPARSE-LBL": ["sparse lbl", "long baseline", "lbl calibration", "transponder network", "fusion 2"],
    "USBL-CAL": ["usbl", "ultra-short baseline", "ray-tracing", "acoustic telemetry", "ranger 2"],
    "INS-DVL-INTEG": ["lodestar", "syrinx", "phins", "dvl", "inertial navigation"],
    "USV-COMMAND": ["wavebot", "c-worker", "drix", "uncrewed surface vehicle", "usv"],
    "AUV-OPS": ["auv", "autonomous underwater vehicle", "mission planning"],
    "MBES-CAL-ATEX": ["multibeam", "mbes", "patch test", "backscatter calibration", "norbit"],
    "SBP-CHIRP": ["sub-bottom", "chirp", "shallow hazards", "stratigraphy"],
    "MAG-PIPELINE": ["seaspy", "magnetometer", "uxo", "ferrous anomaly"],
    "ROV-IRM-VIDEO": ["rov video", "irm", "photogrammetry", "catenary chain"],
    "SUBSEA-METROLOGY": ["metrology", "spoolpiece", "jacket alignment", "tie-in", "touchdown"],
    "CONST-SUPPORT": ["pipelay", "jacket installation", "construction support", "barge"]
}

# Sidebar Controls
st.sidebar.header("🎯 Target Role & Weighting Setup")
selected_role = st.sidebar.selectbox("Select Target Offshore Role", list(ROLE_CRITERIA.keys()))

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Dynamic Weighting Rules (v2.4)")
exp_weight = st.sidebar.slider("Experience Weight Factor", 0.5, 2.0, 1.0, 0.1)
software_weight = st.sidebar.slider("Software Recency Weight", 0.5, 2.0, 1.2, 0.1)
specialist_weight = st.sidebar.slider("Specialist Tag Multiplier", 0.5, 3.0, 1.5, 0.1)

role_config = ROLE_CRITERIA[selected_role]

st.markdown(f"### 📋 Active Evaluation Profile: **{selected_role}**")
st.markdown(f"*Minimum Experience Required: {role_config['min_exp']} Years | Priority Tags: {', '.join(role_config['required_tags'])}*")

# Batch CV Uploader (1 to 10+ CVs)
uploaded_files = st.file_uploader("Upload Candidate CVs (PDF) — Select 1 up to 10+ CVs for Comparative Scrutiny", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    if len(uploaded_files) > 10:
        st.warning("⚠️ Maximum recommended batch is 10 CVs at a time. Processing first 10 files.")
        uploaded_files = uploaded_files[:10]

    candidate_results = []

    with st.spinner(f"Scrutinizing {len(uploaded_files)} candidate CV(s) against Ruvira Offshore matrix..."):
        for file in uploaded_files:
            cv_text = extract_pdf_text(file)
            cv_lower = cv_text.lower()
            
            years_found = re.findall(r'(\d+[\+\s]*(?:years?|yrs?))', cv_lower)
            est_exp = 5
            if years_found:
                nums = [int(re.search(r'\d+', y).group()) for y in years_found if int(re.search(r'\d+', y).group()) < 40]
                if nums:
                    est_exp = max(nums)
            
            matched_t1 = [sw.upper() for sw in TIER_1_SOFTWARE if sw in cv_lower]
            matched_leg = [sw.upper() for sw in LEGACY_SOFTWARE if sw in cv_lower]
            tags = [tag for tag, kws in SPECIALIST_TAGS.items() if any(kw in cv_lower for kw in kws)]
            
            base_exp_score = min(est_exp * 0.4 * exp_weight, 4.0)
            sw_score = min(len(set(matched_t1)) * 0.5 * software_weight, 3.0)
            role_tag_matches = sum(1 for t in role_config["required_tags"] if t in tags)
            tag_bonus = min(len(tags) * 0.4 * specialist_weight + (role_tag_matches * 1.0), 4.0)
            
            raw_score = (base_exp_score + sw_score + tag_bonus) * role_config["weight_multiplier"]
            demand_rank = max(1, min(10, round(raw_score / 1.2)))
            
            if demand_rank >= 8:
                rec = "Elite Candidate - Immediate Interview Recommended"
            elif demand_rank >= 6:
                rec = "Qualified Specialist - Suitable for Project Assignment"
            else:
                rec = "Foundational / Generalist - Review for Junior Role"

            candidate_results.append({
                "Candidate Name": file.name.replace(".pdf", "").replace("_", " "),
                "Experience": f"{est_exp} Years",
                "Demand Rank": demand_rank,
                "Tier-1 Software": ", ".join(list(set(matched_t1))[:4]) or "Standard",
                "Specialist Tags": ", ".join([f"[{t}]" for t in tags]) or "None",
                "Recommendation": rec,
                "raw_score": demand_rank
            })

    candidate_results = sorted(candidate_results, key=lambda x: x["raw_score"], reverse=True)

    st.markdown("---")
    st.markdown("## 🏆 Side-by-Side Comparative Ranking Matrix")
    
    df_display = pd.DataFrame(candidate_results)
    
    st.dataframe(
        df_display[["Candidate Name", "Experience", "Demand Rank", "Tier-1 Software", "Specialist Tags", "Recommendation"]],
        use_container_width=True
    )

    top_cand = candidate_results[0]
    st.success(f"🌟 **Top Recommended Candidate for {selected_role}: {top_cand['Candidate Name']}** (Rank: {top_cand['Demand Rank']}/10) — *{top_cand['Recommendation']}*")

    st.markdown("---")
    csv_data = df_display.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Scrutiny Matrix Report (CSV)",
        data=csv_data,
        file_name=f"Ruvira_Offshore_Matrix_Report_{selected_role.replace(' ', '_')}.csv",
        mime="text/csv"
    )
else:
    st.info("👈 Please select the target role in the sidebar and upload between 1 to 10 candidate PDF CVs above to start comparative scrutiny.")
