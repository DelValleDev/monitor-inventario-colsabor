from __future__ import annotations

from io import StringIO
from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.app.application.dane_service import DaneService

router = APIRouter(prefix="/api/dane", tags=["dane"])
service = DaneService()


async def _upload_to_text(upload: UploadFile) -> StringIO:
    raw = await upload.read()
    try:
        return StringIO(raw.decode("utf-8"))
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail=f"El archivo {upload.filename} no esta en UTF-8.") from exc


@router.get("/current")
def calculate_current_dane() -> dict:
    try:
        return service.current()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/calculate")
async def calculate_uploaded_dane(
    ventas: Annotated[UploadFile, File(description="CSV de ventas 2025")],
    saldos: Annotated[UploadFile, File(description="CSV de saldos 31-dic")],
) -> dict:
    try:
        return service.calculate(
            await _upload_to_text(ventas),
            await _upload_to_text(saldos),
            ventas.filename or "ventas.csv",
            saldos.filename or "saldos.csv",
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
