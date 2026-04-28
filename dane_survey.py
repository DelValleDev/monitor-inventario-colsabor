"""
Módulo de Encuesta DANE – DIAN Automator Middleware
Procesa los CSVs de ventas e inventario, los clasifica en categorías DIAN
y presenta la tabla lista para revisar y aprobar.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN DE CATEGORÍAS DIAN
# Orden importa: la primera regla que coincida gana.
# ─────────────────────────────────────────────────────────────────────────────
DIAN_CATEGORIES: list[dict] = [
    {
        "codigo": "3541002",
        "nombre": "Esencias",
        "descripcion": "Todo lo que diga ESENCIA o JARABE",
        "keywords": ["ESENCIA", "JARABE"],
        "color": "#6366f1",
    },
    {
        "codigo": "2399907",
        "nombre": "Concentrados para bebidas",
        "descripcion": "Todo lo que diga SABOR CONCENTRADO o CONCENTRADO",
        "keywords": ["CONCENTRADO"],
        "color": "#0891b2",
    },
    {
        "codigo": "3432004",
        "nombre": "Colorantes para alimentos",
        "descripcion": "Todo lo que diga COLOR/COLORANTE o nombres específicos de colorantes",
        "keywords": [
            "COLOR", "COLORANTE",
            # Nombres químicos de colorantes – evitan depender del typo "COLOR"
            "TARTRAZINA", "CARMOISINA", "ERYTROSINA", "ERITROSINA",
            "SUNSET", "PUNZO", "ROJO N ", "AZUL BTE", "AZUL 1 ",
        ],
        "color": "#dc2626",
    },
    {
        "codigo": "2399921",
        "nombre": "Productos aromáticos diversos",
        "descripcion": "Todo lo que diga AROMA",
        "keywords": ["AROMA"],
        "color": "#7c3aed",
    },
    {
        "codigo": "2399913",
        "nombre": "Premezclas",
        "descripcion": "Todo lo que diga MEJORADOR o LUXURY (incluye variante LUXURI)",
        "keywords": ["MEJORADOR", "LUXURY", "LUXURI"],
        "color": "#b45309",
    },
    {
        "codigo": "2399597",
        "nombre": "Condimentos y aliños",
        "descripcion": "Condimento, ESTANDAR, STAND, TRIX, GRITZ o para snacks",
        "keywords": [
            "CONDIMENTO", "ALIÑO",
            "ESTANDAR", "ESTÁNDAR", "STANDAR",
            "STAND", "TRIX", "GRITZ", "GRITS", "SNACK",
        ],
        "color": "#059669",
    },
    {
        "codigo": "2399603",
        "nombre": "Polvo para hornear",
        "descripcion": "Todo lo que diga HORNEAR",
        "keywords": ["HORNEAR"],
        "color": "#d97706",
    },
    {
        "codigo": "2352005",
        "nombre": "AZUCAR (SACARIN, SUCRALOSA, stevia)",
        "descripcion": "Azúcar, Sacarina, Sucralosa, Stevia",
        "keywords": ["AZUCAR", "AZÚCAR", "SACARIN", "SACARINA", "SUCRALOSA", "STEVIA"],
        "color": "#db2777",
    },
    {
        "codigo": "2149402",
        "nombre": "Rellenos y GLASEADOS",
        "descripcion": "Todo lo que diga RELLENO o GLASEADO",
        "keywords": ["RELLENO", "GLASEAD", "GLASEADO"],
        "color": "#64748b",
    },
]

_CODE_TO_CAT: dict[str, dict] = {c["codigo"]: c for c in DIAN_CATEGORIES}

# ─────────────────────────────────────────────────────────────────────────────
# MIDDLEWARE DE CLASIFICACIÓN
# ─────────────────────────────────────────────────────────────────────────────


def classify_product(name: str) -> tuple[str | None, str]:
    """Retorna (codigo_dian, nombre_categoria) o (None, 'Sin clasificar')."""
    name_up = str(name).upper().strip()
    for cat in DIAN_CATEGORIES:
        for kw in cat["keywords"]:
            if kw in name_up:
                return cat["codigo"], cat["nombre"]
    return None, "Sin clasificar"


# ─────────────────────────────────────────────────────────────────────────────
# LOCALIZACIÓN DE ARCHIVOS CSV
# ─────────────────────────────────────────────────────────────────────────────


def _find_csv_files() -> tuple[Path | None, Path | None]:
    """Busca los archivos CSV en rutas candidatas (raíz del proyecto)."""
    roots = [
        Path(__file__).resolve().parents[1],  # raíz esperada del proyecto
        Path(__file__).resolve().parent,      # inventory_monitor/
        Path.cwd(),                           # cwd de streamlit run
        Path.cwd().parent,                    # si streamlit corre dentro de inventory_monitor/
    ]
    # Deduplicar rutas manteniendo orden
    candidates = list(dict.fromkeys(r.resolve() for r in roots if r.exists()))
    ventas_path: Path | None = None
    saldos_path: Path | None = None

    # 1) Intento por nombre exacto (más estable)
    exact_ventas = "Ventas por producto 2025 Colsabor - Sheet1.csv"
    exact_saldos = "Saldos de productos - 31-12-25.xlsx - Sheet1.csv"
    for base in candidates:
        v = base / exact_ventas
        s = base / exact_saldos
        if ventas_path is None and v.exists():
            ventas_path = v
        if saldos_path is None and s.exists():
            saldos_path = s
        if ventas_path and saldos_path:
            return ventas_path, saldos_path

    # 2) Intento por patrones
    for base in candidates:
        if ventas_path is None:
            hits = list(base.glob("Ventas*Colsabor*.csv"))
            if hits:
                ventas_path = hits[0]
        if saldos_path is None:
            hits = list(base.glob("Saldos*31-12*.csv"))
            if hits:
                saldos_path = hits[0]
        if ventas_path and saldos_path:
            break

    # 3) Último intento recursivo en primer nivel de cada carpeta candidata
    if ventas_path is None or saldos_path is None:
        for base in candidates:
            if ventas_path is None:
                hits = list(base.rglob("Ventas*Colsabor*.csv"))
                if hits:
                    ventas_path = hits[0]
            if saldos_path is None:
                hits = list(base.rglob("Saldos*31-12*.csv"))
                if hits:
                    saldos_path = hits[0]
            if ventas_path and saldos_path:
                break

    return ventas_path, saldos_path


# ─────────────────────────────────────────────────────────────────────────────
# PARSERS DE CSV
# ─────────────────────────────────────────────────────────────────────────────


def _clean_number(val: str | float) -> float:
    """Convierte strings con comas de miles a float."""
    if isinstance(val, (int, float)):
        return float(val)
    cleaned = re.sub(r"[,\s]", "", str(val).strip())
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


@st.cache_data(show_spinner=False)
def cargar_ventas(filepath: str) -> pd.DataFrame:
    """
    Carga el CSV de ventas.
    Estructura: 7 filas de cabecera metadata, fila 8 = columnas.
    """
    try:
        df = pd.read_csv(
            filepath,
            skiprows=7,
            header=0,
            encoding="utf-8",
            dtype=str,
            on_bad_lines="skip",
        )
        if df.shape[1] < 8:
            st.error("El archivo de ventas no tiene el formato esperado.")
            return pd.DataFrame()

        df.columns = [
            "codigo", "nombre", "ref_fabrica", "grupo",
            "cant_vendida", "valor_bruto", "descuento", "subtotal",
            "imp_cargo", "imp_retencion", "total",
        ] + [f"_extra_{i}" for i in range(df.shape[1] - 11)]

        # Limpiar: solo filas con código y grupo de inventario válidos
        grupos_validos = {"MATERIAS PRIMAS", "PRODUCTO TERMINADO", "MERCANCIAS"}
        df["grupo"] = df["grupo"].astype(str).str.strip().str.upper()
        df = df[df["grupo"].isin(grupos_validos)].copy()

        df["codigo"] = df["codigo"].astype(str).str.strip()
        df["nombre"] = df["nombre"].astype(str).str.strip()
        df["cant_vendida"] = df["cant_vendida"].apply(_clean_number)
        df["subtotal"] = df["subtotal"].apply(_clean_number)

        df = df[df["codigo"] != ""].reset_index(drop=True)
        return df

    except Exception as exc:
        st.error(f"Error cargando archivo de ventas: {exc}")
        return pd.DataFrame()


@st.cache_data(show_spinner=False)
def cargar_saldos(filepath: str) -> pd.DataFrame:
    """
    Carga el CSV de saldos al 31-dic.
    Formato complejo: filas 'Producto:' y 'Bodega:' intercaladas con datos reales.
    Se filtran y agrupa por código (suma de todas las bodegas).
    """
    try:
        df_raw = pd.read_csv(
            filepath,
            skiprows=7,
            header=0,
            encoding="utf-8",
            dtype=str,
            on_bad_lines="skip",
        )
        if df_raw.shape[1] < 4:
            st.error("El archivo de saldos no tiene el formato esperado.")
            return pd.DataFrame()

        # Normalizar nombres de columnas
        df_raw.columns = ["codigo", "nombre", "referencia", "saldo"] + [
            f"_extra_{i}" for i in range(df_raw.shape[1] - 4)
        ]

        cod_col = df_raw["codigo"].astype(str).str.strip()

        # Conservar solo filas de datos reales (excluir encabezados de grupo).
        # Cada condición va entre paréntesis para que & no absorba el >.
        mask = (
            (cod_col.str.len() > 0)
            & ~cod_col.str.startswith("Producto:")
            & ~cod_col.str.startswith("Bodega:")
            & ~cod_col.str.upper().str.startswith("TOTAL")
            & ~cod_col.str.upper().str.startswith("CODIGO")
            & cod_col.notna()
        )
        df = df_raw[mask].copy()

        df["codigo"] = df["codigo"].astype(str).str.strip()
        df["nombre"] = df["nombre"].astype(str).str.strip()
        df["saldo"] = df["saldo"].apply(_clean_number)

        # Sumar por código (múltiples bodegas)
        df_grp = (
            df.groupby(["codigo", "nombre"], as_index=False)["saldo"]
            .sum()
        )

        return df_grp

    except Exception as exc:
        st.error(f"Error cargando archivo de saldos: {exc}")
        return pd.DataFrame()


# ─────────────────────────────────────────────────────────────────────────────
# CÁLCULO DE LA TABLA DIAN
# ─────────────────────────────────────────────────────────────────────────────


def calcular_tabla_dian(
    df_ventas: pd.DataFrame,
    df_saldos: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Clasifica productos y agrega por categoría DIAN.

    Regla de negocio aplicada:
        Los productos con código que empieza con "10" son materias primas
        (MATERIAS PRIMAS en Siigo) y se excluyen del informe de encuesta.

    Retorna:
        df_dian     – tabla principal con 9 categorías DIAN
        df_v_detail – ventas detalladas con columna de clasificación
        df_s_detail – saldos detallados con columna de clasificación
    """
    # ── Excluir materias primas (códigos que empiezan con "10") ──────────
    if not df_ventas.empty:
        df_ventas = df_ventas[
            ~df_ventas["codigo"].astype(str).str.startswith("10")
        ].copy()
    if not df_saldos.empty:
        df_saldos = df_saldos[
            ~df_saldos["codigo"].astype(str).str.startswith("10")
        ].copy()

    # ── Clasificar ventas ─────────────────────────────────────────────────
    df_v = df_ventas.copy()
    if not df_v.empty:
        clasificacion = df_v["nombre"].apply(
            lambda n: pd.Series(classify_product(n), index=["dian_codigo", "dian_nombre"])
        )
        df_v = pd.concat([df_v, clasificacion], axis=1)
    else:
        df_v["dian_codigo"] = pd.NA
        df_v["dian_nombre"] = "Sin clasificar"

    # ── Clasificar saldos ─────────────────────────────────────────────────
    df_s = df_saldos.copy()
    if not df_s.empty:
        clasificacion_s = df_s["nombre"].apply(
            lambda n: pd.Series(classify_product(n), index=["dian_codigo", "dian_nombre"])
        )
        df_s = pd.concat([df_s, clasificacion_s], axis=1)
    else:
        df_s["dian_codigo"] = pd.NA
        df_s["dian_nombre"] = "Sin clasificar"

    # ── Agregar ventas por categoría ──────────────────────────────────────
    ventas_agg = (
        df_v[df_v["dian_codigo"].notna()]
        .groupby(["dian_codigo", "dian_nombre"], as_index=False)
        .agg(cant_vendida=("cant_vendida", "sum"), valor_total=("subtotal", "sum"))
    )

    # ── Agregar saldos por categoría ──────────────────────────────────────
    saldos_agg = (
        df_s[df_s["dian_codigo"].notna()]
        .groupby(["dian_codigo", "dian_nombre"], as_index=False)
        .agg(saldo_31dic=("saldo", "sum"))
    )

    # ── Construir tabla DIAN con las 9 categorías ─────────────────────────
    rows = []
    for cat in DIAN_CATEGORIES:
        v = ventas_agg[ventas_agg["dian_codigo"] == cat["codigo"]]
        s = saldos_agg[saldos_agg["dian_codigo"] == cat["codigo"]]

        cant_vendida = float(v["cant_vendida"].sum()) if not v.empty else 0.0
        valor_total = float(v["valor_total"].sum()) if not v.empty else 0.0
        saldo_31dic = float(s["saldo_31dic"].sum()) if not s.empty else 0.0
        vu_venta = valor_total / cant_vendida if cant_vendida > 0 else 0.0

        rows.append(
            {
                "Código DIAN": cat["codigo"],
                "Producto": cat["nombre"],
                "Cant. producida": 0,
                "Valor Producción": 0,
                "Cant. vendida": cant_vendida,
                "V/U. de venta": vu_venta,
                "Valor vtas. tot.": valor_total,
                "Valor vtas. ext.": 0,
                "Cant. exis. 31 dic.": saldo_31dic,
            }
        )

    df_dian = pd.DataFrame(rows)
    return df_dian, df_v, df_s


