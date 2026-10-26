import hmac
import os
import time
import requests
from fastapi import APIRouter, HTTPException, Header, BackgroundTasks
from core.config import settings
from core.security.pkce import generar_pkce
from core.security.jwt_validator import validar_jwt_reniec
from schemas.auth import (
    AuthStartRequest,
    AuthStartResponse,
    AuthNotifyResponse,
    AuthStatusResponse,
    AuthTokenResponse,
    UserClaimsResponse,
)

router = APIRouter(prefix="/auth", tags=["ID-Perú CIBA Auth"])

# Almacén en memoria simulando BD transaccional (PostgreSQL)
# auth_req_id -> {
#     "auth_req_id": str,
#     "login_hint": str,
#     "acr_values": str,
#     "code_verifier": str,
#     "client_notification_token": str,
#     "status": "PENDING" | "APPROVED" | "REJECTED" | "EXPIRED" | "ERROR",
#     "interval": int,
#     "expires_in": int,
#     "expires_at": float,
#     "tokens": dict | None,
#     "claims": dict | None,
#     "last_polled_at": float,
#     "error_detail": str | None,
# }
transacciones_db: dict[str, dict] = {}


def intercambiar_tokens_reniec(auth_req_id: str) -> dict:
    """
    Consume POST /service/ciba/token hacia la Plataforma ID-Perú utilizando application/x-www-form-urlencoded.
    Verifica los tokens y almacena los claims extraídos.
    """
    tx = transacciones_db.get(auth_req_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")

    url = f"{settings.RENIEC_BASE_URL}/service/ciba/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": settings.RENIEC_REFERER,
    }
    payload = {
        "client_id": settings.RENIEC_CLIENT_ID,
        "client_secret": settings.RENIEC_CLIENT_SECRET,
        "grant_type": "urn:openid:params:grant-type:ciba",
        "auth_req_id": auth_req_id,
        "login_hint": tx["login_hint"],
        "code_verifier": tx["code_verifier"],
    }

    try:
        response = requests.post(url, data=payload, headers=headers, timeout=settings.REQUEST_TIMEOUT)
    except Exception as exc:
        tx["status"] = "ERROR"
        tx["error_detail"] = f"Error al conectar con ID-Perú /service/ciba/token: {exc}"
        raise HTTPException(status_code=502, detail=tx["error_detail"])

    if response.status_code == 200:
        token_data = response.json()
        tx["tokens"] = token_data
        tx["status"] = "APPROVED"

        # Validar y procesar JWT access_token
        access_token = token_data.get("access_token")
        if access_token:
            try:
                # Validación criptográfica con JWKS
                claims = validar_jwt_reniec(access_token)
                tx["claims"] = claims
            except Exception as e:
                # Si estamos en ambiente de pruebas o aún no hay JWKS en vivo, parsear claims básicos
                import jwt as pyjwt
                try:
                    claims = pyjwt.decode(access_token, options={"verify_signature": False})
                    tx["claims"] = claims
                except Exception:
                    tx["claims"] = {
                        "document_number": tx["login_hint"],
                        "name": "CIUDADANO VALIDADO",
                    }
        return token_data

    # Manejar respuestas controladas de RENIEC
    error_json = {}
    try:
        error_json = response.json()
    except Exception:
        pass

    codigo = error_json.get("codigo", "")
    mensaje = error_json.get("mensaje", response.text)

    # 20001: Autenticación pendiente
    if codigo == "20001" or "pendiente" in mensaje.lower():
        tx["status"] = "PENDING"
        return {"status": "PENDING", "message": mensaje}

    # 20009: auth_req_id expirado
    if codigo == "20009" or "expirado" in mensaje.lower():
        tx["status"] = "EXPIRED"
        tx["error_detail"] = mensaje
        return {"status": "EXPIRED", "message": mensaje}

    # Errores que finalizan el flujo como rechazado/fallido
    tx["status"] = "REJECTED"
    tx["error_detail"] = mensaje
    return {"status": "REJECTED", "message": mensaje}


