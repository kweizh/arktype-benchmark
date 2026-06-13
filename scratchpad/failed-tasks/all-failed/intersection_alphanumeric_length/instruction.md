# Username Validator with ArkType

## Goal
At `/home/user/myproject`, build a TypeScript CLI that validates a username against an ArkType `2.2.0` schema.

## Acceptance Criteria
- Project path: `/home/user/myproject`.
- Command: `npx tsx src/validate.ts <username>`.
- The schema MUST be defined as a SINGLE ArkType expression chain (no manual JS regex `.test(...)` calls or hand-written validation outside of `.narrow(...)`).
- The package `arktype` MUST be pinned to version `2.2.0` in `package.json`.
- The following cases MUST hold:
  - `npx tsx src/validate.ts alice123` → prints exactly `valid`, exit code `0`.
  - `npx tsx src/validate.ts al` (too short) → prints exactly `invalid`, exit code `1`.
  - `npx tsx src/validate.ts aaaaaaaaaaaaaaaaaaaa` (20 `a` characters, too long) → prints exactly `invalid`, exit code `1`.
  - `npx tsx src/validate.ts 'alice!'` (non-alphanumeric) → prints exactly `invalid`, exit code `1`.
  - `npx tsx src/validate.ts 1alice` (does not start with a letter) → prints exactly `invalid`, exit code `1`.
