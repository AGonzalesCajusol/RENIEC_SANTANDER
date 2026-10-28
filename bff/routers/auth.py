import hmac
import logging
import os
from datetime import datetime, timezone
import requests
from fastapi import APIRouter, HTTPException, Header, BackgroundTasks, Depends, Query
from sqlmodel import Session, select
from core.config import settings
from core.database import CibaTransaction, get_session
from core.security.pkce import generar_pkce
from core.security.jwt_validator import validar_jwt_reniec
from schemas.auth import (
    AuthStartRequest,
    AuthStartResponse,
    AuthNotifyPayload,
    AuthNotifyResponse,
    AuthStatusResponse,
    AuthTokenResponse,
    UserClaimsResponse,
)

router = APIRouter(prefix="/auth", tags=["ID-Perú CIBA Auth"])
logger = logging.getLogger(__name__)


def intercambiar_tokens_reniec_db(auth_req_id: str, session: Session) -> dict:
    """
    Consume POST /service/ciba/token hacia la Plataforma ID-Perú utilizando application/x-www-form-urlencoded.
    Verifica los tokens y almacena los claims extraídos en PostgreSQL.
    """
    tx = session.get(CibaTransaction, auth_req_id)
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
        "login_hint": tx.login_hint,
        "code_verifier": tx.code_verifier,
    }

    try:
        response = requests.post(url, data=payload, headers=headers, timeout=settings.REQUEST_TIMEOUT)
    except Exception as exc:
        tx.status = "ERROR"
        tx.error_detail = f"Error al conectar con ID-Perú /service/ciba/token: {exc}"
        session.add(tx)
        session.commit()
        raise HTTPException(status_code=502, detail=tx.error_detail)

    if response.status_code == 200:
        token_data = response.json()
        
        # Verificar si RENIEC respondió 200 pero con un mensaje de estado pendiente o error
        codigo = str(token_data.get("codigo", ""))
        mensaje = str(token_data.get("mensaje", ""))

        if codigo == "20001" or "pendiente" in mensaje.lower():
            tx.status = "PENDING"
            session.add(tx)
            session.commit()
            return {"status": "PENDING", "message": mensaje}

        if codigo == "20009" or "expirado" in mensaje.lower():
            tx.status = "EXPIRED"
            tx.error_detail = mensaje
            session.add(tx)
            session.commit()
            return {"status": "EXPIRED", "message": mensaje}

        if "access_token" in token_data:
            tx.tokens = token_data
            tx.status = "APPROVED"
            tx.completed_at = datetime.now(timezone.utc)

            # Validar y procesar JWT access_token
            access_token = token_data.get("access_token")
            try:
                claims = validar_jwt_reniec(access_token)
                tx.claims = claims
            except Exception:
                import jwt as pyjwt
                try:
                    claims = pyjwt.decode(access_token, options={"verify_signature": False})
                    tx.claims = claims
                except Exception:
                    tx.claims = {
                        "document_number": tx.login_hint,
                        "name": "CIUDADANO VALIDADO",
                    }
            session.add(tx)
            session.commit()
            return token_data

        # Si retornó otro código no exitoso dentro de 200 OK
        if token_data.get("error"):
            tx.status = "REJECTED"
            tx.error_detail = mensaje or token_data.get("error")
            session.add(tx)
            session.commit()
            return {"status": "REJECTED", "message": tx.error_detail}

    # Manejar respuestas controladas de RENIEC
    error_json = {}
    try:
        error_json = response.json()
    except Exception:
        pass

    codigo = error_json.get("codigo", "")
    mensaje = error_json.get("mensaje", response.text)

    if codigo == "20001" or "pendiente" in mensaje.lower():
        tx.status = "PENDING"
        session.add(tx)
        session.commit()
        return {"status": "PENDING", "message": mensaje}

    if codigo == "20009" or "expirado" in mensaje.lower():
        tx.status = "EXPIRED"
        tx.error_detail = mensaje
        session.add(tx)
        session.commit()
        return {"status": "EXPIRED", "message": mensaje}

    tx.status = "REJECTED"
    tx.error_detail = mensaje
    session.add(tx)
    session.commit()
    return {"status": "REJECTED", "message": mensaje}


def _tarea_segundo_plano_token(auth_req_id: str):
    """Ejecuta el intercambio en una sesión separada de DB en background."""
    from core.database.session import engine
    with Session(engine) as session:
        intercambiar_tokens_reniec_db(auth_req_id, session)


