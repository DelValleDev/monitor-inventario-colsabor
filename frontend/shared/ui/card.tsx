import { type HTMLAttributes } from "react";
import { cn } from "@/shared/lib/utils";
import { AnimatedNumber } from "./animated-number";

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
  const numericValue = typeof value === "number" ? value : null;
  return (
    <Card className={`kpi-card kpi-${tone}`}>
      <span className="kpi-orb" />
      <div className="label">{label}</div>
      <div className="value">
        {numericValue === null ? value : <AnimatedNumber value={numericValue} />}
      </div>
      {hint ? <div className="kpi-hint">{hint}</div> : null}
    </Card>
  );
}
