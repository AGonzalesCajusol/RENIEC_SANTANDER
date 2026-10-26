from typing import Optional
from pydantic import BaseModel, Field


class AuthStartRequest(BaseModel):
    # Soporta tanto login_hint (técnico ID-Perú) como dni (frontend)
    login_hint: Optional[str] = Field(None, description="Número de DNI del ciudadano", example="12345678")
    dni: Optional[str] = Field(None, description="Alias para número de DNI", example="12345678")
    acr_values: Optional[str] = Field(None, description="Nivel/método ('face_mobile' o 'pki_dnie')", example="face_mobile")
    method: Optional[str] = Field(None, description="Alias para acr_values", example="face_mobile")
    binding_message: Optional[str] = Field("Autenticación Santander", description="Mensaje asociado a la transacción")


class AuthStartResponse(BaseModel):
    auth_req_id: str
    qr: str
    expires_in: int
    interval: int
    # Campos normalizados para el frontend
    transactionId: str
    expiresIn: int
    message: str = "Transacción CIBA iniciada"


class AuthNotifyPayload(BaseModel):
    auth_req_id: str
    status: str = "completed"


class AuthNotifyResponse(BaseModel):
    status: str = "received"


class AuthStatusResponse(BaseModel):
    auth_req_id: str
    transactionId: str
    status: str  # PENDING, APPROVED, REJECTED, EXPIRED, ERROR
    message: Optional[str] = None
    claims: Optional[dict] = None


class UserClaimsResponse(BaseModel):
    document_number: Optional[str] = None
    name: Optional[str] = None
    given_name: Optional[str] = None
    auth_time: Optional[int] = None
    sub: Optional[str] = None


class AuthTokenResponse(BaseModel):
    access_token: str
    id_token: Optional[str] = None
    expires_in: Optional[int] = 3600
    token_type: Optional[str] = "Bearer"
    claims: Optional[UserClaimsResponse] = None
