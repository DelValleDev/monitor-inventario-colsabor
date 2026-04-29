export const moneyFormatter = new Intl.NumberFormat("es-CO", {
  maximumFractionDigits: 0,
  style: "currency",
  currency: "COP"
});

export const numberFormatter = new Intl.NumberFormat("es-CO", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2
});

export const compactNumberFormatter = new Intl.NumberFormat("es-CO", {
  maximumFractionDigits: 1,
  notation: "compact"
});

export const percentFormatter = new Intl.NumberFormat("es-CO", {
  minimumFractionDigits: 1,
  maximumFractionDigits: 1
});

export function asNumber(value: unknown): number {
  if (typeof value === "number") {
    return Number.isFinite(value) ? value : 0;
  }
  const parsed = Number(String(value ?? "").replace(/[$,%\s]/g, "").replaceAll(",", ""));
  return Number.isFinite(parsed) ? parsed : 0;
}

export function formatNumber(value: unknown): string {
  return numberFormatter.format(asNumber(value));
}

export function formatCompact(value: unknown): string {
  return compactNumberFormatter.format(asNumber(value));
}

export function formatMoney(value: unknown): string {
  return moneyFormatter.format(asNumber(value));
}

export function formatPercent(value: unknown): string {
  return `${percentFormatter.format(asNumber(value))}%`;
}
