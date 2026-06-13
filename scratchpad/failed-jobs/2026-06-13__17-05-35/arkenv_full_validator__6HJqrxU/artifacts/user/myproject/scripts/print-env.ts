import { env } from "../src/env.js";

const output = {
  HOST: env.HOST,
  PORT: env.PORT,
  DEBUG: env.DEBUG,
  NODE_ENV: env.NODE_ENV,
  ALLOWED_ORIGINS: env.ALLOWED_ORIGINS,
  types: {
    PORT: typeof env.PORT,
    DEBUG: typeof env.DEBUG,
    ALLOWED_ORIGINS_IS_ARRAY: Array.isArray(env.ALLOWED_ORIGINS),
  },
};

console.log(`ENV_JSON=${JSON.stringify(output)}`);
