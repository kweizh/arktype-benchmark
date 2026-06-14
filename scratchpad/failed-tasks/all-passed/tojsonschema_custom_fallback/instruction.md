# JSON Schema Export with Custom Fallbacks (ArkType)

## Background
You are building a small JSON Schema export module that converts an ArkType schema for a recursive `User` profile into a draft-07 JSON Schema document. The source ArkType schema deliberately uses features that have no native JSON Schema equivalent (a transformation/morph and a custom narrow predicate), so the conversion has to be configured with fallback handlers that produce sensible, lossy representations instead of throwing.

## Requirements
- Implement the project under `/home/user/myproject`. `arktype@2.2.0` and `tsx` are already installed.
- Define a single ArkType `Type` named `User` (built with `scope(...).export()` so it can be recursive) with at least these fields:
  - `id`: an unconstrained UUID string.
  - `username`: a string carrying a CUSTOM narrow / predicate that requires the value to be alphanumeric AND not appear in a reserved-words list (the list must contain at least `"admin"`, `"root"`, and `"system"`).
  - `score`: a value produced by a MORPH that parses a numeric string and yields a number (e.g. ArkType's `string.numeric.parse` keyword).
  - `friends`: an array of nested `User` instances (recursive self-reference).
- Convert the schema to a draft-07 JSON Schema using ArkType's `toJsonSchema()` API with a `fallback` configuration that:
  - For ANY morph node, returns a JSON Schema object equivalent to `{ "type": "string", "format": "morph-redacted", "description": "morph dropped" }` (i.e. the morphed input/output is collapsed to a redacted string placeholder).
  - For ANY predicate / narrow node, returns the existing base JSON Schema with an extra `x-arktype-fallback: "predicate"` annotation merged in (so the constraint is dropped but the fact that a predicate existed is recorded).
- Provide a CLI entrypoint `cli.ts` at the project root that takes NO stdin, writes the resulting JSON Schema to `out/user.schema.json` (creating `out/` if necessary), and prints exactly `WROTE <path>` to stdout on a single line, where `<path>` is the absolute path of the written file. The CLI MUST exit with code `0`.
- The validator module under `src/` (the file that builds the `Type` and calls `toJsonSchema(...)`) MUST contain the literal substrings `toJsonSchema(` and `fallback`.

## Implementation Hints
- Consult the official ArkType documentation (configuration / `toJsonSchema` and the 2.2 release notes) for the exact option names, fallback context shape, and handler return types BEFORE writing code. Do not guess the API.
- Recursive types in ArkType require a named-scope construction so that self-references (`friends`) resolve.
- The morph fallback handler must return a JSON Schema object directly; the predicate fallback handler should merge its annotation onto the base schema rather than replacing it.

## Acceptance Criteria
- Project path: /home/user/myproject
- Command: `npx --no-install tsx cli.ts` (run from `/home/user/myproject`)
- Input: none (the CLI does not read stdin).
- Output: on success, stdout contains exactly one line of the form `WROTE <absolute-path>` where `<absolute-path>` resolves to `/home/user/myproject/out/user.schema.json`. The CLI exits with code `0`.
- Artifact: a JSON file at `/home/user/myproject/out/user.schema.json` whose contents are a valid JSON Schema document with:
  - `"$schema": "http://json-schema.org/draft-07/schema#"` at the top level.
  - At least one node anywhere in the document that has `"format": "morph-redacted"` (the morph fallback for the `score` field).
  - At least one node anywhere in the document carrying `"x-arktype-fallback": "predicate"` (the narrow fallback for `username`).
  - At least one `"$ref"` string anywhere in the document, referencing the recursive `User` definition (for the `friends` array).
- Source-shape: the file under `/home/user/myproject/src/` that defines the `User` type and exports the JSON Schema MUST contain both of the literal substrings `toJsonSchema(` and `fallback`.

