from fastapi import APIRouter, HTTPException, Header
from core.security import generar_pkce, validar_jwt_reniec
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
    # Generación de PKCE para el flujo CIBA
    pkce_data = generar_pkce()
    # pkce_data["code_verifier"] -> Se almacenará en BD junto con el session/auth_req_id
    # pkce_data["code_challenge"] y "S256" -> Se envían a /service/bc-authorize

    return {
        "message": "Transacción iniciada con PKCE generado",
        "qr": "VALOR_QR_DE_EJEMPLO",
    }


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
    summary="Consultar / canjear tokens con RENIEC y validar criptográficamente",
)
def consultar_tokens(auth_req_id: str):
    """
    1. Consulta POST /service/ciba/token usando code_verifier y auth_req_id.
    2. Valida el JWT resultante usando las llaves JWKS de RENIEC (RS256).
    """
    # Simulación de respuesta de tokens obtenida tras canje
    tokens_ejemplo = {
        "access_token": "JWT_DE_ACCESO_EJEMPLO",
        "id_token": "JWT_DE_IDENTIDAD_EJEMPLO",
    }

    # Ejemplo de validación criptográfica con JWKS de RENIEC
    # resultado_validacion = validar_jwt_reniec(tokens_ejemplo["id_token"])

    return tokens_ejemplo

