import time
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "RENIEC Santander BFF"}


@patch("routers.health.requests.get")
def test_health_check_reniec_up(mock_get, client: TestClient):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"keys": [{"kid": "key-1"}]}
    mock_get.return_value = mock_resp

    response = client.get("/health/reniec")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UP"
    assert data["connected"] is True
    assert data["available_keys"] == 1


@patch("routers.health.requests.get")
def test_health_check_reniec_down(mock_get, client: TestClient):
    mock_get.side_effect = Exception("Conexión rechazada")

    response = client.get("/health/reniec")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "DOWN"
    assert data["connected"] is False
    assert "Conexión rechazada" in data["error"]
