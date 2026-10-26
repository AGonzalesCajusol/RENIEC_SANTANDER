from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, health

app = FastAPI(
    title="BFF ID-Perú CIBA - Santander",
    description="Servicio Backend for Frontend (BFF) para el flujo de autenticación CIBA (OpenID Connect Client Initiated Backchannel Authentication) con ID-Perú / RENIEC.",
    version="1.3",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configuración de CORS para permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro de routers desacoplados
app.include_router(health.router)
app.include_router(auth.router, prefix="/api")


