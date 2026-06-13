# Cyclic Organizational Chart Schema with ArkType `scope`

## Goal
At `/home/user/myproject/src/index.ts`, build a cyclic `Member` schema and a `findRoot` helper using ArkType `scope`. Export `Member` and `findRoot` as named exports from `src/index.ts`. Run with `npx tsx /home/user/myproject/src/index.ts`.

## Acceptance Criteria
1. A valid 3-level org tree with UUIDs MUST validate via `Member.assert(...)`.
2. An invalid UUID in any node MUST cause `.assert(...)` to throw.
3. A `subordinates` value that is not an array MUST be rejected.
4. `findRoot` MUST return the top-level Member (one without a `manager`).
5. The schema MUST be created with `scope({ Member: {...} }).export()`.
6. Both `manager` and `subordinates` properties MUST be defined with optional-key syntax (e.g., `"manager?"`).
