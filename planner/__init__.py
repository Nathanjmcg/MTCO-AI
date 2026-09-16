"""
MTCO AI Roadmap planner component
Version 1.0

A two way Streamlit component. It shows the dashboard exactly as it is (in a
nested frame, untouched), adds the What's Next button, and returns the plan
back to Python when someone saves an arrangement. Two way is the whole point:
st.components.v1.html can only send, so the drag order could never get back
to the server to be written to GitHub.
"""
from pathlib import Path

import streamlit.components.v1 as components

_FRONTEND = Path(__file__).parent / "frontend"
_component = components.declare_component("mtco_planner", path=str(_FRONTEND))


def planner(dashboard_html, roadmap, plan, can_save, saved_at="", height=900, key=None):
    """Render the board. Returns None until someone saves, then the plan dict
    {"lanes": {"now": [id, ...], "next": [...], "later": [...]}, "nonce": n}."""
    return _component(dashboard_html=dashboard_html, roadmap=roadmap, plan=plan,
                      can_save=bool(can_save), saved_at=saved_at, height=height,
                      key=key, default=None)
