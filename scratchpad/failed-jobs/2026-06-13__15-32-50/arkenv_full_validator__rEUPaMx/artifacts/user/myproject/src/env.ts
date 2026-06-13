import { createEnv } from "arkenv";

export const env = createEnv({
  HOST: "string.ip | 'localhost'",
  PORT: "1 <= number.integer <= 65535",
  DEBUG: "boolean",
  NODE_ENV: "'development' | 'production' | 'test'",
  ALLOWED_ORIGINS: "string.url[] > 0"
});