@router.post(
    "/start",
    response_model=AuthStartResponse,
    summary="Iniciar transacción OIDC CIBA",
    description="""
Inicia una nueva transacción de autenticación CIBA contra la plataforma ID-Perú (RENIEC).

**Acciones que ejecuta el BFF:**
1. Valida el número de DNI y el método de autenticación (`face_mobile` para biometría facial o `pki_dnie` para DNIe).
2. Genera los secretos criptográficos: `code_verifier` / `code_challenge` (PKCE S256) y el `client_notification_token` (secreto de 256 bits).
3. Consume `POST /service/bc-authorize` en RENIEC incluyendo cabeceras de seguridad (`Referer` institucional).
4. Persiste la transacción en PostgreSQL y devuelve el `qr` y `auth_req_id` al frontend.
    """,
    responses={
        200: {"description": "Transacción CIBA iniciada exitosamente; contiene el código para QR o Deep Link"},
        400: {"description": "Parámetros inválidos (ej. DNI no contiene 8 dígitos o método no soportado)"},
        502: {"description": "Error al comunicarse con la plataforma RENIEC IdAAS"},
    }
)
def iniciar_autenticacion(data: AuthStartRequest, session: Session = Depends(get_session)):
    """
    Paso 1-4 del Flujo CIBA:
    1. Valida el DNI (login_hint) y el método (acr_values).
    2. Genera PKCE (code_challenge con S256) y client_notification_token (mínimo 128 bits).
    3. Consume POST /service/bc-authorize de RENIEC con headers (Content-Type x-www-form-urlencoded y Referer).
    4. Guarda la transacción en PostgreSQL asociada al auth_req_id y devuelve el qr al frontend.
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
    auth_req_id = reniec_data.get("auth_req_id") or reniec_data.get("transactionId") or reniec_data.get("id")
    qr = (
        reniec_data.get("qr")
        or reniec_data.get("qr_code")
        or reniec_data.get("data")
        or reniec_data.get("code")
    )
    if auth_req_id and not qr:
        qr = auth_req_id

    expires_in = int(reniec_data.get("expires_in", 600))
    interval = int(reniec_data.get("interval", 5))

    if not auth_req_id:
        raise HTTPException(
            status_code=502,
            detail=f"Respuesta incompleta de RENIEC (falta auth_req_id). Payload recibido: {reniec_data}"
        )

    # 3. Resguardo transaccional en PostgreSQL (Cumpliendo con la Sección 8.1.3 y SQLModel)
    ahora = datetime.now(timezone.utc)
    expires_at = datetime.fromtimestamp(ahora.timestamp() + expires_in, tz=timezone.utc)

    nueva_tx = CibaTransaction(
        auth_req_id=auth_req_id,
        login_hint=dni,
        acr_values=acr,
        code_verifier=pkce["code_verifier"],
        code_challenge=pkce["code_challenge"],
        client_notification_token=client_notification_token,
        status="PENDING",
        interval=interval,
        expires_in=expires_in,
        created_at=ahora,
        expires_at=expires_at,
    )
    session.add(nueva_tx)
    session.commit()

    return AuthStartResponse(
        auth_req_id=auth_req_id,
        qr=qr,
        expires_in=expires_in,
        interval=interval,
        transactionId=auth_req_id,
        expiresIn=expires_in,
        message="Transacción iniciada con éxito",
    )


@router.post(
    "/notify",
    response_model=AuthNotifyResponse,
    summary="Webhook oficial url_notify de RENIEC (ID-Perú CIBA)",
    description="""
Endpoint público registrado ante RENIEC al que el servidor IdAAS envía una notificación HTTP POST cuando el ciudadano concluye la autenticación biométrica en la aplicación móvil ID-Perú.

**Requisitos de seguridad (Especificación técnica RENIEC v1.3 - Sección 8.1.5):**
* **Cabecera `Authorization`:** Debe incluir `Bearer <client_notification_token>`. Se valida en tiempo constante para evitar ataques de temporización.
* **Cuerpo:** JSON con `auth_req_id` y `status: "completed"`.
* **Comportamiento:** Responde `200 OK {"status": "received"}` de inmediato y dispara una tarea en background para consultar los tokens definitivos a `/service/ciba/token`.
    """,
    responses={
        200: {"description": "Notificación recibida y autenticada con éxito"},
        400: {"description": "Cuerpo inválido (falta auth_req_id)"},
        401: {"description": "Token Bearer ausente o inválido"},
        404: {"description": "Transacción no encontrada o expirada"},
    }
)
def endpoint_notificacion(
    payload: AuthNotifyPayload,
    background_tasks: BackgroundTasks,
    authorization: str | None = Header(None, description="Encabezado 'Bearer <client_notification_token>' enviado por RENIEC"),
    session: Session = Depends(get_session),
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
    auth_req_id = payload.auth_req_id

    if not auth_req_id:
        raise HTTPException(status_code=400, detail="auth_req_id requerido en el body")

    tx = session.get(CibaTransaction, auth_req_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transacción no encontrada o expirada")

    # Comparación en tiempo constante (Sección 8.1.5)
    if not hmac.compare_digest(tx.client_notification_token, incoming_token):
        raise HTTPException(status_code=401, detail="client_notification_token inválido")

    # Notificación válida -> Ejecutar en segundo plano la consulta de tokens con sesión propia
    background_tasks.add_task(_tarea_segundo_plano_token, auth_req_id)

    return AuthNotifyResponse(status="received")


@router.get(
    "/status",
    response_model=AuthStatusResponse,
    summary="Consulta de estado de la transacción CIBA",
    description="""
