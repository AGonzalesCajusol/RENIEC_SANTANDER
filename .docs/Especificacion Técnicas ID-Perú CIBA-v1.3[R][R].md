

|  | DOCUMENTO TÉCNICO |  |
| --- | --- | --- |
| VERSIÓN: 1.3 | CÓDIGO: DT - DCSD/SDSCD-037 |  |
| DIRECCIÓN: CERTIFICACIÓN Y SERVICIOS DIGITALES |  |  |
| SUB DIRECCIÓN: SERVICIOS DE CERTIFICACIÓN DIGITAL |  |  |
| PILOTO DE AUTENTICACIÓN MEDIANTE ARQUITECTURA BFF BASADO EN CIBA + PKCE ESPECIFICACIÓN TÉCNICA |  |  |
| CLASIFICACIÓN: | PÚBLICO |  |
| RUBRO | NOMBRE | CARGO |
| ELABORADO POR: | Ronald Sucasaca Surco | Especialista de Servicios PKI |
| REVISADO POR: | Richard Martin Quispe Araca | Líder del Equipo de Servicios Digitales |
| APROBADO POR: | César Roberto Rosales Maquera | Subdirector de Servicios de Certificación Digital |

1

| CESAR ROBERTO ROSALES MAQUERA | Firmado digitalmente por: ROSALES MAQUERA Cesar Roberto FAU 20295613620 soft Motivo: Soy el autor del documento Fecha: 20/10/2026 18:57:58-0500 |
| --- | --- |
| Sub Director de Servicios de Certificación Digital REGISTRO NACIONAL DE IDENTIFICACIÓN Y ESTADO CIVIL |  |

logo: REPUBLICA DEL PERU FIRMA DIGITAL

| Firmado digitalmente por: QUISPE ARACA Richard Martin FAU 20295613620 soft Motivo: En señal de conformidad Fecha: 19/10/2026 12:18:27-0500 |
| --- |

PLATAFORMA DE AUTENTICACIÓN DE LA IDENTIDAD DIGITAL ID-PERÚ

## **1. HISTORIAL DE VERSIONES**

| VERSIÓN | ESTADO | FECHA |
| --- | --- | --- |
| V1.0 | DEPRECADO | 13/03/2026 |
| V1.1 | DEPRECADO | 09/04/2026 |
| V1.2 | DEPRECADO | 04/06/2026 |
| V1.3 | APROBADO | 29/09/2026 |

***Tabla 1: Historial de versiones***

## **2. CONTENIDO**

| 1. | HISTORIAL DE VERSIONES | 2 |
| --- | --- | --- |
| 2. | CONTENIDO | 2 |
| 3. | DESCRIPCIÓN GENERAL | 5 |
| 4. | GLOSARIO DE TÉRMINOS | 5 |
| 5. | FLUJO FUNCIONAL RESUMIDO | 7 |
| 6. | REQUISITOS PREVIOS | 7 |
| 7. | ENDPOINTS DE LA PLATAFORMA ID PERÚ | 8 |
| 8. | IMPLEMENTACION DEL FLUJO OIDC CIBA | 8 |
| 8.1. | BFF INTEGRADOR | 8 |
| 8.1.1. | Flujo de Inicio de transacción OIDC CIBA | 8 |
| 8.1.2. | Respuestas esperadas al inicio del flujo | 10 |
| 8.1.3. | Parámetros de la respuesta de inicio de transacción | 11 |
| 8.1.4. | Endpoint del BFF para inicio de transacción | 11 |
| 8.1.5. | Criterios para solicitar repuesta | 11 |
| 8.1.6. | Obtención de la respuesta de la plataforma ID Perú | 16 |
| 8.1.7. | Exposición del Endpoint del BFF para consulta de estado | 17 |
| 8.1.8. | Exposición del Endpoint del BFF para la obtención de claims | 17 |
| 8.2. | FRONTEND INTEGRADOR | 17 |
| 8.2.1. | Invocación de la aplicación ID Perú | 17 |
| 8.2.2. | Proceso de autenticación en la aplicación ID Perú | 23 |
| 8.2.3. | Respuesta desde la aplicación ID Perú | 23 |
| 9. | FLUJO COMPLETO DE COMUNICACIÓN | 24 |
| 10. | CONSIDERACIONES TÉCNICAS GENERALES | 25 |
| 11. | ANEXOS | 26 |
| 11.1. | Anexo I | 26 |

2

PLATAFORMA DE AUTENTICACIÓN DE LA IDENTIDAD DIGITAL ID-PERÚ

| 11.2. | Anexo II | 30 |
| --- | --- | --- |
|  | Tabla 1: Historial de versiones | 2 |
|  | Tabla 2: Glosario de términos | 7 |
|  | Tabla 3: Flujo CIBA | 7 |
|  | Tabla 4: Requisitos previos | 8 |
|  | Tabla 5: Endpoints de integración | 8 |
|  | Tabla 6: Contenido para el header de la solicitud | 8 |
|  | Tabla 7: Contenido para el body de la solicitud | 9 |
|  | Tabla 8: Ejemplo del parámetro code_verifier | 9 |
|  | Tabla 9: Ejemplo codificado del parámetro code_verifier | 9 |
|  | Tabla 10: Ejemplo del parámetro code_challenge | 10 |
|  | Tabla 11: Ejemplo resumido del parámetro code_challenge | 10 |
|  | Tabla 12: Ejemplo del parámetro code_challenge | 10 |
|  | Tabla 13: Contenido de Header en él envió de la notificación | 12 |
|  | Tabla 14: Parámetros para body de consulta de estado de transacción CIBA | 16 |
|  | Tabla 15: Segmentos del esquema para la llamada al cliente de windows de ID Perú .. | 17 |
|  | Tabla 16: Segmentos del intent para el llamado de la aplicación ID Perú en android | 18 |
|  | Tabla 17: Segmentos del esquema para la llamada de la aplicación ID Perú | 18 |
|  | Tabla 18: Parámetros específicos para invocar la aplicación ID Perú en Android | 20 |
|  | Tabla 19: Datos específicos para invocar la aplicación ID Perú en iOS | 22 |
|  | Tabla 20: Parámetros necesarios para la query | 23 |
|  | Tabla 21: Flujo completo de comunicación | 24 |
|  | Tabla 22: Catalogo de mensajes enviados por la plataforma ID Perú | 30 |
|  | Tabla 23: Catalogo de mensajes enviados por la aplicación móvil ID Perú | 33 |
|  | Endpoint 1: Inicio de flujo CIBA | 8 |
|  | Endpoint 2: Certificados para verificación de JWT | 15 |
|  | Endpoint 3: Consulta de estado de transacción CIBA | 16 |
|  | Código fuente 1: Ejemplo de cURL para inicio de transacción CIBA | 10 |
|  | Código fuente 2: Ejemplo de respuesta de error al inicio del flujo de autenticación | 10 |
|  | Código fuente 3: Ejemplo de respuesta de éxito al inicio del flujo de autenticación | 11 |
|  | Código fuente 4: Json de ejemplo hacia url_notify | 12 |
|  | Código fuente 5: Json de respuesta afirmativa desde la aplicación ID Perú | 13 |
|  | Código fuente 6: Respuesta de estado pendiente | 14 |
|  | Código fuente 7: Respuesta de error de auth_req_id requerido | 14 |
|  | Código fuente 8: Respuesta de error de code_verifier requerido | 14 |
|  | Código fuente 9: Respuesta de autenticación exitosa | 14 |

3

PLATAFORMA DE AUTENTICACIÓN DE LA IDENTIDAD DIGITAL ID-PERÚ

| Código fuente 10: Mensaje de reintento al endpoint bc-authorize luego de un flujo terminado | 15 |
| --- | --- |
| Código fuente 11: Fragmento PAYLOAD del JWT de access_token | 15 |
| Código fuente 12: Seudocódigo para la validación del JWT | 16 |
| Código fuente 13: Ejemplo de cURL para consulta de estado de transacción CIBA | 17 |
| Código fuente 14: Intent para llamada de la aplicación ID Perú en android | 18 |
| Código fuente 15: Esquema de llamado de la aplicación ID Peru en iOS | 18 |
| Código fuente 16: Ejemplo de invocación de aplicación ID Perú desde SO Android | 19 |
| Código fuente 17: Código de integración modelo para SO android | 20 |
| Código fuente 18: Ejemplo de invocación de aplicación ID Perú desde SO iOS | 22 |
| Código fuente 19: Ejemplo de archivo info.plist para SO iOS | 23 |
| Código fuente 20: Json de respuesta de la aplicación ID Perú | 23 |
| Código fuente 21: Json de ejemplo de mensaje enviado por la plataforma IF Perú | 26 |
| Código fuente 22: Json de ejemplo enviado por la Aplicación móvil ID Perú | 30 |

4

PLATAFORMA DE AUTENTICACIÓN DE LA IDENTIDAD DIGITAL ID-PERÚ

## **3. DESCRIPCIÓN GENERAL**

La Plataforma de Autenticación de la Identidad Digital Nacional ID Perú permite a las entidades integradoras realizar autenticación digital mediante el flujo CIBA con PKCE, empleando una arquitectura BFF para proteger credenciales, centralizar la transacción y desacoplar al frontend integrador de los servicios internos de RENIEC. El flujo está orientado a escenarios de integración por api considerando toda la comunicación por backend y el consumo por frontend. el frontend integrador inicia la operación contra su BFF; el BFF solicita la transacción CIBA a ID Perú, administra el *auth_req_id*, recibe la notificación de ID Perú en su *url_notify*, obtiene los *tokens*. La validación del ciudadano se realiza en la aplicación ID Perú.

El frontend integrador puede ser cualquiera de los siguientes, y solo cambia la forma en que se entrega el valor qr a la aplicación ID Perú; el BFF es el mismo para todos:

* Aplicación móvil nativa (Android o iOS): invoca la aplicación ID Perú instalada en el mismo dispositivo (App-to-App) y recibe el control de vuelta al terminar.
* Aplicación web abierta desde un celular: abre la aplicación ID Perú del mismo dispositivo mediante un enlace (Web-to-App) que lleva el valor qr.
* Aplicación web abierta desde una computadora: muestra el valor qr como una imagen QR, que el ciudadano escanee con la aplicación ID Perú de su celular. Así mismo se puede hacer uso del valor del qr para lanzar el aplicativo nativo de Windows cliente ID Perú; si se desea realizar la autenticación con el DNlE utilizando una lectora de tarjetas inteligentes.

## **4. GLOSARIO DE TÉRMINOS**

