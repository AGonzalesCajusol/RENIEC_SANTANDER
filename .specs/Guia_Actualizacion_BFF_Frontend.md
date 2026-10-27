# Guía Paso a Paso: Actualización y Despliegue del BFF y Frontend

Esta guía describe el procedimiento operativo estándar para actualizar tanto el backend (**BFF en FastAPI**) como la aplicación web (**Frontend en React/Vite**) en el servidor de producción o pruebas (ej. `http://34.230.11.10/`).

---

## 📋 Resumen Rápido de Reinicios

| Qué actualizaste | ¿Reiniciar Nginx? | ¿Reiniciar Servicio BFF? |
| :--- | :---: | :---: |
| **Código o dependencias de Python (BFF)** | ❌ No | **✅ SÍ (`systemctl restart reniec-bff`)** |
| **Archivos estáticos del Frontend (`dist/`)** | ❌ No | ❌ No (Nginx lee los archivos nuevos al instante) |
| **Configuración de Nginx (`/etc/nginx/...`)** | **✅ SÍ (`systemctl reload nginx`)** | ❌ No |

---

## 🚀 Procedimiento Completo en el Servidor

Conéctate por SSH a tu servidor y sigue estos pasos:

### Paso 1: Descargar los últimos cambios de Git

```bash
# 1. Ubicarse en la raíz del proyecto
cd /var/www/RENIEC_SANTANDER   # (o la ruta donde esté clonado el repo en tu servidor)

# 2. Descargar la versión más reciente
git pull origin main
```

---

### Paso 2: Actualizar el Backend (BFF)

1. **Entrar al directorio del BFF:**
   ```bash
   cd bff
   ```

2. **Sincronizar las dependencias con `uv`:**
   ```bash
   uv sync
   ```
   *(Esto actualizará automáticamente el entorno `.venv` con las librerías declaradas en `uv.lock`, incluyendo `httpx`, `fastapi`, `sqlmodel`, etc.)*

3. **Ejecutar migraciones de base de datos (si las hubiera):**
   ```bash
   uv run python -c "from core.database import init_db; init_db()"
   ```

4. **Reiniciar el servicio del BFF en Systemd:**
   ```bash
   sudo systemctl restart reniec-bff
   ```

5. **Verificar que el BFF arrancó correctamente:**
   ```bash
   sudo systemctl status reniec-bff
   ```
   *(Debe aparecer en verde como `active (running)`)*.

6. **Probar el healthcheck:**
   ```bash
   curl -i http://localhost:8000/health
   # O directamente desde la IP pública:
   curl -i http://34.230.11.10/health
   ```

---

### Paso 3: Actualizar el Frontend (React + Vite)

Dado que Nginx sirve los archivos HTML, CSS y JS ya compilados, se debe compilar la nueva versión:

1. **Entrar al directorio del frontend:**
   ```bash
   cd ../frontend
   ```

2. **Instalar dependencias de Node.js (si se agregaron paquetes nuevos):**
   ```bash
   npm install
   ```

3. **Verificar las variables de entorno:**
   Asegúrate de que el archivo `.env` del frontend apunte a tu servidor:
   ```bash
   cat .env
   # Debe contener:
   # VITE_API_URL=http://34.230.11.10
   # VITE_USE_MOCK=false
   ```

4. **Compilar el build de producción:**
   ```bash
   npm run build
   ```
   *(Esto generará los nuevos archivos optimizados en la carpeta `dist/`)*.

5. **Copiar los archivos generados al directorio público de Nginx:**
   *(Si el frontend compila directamente en la carpeta donde Nginx lee, este paso no es necesario. Si usas una ruta web dedicada, copia los archivos)*:
   ```bash
   # Ejemplo si Nginx lee desde /var/www/html o similar:
   sudo cp -r dist/* /var/www/RENIEC_SANTANDER/frontend/dist/
   ```

6. **Ajustar permisos y SELinux (en entornos RHEL / Rocky / CentOS):**
   ```bash
   sudo restorecon -Rv /var/www/RENIEC_SANTANDER/frontend/dist
   ```

---

## 🔍 Verificación Final en el Navegador

1. Abre tu navegador web e ingresa a:
   ```text
   http://34.230.11.10/
   ```
2. Realiza un **Hard Refresh** en el navegador para limpiar la caché de archivos viejos:
   * **Windows / Linux:** `Ctrl + F5` o `Ctrl + Shift + R`
   * **Mac:** `Cmd + Shift + R`
3. Comprueba que aparezcan las dos opciones:
   * 📱 **Flujo DNI Digital (Perú Pass - 3 Pantallas)**
   * 🔑 **Flujo ID-Perú CIBA**
4. Haz clic en *"Iniciar con DNI Digital"*, escanea el código QR con **Perú Pass** y verifica que los datos lleguen correctamente a la Pantalla 3.

---

## 🛠️ Solución de Problemas Frecuentes

* **Si el BFF no arranca:**
  Revisa los logs detallados del servicio con:
  ```bash
  journalctl -u reniec-bff -n 50 --no-pager
  ```

* **Si la base de datos no conecta:**
  Verifica que el servicio de PostgreSQL esté arriba:
  ```bash
  sudo systemctl status postgresql
  # o si está en docker:
  docker ps -a
  ```

* **Si el frontend muestra una pantalla en blanco:**
  Abre la consola de desarrollador del navegador (`F12` -> *Console*) para ver si hay algún error de carga de recursos o de conexión con `/api`.