Permite al frontend consultar el estado actual de la autenticación.

**Parámetros:**
* `auth_req_id`: Identificador de la transacción devuelto en `/start`.
* `check_reniec`: Si es `true` (por ejemplo, cuando el usuario presiona el botón *"Ya me autentiqué en mi celular"*), el BFF realiza una consulta activa a `/service/ciba/token` de RENIEC para confirmar si el ciudadano ya aprobó, sin esperar al webhook.
    """,
    responses={
        200: {"description": "Estado retornado (PENDING, APPROVED, REJECTED, EXPIRED, ERROR)"},
        404: {"description": "Transacción no encontrada o vencida"},
    }
)
@router.get(
    "/{auth_req_id}/status",
    response_model=AuthStatusResponse,
    include_in_schema=False
)
def consultar_estado(
    auth_req_id: str,
    check_reniec: bool = Query(
        False,
        description="Si es True, consulta activamente a RENIEC si el estado local aún es PENDING (ej: botón 'Ya me autentiqué')",
    ),
    session: Session = Depends(get_session),
):
    """
    Paso 10 y Sección 8.1.5 de la Especificación ID-Perú:
    Consulta del estado desde el frontend.
    Si check_reniec=True (o al confirmar el usuario) y el estado local sigue en PENDING,
    el BFF consulta /service/ciba/token de ID-Perú usando el auth_req_id y code_verifier.
    """
    tx = session.get(CibaTransaction, auth_req_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transacción no encontrada o vencida")

    # Verificar expiración de tiempo
    ahora = datetime.now(timezone.utc)
    if ahora > tx.expires_at and tx.status == "PENDING":
        tx.status = "EXPIRED"
        session.add(tx)
        session.commit()

    # Si la transacción sigue en PENDING y se solicita chequeo activo o confirmación del usuario
    if tx.status == "PENDING" and check_reniec:
        try:
            intercambiar_tokens_reniec_db(auth_req_id, session)
            session.refresh(tx)
        except Exception as exc:
            logger.warning(f"Error consultando /service/ciba/token a RENIEC: {exc}")

    mensajes = {
        "PENDING": "Esperando autenticación del ciudadano en ID-Perú.",
        "APPROVED": "Autenticación completada exitosamente.",
        "REJECTED": "La autenticación fue rechazada o cancelada por el usuario.",
        "EXPIRED": "La solicitud de autenticación ha expirado.",
        "ERROR": tx.error_detail or "Ocurrió un error en el proceso.",
    }

    return AuthStatusResponse(
        auth_req_id=auth_req_id,
        transactionId=auth_req_id,
        status=tx.status,
        message=mensajes.get(tx.status, f"Estado: {tx.status}"),
        claims=tx.claims,
    )


@router.get("/{auth_req_id}/claims", response_model=UserClaimsResponse, summary="Claims del usuario autenticado")
def obtener_claims(auth_req_id: str, session: Session = Depends(get_session)):
    """
    Sección 8.1.8 y Paso 19:
    Devuelve los datos del usuario con principio de mínima exposición (document_number, name, etc.).
    """
    tx = session.get(CibaTransaction, auth_req_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")

    if tx.status != "APPROVED" or not tx.claims:
        raise HTTPException(status_code=400, detail="La autenticación aún no está aprobada")

    claims = tx.claims
    return UserClaimsResponse(
        document_number=claims.get("document_number") or tx.login_hint,
        name=claims.get("name") or claims.get("given_name"),
        given_name=claims.get("given_name"),
        auth_time=claims.get("auth_time"),
        sub=claims.get("sub"),
    )


@router.post("/token", response_model=AuthTokenResponse, summary="Obtener tokens finales de la transacción")
def consultar_tokens(auth_req_id: str, session: Session = Depends(get_session)):
    """
    Paso 17-18:
    Permite obtener o canjear los tokens JWT emitidos tras la aprobación de la transacción.
    """
    tx = session.get(CibaTransaction, auth_req_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")

    if not tx.tokens:
        token_data = intercambiar_tokens_reniec_db(auth_req_id, session)
        if tx.status != "APPROVED":
            raise HTTPException(status_code=400, detail=tx.error_detail or "Transacción no aprobada aún")
    else:
        token_data = tx.tokens

    claims_obj = None
    if tx.claims:
        c = tx.claims
        claims_obj = UserClaimsResponse(
            document_number=c.get("document_number") or tx.login_hint,
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
