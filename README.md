# StudyFlow — Homework 2: Hello! DevOps

StudyFlow is a responsive study-task planner backed by a real Python FastAPI server and SQLite. Users can create, review, filter, complete, and delete tasks. The project demonstrates **DevOps** by using GitHub version control, automated API tests via GitHub Actions, and Git-connected automatic deployment on Render.

## Project structure

```
app.py                       FastAPI routes and SQLite data storage
static/index.html             Web interface
static/style.css              Responsive styling
static/app.js                 Browser interaction with the REST API
tests/test_app.py             API regression tests
.github/workflows/ci.yml      GitHub Actions continuous integration
render.yaml                   Render web-service deployment configuration
requirements.txt              Runtime dependencies
requirements-dev.txt          Testing dependencies
```

## Run locally on Windows (PowerShell)

1. Install Python 3.11 or newer and open PowerShell in this folder.
2. Install libraries: `py -m pip install -r requirements.txt`
3. Run server: `py -m uvicorn app:app --host 127.0.0.1 --port 8000`
4. Visit http://127.0.0.1:8000/ and try adding/completing/deleting a task.
5. Check http://127.0.0.1:8000/health and http://127.0.0.1:8000/docs
6. Press Ctrl+C to stop the server.

On macOS / Linux, use `python3 -m pip` and `python3 -m uvicorn` instead of `py -m`.

## Run automated tests

Install test dependencies: `py -m pip install -r requirements-dev.txt`
Then run: `py -m pytest -q`

## Upload to GitHub

1. Create a new **public** GitHub repository, e.g. `studyflow-hw2`. If copying these files into an existing README-enabled repository, clone that repository first to avoid unnecessary Git history conflicts.
2. Upload the contents of this folder (including the hidden `.github` folder and `.gitignore`) to the **root** of your GitHub repository; or push with Git using normal `git add`, `commit`, and `push` commands. **Do not use `git push --force` on a repository that already contains work.**
3. Under **Actions**, confirm the `Test StudyFlow API` workflow passes. A green check verifies the API tests (not deployment).
4. The SQLite database file and credentials are ignored by `.gitignore`.

## Public deployment and automatic update (Render)

1. Sign in at https://dashboard.render.com/ and create a **Web Service** using the GitHub repository. Grant GitHub access to Render when requested. Select **Python 3**, and the **Free** plan if offered.
2. Use `pip install -r requirements.txt` as **Build Command**.
3. Use `uvicorn app:app --host 0.0.0.0 --port $PORT` as **Start Command**.
4. Select the `main` branch and enable **Auto-Deploy: On Commit**. After GitHub Actions succeeds, you may switch to **After CI Checks Pass** so Render deploys only passing code. The included `render.yaml` uses the current `autoDeployTrigger: commit` setting and can also be used with Render Blueprint deployment.
5. Open the assigned `https://<service>.onrender.com` URL after Render reports the service as **Live**.
6. Edit any visible text or project version, commit and push the change, then verify Render deployed the new commit. Capture the deployment history and browser result for homework evidence.

**Important limitation of the free demo:** the local SQLite file on Render's ephemeral filesystem is not persistent across all redeploys/restarts. This is adequate for a demo but not for a production multiuser task-management service. To preserve shared tasks reliably, use a persistent managed database and authentication. Free services may spin down when idle and take longer on the first request.

## Deployment proof (important)

GitHub Actions passing by itself does not mean the site has been deployed. To prove the DevOps goal, first show the deployed site in a browser, then change a **visible string in `static/index.html`** (for example, the hero description), commit and push to `main`, and capture the new deployed text plus the successful deploy event in Render.

## Homework 2 evidence checklist

- [ ] Screenshot: working local browser UI with a created task.
- [ ] Screenshot: GitHub repository and latest commit.
- [ ] Screenshot: GitHub Actions test result (green).
- [ ] Screenshot: Render service **Live** status with public URL.
- [ ] Screenshot: publicly loaded browser URL and successful app interaction.
- [ ] Screenshot: auto-deployment triggered after a newer Git push.
- [ ] One-page report including your student ID, name, repo URL, public URL, technology stack, test results, and DevOps flow.
- [ ] ZIP named `StudentID_Name_HW2.zip` containing screenshots and report.

Do not describe a failed, pending, or untested deployment as successful. Replace placeholders in the report with real evidence.

## Notes

This assignment example intentionally does not collect accounts, personal information, or private data. Anyone visiting the demo may access and modify its shared tasks; do not use it to store sensitive information.
