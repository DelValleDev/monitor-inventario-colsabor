"use client";

import type { ColumnDef } from "@tanstack/react-table";
import { formatNumber } from "@/shared/lib/format";
import type { InventoryRow } from "@/shared/types/inventory";

function statusClass(status: string) {
  if (status.includes("Crítico")) return "status-critical";
  if (status.includes("Bajo")) return "status-low";
  if (status.includes("OK")) return "status-ok";
  return "status-missing";
}

export const inventoryColumns: ColumnDef<InventoryRow>[] = [
  { accessorKey: "Referencia", header: "Referencia", size: 130 },
  {
    accessorKey: "Nombre",
    header: "Nombre",
    cell: ({ getValue }) => (
      <span className="cell-name" title={String(getValue() ?? "")}>
        {String(getValue() ?? "")}
      </span>
    ),
    size: 440
  },
  {
    accessorKey: "Mínimo (g)",
    header: "Minimo (g)",
    cell: ({ getValue }) => <span className="cell-number">{formatNumber(getValue())}</span>,
    size: 140
  },
  {
    accessorKey: "Stock Actual",
    header: "Stock actual",
    cell: ({ getValue }) => <span className="cell-number">{formatNumber(getValue())}</span>,
    size: 140
  },
  {
    accessorKey: "Diferencia",
    header: "Diferencia",
    cell: ({ getValue }) => <span className="cell-number">{formatNumber(getValue())}</span>,
    size: 140
  },
  {
    accessorKey: "Estado",
    header: "Estado",
    cell: ({ getValue }) => {
      const status = String(getValue() ?? "");
      return <span className={`status-badge ${statusClass(status)}`}>{status}</span>;
    },
    size: 180
  }
];
