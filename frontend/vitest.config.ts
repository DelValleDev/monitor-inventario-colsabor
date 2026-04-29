import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": new URL(".", import.meta.url).pathname
    }
  },
  test: {
    environment: "jsdom",
    exclude: ["**/node_modules/**", "**/.next/**", "**/tests/e2e/**"],
    globals: true,
    setupFiles: ["./tests/setup.ts"]
  }
});
