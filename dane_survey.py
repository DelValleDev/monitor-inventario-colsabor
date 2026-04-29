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
    """Busca los archivos CSV en rutas candidatas (raíz del proyecto).

    Orden de búsqueda:
      1. data/ junto al módulo  → siempre funciona en Streamlit Cloud
      2. Directorio del módulo
      3. Parents del módulo (entorno local de desarrollo)
      4. cwd y su padre (fallback)
    """
    module_dir = Path(__file__).resolve().parent
    roots = [
        module_dir / "data",              # data/ en el repo → prioridad máxima
        module_dir,                       # inventory_monitor/
        module_dir.parent,               # raíz del proyecto (entorno local)
        Path.cwd(),                      # cwd de streamlit run
        Path.cwd().parent,               # si streamlit corre dentro de inventory_monitor/
    ]
    # Deduplicar rutas manteniendo orden
    candidates = list(dict.fromkeys(r.resolve() for r in roots if r.exists()))
    ventas_path: Path | None = None
    saldos_path: Path | None = None

    # 1) Nombres cortos preferidos (facilita despliegue y adjuntos)
    short_ventas = "ventas2025.csv"
    short_saldos = "saldos31dic2025.csv"
    for base in candidates:
        v = base / short_ventas
        s = base / short_saldos
        if ventas_path is None and v.exists():
            ventas_path = v
        if saldos_path is None and s.exists():
            saldos_path = s
        if ventas_path and saldos_path:
            return ventas_path, saldos_path

    # 2) Nombres exactos exportados desde Siigo / Excel histórico
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

    # 3) Intento por patrones
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

    # 4) Último intento recursivo
    if ventas_path is None or saldos_path is None:
        for base in candidates:
            if ventas_path is None:
                for pattern in ("ventas2025.csv", "Ventas*Colsabor*.csv"):
                    hits = list(base.rglob(pattern))
                    if hits:
                        ventas_path = hits[0]
                        break
            if saldos_path is None:
                for pattern in ("saldos31dic2025.csv", "Saldos*31-12*.csv"):
                    hits = list(base.rglob(pattern))
                    if hits:
                        saldos_path = hits[0]
                        break
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


def _parse_ventas(src: "str | object") -> pd.DataFrame:
    """Parsea el CSV de ventas desde ruta (str) o file-like object."""
    df = pd.read_csv(
        src,
        skiprows=7,
        header=0,
        encoding="utf-8",
        dtype=str,
        on_bad_lines="skip",
    )
    if df.shape[1] < 8:
        return pd.DataFrame()

    df.columns = [
        "codigo", "nombre", "ref_fabrica", "grupo",
        "cant_vendida", "valor_bruto", "descuento", "subtotal",
        "imp_cargo", "imp_retencion", "total",
    ] + [f"_extra_{i}" for i in range(df.shape[1] - 11)]

    grupos_validos = {"MATERIAS PRIMAS", "PRODUCTO TERMINADO", "MERCANCIAS"}
    df["grupo"] = df["grupo"].astype(str).str.strip().str.upper()
    df = df[df["grupo"].isin(grupos_validos)].copy()

    df["codigo"] = df["codigo"].astype(str).str.strip()
    df["nombre"] = df["nombre"].astype(str).str.strip()
    df["cant_vendida"] = df["cant_vendida"].apply(_clean_number)
    df["subtotal"] = df["subtotal"].apply(_clean_number)
    return df[df["codigo"] != ""].reset_index(drop=True)


def _parse_saldos(src: "str | object") -> pd.DataFrame:
    """Parsea el CSV de saldos desde ruta (str) o file-like object."""
    df_raw = pd.read_csv(
        src,
        skiprows=7,
        header=0,
        encoding="utf-8",
        dtype=str,
        on_bad_lines="skip",
    )
    if df_raw.shape[1] < 4:
        return pd.DataFrame()

    df_raw.columns = ["codigo", "nombre", "referencia", "saldo"] + [
        f"_extra_{i}" for i in range(df_raw.shape[1] - 4)
    ]

    cod_col = df_raw["codigo"].astype(str).str.strip()
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
    return df.groupby(["codigo", "nombre"], as_index=False)["saldo"].sum()


