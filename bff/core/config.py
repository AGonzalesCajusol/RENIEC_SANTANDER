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
    
    # URL pública o webhook registrada ante RENIEC
    URL_NOTIFY: str = "http://localhost:8000/api/auth/notify"
    
    # Configuración de timeout y reintentos
    REQUEST_TIMEOUT: int = 15

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