# ─────────────────────────────────────────────────────────────────────────────
# INTERFAZ STREAMLIT
# ─────────────────────────────────────────────────────────────────────────────

_BADGE_COLORS: dict[str, str] = {
    "3541002": "#6366f1",
    "2399907": "#0891b2",
    "3432004": "#dc2626",
    "2399921": "#7c3aed",
    "2399913": "#b45309",
    "2399597": "#059669",
    "2399603": "#d97706",
    "2352005": "#db2777",
    "2149402": "#64748b",
}


def _badge(text: str, color: str = "#64748b") -> str:
    return (
        f'<span style="display:inline-block;padding:2px 8px;border-radius:999px;'
        f"font-size:10px;font-weight:700;letter-spacing:.05em;color:#fff;"
        f'background:{color}">{text}</span>'
    )


def render_dane_survey() -> None:
    """Renderiza la página de Encuesta DANE / Reporte de producción DIAN."""

    # ── Título de sección ─────────────────────────────────────────────────
    st.markdown(
        """
        <div style="margin-bottom:24px;">
          <div style="font-size:22px;font-weight:800;letter-spacing:-.04em;
                      color:var(--text-primary);line-height:1.2;">
            📊 Encuesta de Producción DANE
          </div>
          <div style="font-size:12px;color:var(--text-muted);margin-top:4px;
                      font-weight:500;letter-spacing:.02em;">
            Cálculo automático por categoría DIAN · Año 2025
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Buscar archivos CSV ───────────────────────────────────────────────
    ventas_path, saldos_path = _find_csv_files()

    files_ok = True
    if ventas_path is None:
        st.error("No se encontró el archivo de Ventas por producto 2025.")
        files_ok = False
    if saldos_path is None:
        st.error("No se encontró el archivo de Saldos al 31-dic.")
        files_ok = False

    if not files_ok:
        st.info(
            "Asegúrate de que los archivos estén en la raíz del proyecto:\n"
            "- `Ventas por producto 2025 Colsabor - Sheet1.csv`\n"
            "- `Saldos de productos - 31-12-25.xlsx - Sheet1.csv`"
        )
        st.caption(
            f"Ruta actual de ejecución: `{Path.cwd()}`"
        )
        return
    st.caption(
        f"Archivos cargados: `{ventas_path.name}` y `{saldos_path.name}`"
    )

    # ── Carga de datos ────────────────────────────────────────────────────
    with st.spinner("Cargando y clasificando productos…"):
        df_ventas = cargar_ventas(str(ventas_path))
        df_saldos = cargar_saldos(str(saldos_path))

    if df_ventas.empty and df_saldos.empty:
        st.warning("No se pudieron cargar los datos de ninguno de los dos archivos.")
        return

    df_dian, df_v_detail, df_s_detail = calcular_tabla_dian(df_ventas, df_saldos)

    # ── Métricas de clasificación ─────────────────────────────────────────
    total_v = len(df_v_detail)
    clasificados_v = int(df_v_detail["dian_codigo"].notna().sum())
    sin_v = total_v - clasificados_v

    total_s = len(df_s_detail)
    clasificados_s = int(df_s_detail["dian_codigo"].notna().sum())
    sin_s = total_s - clasificados_s

    st.markdown(
        f"""
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:24px;">
          <div class="cs-card cs-card-blue">
            <div class="cs-card-icon">🛒</div>
            <div class="cs-card-value">{total_v}</div>
            <div class="cs-card-label">SKUs en Ventas</div>
            <div class="cs-card-sub">Referencias activas 2025</div>
          </div>
          <div class="cs-card cs-card-green">
            <div class="cs-card-icon">✅</div>
            <div class="cs-card-value">{clasificados_v}</div>
            <div class="cs-card-label">Clasificados</div>
            <div class="cs-card-sub">Con código DIAN asignado</div>
          </div>
          <div class="cs-card cs-card-amber">
            <div class="cs-card-icon">⚠️</div>
            <div class="cs-card-value">{sin_v}</div>
            <div class="cs-card-label">Sin clasificar</div>
            <div class="cs-card-sub">Requieren revisión</div>
          </div>
          <div class="cs-card cs-card-red">
            <div class="cs-card-icon">📦</div>
            <div class="cs-card-value">{total_s}</div>
            <div class="cs-card-label">SKUs en Saldos</div>
            <div class="cs-card-sub">Con existencias al 31-dic</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Tabla principal DIAN ──────────────────────────────────────────────
    st.markdown(
        '<div class="cs-section">📋 Tabla DIAN – Encuesta de Producción</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="font-size:11px;color:var(--text-muted);margin-bottom:12px;">'
        '⚠️ <b>Cant. producida</b> y <b>Valor Producción</b> requieren datos de producción interna '
        '(no disponibles en los CSVs cargados). Las demás columnas se calcularon automáticamente.'
        "</div>",
        unsafe_allow_html=True,
    )

    # Formato visual de la tabla
    def _fmt_num(v: float) -> str:
        if v == 0:
            return "–"
        return f"{v:,.2f}"

    def _fmt_cop(v: float) -> str:
        if v == 0:
            return "–"
        return f"$ {v:,.0f}"

    df_display = df_dian.copy()
    df_display["Cant. producida"] = df_display["Cant. producida"].apply(_fmt_num)
    df_display["Valor Producción"] = df_display["Valor Producción"].apply(_fmt_cop)
    df_display["Cant. vendida"] = df_display["Cant. vendida"].apply(_fmt_num)
    df_display["V/U. de venta"] = df_display["V/U. de venta"].apply(_fmt_cop)
    df_display["Valor vtas. tot."] = df_display["Valor vtas. tot."].apply(_fmt_cop)
    df_display["Valor vtas. ext."] = df_display["Valor vtas. ext."].apply(_fmt_cop)
    df_display["Cant. exis. 31 dic."] = df_display["Cant. exis. 31 dic."].apply(_fmt_num)

    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        height=420,
        column_config={
            "Código DIAN": st.column_config.TextColumn("Cód. DIAN", width="small"),
            "Producto": st.column_config.TextColumn("Categoría DIAN", width="medium"),
            "Cant. producida": st.column_config.TextColumn("Cant. producida", width="small"),
            "Valor Producción": st.column_config.TextColumn("Valor Prod.", width="small"),
            "Cant. vendida": st.column_config.TextColumn("Cant. vendida", width="small"),
            "V/U. de venta": st.column_config.TextColumn("V/U venta", width="small"),
            "Valor vtas. tot.": st.column_config.TextColumn("Valor vtas. tot.", width="medium"),
            "Valor vtas. ext.": st.column_config.TextColumn("Vtas. ext.", width="small"),
            "Cant. exis. 31 dic.": st.column_config.TextColumn("Exis. 31 dic.", width="small"),
        },
    )

    # Exportar tabla DIAN
    csv_dian = df_dian.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Exportar tabla DIAN (CSV)",
        data=csv_dian,
        file_name="encuesta_dane_2025.csv",
        mime="text/csv",
    )

    # ── Desglose por categoría ────────────────────────────────────────────
    st.markdown(
        '<div class="cs-section">🔍 Desglose por categoría</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="font-size:11px;color:var(--text-muted);margin-bottom:10px;">'
        "Expande cada categoría para ver los productos que la componen."
        "</div>",
        unsafe_allow_html=True,
    )

    for cat in DIAN_CATEGORIES:
        cod = cat["codigo"]
        color = cat["color"]
        v_cat = df_v_detail[df_v_detail["dian_codigo"] == cod]
        s_cat = df_s_detail[df_s_detail["dian_codigo"] == cod]

        n_prod_v = len(v_cat)
        n_prod_s = len(s_cat)

        with st.expander(
            f"{cat['nombre']} · {cat['codigo']} — {n_prod_v} SKU(s) en ventas · {n_prod_s} SKU(s) en saldos"
        ):
            st.markdown(
                f'<span style="font-size:11px;color:var(--text-muted);">'
                f'Regla de clasificación: <i>{cat["descripcion"]}</i></span>',
                unsafe_allow_html=True,
            )
            tabs = st.tabs(["Ventas 2025", "Saldos 31-dic"])

            with tabs[0]:
                if v_cat.empty:
                    st.info("Sin ventas registradas en esta categoría.")
                else:
                    cols_v = ["codigo", "nombre", "grupo", "cant_vendida", "subtotal"]
                    df_v_show = v_cat[cols_v].copy()
                    df_v_show.columns = [
                        "Código", "Nombre", "Grupo", "Cant. vendida", "Subtotal ($)"
                    ]
                    df_v_show["Cant. vendida"] = df_v_show["Cant. vendida"].apply(
                        lambda x: f"{x:,.2f}"
                    )
                    df_v_show["Subtotal ($)"] = df_v_show["Subtotal ($)"].apply(
                        lambda x: f"$ {x:,.0f}"
                    )
                    st.dataframe(df_v_show, use_container_width=True, hide_index=True)

            with tabs[1]:
                if s_cat.empty:
                    st.info("Sin existencias al 31-dic en esta categoría.")
                else:
                    cols_s = ["codigo", "nombre", "saldo"]
                    df_s_show = s_cat[cols_s].copy()
                    df_s_show.columns = ["Código", "Nombre", "Saldo (uds.)"]
                    df_s_show["Saldo (uds.)"] = df_s_show["Saldo (uds.)"].apply(
                        lambda x: f"{x:,.2f}"
                    )
                    st.dataframe(df_s_show, use_container_width=True, hide_index=True)

    # ── Productos sin clasificar ──────────────────────────────────────────
    df_v_sin = df_v_detail[df_v_detail["dian_codigo"].isna()].copy()
    df_s_sin = df_s_detail[df_s_detail["dian_codigo"].isna()].copy()

    if not df_v_sin.empty or not df_s_sin.empty:
        st.markdown(
            '<div class="cs-section">⚠️ Productos sin clasificar</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div style="font-size:11px;color:var(--text-muted);margin-bottom:10px;">'
            "Estos productos no coincidieron con ninguna regla de clasificación. "
            "Revisa si necesitan agregarse a las categorías DIAN o si corresponden "
            "a materias primas que no reportan en la encuesta."
            "</div>",
            unsafe_allow_html=True,
        )

        sc1, sc2 = st.columns(2)

        with sc1:
            st.markdown(
                f"**Sin clasificar en Ventas** ({len(df_v_sin)} SKUs)",
                unsafe_allow_html=True,
            )
            if not df_v_sin.empty:
                cols_vs = ["codigo", "nombre", "grupo", "cant_vendida", "subtotal"]
                df_vs_show = df_v_sin[cols_vs].copy()
                df_vs_show.columns = ["Código", "Nombre", "Grupo", "Cant.", "Subtotal ($)"]
                df_vs_show["Cant."] = df_vs_show["Cant."].apply(lambda x: f"{x:,.2f}")
                df_vs_show["Subtotal ($)"] = df_vs_show["Subtotal ($)"].apply(
                    lambda x: f"$ {x:,.0f}"
                )
                st.dataframe(df_vs_show, use_container_width=True, hide_index=True)

        with sc2:
            st.markdown(
                f"**Sin clasificar en Saldos** ({len(df_s_sin)} SKUs)",
                unsafe_allow_html=True,
            )
            if not df_s_sin.empty:
                cols_ss = ["codigo", "nombre", "saldo"]
                df_ss_show = df_s_sin[cols_ss].copy()
                df_ss_show.columns = ["Código", "Nombre", "Saldo (uds.)"]
                df_ss_show["Saldo (uds.)"] = df_ss_show["Saldo (uds.)"].apply(
                    lambda x: f"{x:,.2f}"
                )
                st.dataframe(df_ss_show, use_container_width=True, hide_index=True)

    # ── Nota de producción ─────────────────────────────────────────────────
    st.markdown(
        """
        <div style="margin-top:24px;padding:14px 18px;border-radius:14px;
                    background:var(--amber-bg);border:1px solid var(--amber-border);">
          <div style="font-size:12px;font-weight:700;color:var(--amber);margin-bottom:6px;">
            ℹ️ Datos pendientes de completar
          </div>
          <div style="font-size:11px;color:var(--text-secondary);line-height:1.7;">
            <b>Cant. producida</b> y <b>Valor Producción</b> no están disponibles en los CSVs
            de ventas e inventario. Para completar la encuesta, se requieren los reportes de
            producción interna (órdenes de fabricación o movimientos de producción de Siigo).
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
