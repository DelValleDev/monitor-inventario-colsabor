from __future__ import annotations

from io import BytesIO

import inventory_core


class InventoryService:
    def login(self, email: str, password: str) -> dict:
        return inventory_core.authenticate_user(email, password)

    def current(self, *, refresh: bool = False) -> dict:
        return inventory_core.get_current_inventory_payload(refresh=refresh)

    def upload(self, raw: bytes, filename: str | None) -> dict:
        df_excel = inventory_core.parse_inventory_excel(BytesIO(raw))
        df_siigo, total_siigo, updated_at, source = inventory_core.get_siigo_dataframe(refresh=False)
        payload = inventory_core.build_inventory_payload(df_excel, df_siigo, total_siigo, updated_at, source)
        payload["source"]["inventory"] = filename or "excel"
        return payload

    def export_full(self) -> bytes:
        payload = self.current(refresh=False)
        df = inventory_core.pd.DataFrame(payload["rows"])
        return inventory_core.generar_excel_tabla_descarga(
            df,
            sheet_title="inventario",
            table_display_name="TablaInventario",
        )

    def export_missing(self) -> bytes:
        payload = self.current(refresh=False)
        rows = [
            row
            for row in payload["rows"]
            if "Crítico" in str(row.get("Estado", "")) or "Bajo" in str(row.get("Estado", ""))
        ]
        df = inventory_core.pd.DataFrame(rows)
        return inventory_core.generar_excel_tabla_descarga(
            df,
            sheet_title="faltantes",
            table_display_name="TablaFaltantes",
        )
