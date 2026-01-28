# 🔧 Configuración de Google Sheets (Base de Datos)

Esta app usa Google Sheets como base de datos para guardar el inventario de cada usuario.

## 📋 Pasos para Configurar

### 1️⃣ Crear Proyecto en Google Cloud

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Nombre sugerido: "Colsabor-Inventario"

### 2️⃣ Habilitar APIs necesarias

1. En el menú lateral, ve a **"APIs y servicios"** > **"Biblioteca"**
2. Busca y habilita:
   - **Google Sheets API**
   - **Google Drive API**

### 3️⃣ Crear Cuenta de Servicio

1. Ve a **"APIs y servicios"** > **"Credenciales"**
2. Click en **"Crear credenciales"** > **"Cuenta de servicio"**
3. Nombre: `colsabor-inventario-service`
4. Descripción: `Servicio para guardar inventarios`
5. Click **"Crear y continuar"**
6. Rol: **"Editor"** (o "Propietario" para más permisos)
7. Click **"Listo"**

### 4️⃣ Generar Clave JSON

1. En la lista de cuentas de servicio, click en la que acabas de crear
2. Ve a la pestaña **"Claves"**
3. Click **"Agregar clave"** > **"Crear nueva clave"**
4. Selecciona **JSON**
5. Click **"Crear"** - Se descargará un archivo `.json`

**⚠️ IMPORTANTE:** Guarda este archivo de forma segura. Contiene las credenciales.

### 5️⃣ Configurar en Streamlit Cloud

1. Ve a tu app en [share.streamlit.io](https://share.streamlit.io)
2. Click en **"Settings"** (⚙️) > **"Secrets"**
3. Agrega el siguiente contenido (copiando del archivo JSON):

```toml
[gcp_service_account]
type = "service_account"
project_id = "tu-project-id"
private_key_id = "tu-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nTU_CLAVE_PRIVADA_AQUI\n-----END PRIVATE KEY-----\n"
client_email = "tu-service-account@tu-project-id.iam.gserviceaccount.com"
client_id = "tu-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "tu-cert-url"
```

### 6️⃣ Compartir la Hoja de Cálculo (Automático)

La app creará automáticamente una hoja llamada **"Colsabor_Inventarios"**.

Si quieres acceso manual:
1. Copia el **email de la cuenta de servicio** (del archivo JSON: `client_email`)
2. Abre Google Sheets
3. Busca la hoja "Colsabor_Inventarios"
4. Click en **"Compartir"**
5. Pega el email de la cuenta de servicio
6. Dale permisos de **"Editor"**

---

## 🧪 Probar Localmente (Opcional)

Si quieres probar en tu computadora:

1. Guarda el archivo JSON descargado como `service_account.json` en la carpeta del proyecto

2. Crea un archivo `.streamlit/secrets.toml` con el contenido del JSON:

```toml
[gcp_service_account]
type = "service_account"
project_id = "..."
# ... resto del contenido
```

3. Ejecuta: `streamlit run app.py`

---

## ✅ Verificar que Funciona

1. Inicia sesión en la app
2. Sube un archivo Excel
3. Deberías ver: **"✅ Inventario guardado en Google Sheets"**
4. Ve a [Google Sheets](https://docs.google.com/spreadsheets/)
5. Busca la hoja **"Colsabor_Inventarios"**
6. Deberías ver una pestaña con tu inventario: `Inventario_tu_usuario`

---

## 📊 Estructura de la Hoja

La hoja creará automáticamente:
- **Una pestaña por usuario**: `Inventario_usuario`
- **Columnas**: Las mismas del Excel (Referencia, Nombre, Inventario Mínimo)
- **Metadatos**: Fecha de última actualización en columna Z

---

## 🔒 Seguridad

- ✅ Las credenciales están en Streamlit Secrets (no en el código)
- ✅ Solo la app tiene acceso a la hoja
- ✅ Los usuarios no ven las credenciales
- ✅ Cada usuario solo trabaja con su pestaña

---

## ❓ Problemas Comunes

### "Google Sheets no configurado"
- Verifica que agregaste las credenciales en Streamlit Secrets
- Asegúrate de copiar TODO el contenido del JSON
- Revisa que no haya errores de formato en el TOML

### "Permission denied"
- La cuenta de servicio necesita acceso a la hoja
- Comparte la hoja con el email de la cuenta de servicio

### "API not enabled"
- Habilita Google Sheets API y Google Drive API en Google Cloud Console

---

## 📞 Soporte

Si tienes problemas, revisa:
- [Documentación de gspread](https://docs.gspread.org/)
- [Google Cloud IAM](https://console.cloud.google.com/iam-admin)
