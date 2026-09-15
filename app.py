"""
MTCO AI Roadmap
Version 1.1

Streamlit wrapper around the self contained dashboard.html. The company and
project records live in data/roadmap.json (Ken appends proposals there); this
file injects that JSON into the dashboard at render time so the HTML itself
never has to be edited to change the data.
"""
import json
import pathlib

import streamlit as st
import streamlit.components.v1 as components

HERE = pathlib.Path(__file__).parent
PLACEHOLDER = "__ROADMAP_JSON__"
FALLBACK = {"active": ["mtco", "kensite", "aes"], "categories": [], "projects": []}

st.set_page_config(page_title="MTCO AI Project Dashboard", layout="wide",
                   initial_sidebar_state="collapsed")

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


def load_roadmap():
    try:
        data = json.loads((HERE / "data" / "roadmap.json").read_text(encoding="utf-8"))
        data.setdefault("active", FALLBACK["active"])
        data.setdefault("projects", [])
        return data
    except Exception:  # noqa: BLE001  missing or malformed file: show an empty roadmap, not a crash
        return dict(FALLBACK)


def encode_for_template(obj):
    """The dashboard keeps its page as a JSON encoded string inside a script
    tag, so the injected JSON has to be escaped one level further, and must
    not be able to close that script tag."""
    inner = json.dumps(obj, ensure_ascii=False)
    outer = json.dumps(inner, ensure_ascii=False)[1:-1]
    return outer.replace("/", "\\/").replace("<", "\\u003C")


html = (HERE / "dashboard.html").read_text(encoding="utf-8")
html = html.replace(PLACEHOLDER, encode_for_template(load_roadmap()))
components.html(html, height=900, scrolling=False)
