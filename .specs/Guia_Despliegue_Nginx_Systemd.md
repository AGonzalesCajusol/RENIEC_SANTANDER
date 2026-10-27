# GUÍA DE DESPLIEGUE EN PRODUCCIÓN (AMAZON LINUX 2023 / AL2023)
## Base de Datos (Docker / Nativo) + Backend BFF (FastAPI) + Frontend (Nginx)
### Santander Perú · Plataforma ID-Perú (RENIEC)

---

| Metadato | Detalle |
| :--- | :--- |
| **Versión** | 1.3 |
| **Fecha** | Octubre 2026 |
| **Sistema Operativo** | **Amazon Linux 2023 (AL2023)** |
| **Base de Datos** | PostgreSQL 17 (vía Docker en puerto 5435 o Nativo con DNF) |
| **BFF / Backend** | FastAPI + SQLModel + Psycopg 3 |
| **Web Server / Proxy** | Nginx 1.20+ (servidor estáticos en `/var/www` y Reverse Proxy) |
| **Estado** | Aprobado para Despliegue en AWS EC2 |

---

## 1. INSTALACIÓN Y CONFIGURACIÓN DE LA BASE DE DATOS (POSTGRESQL)

Tienes dos métodos para tener PostgreSQL corriendo en el puerto **`5435`** con la base de datos `reniec_santander_db`:

### Opción A: Mediante Docker (Recomendada / Idéntica a tu entorno actual)

En tu entorno actual, PostgreSQL corre como un contenedor Docker (`postgres:17-alpine`) exponiendo el puerto `5435`.

1. **Instalar e iniciar Docker en Amazon Linux 2023:**
   ```bash
   sudo dnf install -y docker
   sudo systemctl enable --now docker
   sudo usermod -aG docker ec2-user
   ```
   *(Cierra sesión y vuelve a entrar por SSH para aplicar los permisos de grupo).*

2. **Crear y levantar el contenedor de PostgreSQL:**
   ```bash
   docker run -d \
     --name reniec-santander-db \
     --restart always \
     -p 5435:5432 \
     -e POSTGRES_USER=postgres \
     -e POSTGRES_PASSWORD=postgres \
     -e POSTGRES_DB=reniec_santander_db \
     -v pgdata_santander:/var/lib/postgresql/data \
     postgres:17-alpine
   ```

3. **Verificar que el contenedor esté corriendo:**
   ```bash
   docker ps
   ```

---

### Opción B: Instalación Nativa en Amazon Linux 2023 (Servicio del Sistema)

Si prefieres instalar el servicio de PostgreSQL directamente en el sistema operativo sin Docker:

1. **Instalar el servidor de PostgreSQL 15 en AL2023:**
   ```bash
   sudo dnf install -y postgresql15-server postgresql15
   ```

2. **Inicializar y cambiar el puerto a 5435:**
   ```bash
   # Inicializar la base de datos
   sudo postgresql-setup --initdb

   # Configurar el puerto 5435 en postgresql.conf
   sudo sed -i "s/#port = 5432/port = 5435/g" /var/lib/pgsql/data/postgresql.conf

   # Permitir autenticación local por contraseña en pg_hba.conf
   sudo sed -i 's/ident/md5/g' /var/lib/pgsql/data/pg_hba.conf
   sudo sed -i 's/scram-sha-256/md5/g' /var/lib/pgsql/data/pg_hba.conf

   # Iniciar el servicio
   sudo systemctl enable --now postgresql
   ```

3. **Crear el usuario y la base de datos:**
   ```bash
   # Acceder como usuario postgres
   sudo -u postgres psql -p 5435 -c "ALTER USER postgres PASSWORD 'postgres';"
   sudo -u postgres psql -p 5435 -c "CREATE DATABASE reniec_santander_db;"
   ```

---

## 2. INSTALACIÓN DE DEPENDENCIAS DEL SISTEMA

Instalar Python, Node.js y Nginx con `dnf`:

```bash
sudo dnf update -y
sudo dnf install -y python3 python3-pip python3-devel git gcc nodejs npm nginx
sudo systemctl enable nginx
```

---

## 3. INSTALACIÓN DEL BACKEND (BFF) Y CONEXIÓN A POSTGRESQL

