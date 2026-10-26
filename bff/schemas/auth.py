from pydantic import BaseModel, Field


class AuthStartRequest(BaseModel):
    login_hint: str = Field(..., description="Número de DNI del ciudadano", example="12345678")
    acr_values: str = Field(..., description="Nivel de autenticación (ej: 'face_mobile' o 'pki_dnie')", example="face_mobile")


class AuthStartResponse(BaseModel):
    message: str
    qr: str


class AuthNotifyResponse(BaseModel):
    status: str


class AuthTokenResponse(BaseModel):
    access_token: str
    id_token: str
