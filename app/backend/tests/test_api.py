from datetime import datetime, timedelta

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from fastapi.testclient import TestClient

from backend.main import app
from backend.db import Base, engine
from backend.parsers import PARSER_REGISTRY

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


def test_mock_parser():
    parser = PARSER_REGISTRY["mock_worldline"]
    sample = Path(__file__).resolve().parents[1] / "samples" / "worldline_mock.csv"
    with sample.open("rb") as f:
        rows = list(parser.parse(f))
    assert len(rows) == 2
    assert rows[0].amount_cents == 1000


def test_csv_import():
    # Create event
    payload = {
        "name": "Import Event",
        "start_at": datetime.utcnow().isoformat(),
        "end_at": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
    }
    r = client.post("/events/", json=payload)
    event_id = r.json()["id"]

    # Create selling point
    sp_payload = {"name": "Gate A", "latitude": 0.0, "longitude": 0.0}
    r = client.post(f"/events/{event_id}/selling-points", json=sp_payload)
    sp_id = r.json()["id"]

    # Create EPT
    ept_payload = {"provider": "worldline", "label": "Terminal 1"}
    r = client.post(f"/events/selling-points/{sp_id}/epts", json=ept_payload)
    ept_id = r.json()["id"]

    sample = Path(__file__).resolve().parents[1] / "samples" / "worldline_mock.csv"
    with sample.open("rb") as f:
        r = client.post(
            f"/events/{event_id}/imports",
            data={"parser": "mock_worldline"},
            files={"file": ("worldline_mock.csv", f, "text/csv")},
        )
    assert r.status_code == 200
    data = r.json()
    assert data == {"processed": 2, "inserted": 2, "skipped_duplicates": 0, "errors": 0}

    # Re-upload should skip duplicates
    with sample.open("rb") as f:
        r = client.post(
            f"/events/{event_id}/imports",
            data={"parser": "mock_worldline"},
            files={"file": ("worldline_mock.csv", f, "text/csv")},
        )
    data = r.json()
    assert data == {"processed": 2, "inserted": 0, "skipped_duplicates": 2, "errors": 0}
