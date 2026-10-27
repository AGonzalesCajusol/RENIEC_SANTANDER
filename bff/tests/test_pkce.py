import base64
import hashlib
from core.security.pkce import generar_pkce


def test_generar_pkce_structure():
    pkce = generar_pkce()
    assert "code_verifier" in pkce
    assert "code_challenge" in pkce
    assert pkce["code_challenge_method"] == "S256"

    # RFC 7636 especifica entre 43 y 128 caracteres para code_verifier
    assert 43 <= len(pkce["code_verifier"]) <= 128


def test_generar_pkce_sha256_challenge():
    pkce = generar_pkce()
    verifier = pkce["code_verifier"]
    challenge = pkce["code_challenge"]

    # Re-computar SHA256 base64url sin padding
    digest = hashlib.sha256(verifier.encode("utf-8")).digest()
    expected_challenge = base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")

    assert challenge == expected_challenge
