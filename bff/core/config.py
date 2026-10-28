from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Ruta al archivo .env dentro del directorio bff/
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    # Credenciales y URLs de RENIEC
    RENIEC_BASE_URL: str = "https://idaas2.reniec.gob.pe"
    RENIEC_CLIENT_ID: str = "tu_client_id"
    RENIEC_CLIENT_SECRET: str = "tu_client_secret"
    RENIEC_REFERER: str = "santander.com.pe"
    
    # URL pública o webhook registrada ante RENIEC para notificaciones CIBA
    URL_NOTIFY_ID_PERU: str = "http://localhost:8000/api/auth/notify"
    
    # Configuración de timeout y reintentos
    REQUEST_TIMEOUT: int = 15

    # Base de Datos PostgreSQL
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@127.0.0.1:5435/reniec_santander_db"

    # Módulo de Verificación de DNI Digital (Inji Verify - RENIEC Oficial)
    VERIFY_SERVICE_INTERNAL_URL: str = "https://verify.inji-reniec.com/v1/verify"
    VERIFY_SERVICE_PUBLIC_URL: str = "https://verify.inji-reniec.com/v1/verify"
    VERIFY_CLIENT_ID: str = "did:web:verify.inji-reniec.com:v1:verify"
    VERIFY_PRESENTATION_DEFINITION_ID: str = "b2c3d4e5-f6a7-8901-bcde-f12345678901"
    VERIFY_POLLING_TIMEOUT_SEC: float = 2.0

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
