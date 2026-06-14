import arkenvVitePlugin from "@arkenv/vite-plugin";
import reactPlugin from "@vitejs/plugin-react";
import { type } from "arkenv";
import { defineConfig } from "vite";

export const Env = type({
  VITE_API_URL: "string.url",
  VITE_FEATURE_FLAGS: "boolean",
  VITE_MAX_UPLOAD_MB: "1<=number.integer<=1024",
});

export default defineConfig({
  plugins: [reactPlugin(), arkenvVitePlugin(Env)],
});
