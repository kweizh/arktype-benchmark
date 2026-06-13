# Redacted Password Error Message

## Goal
In the existing ArkType project at `/home/user/myproject`, define a password schema that validates a minimum length of 8 characters, and ensure that whenever validation fails the resulting ArkType error message NEVER contains the actual password value. The actual value must be redacted as the literal string `<redacted>`.

## Acceptance Criteria
- Project path: `/home/user/myproject`
- arktype version: `2.2.0` (already installed in `package.json`; do not change).
- The schema must be exported as the named export `PasswordSchema` from `/home/user/myproject/src/schema.ts` (an ArkType `Type` instance accepting a `string`).
- A password whose length is strictly less than `8` (e.g. `"mySecret"`) MUST cause the schema to produce a validation error (an `ArkErrors` result; not a successful parse).
- The resulting validation error message string MUST contain the literal substring `<redacted>`.
- The resulting validation error message string MUST NOT contain the literal value of the invalid password that was supplied (e.g. the substring `mySecret` must not appear anywhere in the error message).
- A password whose length is greater than or equal to `8` (e.g. `"longenoughpw"`) MUST validate successfully (no `ArkErrors`).

