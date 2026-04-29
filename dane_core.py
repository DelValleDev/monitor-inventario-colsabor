"""
Core de calculo DANE sin dependencias de Streamlit.

Este modulo es la base para la nueva API FastAPI y mantiene las mismas reglas
de negocio que la pantalla legacy de Streamlit.
"""

from __future__ import annotations

import math
import re
from pathlib import Path
from typing import Any

import pandas as pd


DIAN_CATEGORIES: list[dict[str, Any]] = [
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
        "descripcion": "Todo lo que diga COLOR/COLORANTE o nombres especificos de colorantes",
        "keywords": [
            "COLOR",
            "COLORANTE",
            "TARTRAZINA",
            "CARMOISINA",
            "ERYTROSINA",
            "ERITROSINA",
            "SUNSET",
            "PUNZO",
            "ROJO N ",
            "AZUL BTE",
            "AZUL 1 ",
        ],
        "color": "#dc2626",
    },
    {
        "codigo": "2399921",
        "nombre": "Productos aromaticos diversos",
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
            "CONDIMENTO",
            "ALIÑO",
            "ESTANDAR",
            "ESTÁNDAR",
            "STANDAR",
            "STAND",
            "TRIX",
            "GRITZ",
            "GRITS",
            "SNACK",
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
        "descripcion": "Azucar, Sacarina, Sucralosa, Stevia",
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

EXCLUDED_PRODUCT_KEYWORDS = (
    "BIDON",
    "BIDÓN",
    "BIDONES",
    "BOTELLA",
    "CAJA",
    "EMPAQUE",
    "ENVASE",
    "FRASCO",
    "GARRAFA",
    "GOTERO",
    "TAPA",
    "TAPON",
    "TAPÓN",
    "TAPONES",
    "TARRINA",
    "TARRO",
)


def classify_product(name: str) -> tuple[str | None, str]:
    """Retorna (codigo_dian, nombre_categoria) o (None, 'Sin clasificar')."""
    name_up = str(name).upper().strip()
    for cat in DIAN_CATEGORIES:
        for keyword in cat["keywords"]:
            if keyword in name_up:
                return cat["codigo"], cat["nombre"]
    return None, "Sin clasificar"


def is_excluded_inventory_product(name: str) -> bool:
    """Excluye envases/empaques que no hacen parte del producto DIAN."""
    name_up = str(name).upper()
    return any(
        re.search(rf"\b{re.escape(keyword)}S?\b", name_up)
        for keyword in EXCLUDED_PRODUCT_KEYWORDS
    )


def clean_number(value: str | float) -> float:
    """Convierte strings con comas de miles a float."""
    if isinstance(value, (int, float)):
        return float(value)
    cleaned = re.sub(r"[,\s]", "", str(value).strip())
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def parse_ventas(src: str | object) -> pd.DataFrame:
    """Parsea el CSV de ventas desde ruta o file-like object."""
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
        "codigo",
        "nombre",
        "ref_fabrica",
        "grupo",
        "cant_vendida",
        "valor_bruto",
        "descuento",
        "subtotal",
        "imp_cargo",
        "imp_retencion",
        "total",
    ] + [f"_extra_{i}" for i in range(df.shape[1] - 11)]

    grupos_validos = {"MATERIAS PRIMAS", "PRODUCTO TERMINADO", "MERCANCIAS"}
    df["grupo"] = df["grupo"].astype(str).str.strip().str.upper()
    df = df[df["grupo"].isin(grupos_validos)].copy()

    df["codigo"] = df["codigo"].astype(str).str.strip()
    df["nombre"] = df["nombre"].astype(str).str.strip()
    df["cant_vendida"] = df["cant_vendida"].apply(clean_number)
    df["subtotal"] = df["subtotal"].apply(clean_number)
    return df[df["codigo"] != ""].reset_index(drop=True)


def parse_saldos(src: str | object) -> pd.DataFrame:
    """Parsea el CSV de saldos desde ruta o file-like object."""
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
    df["saldo"] = df["saldo"].apply(clean_number)
    return df.groupby(["codigo", "nombre"], as_index=False)["saldo"].sum()


def find_csv_files() -> tuple[Path | None, Path | None]:
    """Busca CSVs de ventas y saldos en rutas candidatas del proyecto."""
    module_dir = Path(__file__).resolve().parent
    roots = [
        module_dir / "data",
        module_dir,
        module_dir.parent,
        Path.cwd(),
        Path.cwd().parent,
    ]
    candidates = list(dict.fromkeys(r.resolve() for r in roots if r.exists()))
    ventas_path: Path | None = None
    saldos_path: Path | None = None

    for base in candidates:
        v = base / "ventas2025.csv"
        s = base / "saldos31dic2025.csv"
        if ventas_path is None and v.exists():
            ventas_path = v
        if saldos_path is None and s.exists():
            saldos_path = s
        if ventas_path and saldos_path:
            return ventas_path, saldos_path

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

    return ventas_path, saldos_path


