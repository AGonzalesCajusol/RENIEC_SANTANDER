from typing import Optional
from pydantic import BaseModel, Field


class AuthStartRequest(BaseModel):
    # Soporta tanto login_hint (técnico ID-Perú) como dni (frontend)
    login_hint: Optional[str] = Field(
        None,
        description="Número de DNI del ciudadano (8 dígitos numéricos)",
        json_schema_extra={"example": "43468328"}
    )
    dni: Optional[str] = Field(
        None,
        description="Alias amigable para el número de DNI",
        json_schema_extra={"example": "43468328"}
    )
    acr_values: Optional[str] = Field(
        "face_mobile",
        description="Método de autenticación solicitado: 'face_mobile' (biometría facial) o 'pki_dnie' (DNI electrónico)",
        json_schema_extra={"example": "face_mobile"}
    )
    method: Optional[str] = Field(
        None,
        description="Alias para acr_values ('face_mobile' o 'pki_dnie')",
        json_schema_extra={"example": "face_mobile"}
    )
    binding_message: Optional[str] = Field(
        "Autenticación Santander",
        description="Mensaje visible en la app del ciudadano asociado a la transacción",
        json_schema_extra={"example": "Autenticación Santander"}
    )


class AuthStartResponse(BaseModel):
    auth_req_id: str = Field(..., description="Identificador único de la transacción CIBA emitido por RENIEC", json_schema_extra={"example": "RENIEC_IDAAS.B-c883bc98...-Ciba"})
    qr: str = Field(..., description="Cadena de sesión que debe codificarse en el QR o enlaces de app", json_schema_extra={"example": "RENIEC_IDAAS.B-c883bc98...-Ciba"})
    expires_in: int = Field(600, description="Tiempo de vigencia de la transacción en segundos", json_schema_extra={"example": 600})
    interval: int = Field(5, description="Intervalo mínimo sugerido en segundos entre consultas", json_schema_extra={"example": 5})
    # Campos normalizados para el frontend
    transactionId: str = Field(..., description="Alias idéntico a auth_req_id para compatibilidad con el frontend")
    expiresIn: int = Field(600, description="Alias idéntico a expires_in")
    message: str = Field("Transacción iniciada con éxito", description="Mensaje informativo del estado de inicio")


class AuthNotifyPayload(BaseModel):
    auth_req_id: str = Field(
        ...,
        description="Identificador único de la transacción finalizada",
        json_schema_extra={"example": "RENIEC_IDAAS.B-c883bc98...-Ciba"}
    )
    status: str = Field(
        "completed",
        description="Estado informado por ID-Perú al concluir el proceso ('completed')",
        json_schema_extra={"example": "completed"}
    )


class AuthNotifyResponse(BaseModel):
    status: str = Field("received", description="Confirmación inmediata de recepción del webhook", json_schema_extra={"example": "received"})


class AuthStatusResponse(BaseModel):
    auth_req_id: str = Field(..., description="Identificador de la transacción consultada")
    transactionId: str = Field(..., description="Alias idéntico a auth_req_id")
    status: str = Field(..., description="Estado de la transacción: PENDING, APPROVED, REJECTED, EXPIRED, ERROR", json_schema_extra={"example": "APPROVED"})
    message: Optional[str] = Field(None, description="Mensaje descriptivo del estado actual")
    claims: Optional[dict] = Field(
        None,
        description="Datos y atributos del ciudadano autenticado si el estado es APPROVED",
        json_schema_extra={
            "example": {
                "document_number": "43468328",
                "name": "JUAN PEREZ",
                "auth_time": 1730138400,
                "acr": "face_mobile"
            }
        }
    )


class UserClaimsResponse(BaseModel):
    document_number: Optional[str] = Field(None, description="Número de DNI del usuario autenticado", json_schema_extra={"example": "43468328"})
    name: Optional[str] = Field(None, description="Nombre completo del ciudadano", json_schema_extra={"example": "JUAN CARLOS PEREZ GOMEZ"})
    given_name: Optional[str] = Field(None, description="Nombres del ciudadano", json_schema_extra={"example": "JUAN CARLOS"})
    auth_time: Optional[int] = Field(None, description="Marca de tiempo UNIX en la que se autenticó", json_schema_extra={"example": 1730138400})
    sub: Optional[str] = Field(None, description="Identificador único de sujeto / usuario")


class AuthTokenResponse(BaseModel):
    access_token: str = Field(..., description="Token de acceso JWT firmado por RENIEC")
    id_token: Optional[str] = Field(None, description="Token de identidad OpenID Connect")
    expires_in: Optional[int] = Field(3600, description="Tiempo de expiración del token en segundos")
    token_type: Optional[str] = Field("Bearer", description="Tipo de token")
    claims: Optional[UserClaimsResponse] = Field(None, description="Claims extraídos y validados del JWT")
