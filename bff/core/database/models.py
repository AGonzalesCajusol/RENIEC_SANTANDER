from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa
from sqlmodel import SQLModel, Field, Column, JSON


class CibaTransaction(SQLModel, table=True):
    """
    Tabla de resguardo de transacciones CIBA + PKCE (PostgreSQL).
    Cumple con la Sección 8.1.3 y Sección 10 de la especificación ID-Perú v1.3:
    - Sin sesión en webhook (Punto 1).
    - Resguardo de code_verifier y client_notification_token (Punto 2).
    - Resguardo de resultado único de tokens y claims (Punto 3).
    - Multi-instancia y alta disponibilidad (Punto 4).
    """
    __tablename__ = "ciba_transactions"

    auth_req_id: str = Field(primary_key=True, index=True, max_length=255)
    login_hint: str = Field(index=True, max_length=8)
    acr_values: str = Field(max_length=32)

    # Parámetros criptográficos (RFC 7636 y CIBA)
    code_verifier: str = Field(max_length=128)
    code_challenge: str = Field(max_length=128)
    client_notification_token: str = Field(index=True, max_length=128)

    # Estado del flujo (PENDING, APPROVED, REJECTED, EXPIRED, ERROR)
    status: str = Field(default="PENDING", index=True, max_length=20)
    interval: int = Field(default=5)
    expires_in: int = Field(default=600)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = Field(index=True)
    completed_at: Optional[datetime] = Field(default=None)

    # Tokens JWT y claims de identidad verificados
    tokens: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    claims: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    error_detail: Optional[str] = Field(default=None)


class VerifySession(SQLModel, table=True):
    """
    Tabla de resguardo de sesiones de verificación de credenciales DNId (Perú Pass / Inji Verify).
    """
    __tablename__ = "verify_sessions"

    request_id: str = Field(primary_key=True, index=True, max_length=255)
    transaction_id: str = Field(index=True, max_length=255)
    client_id: str = Field(max_length=255)
    presentation_definition_id: str = Field(max_length=100)
    request_uri: str = Field(max_length=1000)
    qr_data: str = Field(max_length=2000)

    # Estado de la verificación: PENDING, VP_SUBMITTED, COMPLETED, EXPIRED, FAILED
    status: str = Field(default="PENDING", index=True, max_length=30)
    expires_at: Optional[int] = Field(default=None, sa_column=Column(sa.BigInteger))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = Field(default=None)

    # Credencial SD-JWT y datos extraídos
    vc_raw: Optional[str] = Field(default=None)
    claims: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    error_detail: Optional[str] = Field(default=None)
