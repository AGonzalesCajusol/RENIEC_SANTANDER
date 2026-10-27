import pytest
from unittest.mock import patch, MagicMock
from core.security.sd_jwt import parse_sd_jwt_claims, decode_base64url


def test_parse_sd_jwt_claims():
    # Simula un disclosure SD-JWT codificado en Base64URL: ["sal", "CUI_DNI", "47291038"]
    # ["salt123","CUI_DNI","47291038"] en base64url -> WyJzYWx0MTIzIiwiQ1VJX0ROSSIsIjQ3MjkxMDM4Il0
    # ["salt456","PRENOMBRES","JUAN CARLOS"] -> WyJzYWx0NDU2IiwiUFJFTk9NQlJFUyIsIkpVQU4gQ0FSTE9TIl0
    jwt_emisor = "eyJhbGciOiJFUzI1NiJ9.eyJpc3MiOiJyZW5pZWMifQ.signature"
    disc1 = "WyJzYWx0MTIzIiwiQ1VJX0ROSSIsIjQ3MjkxMDM4Il0"
    disc2 = "WyJzYWx0NDU2IiwiUFJFTk9NQlJFUyIsIkpVQU4gQ0FSTE9TIl0"
    kb_jwt = "eyJhbGciOiJFUzI1NiJ9.kb.signature"
    
    sd_jwt = f"{jwt_emisor}~{disc1}~{disc2}~{kb_jwt}"
    
    claims = parse_sd_jwt_claims(sd_jwt)
    assert claims.get("CUI_DNI") == "47291038"
    assert claims.get("PRENOMBRES") == "JUAN CARLOS"


def test_dni_digital_init_endpoint(client):
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "transactionId": "txn_test_123",
            "requestId": "req_test_123",
            "expiresAt": 1793119421387,
            "requestUri": "https://verify-ts-iugo.rss-systems.com/v1/verify/vp-request/req_test_123"
        }
        mock_post.return_value = mock_response

        response = client.post("/api/dni-digital/init", json={"documentType": "DNI"})
        assert response.status_code == 200
        data = response.json()
        assert data["requestId"] == "req_test_123"
        assert data["transactionId"] == "txn_test_123"
        assert "openid4vp://authorize" in data["qrData"]


def test_dni_digital_status_endpoint(client):
    # Primero inicializamos una transacción para tenerla en BD
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "transactionId": "txn_status_test",
            "requestId": "req_status_test",
            "expiresAt": 1793119421387,
            "requestUri": "https://verify-ts-iugo.rss-systems.com/v1/verify/vp-request/req_status_test"
        }
        mock_post.return_value = mock_response
        client.post("/api/dni-digital/init", json={})

    # Consultamos estado PENDING
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"status": "ACTIVE"}
        mock_get.return_value = mock_resp

        res = client.get("/api/dni-digital/status/req_status_test")
        assert res.status_code == 200
        assert res.json()["status"] == "PENDING"
