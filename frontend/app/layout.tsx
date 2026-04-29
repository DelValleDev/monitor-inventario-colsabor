import "./globals.css";
import type { ReactNode } from "react";
import { AppShell } from "@/widgets/layout/app-shell";

export const metadata = {
  title: "Colsabor Inventory",
  description: "Monitor de inventario Colsabor sin Streamlit"
};

export default function RootLayout({
  children
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <html lang="es">
      <body>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
