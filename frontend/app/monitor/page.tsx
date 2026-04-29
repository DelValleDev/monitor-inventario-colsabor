"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { InventoryDashboard } from "@/components/inventory/inventory-dashboard";
import { getInventory } from "@/lib/api";
import type { InventoryPayload } from "@/types/inventory";
import { Loader } from "@/components/ui/loader";

export default function MonitorPage() {
  const [payload, setPayload] = useState<InventoryPayload | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getInventory()
      .then(setPayload)
      .catch((error) => toast.error(error instanceof Error ? error.message : "No se pudo cargar inventario"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <Loader label="Cargando monitor de inventario..." />;
  }

  return <InventoryDashboard initialPayload={payload} />;
}
