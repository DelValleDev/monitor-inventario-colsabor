"use client";

import { BarChart3, Boxes, DatabaseZap, Moon, PackageSearch, RefreshCw, Sun } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { type ReactNode, useEffect, useState } from "react";
import { Toaster } from "sonner";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/monitor", label: "Monitor", icon: PackageSearch },
  { href: "/dane", label: "Encuesta DANE", icon: BarChart3 }
];

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const [theme, setTheme] = useState<"dark" | "light">("dark");

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
  }, [theme]);

  return (
    <div className="app-shell">
      <div className="ambient ambient-a" />
      <div className="ambient ambient-b" />

      <aside className="sidebar">
        <Link className="brand-block" href="/monitor">
          <div className="brand-mark">
            <Boxes size={25} />
          </div>
          <div>
            <div className="brand-name">COLSABOR</div>
            <div className="brand-sub">Inventory Command</div>
          </div>
        </Link>

        <nav className="side-nav">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = pathname === item.href || (pathname === "/" && item.href === "/monitor");
            return (
              <Link className={cn("side-link", active && "active")} href={item.href} key={item.href}>
                <Icon size={18} />
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="side-status">
          <DatabaseZap size={18} />
          <div>
            <div className="status-title">Sistema activo</div>
            <div className="muted">FastAPI + Next.js</div>
          </div>
        </div>
      </aside>

      <div className="main-stage">
        <header className="topbar">
          <div>
            <div className="eyebrow">Live Operations</div>
            <h1>Centro Inteligente de Inventario</h1>
          </div>
          <div className="top-actions">
            <span className="live-pill">
              <span />
              LIVE
            </span>
            <button className="icon-btn" onClick={() => window.location.reload()} type="button">
              <RefreshCw size={17} />
            </button>
            <button
              className="icon-btn"
              onClick={() => setTheme((current) => (current === "dark" ? "light" : "dark"))}
              type="button"
            >
              {theme === "dark" ? <Sun size={17} /> : <Moon size={17} />}
            </button>
          </div>
        </header>
        {children}
      </div>
      <Toaster richColors position="top-right" />
    </div>
  );
}
