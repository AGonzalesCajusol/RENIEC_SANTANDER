# RENIEC - Banco Santander: Integración de Identidad Digital

Este repositorio contiene la implementación de referencia para la integración entre **Banco Santander** y la **Plataforma Nacional de Identidad Digital (ID Perú / RENIEC)**, soportando los dos flujos oficiales de autenticación y verificación de credenciales:

1. **Verificación de DNI Digital (DNId / Perú Pass):** Basado en el estándar internacional **OpenID4VP** (OpenID for Verifiable Presentations) y credenciales **SD-JWT** (Selective Disclosure JWT).
2. **Autenticación ID-Perú CIBA:** Basado en el estándar **OpenID Connect CIBA** (Client Initiated Backchannel Authentication) con **PKCE** (RFC 7636).

---

## 🏛️ Arquitectura General

El sistema implementa el patrón **BFF (Backend For Frontend)** para aislar y proteger el frontend (web o móvil), resguardar credenciales y secretos criptográficos, y orquestar las llamadas hacia los servicios de RENIEC.

```mermaid
flowchart TD
    subgraph Cliente["Dispositivo del Ciudadano"]
        UserBrowser["Navegador Web / App Santander (Frontend)"]
        MobileApp["App Móvil Perú Pass (Billetera DNId)"]
    end

    subgraph Entidad["Infraestructura Banco Santander"]
        BFF["BFF Integrador (FastAPI / Python)<br>:8000"]
        PostgresDB[("PostgreSQL 13 / 17<br>Transacciones y Sesiones")]
        BFF <--> PostgresDB
    end

    subgraph RENIEC["Infraestructura RENIEC"]
        VerifyService["Verify Service (Inji Verify / OpenID4VP)<br>verify.inji-reniec.com"]
        IdPeruCIBA["ID-Perú IdAAS (CIBA + PKCE)<br>idaas2.reniec.gob.pe"]
    end

    %% Relaciones
    UserBrowser <--> |"1. HTTPS /api"| BFF
    MobileApp <--> |"2. OpenID4VP HTTPS (Escaneo QR / Deeplink)"| VerifyService
    BFF <--> |"3. REST API (/vp-request, /status, /vp-result)"| VerifyService
    BFF <--> |"4. Backchannel (/bc-authorize, /ciba/token)"| IdPeruCIBA
```

---

## 📱 1. Flujo DNI Digital (Perú Pass - OpenID4VP)

Permite validar la identidad del cliente mediante su **DNI Digital** emitido en la aplicación móvil **Perú Pass**.

### Experiencia de Usuario (3 Pantallas)

```text
  [ PANTALLA 1 ]                       [ PANTALLA 2 ]                       [ PANTALLA 3 ]
+----------------------+             +----------------------+             +----------------------+
|  Santander           |             |  Escanea con         |             |  ¡Identidad          |
|                      |             |  Perú Pass           |             |  Verificada!         |
|  Verifica tu         |  [Click]    |    [ CÓDIGO QR ]     |  [Autoriza] |        ✅            |
|  identidad para      | ----------> |                      | ----------> |  DNI: 43468328       |
|  continuar           |             |  Expira en: 02:45 min|             |  Wilson Coronado B.  |
|  [ Iniciar con DNI ] |             |  (Esperando escaneo..|             |  Nac: PERUANO        |
+----------------------+             +----------------------+             +----------------------+
                                                ▲
                                                │ Polling en segundo plano
                                                │ (cada 2.5 seg al BFF)
```

1. **Pantalla 1 (Solicitud):** El usuario pulsa *"Iniciar con DNI Digital"*. El frontend invoca `POST /api/dni-digital/init`.
2. **Pantalla 2 (Código QR):** Se renderiza el QR con esquema `openid4vp://authorize?client_id=...&request_uri=...`. El ciudadano escanea el QR con **Perú Pass** y autoriza con huella/PIN. El frontend consulta en segundo plano (`GET /api/dni-digital/status/:requestId`).
3. **Pantalla 3 (Éxito y Desglose):** El BFF detecta el estado `VP_SUBMITTED`, descarga el resultado desde `/vp-result`, decodifica el token **SD-JWT** (disclosures Base64URL) y entrega los atributos del titular:
   - DNI (`CUI_DNI`)
   - Nombres y Apellidos (`PRENOMBRES`)
   - Nacionalidad (`NACIONALIDAD`)
   - Fecha de Nacimiento (`FECHA_NACIMIENTO`)
   - Metadatos del emisor institucional (`DniPeruanoCredential`, vigencia y emisor).

---

## 🔑 2. Flujo ID-Perú CIBA (Autenticación Biométrica / App ID-Perú)

Flujo desacoplado en el que el BFF solicita la autorización a ID-Perú (`/service/bc-authorize`) enviando desafío PKCE (`code_challenge`) y un `client_notification_token`. Al autorizarse en la app ID-Perú, RENIEC notifica vía webhook (`url_notify`) al BFF para que este obtenga los tokens definitivos (`/service/ciba/token`).

---