| Término | Definición resumida |
| --- | --- |
| OIDC CIBA | Flujo de autenticación del tipo Open Id Connect (OIDC), donde la solicitud inicia por backend y la validación del usuario ocurre de forma desacoplada. |
| PKCE | Mecanismo de seguridad que protege el flujo de autorización vinculando la solicitud inicial con el intercambio posterior de tokens. |
| BFF | Backend For Frontend. Componente intermedio entre el frontend integrador (aplicación móvil o web) y la Plataforma ID Perú. |
| Frontend integrador | Capa con la que interactúa el ciudadano: aplicación móvil nativa (Android/iOS) o aplicación web (en computadora o en celular). Solo consume los servicios del BFF. |
| App-to-App | Comunicación entre la aplicación integradora y la aplicación ID Perú instalada en el dispositivo. |

5

## PLATAFORMA DE AUTENTICACIÓN DE LA IDENTIDAD DIGITAL ID-PERÚ

| Web-to-App | Enlace que una aplicación web abierta en un celular usa para abrir la aplicación ID Perú del mismo dispositivo, llevando el valor qr (intent:// en Android, URL Scheme en iOS). |
| --- | --- |
| Código QR | Imagen que codifica el valor qr tal cual; la muestra una aplicación web en computadora para que el ciudadano la escanee con la aplicación ID Perú. |
| client_id | Identificador único asignado por RENIEC a la plataforma integradora de una entidad. |
| client_secret | Secreto asociado al client_id. Debe resguardarse en el BFF y no exponerse en el frontend (app móvil ni navegador). |
| auth_req_id | Identificador único de la transacción CIBA. Se usa para consultar el estado del flujo. |
| url_notify | Endpoint público del BFF, registrado ante RENIEC, al que la Plataforma ID Perú envía un POST cuando la autenticación concluye. |
| client_notification_token | Token aleatorio generado por el BFF al iniciar la transacción. ID Perú lo devuelve como Bearer al llamar a url_notify, para que el BFF verifique que la notificación es legítima. |
| login_hint | Identificador del usuario a autenticar, normalmente el número de DNI. |
| acr_values | Método o nivel de autenticación solicitado: face_mobile o pki_dnie. |
| code_verifier | Cadena aleatoria generada por el BFF para el mecanismo PKCE. |
| code_challenge | Valor derivado del code_verifier usando SHA-256 y Base64URL sin padding. |
| code_challenge_metho d | Método usado para generar el code_challenge; en este flujo debe ser S256. |
| access_token | Token JWT emitido cuando la autenticación finaliza correctamente. |
| id_token | Token JWT con información de identidad del usuario autenticado. |
| JWT | Token que contiene información en formato JSON y que se encuentra firmado para garantizar su integridad. |
| JWKS | Conjunto de llaves públicas usado para validar la firma de los JWT. |
| Claims | Atributos o datos asociados al usuario autenticado, retornados en el JWT. |
| auth_time | Momento de la autenticación. |
| Base64URL | Codificación segura para URL y en algunos valores transmitidos. |
| URL Scheme | Mecanismo usado en iOS para abrir otra aplicación mediante una URL personalizada. |
| Intent | Mecanismo usado en Android para invocar otra aplicación o actividad. |
| DNIe | Documento Nacional de Identidad electrónico, usado como método de autenticación. |

6

PLATAFORMA DE AUTENTICACIÓN DE LA IDENTIDAD DIGITAL ID-PERÚ

| NFC | Tecnología de comunicación inalámbrica de corto alcance utilizada para la lectura del DNlE desde dispositivos móviles compatibles. |
| --- | --- |
| Content-Type | Cabecera HTTP que indica el formato de la solicitud; para /bc-authorize y /token se usa application/x-www-form-urlencoded. |
| Referer | Cabecera HTTP que contiene la URL de la página desde la cual se origina una solicitud y permite identificar su dominio de origen. |
| error | Parámetro o campo utilizado para indicar el tipo de error producido durante una operación. |

***Tabla 2: Glosario de términos***

## **5. FLUJO FUNCIONAL RESUMIDO**

| Paso | Descripción |
| --- | --- |
| 1 | El frontend integrador solicita al BFF iniciar una autenticación CIBA. |
| 2 | El BFF valida la solicitud, genera el code_verifier, el code_challenge y el client_notification_token, y consume /service/bc-authorize. Enviando los parámetros necesarios. |
| 3 | ID Perú valida la solicitud y, si es correcta, devuelve auth_req_id, qr, expires_in, interval y los valores operativos; el BFF los almacena asociados a la transacción. En caso contrario, ID Perú devuelve un error controlado. |
| 4 | El BFF procesa la respuesta de ID Perú y envía al frontend los parámetros necesarios, incluido el valor de qr, para interactuar con la aplicación móvil ID Perú según el entorno: invocación app-to-app (app nativa), enlace web-to-app (web en celular) o imagen QR (web en computadora). |
| 5 | La aplicación ID Perú ejecuta la autenticación del usuario según el método solicitado. |
| 6 | ID Perú notifica al BFF en su url_notify, con el client_notification_token como Bearer. |
| 7 | El BFF consulta /service/ciba/token al recibir la notificación en url_notify, utilizando auth_req_id, login_hint y code_verifier. |
| 8 | Si la autenticación es exitosa, ID Perú devuelve access_token e id_token; en caso contrario, devuelve un error controlado. |
| 9 | El BFF valida los JWT, cruza el número de DNI y el método de autenticación con lo solicitado y extrae los claims enviados en la respuesta. |
| 10 | El frontend consulta el estado de la transacción al BFF (nunca a ID Perú) y, al concluir, obtiene el resultado. |

***Tabla 3: Flujo CIBA***

## **6. REQUISITOS PREVIOS**

| Requisito | Descripción |
| --- | --- |
| Convenio vigente | La entidad integradora debe contar con autorización y convenio vigente con RENIEC. |
| Credenciales técnicas | Debe disponer de client_id y client_secret asignados por RENIEC. |
| Registro de app móvil | Si el frontend es una aplicación móvil nativa, debe estar registrada previamente ante RENIEC (packageId y/o bundleId). No aplica a un frontend web. |

7

PLATAFORMA DE AUTENTICACIÓN DE LA IDENTIDAD DIGITAL ID-PERÚ

| Registro de url_notify | La URL pública del endpoint url_notify del BFF debe estar registrada ante RENIEC para el client_id de la entidad. |
| --- | --- |
| Aplicación ID Perú | El celular del usuario debe tener instalada la aplicación ID Perú (en el mismo dispositivo del frontend, o en un celular aparte cuando el frontend es web en computadora). |
| Conectividad | El dispositivo y el BFF deben contar con acceso a Internet y a los endpoints autorizados. El url_notify del BFF debe ser alcanzable desde Internet. |
| BFF operativo | La entidad debe implementar un BFF que actúe como intermediario seguro entre el frontend y la Plataforma ID Perú. |

***Tabla 4: Requisitos previos***

## **7. ENDPOINTS DE LA PLATAFORMA ID PERÚ**

Para el flujo de autenticación bajo el estándar OIDC CIBA, la Plataforma ID Perú dispone de endpoints específicos que permiten iniciar la transacción, consultar su estado, obtener los tokens y validar los JWT emitidos. Estos endpoints son consumidos por el BFF de la entidad integradora como parte del flujo técnico de integración.

| Métod o | Endpoint | Uso |
| --- | --- | --- |
| POST | /service/bc- authorize | Inicia la transacción CIBA y retorna auth_req_id y qr. |
| POST | /service/ciba/token | Consulta el estado de la transacción y retorna tokens si la autenticación concluyó correctamente. |
| GET | /service/jwks | Publica las llaves públicas para validar los JWT emitidos por la plataforma. |

***Tabla 5: Endpoints de integración***

En sentido inverso, la Plataforma ID Perú consume un endpoint expuesto por la entidad: el url_notify del BFF (POST), al que notifica cuando la autenticación concluye.

## **8. IMPLEMENTACION DEL FLUJO OIDC CIBA**

### **8.1. BFF INTEGRADOR**

#### **8.1.1. Flujo de Inicio de transacción OIDC CIBA**

El inicio de la transacción se realiza mediante una solicitud hacia el endpoint *bc_authorize*. Como resultado, se obtiene el *auth_req_id* y los datos operativos requeridos para continuar el flujo.

<u>https://idaas2.reniec.gob.pe/service/bc-authorize</u>

***Endpoint 1: Inicio de flujo CIBA.***

| Header | Valor |
| --- | --- |
| Content-Type | application/x-www-form-urlencoded |
| Referer | mientidad.dominio.com |

***Tabla 6: Contenido para el header de la solicitud.***

| Parámetro | Obligatorio | Tipo / Formato | Descripción técnica |
| --- | --- | --- | --- |

8

PLATAFORMA DE AUTENTICACIÓN DE LA IDENTIDAD DIGITAL ID-PERÚ

| client_id | Sí | string | Identificador de cliente asignado por RENIEC a la entidad integradora. |
| --- | --- | --- | --- |
| client_secret | Sí | string | Secreto del cliente asignado por RENIEC; prohibida su exposición. |
| grant_type | Sí | string fijo | Debe enviarse como urn:openid:params:grant-type:ciba. |
| scope | Sí | String fijo | Alcance obligatorio openid. |
| login_hint | Sí | string | Nivel/método de autenticación requerido. (“face_mobile”, “pki_dnie”). En ambos casos el login_hint es obligatorio. |
| binding_message | No | string | Mensaje asociado a la transacción. |
| requested_expiry | No | integer (seg) | Tiempo solicitado de vigencia de la transacción. |
| acr_values | Sí | string | Nivel/método de autenticación requerido. (“face_mobile”, “pki_dnie”). |
| code_challenge | Sí | string (Base64URL ) | Valor derivado por PKCE (S256). Debe corresponder al code_verifier. |
| code_challenge_metho d | Si | String fijo | Debe enviarse como S256 |
| client_notification_token | Sí | string | Token aleatorio generado por el BFF para esta transacción. ID Perú lo devuelve como Bearer al llamar al url_notify del BFF. |

***Tabla 7: Contenido para el body de la solicitud.***

En la solicitud POST, es obligatorio enviar el encabezado *Referer* con el dominio de su entidad. Para evitar bloqueos de seguridad.

## ***Parámetro “code_challenge”***

Valor de seguridad del mecanismo PKCE, derivado del *code_verifier*. Su uso es obligatorio y permite validar que el intercambio de tokens sea realizado por la misma entidad que inició la transacción.

### ***Paso 1: Generar code_verifier***

* ✓ Tipo: cadena aleatoria
* ✓ Longitud: 43 y 128 caracteres
* ✓ Caracteres permitidos: A-Z a-z 0-9

```text
code_verifier = "K3m1ltcipINIXUO3WQFUqJ7LnkikFrLvU4HoqfMPxrczN31j2TN7wWAYwJd4v7xGW"
```

***Tabla 8: Ejemplo del parámetro code_verifier***

### ***Paso 2: aplicar SHA-256***

Se calcula el hash SHA-256 del *code_verifier*.

```text
sha256(code_verifier) -> bytes binarios
(en hexadecimal: bdd38cca46e7a1f3ad0d7f8e73e519a155c5d28a6ef6d08d5d3268e9b01749c9)
```

***Tabla 9: Ejemplo codificado del parámetro code_verifier***

9

PLATAFORMA DE AUTENTICACIÓN DE LA IDENTIDAD DIGITAL ID-PERÚ

## ***Paso 3: codificar en Base64 URL Safe (sin padding)***

El hash binario se convierte en Base64 URL-Safe, aplicando las reglas: reemplazar + por -, / por _ y eliminar el relleno =

```text
code_challenge = "vdOMykbnof0tDX-Oc-UZoVXF0opu9tCNXTJo6bAXSck"
```

***Tabla 10: Ejemplo del parámetro code_challenge***

```text
code_challenge = BASE64URL( SHA256( code_verifier ) )
```

***Tabla 11: Ejemplo resumido del parámetro code_challenge***

* El *code_challenge* y el *code_verifier* están intrínsecamente ligados.

```text
--data-urlencode 'code_challenge=CODE_CHALLENGE_BASE64URL'
```

***Tabla 12: Ejemplo del parámetro code_challenge***

## ***Parámetro "client_notification_token"***

Token que permite al BFF comprobar que una llamada a su url_notify proviene de la Plataforma ID Perú y corresponde a esta transacción. El BFF lo genera por cada transacción, lo envía en el inicio y lo resguarda; cuando ID Perú notifica, lo devuelve en la cabecera Authorization: Bearer.

* Tipo: cadena aleatoria generada criptográficamente (al menos 128 bits).
* Uso único: un valor distinto por transacción.
* Debe guardarse en el BFF junto con el auth_req_id y el code_verifier.

```text
curl --location 'https://idaas2.reniec.gob.pe/service/bc-authorize' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--header 'Referer: mientidad.dominio.com' \
--data-urlencode 'client_id=CLIENT_ID_ASIGNADO_POR_RENIEC' \
--data-urlencode 'client_secret=CLIENT_SECRET_ASIGNADO_POR_RENIEC' \
--data-urlencode 'grant_type=urn:openid:params:grant-type:ciba' \
--data-urlencode 'scope=openid' \
--data-urlencode 'login_hint=12345678' \
--data-urlencode 'binding_message=Mensaje personalizado' \
--data-urlencode 'requested_expiry=600' \
--data-urlencode 'acr_values=face_mobile' \
--data-urlencode 'code_challenge=CODE_CHALLENGE_BASE64URL' \
--data-urlencode 'code_challenge_method=S256' \
--data-urlencode 'client_notification_token=TOKEN_ALEATORIO_GENERADO_POR_EL_BFF'
```

***Código fuente 1: Ejemplo de cURL para inicio de transacción CIBA***

### **8.1.2. Respuestas esperadas al inicio del flujo.**

Al ejecutar la petición al endpoint de inicio de transacción, la Plataforma ID Perú generará una nueva solicitud de autenticación para el flujo app-to-app. La respuesta podrá ser de éxito o error, según la validación de los parámetros enviados. A continuación, se detallan los posibles escenarios de respuesta.

#### ***Respuesta de error***

La respuesta de error es en formato json con el siguiente aspecto. Anexo I.

```json
{
  "codigo": "10001",
  "error": "server_error",
  "mensaje": "CIBA: client_id requerido."
}
```

***Código fuente 2: Ejemplo de respuesta de error al inicio del flujo de autenticación***

10

PLATAFORMA DE AUTENTICACIÓN DE LA IDENTIDAD DIGITAL ID-PERÚ

## ***Respuesta de éxito***

La respuesta de éxito es en formato json con el siguiente aspecto.

```json
{
  "auth_req_id": "RENIEC_IDAAS...ee3-Ciba",
  "expires_in": 600,
  "qr": "UkVOSUVDIENsY...2dpbilAQClubw==",
  "interval": 5,
  "c_nonce": "a04f5...b4ae1d88e8e92c7fa",
  "c_nonce_expires_in": 600
}
```

***Código fuente 3: Ejemplo de respuesta de éxito al inicio del flujo de autenticación***

### **8.1.3. Parámetros de la respuesta de inicio de transacción**

A continuación, se detalla cada parámetro de la respuesta.

* **auth_req_id**: identificador único de la transacción. Debe ser gestionado por el BFF durante todo el flujo y quedar asociado al frontend (sesión o cliente) que inició la transacción: solo ese frontend debe poder recibir su resultado.
* **expires_in**: tiempo de vigencia de la transacción, expresado en segundos.
* **qr**: valor que el frontend entrega a la aplicación ID Perú: en la invocación app-to-app, en el enlace web-to-app o codificado en una imagen QR. Debe usarse tal cual se recibe, sin agregar, quitar ni transformar caracteres.
* **interval**: intervalo mínimo, en segundos, entre consultas.
* **c_nonce**: valor auxiliar generado por la plataforma para uso interno.
* **c_nonce_expires_in**: tiempo de vigencia de c_nonce, expresado en segundos.

## ***Resguardo de la transacción en el BFF***

Entre el inicio de la transacción y la notificación de ID Perú no interviene el frontend: la llamada a **url_notify** llega directamente al BFF, sin sesión de usuario. Por ello, el BFF debe persistir por cada transacción los datos que necesitará después, y no mantenerlos solo en la memoria de la petición o en la sesión del frontend:

* **auth_req_id**, **login_hint** y **acr_values** solicitados.
* **code_verifier** y **client_notification_token**, generados por el BFF.
* **interval**, **expires_in** y la fecha de vencimiento calculada.
* Solo el **qr**, debe enviarse al frontend.

### **8.1.4. Endpoint del BFF para inicio de transacción**

El BFF deberá exponer un endpoint propio para iniciar la transacción, cuya gestión estará a cargo de la entidad.

### **8.1.5. Criterios para solicitar repuesta**

La consulta deberá realizarse cuando se cumpla cualquiera de los siguientes criterios, sin necesidad de esperar a que se cumplan ambos:

11

PLATAFORMA DE AUTENTICACIÓN DE LA IDENTIDAD DIGITAL ID-PERÚ

## ***Al recibir la notificación en url_notify***

El BFF debe registrar y exponer un endpoint propio (*url_notify*) para que la Plataforma ID Perú pueda notificarle cuando la autenticación haya concluido de manera exitosa.

* La notificación es en un mensaje en formato JSON enviado vía POST a esa URL.
* El endpoint *url_notify* debe ser alcanzable públicamente por la Plataforma ID Perú (expuesto hacia internet, no solo accesible dentro de la red interna del BFF).
* Al recibir esta notificación, el BFF solicitar la respuesta con la certeza de que ya existe (o está por existir de inmediato) un resultado definitivo que consultar.

Formato del mensaje recibido en *url_notify* (POST, Content-Type: application/json):

| HEADER | VALOR |
| --- | --- |
| Content-Type | application/json |
| Authorization | Bearer {client_notification_token enviado por el BFF al iniciar la transacción} |

***Tabla 13: Contenido de Header en él envió de la notificación***

```json
{
    "auth_req_id":"RENIEC_IDAAS...f0-Ciba",
    "status":"completed"
}
```

***Código fuente 4: Json de ejemplo hacia url_notify***

Antes de actuar sobre una notificación, el BFF debe validarla:

* El auth_req_id debe corresponder a una transacción propia que siga abierta (no concluida ni vencida).
* El Bearer recibido debe ser igual al client_notification_token guardado para ese auth_req_id. La comparación debe hacerse en tiempo constante. Si no coincide, se responde 401 y no se consulta /service/ciba/token.
* Una notificación válida se responde de inmediato con 200 y se ejecuta en segundo plano la consulta de la respuesta a ID Perú.
* La notificación puede provenir de distintas direcciones IP de la Plataforma ID Perú; la legitimidad se comprueba con el Bearer, no con la IP de origen.
* El valor de status informa que el proceso concluyó; el resultado definitivo (éxito o error) se obtiene siempre de /service/ciba/token.

## ***Al recibir respuesta afirmativa desde la aplicación ID Perú***

Cuando la aplicación ID Perú es invocada desde otra aplicación móvil (flujo App to App, con un callback registrado según el mecanismo de invocación descrito en las secciones "Invocación de la aplicación ID Perú en Android/iOS" de este mismo documento), la Plataforma ID Perú retorna el control a la aplicación que la invocó una vez que el proceso termina. Al volver, la aplicación ID Perú entrega un mensaje en formato Base64.

Al decodificar ese Base64 se obtiene un JSON con el siguiente contenido:

12

PLATAFORMA DE AUTENTICACIÓN DE LA IDENTIDAD DIGITAL ID-PERÚ

```json
{
  "status":true
}
```

***Código fuente 5: Json de respuesta afirmativa desde la aplicación ID Perú***

El parámetro status = true dentro de ese JSON indica que la autenticación fue exitosa. Solo en ese caso corresponde solicitar el resultado a la plataforma ID Perú.

## ***Recibir la confirmación explícita del usuario (Alternativo en web)***

Cuando el frontend es una aplicación web en computadora con imagen QR o en celular con enlace web-to-app, la aplicación ID Perú no devuelve el control a la web. Como señal de respaldo ante una notificación demorada, el frontend puede ofrecer una acción explícita del usuario (por ejemplo, un botón "Ya me autenticué"):

* El frontend solicita al BFF una sola consulta del resultado de la transacción; nunca consulta `/service/ciba/token` directamente.
* El BFF ejecuta una única consulta a `/service/ciba/token`, respetando el interval desde la consulta anterior.
* Solo el frontend que inició la transacción puede solicitar esta consulta.

La consulta debe priorizarse para el momento en el que ya es razonable esperar un resultado afirmativo, y no para un momento en el que se tiene certeza de que todavía no existe una respuesta final (por ejemplo, arrancar a consultar `/ciba/token` inmediatamente después de `/ciba/start`, sin ninguna señal de que el usuario siquiera completó el proceso en su dispositivo).

Hacer polling en ese tipo de momentos (sin una señal previa que indique que hay un resultado disponible) genera consultas innecesarias contra la Plataforma ID Perú y puede hacer que la integración quede bloqueada por el rate limit del cerco de seguridad de RENIEC. En caso que se tenga un caso de bloqueo, comunicarse por el canal oficial al correo <u>identidaddigital@reniec.gob.pe</u> .

Por eso se recomienda realizar la consulta condicionada a estas señales:

* Iniciar la consulta únicamente al recibir alguno de los criterios anteriores (url_notify, respuesta afirmativa status = true desde la aplicación ID Perú o confirmación explícita del usuario en un frontend web).
* Evitar polling innecesario en momentos en los que no hay ninguna señal de que exista ya un resultado.

## ***Respuestas esperadas al realizar la consulta***

La Plataforma ID Perú puede retornar distintos estados de la transacción. El BFF deberá interpretarlos y determinar si corresponde continuar la consulta, finalizar el flujo o registrar la transacción como fallida.

### ***a) Estado: autenticación pendiente***

Indica que la transacción aún se encuentra en proceso y que no existe un resultado final.

13

PLATAFORMA DE AUTENTICACIÓN DE LA IDENTIDAD DIGITAL ID-PERÚ

```json
{
  "codigo": "20001",
  "error": "server_warn",
  "mensaje": "Autenticación pendiente."
}
```

***Código fuente 6: Respuesta de estado pendiente***

## ***b) Estado: autenticación con Error***

Indica que la transacción ya no es válida. En este caso, el BFF deberá finalizar el flujo como no exitoso, registrar el evento y requerir una nueva transacción si corresponde. Catalogo completo en el Anexo I.

```json
{
  "codigo": "20006",
  "error": "server_error",
  "mensaje": "CIBA: auth_req_id requerido."
}
```

***Código fuente 7: Respuesta de error de auth_req_id requerido***

```json
{
  "codigo": "20012",
  "error": "server_error",
  "mensaje": "CIBA: code_verifier requerido."
}
```

***Código fuente 8: Respuesta de error de code_verifier requerido***

## ***c) Estado: autenticación exitosa (credenciales emitidas)***

Indica que la autenticación fue completada satisfactoriamente y que la plataforma retornó las credenciales correspondientes. En este caso, el BFF deberá resguardar la respuesta y continuar con el tratamiento posterior definido para la aplicación integradora.

```json
{
  "access_token": "eyJ...hbGfQ.eyJ...hIn0.fu...GA",
  "expires_in": 3600,
  "token_type": "Bearer",
  "c_nonce": "fd93a...82170e85",
  "c_nonce_expires_in": 600,
  "id_token": "eyJhbGci...mpMifQ.eyJp...pbGUifQ.JrmJc...UBXA",
  "not-before-policy": 0,
  "session_state": "RENIEC_IDAAS.B-750ac8...c7c60711-Ciba",
  "scope": "openid"
}
```

***Código fuente 9: Respuesta de autenticación exitosa***

## ***Metadatos de respuesta exitosa***

Ante una respuesta exitosa, el BFF debe procesar y resguardar las credenciales retornadas por la Plataforma ID Perú.

* *access_token*: token de acceso en formato JWT. Debe validarse criptográficamente con las claves públicas publicadas en jwk_set_uri antes de procesar sus claims.
* *expires_in*: vigencia del token, expresada en segundos.
* *token_type*: tipo de token emitido, usualmente Bearer.
* *c_nonce* y *c_nonce_expires_in*: valores informativos generados por la plataforma.
* *id_token*: JWT con información de identidad, sujeto al mismo criterio de validación aplicado al access_token.

14

PLATAFORMA DE AUTENTICACIÓN DE LA IDENTIDAD DIGITAL ID-PERÚ

* *not-before-policy*, *session_state* y *scope*: metadatos informativos asociados al resultado de autenticación.

***Nota:***

El flujo no permite renovar el token mediante refresh_token. Por tanto, cualquier consulta al endpoint /bc-authorize después de obtener los datos mencionados devolverá una respuesta de «no encontrado». Este error es controlado, ya que el auth_req_id fue eliminado y el flujo ha concluido su ciclo de vida.

```json
{
    "codigo": "20008",
    "error": "server_error",
    "mensaje": "CIBA: auth_req_id no encontrado."
}
```

***Código fuente 10: Mensaje de reintento al endpoint bc-authorize luego de un flujo terminado***

Para la validación de JWT, el BFF debe verificar firma, vigencia y claims mínimos utilizando el conjunto de claves públicas expuesto por la plataforma.

```json
{
    "iss": "https://idaas2.reniec.gob.pe/service",
    "sub": "b773d1...c4ff6508",
    "aud": "https://mientidad.dominio.com",
    "exp": 1771549258,
    "iat": 1771548958,
    "auth_time": 1771548958,
    "jti": "5046...97c4def7f782",
    "typ": "Bearer",
    "azp": "f9b97...7dff66b7",
    "sid": "384c51...3bcd2d",
    "scope": "openid",
    "name": "",
    "given_name": "",
    "document_number": "12345678",
    "c_nonce": "fd93ac3c4ce4a6...5daeb5c8fdac8b55eb29bb82170e85",
    "c_nonce_expires_in": 600,
    "auth_req_id": "RENIEC_IDAAS...df1-Ciba"
}
```

***Código fuente 11: Fragmento PAYLOAD del JWT de access_token***

<u>https://idaas2.reniec.gob.pe/service/jwks</u>

***Endpoint 2: Certificados para verificación de JWT***

Siempre debe validarse el JWT. Si no supera la validación, su contenido no debe considerarse confiable y deberá ser descartado.

```go
func validarJwt(jwtString) :
    # 1) parsear token (sin confiar aún)
    header = parseHeader(jwtString)          # base64url decode del header JSON
    claims = parseClaims(jwtString)           # base64url decode del payload JSON
    kid = header["kid"]
    alg = header["alg"]

    # 2) validar algoritmo permitido (evitar "none" u otros no esperados)
    if alg not in ["RS256"] :
        return INVALIDO("alg no permitido")

    # 3) obtener JWKS (cacheado)
    jwks = cache.get("jwks")
    if jwks is null or cache.expirado("jwks") :
        jwks = httpGET("https://idaas2.reniec.gob.pe/service/jwks")
        cache.put("jwks", jwks, ttl=15min)

    # 4) seleccionar la llave por kid y uso firma
    jwk = buscarEn(jwks["keys"], where key["kid"] == kid and key["use"] == "sig")
```

15

PLATAFORMA DE AUTENTICACIÓN DE LA IDENTIDAD DIGITAL ID-PERÚ

```python
if jwk is null:
    # refrescar una vez por si rotaron llaves
    jwks = httpGET("https://idaas2.reniec.gob.pe/service/jwks")
    cache.put("jwks", jwks, ttl=15min)
    jwk = buscarEn(jwks["keys"], where key["kid"] == kid and key["use"] == "sig")
    if jwk is null:
        return INVALIDO("kid no encontrado")

# 5) construir clave pública RSA desde n,e (Base64URL)
publicKey = construirRsaPublicKey(n=jwk["n"], e=jwk["e"])

# 6) verificar firma criptográfica del JWT
if !verificarFirma(jwtString, publicKey, alg):
    return INVALIDO("firma inválida")

# 7) validar claims (política mínima recomendada)
now = epochSeconds()
if claims["exp"] <= now:
    return INVALIDO("token expirado")

if claims["iss"] != "EMISOR_ESPERADO":
    return INVALIDO("issuer inválido")

if claims["azp"] != expectedClientId:
    return INVALIDO("azp no coincide con client_id")
return VALIDO(claims)
```

***Código fuente 12: Seudocódigo para la validación del JWT***

### **8.1.6. Obtención de la respuesta de la plataforma ID Perú**

Esta sección describe la obtención del resultado del flujo CIBA, en donde se verifica el estado de la transacción ante la Plataforma ID Perú hasta obtener un resultado definitivo.

<u>https://idaas2.reniec.gob.pe/service/ciba/token</u>

***Endpoint 3: Consulta de estado de transacción CIBA***

Se debe de considerar el mismo contenido del header mostrado en el inicio de transacción CIBA.

| Parámetro | Obligatorio | Tipo / Formato | Descripción técnica |
| --- | --- | --- | --- |
| client_id | Sí | string | Identificador de cliente asignado por RENIEC. |
| client_secret | Sí | string | Secreto del cliente asignado por RENIEC. |
| grant_type | Sí | string fijo | Debe enviarse como urn:openid:params:grant-type:ciba. |
| login_hint | Sí | string | Identificador del usuario a autenticar (número de DNI). Debe validarse formato exacto del DNI. |
| auth_req_id | Sí | string | Código único que identifica a la transacción de autenticación. |
| code_verifier | Sí | string | Código verificador creado por la entidad integradora al inicio del flujo de autenticación. Debe corresponder al code_challenge |

***Tabla 14: Parámetros para body de consulta de estado de transacción CIBA***

```text
curl --location 'https://idaas2.reniec.gob.pe/service/ciba/token' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--header 'Referer: mientidad.dominio.com' \
--data-urlencode 'client_id= CLIENT_ID_ASIGNADO_POR_RENIEC' \
--data-urlencode 'client_secret= CLIENT_SECRET_ASIGNADO_POR_RENIEC' \
--data-urlencode 'grant_type=urn:openid:params:grant-type:ciba' \
--data-urlencode 'auth_req_id=RENIEC_IDAAS...666c-Ciba' \
--data-urlencode 'login_hint=12345678' \
--data-urlencode 'code_verifier=dBjftJeZ4CVP8mB92K27uhbUJU1p1rlwW1gFWFOEjXk'
```

16

PLATAFORMA DE AUTENTICACIÓN DE LA IDENTIDAD DIGITAL ID-PERÚ

***Código fuente 13: Ejemplo de cURL para consulta de estado de transacción CIBA***

### **8.1.7. Exposición del Endpoint del BFF para consulta de estado**

El BFF deberá exponer un endpoint para consultar el estado de la transacción. La entidad será responsable de su gestión.

### **8.1.8. Exposición del Endpoint del BFF para la obtención de claims**

El BFF deberá exponer un endpoint para obtener y procesar los claims de autenticación. La entidad será responsable de su gestión.

## **8.2. FRONTEND INTEGRADOR**

### **8.2.1. Invocación de la aplicación ID Perú.**

La invocación de la aplicación ID Perú se realiza de forma diferenciada en Web, Web Movil, Android y iOS. El valor que será utilizado en reemplazo de las menciones de *code* o *data* corresponderá al contenido del parámetro *qr*.

#### ***8.2.1.1. Invocación de la aplicación ID Perú desde Web (Desktop)***

En una computadora, el frontend muestra el valor *qr* como imagen QR para que el ciudadano la escanee con la aplicación ID Perú de su celular.

* La imagen debe codificar el valor *qr* exactamente como lo retornó la Plataforma ID Perú, sin agregar, quitar ni transformar caracteres.
* Se recomienda un tamaño que permita escanearla sin dificultad desde la pantalla (por ejemplo, 280 × 280 píxeles o más).
* Junto a la imagen se recomienda mostrar el tiempo restante de la transacción, calculado a partir de expires_in.

#### ***8.2.1.2. Invocación del Cliente ID Perú desde la web (Windows)***

Cuando el método de autenticación es DNIE (acr_values = pki_dnie) y la web se abre en una computadora con Windows, el ciudadano puede autenticarse con el Cliente ID Perú de escritorio, que lee el DNIE mediante una lectora de tarjetas inteligentes, en lugar de escanear la imagen QR con el celular. El frontend lo ofrece con un botón adicional (por ejemplo, "Iniciar con Cliente ID Perú") cuyo destino (href) es el enlace siguiente:

```text
idaas2://launch?data={qr}
```

| CAMPO | VALOR |
| --- | --- |
| Scheme | idaas2 |
| Host | launch |
| data | Valor qr completo obtenido en el inicio del flujo de autenticación, insertado tal cual, sin codificar. |

***Tabla 15: Segmentos del esquema para la llamada al cliente de windows de ID Perú***

* El lector de tarjetas inteligentes debe ser compatible con el ISO/IEC 7816.
* Versión de Windows compatible es 10.0.17134.0 o superior

17

PLATAFORMA DE AUTENTICACIÓN DE LA IDENTIDAD DIGITAL ID-PERÚ

### **8.2.1.3. *Invocación de la aplicación ID Perú desde la web (Android)***

En el navegador de un celular Android, la aplicación ID Perú se abre mediante un enlace *intent://*, colocado como destino (href) de un botón o enlace que el ciudadano pulsa. El navegador resuelve el intent hacia la aplicación ID Perú instalada y le entrega el valor *qr*.

```text
intent://idaas.reniec.com/auth/#Intent;scheme=reniec;package=pe.gob.reniec.pki.reniecidaas2;S.name=ID%20Per%C3%BA;S.data={qr};end
```

***Código fuente 14: Intent para llamada de la aplicación ID Perú en android***

| CAMPO | VALOR |
| --- | --- |
| Host y ruta | idaas.reniec.com/auth/ |
| scheme | reniec |
| package | pe.gob.reniec.pki.reniecidaas2 |
| S.name | ID%20Per%C3%BA (texto “ID Perú” codificado para URL) |
| S.data | Valor qr obtenido en el inicio del flujo de autenticación, insertado tal cual, sin codificar. |

***Tabla 16: Segmentos del intent para el llamado de la aplicación ID Perú en android***

### **8.2.1.4. *Invocación de la aplicación ID Perú desde la web (iOS)***

En el navegador de un iPhone o iPad, la aplicación ID Perú se abre mediante su URL Scheme, colocado como destino (href) de un botón o enlace que el ciudadano pulsa.

```text
reniecidaas://auth?data={qr codificado para URL}
```

***Código fuente 15: Esquema de llamado de la aplicación ID Peru en iOS***

| CAMPO | VALOR |
| --- | --- |
| Scheme | reniecidaas |
| Host | auth |
| data | Valor qr obtenido en el inicio del flujo de autenticación, codificado para URL (por ejemplo, = se envía como %3D). La aplicación ID Perú lo decodifica y obtiene el valor exacto. |

***Tabla 17: Segmentos del esquema para la llamada de la aplicación ID Perú***

### ***Selección del enlace según el dispositivo***

El frontend debe decidir qué presentar según el dispositivo en que se abrió la web: el enlace de Android, el de iOS o, en computadora, la imagen QR. En celular, la imagen QR puede ofrecerse igualmente en un panel desplegable, útil para pruebas o para autenticarse con otro celular.

### **8.2.1.5. *Invocación de la aplicación ID Perú desde app nativa (Android)***

En Android, la aplicación ID Perú se invoca mediante un *Intent* explícito hacia el componente publicado por la aplicación destino, enviando como entrada el parámetro requerido para el flujo. Previamente, la aplicación integradora debe validar la disponibilidad del componente y, una vez ejecutada la invocación, esperar el resultado de la operación.

18

PLATAFORMA DE AUTENTICACIÓN DE LA IDENTIDAD DIGITAL ID-PERÚ

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.INTERNET" />

    <application ...>
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:launchMode="singleTop"
            ...>
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>

    <queries>
        <package android:name="pe.gob.reniec.pki.reniecidaas2" />
    </queries>
</manifest>
```

***Código fuente 16: Ejemplo de invocación de aplicación ID Perú desde SO Android***

En Android 11+, se debe declarar la visibilidad de paquetes para que resolveActivity() detecte si ID Perú está instalada. Si se lanza directo con ComponentName, no es obligatorio, pero fallará si la app no existe.

```kotlin
package pe.gob.tuempresa.tuapp

import android.app.Activity
import android.content.ComponentName
import android.content.Intent
import android.os.Bundle
import android.util.Log
import androidx.activity.result.ActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {

    private val TAG = "IDPERU"

    private val TARGET_PKG = "pe.gob.reniec.pki.reniecidaas2"
    private val TARGET_ACT = "pe.gob.reniec.feature.gateway.AppGatewayActivity"

    // — Launcher — debe declararse antes de onStart ----------------------------------
    private val idPeruResultLauncher =
        registerForActivityResult(ActivityResultContracts.StartActivityForResult()) {
            result ->
                procesarResultado(result.resultCode, result.data)
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // binding.btnAutenticar.setOnClickListener {
        abrirIdPeru(codigoObtenidoDelBff)
        }
    }

    // — Invocar ID Perú -------------------------------------------------------------
    fun abrirIdPeru(code: String) {
        val intent = Intent().apply {
            component = ComponentName(TARGET_PKG, TARGET_ACT)
            putExtra("code", code)
        }

        if (intent.resolveActivity(packageManager) == null) {
            Log.e(TAG, "ID Perú no está instalada o no se puede resolver la actividad")
            mostrarResultado(false, "ID Perú no está instalada en este dispositivo.")
            return
        }

        Log.d(TAG, "Abriendo ID Perú — codeLen=${code.length}")
    }
}
```

19

PLATAFORMA DE AUTENTICACIÓN DE LA IDENTIDAD DIGITAL ID-PERÚ

```kotlin
idPeruResultLauncher.launch(intent)
}

