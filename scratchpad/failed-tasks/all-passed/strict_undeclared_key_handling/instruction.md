# Strict Undeclared-Key Handling with ArkType

## Goal
Define three [ArkType](https://arktype.io/) `2.2.0` schemas at `/home/user/myproject/src/schemas.ts` that demonstrate the three different strategies for handling undeclared object keys.

## Acceptance Criteria
- Project path: `/home/user/myproject`
- Module path: `/home/user/myproject/src/schemas.ts`
- The package `arktype` must be pinned to exactly `2.2.0` in `/home/user/myproject/package.json`.
- The module MUST provide three named exports: `LooseUser`, `RejectUser`, and `DeleteUser`.
- The following behaviors MUST all hold when the module is imported and the schemas are invoked as functions:
  1. `LooseUser({ name: "a", extra: 1 })` MUST return an object where `extra === 1`.
  2. `RejectUser({ name: "a", extra: 1 })` MUST return a `type.errors` instance (validation failure).
  3. `DeleteUser({ name: "a", extra: 1 })` MUST return an object where `"extra" in result === false`.
  4. All three schemas MUST accept `{ name: "a" }` without errors (no `type.errors` returned).
  5. The schemas MUST be exported as named exports `LooseUser`, `RejectUser`, `DeleteUser` from `/home/user/myproject/src/schemas.ts`.

