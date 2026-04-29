import type { DictRow } from "./dane";

export type InventoryRow = {
  Referencia: string;
  Nombre: string;
  "Mínimo (g)": number;
  "Stock Actual": number;
  Diferencia: number;
  Estado: string;
};

export type InventorySummary = {
  total: number;
  criticos: number;
  bajos: number;
  ok: number;
  no_encontrados: number;
  total_siigo: number;
  ultima_actualizacion?: string;
};

export type InventoryPayload = {
  summary: InventorySummary;
  rows: InventoryRow[];
  missing: InventoryRow[];
  deficits: InventoryRow[];
  source: {
    inventory: string;
    siigo: string;
  };
  technical?: DictRow;
};
