# Validated Function Pipeline with ArkType `type.fn`

## Goal
In the pre-initialized TypeScript project at `/home/user/myproject`, implement and export two runtime-validated functions, `applyTax` and `formatInvoice`, defined with ArkType's `type.fn` API (arktype@2.2.0), then build the project so the compiled module is loadable from Node.

## Acceptance Criteria
- Project path: `/home/user/myproject`
- Build command: `npm run build`
- Compiled entrypoint: `/home/user/myproject/dist/pipeline.js`
- The compiled module MUST export two named functions, `applyTax` and `formatInvoice`.
- Both functions MUST be defined via the `type.fn(... , ":", returnType)((...) => ...)` signature.
- `applyTax(100)` MUST return `110` (using the default tax rate of `0.1`).
- `applyTax(100, 0.2)` MUST return `120`.
- `applyTax("100" as any, 0.1)` MUST throw a `TraversalError` whose message references the offending parameter position (e.g., `[0]`).
- `formatInvoice([10, 20, 30])` MUST return `{ total: 60, count: 3 }`.
- `formatInvoice([10, 20, 30], 0.5)` MUST return `{ total: 30, count: 3 }`.
- `dependencies.arktype` in `package.json` MUST remain pinned to `"2.2.0"`.
