"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

type SortDirection = "asc" | "desc";
type SortState = { key: string; direction: SortDirection };

type TableColumn = {
  key: string;
  label: string;
  numeric?: boolean;
  format?: (value: unknown) => string;
};

type DictRow = Record<string, unknown>;

type Category = {
  codigo: string;
  nombre: string;
  descripcion: string;
  color: string;
  cant_vendida: number;
  valor_ventas: number;
  existencias: number;
  vu_promedio: number;
  pct_valor: number;
  pct_cantidad: number;
  ventas: DictRow[];
  saldos: DictRow[];
};

type DanePayload = {
  summary: {
    total_cant_vendida: number;
    total_valor_ventas: number;
    total_existencias: number;
    vu_global: number;
    skus_ventas_clasificados: number;
    skus_saldos_clasificados: number;
    skus_ventas_sin_clasificar: number;
    skus_saldos_sin_clasificar: number;
  };
  dian_table: DictRow[];
  categories: Category[];
  unclassified: {
    ventas: DictRow[];
    saldos: DictRow[];
  };
  source?: {
    ventas?: string;
    saldos?: string;
  };
};

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  (typeof window !== "undefined" &&
  window.location.hostname === "localhost" &&
  window.location.port === "3000"
    ? "http://localhost:8000"
    : "");

const moneyFormatter = new Intl.NumberFormat("es-CO", {
  maximumFractionDigits: 0,
  style: "currency",
  currency: "COP"
});

const numberFormatter = new Intl.NumberFormat("es-CO", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2
});

const percentFormatter = new Intl.NumberFormat("es-CO", {
  minimumFractionDigits: 1,
  maximumFractionDigits: 1
});

function asNumber(value: unknown): number {
  if (typeof value === "number") {
    return Number.isFinite(value) ? value : 0;
  }
  const parsed = Number(String(value ?? "").replace(/[$,%\s]/g, "").replaceAll(",", ""));
  return Number.isFinite(parsed) ? parsed : 0;
}

function formatNumber(value: unknown): string {
  return numberFormatter.format(asNumber(value));
}

function formatMoney(value: unknown): string {
  return moneyFormatter.format(asNumber(value));
}

function formatPercent(value: unknown): string {
  return `${percentFormatter.format(asNumber(value))}%`;
}

function compareRows(a: DictRow, b: DictRow, sort: SortState, numeric?: boolean): number {
  const left = a[sort.key];
  const right = b[sort.key];

  if (numeric) {
    return asNumber(left) - asNumber(right);
  }

  return String(left ?? "").localeCompare(String(right ?? ""), "es", {
    numeric: true,
    sensitivity: "base"
  });
}

