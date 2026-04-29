import { describe, expect, it } from "vitest";
import { asNumber, formatNumber, formatPercent } from "@/shared/lib/format";

describe("format helpers", () => {
  it("parses numeric display strings", () => {
    expect(asNumber("$ 1,234")).toBe(1234);
    expect(asNumber("9.5%")).toBe(9.5);
  });

  it("formats numbers in es-CO style", () => {
    expect(formatNumber(1234.5)).toContain("1.234");
    expect(formatPercent(9.55)).toContain("%");
  });
});
