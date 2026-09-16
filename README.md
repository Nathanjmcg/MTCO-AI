# MTCO AI Roadmap

Working folder for the MTCO Group AI Roadmap dashboard, live at
https://mtco-ai.streamlit.app and deployed from the GitHub repo
Nathanjmcg/mtco-ai.

## Files
- `app.py` - Streamlit entry point. Reads dashboard.html, injects data/roadmap.json into it and renders it full page.
- `dashboard.html` - the dashboard itself (logos, fonts and runtime inlined). Holds no project data.
- `data/roadmap.json` - the companies shown, the category list and every project. Ken appends proposals to the copy in the repo.
- `requirements.txt` - Streamlit only.
- `planner/` - the What's Next planner, a two way Streamlit component. `frontend/index.html` shows the board and the planner; `__init__.py` wires it to Python.
- `Publish App To GitHub.py` - pushes the files above to the repo. Run it after any change.
- `Publish App.cmd`, `Push Roadmap Data.cmd`, `Pull Roadmap Data.cmd` - double click versions of the same thing.

## Making a change live
1. Edit the file(s) in this folder.
2. Run `Publish App To GitHub.py` from a terminal with the full Python path.
3. Streamlit Cloud redeploys within a couple of minutes.

## Where the project data lives
`data/roadmap.json` in the repo is the single source of truth. Ken writes to it when
someone emails him an idea, so the publish script never overwrites it (it only creates
it if the repo has none). To edit a project by hand, edit it on GitHub or pull the file
down first.

Each project carries: id, company (mtco, kensite, aes, eventus, ats, thinkhire, fireflai),
name, stage (Proposed, Scoped, Planned, Building, Testing, Shipped), category (one of the
list in the file), owner, proposed_by, date (Mon YYYY), summary (one line, shown on the
card), scope (What it does), how (How it does it) and who (a list of {who, how} pairs).

## Ken
Staff on the proposers list, and guests granted the ai_roadmap ability, can email Ken an
idea. He works out the company and category, asks for anything he cannot infer, then files
it as Proposed and confirms with a link to the app.

## Run locally
```
pip install -r requirements.txt
streamlit run app.py
```

## What's Next planner
The button under the stage bracket opens a planner: every Proposed idea across the
group, dragged into Now, Next or Later to form the AI Manager's queue. Saving writes
a `plan` object into `data/roadmap.json` in the repo and nothing else, so a proposal
Ken filed a second earlier can never be lost by someone saving an arrangement.

Saving needs a GitHub token with contents write access to this repo, stored in the
app's Streamlit Cloud secrets as `github_token`:

    Streamlit Cloud > this app > Settings > Secrets
    github_token = "ghp_..."

Without it the planner still opens, read only, and says so on screen. Note the app is
public, so with the token in place anyone who has the link can rearrange the plan.
Every save is a commit, so the history in GitHub is the audit trail and any change can
be reverted.
