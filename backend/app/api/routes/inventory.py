from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import Response

from backend.app.application.inventory_service import InventoryService

router = APIRouter(tags=["inventory"])
service = InventoryService()

EXCEL_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@router.post("/api/auth/login")
async def login(payload: dict) -> dict:
    result = service.login(str(payload.get("email", "")), str(payload.get("password", "")))
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["error"])
    return result


@router.get("/api/inventory/current")
def inventory_current(refresh: Annotated[bool, Query()] = False) -> dict:
    try:
        return service.current(refresh=refresh)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/api/inventory/refresh")
def inventory_refresh() -> dict:
    try:
        return service.current(refresh=True)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/api/inventory/upload")
async def inventory_upload(file: Annotated[UploadFile, File(description="Excel de inventario minimo")]) -> dict:
    try:
        return service.upload(await file.read(), file.filename)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/api/inventory/export/full")
def inventory_export_full() -> Response:
    try:
        return Response(
            content=service.export_full(),
            media_type=EXCEL_MIME,
            headers={"Content-Disposition": 'attachment; filename="inventario_completo.xlsx"'},
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/api/inventory/export/missing")
def inventory_export_missing() -> Response:
    try:
        return Response(
            content=service.export_missing(),
            media_type=EXCEL_MIME,
            headers={"Content-Disposition": 'attachment; filename="faltantes.xlsx"'},
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
