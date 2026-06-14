# SKU Catalog Validator (ArkType)

## Background
A wholesale platform receives JSON catalog payloads from vendors and needs to enforce a strict SKU format and uniqueness invariant before persisting the catalog. Build a TypeScript validator under `/home/user/myproject` using `arktype@2.2.0` that combines a schema-level regex pattern for individual SKUs with a structural uniqueness check across the whole list.

## Requirements
- Validate a catalog object with the following shape:
  - `vendorId`: a UUID string.
  - `skus`: an array of SKU strings, each matching the pattern `^[A-Z]{2}-\d{4}-[a-z]{3}$` (e.g. `AB-1234-xyz`).
  - The `skus` array MUST contain at least 1 and at most 200 elements.
  - All SKU values in `skus` MUST be unique (case-sensitive).
- The SKU pattern MUST be expressed inside the ArkType schema definition. Do NOT post-filter the validated data with manual `.test()` or `.match()` calls.
- Uniqueness MUST be enforced through an ArkType narrow predicate that yields a structured ArkError whose path includes `skus`.
- Expose the result through a CLI that reads a single JSON catalog payload from stdin.

## Implementation Hints
- The TypeScript project under `/home/user/myproject` is preconfigured with `arktype@2.2.0`, `tsx`, and a `tsconfig.json` using `module: NodeNext`. Consult the ArkType documentation for the exact syntax of regex-based string constraints and structured narrow predicates.
- The implementation lives in `src/validator.ts` and a CLI entrypoint at `cli.ts`.

## Acceptance Criteria
- Project path: /home/user/myproject
- Command: `npx tsx cli.ts`
- Input: a single JSON catalog payload supplied via stdin.
- Output (stdout):
  - If the payload validates: print exactly the line `VALID` followed by a newline and the JSON-stringified validated catalog on the next line.
  - If the payload is rejected: print exactly one line starting with `INVALID:` followed by a space and any error description.
- The CLI MUST exit with code 0 for both valid and invalid inputs (stdout decides the outcome).
- The TypeScript validator module file `src/validator.ts` MUST encode the SKU regex constraint at the schema level. No manual `.test()` / `.match()` filtering of validated data is allowed.
- The TypeScript validator module file `src/validator.ts` MUST express SKU uniqueness via an ArkType narrow predicate.
- `arktype@2.2.0` and `tsx` are preinstalled in `/home/user/myproject` and `tsconfig.json` is preconfigured with `module: NodeNext` and `moduleResolution: NodeNext`.

