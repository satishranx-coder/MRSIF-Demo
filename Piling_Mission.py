"""MRSIF Pile Foundation Mission Assurance demonstration.

Run locally:
    python -m pip install -r requirements.txt
    streamlit run mrsif_piling_mission.py

The engineering workspace is implemented as a self-contained browser component
stored beside this launcher in ``mrsif_piling_foundation_demo.html``.
"""

from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


APP_TITLE = "MRSIF | Pile Foundation Mission Assurance"
DEMO_FILE = Path(__file__).with_name("mrsif_piling_foundation_demo.html")


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
      header[data-testid="stHeader"] { background: transparent; }
      .stApp { background: #f2efe7; }
      .block-container {
        max-width: 100%;
        padding: 0.35rem 0.45rem 1rem;
      }
      iframe[title="streamlit_components.v1.components.html"] {
        border: 0;
        background: #f2efe7;
      }
      #MainMenu, footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


def load_demo() -> str:
    """Load the workspace HTML from the same folder as this Python file."""
    if not DEMO_FILE.exists():
        st.error(
            "The mission workspace file is missing. Keep "
            "`mrsif_piling_foundation_demo.html` in the same folder as this "
            "Python file."
        )
        st.stop()

    return DEMO_FILE.read_text(encoding="utf-8")


components.html(
    load_demo(),
    height=2450,
    scrolling=True,
)

