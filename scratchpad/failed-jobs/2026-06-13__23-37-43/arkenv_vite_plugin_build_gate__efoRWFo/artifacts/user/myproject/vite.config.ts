import arkenvPlugin from "@arkenv/vite-plugin";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export const Env = {
  VITE_API_URL: "string.url",
  VITE_FEATURE_FLAGS: "boolean",
  VITE_MAX_UPLOAD_MB: "1 <= number.integer <= 1024",
} as const;

export default defineConfig({
  plugins: [react(), arkenvPlugin(Env)],
});
