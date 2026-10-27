import base64
import json
import logging
from typing import Any, Dict

logger = logging.getLogger("sd_jwt")


def decode_base64url(data: str) -> bytes:
    """Decodifica cadenas en Base64URL completando el padding si falta."""
    rem = len(data) % 4
    if rem > 0:
        data += "=" * (4 - rem)
    return base64.urlsafe_b64decode(data)


def parse_sd_jwt_claims(vc_raw: str) -> Dict[str, Any]:
    """
    Decodifica una credencial SD-JWT (Selective Disclosure JWT) según el estándar de Inji / RENIEC.
    Formato: <JWT_EMISOR>~<DISCLOSURE_1>~<DISCLOSURE_2>~...~<KB_JWT>

    Cada disclosure es una tupla JSON codificada en Base64URL: [sal, nombre_campo, valor]
    """
    claims: Dict[str, Any] = {}
    if not vc_raw:
        return claims

    parts = vc_raw.split("~")
    # Los disclosures son las partes intermedias (entre la cabecera/cuerpo del emisor y el key binding jwt final)
    for part in parts[1:]:
        if not part:
            continue
        try:
            decoded_bytes = decode_base64url(part)
            parsed = json.loads(decoded_bytes.decode("utf-8"))
            if isinstance(parsed, list) and len(parsed) >= 3:
                # parsed: [salt, claim_name, claim_value]
                _, claim_name, claim_value = parsed[0], parsed[1], parsed[2]
                claims[claim_name] = claim_value
        except Exception as e:
            # Si no es un disclosure parseable (ej. key binding jwt o padding), se omite
            logger.debug(f"Segmento omitido o no es disclosure SD-JWT: {e}")

    return claims
