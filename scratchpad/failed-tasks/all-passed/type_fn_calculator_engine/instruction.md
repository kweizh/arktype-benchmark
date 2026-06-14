# Calculator Engine with `type.fn` (ArkType)

## Background
Build a small calculator engine in TypeScript under `/home/user/myproject` that uses `arktype@2.2.0`'s `type.fn` to validate every function boundary at runtime. The engine exposes five binary arithmetic operations and a single dispatcher, and is driven by a stdin/stdout CLI.

## Requirements
- Implement five binary operations: `add`, `subtract`, `multiply`, `divide`, and `modulo`. Each accepts two `number` arguments and returns a `number`.
- `divide` MUST reject any divisor equal to `0` at its `type.fn` boundary.
- `modulo` MUST reject any divisor that is not a non-zero integer (e.g., `2.5` or `0` must be rejected) at its `type.fn` boundary.
- Implement a dispatcher `compute(op, a, b)` that is itself defined via `type.fn`. The first parameter MUST be constrained at the `type.fn` boundary to the literal union of the five operation names; `a` and `b` MUST be constrained to `number`. The dispatcher returns a `number` and routes to the correct underlying operation.
- Provide a CLI entrypoint that reads ONE JSON line from stdin of shape `{"op": <operation-name>, "a": <number>, "b": <number>}`, calls the dispatcher, and prints the result.
- All validation rejection MUST come from the `type.fn` wrappers (i.e. the `TraversalError` thrown by ArkType). The CLI MUST NOT perform manual `if/typeof` precondition checks that pre-empt the `type.fn` boundary; the only allowed manual error handling is a single `try/catch` around the dispatch call to translate the thrown `TraversalError` into the failure line.

## Implementation Hints
- Recall that in `arktype@2.2.0`, `type.fn` takes parameter definitions followed by a `":"` separator and a return type definition, and returns a higher-order callable that wraps an implementation lambda.
- Constraints like "non-zero" or "non-zero integer" can be expressed entirely inside an ArkType definition string using primitive keywords, ranges, unions, and intersections — no narrows or manual guards required.
- ArkType throws a `TraversalError` from a `type.fn` call when an argument or the return value fails validation; the thrown object's `message` is suitable for printing verbatim.
- The project already has `arktype@2.2.0`, `tsx`, and a `tsconfig.json` with `module: NodeNext` preinstalled. Use `npx tsx` to execute TypeScript directly.

## Acceptance Criteria
- Project path: /home/user/myproject
- Command: `npx tsx cli.ts`
- Input: a single JSON object supplied via stdin with fields `op` (string), `a` (number), and `b` (number).
- Output (stdout):
  - On success, print exactly one line of the form `OK <result>`, where `<result>` is the numeric output of the dispatcher rendered with JavaScript's default `String(number)` representation (e.g. `OK 5`, `OK 2.5`, `OK -3`).
  - On any `TraversalError` thrown by a `type.fn` wrapper (invalid op, non-numeric argument, divide-by-zero, modulo by a non-integer or zero divisor, etc.), print exactly one line of the form `ERR <message>`, where `<message>` is the `message` property of the thrown error.
- The CLI MUST exit with status code 0 regardless of whether the input is accepted or rejected; the `OK`/`ERR` prefix is the sole success signal.
- The TypeScript source files MUST live under `/home/user/myproject` and the entrypoint MUST be `/home/user/myproject/cli.ts`.

