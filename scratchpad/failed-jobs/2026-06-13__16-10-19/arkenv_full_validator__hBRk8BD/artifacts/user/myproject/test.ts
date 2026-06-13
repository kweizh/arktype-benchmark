import arkenv from "arkenv";

const env = arkenv({
  HOST: "string.ip | 'localhost'",
  PORT: "number.port",
  DEBUG: "boolean",
  NODE_ENV: "'development' | 'production' | 'test'",
  ALLOWED_ORIGINS: "string.url[]"
});

console.log(env);
