#!/usr/bin/env python3
"""Adapt the existing StudyFlow HW2 app for the HW3 CI/CD proof.
Run once inside a clone of Smithyyy21104/studyflow-hw2.
The script is idempotent and refuses to modify an unexpected file layout.
"""
from pathlib import Path
import sys


def replace_once(path: Path, old: str, new: str) -> None:
    if not path.exists():
        raise SystemExit(f"Missing original StudyFlow file: {path}")
    text = path.read_text(encoding="utf-8")
    if new in text:
        print(f"Already updated: {path}")
        return
    if text.count(old) != 1:
        raise SystemExit(f"Expected exactly one occurrence in {path}: {old[:100]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print(f"Updated: {path}")


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    app = root / "app.py"
    html = root / "static/index.html"
    replace_once(
        app,
        'app = FastAPI(title="StudyFlow - HW2 DevOps Demo", version="1.0.0", lifespan=lifespan)',
        'app = FastAPI(title="StudyFlow - HW3 Automated Deployment", version="3.0.0", lifespan=lifespan)',
    )
    replace_once(
        app,
        """@app.get("/api/tasks")""",
        """@app.get("/deployment")
def deployment_status():
    return {"service": "StudyFlow", "version": app.version,
            "commit": os.getenv("DEPLOY_VERSION", "local"),
            "pipeline": "GitHub Actions -> Docker Hub -> self-hosted runner"}


@app.get("/api/tasks")""",
    )
    replace_once(html, 'HW2 · DevOps Demo', 'HW3 · Automated CI/CD')
    replace_once(html, 'Every single day.', 'Automatically deployed.')
    replace_once(html, 'HW2 • Open Source Software Development', 'HW3 • Docker + GitHub Actions + Docker Hub')
    replace_once(html, 'Plan smarter. Deploy faster.', 'Code changes deploy automatically.')
    print("HW3 app changes applied. Run: python3 -m pytest -q")


if __name__ == '__main__':
    main()
