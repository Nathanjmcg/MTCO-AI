# MTCO AI Project Dashboard

Streamlit wrapper around a self-contained HTML dashboard.

## Files
- `app.py` - Streamlit entry point
- `dashboard.html` - the dashboard, fully self-contained (logos, fonts and runtime inlined)
- `requirements.txt`

## Run locally
```
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud
1. Push this folder to a GitHub repo (files at the root).
2. share.streamlit.io > New app > pick the repo, branch and `app.py`.

## Updating
Replace `dashboard.html` with a fresh export and redeploy.
