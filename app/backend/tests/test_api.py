from datetime import datetime, timedelta

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from fastapi.testclient import TestClient

from backend.main import app
from backend.db import Base, engine

client = TestClient(app)

# Reset database
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def test_event_crud():
    payload = {
        "name": "Test Event",
        "start_at": datetime.utcnow().isoformat(),
        "end_at": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
    }
    r = client.post("/events/", json=payload)
    assert r.status_code == 200
    event = r.json()

    r = client.get("/events/")
    assert any(e["id"] == event["id"] for e in r.json())

    r = client.patch(f"/events/{event['id']}", json={"name": "Updated"})
    assert r.json()["name"] == "Updated"

    r = client.delete(f"/events/{event['id']}")
    assert r.status_code == 200


def test_summary_empty():
    payload = {
        "name": "Summary Event",
        "start_at": datetime.utcnow().isoformat(),
        "end_at": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
    }
    r = client.post("/events/", json=payload)
    event_id = r.json()["id"]
    r = client.get(f"/events/{event_id}/summary")
    assert r.status_code == 200
    data = r.json()
    assert data["event_id"] == event_id
    assert data["selling_points"] == []
