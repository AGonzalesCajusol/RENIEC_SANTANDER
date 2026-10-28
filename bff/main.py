from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import init_db
from routers import auth, health, dni_digital


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicializa las tablas de PostgreSQL al arrancar el BFF
    init_db()
    yield


app = FastAPI(
    title="BFF ID-Perú CIBA & DNI Digital - Santander",
    description="""
### API Backend for Frontend (BFF) - Plataforma de Identidad Digital (RENIEC / ID-Perú)

Este servicio centraliza y desacopla la comunicación segura entre las aplicaciones cliente (Web/Móvil de Santander) y los servicios de identidad del Estado Peruano (RENIEC):

1. **Flujo ID-Perú CIBA + PKCE:** Autenticación desacoplada mediante la app oficial **ID Perú** (Biometría Facial `face_mobile` y DNI electrónico `pki_dnie`).
2. **Flujo DNI Digital OpenID4VP:** Verificación de credenciales verificables con la billetera **Perú Pass** (Inji Verify).

---
* **Especificación técnica:** ID-Perú CIBA v1.3 (DT-DCSD/SDSCD-037).
* **Seguridad:** Arquitectura BFF con protección de credenciales (`client_secret`), PKCE S256, tokens de notificación únicos de 256 bits y verificación criptográfica de JWT / JWKS.
    """,
    version="1.3.1",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
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
app.include_router(dni_digital.router, prefix="/api")


