"""
MTCO AI Roadmap
Version 2.1

2.1: the AI Summit picker. A floating button on the dashboard opens a picker:
your name, the day, tick the sessions, Save. The save is written to
data/summit_picks.json in this repo with the same token the plan uses, and
Ken (Kensite's agent) reads that file every two minutes, emails the person
their diary entries and books the follow ups after each session. The
programme it shows is data/summit_programme.json. Nothing about the
dashboard or the What's Next plan changes.

Streamlit entry point. The company and project records live in
data/roadmap.json (Ken appends proposals there); this file injects that JSON
into dashboard.html at render time so the HTML itself never has to be edited
to change the data.

2.0: the What's Next planner. The board is now rendered by a two way
component (planner/) rather than components.html, so the order someone drags
the proposed ideas into can come back to Python and be written to GitHub. The
dashboard itself is untouched and still shown exactly as it was.

Saving needs a GitHub token with contents write access to this repo, stored
in the app's Streamlit Cloud secrets as github_token. Without it the planner
opens read only and says so; nothing else about the app changes.
"""
import base64
import json
import pathlib
from datetime import datetime, timezone

import requests
import streamlit as st

from planner import planner

HERE = pathlib.Path(__file__).parent
PLACEHOLDER = "__ROADMAP_JSON__"
REPO = "Nathanjmcg/mtco-ai"
BRANCH = "main"
DATA_PATH = "data/roadmap.json"
API = f"https://api.github.com/repos/{REPO}/contents/{DATA_PATH}"
SUMMIT_PROGRAMME = "data/summit_programme.json"
SUMMIT_PICKS = "data/summit_picks.json"
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


def token():
    """The GitHub token from Streamlit secrets, or None when saving is off.
    st.secrets raises rather than returning a default when no secrets file
    exists at all, which is the normal case when running locally."""
    try:
        return st.secrets.get("github_token") or None
    except Exception:  # noqa: BLE001
        return None


def headers(tok):
    return {"Authorization": f"Bearer {tok}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"}