// — Procesar respuesta ------------------------------------------
private fun procesarResultado(resultCode: Int, data: Intent?) {
    if (data != null && data.hasExtra("payload")) {
        // Formato nuevo: payload JSON codificado en Base64
        val rawBase64 = data.getStringExtra("payload")
        val resultado = parsearPayload(rawBase64)
        Log.d(TAG, "FORMAT=payload | ok=${resultado.ok} | mensaje=${resultado.mensaje}")
        Log.d(TAG, "JSON decodificado: ${resultado.jsonRaw}")
        mostrarResultado(resultado.ok, resultado.mensaje)
    } else {
        // Formato legacy: auth_message suelto en el Intent
        val ok = resultCode == Activity.RESULT_OK
        val mensaje = data?.getStringExtra("auth_message")
            ?.takeIf { it.isNotEmpty() }
            ?: if (ok) "Autenticación completada exitosamente."
            else "Operación cancelada por el usuario."
        Log.d(TAG, "FORMAT=legacy | ok=$ok | mensaje=$mensaje")
        mostrarResultado(ok, mensaje)
    }
}

// — Parsear payload Base64 → JSON --------------------------------
private data class IdPeruPayload(val ok: Boolean, val mensaje: String, val jsonRaw: String)

private fun parsearPayload(base64Payload: String?): IdPeruPayload {
    if (base64Payload == null) {
        return IdPeruPayload(false, "Operación cancelada.", "{}")
    }
    return try {
        val jsonBytes = android.util.Base64.decode(base64Payload, android.util.Base64.NO_WRAP)
        val jsonString = String(jsonBytes, Charsets.UTF_8)
        Log.d(TAG, "PAYLOAD_JSON: $jsonString")

        val json = org.json.JSONObject(jsonString)
        val status = json.optBoolean("status", false)
        val message = json.optString("message", "").takeIf { it.isNotEmpty() }
            ?: if (status) "Autenticación completada exitosamente."
            else "Operación no completada."

        IdPeruPayload(status, message, jsonString)
    } catch (e: Exception) {
        Log.e(TAG, "PAYLOAD_PARSE_ERROR: ${e.message}")
        IdPeruPayload(false, "Error al procesar respuesta de ID Perú.", "{}")
    }
}

