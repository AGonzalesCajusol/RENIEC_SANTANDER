import urllib.parse
from datetime import datetime, timezone
import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session
from typing import Optional, Dict, Any

from core.config import settings
from core.database import get_session
from core.database.models import VerifySession
from core.security.sd_jwt import parse_sd_jwt_claims

router = APIRouter(prefix="/dni-digital", tags=["DNI Digital (Perú Pass)"])


class InitVerifyRequest(BaseModel):
    documentType: str = "DNI"
    purpose: str = "ONBOARDING_DIGITAL"
    presentationDefinitionId: Optional[str] = None


class InitVerifyResponse(BaseModel):
    requestId: str
    transactionId: str
    qrData: str
    expiresAt: Optional[int]


class VerifyStatusResponse(BaseModel):
    status: str  # PENDING | COMPLETED | EXPIRED | REJECTED | ERROR
    verifiedData: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


def build_openid4vp_uri(client_id: str, request_uri: str) -> str:
    """Construye el enlace URI openid4vp://authorize con percent-encoding."""
    encoded_client_id = urllib.parse.quote(client_id, safe="")
    encoded_request_uri = urllib.parse.quote(request_uri, safe="")
    return f"openid4vp://authorize?client_id={encoded_client_id}&request_uri={encoded_request_uri}"


@router.post("/init", response_model=InitVerifyResponse)
async def init_verification(
    payload: InitVerifyRequest,
    db: Session = Depends(get_session)
):
    """
    Paso 1 del flujo: Inicializa la solicitud de verificación contra el contenedor local de Verify (:8081).
    Genera la URL openid4vp:// lista para ser renderizada en código QR o invocada vía Deeplink en Perú Pass.
    """
    definition_id = payload.presentationDefinitionId or settings.VERIFY_PRESENTATION_DEFINITION_ID
    verify_url = f"{settings.VERIFY_SERVICE_INTERNAL_URL}/vp-request"

    request_payload = {
        "clientId": settings.VERIFY_CLIENT_ID,
        "presentationDefinitionId": definition_id,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(verify_url, json=request_payload)
            if resp.status_code not in (200, 201):
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Verify Service error ({resp.status_code}): {resp.text}"
                )
            data = resp.json()
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"No se pudo conectar con el servicio local de verificación en {verify_url}: {e}"
        )

    transaction_id = data["transactionId"]
    request_id = data["requestId"]
    expires_at = data.get("expiresAt")
    request_uri = data["requestUri"]

    qr_data = build_openid4vp_uri(settings.VERIFY_CLIENT_ID, request_uri)

    session = VerifySession(
        request_id=request_id,
        transaction_id=transaction_id,
        client_id=settings.VERIFY_CLIENT_ID,
        presentation_definition_id=definition_id,
        request_uri=request_uri,
        qr_data=qr_data,
        status="PENDING",
        expires_at=expires_at,
    )
    db.add(session)
    db.commit()

    return InitVerifyResponse(
        requestId=request_id,
        transactionId=transaction_id,
        qrData=qr_data,
        expiresAt=expires_at,
    )


@router.get("/status/{request_id}", response_model=VerifyStatusResponse)
async def get_verification_status(
    request_id: str,
    db: Session = Depends(get_session)
):
    """
    Paso 2 y 3 del flujo: Consulta de estado de la verificación para el Frontend.
    Realiza consulta no bloqueante hacia el contenedor Verify y extrae los claims al completarse.
    """
    session = db.get(VerifySession, request_id)
    if not session:
        raise HTTPException(status_code=404, detail="Solicitud de verificación no encontrada.")

    # Si ya fue completada previamente en la BD, responder directamente
    if session.status == "COMPLETED":
        return VerifyStatusResponse(
            status="COMPLETED",
            verifiedData=session.claims,
            message="Identidad verificada exitosamente"
        )

    status_url = f"{settings.VERIFY_SERVICE_INTERNAL_URL}/vp-request/{request_id}/status"

    try:
        # Usamos timeout corto para que la consulta al BFF sea rápida y no bloquee el hilo web
        async with httpx.AsyncClient(timeout=settings.VERIFY_POLLING_TIMEOUT_SEC) as client:
            resp = await client.get(status_url)
            if resp.status_code == 200:
                verify_status_data = resp.json()
                raw_status = verify_status_data.get("status")

                if raw_status == "VP_SUBMITTED":
                    # El usuario presentó la credencial en Perú Pass: obtenemos el resultado final
                    result_url = f"{settings.VERIFY_SERVICE_INTERNAL_URL}/vp-result/{session.transaction_id}"
                    res_resp = await client.get(result_url)
                    if res_resp.status_code == 200:
                        res_data = res_resp.json()
                        if res_data.get("vpResultStatus") == "SUCCESS":
                            vc_results = res_data.get("vcResults", [])
                            vc_raw = vc_results[0].get("vc") if vc_results else None
                            
                            claims = parse_sd_jwt_claims(vc_raw) if vc_raw else {}
                            
                            session.status = "COMPLETED"
                            session.vc_raw = vc_raw
                            session.claims = claims
                            session.completed_at = datetime.now(timezone.utc)
                            db.add(session)
                            db.commit()

                            return VerifyStatusResponse(
                                status="COMPLETED",
                                verifiedData=claims,
                                message="Verificación completada satisfactoriamente con Perú Pass"
                            )
                elif raw_status == "EXPIRED":
                    session.status = "EXPIRED"
                    db.add(session)
                    db.commit()
                    return VerifyStatusResponse(status="EXPIRED", message="El código QR ha expirado")
                elif raw_status in ("REJECTED", "FAILED"):
                    session.status = "REJECTED"
                    db.add(session)
                    db.commit()
                    return VerifyStatusResponse(status="REJECTED", message="El usuario canceló la presentación")

    except httpx.TimeoutException:
        # El endpoint de Verify hace long-polling: si expira el timeout local de 2s, significa que sigue PENDING
        pass
    except httpx.RequestError as e:
        # Error de red con el contenedor
        return VerifyStatusResponse(status="PENDING", message=f"Consultando servicio... ({e})")

    return VerifyStatusResponse(status="PENDING", message="Esperando escaneo y autorización en Perú Pass...")