function SortableTable({
  columns,
  rows,
  initialSort,
  emptyText = "Sin datos."
}: {
  columns: TableColumn[];
  rows: DictRow[];
  initialSort?: SortState;
  emptyText?: string;
}) {
  const [sort, setSort] = useState<SortState>(
    initialSort ?? { key: columns[0]?.key ?? "", direction: "asc" }
  );

  const sortedRows = useMemo(() => {
    const column = columns.find((item) => item.key === sort.key);
    const direction = sort.direction === "asc" ? 1 : -1;
    return [...rows].sort((a, b) => compareRows(a, b, sort, column?.numeric) * direction);
  }, [columns, rows, sort]);

  function toggleSort(key: string) {
    setSort((current) => ({
      key,
      direction: current.key === key && current.direction === "asc" ? "desc" : "asc"
    }));
  }

  if (rows.length === 0) {
    return <p className="muted">{emptyText}</p>;
  }

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            {columns.map((column) => (
              <th className={column.numeric ? "num" : undefined} key={column.key}>
                <button type="button" onClick={() => toggleSort(column.key)}>
                  {column.label}
                  <span className="sort">
                    {sort.key === column.key ? (sort.direction === "asc" ? "↑" : "↓") : ""}
                  </span>
                </button>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sortedRows.map((row, rowIndex) => (
            <tr key={`${String(row.codigo ?? rowIndex)}-${rowIndex}`}>
              {columns.map((column) => {
                const value = row[column.key];
                return (
                  <td className={column.numeric ? "num" : undefined} key={column.key}>
                    {column.format ? column.format(value) : String(value ?? "")}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function exportCsv(rows: DictRow[], filename: string) {
  if (rows.length === 0) {
    return;
  }

  const headers = Object.keys(rows[0]);
  const csv = [
    headers.join(","),
    ...rows.map((row) =>
      headers
        .map((header) => `"${String(row[header] ?? "").replaceAll('"', '""')}"`)
        .join(",")
    )
  ].join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

const dianColumns: TableColumn[] = [
  { key: "Código DIAN", label: "Cod. DIAN" },
  { key: "Producto", label: "Categoria" },
  { key: "Cant. vendida", label: "Cant. vendida", numeric: true, format: formatNumber },
  { key: "V/U. de venta", label: "V/U", numeric: true, format: formatMoney },
  { key: "Valor vtas. tot.", label: "Ventas", numeric: true, format: formatMoney },
  { key: "Cant. exis. 31 dic.", label: "Exis. 31 dic.", numeric: true, format: formatNumber }
];

const ventasColumns: TableColumn[] = [
  { key: "codigo", label: "Codigo" },
  { key: "nombre", label: "Nombre" },
  { key: "cant_vendida", label: "Cant. vendida", numeric: true, format: formatNumber },
  { key: "subtotal", label: "Subtotal", numeric: true, format: formatMoney },
  { key: "pct_cantidad", label: "% de cant.", numeric: true, format: formatPercent },
  { key: "vu", label: "V/U", numeric: true, format: formatMoney }
];

const saldosColumns: TableColumn[] = [
  { key: "codigo", label: "Codigo" },
  { key: "nombre", label: "Nombre" },
  { key: "saldo", label: "Saldo", numeric: true, format: formatNumber },
  { key: "pct_total", label: "% del total", numeric: true, format: formatPercent }
];

export default function Home() {
  const [payload, setPayload] = useState<DanePayload | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [ventasFile, setVentasFile] = useState<File | null>(null);
  const [saldosFile, setSaldosFile] = useState<File | null>(null);
  const [openCodes, setOpenCodes] = useState<Set<string>>(new Set());

  async function loadCurrent() {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/api/dane/current`);
      if (!response.ok) {
        throw new Error(await response.text());
      }
      setPayload((await response.json()) as DanePayload);
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo cargar DANE.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadCurrent();
  }, []);

  async function handleUpload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!ventasFile || !saldosFile) {
      setError("Selecciona los dos CSVs: ventas y saldos.");
      return;
    }

    const form = new FormData();
    form.append("ventas", ventasFile);
    form.append("saldos", saldosFile);

    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/api/dane/calculate`, {
        method: "POST",
        body: form
      });
      if (!response.ok) {
        throw new Error(await response.text());
      }
      setPayload((await response.json()) as DanePayload);
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo calcular DANE.");
    } finally {
      setLoading(false);
    }
  }

  function toggleCategory(code: string) {
    setOpenCodes((current) => {
      const next = new Set(current);
      if (next.has(code)) {
        next.delete(code);
      } else {
        next.add(code);
      }
      return next;
    });
  }

  return (
    <main className="shell">
      <header className="topbar">
        <div className="brand">
          <h1>Colsabor Inventory</h1>
          <p>Nueva interfaz React + API FastAPI, sin componentes Streamlit.</p>
        </div>
        <nav className="nav" aria-label="Secciones">
          <button type="button">Monitor</button>
          <button className="active" type="button">Encuesta DANE</button>
        </nav>
      </header>

      <section className="content">
        {error ? <div className="error">{error}</div> : null}

        <div className="panel">
          <div className="panel-header">
            <div>
              <h2>Encuesta de Produccion DANE</h2>
              <p className="muted">
                Datos: ventas {payload?.source?.ventas ?? "-"} | saldos{" "}
                {payload?.source?.saldos ?? "-"}
              </p>
            </div>
            <button className="secondary" type="button" onClick={() => void loadCurrent()}>
              Recargar CSVs actuales
            </button>
          </div>

          <form className="upload" onSubmit={handleUpload}>
            <label>
              Ventas CSV{" "}
              <input
                accept=".csv"
                type="file"
                onChange={(event) => setVentasFile(event.target.files?.[0] ?? null)}
              />
            </label>
            <label>
              Saldos CSV{" "}
              <input
                accept=".csv"
                type="file"
                onChange={(event) => setSaldosFile(event.target.files?.[0] ?? null)}
              />
            </label>
            <button className="primary" disabled={loading} type="submit">
              Calcular con archivos
            </button>
          </form>
        </div>

        {loading ? <p className="muted">Cargando...</p> : null}

        {payload ? (
          <>
            <section className="grid summary">
              <div className="card">
                <div className="label">Ventas</div>
                <div className="value">{formatMoney(payload.summary.total_valor_ventas)}</div>
              </div>
              <div className="card">
                <div className="label">Cant. vendida</div>
                <div className="value">{formatNumber(payload.summary.total_cant_vendida)}</div>
              </div>
              <div className="card">
                <div className="label">V/U global</div>
                <div className="value">{formatMoney(payload.summary.vu_global)}</div>
              </div>
              <div className="card">
                <div className="label">Existencias</div>
                <div className="value">{formatNumber(payload.summary.total_existencias)}</div>
              </div>
            </section>

            <section className="panel">
              <div className="panel-header">
                <h2>Tabla DIAN</h2>
                <button
                  className="secondary"
                  type="button"
                  onClick={() => exportCsv(payload.dian_table, "encuesta_dane_2025.csv")}
                >
                  Exportar CSV
                </button>
              </div>
              <SortableTable
                columns={dianColumns}
                rows={payload.dian_table}
                initialSort={{ key: "Valor vtas. tot.", direction: "desc" }}
              />
            </section>

            <section className="panel">
              <div className="panel-header">
                <h2>Desglose por categoria</h2>
                <p className="muted">
                  Cada tabla ordena por valores numericos reales, no por texto formateado.
                </p>
              </div>

              <div className="categories">
                {payload.categories.map((category) => {
                  const isOpen = openCodes.has(category.codigo);
                  return (
                    <article className={`category ${isOpen ? "open" : ""}`} key={category.codigo}>
                      <button
                        className="category-header"
                        type="button"
                        onClick={() => toggleCategory(category.codigo)}
                      >
                        <span className="category-main">
                          <span className="chevron">&gt;</span>
                          <span className="dot" style={{ background: category.color }} />
                          <span>
                            <span className="category-title">
                              {category.nombre} · {category.codigo}
                            </span>
                            <span className="category-meta">
                              Ventas: {formatMoney(category.valor_ventas)} (
                              {formatPercent(category.pct_valor)}) | Cant.:{" "}
                              {formatNumber(category.cant_vendida)} | Exis.:{" "}
                              {formatNumber(category.existencias)}
                            </span>
                          </span>
                        </span>
                      </button>

                      {isOpen ? (
                        <div className="category-body">
                          <div className="grid metrics">
                            <div className="metric">
                              <div className="label">Cant. vendida total</div>
                              <div className="value">{formatNumber(category.cant_vendida)}</div>
                            </div>
                            <div className="metric">
                              <div className="label">Valor ventas</div>
                              <div className="value">{formatMoney(category.valor_ventas)}</div>
                            </div>
                            <div className="metric">
                              <div className="label">V/U ponderado</div>
                              <div className="value">{formatMoney(category.vu_promedio)}</div>
                            </div>
                            <div className="metric">
                              <div className="label">Exis. 31-dic</div>
                              <div className="value">{formatNumber(category.existencias)}</div>
                            </div>
                          </div>

                          <p className="muted">Regla: {category.descripcion}</p>
                          <div className="tabs">
                            <div>
                              <h3>Ventas 2025</h3>
                              <SortableTable
                                columns={ventasColumns}
                                emptyText="Sin ventas registradas en esta categoria."
                                initialSort={{ key: "cant_vendida", direction: "desc" }}
                                rows={category.ventas}
                              />
                            </div>
                            <div>
                              <h3>Saldos 31-dic</h3>
                              <SortableTable
                                columns={saldosColumns}
                                emptyText="Sin existencias en esta categoria."
                                initialSort={{ key: "saldo", direction: "desc" }}
                                rows={category.saldos}
                              />
                            </div>
                          </div>
                        </div>
                      ) : null}
                    </article>
                  );
                })}
              </div>
            </section>
          </>
        ) : null}
      </section>
    </main>
  );
}
