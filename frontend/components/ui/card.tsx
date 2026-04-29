import { type HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

export function Card({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("glass-card", className)} {...props} />;
}

export function KpiCard({
  label,
  value,
  hint,
  tone = "blue"
}: {
  label: string;
  value: string | number;
  hint?: string;
  tone?: "blue" | "red" | "amber" | "green" | "violet";
}) {
  return (
    <Card className={`kpi-card kpi-${tone}`}>
      <span className="kpi-orb" />
      <div className="label">{label}</div>
      <div className="value">{value}</div>
      {hint ? <div className="kpi-hint">{hint}</div> : null}
    </Card>
  );
}
