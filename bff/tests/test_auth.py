from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlmodel import Session
from core.database.models import CibaTransaction


def test_auth_start_invalid_dni(client: TestClient):
    response = client.post("/api/auth/start", json={"login_hint": "123", "acr_values": "face_mobile"})
    assert response.status_code == 400
    assert "8 dígitos" in response.json()["detail"]


def test_auth_start_invalid_acr(client: TestClient):
    response = client.post("/api/auth/start", json={"login_hint": "12345678", "acr_values": "invalid_method"})
    assert response.status_code == 400
    assert "acr_values inválido" in response.json()["detail"]


@patch("routers.auth.requests.post")
def test_auth_start_success(mock_post, client: TestClient, session: Session):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "auth_req_id": "test-tx-12345",
        "qr": "ciba:test-tx-12345",
        "expires_in": 600,
        "interval": 5,
    }
    mock_post.return_value = mock_resp

    response = client.post(
        "/api/auth/start",
        json={"login_hint": "45678901", "acr_values": "face_mobile"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["auth_req_id"] == "test-tx-12345"
    assert data["qr"] == "ciba:test-tx-12345"

    # Verificar que se guardó en la base de datos
    tx = session.get(CibaTransaction, "test-tx-12345")
    assert tx is not None
    assert tx.login_hint == "45678901"
    assert tx.status == "PENDING"
    assert tx.code_verifier is not None


def test_auth_status_not_found(client: TestClient):
    response = client.get("/api/auth/inexistente/status")
    assert response.status_code == 404


def test_auth_status_pending(client: TestClient, session: Session):
    ahora = datetime.now(timezone.utc)
    tx = CibaTransaction(
        auth_req_id="tx-pending-1",
        login_hint="12345678",
        acr_values="face_mobile",
        code_verifier="verifier123",
        code_challenge="challenge123",
        client_notification_token="token123",
        status="PENDING",
        created_at=ahora,
        expires_at=ahora + timedelta(minutes=10),
    )
    session.add(tx)
    session.commit()

    response = client.get("/api/auth/tx-pending-1/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "PENDING"
    assert "Esperando autenticación" in data["message"]


def test_auth_status_expired(client: TestClient, session: Session):
    ahora = datetime.now(timezone.utc)
    tx = CibaTransaction(
        auth_req_id="tx-expired-1",
        login_hint="12345678",
        acr_values="face_mobile",
        code_verifier="verifier123",
        code_challenge="challenge123",
        client_notification_token="token123",
        status="PENDING",
        created_at=ahora - timedelta(minutes=20),
        expires_at=ahora - timedelta(minutes=10),  # Ya vencido
    )
    session.add(tx)
    session.commit()

    response = client.get("/api/auth/tx-expired-1/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "EXPIRED"


def test_auth_notify_invalid_token(client: TestClient, session: Session):
    ahora = datetime.now(timezone.utc)
    tx = CibaTransaction(
        auth_req_id="tx-notify-1",
        login_hint="12345678",
        acr_values="face_mobile",
        code_verifier="verifier123",
        code_challenge="challenge123",
        client_notification_token="secret-token-123",
        status="PENDING",
        created_at=ahora,
        expires_at=ahora + timedelta(minutes=10),
    )
    session.add(tx)
    session.commit()

    # Token incorrecto
    headers = {"Authorization": "Bearer token-invalido"}
    response = client.post("/api/auth/notify", json={"auth_req_id": "tx-notify-1"}, headers=headers)
    assert response.status_code == 401
    assert "client_notification_token inválido" in response.json()["detail"]


@patch("routers.auth._tarea_segundo_plano_token")
def test_auth_notify_success(mock_bg_task, client: TestClient, session: Session):
    ahora = datetime.now(timezone.utc)
    tx = CibaTransaction(
        auth_req_id="tx-notify-2",
        login_hint="12345678",
        acr_values="face_mobile",
        code_verifier="verifier123",
        code_challenge="challenge123",
        client_notification_token="secret-token-correct",
        status="PENDING",
        created_at=ahora,
        expires_at=ahora + timedelta(minutes=10),
    )
    session.add(tx)
    session.commit()

    headers = {"Authorization": "Bearer secret-token-correct"}
    response = client.post("/api/auth/notify", json={"auth_req_id": "tx-notify-2"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "received"


def test_claims_endpoint_not_approved(client: TestClient, session: Session):
    ahora = datetime.now(timezone.utc)
    tx = CibaTransaction(
        auth_req_id="tx-pending-claims",
        login_hint="12345678",
        acr_values="face_mobile",
        code_verifier="verifier",
        code_challenge="challenge",
        client_notification_token="token",
        status="PENDING",
        created_at=ahora,
        expires_at=ahora + timedelta(minutes=10),
    )
    session.add(tx)
    session.commit()

    response = client.get("/api/auth/tx-pending-claims/claims")
    assert response.status_code == 400


def test_claims_endpoint_approved(client: TestClient, session: Session):
    ahora = datetime.now(timezone.utc)
    tx = CibaTransaction(
        auth_req_id="tx-approved-claims",
        login_hint="12345678",
        acr_values="face_mobile",
        code_verifier="verifier",
        code_challenge="challenge",
        client_notification_token="token",
        status="APPROVED",
        claims={"document_number": "12345678", "name": "JUAN PEREZ", "given_name": "JUAN"},
        created_at=ahora,
        expires_at=ahora + timedelta(minutes=10),
    )
    session.add(tx)
    session.commit()

    response = client.get("/api/auth/tx-approved-claims/claims")
    assert response.status_code == 200
    data = response.json()
    assert data["document_number"] == "12345678"
    assert data["name"] == "JUAN PEREZ"
