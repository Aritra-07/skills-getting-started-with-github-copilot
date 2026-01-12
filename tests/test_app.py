from fastapi.testclient import TestClient
from urllib.parse import quote
import copy

from src import app as app_module

client = TestClient(app_module.app)

# Snapshot of initial activities so tests can reset state between runs
ORIGINAL_ACTIVITIES = copy.deepcopy(app_module.activities)

import pytest

@pytest.fixture(autouse=True)
def reset_activities():
    # Reset the in-memory activities before each test
    app_module.activities = copy.deepcopy(ORIGINAL_ACTIVITIES)
    yield


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_adds_participant():
    email = "test_user@example.com"
    path = f"/activities/{quote('Chess Club')}/signup?email={quote(email)}"
    resp = client.post(path)
    assert resp.status_code == 200
    data = client.get("/activities").json()
    assert email in data["Chess Club"]["participants"]


def test_remove_participant():
    email = "daniel@mergington.edu"
    # ensure present initially
    assert email in client.get("/activities").json()["Chess Club"]["participants"]
    path = f"/activities/{quote('Chess Club')}/participants?email={quote(email)}"
    resp = client.delete(path)
    assert resp.status_code == 200
    data = client.get("/activities").json()
    assert email not in data["Chess Club"]["participants"]


def test_remove_missing_participant_returns_404():
    path = f"/activities/{quote('Chess Club')}/participants?email={quote('missing@example.com')}"
    resp = client.delete(path)
    assert resp.status_code == 404
