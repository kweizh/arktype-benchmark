# Elysia + ArkType Standard Schema Endpoint

## Goal
Build an Elysia server that uses an ArkType schema (via the Standard Schema interface) to validate the body of a `POST /user` endpoint.

## Acceptance Criteria
- Project path: /home/user/myproject
- Start command: bun run start
- Port: 3000
- API Endpoint:
  - `POST /user` with JSON body validated by an ArkType schema with shape `{ username: alphanumeric string of length 3-20, email: string.email, age: integer >= 18 }`.
  - On a valid body the endpoint returns HTTP 200 with a JSON response containing the validated `username` (e.g. `{ "username": <username>, ... }`).
  - On an invalid body the endpoint returns HTTP 422.
- Validation rules enforced through ArkType:
  1. `POST /user` with a valid body returns HTTP 200 and JSON containing the validated `username`.
  2. `POST /user` with `age: 17` returns HTTP 422.
  3. `POST /user` with `email: "not-an-email"` returns HTTP 422.
  4. `POST /user` with extra unknown fields MUST still succeed (ArkType ignores undeclared keys by default).
  5. The body validator MUST be a `type({...})` ArkType instance passed directly to Elysia's `body:` option (NOT wrapped in `t.Object`).
  6. The server MUST be reachable on `http://localhost:3000` during the test run.