## 📂 Estructura del Proyecto

```text
RENIEC_SANTANDER/
├── .docs/                 # Documentación técnica oficial entregada por RENIEC
├── .specs/                # Especificaciones técnicas, arquitectura y diagramas
│   ├── arquitectura_verificacion.md
│   ├── especificacion_flujo_verificacion.md
│   ├── Especificacion_Persistencia_Modelo_Transaccional.md
│   ├── Especificacion_Tecnica_ID_Peru_CIBA.md
│   ├── Guia_Configuracion_Variables_Y_Webhook_Notificaciones.md
│   └── Guia_Despliegue_Nginx_Systemd.md
├── bff/                   # Backend For Frontend en Python / FastAPI
│   ├── core/
│   │   ├── config.py      # Configuración de entornos y variables
│   │   ├── database/      # Modelos SQLModel (CibaTransaction, VerifySession)
│   │   └── security/      # Lógica criptográfica (PKCE, SD-JWT decoder)
│   ├── routers/
│   │   ├── auth.py        # Endpoints CIBA (/api/auth)
│   │   ├── dni_digital.py # Endpoints DNI Digital (/api/dni-digital)
│   │   └── health.py      # Healthchecks (/health)
│   ├── tests/             # Suite de pruebas automatizadas (pytest)
│   └── main.py            # Punto de entrada de la aplicación FastAPI
└── frontend/              # Aplicación Web React 19 + TypeScript + Vite
    ├── src/
    │   ├── components/
    │   │   └── DniDigitalVerification.tsx  # Vista de 3 pantallas DNI Digital
    │   ├── pages/
    │   │   └── AuthenticationPage.tsx      # Vista de flujo CIBA
    │   ├── services/      # Clientes HTTP (dniDigitalService, authService)
    │   └── types/         # Definiciones TypeScript
    └── package.json
```

---

## ⚙️ Configuración y Variables de Entorno

### Backend BFF (`bff/.env`)

```ini
# Configuración CIBA
RENIEC_BASE_URL=https://idaas2.reniec.gob.pe
RENIEC_CLIENT_ID=tu_client_id
RENIEC_CLIENT_SECRET=tu_client_secret
RENIEC_REFERER=santander.com.pe
URL_NOTIFY=http://localhost:8000/api/auth/notify

# Base de Datos PostgreSQL
DATABASE_URL=postgresql+psycopg://postgres:postgres@127.0.0.1:5435/reniec_santander_db

# Módulo DNI Digital (Inji Verify - RENIEC Oficial)
VERIFY_SERVICE_INTERNAL_URL=https://verify.inji-reniec.com/v1/verify
VERIFY_SERVICE_PUBLIC_URL=https://verify.inji-reniec.com/v1/verify
VERIFY_CLIENT_ID=did:web:verify.inji-reniec.com:v1:verify
VERIFY_PRESENTATION_DEFINITION_ID=b2c3d4e5-f6a7-8901-bcde-f12345678901
VERIFY_POLLING_TIMEOUT_SEC=2.0
```

### Frontend (`frontend/.env`)

```ini
VITE_API_URL=http://localhost:8000
VITE_USE_MOCK=false
```

---

## 🚀 Despliegue y Ejecución Local

### 1. Iniciar Base de Datos PostgreSQL
Asegurarse de tener la instancia de PostgreSQL corriendo (ej. mediante Docker):
```bash
docker start redcash-db-container # o tu contenedor en el puerto 5435
```

### 2. Iniciar el BFF (FastAPI)
```bash
cd bff
uv venv
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
* **Documentación interactiva Swagger:** [http://localhost:8000/docs](http://localhost:8000/docs)

### 3. Iniciar el Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
```
* **Aplicación Web:** [http://localhost:5173](http://localhost:5173)

---

## 🧪 Pruebas Automatizadas

Para ejecutar la suite completa de pruebas unitarias del BFF:
```bash
cd bff
uv run pytest
```
*Tests incluidos: Creación de transacciones, decodificación y parsing de SD-JWT, validación de PKCE y controladores HTTP.*

---

## 📚 Referencias Técnicas
Para consultar las especificaciones técnicas completas y detalladas, diríjase a la carpeta [`.specs/`](file:///home/wecbxxx/PycharmProjects/RENIEC_SANTANDER/.specs):
* [Especificación del Flujo de Verificación (DNI Digital)](.specs/especificacion_flujo_verificacion.md)
* [Arquitectura de Verificación y Componentes](.specs/arquitectura_verificacion.md)
* [Especificación Técnica ID-Perú CIBA v1.3](.specs/Especificacion_Tecnica_ID_Peru_CIBA.md)
* [Modelo Transaccional y Persistencia](.specs/Especificacion_Persistencia_Modelo_Transaccional.md)
* [Guía de Variables y Notificaciones](.specs/Guia_Configuracion_Variables_Y_Webhook_Notificaciones.md)
* [Guía de Despliegue en Servidor Linux (Nginx + Systemd)](.specs/Guia_Despliegue_Nginx_Systemd.md)
