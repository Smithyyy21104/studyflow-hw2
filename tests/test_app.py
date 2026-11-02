import pytest
from fastapi.testclient import TestClient
from app import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv('TASKS_DB_PATH', str(tmp_path / 'test.sqlite3'))
    monkeypatch.setenv('SEED_DEMO', '0')
    with TestClient(app) as test_client:
        yield test_client


def test_home_health_and_initial_stats(client):
    assert client.get('/').status_code == 200
    assert 'StudyFlow' in client.get('/').text
    assert client.get('/health').json()['status'] == 'ok'
    assert client.get('/api/stats').json() == {'total': 0, 'done': 0, 'pending': 0}


def test_create_complete_filter_delete(client):
    response = client.post('/api/tasks', json={'title': 'Review slides', 'category': 'Study', 'priority': 'high', 'due_date': '2026-11-02'})
    assert response.status_code == 201
    task = response.json()
    assert task['title'] == 'Review slides'
    assert task['completed'] is False
    assert len(client.get('/api/tasks?status=pending').json()) == 1
    update = client.patch(f"/api/tasks/{task['id']}", json={'completed': True})
    assert update.status_code == 200 and update.json()['completed'] is True
    assert len(client.get('/api/tasks?status=done').json()) == 1
    assert client.get('/api/stats').json() == {'total': 1, 'done': 1, 'pending': 0}
    assert client.delete(f"/api/tasks/{task['id']}").status_code == 204
    assert client.get('/api/stats').json()['total'] == 0


def test_validation_and_missing_task(client):
    assert client.post('/api/tasks', json={'title': ''}).status_code == 422
    assert client.post('/api/tasks', json={'title': '  '}).status_code == 422
    assert client.patch('/api/tasks/987', json={'completed': None}).status_code == 422
    assert client.patch('/api/tasks/987', json={'completed': True}).status_code == 404
    assert client.delete('/api/tasks/987').status_code == 404
    assert client.get('/api/tasks?status=unknown').status_code == 422