private fun mostrarResultado(ok: Boolean, mensaje: String) {
    Log.d(TAG, "Resultado final — ok=$ok mensaje=$mensaje")
    // Ejemplo: binding.tvResultado.text = mensaje
    // Ejemplo: if (ok) navegarASiguientePantalla() else mostrarError(mensaje)
}
```

***Código fuente 17: Código de integración modelo para SO android***

| Campo | Valor |
| --- | --- |
| Package | pe.gob.reniec.pki.reniecidaas2 |
| Activity | pe.gob.reniec.feature.gateway.AppGatewayActivity |
| Extra enviado | code (String) — Parámetro qr obtenido en el inicio del flujo de autenticación |

***Tabla 18: Parámetros específicos para invocar la aplicación ID Perú en Android.***

Los valores correspondientes al paquete y a la actividad de destino de la aplicación ID Perú no deben ser definidos ni modificados de forma arbitraria, ya que resultan indispensables para la correcta apertura e invocación de la aplicación ID Perú.

20

PLATAFORMA DE AUTENTICACIÓN DE LA IDENTIDAD DIGITAL ID-PERÚ

## ***8.2.1.6. Invocación de la aplicación ID Perú desde app nativa (iOS)***

En iOS, la invocación de la aplicación ID Perú se realiza mediante un *URL Scheme* registrado por la aplicación destino. Para ello, la aplicación integradora construye una URL con los parámetros requeridos por el flujo.

```swift
import UIKit

