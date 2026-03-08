import pytest
import json
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_home_loads(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"Bhavya" in res.data


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"


def test_projects_api(client):
    res = client.get("/api/projects")
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)
    assert len(data) == 4
    assert data[0]["title"] == "URL Shortener API"


def test_contact_success(client):
    res = client.post("/api/contact", json={
        "name": "Test User",
        "email": "test@example.com",
        "subject": "Job Opportunity",
        "message": "Hi Bhavya, I have a great opportunity for you!"
    })
    assert res.status_code == 200
    assert res.get_json()["success"] is True


def test_contact_missing_name(client):
    res = client.post("/api/contact", json={
        "email": "test@example.com",
        "message": "Hello there this is a message"
    })
    assert res.status_code == 400


def test_contact_invalid_email(client):
    res = client.post("/api/contact", json={
        "name": "Test", "email": "notanemail", "message": "Hello testing"
    })
    assert res.status_code == 400


def test_contact_short_message(client):
    res = client.post("/api/contact", json={
        "name": "Test", "email": "t@t.com", "message": "Hi"
    })
    assert res.status_code == 400


def test_contact_no_body(client):
    res = client.post("/api/contact")
    assert res.status_code == 400


def test_404(client):
    res = client.get("/nonexistent-page")
    assert res.status_code == 404
