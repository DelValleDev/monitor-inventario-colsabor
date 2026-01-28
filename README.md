# 📦 Monitor de Inventario Inteligente - Colsabor

Aplicación web con Streamlit para monitorear el inventario conectado a la API de Siigo.

## 🚀 Características

- **Carga de Excel**: Sube archivos `.xlsx` con inventario mínimo
- **Conexión API Siigo**: Autenticación y consulta de stock en tiempo real
- **Procesamiento Inteligente**: Cruce automático de datos y detección de faltantes
- **Visualización**: Tabla interactiva con filtros y métricas
- **Exportación**: Genera reportes en Excel y HTML para imprimir

## 📋 Requisitos

- Python 3.8 o superior
- Credenciales de API de Siigo (opcional - incluye modo demostración)

## 🔧 Instalación

1. **Crear entorno virtual** (recomendado):
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar credenciales** (opcional):
   
   Abre `app.py` y modifica las variables al inicio:
   ```python
   SIIGO_API_BASE_URL = "https://api.siigo.com/v1"
   SIIGO_USERNAME = "tu_usuario@empresa.com"
   SIIGO_ACCESS_KEY = "tu_access_key_aqui"
   ```

## ▶️ Ejecutar la Aplicación

```bash
streamlit run app.py
```

La aplicación se abrirá en tu navegador en `http://localhost:8501`

## 📁 Formato del Archivo Excel

El archivo Excel debe contener las siguientes columnas:

| Columna | Descripción |
|---------|-------------|
| Referencia | Código único del producto (debe coincidir con Siigo) |
| Nombre | Nombre descriptivo del producto |
| Inventario Mínimo por gramos | Cantidad mínima de stock requerida |

### Ejemplo:

| Referencia | Nombre | Inventario Mínimo por gramos |
|------------|--------|------------------------------|
| REF001 | Harina de Trigo 1kg | 500 |
| REF002 | Azúcar Refinada 1kg | 300 |
| REF003 | Sal Marina 500g | 200 |

## 🎮 Modo Demostración

Si no tienes credenciales de Siigo, puedes usar el **Modo Demostración** para probar la aplicación con datos simulados.

## 📊 Estados del Inventario

- 🔴 **Crítico**: Stock actual menor al mínimo requerido
- 🟡 **Bajo**: Stock actual entre el mínimo y 120% del mínimo
- 🟢 **OK**: Stock actual por encima del 120% del mínimo
- ⚠️ **No encontrado**: Referencia no existe en Siigo

## 🖨️ Impresión de Reportes

1. Filtra los productos que deseas imprimir
2. Haz clic en "Imprimir Lista de Faltantes"
3. Se abrirá una nueva pestaña con el reporte
4. Usa `Ctrl+P` para imprimir

## 📂 Estructura del Proyecto

```
inventory_monitor/
├── app.py              # Aplicación principal
├── requirements.txt    # Dependencias
├── README.md          # Este archivo
└── plantilla_ejemplo.xlsx  # Plantilla de ejemplo
```

## 🔒 Seguridad

- Las credenciales de Siigo se almacenan localmente
- Se recomienda usar variables de entorno en producción
- Los tokens de autenticación expiran automáticamente

## 🐛 Solución de Problemas

### Error de autenticación con Siigo
- Verifica que las credenciales sean correctas
- Asegúrate de que tu cuenta tenga acceso a la API

### Producto no encontrado en Siigo
- Verifica que la referencia en el Excel coincida exactamente con Siigo
- Revisa espacios en blanco o caracteres especiales

### Error al cargar Excel
- Asegúrate de que el archivo tenga formato `.xlsx`
- Verifica que las columnas tengan los nombres correctos

## 📞 Soporte

Para soporte técnico, contacta al equipo de desarrollo.

---

**Colsabor © 2026** - Monitor de Inventario Inteligente