def calcular_tabla_dian(
    df_ventas: pd.DataFrame,
    df_saldos: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Clasifica productos y agrega por categoria DIAN."""
    if not df_ventas.empty:
        df_ventas = df_ventas[
            ~df_ventas["codigo"].astype(str).str.startswith("10")
        ].copy()
        df_ventas = df_ventas[
            ~df_ventas["nombre"].apply(is_excluded_inventory_product)
        ].copy()
    if not df_saldos.empty:
        df_saldos = df_saldos[
            ~df_saldos["codigo"].astype(str).str.startswith("10")
        ].copy()
        df_saldos = df_saldos[
            ~df_saldos["nombre"].apply(is_excluded_inventory_product)
        ].copy()

    df_v = df_ventas.copy()
    if not df_v.empty:
        clasificacion = df_v["nombre"].apply(
            lambda n: pd.Series(classify_product(n), index=["dian_codigo", "dian_nombre"])
        )
        df_v = pd.concat([df_v, clasificacion], axis=1)
    else:
        df_v["dian_codigo"] = pd.NA
        df_v["dian_nombre"] = "Sin clasificar"

    df_s = df_saldos.copy()
    if not df_s.empty:
        clasificacion_s = df_s["nombre"].apply(
            lambda n: pd.Series(classify_product(n), index=["dian_codigo", "dian_nombre"])
        )
        df_s = pd.concat([df_s, clasificacion_s], axis=1)
    else:
        df_s["dian_codigo"] = pd.NA
        df_s["dian_nombre"] = "Sin clasificar"

    ventas_agg = (
        df_v[df_v["dian_codigo"].notna()]
        .groupby(["dian_codigo", "dian_nombre"], as_index=False)
        .agg(cant_vendida=("cant_vendida", "sum"), valor_total=("subtotal", "sum"))
    )
    saldos_agg = (
        df_s[df_s["dian_codigo"].notna()]
        .groupby(["dian_codigo", "dian_nombre"], as_index=False)
        .agg(saldo_31dic=("saldo", "sum"))
    )

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

    return pd.DataFrame(rows), df_v, df_s


def _json_safe(value: Any) -> Any:
    if pd.isna(value):
        return None
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    return value


def _records(df: pd.DataFrame) -> list[dict[str, Any]]:
    return [
        {str(key): _json_safe(value) for key, value in row.items()}
        for row in df.to_dict(orient="records")
    ]


def build_dane_payload(
    df_ventas: pd.DataFrame,
    df_saldos: pd.DataFrame,
) -> dict[str, Any]:
    """Devuelve una respuesta JSON lista para la interfaz web."""
    df_dian, df_v_detail, df_s_detail = calcular_tabla_dian(df_ventas, df_saldos)

    total_cant_v = float(df_dian["Cant. vendida"].sum())
    total_valor_v = float(df_dian["Valor vtas. tot."].sum())
    total_exis = float(df_dian["Cant. exis. 31 dic."].sum())
    vu_global = total_valor_v / total_cant_v if total_cant_v > 0 else 0.0

    categories: list[dict[str, Any]] = []
    for cat in DIAN_CATEGORIES:
        code = cat["codigo"]
        v_cat = df_v_detail[df_v_detail["dian_codigo"] == code]
        s_cat = df_s_detail[df_s_detail["dian_codigo"] == code]
        cat_cant = float(v_cat["cant_vendida"].sum()) if not v_cat.empty else 0.0
        cat_valor = float(v_cat["subtotal"].sum()) if not v_cat.empty else 0.0
        cat_exis = float(s_cat["saldo"].sum()) if not s_cat.empty else 0.0
        cat_vu = cat_valor / cat_cant if cat_cant > 0 else 0.0
        pct_valor = (cat_valor / total_valor_v * 100) if total_valor_v > 0 else 0.0
        pct_cant = (cat_cant / total_cant_v * 100) if total_cant_v > 0 else 0.0

        sales_rows = v_cat[["codigo", "nombre", "cant_vendida", "subtotal"]].copy()
        if not sales_rows.empty:
            sales_rows["pct_cantidad"] = (
                sales_rows["cant_vendida"] / cat_cant * 100 if cat_cant > 0 else 0.0
            )
            sales_rows["vu"] = sales_rows["subtotal"] / sales_rows["cant_vendida"]
            sales_rows["vu"] = sales_rows["vu"].replace([float("inf"), float("-inf")], 0.0)
            sales_rows["vu"] = sales_rows["vu"].fillna(0.0)

        stock_rows = s_cat[["codigo", "nombre", "saldo"]].copy()
        if not stock_rows.empty:
            stock_rows["pct_total"] = (
                stock_rows["saldo"] / cat_exis * 100 if cat_exis > 0 else 0.0
            )

        categories.append(
            {
                "codigo": code,
                "nombre": cat["nombre"],
                "descripcion": cat["descripcion"],
                "color": cat["color"],
                "cant_vendida": cat_cant,
                "valor_ventas": cat_valor,
                "existencias": cat_exis,
                "vu_promedio": cat_vu,
                "pct_valor": pct_valor,
                "pct_cantidad": pct_cant,
                "ventas": _records(sales_rows),
                "saldos": _records(stock_rows),
            }
        )

    return {
        "summary": {
            "total_cant_vendida": total_cant_v,
            "total_valor_ventas": total_valor_v,
            "total_existencias": total_exis,
            "vu_global": vu_global,
            "skus_ventas_clasificados": int(df_v_detail["dian_codigo"].notna().sum()),
            "skus_saldos_clasificados": int(df_s_detail["dian_codigo"].notna().sum()),
            "skus_ventas_sin_clasificar": int(df_v_detail["dian_codigo"].isna().sum()),
            "skus_saldos_sin_clasificar": int(df_s_detail["dian_codigo"].isna().sum()),
        },
        "dian_table": _records(df_dian),
        "categories": categories,
        "unclassified": {
            "ventas": _records(df_v_detail[df_v_detail["dian_codigo"].isna()]),
            "saldos": _records(df_s_detail[df_s_detail["dian_codigo"].isna()]),
        },
    }
