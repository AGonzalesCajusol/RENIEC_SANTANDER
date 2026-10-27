import time
import requests
from fastapi import APIRouter
from core.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check():
    return {"status": "ok", "service": "RENIEC Santander BFF"}


@router.get("/health/reniec")
def health_check_reniec():
    """
    Verifica la conectividad real con la plataforma ID-Perú de RENIEC:
    1. Consulta el endpoint público JWKS (/service/jwks).
    2. Comprueba si el host es alcanzable, latencia y si el Referer es admitido.
    """
    url_jwks = f"{settings.RENIEC_BASE_URL}/service/jwks"
    headers = {"Referer": settings.RENIEC_REFERER}
    
    start_time = time.time()
    try:
        response = requests.get(url_jwks, headers=headers, timeout=settings.REQUEST_TIMEOUT)
        latency_ms = round((time.time() - start_time) * 1000, 2)
        
        is_ok = response.status_code == 200
        jwks_data = response.json() if is_ok else None
        total_keys = len(jwks_data.get("keys", [])) if jwks_data else 0

        return {
            "status": "UP" if is_ok else "DEGRADED",
            "reniec_base_url": settings.RENIEC_BASE_URL,
            "jwks_endpoint": url_jwks,
            "http_status": response.status_code,
            "latency_ms": latency_ms,
            "connected": is_ok,
            "available_keys": total_keys,
            "client_id_configured": bool(settings.RENIEC_CLIENT_ID and settings.RENIEC_CLIENT_ID != "tu_client_id"),
        }
    except Exception as exc:
        return {
            "status": "DOWN",
            "reniec_base_url": settings.RENIEC_BASE_URL,
            "connected": False,
            "error": str(exc),
        }
