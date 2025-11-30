import json
from django.test import Client


def test_health_endpoint_ok(db):
    client = Client()

    response = client.get("/health/")

    assert response.status_code == 200

    data = json.loads(response.content.decode())
    assert "status" in data
    assert "database" in data
    # basic sanity check
    assert data["status"] in {"ok", "degraded"}
    assert data["database"] in {"ok", "error"}
