from fastapi import APIRouter, HTTPException, Header
from schemas.auth import (
    AuthStartRequest,
    AuthStartResponse,
    AuthNotifyResponse,
    AuthTokenResponse,
)

router = APIRouter(prefix="/auth", tags=["ID-Perú CIBA Auth"])


@router.post(
    "/start",
    response_model=AuthStartResponse,
    summary="Iniciar proceso de autenticación CIBA",
)
def iniciar_autenticacion(data: AuthStartRequest):
    """
    1. Genera PKCE (code_verifier / code_challenge) y client_notification_token.
    2. Consume POST /service/bc-authorize de RENIEC.
    3. Guarda los datos transaccionales en base de datos (ej. PostgreSQL).
    4. Retorna el 'qr' al frontend.
    """
    # Lógica de BFF aquí...
    return {"message": "Transacción iniciada", "qr": "VALOR_QR_DE_EJEMPLO"}


@router.post(
    "/notify",
    response_model=AuthNotifyResponse,
    summary="Webhook de notificación de RENIEC",
)
def endpoint_notificacion(
    payload: dict,
    authorization: str | None = Header(None),
):
    """
    Endpoint url_notify expuesto para que RENIEC notifique el fin del proceso.
    Valida estrictamente el Bearer token (client_notification_token).
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Token no proporcionado o inválido",
        )

    # Procesar la notificación en segundo plano y responder 200 OK
    return {"status": "received"}


@router.post(
    "/token",
    response_model=AuthTokenResponse,
    summary="Consultar / canjear tokens con RENIEC",
)
def consultar_tokens(auth_req_id: str):
    """
    Consulta POST /service/ciba/token usando el code_verifier y auth_req_id.
    Valida el JWT resultante usando las llaves JWKS de RENIEC.
    """
    # Lógica de canje de tokens y validación criptográfica
    return {"access_token": "JWT_DE_ACCESO", "id_token": "JWT_DE_IDENTIDAD"}
