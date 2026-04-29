"use client";

import { Download, RefreshCw, Upload } from "lucide-react";
import { FormEvent, useState } from "react";
import { toast } from "sonner";
import { calculateDane, getCurrentDane } from "@/shared/lib/api";
import { formatMoney, formatNumber } from "@/shared/lib/format";
import type { DanePayload, DictRow } from "@/shared/types/dane";
import { Button } from "@/shared/ui/button";
import { KpiCard } from "@/shared/ui/card";
import { DataTable } from "@/shared/ui/data-table";
import { Loader } from "@/shared/ui/loader";
import { PageHeader } from "@/widgets/layout/page-header";
import { CategoryAccordion } from "./category-accordion";
import { dianColumns, saldosColumns, ventasColumns } from "./dane-columns";

function exportCsv(rows: DictRow[], filename: string) {
  if (rows.length === 0) return;
  const headers = Object.keys(rows[0]);
  const csv = [
    headers.join(","),
    ...rows.map((row) =>
      headers.map((header) => `"${String(row[header] ?? "").replaceAll('"', '""')}"`).join(",")
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

export function DaneDashboard({ initialPayload }: { initialPayload: DanePayload | null }) {
  const [payload, setPayload] = useState<DanePayload | null>(initialPayload);
  const [loading, setLoading] = useState(false);
  const [ventasFile, setVentasFile] = useState<File | null>(null);
  const [saldosFile, setSaldosFile] = useState<File | null>(null);

  async function reload() {
    setLoading(true);
    try {
      setPayload(await getCurrentDane());
      toast.success("DANE actualizado");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "No se pudo actualizar DANE");
    } finally {
      setLoading(false);
    }
  }

  async function handleUpload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!ventasFile || !saldosFile) {
      toast.warning("Selecciona ventas y saldos antes de calcular.");
      return;
    }
    setLoading(true);
    try {
      setPayload(await calculateDane(ventasFile, saldosFile));
      toast.success("Archivos procesados correctamente");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "No se pudieron procesar los CSVs");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <PageHeader
        action={
          <Button onClick={() => void reload()} variant="secondary">
            <RefreshCw size={17} />
            Recargar CSVs
          </Button>
        }
        description="Clasificacion DIAN con tablas premium, ordenamiento real y saldos completamente visibles en tabs dedicados."
        eyebrow="DANE Intelligence"
        title="Encuesta DANE con precision operativa"
      />

      <form className="upload-zone" onSubmit={handleUpload}>
        <div>
          <div className="label">Carga manual</div>
          <p className="muted">Sube ventas y saldos para recalcular sin depender de Streamlit.</p>
        </div>
        <input accept=".csv" onChange={(event) => setVentasFile(event.target.files?.[0] ?? null)} type="file" />
        <input accept=".csv" onChange={(event) => setSaldosFile(event.target.files?.[0] ?? null)} type="file" />
        <Button disabled={loading} type="submit">
          <Upload size={17} />
          Calcular
        </Button>
      </form>

      {loading ? <Loader label="Calculando encuesta DANE..." /> : null}

      {payload ? (
        <>
          <section className="grid summary-grid">
            <KpiCard hint="Valor total reportado" label="Ventas" value={formatMoney(payload.summary.total_valor_ventas)} />
            <KpiCard hint="Unidades vendidas" label="Cant. vendida" tone="green" value={formatNumber(payload.summary.total_cant_vendida)} />
            <KpiCard hint="Promedio ponderado" label="V/U global" tone="violet" value={formatMoney(payload.summary.vu_global)} />
            <KpiCard hint="Saldos clasificados" label="Existencias" tone="amber" value={formatNumber(payload.summary.total_existencias)} />
          </section>

          <section className="panel">
            <div className="panel-header">
              <div>
                <h2>Tabla DIAN</h2>
                <p className="muted">
                  Fuente: ventas {payload.source?.ventas ?? "-"} · saldos {payload.source?.saldos ?? "-"}
                </p>
              </div>
              <Button onClick={() => exportCsv(payload.dian_table, "encuesta_dane_2025.csv")} variant="secondary">
                <Download size={17} />
                Exportar CSV
              </Button>
            </div>
            <DataTable columns={dianColumns} data={payload.dian_table} searchPlaceholder="Buscar categoria DIAN..." />
          </section>

          <section className="panel">
            <div className="panel-header">
              <div>
                <h2>Desglose por categoria</h2>
                <p className="muted">Ventas y saldos se muestran en tabs reales para evitar recortes y scroll bloqueado.</p>
              </div>
            </div>
            <div className="category-list">
              {payload.categories.map((category) => (
                <CategoryAccordion category={category} key={category.codigo} />
              ))}
            </div>
          </section>

          <section className="grid charts-grid">
            <div className="panel">
              <div className="panel-header">
                <h2>Ventas sin clasificar</h2>
              </div>
              <DataTable columns={ventasColumns} data={payload.unclassified.ventas} maxHeight={360} />
            </div>
            <div className="panel">
              <div className="panel-header">
                <h2>Saldos sin clasificar</h2>
              </div>
              <DataTable columns={saldosColumns} data={payload.unclassified.saldos} maxHeight={360} />
            </div>
          </section>
        </>
      ) : (
        <div className="error">No se pudo cargar la informacion DANE.</div>
      )}
    </div>
  );
}
