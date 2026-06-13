# ArkType Global Config Import Ordering

## Goal
In `/home/user/myproject`, demonstrate ArkType's global-config import-order friction point.

## Acceptance Criteria
- Project path: `/home/user/myproject`
- Running `tsx index.ts` MUST validate `{ x: NaN }` successfully (because `numberAllowsNaN: true`).
- Running `tsx broken.ts` MUST reject `{ x: NaN }` (config not applied due to ordering).
- Both scripts MUST use the same schema definition (e.g., imported from a shared module).
- The `config.ts` file MUST contain `import { configure } from "arktype/config"` and a `configure({...})` call.

