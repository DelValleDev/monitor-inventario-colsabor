from __future__ import annotations

from io import StringIO
from typing import Annotated

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

import dane_core


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