def load_local():
    try:
        data = json.loads((HERE / "data" / "roadmap.json").read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001  missing or malformed: an empty roadmap, not a crash
        return dict(FALLBACK)
    data.setdefault("active", FALLBACK["active"])
    data.setdefault("projects", [])
    return data


def load_remote(tok):
    """The repo's own copy, so a plan written by someone else shows up without
    waiting for a redeploy. Returns (data, sha) or (None, None)."""
    try:
        r = requests.get(API, headers=headers(tok), params={"ref": BRANCH}, timeout=15)
        if r.status_code != 200:
            return None, None
        body = r.json()
        return json.loads(base64.b64decode(body["content"]).decode()), body["sha"]
    except Exception:  # noqa: BLE001
        return None, None


def load_json(tok, path):
    """Any JSON file in the repo, live copy first, deployed copy second.
    Returns (data, sha); sha is None when the repo copy could not be read."""
    if tok:
        try:
            r = requests.get(f"https://api.github.com/repos/{REPO}/contents/{path}",
                             headers=headers(tok), params={"ref": BRANCH}, timeout=15)
            if r.status_code == 200:
                body = r.json()
                return json.loads(base64.b64decode(body["content"]).decode()), body["sha"]
        except Exception:  # noqa: BLE001
            pass
    try:
        return json.loads((HERE / path).read_text(encoding="utf-8")), None
    except Exception:  # noqa: BLE001
        return None, None


def save_summit_picks(tok, name, keys):
    """Write ONE person's picks. The file is re-read first and everyone else's
    entry is carried over untouched, so two people saving a minute apart
    cannot lose each other's sessions. saved_at is what Ken watches."""
    current, sha = load_json(tok, SUMMIT_PICKS)
    if sha is None:
        return False, "the picks file could not be read back, so nothing was written"
    if not isinstance(current, dict):
        current = {}
    picks = current.setdefault("picks", {})
    prev = picks.get(name) or {}
    picks[name] = {"keys": [str(k) for k in keys],
                   "saved_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                   "seq": int(prev.get("seq") or 0) + 1}
    body = (json.dumps(current, indent=1, ensure_ascii=False) + "\n").encode("utf-8")
    payload = {"message": f"AI Summit: {name} saved {len(keys)} session(s) from the dashboard",
               "content": base64.b64encode(body).decode(), "branch": BRANCH, "sha": sha}
    try:
        w = requests.put(f"https://api.github.com/repos/{REPO}/contents/{SUMMIT_PICKS}",
                         headers=headers(tok), json=payload, timeout=30)
        if w.status_code in (409, 422):
            return False, "someone else saved at the same moment, so nothing was written; try again"
        w.raise_for_status()
    except Exception as e:  # noqa: BLE001
        return False, f"the write failed ({type(e).__name__})"
    return True, ""


def save_plan(tok, lanes):
    """Write ONLY the plan back. The file is re-read first and every other key
    is carried over untouched, so a proposal Ken filed a second ago cannot be
    lost by someone saving an arrangement they started ten minutes before."""
    current, sha = load_remote(tok)
    if current is None:
        return False, "the roadmap could not be read back, so nothing was written"
    ids = {p.get("id") for p in current.get("projects", [])}
    clean = {k: [i for i in lanes.get(k, []) if i in ids] for k in ("now", "next", "later")}
    current["plan"] = {"lanes": clean,
                       "updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")}
    body = (json.dumps(current, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    payload = {"message": "Update the What's Next plan from the dashboard",
               "content": base64.b64encode(body).decode(), "branch": BRANCH, "sha": sha}
    try:
        w = requests.put(API, headers=headers(tok), json=payload, timeout=30)
        if w.status_code in (409, 422):
            return False, "someone else changed the roadmap at the same moment, so nothing was written"
        w.raise_for_status()
    except Exception as e:  # noqa: BLE001
        return False, f"the write failed ({type(e).__name__})"
    return True, ""


tok = token()
remote, _sha = load_remote(tok) if tok else (None, None)
roadmap = remote or load_local()
if remote is None and tok:
    st.toast("Showing the deployed copy of the roadmap: GitHub could not be reached.")

plan = roadmap.get("plan") or {"lanes": {"now": [], "next": [], "later": []}}
saved_at = st.session_state.get("saved_at", "")

# the AI Summit picker: the programme and everyone's saved picks. Shown only
# while there is a programme to show; the button disappears with the file.
summit_prog, _ = load_json(tok, SUMMIT_PROGRAMME)
summit_picks, _ = load_json(tok, SUMMIT_PICKS)
summit = ({"programme": summit_prog, "picks": (summit_picks or {}).get("picks", {})}
          if summit_prog else None)

html = (HERE / "dashboard.html").read_text(encoding="utf-8")


def encode_for_template(obj):
    """The dashboard keeps its page as a JSON encoded string inside a script
    tag, so the injected JSON has to be escaped one level further, and must
    not be able to close that script tag."""
    inner = json.dumps(obj, ensure_ascii=False)
    outer = json.dumps(inner, ensure_ascii=False)[1:-1]
    return outer.replace("/", "\\/").replace("<", "\\u003C")


board = html.replace(PLACEHOLDER, encode_for_template(roadmap))

result = planner(dashboard_html=board, roadmap=roadmap, plan=plan,
                 can_save=bool(tok), saved_at=saved_at, height=900, key="board",
                 summit=summit, summit_saved_at=st.session_state.get("summit_saved_at", ""))

if result and result.get("nonce") and result["nonce"] != st.session_state.get("nonce"):
    st.session_state["nonce"] = result["nonce"]
    if not tok:
        pass
    elif result.get("kind") == "summit":
        name = str(result.get("name") or "").strip()
        allowed = set((summit_prog or {}).get("attendees") or [])
        if name not in allowed:
            st.error("That name is not on the attendee list, so nothing was saved.")
        else:
            ok, why = save_summit_picks(tok, name, result.get("keys") or [])
            if ok:
                st.session_state["summit_saved_at"] = datetime.now(timezone.utc).strftime("%H:%M UTC")
                st.rerun()
            else:
                st.error(f"Your sessions were not saved: {why}.")
    else:
        ok, why = save_plan(tok, result.get("lanes") or {})
        if ok:
            st.session_state["saved_at"] = datetime.now(timezone.utc).strftime("%H:%M UTC")
            st.rerun()
        else:
            st.error(f"The plan was not saved: {why}. Try again in a moment.")