class SceneDelegate: UIResponder, UIWindowSceneDelegate {

    var window: UIWindow?

    // — Configuración ----------------------------------------------------
    private let idPeruScheme      = "reniecidaas"
    private let idPeruHost        = "auth-external"
    private let callbackScheme    = "tuapp-auth"
    private let callbackUrl       = "tuapp-auth://callback"

    // — Arranque de escena ------------------------------------------------
    func scene(
        _ scene: UIScene,
        willConnectTo session: UISceneSession,
        options connectionOptions: UIScene.ConnectionOptions
    ) {
        guard let windowScene = scene as? UIWindowScene else { return }
        window?.windowScene = windowScene

        // App no estaba corriendo — URL llega en connectionOptions
        if let urlContext = connectionOptions.urlContexts.first {
            manejarURLEntrante(urlContext.url)
        }
    }

    // App en background — iOS la trae al frente con la URL
    func scene(_ scene: UIScene, openURLContexts urlContexts: Set<UIOpenURLContext>) {
        guard let url = urlContexts.first?.url else { return }
        manejarURLEntrante(url)
    }

    // — Invocar ID Perú ---------------------------------------------------
    func abrirIdPeru(code: String) {
        guard let myBundleId = (Bundle.main.object(forInfoDictionaryKey: "CFBundleURLTypes")
            as? [[String: Any]])?.first?["CFBundleURLName"] as? String,
              !myBundleId.isEmpty else {
            print("[IDPERU] ERROR — no se pudo obtener CFBundleURLName del Info.plist")
            return
        }

        guard let codeEncoded = code.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed),
              let callbackEncoded = callbackUrl.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed),
              let bundleEncoded = myBundleId.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed)
        else {
            print("[IDPERU] ERROR — fallo al codificar parámetros")
            return
        }

        let urlString = "\(\(idPeruScheme))://\(\(idPeruHost))?code=\(codeEncoded)&callback=\(callbackEncoded)&myBundleId=\(bundleEncoded)"

        guard let url = URL(string: urlString) else {
            print("[IDPERU] ERROR — URL malformada: \(urlString)")
            return
        }

        guard UIApplication.shared.canOpenURL(url) else {
            print("[IDPERU] ERROR — ID Perú no está instalada o scheme no permitido")
            mostrarResultado(ok: false, mensaje: "ID Perú no está instalada en este dispositivo.")
            return
        }

        print("[IDPERU] abriendo ID Perú → \(urlString)")
        UIApplication.shared.open(url, options: [:]) { success in
            if !success { print("[IDPERU] ERROR — no se pudo abrir la URL") }
        }
    }

    // — Enrutar URL entrante ------------------------------------------------
    private func manejarURLEntrante(_ url: URL) {
        guard url.scheme?.lowercased() == callbackScheme else { return }
```

21

PLATAFORMA DE AUTENTICACIÓN DE LA IDENTIDAD DIGITAL ID-PERÚ

```swift
let queryItems = URLComponents(url: url, resolvingAgainstBaseURL: false)?.queryItems ?? []
print("[IDPERU] callback recibido ← \(url.absoluteString)")

if let base64Payload = queryItems.first(where: { $0.name == "payload" })?.value {
    procesarPayload(base64Payload)
} else {
    procesarLegacy(queryItems)
}
}

