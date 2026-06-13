import arkenv from "arkenv";

export const env = arkenv({
  HOST: "string.ip | 'localhost'",
  PORT: "1 <= number.integer <= 65535",
  DEBUG: "boolean",
  NODE_ENV: "'development' | 'production' | 'test'",
  ALLOWED_ORIGINS: "string[]",
});
