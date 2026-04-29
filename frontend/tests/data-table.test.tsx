import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import type { ColumnDef } from "@tanstack/react-table";
import { DataTable } from "@/shared/ui/data-table";

type Row = { codigo: string; nombre: string; cantidad: number };

const columns: ColumnDef<Row>[] = [
  { accessorKey: "codigo", header: "Codigo" },
  { accessorKey: "nombre", header: "Nombre" },
  { accessorKey: "cantidad", header: "Cantidad" }
];

describe("DataTable", () => {
  it("filters rows from the search input", async () => {
    render(
      <DataTable
        columns={columns}
        data={[
          { codigo: "A", nombre: "Esencia", cantidad: 10 },
          { codigo: "B", nombre: "Colorante", cantidad: 2 }
        ]}
      />
    );

    await userEvent.type(screen.getByPlaceholderText("Buscar..."), "Colorante");
    expect(screen.getByText("Colorante")).toBeInTheDocument();
    expect(screen.queryByText("Esencia")).not.toBeInTheDocument();
  });
});
