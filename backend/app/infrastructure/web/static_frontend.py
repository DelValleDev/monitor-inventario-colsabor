from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


def mount_static_frontend(app: FastAPI) -> None:
    frontend_out = Path(__file__).resolve().parents[4] / "frontend" / "out"
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
