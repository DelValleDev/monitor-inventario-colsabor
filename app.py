"""
Monitor de Inventario Inteligente - Colsabor
Aplicación Streamlit para monitorear inventario conectado a Siigo API
"""

import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import base64
from io import BytesIO
import gspread
from google.oauth2.service_account import Credentials
import json

# ============================================================================
# CONFIGURACIÓN DE CREDENCIALES SIIGO API
# ============================================================================
# URL base de la API de Siigo (fija para todos los usuarios)
SIIGO_API_BASE_URL = "https://api.siigo.com/v1"
# Access Key compartido de la empresa (mismo para todos)
SIIGO_ACCESS_KEY = "MmQzMDk0NjYtZjc3Ny00YzU0LWFmNDMtMjhiYzcxNGM5NTBhOnoyeTk5KE4uYkc="

# ============================================================================
# CONFIGURACIÓN DE GOOGLE SHEETS
# ============================================================================
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Nombre de la hoja de cálculo (se creará si no existe)
SPREADSHEET_NAME = "Colsabor_Inventarios"

# ============================================================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================================================
st.set_page_config(
    page_title="Monitor de Inventario - Colsabor",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilos CSS personalizados - Tema azul moderno
st.markdown(
    """
<style>
    /* Colores principales */
    :root {
        --primary-blue: #2196F3;
        --primary-blue-light: #64B5F6;
        --primary-blue-dark: #1976D2;
        --accent-blue: #03A9F4;
    }
    
    /* Header principal */
    .header-title {
        background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
        color: white !important;
        text-align: center;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(33, 150, 243, 0.3);
        margin-bottom: 20px;
    }
    
    /* Tarjetas de métricas */
    .metric-card {
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(33, 150, 243, 0.3);
    }
    
    /* Login box */
    .login-box {
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(33, 150, 243, 0.2);
        text-align: center;
        margin: 20px auto;
        max-width: 500px;
    }
    
    /* Botones */
    .stButton>button {
        background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 4px rgba(33, 150, 243, 0.3) !important;
        transition: all 0.3s !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(33, 150, 243, 0.4) !important;
    }
    
    /* DataFrames */
    .stDataFrame {
        font-size: 14px;
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* Filas críticas en tabla */
    .critical-row {
        background-color: #ffcdd2 !important;
    }
    
    /* Modo oscuro */
    @media (prefers-color-scheme: dark) {
        .header-title {
            background: linear-gradient(135deg, #1565C0 0%, #0D47A1 100%);
        }
        
        .metric-card, .login-box {
            background: linear-gradient(135deg, #1E3A5F 0%, #2C5282 100%);
            color: #E3F2FD;
        }
        
        .stButton>button {
            background: linear-gradient(135deg, #1976D2 0%, #0D47A1 100%) !important;
        }
    }
    
    /* Impresión */
    @media print {
        .no-print {
            display: none !important;
        }
    }
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================================
# FUNCIONES DE AUTENTICACIÓN Y API SIIGO
# ============================================================================


def autenticar_siigo(username: str, access_key: str) -> dict:
    """
    Autentica con la API de Siigo y obtiene el token de acceso.

    Args:
        username: Usuario de Siigo
        access_key: Clave de acceso de Siigo

    Returns:
        dict: Respuesta con el token o error
    """
    url = "https://api.siigo.com/auth"

    headers = {"Content-Type": "application/json", "Partner-Id": "ColsaborApp"}

    payload = {"username": username, "access_key": access_key}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)

        if response.status_code == 200:
            return {"success": True, "token": response.json().get("access_token")}
        else:
            return {
                "success": False,
                "error": f"Error de autenticación: {response.status_code} - {response.text}",
            }
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Error de conexión: {str(e)}"}


def obtener_todos_los_productos_siigo(token: str) -> dict:
    """
    Obtiene TODOS los productos de Siigo con paginación.

    Args:
        token: Token de autenticación

    Returns:
        dict: Lista de todos los productos
    """
    url = f"{SIIGO_API_BASE_URL}/products"

    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "Partner-Id": "ColsaborApp",
    }

    todos_productos = []
    page = 1
    page_size = 100  # Aumentar tamaño de página para menos requests

    try:
        while True:
            params = {"page": page, "page_size": page_size}

            response = requests.get(url, headers=headers, params=params, timeout=60)

            if response.status_code == 200:
                data = response.json()

                # Manejar diferentes formatos de respuesta
                productos_pagina = []
                if isinstance(data, list):
                    productos_pagina = data
                elif isinstance(data, dict) and "results" in data:
                    productos_pagina = data["results"]

                # Si no hay más productos, salir del loop
                if not productos_pagina or len(productos_pagina) == 0:
                    break

                todos_productos.extend(productos_pagina)

                # Si obtuvimos menos productos que el page_size, es la última página
                if len(productos_pagina) < page_size:
                    break

                page += 1

            else:
                return {
                    "success": False,
                    "error": f"Error al obtener productos: {response.status_code} - {response.text}",
                }

        return {"success": True, "data": todos_productos, "total": len(todos_productos)}

    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Error de conexión: {str(e)}"}}


# ============================================================================
# FUNCIONES DE GOOGLE SHEETS (BASE DE DATOS)
# ============================================================================


def conectar_google_sheets():
    """
    Conecta con Google Sheets usando credenciales de Streamlit Secrets.

    Returns:
        gspread.Client: Cliente autenticado de Google Sheets o None
    """
    try:
        # Obtener credenciales desde Streamlit Secrets
        if "gcp_service_account" in st.secrets:
            credentials_dict = dict(st.secrets["gcp_service_account"])
            credentials = Credentials.from_service_account_info(
                credentials_dict, scopes=SCOPES
            )
            client = gspread.authorize(credentials)
            return client
        else:
            return None
    except Exception as e:
        st.error(f"Error al conectar con Google Sheets: {str(e)}")
        return None


def obtener_o_crear_spreadsheet(client):
    """
    Obtiene la hoja de cálculo o la crea si no existe.

    Args:
        client: Cliente de Google Sheets autenticado

    Returns:
        gspread.Spreadsheet: Hoja de cálculo
    """
    try:
        # Intentar abrir la hoja existente
        spreadsheet = client.open(SPREADSHEET_NAME)
    except gspread.SpreadsheetNotFound:
        # Si no existe, crear nueva
        spreadsheet = client.create(SPREADSHEET_NAME)
        # Compartir con el usuario (opcional)
        # spreadsheet.share('usuario@colsabor.com.co', perm_type='user', role='writer')

    return spreadsheet


def guardar_inventario_excel(usuario_email: str, df_excel: pd.DataFrame):
    """
    Guarda el inventario Excel del usuario en Google Sheets.

    Args:
        usuario_email: Email del usuario
        df_excel: DataFrame con el inventario del Excel
    """
    try:
        client = conectar_google_sheets()
        if client is None:
            st.warning("⚠️ Google Sheets no configurado. Los datos no se guardarán.")
            return False

        spreadsheet = obtener_o_crear_spreadsheet(client)

        # Crear o actualizar worksheet para el usuario
        worksheet_name = f"Inventario_{usuario_email.split('@')[0]}"

        try:
            worksheet = spreadsheet.worksheet(worksheet_name)
            worksheet.clear()
        except gspread.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(
                title=worksheet_name, rows=1000, cols=20
            )

        # Convertir DataFrame a lista de listas
        data = [df_excel.columns.tolist()] + df_excel.values.tolist()

        # Guardar en Google Sheets
        worksheet.update("A1", data)

        # Guardar metadatos (fecha de actualización)
        worksheet.update("Z1", [[datetime.now().strftime("%Y-%m-%d %H:%M:%S")]])

        return True
    except Exception as e:
        st.error(f"Error al guardar en Google Sheets: {str(e)}")
        return False


def cargar_inventario_guardado(usuario_email: str):
    """
    Carga el inventario guardado del usuario desde Google Sheets.

    Args:
        usuario_email: Email del usuario

    Returns:
        pd.DataFrame: DataFrame con el inventario o None si no existe
    """
    try:
        client = conectar_google_sheets()
        if client is None:
            return None

        spreadsheet = obtener_o_crear_spreadsheet(client)
        worksheet_name = f"Inventario_{usuario_email.split('@')[0]}"

        try:
            worksheet = spreadsheet.worksheet(worksheet_name)
            data = worksheet.get_all_values()

            if len(data) <= 1:
                return None

            # Convertir a DataFrame
            df = pd.DataFrame(data[1:], columns=data[0])

            # Convertir columna de inventario_minimo a numérico
            if "inventario_minimo" in df.columns:
                df["inventario_minimo"] = pd.to_numeric(
                    df["inventario_minimo"], errors="coerce"
                )

            return df
        except gspread.WorksheetNotFound:
            return None
    except Exception as e:
        st.error(f"Error al cargar desde Google Sheets: {str(e)}")
        return None


def guardar_productos_siigo(productos_siigo: list):
    """
    Guarda los productos de Siigo en Google Sheets (caché compartido).

    Args:
        productos_siigo: Lista de productos de Siigo
    """
    try:
        client = conectar_google_sheets()
        if client is None:
            return False

        spreadsheet = obtener_o_crear_spreadsheet(client)
        worksheet_name = "Cache_Siigo_Productos"

        try:
            worksheet = spreadsheet.worksheet(worksheet_name)
            worksheet.clear()
        except gspread.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(
                title=worksheet_name, rows=5000, cols=10
            )

        # Convertir productos a DataFrame
        df_siigo = procesar_productos_siigo(productos_siigo)
        
        if len(df_siigo) == 0:
            return False

        # Convertir DataFrame a lista de listas
        data = [df_siigo.columns.tolist()] + df_siigo.values.tolist()

        # Guardar en Google Sheets
        worksheet.update("A1", data)

        # Guardar metadatos (fecha de actualización y total)
        metadata = [
            ["ultima_actualizacion", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ["total_productos", len(productos_siigo)]
        ]
        worksheet.update("Z1", metadata)

        return True
    except Exception as e:
        st.warning(f"No se pudieron guardar productos de Siigo: {str(e)}")
        return False


def cargar_productos_siigo_guardados():
    """
    Carga los productos de Siigo guardados desde Google Sheets.

    Returns:
        tuple: (DataFrame procesado, lista de productos raw, timestamp) o None
    """
    try:
        client = conectar_google_sheets()
        if client is None:
            return None

        spreadsheet = obtener_o_crear_spreadsheet(client)
        worksheet_name = "Cache_Siigo_Productos"

        try:
            worksheet = spreadsheet.worksheet(worksheet_name)
            
            # Obtener metadatos
            metadata = worksheet.get("Z1:Z2")
            if not metadata or len(metadata) < 2:
                return None
                
            ultima_actualizacion_str = metadata[0][0] if len(metadata[0]) > 0 else None
            
            if not ultima_actualizacion_str:
                return None
            
            # Verificar si los datos tienen menos de 24 horas
            ultima_actualizacion = datetime.strptime(ultima_actualizacion_str, "%Y-%m-%d %H:%M:%S")
            horas_transcurridas = (datetime.now() - ultima_actualizacion).total_seconds() / 3600
            
            if horas_transcurridas > 24:
                return None  # Datos muy antiguos
            
            # Cargar datos
            data = worksheet.get_all_values()

            if len(data) <= 1:
                return None

            # Convertir a DataFrame
            df_siigo = pd.DataFrame(data[1:], columns=data[0])
            
            # Convertir columna stock_actual a numérico
            if "stock_actual" in df_siigo.columns:
                df_siigo["stock_actual"] = pd.to_numeric(
                    df_siigo["stock_actual"], errors="coerce"
                ).fillna(0)

            return (df_siigo, None, ultima_actualizacion)
            
        except gspread.WorksheetNotFound:
            return None
    except Exception as e:
        return None


# ============================================================================
# FUNCIONES DE PROCESAMIENTO DE DATOS
# ============================================================================


def cargar_excel(archivo) -> pd.DataFrame:
    """
    Carga y valida el archivo Excel de inventario mínimo.

    Args:
        archivo: Archivo subido por el usuario

    Returns:
        pd.DataFrame: DataFrame con los datos del Excel
    """
    try:
        df = pd.read_excel(archivo)

        # Normalizar nombres de columnas
        df.columns = df.columns.str.strip().str.lower()

        # Mapear posibles variaciones de nombres de columnas
        column_mapping = {
            "referencia": "referencia",
            "ref": "referencia",
            "codigo": "referencia",
            "código": "referencia",
            "nombre": "nombre",
            "producto": "nombre",
            "descripcion": "nombre",
            "descripción": "nombre",
            "inventario minimo": "inventario_minimo",
            "inventario mínimo": "inventario_minimo",
            "inventario minimo por gramos": "inventario_minimo",
            "inventario mínimo por gramos": "inventario_minimo",
            "minimo": "inventario_minimo",
            "mínimo": "inventario_minimo",
            "min": "inventario_minimo",
            "stock_minimo": "inventario_minimo",
            "stock minimo": "inventario_minimo",
        }

        df = df.rename(columns=column_mapping)

        # Validar columnas requeridas
        columnas_requeridas = ["referencia", "nombre", "inventario_minimo"]
        columnas_faltantes = [
            col for col in columnas_requeridas if col not in df.columns
        ]

        if columnas_faltantes:
            raise ValueError(
                f"Columnas faltantes en el Excel: {', '.join(columnas_faltantes)}"
            )

        # Limpiar datos
        df["referencia"] = df["referencia"].astype(str).str.strip()
        df["nombre"] = df["nombre"].astype(str).str.strip()
        df["inventario_minimo"] = pd.to_numeric(
            df["inventario_minimo"], errors="coerce"
        ).fillna(0)

        return df

    except Exception as e:
        raise ValueError(f"Error al cargar el Excel: {str(e)}")


def procesar_productos_siigo(productos: list) -> pd.DataFrame:
    """
    Procesa la lista de productos de Siigo a un DataFrame.

    Args:
        productos: Lista de productos de la API

    Returns:
        pd.DataFrame: DataFrame con productos procesados
    """
    datos = []

    for producto in productos:
        # Extraer información relevante
        referencia = producto.get("code", "")
        nombre = producto.get("name", "")

        # Si no tiene código o nombre, saltar
        if not referencia or not nombre:
            continue

        # El stock puede venir en diferentes estructuras según la API
        stock_actual = 0

        # Intentar obtener stock de diferentes ubicaciones posibles
        if "available_quantity" in producto:
            stock_actual = float(producto["available_quantity"])
        elif "stock" in producto:
            stock_actual = float(producto["stock"])
        elif "warehouses" in producto and isinstance(producto["warehouses"], list):
            # Sumar stock de todas las bodegas
            for bodega in producto["warehouses"]:
                stock_actual += float(bodega.get("quantity", 0))

        datos.append(
            {
                "referencia_siigo": str(referencia).strip(),
                "nombre_siigo": nombre.strip(),
                "stock_actual": stock_actual,
            }
        )

    # Crear DataFrame vacío con las columnas correctas si no hay datos
    if len(datos) == 0:
        return pd.DataFrame(
            columns=["referencia_siigo", "nombre_siigo", "stock_actual"]
        )

    return pd.DataFrame(datos)


def cruzar_inventarios(df_excel: pd.DataFrame, df_siigo: pd.DataFrame) -> pd.DataFrame:
    """
    Cruza los datos del Excel con los de Siigo y determina estado.

    Args:
        df_excel: DataFrame del Excel
        df_siigo: DataFrame de Siigo

    Returns:
        pd.DataFrame: DataFrame con el cruce y estado
    """
    # Realizar merge por referencia
    df_cruzado = df_excel.merge(
        df_siigo, left_on="referencia", right_on="referencia_siigo", how="left"
    )

    # Marcar productos no encontrados en Siigo
    df_cruzado["encontrado_en_siigo"] = df_cruzado["referencia_siigo"].notna()
    df_cruzado["stock_actual"] = df_cruzado["stock_actual"].fillna(0)

    # Calcular diferencia
    df_cruzado["diferencia"] = (
        df_cruzado["stock_actual"] - df_cruzado["inventario_minimo"]
    )

    # Determinar estado
    def determinar_estado(row):
        if not row["encontrado_en_siigo"]:
            return "⚠️ No encontrado en Siigo"
        elif row["stock_actual"] < row["inventario_minimo"]:
            return "🔴 Crítico"
        elif row["stock_actual"] <= row["inventario_minimo"] * 1.2:
            return "🟡 Bajo"
        else:
            return "🟢 OK"

    df_cruzado["estado"] = df_cruzado.apply(determinar_estado, axis=1)

    # Seleccionar y ordenar columnas finales
    columnas_finales = [
        "referencia",
        "nombre",
        "inventario_minimo",
        "stock_actual",
        "diferencia",
        "estado",
    ]

    df_resultado = df_cruzado[columnas_finales].copy()
    df_resultado.columns = [
        "Referencia",
        "Nombre",
        "Mínimo (g)",
        "Stock Actual",
        "Diferencia",
        "Estado",
    ]

    return df_resultado


# ============================================================================
# FUNCIONES DE EXPORTACIÓN E IMPRESIÓN
# ============================================================================


def generar_html_impresion(df: pd.DataFrame, titulo: str = "Lista de Faltantes") -> str:
    """
    Genera HTML formateado para impresión.

    Args:
        df: DataFrame con los datos a imprimir
        titulo: Título del reporte

    Returns:
        str: HTML formateado
    """
    fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")

    # Generar filas de la tabla
    filas_html = ""
    for _, row in df.iterrows():
        estado_class = ""
        if "Crítico" in str(row["Estado"]):
            estado_class = "background-color: #ffcccc;"
        elif "Bajo" in str(row["Estado"]):
            estado_class = "background-color: #fff3cd;"

        filas_html += f"""
        <tr style="{estado_class}">
            <td>{row['Referencia']}</td>
            <td>{row['Nombre']}</td>
            <td style="text-align: right;">{row['Mínimo (g)']:,.0f}</td>
            <td style="text-align: right;">{row['Stock Actual']:,.0f}</td>
            <td style="text-align: right;">{row['Diferencia']:,.0f}</td>
            <td>{row['Estado']}</td>
        </tr>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{titulo}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                font-size: 12px;
            }}
            h1 {{
                color: #1E88E5;
                text-align: center;
                margin-bottom: 5px;
            }}
            .fecha {{
                text-align: center;
                color: #666;
                margin-bottom: 20px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}
            th {{
                background-color: #1E88E5;
                color: white;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            .footer {{
                margin-top: 20px;
                text-align: center;
                color: #666;
                font-size: 10px;
            }}
            @media print {{
                body {{ margin: 0; }}
                .no-print {{ display: none; }}
            }}
        </style>
    </head>
    <body>
        <h1>📦 {titulo}</h1>
        <p class="fecha">Generado el: {fecha_actual}</p>
        
        <table>
            <thead>
                <tr>
                    <th>Referencia</th>
                    <th>Nombre</th>
                    <th>Mínimo (g)</th>
                    <th>Stock Actual</th>
                    <th>Diferencia</th>
                    <th>Estado</th>
                </tr>
            </thead>
            <tbody>
                {filas_html}
            </tbody>
        </table>
        
        <div class="footer">
            <p>Colsabor - Sistema de Monitor de Inventario</p>
            <p>Total de productos listados: {len(df)}</p>
        </div>
        
        <script>
            // Auto-abrir diálogo de impresión
            window.onload = function() {{
                window.print();
            }}
        </script>
    </body>
    </html>
    """

    return html


def generar_excel_descarga(df: pd.DataFrame) -> bytes:
    """
    Genera archivo Excel para descarga.

    Args:
        df: DataFrame con los datos

    Returns:
        bytes: Contenido del archivo Excel
    """
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Faltantes")
    output.seek(0)
    return output.getvalue()


# ============================================================================
# INTERFAZ PRINCIPAL
# ============================================================================


# ============================================================================
# INTERFAZ PRINCIPAL
# ============================================================================


def main():
    """Función principal de la aplicación."""

    # Header moderno
    st.markdown(
        """
        <div class='header-title'>
            <h1 style='margin:0; font-size: 2.5em;'>📦 Monitor de Inventario</h1>
            <p style='margin:5px 0 0 0; font-size: 1.1em; opacity: 0.9;'>Colsabor - Control de Stock Inteligente</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Autenticación (solo si no está autenticado)
    if "token_siigo" not in st.session_state:
        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.markdown(
                """
                <div class='login-box'>
                    <h3 style='margin-top:0; color: #1976D2;'>🔐 Iniciar Sesión</h3>
                    <p style='color: #666; margin-bottom: 20px;'>Ingresa tu usuario de Siigo</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            usuario_email = st.text_input(
                "📧 Usuario de Siigo",
                placeholder="tu.usuario@colsabor.com.co",
                key="email_input",
                help="Tu correo de usuario registrado en Siigo",
            )

            st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                if st.button(
                    "🚀 Conectar a Siigo", use_container_width=True, type="primary"
                ):
                    if usuario_email:
                        with st.spinner("🔄 Autenticando con Siigo..."):
                            # Usar el email del usuario + Access Key compartido de la empresa
                            resultado = autenticar_siigo(
                                usuario_email, SIIGO_ACCESS_KEY
                            )
                            if resultado["success"]:
                                st.session_state["token_siigo"] = resultado["token"]
                                st.session_state["usuario_email"] = usuario_email
                                st.success("✅ Autenticación exitosa")
                                st.balloons()
                                st.rerun()
                            else:
                                st.error(
                                    "❌ Error de autenticación. Verifica tu usuario."
                                )
                                with st.expander("Ver detalles del error"):
                                    st.code(resultado.get("error", "Error desconocido"))
                    else:
                        st.warning("⚠️ Por favor ingresa tu usuario")

            st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

            st.info("💡 **Usa tu correo registrado en Siigo**")

        st.stop()

    # Usuario autenticado - mostrar barra superior con actualización automática
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown(
            f"👤 **Usuario:** {st.session_state.get('usuario_email', 'Usuario')}"
        )
    with col2:
        # Botón de actualizar manualmente
        if st.button(
            "🔄 Actualizar", use_container_width=True, help="Actualizar datos de Siigo"
        ):
            if (
                "ultimo_excel" in st.session_state
                and st.session_state["ultimo_excel"] is not None
            ):
                st.session_state["forzar_actualizacion"] = True
                st.rerun()
    with col3:
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            # Limpiar toda la sesión
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    st.markdown("---")

    # Área de carga de archivo
    st.markdown("### 📤 Cargar Inventario Mínimo")

    # Intentar cargar inventario guardado del usuario
    usuario_email = st.session_state.get("usuario_email", "")
    inventario_guardado = None

    if usuario_email:
        with st.spinner("🔍 Buscando inventario guardado..."):
            inventario_guardado = cargar_inventario_guardado(usuario_email)

    col1, col2 = st.columns([3, 1])

    with col1:
        # Mostrar si hay inventario guardado
        if inventario_guardado is not None:
            st.success(
                f"✅ Inventario guardado encontrado: **{len(inventario_guardado)} productos**"
            )
            usar_guardado = st.checkbox(
                "📁 Usar inventario guardado",
                value=True,
                help="Desmarca para subir un nuevo archivo",
            )

            if usar_guardado:
                archivo_excel = None
                st.session_state["df_excel_cache"] = inventario_guardado
                st.session_state["usando_guardado"] = True
            else:
                st.session_state["usando_guardado"] = False

        # Si no usa guardado o no hay guardado, mostrar uploader
        if inventario_guardado is None or not st.session_state.get(
            "usando_guardado", False
        ):
            archivo_excel = st.file_uploader(
                "Sube tu archivo Excel con el inventario mínimo",
                type=["xlsx", "xls"],
                help="El archivo debe contener: Referencia, Nombre, Inventario Mínimo por gramos",
                label_visibility="collapsed",
            )

            # Guardar el archivo en la sesión
            if archivo_excel is not None:
                st.session_state["ultimo_excel"] = archivo_excel
            elif "ultimo_excel" in st.session_state:
                archivo_excel = st.session_state["ultimo_excel"]

    with col2:
        with st.expander("📋 Formato requerido"):
            st.markdown(
                """
            **Columnas necesarias:**
            - Referencia
            - Nombre  
            - Inventario Mínimo
            """
            )

    # Procesar si hay archivo cargado o inventario guardado
    if archivo_excel or st.session_state.get("usando_guardado", False):
        try:
            # Cargar Excel solo si es nuevo o se forzó actualización
            if "df_excel_cache" not in st.session_state or (
                "forzar_actualizacion" in st.session_state and archivo_excel
            ):
                if archivo_excel:
                    with st.spinner("📂 Cargando archivo Excel..."):
                        df_excel = cargar_excel(archivo_excel)
                        st.session_state["df_excel_cache"] = df_excel
                    st.success(
                        f"✅ Excel cargado: **{len(df_excel)} productos** encontrados"
                    )

                    # Guardar en Google Sheets automáticamente
                    with st.spinner("💾 Guardando en la nube..."):
                        if guardar_inventario_excel(usuario_email, df_excel):
                            st.success("✅ Inventario guardado en Google Sheets")
                else:
                    df_excel = st.session_state["df_excel_cache"]
            else:
                df_excel = st.session_state["df_excel_cache"]
                if not st.session_state.get("usando_guardado", False):
                    st.info(f"📋 Usando Excel en sesión: **{len(df_excel)} productos**")

            # Obtener datos de Siigo (intentar cargar guardados primero)
            if (
                "df_siigo_cache" not in st.session_state
                or "forzar_actualizacion" in st.session_state
            ):
                # Intentar cargar datos guardados en Google Sheets
                datos_guardados = None
                if "forzar_actualizacion" not in st.session_state:
                    with st.spinner("🔍 Buscando datos de Siigo guardados..."):
                        datos_guardados = cargar_productos_siigo_guardados()
                
                if datos_guardados is not None:
                    # Usar datos guardados
                    df_siigo, _, ultima_actualizacion = datos_guardados
                    productos_siigo = []  # No tenemos los productos raw guardados
                    total_obtenidos = len(df_siigo)
                    
                    st.session_state["df_siigo_cache"] = df_siigo
                    st.session_state["productos_siigo_cache"] = productos_siigo
                    st.session_state["total_obtenidos"] = total_obtenidos
                    st.session_state["ultima_actualizacion"] = ultima_actualizacion
                    
                    st.success(f"✅ **{total_obtenidos} productos** cargados desde la nube")
                    st.info(f"⏰ Última actualización: {ultima_actualizacion.strftime('%d/%m/%Y %H:%M:%S')}")
                else:
                    # Obtener datos frescos de Siigo
                    st.info("🔄 Obteniendo productos de Siigo...")

                    with st.spinner("Descargando productos de Siigo con paginación..."):
                        resultado = obtener_todos_los_productos_siigo(
                            st.session_state["token_siigo"]
                        )

                    if not resultado["success"]:
                        st.error(resultado["error"])
                        st.stop()

                    productos_siigo = resultado["data"]
                    total_obtenidos = resultado.get("total", len(productos_siigo))

                    with st.spinner("⚙️ Procesando productos..."):
                        df_siigo = procesar_productos_siigo(productos_siigo)

                    # Guardar en cache de sesión
                    st.session_state["df_siigo_cache"] = df_siigo
                    st.session_state["productos_siigo_cache"] = productos_siigo
                    st.session_state["total_obtenidos"] = total_obtenidos
                    st.session_state["ultima_actualizacion"] = datetime.now()

                    st.success(f"✅ **{total_obtenidos} productos** obtenidos de Siigo")
                    st.success(f"✅ **{len(df_siigo)} productos** procesados correctamente")
                    
                    # Guardar en Google Sheets para próximas sesiones
                    with st.spinner("💾 Guardando en la nube..."):
                        if guardar_productos_siigo(productos_siigo):
                            st.success("✅ Datos guardados en Google Sheets")

                # Limpiar flag de actualización
                if "forzar_actualizacion" in st.session_state:
                    del st.session_state["forzar_actualizacion"]
            else:
                # Usar datos en cache de sesión
                df_siigo = st.session_state["df_siigo_cache"]
                productos_siigo = st.session_state.get("productos_siigo_cache", [])
                total_obtenidos = st.session_state.get(
                    "total_obtenidos", len(df_siigo)
                )
                st.info(
                    f"📊 Usando datos en memoria: **{len(df_siigo)} productos**"
                )

            # Mostrar última actualización
            from datetime import datetime

            if "ultima_actualizacion" not in st.session_state:
                st.session_state["ultima_actualizacion"] = datetime.now()

            col_update1, col_update2 = st.columns([3, 1])
            with col_update1:
                st.caption(
                    f"⏰ Última actualización: {st.session_state['ultima_actualizacion'].strftime('%d/%m/%Y %H:%M:%S')}"
                )

            # Actualizar timestamp
            st.session_state["ultima_actualizacion"] = datetime.now()

            # Debug: Mostrar información de productos obtenidos
            with st.expander("🔍 Ver detalles técnicos"):
                st.write(f"Total productos obtenidos de API: {total_obtenidos}")
                st.write(f"Total productos procesados válidos: {len(df_siigo)}")
                if len(productos_siigo) > 0:
                    st.write("Ejemplo del primer producto:")
                    st.json(productos_siigo[0])
                    st.write("Productos procesados (primeros 20):")
                    st.dataframe(df_siigo.head(20))
                else:
                    st.warning("No se obtuvieron productos de Siigo")

            # Cruzar inventarios
            with st.spinner("Procesando inventarios..."):
                df_resultado = cruzar_inventarios(df_excel, df_siigo)

            st.markdown("---")

            # Métricas resumen con diseño moderno
            st.markdown("### 📊 Resumen del Inventario")

            col1, col2, col3, col4 = st.columns(4)

            total = len(df_resultado)
            criticos = len(df_resultado[df_resultado["Estado"].str.contains("Crítico")])
            bajos = len(df_resultado[df_resultado["Estado"].str.contains("Bajo")])
            ok = len(df_resultado[df_resultado["Estado"].str.contains("OK")])
            no_encontrados = len(
                df_resultado[df_resultado["Estado"].str.contains("No encontrado")]
            )

            with col1:
                st.metric("📦 Total", total, help="Total de productos analizados")
            with col2:
                st.metric(
                    "🔴 Críticos",
                    criticos,
                    delta=f"-{criticos}" if criticos > 0 else "0",
                    delta_color="inverse",
                    help="Productos por debajo del inventario mínimo",
                )
            with col3:
                st.metric("🟡 Bajos", bajos, help="Productos con stock bajo")
            with col4:
                st.metric("🟢 OK", ok, help="Productos con stock suficiente")

            if no_encontrados > 0:
                st.warning(
                    f"⚠️ **{no_encontrados} producto(s)** no encontrado(s) en Siigo"
                )

                # Mostrar lista de productos no encontrados
                with st.expander("📋 Ver productos no encontrados en Siigo"):
                    df_no_encontrados = df_resultado[
                        df_resultado["Estado"].str.contains("No encontrado")
                    ][["Referencia", "Nombre", "Mínimo (g)"]].copy()

                    st.dataframe(
                        df_no_encontrados, use_container_width=True, hide_index=True
                    )

                    st.info(
                        "💡 Verifica que estas referencias existan en Siigo o actualiza el Excel"
                    )

            st.markdown("---")

            # Filtros con diseño mejorado
            st.markdown("### 🔍 Filtrar y Buscar")

            col1, col2 = st.columns(2)

            with col1:
                filtro_estado = st.multiselect(
                    "Estado del producto",
                    options=[
                        "🔴 Crítico",
                        "🟡 Bajo",
                        "🟢 OK",
                        "⚠️ No encontrado en Siigo",
                    ],
                    default=["🔴 Crítico", "🟡 Bajo"],
                )

            with col2:
                buscar = st.text_input(
                    "🔎 Buscar", placeholder="Nombre o referencia..."
                )

            # Aplicar filtros
            df_filtrado = df_resultado.copy()

            if filtro_estado:
                mask = df_filtrado["Estado"].apply(
                    lambda x: any(estado in x for estado in filtro_estado)
                )
                df_filtrado = df_filtrado[mask]

            if buscar:
                mask = df_filtrado["Referencia"].str.contains(
                    buscar, case=False, na=False
                ) | df_filtrado["Nombre"].str.contains(buscar, case=False, na=False)
                df_filtrado = df_filtrado[mask]

            # Mostrar tabla con diseño mejorado
            st.markdown(f"### 📋 Resultados: **{len(df_filtrado)}** productos")

            # Colorear DataFrame
            def colorear_estado(val):
                if "Crítico" in str(val):
                    return "background-color: #ffcdd2"
                elif "Bajo" in str(val):
                    return "background-color: #fff9c4"
                elif "OK" in str(val):
                    return "background-color: #c8e6c9"
                elif "No encontrado" in str(val):
                    return "background-color: #ffccbc"
                return ""

            df_styled = df_filtrado.style.applymap(
                colorear_estado, subset=["Estado"]
            ).format(
                {
                    "Mínimo (g)": "{:,.0f}",
                    "Stock Actual": "{:,.0f}",
                    "Diferencia": "{:,.0f}",
                }
            )

            st.dataframe(df_styled, use_container_width=True, height=450)

            st.markdown("---")

            # Botones de exportación con diseño moderno
            st.markdown("### 📥 Exportar Reportes")

            col1, col2, col3 = st.columns(3)

            # Solo productos críticos y bajos para impresión
            df_faltantes = df_resultado[
                df_resultado["Estado"].str.contains("Crítico|Bajo", regex=True)
            ].copy()

            with col1:
                # Botón para generar HTML de impresión
                if st.button("🖨️ Imprimir Lista de Faltantes", use_container_width=True):
                    if len(df_faltantes) > 0:
                        html_content = generar_html_impresion(
                            df_faltantes, "Lista de Productos Faltantes - Colsabor"
                        )

                        # Codificar en base64 para abrir en nueva pestaña
                        b64 = base64.b64encode(html_content.encode()).decode()
                        href = f'<a href="data:text/html;base64,{b64}" target="_blank" style="text-decoration: none;"><button style="background-color: #1E88E5; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; width: 100%;">📄 Abrir Vista de Impresión</button></a>'
                        st.markdown(href, unsafe_allow_html=True)
                        st.info(
                            "💡 Se abrirá una nueva pestaña. Usa Ctrl+P para imprimir."
                        )
                    else:
                        st.info("No hay productos faltantes para imprimir")

            with col2:
                # Descargar Excel
                if len(df_faltantes) > 0:
                    excel_data = generar_excel_descarga(df_faltantes)
                    st.download_button(
                        label="📥 Descargar Excel Faltantes",
                        data=excel_data,
                        file_name=f"faltantes_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                    )

            with col3:
                # Descargar Excel completo
                excel_completo = generar_excel_descarga(df_resultado)
                st.download_button(
                    label="📥 Descargar Excel Completo",
                    data=excel_completo,
                    file_name=f"inventario_completo_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )

            # Vista previa
            with st.expander("👁️ Vista previa de faltantes"):
                if len(df_faltantes) > 0:
                    st.dataframe(
                        df_faltantes, use_container_width=True, hide_index=True
                    )
                else:
                    st.success(
                        "🎉 ¡Excelente! No hay productos con stock crítico o bajo."
                    )

        except ValueError as e:
            st.error(f"❌ {str(e)}")
        except Exception as e:
            st.error(f"❌ Error inesperado: {str(e)}")
            with st.expander("Ver detalles del error"):
                st.exception(e)

    else:
        # Pantalla de bienvenida cuando no hay archivo
        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            st.info(
                "👆 **Sube un archivo Excel** para comenzar el análisis de inventario"
            )

        with st.expander("📝 Ver ejemplo de formato Excel"):
            st.markdown("**Formato requerido del archivo:**")
            ejemplo_df = pd.DataFrame(
                {
                    "Referencia": ["REF001", "REF002", "REF003", "REF004", "REF005"],
                    "Nombre": [
                        "Harina de Trigo 1kg",
                        "Azúcar Refinada 1kg",
                        "Sal Marina 500g",
                        "Aceite Vegetal 1L",
                        "Mantequilla 250g",
                    ],
                    "Inventario Mínimo por gramos": [500, 300, 200, 400, 100],
                }
            )
            st.dataframe(ejemplo_df, use_container_width=True, hide_index=True)

            # Descargar plantilla
            plantilla_excel = generar_excel_descarga(ejemplo_df)
            st.download_button(
                label="⬇️ Descargar Plantilla Excel",
                data=plantilla_excel,
                file_name="plantilla_inventario_minimo.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

    # Footer moderno
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; padding: 20px;'>
            <p style='color: #1976D2; font-weight: 600; margin: 5px;'>Monitor de Inventario Colsabor</p>
            <p style='color: #999; font-size: 12px; margin: 5px;'>Sistema inteligente de control de stock © 2026</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
