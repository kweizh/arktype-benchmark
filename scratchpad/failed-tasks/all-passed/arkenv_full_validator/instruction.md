# ArkEnv Full Environment Validator

## Goal
Build a Node.js + TypeScript module at `/home/user/myproject/src/env.ts` that uses `arkenv` (powered by `arktype`) to validate, coerce, and infer types for the following environment variables, then exports a single typed value named `env`:

- `HOST`: an IP address (IPv4 or IPv6) **or** the literal string `localhost`.
- `PORT`: an integer in the inclusive range `1..65535`.
- `DEBUG`: a boolean.
- `NODE_ENV`: one of `development`, `production`, or `test`.
- `ALLOWED_ORIGINS`: a comma-separated list of URL strings parsed into an `Array`.

## Acceptance Criteria

- Project path: `/home/user/myproject`
- `package.json` must declare `"type": "module"` and pin these exact versions:
  - `arkenv@0.12.1`
  - `arktype@2.2.0`
- The module at `/home/user/myproject/src/env.ts` MUST export a named binding `env`.
- Provide a runnable script at `/home/user/myproject/scripts/print-env.ts` that imports the `env` object and prints a single line to stdout:
  - Format: `ENV_JSON=<json>` where `<json> = JSON.stringify({ HOST: env.HOST, PORT: env.PORT, DEBUG: env.DEBUG, NODE_ENV: env.NODE_ENV, ALLOWED_ORIGINS: env.ALLOWED_ORIGINS, types: { PORT: typeof env.PORT, DEBUG: typeof env.DEBUG, ALLOWED_ORIGINS_IS_ARRAY: Array.isArray(env.ALLOWED_ORIGINS) } })`.
- Command: `npx tsx /home/user/myproject/scripts/print-env.ts` (run from `/home/user/myproject`).

The verifier will run that command with controlled environments and enforce ALL of the following criteria verbatim:

1. With all env vars set validly, the module MUST load and `env.PORT` MUST be a `number` (not string).
2. `env.DEBUG` MUST be a real boolean when set to "true".
3. `env.ALLOWED_ORIGINS` MUST be an `Array` of length > 0 when set to "https://a.com,https://b.com".
4. With PORT="not-a-number", import MUST throw at startup.
5. With NODE_ENV="staging" (not in enum), import MUST throw at startup.
6. HOST="localhost" MUST be accepted; HOST="999.999.999.999" MUST be rejected.

