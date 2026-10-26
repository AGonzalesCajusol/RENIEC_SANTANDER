import os
from pydantic import BaseModel


class Settings(BaseModel):
    # Credenciales y URLs de RENIEC
    RENIEC_BASE_URL: str = os.getenv("RENIEC_BASE_URL", "https://idaas2.reniec.gob.pe")
    RENIEC_CLIENT_ID: str = os.getenv("RENIEC_CLIENT_ID", "tu_client_id")
    RENIEC_CLIENT_SECRET: str = os.getenv("RENIEC_CLIENT_SECRET", "tu_client_secret")
    RENIEC_REFERER: str = os.getenv("RENIEC_REFERER", "santander.com.pe")
    
    # URL pública o webhook registrada ante RENIEC
    URL_NOTIFY: str = os.getenv("URL_NOTIFY", "http://localhost:8000/api/auth/notify")
    
    # Configuración de timeout y reintentos
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "15"))


settings = Settings()
