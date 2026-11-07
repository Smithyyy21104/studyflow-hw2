# Homework 3 - From Development to Deployment 2

Student: **2025100332 / Kaung Khant Htet**
Existing project: https://github.com/Smithyyy21104/studyflow-hw2

## What this upgrade does

Every push to `main` triggers:
1. **CI**: GitHub-hosted Ubuntu runner tests the FastAPI service.
3. **Docker Hub**: GitHub Actions pushes both `latest` and an immutable `sha-<commit>` tag.
4. **CD**: A separate job on a self-hosted runner pulls that commit-tagged image, redeploys the local service with persistent SQLite data, checks `/health`, and restores the last container if startup fails.
5. **Verification**: `/deployment` reports the actual deployed Git commit, proving the newest push reached the local server.

**You must configure your own Docker Hub credentials and runner on your computer. No credentials are contained in this package.** Do not submit the report as evidence until the workflow completes and you capture actual screenshots.

## Part A - Copy the files into your existing GitHub project

Clone your existing repository and make a separate working copy for HW3:

```bash
git clone https://github.com/Smithyyy21104/studyflow-hw2.git
cd studyflow-hw2
```

Copy the files from **this upgrade pack** into the repository, preserving hidden folders such as `.github` and `.dockerignore`. When macOS asks whether to merge the `.github` folder, **merge**, not replace its existing contents.

Inside the cloned repository run:

```bash
python3 scripts/apply_hw3.py
python3 -m pip install -r requirements-dev.txt
python3 -m pytest -q
```

Existing `app.py`, `static/`, and `tests/test_app.py` stay in place. `apply_hw3.py` changes the app title/version, adds `/deployment`, and changes the visible HW2 text to HW3. It will refuse to overwrite any unknown or altered original file rather than silently breaking your app.

## Part B - Docker Hub

1. Install and start **Docker Desktop** on the machine that will run the deployed service.
2. On https://hub.docker.com/ sign in and create a **public** repository called `studyflow-hw3`.
3. Go to Docker Hub account settings -> **Personal access tokens** and create a token with **Read, Write** access.
4. In GitHub `studyflow-hw2` -> **Settings -> Secrets and variables -> Actions -> New repository secret**, add:
   - `DOCKERHUB_USERNAME` = your Docker Hub username
   - `DOCKERHUB_TOKEN` = your Docker Hub access token
5. Never commit, paste here, or screenshot the token. The workflow reads both only from GitHub Secrets.

## Part C - Self-hosted GitHub Actions runner (Mac)

1. In your GitHub repository go to **Settings -> Actions -> Runners -> New self-hosted runner**.
2. Select **macOS** and **ARM64** for Apple Silicon (or **x64** for Intel Mac). Copy **GitHub's current install and configuration commands** from that page. The registration token expires, so don't use commands from an old screenshot.
3. In the runner `config.sh` setup, choose a distinctive name, and add the custom label **`studyflow-deploy`**. Example: when prompted for additional labels, enter `studyflow-deploy`.
4. Start the runner as instructed (normally `./run.sh`) and keep it running. Docker Desktop must also be running. GitHub -> Settings -> Actions -> Runners should show the runner **Idle/Online**.
5. GitHub-hosted actions build images in the cloud. The self-hosted runner just pulls the image and runs Docker locally.

**Security:** This is a public repository. Do not enable the self-hosted runner to execute workflows from untrusted pull requests. The provided HW3 workflow triggers only a push to `main` or manual dispatch. Protect your GitHub account with 2FA and do not let others push to `main`.

## Part D - First deployment

Run in the cloned project:

```bash
git add Dockerfile .dockerignore .github/workflows/hw3-cicd.yml scripts tests/test_hw3_deployment.py README_HW3.md app.py static/index.html
git commit -m "HW3 automate Docker Hub build and local deployment"
git push origin main
```

On GitHub -> **Actions** -> **HW3 - Test Build Push Deploy**, confirm three green jobs: `Run FastAPI tests`, `Build Docker image and push to Docker Hub`, `Deploy on self-hosted runner`. Docker Hub should show your new `studyflow-hw3` image.

On the Mac browser open:
- http://127.0.0.1:8000/ (StudyFlow dashboard)
- http://127.0.0.1:8000/health (health JSON)
- http://127.0.0.1:8000/deployment (the exact deployed Git commit)

If the runner waits in Queued, check that it is **Online**, that it has label `studyflow-deploy`, and that Docker Desktop is running.

## Part E - Prove automatic redeployment (the essential HW3 proof)

1. Change the user-visible text in `static/index.html` from `Automatically deployed.` to `Automatically updated by GitHub.` (or make another obvious version update).
2. Commit and push this change to `main`, then open Actions to see a **new run**.
3. After the new deploy job completes, reload http://127.0.0.1:8000/ and verify the changed text appears.
4. Compare `/deployment` to the latest commit SHA shown by the successful GitHub Actions run. They must match.
5. Capture genuine screenshots:
   - All 3 GitHub Actions jobs passing on the new push.
   - The updated StudyFlow page in a Mac browser showing the new text.
   - `/deployment` displaying the new commit (may be combined with the browser screenshot).
   - Docker Hub image tags (`latest`, `sha-<commit>`) if room permits.
6. Place screenshots into `screenshots/` for your report. Never use screenshots of this tutorial as your own proof.

## Submission

Submit one ZIP named `2025100332_KaungKhantHtet_HW3.zip` containing **actual verification screenshots** and a **one-page report** with the GitHub link, Docker Hub image, deployment environment, what changed, successful CI/CD run, and what the screenshots show.

An editable report draft is supplied separately. Replace `PENDING` sections with observations from your own successful run. You do **not** need to put Docker Hub tokens, hidden credentials, or the runner's registration token into the submitted ZIP.

## Troubleshooting

- **Docker login denied**: Check that both GitHub secrets exist and the Docker Hub token can write to your repository.
- **Buildx pushes fail**: Check Docker Hub account/repository permissions and image namespace.
- **Deploy job Queued**: Runner offline, lacks the `studyflow-deploy` label, or GitHub Actions isn't enabled for the repo.
- **docker not found / daemon error**: Install/open Docker Desktop on the self-hosted runner.
- **localhost:8000 occupied**: Stop the other local service first or change `HOST_PORT` consistently in `deploy.sh` and `verify.sh`.
- **SQLite permission**: The workflow uses a named Docker volume (`studyflow-hw3-data`) so the non-root app can write to `/data`.
- **Test failure after copying**: Check that `scripts/apply_hw3.py` successfully changed your original app before committing.
- **Failed new deploy**: `deploy.sh` attempts to restart the previous container. Review the failed GitHub Actions job and Docker logs.
- **Runner unattended on Mac**: Docker Desktop and the runner need to stay active. The runner cannot deploy when the laptop is asleep or turned off.
