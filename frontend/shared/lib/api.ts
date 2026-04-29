import axios from "axios";
import type { DanePayload } from "@/shared/types/dane";
import type { InventoryPayload } from "@/shared/types/inventory";
import { danePayloadSchema, inventoryPayloadSchema } from "./api-schemas";

export const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  (typeof window !== "undefined" &&
  window.location.hostname === "localhost" &&
  window.location.port === "3000"
    ? "http://localhost:8000"
    : "");

const api = axios.create({
  baseURL: API_URL,
  timeout: 60000
});

function normalizeApiError(error: unknown): Error {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail ?? error.response?.data;
    return new Error(typeof detail === "string" ? detail : error.message);
  }
  return error instanceof Error ? error : new Error("Error inesperado de API");
}

export async function getCurrentDane(): Promise<DanePayload> {
  try {
    const { data } = await api.get("/api/dane/current");
    return danePayloadSchema.parse(data) as DanePayload;
  } catch (error) {
    throw normalizeApiError(error);
  }
}

export async function calculateDane(ventas: File, saldos: File): Promise<DanePayload> {
  const form = new FormData();
  form.append("ventas", ventas);
  form.append("saldos", saldos);
  try {
    const { data } = await api.post("/api/dane/calculate", form);
    return danePayloadSchema.parse(data) as DanePayload;
  } catch (error) {
    throw normalizeApiError(error);
  }
}

export async function getInventory(refresh = false): Promise<InventoryPayload> {
  try {
    const { data } = await api.get("/api/inventory/current", {
      params: refresh ? { refresh: true } : undefined
    });
    return inventoryPayloadSchema.parse(data) as InventoryPayload;
  } catch (error) {
    throw normalizeApiError(error);
  }
}

export async function uploadInventory(file: File): Promise<InventoryPayload> {
  const form = new FormData();
  form.append("file", file);
  try {
    const { data } = await api.post("/api/inventory/upload", form);
    return inventoryPayloadSchema.parse(data) as InventoryPayload;
  } catch (error) {
    throw normalizeApiError(error);
  }
}
