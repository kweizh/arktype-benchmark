import arkenv from "arkenv";

export const env = arkenv({
  HOST: "string.ip | 'localhost'",
  PORT: "number.port",
  DEBUG: "boolean",
  NODE_ENV: "'development' | 'production' | 'test'",
  ALLOWED_ORIGINS: "string.url[]"
});
