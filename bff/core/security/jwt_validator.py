import jwt
from jwt import PyJWKClient
from core.config import settings

# PyJWKClient maneja automáticamente la caché de las llaves públicas
jwk_client = PyJWKClient(settings.RENIEC_JWKS_URL)


def validar_jwt_reniec(token_jwt: str, expected_client_id: str | None = None) -> dict:
    """
    Descarga llaves públicas del endpoint JWKS de RENIEC, verifica la firma digital
    RS256, comprueba expiración (exp) y valida claims obligatorios (iss, azp, aud).
    """
    target_client_id = expected_client_id or settings.RENIEC_CLIENT_ID

    try:
        # 1. Obtener la llave pública correcta basada en el 'kid' del header del JWT
        signing_key = jwk_client.get_signing_key_from_jwt(token_jwt)

        # 2. Verificar firma, algoritmo (RS256), expiración y claims
        payload = jwt.decode(
            token_jwt,
            signing_key.key,
            algorithms=["RS256"],
            audience=target_client_id,
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iss": True,
            },
            issuer=settings.RENIEC_ISSUER,
        )

        # 3. Validaciones adicionales recomendadas por la especificación CIBA
        if payload.get("iss") != settings.RENIEC_ISSUER:
            raise ValueError(f"Issuer (iss) inválido: {payload.get('iss')}")

        if payload.get("azp") and payload.get("azp") != target_client_id:
            raise ValueError("El cliente (azp) no coincide con el client_id esperado")

        return {"valido": True, "claims": payload}

    except jwt.ExpiredSignatureError:
        return {"valido": False, "error": "Token expirado"}
    except jwt.InvalidTokenError as e:
        return {"valido": False, "error": f"Token inválido: {str(e)}"}
    except Exception as e:
        return {"valido": False, "error": str(e)}
