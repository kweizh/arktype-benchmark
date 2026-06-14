# Generic Paginated Response Validator (ArkType Scope)

## Goal
Build a TypeScript module under `/home/user/myproject` that validates paginated API responses for two resource kinds using `arktype@2.2.0`. The schema MUST be built with `scope(...).export()` and MUST declare a single generic page wrapper named `Page<T>` that is then instantiated for both `User` and `Post` payloads.

## Domain Schema
The generic `Page<T>` wrapper describes a page envelope around any item kind `T`:

- `items`: an array of `T` values.
- `total`: integer, `>= 0` (total number of records across all pages).
- `page`: integer, `>= 1` (current page, 1-indexed).
- `perPage`: integer in the closed interval `[1, 100]`.
- `hasNext`: boolean.

The two underlying item kinds are:

- `User`:
  - `id`: UUID string.
  - `name`: string, length in `[1, 50]`.
- `Post`:
  - `id`: UUID string.
  - `title`: string, length in `[1, 120]`.
  - `authorId`: UUID string.

The scope export MUST expose ready-to-use `Page<User>` and `Page<Post>` instantiations.

## Test Criteria
1. A well-formed `Page<User>` payload MUST validate successfully and the validated object MUST be echoed back as JSON.
2. A well-formed `Page<Post>` payload MUST validate successfully and the validated object MUST be echoed back as JSON.
3. A `Page<User>` payload whose first `items[0]` is malformed (e.g. `id` is not a UUID, or `name` is empty) MUST be rejected.
4. A `Page<User>` (or `Page<Post>`) payload whose `perPage` is outside the `[1, 100]` range MUST be rejected.
5. A payload whose `hasNext` is not a boolean (e.g. the string `"true"`) MUST be rejected.
6. A payload whose `total` is a negative integer MUST be rejected.
7. The validator source MUST construct the schema using ArkType's `scope` API and MUST declare a generic alias (i.e. an alias whose name contains an angle-bracketed type parameter such as `Page<T>` or `Page<t>`).

## Acceptance Criteria
- Project path: `/home/user/myproject`
- Command: `npx tsx cli.ts`
- Input: a single JSON object delivered via stdin of shape `{"kind": "User" | "Post", "page": <PageObject>}`.
- Output (stdout):
  - If validation succeeds: print exactly the line `VALID` followed by a newline and the JSON-stringified validated page object on the next line.
  - If validation fails (including unknown `kind`): print exactly one line starting with `INVALID:` followed by a space and an error description.
- The CLI MUST exit with code 0 regardless of the validation outcome (stdout decides the outcome).
- The TypeScript module file `src/validator.ts` MUST export a `validatePage(kind: "User" | "Post", page: unknown)` function that returns the validated page or throws via ArkType's assertion API.
- The schema MUST be constructed via `scope({...}).export()`. Inline single `type({...})` definitions of the page envelope are NOT acceptable.
- The scope MUST contain a generic declaration for the `Page` envelope (e.g. an alias key like `"Page<T>"`). Defining `Page<User>` and `Page<Post>` by duplicating the envelope per kind is NOT acceptable.
- `arktype@2.2.0` and `tsx` are preinstalled. `tsconfig.json` is preconfigured with `module: NodeNext` and `moduleResolution: NodeNext`.

