To align with TypeScript's structural type system, ArkType ignores undeclared keys in objects by default. This can be problematic in secure environments where extra payload fields might lead to mass-assignment vulnerabilities.

You need to define a `SecureProfileSchema` for an object containing `firstName` (string) and `age` (integer number). You must configure this specific schema to strictly reject any extra, undeclared properties passed into it.

**Constraints:**
- You MUST use the `+` syntax (e.g., `"+": "reject"`) within the individual object schema to explicitly reject extra keys.
- Do NOT use the global `onUndeclaredKey` setting in a `configure()` call, as this must be localized to only this specific schema.
- The `age` property must strictly enforce integer validation using ArkType's string expressions.