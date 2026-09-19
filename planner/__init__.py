"""
MTCO AI Roadmap planner component
Version 1.1

1.1: the AI Summit picker rides in the same component. summit carries the
programme and everyone's saved picks in; a save comes back as
{"kind": "summit", "name": ..., "keys": [...], "nonce": n}, and the What's
Next plan now says {"kind": "plan", ...} so the app can tell them apart.

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


def planner(dashboard_html, roadmap, plan, can_save, saved_at="", height=900, key=None,
            summit=None, summit_saved_at=""):
    """Render the board. Returns None until someone saves, then either the plan
    {"kind": "plan", "lanes": {"now": [...], "next": [...], "later": [...]}, "nonce": n}
    or a summit pick {"kind": "summit", "name": ..., "keys": [...], "nonce": n}."""
    return _component(dashboard_html=dashboard_html, roadmap=roadmap, plan=plan,
                      can_save=bool(can_save), saved_at=saved_at, height=height,
                      summit=summit, summit_saved_at=summit_saved_at,
                      key=key, default=None)
