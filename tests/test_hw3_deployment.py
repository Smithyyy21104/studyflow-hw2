from fastapi.testclient import TestClient
from app import app


def test_deployment_endpoint(monkeypatch, tmp_path):
    monkeypatch.setenv("DEPLOY_VERSION", "example-test-sha")
    monkeypatch.setenv("TASKS_DB_PATH", str(tmp_path / "hw3_test.sqlite3"))
    monkeypatch.setenv("SEED_DEMO", "0")
    with TestClient(app) as client:
        response = client.get("/deployment")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "StudyFlow"
        assert data["version"] == "3.0.0"
        assert data["commit"] == "example-test-sha"
        assert "Docker Hub" in data["pipeline"]
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json()["version"] == "3.0.0"
