# Strict Undeclared Keys Modes (ArkType)

## Background
By default, `arktype@2.2.0` mirrors TypeScript's structural typing and silently accepts extra (undeclared) properties on objects. For real-world inputs such as JSON request bodies, two stricter behaviors are often required: rejecting payloads that contain unknown keys, or stripping them from the validated output. ArkType exposes both via the `+` syntax inside object definitions.

Your task is to build a TypeScript CLI under `/home/user/myproject` that demonstrates all three undeclared-key behaviors against the same logical schema.

## Requirements
- Define **one logical user shape**: `{ id: 'string.uuid', name: 'string', email: 'string.email' }`.
- Build **three distinct ArkType `Type` instances** from this shape, each with a different undeclared-key strategy:
  1. an `ignoreSchema` that uses ArkType's default behavior (extras are kept on output).
  2. a `rejectSchema` that REJECTS objects containing any undeclared key.
  3. a `deleteSchema` that DELETES undeclared keys from the validated output.
- Implement a CLI that reads a single JSON document from stdin with shape `{"mode": "ignore" | "reject" | "delete", "payload": <object>}` and dispatches the payload to the matching schema.
- The CLI must always exit with status code 0. Success or failure is reported through stdout.

## Implementation Hints
- Both per-schema syntax and a global configuration setting can control undeclared-key behavior — for this task, the per-schema control must be expressed inside the object definitions themselves so that the three schemas have different runtime behavior in a single process.
- Read the relevant section of the ArkType objects documentation if you are unsure which value to pass.
- A successful validation should print exactly two lines: the literal `VALID` on the first line, followed by `JSON.stringify(validated)` on the second line. The validated object is the value returned by the schema (which for the `delete` strategy will not contain the stripped keys).
- A failed validation should print exactly one line starting with `INVALID:` followed by a human-readable error message. The error message must mention the offending undeclared key by name when that is the cause.
- An unknown `mode` should also be reported via `INVALID:`.

## Acceptance Criteria
- Project path: /home/user/myproject
- Command: `npx tsx cli.ts`
- Input: a single JSON document on stdin of the form `{"mode": "ignore" | "reject" | "delete", "payload": <object>}`.
- Output (stdout):
  - On success: line 1 is exactly `VALID`; line 2 is the JSON-stringified validated payload returned by ArkType.
  - On failure: a single line beginning with `INVALID:` followed by an error message.
- The CLI MUST exit with code 0 in all cases (success and failure).
- `arktype@2.2.0` and `tsx` are preinstalled. `tsconfig.json` is preconfigured with `module: NodeNext` and `moduleResolution: NodeNext`.

