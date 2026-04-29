"use client";

import {
  Bar,
  BarChart,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";
import type { InventoryPayload } from "@/shared/types/inventory";

const COLORS = ["#fb7185", "#fbbf24", "#34d399", "#94a3b8"];

export function InventoryCharts({ payload }: { payload: InventoryPayload }) {
  const statusData = [
    { name: "Criticos", value: payload.summary.criticos },
    { name: "Bajos", value: payload.summary.bajos },
    { name: "OK", value: payload.summary.ok },
    { name: "No encontrados", value: payload.summary.no_encontrados }
  ];
  const deficitData = payload.deficits.slice(0, 10).map((row) => ({
    name: `${row.Referencia} · ${row.Nombre}`.slice(0, 32),
    deficit: Math.abs(Number(row.Diferencia))
  }));

  return (
    <section className="grid charts-grid">
      <div className="panel">
        <div className="panel-header">
          <div>
            <h2>Salud del inventario</h2>
            <p className="muted">Distribucion por estado operacional.</p>
          </div>
        </div>
        <div style={{ height: 280 }}>
          <ResponsiveContainer height="100%" width="100%">
            <PieChart>
              <Pie data={statusData} dataKey="value" innerRadius={72} outerRadius={105} paddingAngle={4}>
                {statusData.map((entry, index) => (
                  <Cell fill={COLORS[index % COLORS.length]} key={entry.name} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="panel">
        <div className="panel-header">
          <div>
            <h2>Mayores deficits</h2>
            <p className="muted">Productos con mayor faltante contra el minimo.</p>
          </div>
        </div>
        <div style={{ height: 280 }}>
          <ResponsiveContainer height="100%" width="100%">
            <BarChart data={deficitData} layout="vertical" margin={{ left: 20, right: 24 }}>
              <XAxis hide type="number" />
              <YAxis dataKey="name" tick={{ fill: "#94a3b8", fontSize: 11 }} type="category" width={150} />
              <Tooltip />
              <Bar dataKey="deficit" fill="#fb7185" radius={[0, 10, 10, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </section>
  );
}
