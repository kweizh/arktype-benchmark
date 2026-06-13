# Bidirectional ArkType ↔ JSON Schema Round Trip

## Goal
Implement a bidirectional schema converter using ArkType's built-in `toJsonSchema()` method together with the `@ark/json-schema` package so that any ArkType schema can be exported to JSON Schema draft-2020-12, re-parsed back into an ArkType `Type`, and shown to preserve semantic equivalence against a corpus of payloads.

## Project path
- `/home/user/myproject`

## Command
- Command: `npm run check`
- Input: stdin receives a JSON document with shape `{ "schema": <ArkType-definition>, "corpus": [<any>, ...] }`. `<ArkType-definition>` is the JSON-serializable definition that the project must accept and feed into `type(...)`.
- Output: stdout MUST be a single JSON document with the shape `{ "jsonSchema": <object>, "agreements": [ { "index": <int>, "originalAccept": <bool>, "roundTrippedAccept": <bool>, "agree": <bool> }, ... ], "allAgree": <bool> }`. The process MUST exit with code `0` when `allAgree` is `true`.

## Acceptance criteria
1. The exported JSON Schema MUST contain the `$schema` field for draft-2020-12.
2. After round-tripping a schema with nested objects and string keywords (e.g., `string.email`, `number.integer`), the re-parsed ArkType schema MUST accept the same valid corpus and reject the same invalid corpus as the original.
3. The implementation MUST export `roundTrip(schema: Type) => Type`.
4. For each payload in a provided JSON corpus, `original(payload)` and `roundTripped(payload)` MUST agree on (accept/reject) status.

## Additional constraints
- Use `arktype@2.2.0` and the `@ark/json-schema` package (already declared in `package.json`).
- The module file `src/roundTrip.ts` MUST export at least the named symbol `roundTrip` with the signature `roundTrip(schema: Type) => Type`. The same module MUST also expose a named export `exportJsonSchema(schema: Type) => object` that returns the JSON Schema document (containing the `$schema` field) used as the intermediate during the round trip.
- `npm run check` MUST be wired so that it reads stdin and writes the result JSON to stdout as specified above.

