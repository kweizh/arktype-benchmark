Combining multiple morphs in overlapping union branches can trigger a "Union Morphs ParseError" due to non-deterministic transformations. ArkType's `match` API utilizes set theory to skip unmatched branches safely.

You need to implement a `processResponse` handler using the `match` API to safely discriminate between an API response state. It must handle a success state matching an object with `{ status: "'success'", data: "unknown" }` and an error state matching `{ status: "'error'", message: "string" }`.

**Constraints:**
- You MUST strictly use the `match` function from ArkType.
- You MUST include a `"default"` fallback case that throws an error or returns `"assert"` if the input matches neither expected state.
- Do NOT use standard `type().or()` expressions, to ensure you avoid the overlapping union morphs friction point.