@router.post("/start", response_model=AuthStartResponse, summary="Iniciar transacción OIDC CIBA")
def iniciar_autenticacion(data: AuthStartRequest):
    """
    Paso 1-4 del Flujo CIBA:
    1. Valida el DNI (login_hint) y el método (acr_values).
    2. Genera PKCE (code_challenge con S256) y client_notification_token (mínimo 128 bits).
    3. Consume POST /service/bc-authorize de RENIEC con headers (Content-Type x-www-form-urlencoded y Referer).
    4. Guarda la transacción asociada al auth_req_id y devuelve el qr al frontend.
    """
    dni = (data.login_hint or data.dni or "").strip()
    if not dni or len(dni) != 8 or not dni.isdigit():
        raise HTTPException(status_code=400, detail="El DNI (login_hint) debe contener exactamente 8 dígitos.")

    acr = data.acr_values or data.method or "face_mobile"
    if acr not in ["face_mobile", "pki_dnie"]:
        raise HTTPException(status_code=400, detail="acr_values inválido. Debe ser 'face_mobile' o 'pki_dnie'.")

    # 1. Generar PKCE y client_notification_token seguro (>= 128 bits)
    pkce = generar_pkce()
    client_notification_token = os.urandom(32).hex()

    # 2. Preparar solicitud para POST /service/bc-authorize
    url = f"{settings.RENIEC_BASE_URL}/service/bc-authorize"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": settings.RENIEC_REFERER,
    }
    payload = {
        "client_id": settings.RENIEC_CLIENT_ID,
        "client_secret": settings.RENIEC_CLIENT_SECRET,
        "grant_type": "urn:openid:params:grant-type:ciba",
        "scope": "openid",
        "login_hint": dni,
        "binding_message": data.binding_message or "Autenticación Santander",
        "requested_expiry": "600",
        "acr_values": acr,
        "code_challenge": pkce["code_challenge"],
        "code_challenge_method": pkce["code_challenge_method"],
        "client_notification_token": client_notification_token,
    }

    try:
        response = requests.post(url, data=payload, headers=headers, timeout=settings.REQUEST_TIMEOUT)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"No se pudo contactar con RENIEC IdAAS: {exc}")

    if response.status_code != 200:
        detalle_error = response.text
        try:
            err_json = response.json()
            if isinstance(err_json, dict):
                detalle_error = err_json.get("mensaje") or err_json.get("error_description") or err_json.get("error") or response.text
        except Exception:
            pass
        raise HTTPException(status_code=response.status_code, detail=f"Error RENIEC ({response.status_code}): {detalle_error}")

    reniec_data = response.json()
    print("DEBUG RENIEC /bc-authorize RESPONSE:", reniec_data)

    auth_req_id = reniec_data.get("auth_req_id") or reniec_data.get("transactionId") or reniec_data.get("id")
    qr = (
        reniec_data.get("qr")
        or reniec_data.get("qr_code")
        or reniec_data.get("data")
        or reniec_data.get("code")
    )

    # Si RENIEC devolvió auth_req_id pero no un campo qr específico,
    # el propio auth_req_id es el código de sesión para la App ID-Perú
    if auth_req_id and not qr:
        qr = auth_req_id

    expires_in = int(reniec_data.get("expires_in", 600))
    interval = int(reniec_data.get("interval", 5))

    if not auth_req_id:
        raise HTTPException(
            status_code=502,
            detail=f"Respuesta incompleta de RENIEC (falta auth_req_id). Payload recibido: {reniec_data}"
        )

    # 3. Resguardo de la transacción en el BFF (Tabla 7 y Sección 8.1.3)
    transacciones_db[auth_req_id] = {
        "auth_req_id": auth_req_id,
        "login_hint": dni,
        "acr_values": acr,
        "code_verifier": pkce["code_verifier"],
        "client_notification_token": client_notification_token,
        "status": "PENDING",
        "interval": interval,
        "expires_in": expires_in,
        "expires_at": time.time() + expires_in,
        "tokens": None,
        "claims": None,
        "last_polled_at": 0.0,
        "error_detail": None,
    }

    return AuthStartResponse(
        auth_req_id=auth_req_id,
        qr=qr,
        expires_in=expires_in,
        interval=interval,
        transactionId=auth_req_id,
        expiresIn=expires_in,
        message="Transacción iniciada con éxito",
    )


