"use client";

import type { ColumnDef } from "@tanstack/react-table";
import { formatMoney, formatNumber, formatPercent } from "@/shared/lib/format";
import type { DictRow } from "@/shared/types/dane";

const numberCell = (value: unknown) => <span className="cell-number">{formatNumber(value)}</span>;
const moneyCell = (value: unknown) => <span className="cell-number">{formatMoney(value)}</span>;
const percentCell = (value: unknown) => <span className="cell-number">{formatPercent(value)}</span>;
const nameCell = (value: unknown) => <span className="cell-name" title={String(value ?? "")}>{String(value ?? "")}</span>;

export const dianColumns: ColumnDef<DictRow>[] = [
  { accessorKey: "Código DIAN", header: "Cod. DIAN", size: 110 },
  { accessorKey: "Producto", header: "Categoria", cell: ({ getValue }) => nameCell(getValue()), size: 260 },
  { accessorKey: "Cant. vendida", header: "Cant. vendida", cell: ({ getValue }) => numberCell(getValue()), size: 140 },
  { accessorKey: "V/U. de venta", header: "V/U", cell: ({ getValue }) => moneyCell(getValue()), size: 130 },
  { accessorKey: "Valor vtas. tot.", header: "Ventas", cell: ({ getValue }) => moneyCell(getValue()), size: 160 },
  { accessorKey: "Cant. exis. 31 dic.", header: "Exis. 31 dic.", cell: ({ getValue }) => numberCell(getValue()), size: 150 }
];

export const ventasColumns: ColumnDef<DictRow>[] = [
  { accessorKey: "codigo", header: "Codigo", size: 110 },
  { accessorKey: "nombre", header: "Nombre", cell: ({ getValue }) => nameCell(getValue()), size: 420 },
  { accessorKey: "cant_vendida", header: "Cant. vendida", cell: ({ getValue }) => numberCell(getValue()), size: 150 },
  { accessorKey: "subtotal", header: "Subtotal", cell: ({ getValue }) => moneyCell(getValue()), size: 160 },
  { accessorKey: "pct_cantidad", header: "% de cant.", cell: ({ getValue }) => percentCell(getValue()), size: 120 },
  { accessorKey: "vu", header: "V/U", cell: ({ getValue }) => moneyCell(getValue()), size: 130 }
];

export const saldosColumns: ColumnDef<DictRow>[] = [
  { accessorKey: "codigo", header: "Codigo", size: 110 },
  { accessorKey: "nombre", header: "Nombre", cell: ({ getValue }) => nameCell(getValue()), size: 520 },
  { accessorKey: "saldo", header: "Saldo", cell: ({ getValue }) => numberCell(getValue()), size: 140 },
  { accessorKey: "pct_total", header: "% del total", cell: ({ getValue }) => percentCell(getValue()), size: 130 }
];
