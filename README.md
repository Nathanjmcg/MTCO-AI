# MTCO AI Roadmap

Working folder for the MTCO Group AI Roadmap dashboard, live at
https://mtco-ai.streamlit.app and deployed from the GitHub repo
Nathanjmcg/mtco-ai.

## Files
- `app.py` - Streamlit entry point. Reads dashboard.html and renders it full page.
- `dashboard.html` - the dashboard itself, fully self contained (logos, fonts, runtime and project data inlined).
- `requirements.txt` - Streamlit only.
- `Publish App To GitHub.py` - pushes the files above to the repo. Run it after any change.

## Making a change live
1. Edit the file(s) in this folder.
2. Run `Publish App To GitHub.py` from a terminal with the full Python path.
3. Streamlit Cloud redeploys within a couple of minutes.

## Where the project data lives
Company and project records are the `COMPANIES` array inside `dashboard.html`
(search for `const COMPANIES`). Each project is `P(name, stage, owner, date, summary)`
with stage one of Proposed, Scoped, Planned, Building, Testing, Shipped.

## Run locally
```
pip install -r requirements.txt
streamlit run app.py
```