@st.cache_data(show_spinner=False)
def cargar_ventas(filepath: str) -> pd.DataFrame:
    """
    Carga el CSV de ventas desde ruta en disco (cacheado).
    Estructura: 7 filas de cabecera metadata, fila 8 = columnas.
    """
    try:
        return _parse_ventas(filepath)
    except Exception as exc:
        st.error(f"Error cargando archivo de ventas: {exc}")
        return pd.DataFrame()


@st.cache_data(show_spinner=False)
def cargar_saldos(filepath: str) -> pd.DataFrame:
    """
    Carga el CSV de saldos al 31-dic desde ruta en disco (cacheado).
    Formato complejo: filas 'Producto:' y 'Bodega:' intercaladas con datos reales.
    Se filtran y agrupa por código (suma de todas las bodegas).
    """
    try:
        return _parse_saldos(filepath)
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

    # ── Panel de diagnóstico / carga de archivos ──────────────────────────
    logs: list[tuple[str, str]] = []   # (icon, mensaje)

    ventas_path, saldos_path = _find_csv_files()
    logs.append(("🔍", f"Ruta de ejecución: `{Path.cwd()}`"))

    uploaded_ventas = uploaded_saldos = None

    if ventas_path:
        logs.append(("✅", f"Ventas encontrado: `{ventas_path.name}`"))
    else:
        logs.append(("❌", "Ventas **no encontrado** en rutas candidatas"))

    if saldos_path:
        logs.append(("✅", f"Saldos encontrado: `{saldos_path.name}`"))
    else:
        logs.append(("❌", "Saldos **no encontrado** en rutas candidatas"))

    files_ok = ventas_path is not None and saldos_path is not None

    # Si algún CSV falta, mostrar cargador manual (útil en Streamlit Cloud)
    if not files_ok:
        with st.expander("📁 Diagnóstico y carga manual de archivos", expanded=True):
            _log_html = "".join(
                f"<div>{icon} {msg}</div>" for icon, msg in logs
            )
            st.markdown(
                f"""<div style="padding:10px 14px;border-radius:10px;
                background:rgba(0,0,0,0.30);border:1px solid rgba(99,102,241,0.25);
                font-family:'JetBrains Mono',monospace;font-size:11px;line-height:2;
                color:#cbd5e1;margin-bottom:14px;">{_log_html}</div>""",
                unsafe_allow_html=True,
            )
            st.info(
                "**En Streamlit Cloud** los archivos no están en disco. "
                "Súbelos aquí directamente:\n\n"
                "- `ventas2025.csv` (export de Ventas por producto)\n"
                "- `saldos31dic2025.csv` (export de Saldos al 31-dic)"
            )
            col_u1, col_u2 = st.columns(2)
            with col_u1:
                uploaded_ventas = st.file_uploader(
                    "📤 Ventas 2025 (CSV)",
                    type=["csv"],
                    key="upload_ventas_dane",
                )
            with col_u2:
                uploaded_saldos = st.file_uploader(
                    "📤 Saldos 31-dic (CSV)",
                    type=["csv"],
                    key="upload_saldos_dane",
                )

        if uploaded_ventas is None or uploaded_saldos is None:
            return
        # Usar buffers subidos
        logs.append(("📤", "Usando archivos subidos manualmente"))
        files_ok = True
    else:
        with st.expander("📊 Diagnóstico de archivos", expanded=False):
            _log_html = "".join(
                f"<div>{icon} {msg}</div>" for icon, msg in logs
            )
            st.markdown(
                f"""<div style="padding:10px 14px;border-radius:10px;
                background:rgba(0,0,0,0.20);border:1px solid rgba(99,102,241,0.18);
                font-family:'JetBrains Mono',monospace;font-size:11px;line-height:2;
                color:#cbd5e1;">{_log_html}</div>""",
                unsafe_allow_html=True,
            )

    # ── Carga de datos ────────────────────────────────────────────────────
    import io as _io
    with st.spinner("Cargando y clasificando productos…"):
        if uploaded_ventas is not None:
            try:
                df_ventas = _parse_ventas(
                    _io.StringIO(uploaded_ventas.getvalue().decode("utf-8", errors="replace"))
                )
                df_saldos = _parse_saldos(
                    _io.StringIO(uploaded_saldos.getvalue().decode("utf-8", errors="replace"))
                )
            except Exception as _exc:
                st.error(f"Error procesando archivos subidos: {_exc}")
                return
        else:
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

    # ── Tabla principal DIAN con totales ──────────────────────────────────
    st.markdown(
        '<div class="cs-section">📋 Tabla DIAN – Encuesta de Producción</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="font-size:11px;color:var(--text-muted);margin-bottom:12px;">'
        '⚠️ <b>Cant. producida</b> y <b>Valor Producción</b> requieren datos de producción interna '
        "(no disponibles en los CSVs cargados). Las demás columnas se calcularon automáticamente."
        "</div>",
        unsafe_allow_html=True,
    )

    def _fmt_num(v: float) -> str:
        return "–" if v == 0 else f"{v:,.2f}"

    def _fmt_cop(v: float) -> str:
        return "–" if v == 0 else f"$ {v:,.0f}"

    # Fila de TOTALES
    total_cant_v = df_dian["Cant. vendida"].sum()
    total_valor_v = df_dian["Valor vtas. tot."].sum()
    total_exis = df_dian["Cant. exis. 31 dic."].sum()
    vu_global = total_valor_v / total_cant_v if total_cant_v > 0 else 0.0

    totals_row = {
        "Código DIAN": "TOTAL",
        "Producto": "─── SUMA TODAS LAS CATEGORÍAS ───",
        "Cant. producida": _fmt_num(0),
        "Valor Producción": _fmt_cop(0),
        "Cant. vendida": _fmt_num(total_cant_v),
        "V/U. de venta": _fmt_cop(vu_global),
        "Valor vtas. tot.": _fmt_cop(total_valor_v),
        "Valor vtas. ext.": _fmt_cop(0),
        "Cant. exis. 31 dic.": _fmt_num(total_exis),
    }

    df_display = df_dian.copy()
    df_display["Cant. producida"] = df_display["Cant. producida"].apply(_fmt_num)
    df_display["Valor Producción"] = df_display["Valor Producción"].apply(_fmt_cop)
    df_display["Cant. vendida"] = df_display["Cant. vendida"].apply(_fmt_num)
    df_display["V/U. de venta"] = df_display["V/U. de venta"].apply(_fmt_cop)
    df_display["Valor vtas. tot."] = df_display["Valor vtas. tot."].apply(_fmt_cop)
    df_display["Valor vtas. ext."] = df_display["Valor vtas. ext."].apply(_fmt_cop)
    df_display["Cant. exis. 31 dic."] = df_display["Cant. exis. 31 dic."].apply(_fmt_num)

    import pandas as _pd
    df_display = _pd.concat(
        [df_display, _pd.DataFrame([totals_row])], ignore_index=True
    )

    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        height=430,
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

    # ── Desglose por categoría con totales + promedio ─────────────────────
    st.markdown(
        '<div class="cs-section">🔍 Desglose por categoría</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="font-size:11px;color:var(--text-muted);margin-bottom:10px;">'
        "Expande cada categoría para ver cómo aportaron sus productos al total "
        "y cómo se calculó el V/U promedio ponderado."
        "</div>",
        unsafe_allow_html=True,
    )

    for cat in DIAN_CATEGORIES:
        cod = cat["codigo"]
        color = cat["color"]
        v_cat = df_v_detail[df_v_detail["dian_codigo"] == cod]
        s_cat = df_s_detail[df_s_detail["dian_codigo"] == cod]

        # Totales de la categoría
        cat_cant = float(v_cat["cant_vendida"].sum()) if not v_cat.empty else 0.0
        cat_valor = float(v_cat["subtotal"].sum()) if not v_cat.empty else 0.0
        cat_exis = float(s_cat["saldo"].sum()) if not s_cat.empty else 0.0
        cat_vu = cat_valor / cat_cant if cat_cant > 0 else 0.0

        # Contribución al total global
        pct_valor = (cat_valor / total_valor_v * 100) if total_valor_v > 0 else 0.0
        pct_cant = (cat_cant / total_cant_v * 100) if total_cant_v > 0 else 0.0

        label = (
            f"{cat['nombre']}  ·  {cod}"
            f"  |  Ventas: {_fmt_cop(cat_valor)} ({pct_valor:.1f}%)"
            f"  |  Cant.: {_fmt_num(cat_cant)}"
            f"  |  Exis.: {_fmt_num(cat_exis)}"
        )

        with st.expander(label):
            # Resumen de la categoría
            r1, r2, r3, r4 = st.columns(4)
            with r1:
                st.metric("Cant. vendida total", f"{cat_cant:,.2f}")
            with r2:
                st.metric("Valor vtas. total", f"$ {cat_valor:,.0f}")
            with r3:
                st.metric("V/U prom. ponderado", f"$ {cat_vu:,.0f}")
            with r4:
                st.metric("Exis. 31-dic", f"{cat_exis:,.2f}")

            st.markdown(
                f'<div style="font-size:11px;color:var(--text-muted);margin:4px 0 10px;">'
                f"Aporta el <b>{pct_valor:.1f}%</b> del valor total de ventas y el "
                f"<b>{pct_cant:.1f}%</b> de la cantidad vendida.<br>"
                f"<b>V/U ponderado</b> = Valor vtas. categoría ÷ Cant. vendida categoría = "
                f"$ {cat_valor:,.0f} ÷ {cat_cant:,.2f} = <b>$ {cat_vu:,.0f}</b>"
                f"</div>",
                unsafe_allow_html=True,
            )

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
                    df_v_show = v_cat[["codigo", "nombre", "cant_vendida", "subtotal"]].copy()
                    df_v_show.columns = ["Código", "Nombre", "Cant. vendida", "Subtotal ($)"]
                    tot_cat = df_v_show["Cant. vendida"].sum()
                    val_cat = df_v_show["Subtotal ($)"].sum()
                    df_v_show["% de cant."] = (
                        df_v_show["Cant. vendida"] / tot_cat * 100
                        if tot_cat > 0 else 0.0
                    ).apply(lambda x: f"{x:.1f}%")
                    df_v_show["V/U ($)"] = (
                        df_v_show["Subtotal ($)"] / df_v_show["Cant. vendida"]
                    ).apply(lambda x: f"$ {x:,.0f}" if x > 0 else "–")
                    df_v_show["Subtotal ($)"] = df_v_show["Subtotal ($)"].apply(
                        lambda x: f"$ {x:,.0f}"
                    )
                    df_v_show["Cant. vendida"] = df_v_show["Cant. vendida"].apply(
                        lambda x: f"{x:,.2f}"
                    )
                    st.dataframe(df_v_show, use_container_width=True, hide_index=True)
                    st.caption(
                        f"Promedio ponderado = Σ Subtotal ÷ Σ Cant. = "
                        f"$ {val_cat:,.0f} ÷ {tot_cat:,.2f} = "
                        f"$ {val_cat/tot_cat:,.0f}" if tot_cat > 0 else ""
                    )

            with tabs[1]:
                if s_cat.empty:
                    st.info("Sin existencias al 31-dic en esta categoría.")
                else:
                    df_s_show = s_cat[["codigo", "nombre", "saldo"]].copy()
                    df_s_show.columns = ["Código", "Nombre", "Saldo (uds.)"]
                    tot_s = df_s_show["Saldo (uds.)"].sum()
                    df_s_show["% del total cat."] = (
                        df_s_show["Saldo (uds.)"] / tot_s * 100
                        if tot_s > 0 else 0.0
                    ).apply(lambda x: f"{x:.1f}%")
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
        sc1, sc2 = st.columns(2)
        with sc1:
            st.markdown(f"**Sin clasificar en Ventas** ({len(df_v_sin)} SKUs)")
            if not df_v_sin.empty:
                df_vs = df_v_sin[["codigo", "nombre", "cant_vendida", "subtotal"]].copy()
                df_vs.columns = ["Código", "Nombre", "Cant.", "Subtotal ($)"]
                df_vs["Subtotal ($)"] = df_vs["Subtotal ($)"].apply(lambda x: f"$ {x:,.0f}")
                df_vs["Cant."] = df_vs["Cant."].apply(lambda x: f"{x:,.2f}")
                st.dataframe(df_vs, use_container_width=True, hide_index=True)
        with sc2:
            st.markdown(f"**Sin clasificar en Saldos** ({len(df_s_sin)} SKUs)")
            if not df_s_sin.empty:
                df_ss = df_s_sin[["codigo", "nombre", "saldo"]].copy()
                df_ss.columns = ["Código", "Nombre", "Saldo (uds.)"]
                df_ss["Saldo (uds.)"] = df_ss["Saldo (uds.)"].apply(lambda x: f"{x:,.2f}")
                st.dataframe(df_ss, use_container_width=True, hide_index=True)

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
