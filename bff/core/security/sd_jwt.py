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

    Extrae tanto los metadatos públicos del emisor (RENIEC) como los atributos revelados en disclosures.
    """
    claims: Dict[str, Any] = {}
    if not vc_raw:
        return claims

    parts = vc_raw.split("~")

    # 1. Metadatos generales del JWT del Emisor (RENIEC)
    if parts[0]:
        try:
            jwt_parts = parts[0].split(".")
            if len(jwt_parts) >= 2:
                payload = json.loads(decode_base64url(jwt_parts[1]).decode("utf-8"))
                # Guardamos información institucional relevante
                if "vct" in payload:
                    claims["_tipo_credencial"] = payload["vct"]
                if "iss" in payload:
                    claims["_emisor"] = payload["iss"]
                if "validFrom" in payload:
                    claims["_valido_desde"] = payload["validFrom"]
                if "validUntil" in payload:
                    claims["_valido_hasta"] = payload["validUntil"]
                if "issuanceDate" in payload:
                    claims["_fecha_emision"] = payload["issuanceDate"]
        except Exception as e:
            logger.debug(f"No se pudo extraer el payload del emisor: {e}")

    # 2. Atributos compartidos por el ciudadano (Disclosures)
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
            logger.debug(f"Segmento omitido o no es disclosure SD-JWT: {e}")

    return claims
