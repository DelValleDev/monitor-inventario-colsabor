export type SortDirection = "asc" | "desc";

export type DictRow = Record<string, unknown>;

export type Category = {
  codigo: string;
  nombre: string;
  descripcion: string;
  color: string;
  cant_vendida: number;
  valor_ventas: number;
  existencias: number;
  vu_promedio: number;
  pct_valor: number;
  pct_cantidad: number;
  ventas: DictRow[];
  saldos: DictRow[];
};

export type DanePayload = {
  summary: {
    total_cant_vendida: number;
    total_valor_ventas: number;
    total_existencias: number;
    vu_global: number;
    skus_ventas_clasificados: number;
    skus_saldos_clasificados: number;
    skus_ventas_sin_clasificar: number;
    skus_saldos_sin_clasificar: number;
  };
  dian_table: DictRow[];
  categories: Category[];
  unclassified: {
    ventas: DictRow[];
    saldos: DictRow[];
  };
  source?: {
    ventas?: string;
    saldos?: string;
  };
};
