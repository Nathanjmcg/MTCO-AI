import pathlib
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="MTCO AI Project Dashboard", layout="wide", initial_sidebar_state="collapsed")

# Remove Streamlit chrome so the dashboard fills the page
st.markdown(
    """
    <style>
      #MainMenu, header, footer {visibility: hidden;}
      .block-container {padding: 0 !important; max-width: 100% !important;}
      iframe {border: 0;}
    </style>
    """,
    unsafe_allow_html=True,
)

html = (pathlib.Path(__file__).parent / "dashboard.html").read_text(encoding="utf-8")
components.html(html, height=900, scrolling=False)
