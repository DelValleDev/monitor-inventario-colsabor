# 📦 Monitor de Inventario Inteligente - Colsabor

Sistema web moderno para monitorear y controlar el inventario conectado a la API de Siigo.

## ✨ Características

- 🔐 **Login simplificado:** Solo requiere email del usuario
- 🔄 **Sincronización automática con Siigo:** Obtiene todos los productos automáticamente
- 📊 **Análisis inteligente:** Compara inventario mínimo vs stock actual
- 🎨 **Diseño moderno:** Interfaz azul con temas claro/oscuro
- 📥 **Exportación múltiple:** Excel y PDF para imprimir
- 🔍 **Filtros avanzados:** Por estado y búsqueda por texto
- ⚡ **100% en español:** Toda la interfaz en español

## 🚀 Inicio Rápido

### Opción 1: Usar la app en la nube (Recomendado)
Ver instrucciones completas en [DEPLOYMENT.md](DEPLOYMENT.md)

### Opción 2: Ejecutar localmente

1. **Clonar o descargar el proyecto**

2. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

3. **Ejecutar la aplicación:**
```bash
streamlit run app.py
```

4. **Abrir en el navegador:**
La app se abrirá automáticamente en `http://localhost:8501`

## 📋 Formato del Excel

El archivo Excel debe contener estas columnas:

| Columna | Descripción | Ejemplo |
|---------|-------------|---------|
| Referencia | Código del producto | REF001 |
| Nombre | Nombre del producto | Harina de Trigo 1kg |
| Inventario Mínimo por gramos | Stock mínimo requerido | 500 |

## 🎯 Cómo Usar

1. **Iniciar sesión:** Ingresa tu correo de Colsabor
2. **Subir Excel:** Carga tu archivo con el inventario mínimo
3. **Revisar resultados:** La app mostrará:
   - 🔴 Productos críticos (por debajo del mínimo)
   - 🟡 Productos con stock bajo
   - 🟢 Productos OK
   - ⚠️ Productos no encontrados en Siigo
4. **Exportar:** Descarga reportes en Excel o imprime en PDF

## 🔒 Seguridad

- ✅ Todos los usuarios de la empresa usan las mismas credenciales de Siigo (configuradas en el código)
- ✅ No se requiere que cada usuario tenga credenciales de Siigo
- ✅ Solo se pide el email para identificación interna
- ✅ Las credenciales de API están protegidas en el servidor

## 📊 Estados del Inventario

- **🔴 Crítico:** Stock actual < Inventario mínimo
- **🟡 Bajo:** Stock actual entre mínimo y 120% del mínimo
- **🟢 OK:** Stock actual > 120% del mínimo
- **⚠️ No encontrado:** Producto no existe en Siigo

## 🛠️ Tecnologías

- **Streamlit:** Framework web para Python
- **Pandas:** Procesamiento de datos y Excel
- **Requests:** Comunicación con API de Siigo
- **OpenPyXL:** Lectura/escritura de archivos Excel

## 📦 Deployment

Para subir la aplicación gratis y que todos en la empresa la usen:

1. **Streamlit Community Cloud (Recomendado):** 100% gratis, usuarios ilimitados
2. **Render.com:** Plan gratuito disponible
3. **PythonAnywhere:** Plan básico gratuito

Ver guía completa en [DEPLOYMENT.md](DEPLOYMENT.md)

## 🤝 Uso Compartido

**Una sola API para todos:**  
Todos los usuarios de la empresa utilizan las mismas credenciales de Siigo automáticamente. No necesitas configurar nada adicional.

**Límite de usuarios:** Ilimitado ✅

## 📞 Soporte

Si necesitas ayuda:
- Revisa [DEPLOYMENT.md](DEPLOYMENT.md) para instrucciones de deployment
- Consulta la documentación de Streamlit: https://docs.streamlit.io
- Revisa la API de Siigo: https://siigoapi.docs.apiary.io

## 📝 Licencia

© 2026 Colsabor - Uso interno de la empresa
