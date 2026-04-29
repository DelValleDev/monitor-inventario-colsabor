import "./globals.css";
import type { ReactNode } from "react";

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
      <body>{children}</body>
    </html>
  );
}