// — Formato nuevo: payload Base64 → JSON --------------------------------------------------
private func procesarPayload(_ base64Payload: String) {
    guard let decodedData = Data(base64Encoded: base64Payload) else {
        print("[IDPERU] PAYLOAD_DECODE_ERROR — base64 inválido len=\(base64Payload.count)")
        mostrarResultado(ok: false, mensaje: "Error al decodificar respuesta.")
        return
    }

    let jsonString = String(data: decodedData, encoding: .utf8) ?? "{}"
    print("[IDPERU] PAYLOAD_JSON: \(jsonString)")

    do {
        let json = try JSONSerialization.jsonObject(with: decodedData) as? [String: Any]
        let status = json?["status"] as? Bool ?? false
        let message = ((json?["message"] as? String) ?? "")
            .trimmingCharacters(in: .whitespacesAndNewlines)
        let displayMessage = message.isEmpty
            ? (status ? "Autenticación completada exitosamente." : "Operación no completada.")
            : message

        print("[IDPERU] payload → status=\(status) mensaje=\(displayMessage)")
        mostrarResultado(ok: status, mensaje: displayMessage)

    } catch {
        print("[IDPERU] PAYLOAD_PARSE_ERROR — \(error.localizedDescription)")
        mostrarResultado(ok: false, mensaje: "Error al procesar respuesta de ID Perú.")
    }
}

// — Formato legacy: auth_status + auth_message ------------------------------------------------
private func procesarLegacy(_ queryItems: [URLQueryItem]) {
    let status = queryItems.first(where: { $0.name == "auth_status" })?.value
    let message = queryItems.first(where: { $0.name == "auth_message" })?.value?
        .removingPercentEncoding

    let isSuccess = status?.lowercased() == "true" || status?.lowercased() == "true"
    let displayMessage = message?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
    let finalMessage = displayMessage.isEmpty
        ? (isSuccess ? "Autenticación completada exitosamente." : "Operación cancelada por el usuario.")
        : displayMessage

    print("[IDPERU] legacy → status=\(status ?? "nil") ok=\(isSuccess) mensaje=\(finalMessage)")
    mostrarResultado(ok: isSuccess, mensaje: finalMessage)
}

// — Reemplazar con tu lógica de UI ----------------------------------------------------------
private func mostrarResultado(ok: Bool, mensaje: String) {
    print("[IDPERU] Resultado final — ok=\(ok) mensaje=\(mensaje)")
    // Ejemplo con NotificationCenter (para que la vista se entere):
    // NotificationCenter.default.post(name: .idPeruResult, object: nil,
    //      userInfo: ["ok": ok, "mensaje": mensaje])
    //
    // Ejemplo con completion handler almacenado:
    // pendingCompletion?(ok, mensaje)
}
```

**Código fuente 18: Ejemplo de invocación de aplicación ID Perú desde SO iOS**

**Nota:** Este código asume una app con Scene lifecycle (Xcode 11+, iOS 13+). Si tu app usa AppDelegate sin escenas, mueve los métodos `scene(_:openURLContexts:)` y `scene(_:willConnectTo:...)` al equivalente `application(_:open:options:)` de AppDelegate.

| Campo | Valor |
| --- | --- |
| Scheme | reniecidaas |
| Host | auth-external |
| URL de ejemplo | reniecidaas://auth-external?code=...&callback=...&myBundleId=... |

***Tabla 19: Datos específicos para invocar la aplicación ID Perú en iOS.***

22

PLATAFORMA DE AUTENTICACIÓN DE LA IDENTIDAD DIGITAL ID-PERÚ

| Parámetro | Descripción |
| --- | --- |
| Code | Parámetro qr obtenido en el inicio del flujo de autenticación |
| Callback | URL completa de retorno — ej: tuapp-auth://callback (URL-encoded) |
| myBundleId | Identificador de tu app, tomado de CFBundleURLName (URL-encoded) |

***Tabla 20: Parámetros necesarios para la query***

En iOS, estos valores forman parte del mecanismo de interoperabilidad app-to-app, por lo que su correcta configuración resulta obligatoria para la invocación de la aplicación ID Perú y para el retorno controlado hacia la aplicación integradora. Asimismo, el esquema de retorno definido en *callback* deberá encontrarse previamente registrado en el *Info.plist* de la aplicación integradora.

```xml

<key>CFBundleURLTypes</key>
<array>
    <dict>
        <key>CFBundleTypeRole</key>
        <string>Editor</string>
        <key>CFBundleURLName</key>
        <string>pe.gob.tuempresa.tuapp</string>
        <key>CFBundleURLSchemes</key>
        <array>
            <string>tuapp-auth</string>
        </array>
    </dict>
</array>

<key>LSApplicationQueriesSchemes</key>
<array>
    <string>reniecidaas</string>
</array>
```

***Código fuente 19: Ejemplo de archivo info.plist para SO iOS***

### **8.2.2. Proceso de autenticación en la aplicación ID Perú**

Desde este punto, la aplicación ID Perú asume la autenticación según el método solicitado. Mientras el proceso esté en curso, la transacción permanecerá en estado pendiente y el BFF seguirá devolviendo dicho estado. Cuando la autenticación finalice, la transacción actualizará su resultado, ID Perú retornará el control a la aplicación integradora.

### **8.2.3. Respuesta desde la aplicación ID Perú**

La aplicación ID Perú retornará una respuesta codificada en Base64. Al decodificar dicho valor, se obtendrá un objeto JSON con la estructura correspondiente. Para el catálogo completo de respuestas ver Anexo II

```json
{
    "code": 60001,
    "status": false,
    "message": "invalid_qr"
}
```

***Código fuente 20: Json de respuesta de la aplicación ID Perú***

23

PLATAFORMA DE AUTENTICACIÓN DE LA IDENTIDAD DIGITAL ID-PERÚ

Con la recuperación de los *claims* de autenticación desde el BFF, el flujo CIBA se considera concluido. A partir de este punto, la aplicación integradora dispone de la información necesaria para continuar con su lógica de negocio.

## **9. FLUJO COMPLETO DE COMUNICACIÓN**

| Paso | Origen → Destino | Acción |
| --- | --- | --- |
| 1 | Frontend → BFF | Envía la solicitud de autenticación. |
| 2 | BFF | Genera PKCE y client_notification_token. |
| 3 | BFF → IdAAS | Solicita autorización mediante POST /service/bc-authorize, enviando el desafío PKCE, login_hint y client_notification_token. |
| 4 | IdAAS → BFF | Devuelve auth_req_id, qr, expires_in e interval. |
| 5 | BFF → Frontend | Envía el QR con el código de sesión de ID Perú. |
| 6 | Frontend | Procesa y muestra el QR. |
| 7 | Frontend → App ID Perú | La App ID Perú lee el código de sesión mediante intent, esquema o QR. |
| 8 | App ID Perú ↔ IdAAS | Valida el código de sesión. |
| 9 | App ID Perú | Realiza la autenticación del ciudadano. |
| 10 | App ID Perú → IdAAS | Envía la información del procedimiento de autenticación. |
| 11 | IdAAS | Procesa la información de autenticación. |
| 12 | IdAAS → BFF | Notifica mediante POST a su url_notify, enviando auth_req_id, estado completed y el encabezado Authorization: Bearer client_notification_token. |
| 13 | BFF | Compara el token recibido con el token almacenado. |
| 14 | BFF → IdAAS | Responde inmediatamente: 200 si el token coincide o 401 si no coincide. |
| 15 | BFF → IdAAS | Si la notificación es válida, solicita los tokens mediante POST /service/ciba/token, enviando el verificador PKCE. |
| 16 | IdAAS | Valida el verificador PKCE. |
| 17 | IdAAS → BFF | Devuelve un JSON con access_token e id_token en formato JWT. |
| 18 | BFF | Valida y procesa el JWT access_token. |
| 19 | BFF → Frontend | Devuelve los datos del usuario: document_number, name, entre otros. Aplicar mínima exposición; el frontend solo debe recibir lo que la lógica de negocio necesita. |

***Tabla 21: Flujo completo de comunicación***

24

## PLATAFORMA DE AUTENTICACIÓN DE LA IDENTIDAD DIGITAL ID-PERÚ

flow_chart: Sequence diagram of the ID Perú authentication flow

```mermaid
flowchart LR
    A["Frontend Integrador"]
    B["BFF Integrador"]
    C["ID Perú backend (IdAAS)"]
    D["App ID Perú"]
    A -- "POST Solicitud de Autenticación" --> B
    B -- "genera PKCE y client_notification_token" --> B
    B -- "POST /service/bc-authorize (PKCE challenge, login_hint, client_notification_token)" --> C
    C -.-> B
    B -- "auth_req_id, qr, expires_in, interval" --> C
    C -.-> A
    A -- "qr (Código de sesión de ID Perú)" --> A
    A -- "Procesar y Mostrar QR" --> A
    A -.-> D
    D -- "Lectura del código de sesión de ID Perú (intent/schema/qr)" --> C
    C -- "validación de código de sesión de ID Perú" --> C
    D -- "Proceso de autenticación del ciudadano" --> D
    D -- "Envío de la información del procedimiento de autenticación" --> C
    C -- "Procesa la información de autenticación" --> C
    C -- "POST /bff/api/notify (auth_req_id, status “completed”) Authorization: Bearer client_notification_token" --> B
    B -- "valida Bearer contra el token guardado" --> B
    B -.-> C
    C -- "Respuesta inmediata (200 Si token coincide) (401 Si token no coincide)" --> C
    B -- "POST /service/ciba/token (PKCE verifier)" --> C
    C -- "Validación PKCE" --> C
    C -- "Json (JWT=access_token JWT=id_token)" --> B
    B -- "Validación y procesamiento del JWT access_token" --> B
    B -.-> A
    B -- "claims del usuario (document_number, name, ...)" --> A
