"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { DaneDashboard } from "@/components/dane/dane-dashboard";
import { getCurrentDane } from "@/lib/api";
import type { DanePayload } from "@/types/dane";
import { Loader } from "@/components/ui/loader";

export default function DanePage() {
  const [payload, setPayload] = useState<DanePayload | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getCurrentDane()
      .then(setPayload)
      .catch((error) => toast.error(error instanceof Error ? error.message : "No se pudo cargar DANE"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <Loader label="Cargando Encuesta DANE..." />;
  }

  return <DaneDashboard initialPayload={payload} />;
}
