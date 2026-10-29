from fastapi.testclient import TestClient
from pydantic_tutorial.api import app

client = TestClient(app)

def test_create_job():
    r = client.post("/job/", json={"title": "Data Engineer", "description": "Build data pipelines.", "salary": 2400000, "remote": True})
    assert r.status_code == 201
    assert r.json()["id"] == 1

def test_parse_jobs():
    r = client.post("/job/parse", json=[{"title": "Data Engineer", "description": "Build data pipelines.", "salary": 2400000, "remote": True}, {}])
    assert r.status_code == 200
    assert "clean" in r.json()
    assert "errors" in r.json()
