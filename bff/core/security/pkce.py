import base64
import hashlib
import os


def generar_pkce() -> dict:
    """
    Genera el par de claves PKCE (code_verifier y code_challenge).
    1. Genera un code_verifier aleatorio (entre 43 y 128 caracteres).
    2. Aplica SHA-256 al code_verifier.
    3. Codifica en Base64URL sin relleno (=) con método S256.
    """
    token_bytes = os.urandom(64)
    code_verifier = base64.urlsafe_b64encode(token_bytes).rstrip(b"=").decode("utf-8")

    sha256_hash = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    code_challenge = base64.urlsafe_b64encode(sha256_hash).rstrip(b"=").decode("utf-8")

    return {
        "code_verifier": code_verifier,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
