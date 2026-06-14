# ArkEnv Vite Plugin Build Gate

## Background
Production Vite apps frequently boot with mis-typed or missing client environment variables, then crash deep inside React render. The `@arkenv/vite-plugin` package integrates the `arkenv` validator (built on top of `arktype@2.2.0`) directly into Vite's build pipeline so that an invalid environment halts the build immediately. Your task is to wire this plugin into a minimal Vite + React project so that builds are gated by a strict environment schema.

## Requirements
- Initialize a minimal Vite + React + TypeScript project at `/home/user/myproject` (entry component, HTML, vite config, package.json, tsconfig).
- Configure `vite.config.ts` to use `@arkenv/vite-plugin` with a schema that declares the following client-exposed environment variables:
  - `VITE_API_URL` — must be a syntactically valid URL string.
  - `VITE_FEATURE_FLAGS` — boolean (the plugin / arkenv must coerce the string `"true"`/`"false"`).
  - `VITE_MAX_UPLOAD_MB` — integer between 1 and 1024 inclusive (the plugin / arkenv must coerce the string into an integer).
- The React entry source (`src/main.tsx`) must read `import.meta.env.VITE_API_URL` and use it at least once (for example, render it inside the React tree or store it in a constant that the bundler cannot trivially drop).
- Provide two npm scripts in `package.json`:
  - `build` — runs `vite build`.
  - `validate-env` — a passthrough script that exits with the same status as `vite build` (it may simply invoke the build, or otherwise force the plugin to validate). Either way, it must rely on the Vite plugin doing the validation, not a separate hand-rolled prebuild script.
- Commit a `.env.example` file at the project root with placeholder values for the three variables documenting their expected shape. Do **NOT** create or seed a `.env` file — the implementer/test will supply environment values via real environment variables at build time.
- When the environment is invalid or any required variable is missing, `npm run build` MUST exit non-zero. When the environment is valid, `npm run build` MUST exit zero and produce a Vite build output under `dist/`.

## Implementation Hints
- Use the `@arkenv/vite-plugin` package — do not write your own prebuild validation script and do not call `arkenv()` from application code instead of the plugin.
- Consult the plugin's README / docs at https://arkenv.js.org/docs/vite-plugin for the correct import name and call signature.
- Use `@vitejs/plugin-react` for React support.
- Pick `arkenv` / `arktype` notation that yields a URL string, a coerced boolean, and a ranged integer.
- The plugin reads values via Vite's `loadEnv` mechanism, which also includes `process.env` entries, so supplying values via real environment variables at test time is sufficient — no `.env` file required.

## Acceptance Criteria
- Project path: /home/user/myproject
- Command: `npm run build` (executed from the project root).
- Behavior:
  - With all three variables set to valid values via the process environment, `npm run build` exits with status 0 and produces `/home/user/myproject/dist/index.html`.
  - With `VITE_API_URL` set to a non-URL value (other variables valid), `npm run build` exits non-zero and the combined stdout/stderr contains an arkenv/arktype-style validation error mentioning `VITE_API_URL`.
  - With `VITE_MAX_UPLOAD_MB` set to `0` (other variables valid), `npm run build` exits non-zero.
  - With `VITE_API_URL` and/or `VITE_FEATURE_FLAGS` and/or `VITE_MAX_UPLOAD_MB` unset, `npm run build` exits non-zero.
- Source layout:
  - `/home/user/myproject/vite.config.ts` exists and imports from `@arkenv/vite-plugin`.
  - `/home/user/myproject/src/main.tsx` exists and references `import.meta.env.VITE_API_URL`.
  - `/home/user/myproject/.env.example` exists at the project root.
  - `/home/user/myproject/.env` is NOT committed.
- `package.json` defines both `build` and `validate-env` npm scripts.

