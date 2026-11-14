import streamlit as st
import re

# Page Configuration
st.set_page_config(
    page_title="Offshore CV Scrutiny Matrix",
    page_icon="🧭",
    layout="wide"
)

# Helper function to extract text from PDF if pypdf is available
def extract_pdf_text(uploaded_file):
    try:
        import pypdf
        reader = pypdf.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except ImportError:
        # Fallback if pypdf isn't installed
        return uploaded_file.getvalue().decode("latin-1", errors="ignore")

# Taxonomy Definitions
TIER_1_SOFTWARE = [
    "qinsy", "eiva", "navisuite", "caris", "hips", "sips", 
    "sonarwiz", "kingdom", "qimera", "starfix", "fusion 2", 
    "autocad civil 3d", "microstation", "uxo bentley", "opensite", "dgl"
]

LEGACY_SOFTWARE = [
    "hydropro", "triton isis", "sonarweb", "winfrog", "starfix 3"
]

SPECIALIST_TAGS = {
    "SPARSE-LBL": ["sparse lbl", "long baseline", "lbl calibration", "transponder network"],
    "USBL-CAL": ["usbl", "ultra-short baseline", "ray-tracing", "acoustic telemetry"],
    "INS-DVL-INTEG": ["lodestar", "syrinx", "phins", "dvl", "inertial navigation"],
    "USV-COMMAND": ["wavebot", "c-worker", "drix", "uncrewed surface vehicle", "usv"],
    "AUV-OPS": ["auv", "autonomous underwater vehicle", "mission planning"],
    "MBES-CAL-ATEX": ["multibeam", "mbes", "patch test", "backscatter calibration"],
    "SBP-CHIRP": ["sub-bottom", "chirp", "shallow hazards", "stratigraphy"],
    "MAG-PIPELINE": ["seaspy", "magnetometer", "uxo", "ferrous anomaly"],
    "ROV-IRM-VIDEO": ["rov video", "irm", "photogrammetry", "catenary chain"],
    "SUBSEA-METROLOGY": ["metrology", "spoolpiece", "jacket alignment", "tie-in"],
    "CFIHOS-COMPLIANT": ["cfihos", "iogp", "fit-checks"]
}

# App Header
st.title("🧭 Offshore CV Scrutiny & Competency Matrix")
st.markdown("Upload candidate CVs in PDF format to instantly evaluate software recency, specialist tags, and compute market demand ranking.")

uploaded_file = st.file_uploader("Upload Candidate CV (PDF)", type=["pdf"])

if uploaded_file is not None:
    with st.spinner("Scrutinizing CV text and extracting competencies..."):
        cv_text = extract_pdf_text(uploaded_file)
        cv_lower = cv_text.lower()
        
        # 1. Experience Extraction (heuristic search for years)
        years_found = re.findall(r'(\d+[\+\s]*(?:years?|yrs?))', cv_lower)
        estimated_exp = 5  # default baseline
        if years_found:
            # parse max mentioned years
            nums = [int(re.search(r'\d+', y).group()) for y in years_found if int(re.search(r'\d+', y).group()) < 40]
            if nums:
                estimated_exp = max(nums)

        # 2. Software Matching
        matched_tier1 = [sw.upper() for sw in TIER_1_SOFTWARE if sw in cv_lower]
        matched_legacy = [sw.upper() for sw in LEGACY_SOFTWARE if sw in cv_lower]
        
        # 3. Specialist Tagging
        identified_tags = []
        for tag, keywords in SPECIALIST_TAGS.items():
            if any(kw in cv_lower for kw in keywords):
                identified_tags.append(tag)

        # 4. Score & Rank Calculation (Scale 1-10)
        # Base score from experience (max 4 points)
        exp_score = min(estimated_exp * 0.4, 4.0)
        # Software score from current market tools (max 3 points)
        sw_score = min(len(matched_tier1) * 0.75, 3.0)
        # Specialist bonus (max 3 points)
        spec_score = min(len(identified_tags) * 0.75, 3.0)
        
        raw_score = exp_score + sw_score + spec_score
        demand_rank = max(1, min(10, round(raw_score)))

        # Display Results
        st.success("CV Scrutiny Complete!")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Estimated Experience", f"~ {estimated_exp} Years")
        with col2:
            st.metric("Current Software Matches", len(matched_tier1))
        with col3:
            st.metric("Composite Demand Rank", f"{demand_rank} / 10", delta="High Demand" if demand_rank >= 8 else "Standard")

        st.markdown("---")
        
        # Detailed Breakdown
        r_col1, r_col2 = st.columns(2)
        
        with r_col1:
            st.subheader("🛠️ Software Portfolio")
            if matched_tier1:
                st.markdown("**Current Market Standard (Tier 1):**")
                for sw in set(matched_tier1):
                    st.markdown(f"- ✅ {sw}")
            if matched_legacy:
                st.markdown("**Legacy Packages Identified:**")
                for sw in set(matched_legacy):
                    st.markdown(f"- ⚠️ {sw}")
            if not matched_tier1 and not matched_legacy:
                st.info("No specific industry software keywords matched in text.")

        with r_col2:
            st.subheader("🏷️ Specialist Tags Identified")
            if identified_tags:
                for tag in identified_tags:
                    st.markdown(f"- `[{tag}]`")
            else:
                st.info("No elite specialist tags detected in CV text.")

        st.markdown("---")
        st.subheader("📋 Recruiter Assessment & Recommendation")
        if demand_rank >= 9:
            st.error("**Elite Subject Matter Expert (Rank 9-10):** Candidate possesses advanced current-generation software proficiency and high-value niche specialist tags. Recommended for immediate client interview.")
        elif demand_rank >= 7:
            st.warning("**Advanced Specialist (Rank 7-8):** Strong operational background with solid market-standard software familiarity.")
        else:
            st.info("**Foundational / Generalist (Rank 1-6):** Standard profile. Consider for junior roles or verify hands-on experience.")
