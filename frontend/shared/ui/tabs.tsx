"use client";

import { type ReactNode } from "react";
import { cn } from "@/shared/lib/utils";

export function TabSwitch<T extends string>({
  tabs,
  value,
  onChange
}: {
  tabs: Array<{ value: T; label: string; icon?: ReactNode }>;
  value: T;
  onChange: (value: T) => void;
}) {
  return (
    <div className="tab-switch">
      {tabs.map((tab) => (
        <button
          className={cn("tab-button", value === tab.value && "active")}
          key={tab.value}
          onClick={() => onChange(tab.value)}
          type="button"
        >
          {tab.icon}
          {tab.label}
        </button>
      ))}
    </div>
  );
}
