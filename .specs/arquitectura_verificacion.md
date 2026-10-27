# Arquitectura de Verificación de DNI Digital (Perú Pass / ID Perú)

Basado en la documentación técnica oficial de RENIEC:
* *Guía técnica: Habilitar la API de verificación del DNId en infraestructura gestionada por una entidad externa (DT-DCSD/SDSCD-035)*
* *Guía técnica: Integración y consumo del servicio de verificación de credenciales a través de endpoints (DT-DCSD/SDSCD-036)*
* *Especificación técnica: Piloto de autenticación mediante arquitectura BFF basado en CIBA + PKCE (ID-Perú CIBA-v1.3)*

---

## 1. Diagrama de Componentes y Roles

```mermaid
flowchart TD
    subgraph Cliente["Dispositivo del Ciudadano"]
        AppPeruPass["Aplicación Perú Pass<br>(Billetera Digital / DNId)"]
        UserBrowser["Navegador Web / App Móvil<br>(Frontend Integrador)"]
    end

    subgraph Entidad["Infraestructura de la Entidad (Santander)"]
        BFF["BFF Integrador<br>(Backend for Frontend / Lógica de Negocio)"]
        
        subgraph VerifyModule["Módulo de Verificación (Inji Verify / RENIEC)"]
            VerifyUI["verify-ui<br>(dnid-verify-react)"]
            VerifyService["verify-service<br>(reniec-verify-service)"]
            VerifyDB[("PostgreSQL 13<br>(verify-db)")]
            
            VerifyUI <--> |"VITE_INJI_VERIFY_SERVICE_URL"| VerifyService
            VerifyService <--> VerifyDB
        end
    end

    subgraph RENIEC["Infraestructura RENIEC"]
        IdPeru["Plataforma ID Perú / Issuer<br>(Emisor de Credenciales y Firmas)"]
    end

    %% Relaciones y flujos
    UserBrowser <--> |"1. HTTPS (Lógica de la Entidad)"| BFF
    BFF <--> |"2. API REST (/vp-request, /status, /vp-result)"| VerifyService
    AppPeruPass <--> |"3. OpenID4VP HTTPS (Escaneo QR / Presentación VP)"| VerifyService
    VerifyService -.-> |"4. Validación de Firmas / Carga de la prueba"| IdPeru
```

---

## 2. Descripción de Componentes y Responsabilidades

| Componente | Administrado por | Rol / Responsabilidad |
| :--- | :--- | :--- |
| **Frontend Integrador** | Entidad (Santander) | Interfaz web o móvil con la que interactúa el usuario para solicitar el trámite o autenticación. |
| **BFF Integrador** | Entidad (Santander) | Backend For Frontend que resguarda credenciales y secretos, maneja sesiones, y orquesta las peticiones hacia el Verify Service. |
| **Verify Service (`reniec-verify-service`)** | Desplegado en la Entidad (Docker provisto por RENIEC) | Servicio backend encargado de: <ul><li>Generar la solicitud `OpenID4VP` (`/vp-request`).</li><li>Exponer el endpoint consultado por **Perú Pass**.</li><li>Verificar criptográficamente las credenciales (SD-JWT).</li><li>Exponer resultados validados (`/vp-result`).</li></ul> |
| **Verify UI (`dnid-verify-react`)** | Desplegado en la Entidad (Docker provisto por RENIEC) | Interfaz web provista por RENIEC para visualizar el código QR e interactuar directamente con `verify-service` mediante la variable `VITE_INJI_VERIFY_SERVICE_URL`. |
| **Perú Pass** | Ciudadano (App móvil) | Billetera digital en el teléfono del usuario donde reside el DNI Digital emitido por RENIEC. |

---

## 3. Diagrama de Secuencia del Flujo de Verificación

```mermaid
sequenceDiagram
    autonumber
    actor Ciudadano
    participant Frontend as Frontend Integrador
    participant BFF as BFF Integrador
    participant Verify as Verify Service (reniec-verify-service)
    participant App as App Perú Pass (Móvil)

    Ciudadano->>Frontend: Solicita trámite / autenticación
    Frontend->>BFF: Inicia proceso de verificación
    BFF->>Verify: POST /v1/verify/vp-request (clientId, presentationDefinitionId)
    Verify-->>BFF: Retorna transactionId, requestId, requestUri
    BFF-->>Frontend: Envía QR / Enlace openid4vp://...
    
    Frontend->>Ciudadano: Muestra código QR o botón deeplink
    Ciudadano->>App: Escanea QR / Abre enlace con Perú Pass
    
    par Monitoreo
        loop Long-polling cada N segundos
            BFF->>Verify: GET /v1/verify/vp-request/{requestId}/status
            Verify-->>BFF: Estado (PENDING / VP_SUBMITTED)
        end
    and Presentación de Credencial
        App->>Verify: Presenta la credencial firmada (OpenID4VP)
        Verify->>Verify: Valida firmas digitales e integridad
    end

    Note over BFF,Verify: Verify responde estado: VP_SUBMITTED

    BFF->>Verify: GET /v1/verify/vp-result/{transactionId}
    Verify-->>BFF: Resultado SUCCESS + SD-JWT (vc)
    BFF->>BFF: Decodifica SD-JWT y extrae atributos permitidos (DNI, Nombres, etc.)
    BFF-->>Frontend: Confirmación de identidad / Datos validados
    Frontend-->>Ciudadano: Trámite completado exitosamente
```