1. **Crear el entorno virtual `.venv`:**
   ```bash
   cd /home/ec2-user/RENIEC_SANTANDER/bff
   python3 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

2. **Configurar el archivo `bff/.env`:**
   ```bash
   cp .env.example .env
   nano .env
   ```
   Asegúrate de que contenga:
   ```ini
   RENIEC_BASE_URL=https://idaas2.reniec.gob.pe
   RENIEC_CLIENT_ID=tu_client_id
   RENIEC_CLIENT_SECRET=tu_client_secret
   RENIEC_REFERER=santander.com.pe
   URL_NOTIFY=http://34.230.11.10/api/auth/notify
   REQUEST_TIMEOUT=15

   # Conexión exacta a PostgreSQL en puerto 5435 (usar 127.0.0.1 para evitar demoras/timeout de resolución IPv6 con Docker)
   DATABASE_URL=postgresql+psycopg://postgres:postgres@127.0.0.1:5435/reniec_santander_db
   ```

3. **Probar la conexión a la base de datos y auto-creación de tablas:**
   ```bash
   python3 -c "from core.database.session import init_db; init_db()"
   ```
   *Debe imprimir: `Base de datos PostgreSQL inicializada exitosamente.`*

---

## 4. CREAR EL SERVICIO DE SYSTEMD PARA EL BACKEND

Crear el archivo `/etc/systemd/system/reniec-bff.service`:

```bash
sudo nano /etc/systemd/system/reniec-bff.service
```

Contenido:
```ini
[Unit]
Description=BFF RENIEC Santander CIBA (FastAPI)
After=network.target

[Service]
User=ec2-user
Group=ec2-user
WorkingDirectory=/home/ec2-user/RENIEC_SANTANDER/bff
Environment="PATH=/home/ec2-user/RENIEC_SANTANDER/bff/.venv/bin:/usr/bin"
ExecStart=/home/ec2-user/RENIEC_SANTANDER/bff/.venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --workers 4

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Iniciar el servicio:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now reniec-bff
sudo systemctl status reniec-bff
```

---

## 5. COMPILAR EL FRONTEND Y COPIAR A `/var/www`

1. Configurar `frontend/.env`:
   ```bash
   cd /home/ec2-user/RENIEC_SANTANDER/frontend
   nano .env
   ```
   ```ini
   VITE_API_URL=http://34.230.11.10
   VITE_USE_MOCK=false
   ```

2. Compilar con Vite:
   ```bash
   sudo chown -R ec2-user:ec2-user /home/ec2-user/RENIEC_SANTANDER/frontend
   npm install
   npm run build
   ```

3. Copiar a la ruta web `/var/www`:
   ```bash
   sudo mkdir -p /var/www/RENIEC_SANTANDER/frontend/dist
   sudo cp -r dist/* /var/www/RENIEC_SANTANDER/frontend/dist/
   sudo chown -R nginx:nginx /var/www/RENIEC_SANTANDER
   sudo chmod -R 755 /var/www/RENIEC_SANTANDER
   ```

---

## 6. CONFIGURAR NGINX Y SELINUX

1. Configurar Nginx en `/etc/nginx/conf.d/santander.conf`:
   ```bash
   sudo nano /etc/nginx/conf.d/santander.conf
   ```

   ```nginx
   server {
       listen 80;
       server_name 34.230.11.10;

       # Frontend estático
       root /var/www/RENIEC_SANTANDER/frontend/dist;
       index index.html index.htm;

       location / {
           try_files $uri $uri/ /index.html;
       }

       location ~* \.(?:ico|css|js|gif|jpe?g|png|woff2?|eot|ttf|svg)$ {
           expires 6M;
           access_log off;
           add_header Cache-Control "public";
       }

       # Backend Reverse Proxy hacia Uvicorn (:8000)
       location /api/ {
           proxy_pass http://127.0.0.1:8000;
           proxy_http_version 1.1;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }

       location ~ ^/(health|docs|redoc|openapi.json) {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }

       error_page 404 /index.html;
   }
   ```

2. **Permitir tráfico de red en SELinux:**
   ```bash
   sudo setsebool -P httpd_can_network_connect 1
   sudo restorecon -Rv /var/www/RENIEC_SANTANDER/frontend/dist
   ```

3. **Recargar Nginx:**
   ```bash
   sudo nginx -t && sudo systemctl restart nginx
   ```
