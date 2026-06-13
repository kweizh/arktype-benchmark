# ArkType: Numeric String Morph with Modulo Constraint

## Background
Build a small validator using ArkType (`arktype@2.2.0`) that parses a numeric string into a number and constrains the parsed number to be even.

## Requirements
- Define an ArkType schema for an object with a single property `score`.
- `score` must accept a numeric string as input, morph it into a number, and then constrain that number so only even integers are allowed.
- Provide a CLI entrypoint that reads a single JSON payload from `argv[2]` and prints the validation result.

## Implementation Hints
- Use ArkType's pipe/morph syntax to chain a string-to-number parser with a numeric divisor constraint.
- Refer to the official docs: https://arktype.io/docs/primitives and https://arktype.io/docs/expressions.

## Acceptance Criteria
- Project path: /home/user/myproject
- Command: `npx tsx validate.ts '<json_input>'`
- On valid input, exit code is `0` and stdout contains a single line with `OK: <validated_json>` where `<validated_json>` is the validated object serialized as compact JSON.
- On invalid input, exit code is `1` and stdout contains a single line starting with `INVALID:`.
- The schema definition for `score` must use the tuple expression `["string.numeric.parse", "|>", "number % 2"]` (the documented ArkType syntax for piping a `string.numeric.parse` morph into a `number % 2` divisor constraint).
- The following inputs must produce the listed outcomes:
  1. `{"score":"42"}` -> `OK: {"score":42}` (the value is a number, not a string)
  2. `{"score":"43"}` -> `INVALID: ...`
  3. `{"score":"abc"}` -> `INVALID: ...`
  4. `{"score":42}` -> `INVALID: ...` (already a number, the morph requires a string input)

