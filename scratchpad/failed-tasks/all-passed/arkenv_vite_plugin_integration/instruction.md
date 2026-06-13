# ArkEnv Vite Plugin Integration

## Goal
In the existing Vite project at `/home/user/myproject`, configure the `@arkenv/vite-plugin` so that the build process validates required environment variables at build time and fails fast when they are missing or malformed. The schema MUST require:

- `VITE_API_URL`: a valid URL
- `VITE_FEATURE_FLAG`: a boolean

## Acceptance Criteria
1. Running `vite build` with valid env vars set (e.g. `VITE_API_URL=https://api.example.com VITE_FEATURE_FLAG=true`) MUST exit 0.
2. Running `vite build` WITHOUT `VITE_API_URL` set MUST exit non-zero AND the build's stderr/stdout MUST mention the missing variable `VITE_API_URL`.
3. Running `vite build` with `VITE_API_URL="not a url"` MUST exit non-zero.
4. `vite.config.ts` MUST import and register the `@arkenv/vite-plugin` plugin.

