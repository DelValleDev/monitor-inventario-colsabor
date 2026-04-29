import { expect, test } from "@playwright/test";

test("loads the premium shell", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("COLSABOR")).toBeVisible();
  await expect(page.getByRole("link", { name: "Monitor" })).toBeVisible();
});

test("loads DANE route and keeps saldos accessible", async ({ page }) => {
  await page.goto("/dane");
  await expect(page.getByRole("link", { name: "Encuesta DANE" })).toBeVisible();
});
