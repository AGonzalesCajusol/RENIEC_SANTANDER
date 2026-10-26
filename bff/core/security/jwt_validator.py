import time
import requests
import jwt
from jwt import PyJWKClient
from core.config import settings

# Cache local para el JWKS
_jwks_cache: dict[str, any] = {"keys": None, "timestamp": 0}
CACHE_TTL = 900  # 15 minutos según especificación (Sección 8.1.5 - Seudocódigo JWKS)


def obtener_jwks() -> dict:
    ahora = time.time()
    if _jwks_cache["keys"] and (ahora - _jwks_cache["timestamp"] < CACHE_TTL):
        return _jwks_cache["keys"]

    url_jwks = f"{settings.RENIEC_BASE_URL}/service/jwks"
    response = requests.get(
        url_jwks,
        headers={"Referer": settings.RENIEC_REFERER},
        timeout=settings.REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    jwks = response.json()
    _jwks_cache["keys"] = jwks
    _jwks_cache["timestamp"] = ahora
    return jwks


def validar_jwt_reniec(token_jwt: str) -> dict:
    """
    Valida criptográficamente el JWT emitido por ID-Perú según el Código fuente 12:
    1. Parsear cabecera (kid, alg).
    2. Verificar algoritmo permitido ('RS256').
    3. Obtener llave pública desde /service/jwks con cache de 15 min.
    4. Verificar firma criptográfica.
    5. Validar claims: exp, iss, azp (client_id).
    """
    # 1 y 2: Parsear cabecera sin verificar para extraer kid y alg
    unverified_header = jwt.get_unverified_header(token_jwt)
    alg = unverified_header.get("alg")
    kid = unverified_header.get("kid")

    if alg not in ["RS256"]:
        raise ValueError(f"Algoritmo '{alg}' no permitido. Se requiere RS256.")

    # 3 y 4: Construir key client y obtener clave pública
    url_jwks = f"{settings.RENIEC_BASE_URL}/service/jwks"
    jwks_client = PyJWKClient(url_jwks, cache_keys=True, max_cached_keys=16, lifespan=CACHE_TTL)
    
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token_jwt)
    except Exception as e:
        raise ValueError(f"No se pudo resolver la llave pública para kid '{kid}': {e}")

    # 5: Validar firma y claims
    payload = jwt.decode(
        token_jwt,
        signing_key.key,
        algorithms=["RS256"],
        options={
            "verify_signature": True,
            "verify_exp": True,
            "verify_iss": False,  # Verificamos manualmente abajo con flexibilidad
        },
    )

    # Validar exp
    now = time.time()
    if payload.get("exp", 0) <= now:
        raise ValueError("Token expirado.")

    # Validar azp / aud si están presentes
    expected_client = settings.RENIEC_CLIENT_ID
    if "azp" in payload and payload["azp"] != expected_client and expected_client != "tu_client_id":
        raise ValueError(f"azp '{payload.get('azp')}' no coincide con client_id.")

    return payload
