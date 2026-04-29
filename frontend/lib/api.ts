import type { DanePayload } from "@/types/dane";
import type { InventoryPayload } from "@/types/inventory";

export const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  (typeof window !== "undefined" &&
  window.location.hostname === "localhost" &&
  window.location.port === "3000"
    ? "http://localhost:8000"
    : "");

async function parseResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `HTTP ${response.status}`);
  }
  return (await response.json()) as T;
}

export async function getCurrentDane(): Promise<DanePayload> {
  return parseResponse<DanePayload>(await fetch(`${API_URL}/api/dane/current`));
}

export async function calculateDane(ventas: File, saldos: File): Promise<DanePayload> {
  const form = new FormData();
  form.append("ventas", ventas);
  form.append("saldos", saldos);
  return parseResponse<DanePayload>(
    await fetch(`${API_URL}/api/dane/calculate`, {
      method: "POST",
      body: form
    })
  );
}

export async function getInventory(refresh = false): Promise<InventoryPayload> {
  const url = new URL(`${API_URL}/api/inventory/current`, window.location.origin);
  if (refresh) {
    url.searchParams.set("refresh", "true");
  }
  return parseResponse<InventoryPayload>(await fetch(url.toString()));
}

export async function uploadInventory(file: File): Promise<InventoryPayload> {
  const form = new FormData();
  form.append("file", file);
  return parseResponse<InventoryPayload>(
    await fetch(`${API_URL}/api/inventory/upload`, {
      method: "POST",
      body: form
    })
  );
}
