from __future__ import annotations

from io import StringIO

import dane_core


class DaneService:
    def current(self) -> dict:
        ventas_path, saldos_path = dane_core.find_csv_files()
        if ventas_path is None or saldos_path is None:
            raise FileNotFoundError("No se encontraron ventas2025.csv y saldos31dic2025.csv.")
        payload = dane_core.build_dane_payload(
            dane_core.parse_ventas(str(ventas_path)),
            dane_core.parse_saldos(str(saldos_path)),
        )
        payload["source"] = {"ventas": ventas_path.name, "saldos": saldos_path.name}
        return payload

    def calculate(self, ventas_text: StringIO, saldos_text: StringIO, ventas_name: str, saldos_name: str) -> dict:
        payload = dane_core.build_dane_payload(
            dane_core.parse_ventas(ventas_text),
            dane_core.parse_saldos(saldos_text),
        )
        payload["source"] = {"ventas": ventas_name, "saldos": saldos_name}
        return payload
