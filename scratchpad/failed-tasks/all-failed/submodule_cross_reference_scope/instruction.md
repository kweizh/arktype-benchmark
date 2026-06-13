# ArkType Scope with Cross-Referenced Submodules

## Goal
Using `arktype@2.2.0`, build a TypeScript project at `/home/user/myproject` whose `src/scope.ts` file default-exports an ArkType `Module` produced by a single `scope({...}).export()` call. The scope must declare two submodules using dot-notation keys — `db.config` and `http.server` — where the `http.server` schema references the `db.config` alias from within the same scope.

## Acceptance Criteria
- Project path: /home/user/myproject
- Command: `npx tsx src/scope.ts` exits with code 0.
- `src/scope.ts` default-exports the runtime `Module` returned by `.export()`.
- `package.json` pins `arktype` to exactly `2.2.0`.
- The following test criteria are enforced verbatim by the verifier:
  1. `module.db.config.assert({...})` MUST validate a config payload.
  2. `module.http.server.assert({...})` MUST validate when given a payload that contains a nested `db.config`-shaped property.
  3. Cross-submodule references MUST resolve (verified by validating a payload that exercises the reference).
  4. Invalid `db.config` payloads passed via the server schema MUST be rejected.
  5. The scope MUST be defined in a single `scope({...}).export()` call with at least two submodule keys using dot notation.

