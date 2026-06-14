import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import arkenv from "@arkenv/vite-plugin";

export default defineConfig({
  plugins: [
    react(),
    arkenv({
      VITE_API_URL: "string.url",
      VITE_FEATURE_FLAGS: "boolean",
      VITE_MAX_UPLOAD_MB: "1 <= number.integer <= 1024",
    }),
  ],
});