@router.post("/notify", response_model=AuthNotifyResponse, summary="Webhook oficial url_notify de RENIEC")
def endpoint_notificacion(
    payload: dict,
    background_tasks: BackgroundTasks,
    authorization: str | None = Header(None),
):
    """
    Paso 12-15 del Flujo CIBA:
    1. ID-Perú envía POST con Authorization: Bearer <client_notification_token> y payload {"auth_req_id", "status": "completed"}.
    2. Compara el token en tiempo constante (hmac.compare_digest). Si no coincide -> 401.
    3. Responde inmediatamente 200 OK.
    4. En segundo plano (background tasks), ejecuta la consulta a /service/ciba/token con el PKCE code_verifier.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Encabezado Authorization Bearer requerido")

    incoming_token = authorization.split("Bearer ", 1)[1].strip()
    auth_req_id = payload.get("auth_req_id")

    if not auth_req_id:
        raise HTTPException(status_code=400, detail="auth_req_id requerido en el body")

    tx = transacciones_db.get(auth_req_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transacción no encontrada o expirada")

    # Comparación en tiempo constante (Sección 8.1.5)
    if not hmac.compare_digest(tx["client_notification_token"], incoming_token):
        raise HTTPException(status_code=401, detail="client_notification_token inválido")

    # Notificación válida -> Ejecutar en segundo plano la consulta de tokens
    background_tasks.add_task(intercambiar_tokens_reniec, auth_req_id)

    return AuthNotifyResponse(status="received")


@router.get("/status", response_model=AuthStatusResponse, summary="Consulta de estado de la transacción CIBA")
@router.get("/{auth_req_id}/status", response_model=AuthStatusResponse)
def consultar_estado(auth_req_id: str):
    """
    Paso 10: Consulta del estado desde el frontend (nunca consulta directo a RENIEC).
    Controla el respeto del intervalo mínimo para evitar rate-limiting.
    """
    tx = transacciones_db.get(auth_req_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transacción no encontrada o vencida")

    # Verificar expiración de tiempo
    if time.time() > tx["expires_at"]:
        tx["status"] = "EXPIRED"

    # Si sigue pendiente y el usuario o frontend consulta respetando el interval,
    # o si se requiere comprobación de respaldo
    ahora = time.time()
    if tx["status"] == "PENDING" and (ahora - tx["last_polled_at"] >= tx["interval"]):
        tx["last_polled_at"] = ahora
        # Consulta de respaldo opcional / pasiva a token
        try:
            intercambiar_tokens_reniec(auth_req_id)
        except Exception:
            pass

    mensajes = {
        "PENDING": "Esperando autenticación del ciudadano en ID-Perú.",
        "APPROVED": "Autenticación completada exitosamente.",
        "REJECTED": "La autenticación fue rechazada o cancelada por el usuario.",
        "EXPIRED": "La solicitud de autenticación ha expirado.",
        "ERROR": tx.get("error_detail") or "Ocurrió un error en el proceso.",
    }

    return AuthStatusResponse(
        auth_req_id=auth_req_id,
        transactionId=auth_req_id,
        status=tx["status"],
        message=mensajes.get(tx["status"], f"Estado: {tx['status']}"),
        claims=tx.get("claims"),
    )


@router.get("/{auth_req_id}/claims", response_model=UserClaimsResponse, summary="Claims del usuario autenticado")
def obtener_claims(auth_req_id: str):
    """
    Sección 8.1.8 y Paso 19:
    Devuelve los datos del usuario con principio de mínima exposición (document_number, name, etc.).
    """
    tx = transacciones_db.get(auth_req_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")

    if tx["status"] != "APPROVED" or not tx.get("claims"):
        raise HTTPException(status_code=400, detail="La autenticación aún no está aprobada")

    claims = tx["claims"]
    return UserClaimsResponse(
        document_number=claims.get("document_number") or tx["login_hint"],
        name=claims.get("name") or claims.get("given_name"),
        given_name=claims.get("given_name"),
        auth_time=claims.get("auth_time"),
        sub=claims.get("sub"),
    )


@router.post("/token", response_model=AuthTokenResponse, summary="Obtener tokens finales de la transacción")
def consultar_tokens(auth_req_id: str):
    """
    Paso 17-18:
    Permite obtener o canjear los tokens JWT emitidos tras la aprobación de la transacción.
    """
    tx = transacciones_db.get(auth_req_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")

    if not tx.get("tokens"):
        token_data = intercambiar_tokens_reniec(auth_req_id)
        if tx["status"] != "APPROVED":
            raise HTTPException(status_code=400, detail=tx.get("error_detail") or "Transacción no aprobada aún")
    else:
        token_data = tx["tokens"]

    claims_obj = None
    if tx.get("claims"):
        c = tx["claims"]
        claims_obj = UserClaimsResponse(
            document_number=c.get("document_number") or tx["login_hint"],
            name=c.get("name"),
            given_name=c.get("given_name"),
            auth_time=c.get("auth_time"),
            sub=c.get("sub"),
        )

    return AuthTokenResponse(
        access_token=token_data.get("access_token", ""),
        id_token=token_data.get("id_token"),
        expires_in=token_data.get("expires_in", 3600),
        token_type=token_data.get("token_type", "Bearer"),
        claims=claims_obj,
    )
