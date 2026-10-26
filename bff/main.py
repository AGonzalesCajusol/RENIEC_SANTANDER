from fastapi import FastAPI
from routers import auth, health

app = FastAPI(
    title="BFF ID-Perú CIBA - Santander",
    description="Servicio Backend for Frontend (BFF) para el flujo de autenticación CIBA (OpenID Connect Client Initiated Backchannel Authentication) con ID-Perú / RENIEC.",
    version="1.3",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Registro de routers desacoplados
app.include_router(health.router)
app.include_router(auth.router, prefix="/api")


