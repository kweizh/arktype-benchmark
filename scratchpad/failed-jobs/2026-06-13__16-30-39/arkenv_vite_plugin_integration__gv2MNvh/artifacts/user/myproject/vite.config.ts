import { defineConfig } from "vite";
import arkenv from "@arkenv/vite-plugin";

export default defineConfig({
  plugins: [
    arkenv({
      VITE_API_URL: "string.url",
      VITE_FEATURE_FLAG: "boolean",
    }),
  ],
});