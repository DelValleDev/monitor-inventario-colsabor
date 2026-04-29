from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes import dane, health, inventory
from backend.app.infrastructure.web.static_frontend import mount_static_frontend


def create_app() -> FastAPI:
    app = FastAPI(
        title="Colsabor Inventory API",
        version="0.2.0",
        description="Backend hexagonal para el monitor de inventario Colsabor.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health.router)
    app.include_router(dane.router)
    app.include_router(inventory.router)
    mount_static_frontend(app)
    return app


app = create_app()
