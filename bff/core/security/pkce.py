import base64
import hashlib
import os


def generar_pkce() -> dict[str, str]:
    """
    Genera los parámetros PKCE cumpliendo con RFC 7636 y la especificación ID-Perú CIBA v1.3:
    - code_verifier: Cadena aleatoria segura entre 43 y 128 caracteres (A-Z, a-z, 0-9).
    - code_challenge: Base64URL sin padding del hash SHA-256 del code_verifier.
    - code_challenge_method: "S256"
    """
    # 64 bytes de entropía codificados en base64url proporcionan ~86 caracteres sin padding
    verifier_bytes = os.urandom(64)
    code_verifier = (
        base64.urlsafe_b64encode(verifier_bytes).decode("utf-8").rstrip("=")
    )

    digest = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    code_challenge = (
        base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")
    )

    return {
        "code_verifier": code_verifier,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
