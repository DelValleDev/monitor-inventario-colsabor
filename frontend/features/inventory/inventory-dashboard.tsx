"use client";

import { Download, FileSpreadsheet, RefreshCw, UploadCloud } from "lucide-react";
import { useMemo, useState } from "react";
import { toast } from "sonner";
import { API_URL, getInventory, uploadInventory } from "@/shared/lib/api";
import { formatNumber } from "@/shared/lib/format";
import type { InventoryPayload } from "@/shared/types/inventory";
import { PageHeader } from "@/widgets/layout/page-header";
import { Button } from "@/shared/ui/button";
import { KpiCard } from "@/shared/ui/card";
import { DataTable } from "@/shared/ui/data-table";
import { Loader } from "@/shared/ui/loader";
import { inventoryColumns } from "./inventory-columns";
import { InventoryCharts } from "./inventory-charts";

export function InventoryDashboard({ initialPayload }: { initialPayload: InventoryPayload | null }) {
  const [payload, setPayload] = useState<InventoryPayload | null>(initialPayload);
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState<File | null>(null);

  async function refresh(force = false) {
    setLoading(true);
    try {
      setPayload(await getInventory(force));
      toast.success(force ? "Siigo actualizado" : "Inventario cargado");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "No se pudo cargar inventario");
    } finally {
      setLoading(false);
    }
  }

  async function upload() {
    if (!file) {
      toast.warning("Selecciona un Excel antes de procesar.");
      return;
    }
    setLoading(true);
    try {
      setPayload(await uploadInventory(file));
      toast.success("Excel procesado con datos de Siigo");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "No se pudo procesar el Excel");
    } finally {
      setLoading(false);
    }
  }

  const criticalRows = useMemo(
    () => payload?.rows.filter((row) => row.Estado.includes("Crítico") || row.Estado.includes("Bajo")) ?? [],
    [payload]
  );

  return (
    <div className="page">
      <PageHeader
        action={
          <div className="top-actions">
            <Button onClick={() => void refresh(false)} variant="secondary">
              <RefreshCw size={17} />
              Recargar
            </Button>
            <Button onClick={() => void refresh(true)}>
              <RefreshCw size={17} />
              Actualizar Siigo
            </Button>
          </div>
        }
        description="Cruce automatico entre inventario minimo, Supabase y stock actual de Siigo con graficos, filtros y exportes."
        eyebrow="Inventory Command Center"
        title="Monitor inteligente de inventario"
      />

      <section className="upload-zone">
        <div>
          <div className="label">Excel de inventario minimo</div>
          <p className="muted">Columnas esperadas: Referencia/Codigo, Nombre e Inventario minimo por gramos.</p>
        </div>
        <input accept=".xlsx,.xls" onChange={(event) => setFile(event.target.files?.[0] ?? null)} type="file" />
        <Button onClick={() => void upload()} variant="secondary">
          <UploadCloud size={17} />
          Procesar Excel
        </Button>
      </section>

      {loading ? <Loader label="Cruzando inventario con Siigo..." /> : null}

      {payload ? (
        <>
          <section className="grid summary-grid">
            <KpiCard hint={`${payload.summary.total_siigo} productos en Siigo`} label="Referencias" value={payload.summary.total} />
            <KpiCard hint="Por debajo del minimo" label="Criticos" tone="red" value={payload.summary.criticos} />
            <KpiCard hint="Margen menor o igual a 20%" label="Stock bajo" tone="amber" value={payload.summary.bajos} />
            <KpiCard hint="Stock suficiente" label="En orden" tone="green" value={payload.summary.ok} />
          </section>

          <InventoryCharts payload={payload} />

          <section className="panel">
            <div className="panel-header">
              <div>
                <h2>Resultados del cruce</h2>
                <p className="muted">
                  Fuente inventario: {payload.source.inventory} · Siigo: {payload.source.siigo} ·{" "}
                  {formatNumber(payload.summary.no_encontrados)} no encontrados
                </p>
              </div>
              <div className="top-actions">
                <a className="btn btn-secondary" href={`${API_URL}/api/inventory/export/missing`}>
                  <Download size={17} />
                  Faltantes
                </a>
                <a className="btn btn-primary" href={`${API_URL}/api/inventory/export/full`}>
                  <FileSpreadsheet size={17} />
                  Completo
                </a>
              </div>
            </div>
            <DataTable columns={inventoryColumns} data={payload.rows} searchPlaceholder="Buscar referencia o producto..." />
          </section>

          <section className="panel">
            <div className="panel-header">
              <div>
                <h2>Accion prioritaria</h2>
                <p className="muted">Criticos y bajos listos para exportar o revisar.</p>
              </div>
            </div>
            <DataTable columns={inventoryColumns} data={criticalRows} maxHeight={380} />
          </section>
        </>
      ) : (
        <div className="error">No se pudo cargar el monitor. Revisa credenciales de Supabase/Siigo o intenta refrescar.</div>
      )}
    </div>
  );
}
