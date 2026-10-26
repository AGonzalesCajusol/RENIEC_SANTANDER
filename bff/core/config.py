import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "BFF ID-Perú CIBA - Santander"
    VERSION: str = "1.3"
    
    # RENIEC CIBA Configuration
    RENIEC_BASE_URL: str = "https://idaas2.reniec.gob.pe/service"
    RENIEC_JWKS_URL: str = "https://idaas2.reniec.gob.pe/service/jwks"
    RENIEC_ISSUER: str = "https://idaas2.reniec.gob.pe/service"
    RENIEC_CLIENT_ID: str = os.getenv("RENIEC_CLIENT_ID", "santander_client_id_default")
    RENIEC_CLIENT_SECRET: str = os.getenv("RENIEC_CLIENT_SECRET", "")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
