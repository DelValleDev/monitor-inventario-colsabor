from __future__ import annotations

from io import BytesIO
from io import StringIO
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

import dane_core
import inventory_core


app = FastAPI(
    title="Colsabor Inventory API",
    version="0.1.0",
    description="API para migrar el monitor de inventario fuera de Streamlit.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def _upload_to_text(upload: UploadFile) -> StringIO:
    raw = await upload.read()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"El archivo {upload.filename} no esta en UTF-8.",
        ) from exc
    return StringIO(text)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/auth/login")
async def login(payload: dict) -> dict:
    email = str(payload.get("email", ""))
    password = str(payload.get("password", ""))
    result = inventory_core.authenticate_user(email, password)
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["error"])
    return result


@app.get("/api/dane/current")
def calculate_current_dane() -> dict:
    """Calcula DANE con los CSVs versionados en la carpeta data/."""
    ventas_path, saldos_path = dane_core.find_csv_files()
    if ventas_path is None or saldos_path is None:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron ventas2025.csv y saldos31dic2025.csv.",
        )

    try:
        df_ventas = dane_core.parse_ventas(str(ventas_path))
        df_saldos = dane_core.parse_saldos(str(saldos_path))
        payload = dane_core.build_dane_payload(df_ventas, df_saldos)
    except Exception as exc:  # pragma: no cover - guardrail API
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    payload["source"] = {
        "ventas": ventas_path.name,
        "saldos": saldos_path.name,
    }
    return payload


@app.post("/api/dane/calculate")
async def calculate_uploaded_dane(
    ventas: Annotated[UploadFile, File(description="CSV de ventas 2025")],
    saldos: Annotated[UploadFile, File(description="CSV de saldos 31-dic")],
) -> dict:
    """Calcula DANE a partir de dos CSVs subidos por el navegador."""
    try:
        ventas_text = await _upload_to_text(ventas)
        saldos_text = await _upload_to_text(saldos)
        df_ventas = dane_core.parse_ventas(ventas_text)
        df_saldos = dane_core.parse_saldos(saldos_text)
        payload = dane_core.build_dane_payload(df_ventas, df_saldos)
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - guardrail API
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    payload["source"] = {
        "ventas": ventas.filename,
        "saldos": saldos.filename,
    }
    return payload


@app.get("/api/inventory/current")
def inventory_current(refresh: Annotated[bool, Query()] = False) -> dict:
    try:
        return inventory_core.get_current_inventory_payload(refresh=refresh)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/inventory/refresh")
def inventory_refresh() -> dict:
    try:
        return inventory_core.get_current_inventory_payload(refresh=True)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/inventory/upload")
async def inventory_upload(file: Annotated[UploadFile, File(description="Excel de inventario minimo")]) -> dict:
    raw = await file.read()
    try:
        df_excel = inventory_core.parse_inventory_excel(BytesIO(raw))
        df_siigo, total_siigo, updated_at, source = inventory_core.get_siigo_dataframe(refresh=False)
        payload = inventory_core.build_inventory_payload(df_excel, df_siigo, total_siigo, updated_at, source)
        payload["source"]["inventory"] = file.filename or "excel"
        return payload
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/inventory/export/full")
def inventory_export_full() -> Response:
    try:
        payload = inventory_core.get_current_inventory_payload(refresh=False)
        df = inventory_core.pd.DataFrame(payload["rows"])
        content = inventory_core.generar_excel_tabla_descarga(df, sheet_title="inventario", table_display_name="TablaInventario")
        return Response(
            content=content,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": 'attachment; filename="inventario_completo.xlsx"'},
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/inventory/export/missing")
def inventory_export_missing() -> Response:
    try:
        payload = inventory_core.get_current_inventory_payload(refresh=False)
        rows = [
            row
            for row in payload["rows"]
            if "Crítico" in str(row.get("Estado", "")) or "Bajo" in str(row.get("Estado", ""))
        ]
        df = inventory_core.pd.DataFrame(rows)
        content = inventory_core.generar_excel_tabla_descarga(df, sheet_title="faltantes", table_display_name="TablaFaltantes")
        return Response(
            content=content,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": 'attachment; filename="faltantes.xlsx"'},
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


frontend_out = Path(__file__).resolve().parents[1] / "frontend" / "out"
static_assets = frontend_out / "_next"
if static_assets.exists():
    app.mount("/_next", StaticFiles(directory=static_assets), name="next-assets")


@app.get("/{full_path:path}")
def serve_frontend(full_path: str):
    if not frontend_out.exists():
        raise HTTPException(status_code=404, detail="Frontend no construido.")

    requested = frontend_out / full_path
    if requested.is_file():
        return FileResponse(requested)

    html_file = frontend_out / f"{full_path}.html"
    if html_file.is_file():
        return FileResponse(html_file)

    index_file = frontend_out / "index.html"
    if index_file.is_file():
        return FileResponse(index_file)

    raise HTTPException(status_code=404, detail="Frontend no encontrado.")
