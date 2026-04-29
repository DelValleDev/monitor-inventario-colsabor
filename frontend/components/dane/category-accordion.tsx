"use client";

import { AnimatePresence, motion } from "framer-motion";
import { BarChart3, Boxes, ChevronRight, PackageOpen } from "lucide-react";
import { useState } from "react";
import { formatMoney, formatNumber, formatPercent } from "@/lib/format";
import type { Category } from "@/types/dane";
import { DataTable } from "@/components/ui/data-table";
import { TabSwitch } from "@/components/ui/tabs";
import { saldosColumns, ventasColumns } from "./dane-columns";

type ActiveTab = "ventas" | "saldos";

export function CategoryAccordion({ category }: { category: Category }) {
  const [open, setOpen] = useState(false);
  const [tab, setTab] = useState<ActiveTab>("ventas");

  return (
    <motion.article className="category-card" layout>
      <button className="category-trigger" onClick={() => setOpen((value) => !value)} type="button">
        <span className="category-title-row">
          <motion.span animate={{ rotate: open ? 90 : 0 }}>
            <ChevronRight size={18} />
          </motion.span>
          <span className="category-dot" style={{ background: category.color, color: category.color }} />
          <span>
            <span className="category-title">{category.nombre} · {category.codigo}</span>
            <span className="category-meta">
              Ventas {formatMoney(category.valor_ventas)} ({formatPercent(category.pct_valor)}) · Cant.{" "}
              {formatNumber(category.cant_vendida)} · Exis. {formatNumber(category.existencias)}
            </span>
          </span>
        </span>
      </button>

      <AnimatePresence initial={false}>
        {open ? (
          <motion.div
            animate={{ height: "auto", opacity: 1 }}
            className="category-body"
            exit={{ height: 0, opacity: 0 }}
            initial={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.22 }}
          >
            <div className="grid metrics-grid">
              <div className="mini-metric">
                <span className="label">Cant. vendida</span>
                <strong>{formatNumber(category.cant_vendida)}</strong>
              </div>
              <div className="mini-metric">
                <span className="label">Valor ventas</span>
                <strong>{formatMoney(category.valor_ventas)}</strong>
              </div>
              <div className="mini-metric">
                <span className="label">V/U ponderado</span>
                <strong>{formatMoney(category.vu_promedio)}</strong>
              </div>
              <div className="mini-metric">
                <span className="label">Exis. 31-dic</span>
                <strong>{formatNumber(category.existencias)}</strong>
              </div>
            </div>

            <div className="panel-header">
              <div>
                <h3>Detalle operacional</h3>
                <p className="muted">Regla de clasificacion: {category.descripcion}</p>
              </div>
              <TabSwitch<ActiveTab>
                onChange={setTab}
                tabs={[
                  { value: "ventas", label: "Ventas 2025", icon: <BarChart3 size={16} /> },
                  { value: "saldos", label: "Saldos 31-dic", icon: <Boxes size={16} /> }
                ]}
                value={tab}
              />
            </div>

            {tab === "ventas" ? (
              <DataTable
                columns={ventasColumns}
                data={category.ventas}
                maxHeight={520}
                searchPlaceholder="Buscar en ventas..."
              />
            ) : (
              <DataTable
                columns={saldosColumns}
                data={category.saldos}
                maxHeight={520}
                searchPlaceholder="Buscar en saldos..."
              />
            )}

            {tab === "saldos" && category.saldos.length === 0 ? (
              <div className="loader-panel">
                <PackageOpen size={28} />
                <span className="muted">Sin existencias registradas para esta categoria.</span>
              </div>
            ) : null}
          </motion.div>
        ) : null}
      </AnimatePresence>
    </motion.article>
  );
}
