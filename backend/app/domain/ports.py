from __future__ import annotations

from typing import Protocol


class DaneUseCase(Protocol):
    def current(self) -> dict: ...


class InventoryUseCase(Protocol):
    def current(self, *, refresh: bool = False) -> dict: ...