```

### **10. CONSIDERACIONES TÉCNICAS GENERALES**

* Toda integración debe realizarse a través de un BFF.
* El *auth_req_id* debe mantenerse correlacionado durante todo el flujo.
* La respuesta exitosa con *access_token* e *id_token* debe ser resguardada por la entidad integradora, ya que corresponde al resultado único de la transacción y no debe asumirse su disponibilidad para múltiples recuperaciones ante la Plataforma ID Perú.
* Todo JWT debe validarse antes de procesarse.
* Los *claims* deben exponerse bajo criterio de mínima exposición.

25

PLATAFORMA DE AUTENTICACIÓN DE LA IDENTIDAD DIGITAL ID-PERÚ

* Los parámetros de expiración, y estado transaccional deben respetarse durante toda la ejecución.
* Todos los datos requeridos para la invocación de la aplicación ID Perú deberán ser proporcionados exclusivamente por RENIEC.

## **11. ANEXOS**

### **11.1. Anexo I**

Los errores controlados de la Plataforma ID Perú se presentan como respuestas estructuradas. Estos errores permiten identificar situaciones esperadas dentro del flujo de integración, como solicitudes incompletas, parámetros inválidos, clientes no autorizados, URL de redirección no registradas, cancelación del proceso por parte del usuario o indisponibilidad temporal de algún servicio relacionado. Cada error se documenta considerando su código, descripción técnica, mensaje mostrado, escenario de ocurrencia, causa probable y acción recomendada. Esta clasificación permite facilitar el diagnóstico por parte de las entidades integradoras y mejorar la atención de incidencias durante las etapas de desarrollo, certificación y producción.

Son errores devueltos directamente por los servicios o endpoints de la plataforma.

```json
{
  "codigo": "10001",
  "error": "server_error",
  "mensaje": "CIBA: client_id requerido."
}
```

***Código fuente 21: Json de ejemplo de mensaje enviado por la plataforma IF Perú***

26

| N.º | Código | Tipo | Mensaje mostrado | Escenario | Causa probable | Acción recomendada |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 10001 | server_error | CIBA: client_id requerido | Al consumir el endpoint /service/bc-authorize | No se envió el parámetro client_id en la solicitud. | Enviar el parámetro client_id asignado a la entidad integradora. |
| 2 | 10002 | server_error | CIBA: client_secret requerido | Al consumir el endpoint /service/bc-authorize | No se envió el parámetro client_secret. | Enviar el client_secret correspondiente al cliente registrado. |
| 3 | 10003 | server_error | CIBA: grant_type requerido | Al consumir el endpoint /service/bc-authorize | No se envió el parámetro grant_type. | Enviar grant_type=urn:openid:params:grant-type:ciba. |
| 4 | 10004 | server_error | CIBA: grant_type inválido | Al validar los parámetros de la solicitud | El valor de grant_type no corresponde al flujo CIBA. | Usar exactamente urn:openid:params:grant-type:ciba. |
| 5 | 10005 | server_error | CIBA: scope requerido | Al consumir el endpoint /service/bc-authorize | No se envió el parámetro scope. | Enviar el alcance requerido, por ejemplo, openid. |
| 6 | 10006 | server_error | CIBA: scope inválido | Al validar el parámetro scope | El parámetro contiene valores no permitidos, caracteres inválidos o scopes no autorizados. | Verificar que scopes sea exactamente openid. |
| 7 | 10007 | server_error | CIBA: login_hint requerido | Al consumir el endpoint /service/bc-authorize | No se envió el parámetro login_hint. | Enviar el identificador del ciudadano requerido por el flujo, número de DNI. |
| 8 | 10008 | server_error | CIBA: login_hint inválido | Al validar el identificador del ciudadano | El valor enviado no cumple el formato esperado, está vacío o contiene caracteres inválidos. | Validar el formato del login_hint antes de enviar la solicitud. |
| 9 | 10009 | server_error | CIBA: acr_values requerido | Al consumir el endpoint /service/bc-authorize | No se envió el parámetro acr_values. | Enviar el factor de autenticación requerido, por ejemplo face_mobile. |
| 10 | 10010 | server_error | CIBA: acr_values inválido | Al validar el factor de autenticación | El valor enviado no está permitido o no está habilitado para el cliente. | Verificar los valores acr_values autorizados para la entidad. |
| 11 | 10011 | server_error | CIBA: code_challenge requerido | Al consumir el endpoint /service/bc-authorize | No se envió el parámetro code_challenge. | Enviar el code_challenge generado para el flujo PKCE. |
| 12 | 10012 | server_error | CIBA: code_challenge inválido | Al validar el parámetro code_challenge | El valor enviado no cumple el formato esperado para PKCE. | Generar correctamente el code_challenge a partir del code_verifier. |

27

## PLATAFORMA DE AUTENTICACIÓN DE LA IDENTIDAD DIGITAL ID-PERÚ

| 13 | 10013 | server_error | CIBA: code_challenge_method requerido | Al consumir el endpoint /service/bc-authorize | No se envió el parámetro code_challenge_method. | Enviar el método de generación del challenge, por ejemplo S256. |
| --- | --- | --- | --- | --- | --- | --- |
| 14 | 10014 | server_error | CIBA: code_challenge_method inválido | Al validar el método PKCE | El método enviado no es soportado por la plataforma. | Usar S256, si es el método definido por ID Perú. |
| 15 | 10015 | server_error | CIBA: cliente no registrado | Al validar las credenciales del cliente | El client_id enviado no existe en la plataforma. | Verificar que el cliente esté registrado en el ambiente correspondiente. |
| 16 | 10016 | server_error | CIBA: credenciales del cliente inválidas | Al validar client_id y client_secret | El client_secret no corresponde al client_id enviado. | Verificar las credenciales asignadas a la entidad integradora. |
| 17 | 10017 | server_error | CIBA: cliente inactivo | Al validar el estado del cliente | El cliente existe, pero se encuentra deshabilitado o inactivo. | Solicitar la activación o revisión del cliente en la plataforma ID Perú. |
| 18 | 10018 | server_error | CIBA: cliente no autorizado para flujo CIBA | Al validar permisos del cliente | El cliente no tiene habilitado el flujo CIBA. | Solicitar la habilitación del flujo CIBA para el cliente correspondiente. |
| 19 | 10019 | server_error | CIBA: acr_values no autorizado para el cliente | Al validar el factor de autenticación | El cliente no tiene permitido usar el factor enviado, por ejemplo face_mobile. | Usar un acr_values autorizado o solicitar su habilitación. |
| 20 | 10020 | server_error | CIBA: método HTTP no permitido | Al consumir el endpoint /service/bc-authorize | Se intentó consumir el endpoint con un método distinto a POST. | Consumir el endpoint usando el método POST. |
| 21 | 20001 | server_warn | Autenticación pendiente | Al consultar el endpoint /service/ciba/token | El ciudadano aún no ha completado la autenticación en la aplicación ID Perú. | Continuar consultando el estado del flujo según el intervalo permitido. |
| 22 | 20002 | server_error | CIBA: client_id requerido | Al consumir el endpoint /service/ciba/token | No se envió el parámetro client_id. | Enviar el client_id asignado a la entidad integradora. |
| 23 | 20003 | server_error | CIBA: client_secret requerido | Al consumir el endpoint /service/ciba/token | No se envió el parámetro client_secret. | Enviar el client_secret correspondiente al cliente registrado. |
| 24 | 20004 | server_error | CIBA: grant_type requerido | Al consumir el endpoint /service/ciba/token | No se envió el parámetro grant_type. | Enviar grant_type=urn:openid:params:grant-type:ciba. |
| 25 | 20005 | server_error | CIBA: grant_type inválido | Al validar los parámetros de la solicitud | El valor de grant_type no corresponde al flujo CIBA. | Usar exactamente urn:openid:params:grant-type:ciba. |

28

## PLATAFORMA DE AUTENTICACIÓN DE LA IDENTIDAD DIGITAL ID-PERÚ

| 26 | 20006 | server_error | CIBA: auth_req_id requerido | Al consumir el endpoint /service/ciba/token | No se envió el parámetro auth_req_id. | Enviar el auth_req_id obtenido previamente desde el endpoint /service/bc-authorize. |
| --- | --- | --- | --- | --- | --- | --- |
| 27 | 20007 | server_error | CIBA: auth_req_id inválido | Al validar la solicitud de autenticación | El auth_req_id no tiene el formato esperado o fue alterado. | Verificar que el valor enviado sea exactamente el retornado por el inicio del flujo CIBA. |
| 28 | 20008 | server_error | CIBA: auth_req_id no encontrado | Al buscar la transacción CIBA | No existe una transacción asociada al auth_req_id enviado. | Generar una nueva solicitud desde /service/bc-authorize. |
| 29 | 20009 | server_error | CIBA: auth_req_id expirado | Al consultar el token | La solicitud de autenticación superó el tiempo de vigencia permitido. | Iniciar nuevamente el flujo CIBA desde /service/bc-authorize. |
| 30 | 20010 | server_error | CIBA: login_hint requerido | Al consumir el endpoint /service/ciba/token | No se envió el parámetro login_hint. | Enviar el mismo identificador del ciudadano usado al iniciar el flujo. |
| 31 | 20011 | server_error | CIBA: login_hint inválido | Al validar el identificador del ciudadano | El valor enviado no cumple el formato esperado o no coincide con la transacción. | Validar que el login_hint corresponda al usado en /service/bc-authorize. |
| 32 | 20012 | server_error | CIBA: code_verifier requerido | Al consumir el endpoint /service/ciba/token | No se envió el parámetro code_verifier. | Enviar el code_verifier asociado al code_challenge enviado al iniciar el flujo. |
| 33 | 20013 | server_error | CIBA: code_verifier inválido | Al validar PKCE | El code_verifier no corresponde al code_challenge registrado. | Verificar la generación PKCE y enviar el code_verifier correcto. |
| 34 | 20014 | server_error | CIBA: cliente no registrado | Al validar las credenciales del cliente | El client_id no existe en la plataforma. | Verificar que el cliente esté registrado en el ambiente correspondiente. |
| 35 | 20015 | server_error | CIBA: credenciales del cliente inválidas | Al validar client_id y client_secret | El client_secret no corresponde al client_id enviado. | Verificar las credenciales asignadas a la entidad integradora. |
| 36 | 20016 | server_error | CIBA: cliente inactivo | Al validar el estado del cliente | El cliente existe, pero está deshabilitado o inactivo. | Solicitar la activación o revisión del cliente en ID Perú. |
| 37 | 20017 | server_error | CIBA: cliente no autorizado para flujo CIBA | Al validar permisos del cliente | El cliente no tiene habilitado el flujo CIBA. | Solicitar la habilitación del flujo CIBA para el cliente correspondiente. |
| 38 | 20018 | server_error | CIBA: autenticación no completada | Al consultar el token | El proceso fue iniciado, pero no llegó a un estado final válido. | Consultar nuevamente si aún está dentro del tiempo permitido o iniciar un nuevo flujo. |

29

PLATAFORMA DE AUTENTICACIÓN DE LA IDENTIDAD DIGITAL ID-PERÚ

| 39 | 20019 | server_error | CIBA: transacción en estado inválido | Al procesar la consulta de token | La transacción no se encuentra en un estado válido para emitir token. | Revisar el estado de la transacción o iniciar nuevamente el flujo. |
| --- | --- | --- | --- | --- | --- | --- |
| 40 | 20020 | server_error | CIBA: intervalo de consulta no permitido | Al consultar repetidamente el token | Se está consultando el endpoint en intervalos menores a los permitidos. | Respetar el intervalo de consulta definido para el flujo CIBA. |
| 41 | 20021 | server_error | CIBA: método HTTP no permitido | Al consumir el endpoint /service/ciba/token | Se intentó consumir el endpoint con un método distinto a POST. | Consumir el endpoint usando el método POST. |

***Tabla 22: Catalogo de mensajes enviados por la plataforma ID Perú***

## **11.2. Anexo II**

Son errores devueltos directamente por la aplicación ID Perú. El formato de error que se recibirá esta codificado en base64 y al decodificarlo se obtiene un valor en formato JSON similar al siguiente:

```json
{
    "code": 60001,
    "status": false,
    "message": "invalid_qr"
}
```

***Código fuente 22: Json de ejemplo enviado por la Aplicación móvil ID Perú***

| N° | Código | Mensaje mostrado | Descripción | Escenario donde ocurre | Causa probable | Acción recomendada |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 60001 | invalid_qr | El parámetro QR es inválido. | Flujo inicial, durante la obtención del código QR. | El parámetro QR no corresponde a una solicitud válida, está vencido, fue alterado o no pertenece al flujo App to App. | Solicitar al usuario generar un nuevo QR e intentar nuevamente. |
| 2 | 60002 | server_message_qr_invalid | QR inválido. | Flujo inicial, al recibir respuesta del servidor durante la validación del QR. | El servidor rechazó el QR enviado por no cumplir las validaciones internas. | Mostrar el mensaje controlado al usuario y permitir un nuevo escaneo. |

30

## PLATAFORMA DE AUTENTICACIÓN DE LA IDENTIDAD DIGITAL ID-PERÚ

| 3 | 60003 | operation_timeout | La operación está tardando más de lo esperado. | Flujo inicial, durante la validación del QR o comunicación con el servidor. | La operación superó el tiempo máximo de espera por lentitud de red, demora del servidor o bloqueo temporal de comunicación. | Indicar al usuario que verifique su conexión a Internet, reinicie su celular y vuelva a intentar. |
| --- | --- | --- | --- | --- | --- | --- |
| 4 | 60004 | network_access_restricted | Por razones de seguridad, tu acceso ha sido restringido temporalmente. Te recomendamos reiniciar tu conexión a internet e intentar nuevamente. | Flujo inicial, durante la validación de acceso a la plataforma. | El acceso fue restringido temporalmente por reglas de seguridad, WAF, IP pública observada como riesgosa o comportamiento anómalo. | Recomendar reiniciar la conexión a Internet, cambiar de red o contactar a soporte si el problema persiste. |
| 5 | 60005 | no_internet_connection | Por favor, asegúrate de estar conectado a internet y vuelve a intentarlo. | Flujo inicial, al intentar validar el código QR o comunicarse con la plataforma. | El dispositivo no tiene conexión a Internet o la conexión es inestable. | Solicitar al usuario verificar Wi-Fi/datos móviles e intentar nuevamente. |
| 6 | 60006 | support_required_persistent_issue | ¿Estás fuera del país o el problema persiste? Escríbenos a identidaddigital@reniec.gob.pe indicando tu DNI, nombre completo, país, teléfono de contacto, modelo de equipo e IP Pública. | Flujo inicial, cuando el problema persiste luego de varios intentos. | El usuario podría estar fuera del país, tener una IP restringida, problemas de red o bloqueo temporal de acceso. | Indicar al usuario que remita la información solicitada al correo de soporte. |
| 7 | 60007 | facial_attempts_exceeded | Has agotado la cantidad de intentos permitidos. Por favor vuelve a intentarlo. | Flujo facial, durante la validación biométrica facial. | El usuario superó la cantidad máxima de intentos permitidos para la verificación facial. | Permitir un nuevo intento según la política definida o indicar al usuario que reinicie el proceso. |
| 8 | 60008 | dnie_blocked | Tu DNIe se encuentra bloqueado. | Flujo DNIe, durante la validación del documento electrónico. | El DNIe del usuario se encuentra bloqueado o no puede ser utilizado para autenticación. | Indicar al usuario que revise el estado de su DNIe o siga el procedimiento |

31

## PLATAFORMA DE AUTENTICACIÓN DE LA IDENTIDAD DIGITAL ID-PERÚ

|  |  |  |  |  |  | correspondiente para desbloqueo. |
| --- | --- | --- | --- | --- | --- | --- |
| 9 | 60009 | invalid_dnie_document | El documento revisado no es un DNIe. Por favor, verifique e intente nuevamente. | Flujo DNIe, durante la lectura o validación del documento. | El documento leído no corresponde a un DNI electrónico válido. | Solicitar al usuario verificar que está utilizando un DNIe válido e intentar nuevamente. |
| 10 | 60010 | nfc_not_available | Este dispositivo no cuenta con la funcionalidad NFC necesaria. | Flujo DNIe, antes o durante la lectura NFC del documento. | El equipo móvil no cuenta con NFC o la funcionalidad NFC no está disponible. | Indicar al usuario que utilice un dispositivo compatible con NFC. |
| 11 | 60021 | dni_minor_age | data_api_error (El número de DNI corresponde a una persona menor de edad.) | Flujo App to App, durante la validación del número de DNI. | El DNI consultado pertenece a un ciudadano menor de edad y no cumple las condiciones requeridas para continuar el flujo. | Informar al usuario que el DNI no puede ser utilizado para esta operación e indicar que debe validar las condiciones del servicio. |
| 12 | 60022 | dni_deceased_or_cancelled | data_api_error El número de DNI corresponde a una persona fallecida o con registro cancelado. | Flujo App to App, durante la validación del número de DNI. | El DNI consultado figura como fallecido, cancelado o no habilitado para realizar la operación. | Informar que el DNI no puede continuar con el proceso y derivar el caso al canal de atención correspondiente si el usuario considera que existe un error. |
| 13 | 60023 | dni_restricted_person | data_api_error El número de DNI pertenece a una persona con restricción registrada. | Flujo App to App, durante la validación del número de DNI. | El DNI consultado presenta una restricción que impide continuar con el flujo de autenticación o validación. | Mostrar el mensaje controlado y no permitir continuar con la operación. Si corresponde, derivar al canal de soporte o atención definido. |
| 14 | 60999 | dni_without_information | data_api_error No se encontró información asociada al número de DNI ingresado. | Flujo App to App, durante la validación del número de DNI. | El DNI no cuenta con información disponible, no fue encontrado o no | Solicitar al usuario verificar el número de DNI ingresado e intentar nuevamente. Si persiste, |

32

PLATAFORMA DE AUTENTICACIÓN DE LA IDENTIDAD DIGITAL ID-PERÚ

|  |  |  |  |  | pudo ser validado en la fuente correspondiente. | derivar al canal de soporte. |
| --- | --- | --- | --- | --- | --- | --- |
| 15 | 69999 | service_unavailable | data_api_error Servicio no disponible. Por favor, inténtalo nuevamente más tarde. | Flujo App to App, al intentar comunicarse con la plataforma o con un servicio interno requerido. | El servicio no se encuentra disponible temporalmente, existe una caída del backend, indisponibilidad de red, mantenimiento o error general no clasificado. | Informar al usuario que el servicio no está disponible temporalmente. Registrar la incidencia y escalar al equipo técnico si el problema persiste. |

***Tabla 23: Catalogo de mensajes enviados por la aplicación móvil ID Perú***

33