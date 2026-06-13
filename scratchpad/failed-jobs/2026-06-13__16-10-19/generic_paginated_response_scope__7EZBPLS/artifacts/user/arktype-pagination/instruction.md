# Generic Paginated Response Schema (ArkType)

## Goal
Build an ArkType-based TypeScript project at `/home/user/arktype-pagination` that defines a generic paginated-response envelope `Page<T>` inside a `scope({...})` and uses it to validate pages of `User` and `Product`.

## Acceptance Criteria
- Project path: `/home/user/arktype-pagination`
- Library: `arktype@2.2.0` (already installed)
- Command: `npx tsx validate.ts <SchemaName>`
  - Reads a JSON document from stdin.
  - On a successful `.assert(...)`: exit code `0` and print `OK` to stdout.
  - On a thrown `TraversalError`: exit code `1` and print the error message to stderr.
  - Supported `<SchemaName>` values: `PageOfUser`, `PageOfProduct`.
- Verbatim test criteria (all MUST hold):
  1. `PageOfUser.assert({ items: [{...valid user}], total: 1, cursor: null })` MUST succeed.
  2. `PageOfUser.assert({ items: [{...invalid user}], total: 1, cursor: null })` MUST throw.
  3. `PageOfProduct.assert(...)` MUST validate Product items.
  4. Passing a User object into `PageOfProduct` MUST be rejected.
  5. The generic MUST be defined as `"Page<T>": {...}` (or whichever syntax the docs verify) inside the `scope({...})` definition.
