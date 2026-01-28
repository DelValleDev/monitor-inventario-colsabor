# 🚀 Cómo Subir la Aplicación Gratis a Internet

## Opción 1: Streamlit Community Cloud (RECOMENDADO - 100% GRATIS)

### Paso 1: Crear cuenta en GitHub
1. Ve a [github.com](https://github.com) y crea una cuenta gratuita
2. Verifica tu correo electrónico

### Paso 2: Subir tu código a GitHub
1. Crea un nuevo repositorio:
   - Click en "New repository"
   - Nombre: `monitor-inventario-colsabor`
   - Selecciona "Public"
   - Click "Create repository"

2. Sube los archivos:
   - `app.py`
   - `requirements.txt`
   - `README.md`
   - `.streamlit/config.toml` (crear esta carpeta y archivo)

### Paso 3: Crear archivo de configuración

Crea una carpeta `.streamlit` y dentro un archivo `config.toml` con este contenido:

```toml
[theme]
primaryColor = "#2196F3"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
headless = true
port = 8501
```

### Paso 4: Configurar Streamlit Cloud
1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Inicia sesión con tu cuenta de GitHub
3. Click en "New app"
4. Selecciona tu repositorio: `monitor-inventario-colsabor`
5. Branch: `main`
6. Main file path: `inventory_monitor/app.py`
7. Click "Deploy!"

### Paso 5: Uso de la Aplicación
**Cada usuario usa su email y contraseña de Siigo:**  
Cada persona que use la app deberá ingresar:
- Su usuario/correo de Siigo
- Su contraseña personal de Siigo

**El Access Key es compartido** - La empresa tiene un único Access Key de API configurado en el código, pero cada usuario se identifica con su propio usuario y contraseña para mayor control y seguridad.

### ✅ ¡Listo!
Tu aplicación estará disponible en una URL como:
`https://monitor-inventario-colsabor.streamlit.app`

Comparte esta URL con todos en tu empresa. **Cada usuario ingresa con su usuario y contraseña personal de Siigo.**

---

## Opción 2: Render.com (GRATIS con límites)

### Paso 1: Crear cuenta
1. Ve a [render.com](https://render.com)
2. Crea cuenta gratuita con GitHub

### Paso 2: Crear Web Service
1. Click "New +"
2. Selecciona "Web Service"
3. Conecta tu repositorio de GitHub
4. Configura:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `streamlit run inventory_monitor/app.py --server.port $PORT --server.address 0.0.0.0`
   - **Environment:** Python 3

### Paso 3: Deploy
Click "Create Web Service" y espera 5-10 minutos.

---

## Opción 3: PythonAnywhere (GRATIS básico)

### Paso 1: Crear cuenta
1. Ve a [pythonanywhere.com](https://www.pythonanywhere.com)
2. Crea cuenta gratuita

### Paso 2: Configurar
1. Ve a "Web" tab
2. Click "Add a new web app"
3. Selecciona "Manual configuration"
4. Python 3.10

### Paso 3: Subir código
1. Usa "Files" tab para subir archivos
2. O clona tu repositorio de GitHub desde la consola Bash

---

## ⚙️ Uso Compartido en la Empresa

### Sistema de Seguridad:
✅ **Credenciales individuales:** Cada usuario usa su propia cuenta de Siigo  
✅ **Mayor seguridad:** No hay credenciales compartidas  
✅ **Trazabilidad:** Se puede identificar quién accede al sistema  
✅ **Sin configuración del servidor:** No se guardan credenciales en el código  

### Cómo lo usarán tus compañeros:
1. Abren la URL de la app
2. Ingresan su correo de Siigo
3. Ingresan su Access Key de Siigo
4. Click en "Conectar a Siigo"
5. ¡Listo! Ya pueden usar la app

### Requisitos para cada usuario:
- ✅ Cuenta activa de Siigo
- ✅ Username (correo)
- ✅ Access Key de API

**¿Cómo obtener credenciales de Siigo?**  
Cada usuario debe contactar al administrador de Siigo de la empresa para obtener su Username y Access Key de API.

### Límites del plan gratuito de Streamlit Cloud:
- ✅ Usuarios ilimitados
- ✅ Uso ilimitado
- ✅ 1 GB de recursos
- ✅ 100% gratis para siempre

---

## 🔒 Ventajas de Seguridad

### Con credenciales individuales:
1. **Auditabilidad:** Cada usuario se identifica con su propia cuenta
2. **Control de acceso:** Solo usuarios con credenciales válidas pueden acceder
3. **Sin riesgo de compartir:** No hay contraseñas en el código fuente
4. **Revocación individual:** Se puede desactivar el acceso de un usuario específico
5. **Cumplimiento:** Mejor alineación con políticas de seguridad empresarial

---

## 🔒 Seguridad Adicional (Opcional)

Si quieres agregar validación extra o credenciales de respaldo, puedes usar Streamlit Secrets:

1. En tu app de Streamlit Cloud, ve a Settings > Secrets
2. Agrega credenciales de administrador (opcional):
```toml
ADMIN_EMAIL = "admin@colsabor.com.co"
ADMIN_KEY = "clave_administrador_backup"
```

3. Estas solo se usarían como credenciales de emergencia o para funciones administrativas adicionales.

---

## 📞 Soporte

Si tienes problemas con el deployment:
- Documentación Streamlit: https://docs.streamlit.io/streamlit-community-cloud
- Foro de la comunidad: https://discuss.streamlit.io/
