# ArkType Evaluation Dataset Research & Benchmark Report

## 1. Library Overview

### Description
[ArkType](https://arktype.io/) is "TypeScript's 1:1 validator," optimized from editor to runtime. It is a highly performant, type-level schema validation library that parses complex TypeScript-like string definitions (e.g., `"string | number[]"`, `"email"`, `"string.numeric.parse"`) directly in TypeScript's type system. It provides instant, type-level autocomplete and diagnostics directly in the editor as you type, matching runtime validation behavior exactly without requiring any IDE plugins, custom language servers, or build-step compilers. At runtime, ArkType compiles highly optimized JIT-compiled validator functions that are up to 100x faster than Zod.

### Ecosystem Role
ArkType serves as a high-performance runtime type-safety boundary in modern TypeScript applications. It implements the [Standard Schema](https://standardschema.dev) specification, making it natively compatible with popular libraries like tRPC, Elysia, and Mastra.
Key ecosystem companions include:
*   **ArkEnv (`ark.env` / `arkenv`)**: A tiny, typesafe environment variable validator that utilizes ArkType's notation to validate, coerce, and type-infer `process.env` and Vite environment variables.
*   **Vite Plugin (`@arkenv/vite-plugin`)**: Integrates environment variable validation into the Vite build pipeline, halting builds immediately if validation fails.
*   **@arktype/attest**: A specialized type-level testing framework built by the ArkType team to make assertions about compile-time types and runtime behavior simultaneously.

### Project Setup
ArkType requires zero build steps or plugins. To initialize a non-interactive project setup:

1.  **Initialize a Node.js project & install dependencies**:
    ```bash
    mkdir arktype-project && cd arktype-project
    npm init -y
    npm install arktype@2.2.0
    npm install -D typescript @types/node
    ```

2.  **Configure `tsconfig.json`**:
    To get full type-level inference and diagnostics, configure TypeScript with modern module resolution and strict settings.
    ```json
    {
      "compilerOptions": {
        "target": "ES2022",
        "module": "NodeNext",
        "moduleResolution": "NodeNext",
        "strict": true,
        "exactOptionalPropertyTypes": true,
        "esModuleInterop": true,
        "skipLibCheck": true,
        "forceConsistentCasingInFileNames": true
      }
    }
    ```

3.  **Create Global Config (Optional)**:
    If customizing built-in keywords globally, import `"arktype/config"` in a separate file (e.g., `config.ts`) before any `"arktype"` imports to ensure the configurations are applied before keywords are compiled:
    ```typescript
    // config.ts
    import { configure } from "arktype/config"
    configure({
      exactOptionalPropertyTypes: false,
      numberAllowsNaN: true
    })
    ```

---

## 2. Core Primitives & APIs

### Pinned Library Versions
*   `arktype`: **`2.2.0`** (Released May/June 2026)
*   `@arktype/attest`: **`0.56.0`**
*   `arkenv`: **`0.12.1`**

### API Reference Table

| Concept/API | Documentation Link | Description |
| :--- | :--- | :--- |
| `type` | [ArkType Primitives](https://arktype.io/docs/primitives) | Main entrypoint for defining schemas from string expressions, objects, or arrays. |
| `scope` | [ArkType Scopes](https://arktype.io/docs/scopes) | Defines resolution spaces for custom aliases, generics, submodules, and cyclic types. |
| `match` | [ArkType Match](https://arktype.io/docs/match) | Pattern matching API mapping string-embedded types to handler functions. |
| `type.fn` | [ArkType Expressions - fn](https://arktype.io/docs/expressions#fn) | Defines runtime-validated functions with typed parameters and return values. |
| `type.declare` | [ArkType Declare](https://arktype.io/docs/declare) | Forces an ArkType schema to conform to a pre-existing compile-time TypeScript interface. |
| `Type.assert(data)` | [ArkType Traversal API](https://arktype.io/docs/traversal-api) | Validates input, throwing a structured `TraversalError` if validation fails. |
| `Type.allows(data)` | [ArkType Traversal API](https://arktype.io/docs/traversal-api) | Type-guard function returning a boolean indicating if validation succeeded. |
| `toJsonSchema()` | [ArkType Configuration](https://arktype.io/docs/configuration#tojsonschema) | Converts an ArkType schema into a JSON Schema draft-2020-12 or draft-07 representation. |
| `@ark/json-schema` | [ArkType Blog 2.2](https://arktype.io/docs/blog/2.2) | Bidirectional JSON Schema parsing package to load JSON Schemas back into ArkType. |
| `attest` | [ArkType Attest](https://github.com/arktypeio/arktype/tree/main/ark/attest) | Type-level testing library asserting static types and runtime outcomes simultaneously. |

---

### Detailed Concept Explanations & Code Snippets

#### 1. Type Validation, Morphs, and Pipes
The `type` function parses string-embedded definitions, object literals, and array structures into a runtime `Type` instance. Morphs represent data transformations (e.g., parsing a string to a Date). The `to` operator (or `|>`) pipes the output of one validation step into another.

```typescript
import { type } from "arktype"

// Define a schema with built-in keywords, range constraints, and a morph pipe
const UserSchema = type({
  id: "string.uuid",                             // Built-in keyword
  username: "string.alphanumeric & 3 <= length <= 20", // Intersected string constraints
  email: "string.email",
  // Parse a numeric string (e.g., "123") and pipe it into an even-number constraint
  score: ["string.numeric.parse", "|>", "number % 2 === 0"],
  // Optional property that defaults to "guest" if omitted
  role: ["'admin' | 'user' | 'guest'", "=", "user"]
})

// Type inference
type User = typeof UserSchema.infer
/* Inferred as:
   {
     id: string;
     username: string;
     email: string;
     score: number;
     role: "admin" | "user" | "guest";
   }
*/

// Usage 1: Direct Invocation (Returns output or ArkErrors)
const result = UserSchema({
  id: "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  username: "alice123",
  email: "alice@example.com",
  score: "42" // Will parse "42" to 42, which satisfies % 2 === 0
})

if (result instanceof type.errors) {
  console.error("Validation failed:", result.flatProblemsByPath)
} else {
  console.log("Successfully validated user:", result)
  // result.score is inferred and validated as number (42)
}

// Usage 2: Assertion (Throws TraversalError on failure)
try {
  const verifiedUser = UserSchema.assert({
    id: "invalid-uuid",
    username: "a",
    email: "not-an-email",
    score: "43"
  })
} catch (e: any) {
  // e.arkErrors contains structured programmatic error details
  console.error(e.message)
}
```
*   **Equivalent in other surfaces**: Since ArkType is a TypeScript-native library with no CLI validators, this SDK interface is the primary mechanism. Other standard validators (e.g., Zod) require chaining methods like `z.string().uuid()`, whereas ArkType uses concise string expressions.

#### 2. Scopes, Cyclic Types, and Thunks
Scopes are encapsulated resolution spaces where you can register custom type aliases, nested submodules, and cyclic/recursive schemas.

```typescript
import { scope } from "arktype"

// Create a scope containing recursive types and a custom submodule
const orgScope = scope({
  // Private alias (indicated by importing/exporting)
  uuid: "string.uuid",

  // Recursive Cyclic Type: Member can contain a nested array of Members
  Member: {
    id: "uuid",
    name: "string",
    "manager?": "Member",
    "subordinates?": "Member[]"
  },

  // Submodule grouping
  "db.config": {
    host: "string",
    port: "number.integer"
  }
})

// Export the scope to make a reusable Module
const orgModule = orgScope.export()

// Extract the inferred type of a Member
type Member = typeof orgModule.Member.infer

// Validate deeply cyclic data
const ceo = orgModule.Member.assert({
  id: "f81d4fae-7dec-11d0-a765-00a0c91e6bf6",
  name: "Satya",
  subordinates: [
    {
      id: "a11d4fae-7dec-11d0-a765-00a0c91e6bf6",
      name: "Phil",
      manager: { id: "f81d4fae-7dec-11d0-a765-00a0c91e6bf6", name: "Satya" }
    }
  ]
})
```

#### 3. Pattern Matching (`match`) & Validated Functions (`type.fn`)
ArkType 2.1 introduced `match`, a syntactic pattern matcher built on set theory that optimizes checks by skipping unmatched branches. ArkType 2.2 introduced `type.fn`, which validates function inputs and return values at runtime.

```typescript
import { match, type } from "arktype"

// Pattern Matching
const processResponse = match({
  "string | number": (v) => `Primitive: ${v}`,
  "string[]": (arr) => `Array of strings of length ${arr.length}`,
  "{ success: true, data: unknown }": (obj) => `Success!`,
  "default": "assert" // Throws if none of the cases match
})

console.log(processResponse("hello")) // "Primitive: hello"
console.log(processResponse(["a", "b"])) // "Array of strings of length 2"

// Validated Functions
const calculateTotal = type.fn(
  "number",              // Param 1
  "number = 0.1",        // Param 2 (defaults to 0.1)
  ":",
  "number"               // Return Type
)((price, tax) => {
  return price + price * tax
})

const total = calculateTotal(100) // Returns 110 (100 + 100 * 0.1)
// calculateTotal("100") -> Throws TraversalError: value at [0] must be a number (was string)
```

---

## 3. Real-World Use Cases & Templates

### Integration Patterns

1.  **Environment Variable Validation with ArkEnv (`arkenv`)**:
    ArkEnv reads environment variables, automatically coerces primitive types, and validates the schema at startup.
    ```typescript
    import { arkenv } from "arkenv"

    const env = arkenv({
      HOST: "string.ip | 'localhost'",
      PORT: "number.integer",
      DEBUG: "boolean",
      NODE_ENV: "'development' | 'production' | 'test'"
    })

    // TypeScript automatically infers the types:
    console.log(env.HOST) // string
    console.log(env.PORT) // number
    console.log(env.DEBUG) // boolean
    ```

2.  **API Schema Validation in Elysia / Fastify (Standard Schema)**:
    Because ArkType implements the Standard Schema interface, it integrates directly with modern web frameworks like Elysia:
    ```typescript
    import { Elysia } from "elysia"
    import { type } from "arktype"

    const UserBody = type({
      username: "string.alphanumeric",
      email: "string.email"
    })

    const app = new Elysia()
      .post("/user", ({ body }) => `Created ${body.username}`, {
        body: UserBody // Framework uses the Standard Schema interface for validation
      })
      .listen(3000)
    ```

3.  **Type Testing with `@arktype/attest`**:
    Ensures complex type-level inferences match runtime definitions during testing:
    ```typescript
    import { type } from "arktype"
    import { attest } from "@arktype/attest"

    it("validates types and values simultaneously", () => {
      const NumericParse = type("string.numeric.parse")

      // Asserts that the inferred type is exactly 'number'
      attest<number>(NumericParse.infer)

      // Asserts that parsing invalid data throws the expected type and runtime error
      // @ts-expect-error
      attest(() => type("number%0")).throwsAndHasTypeError(
        "% operator must be followed by a non-zero integer literal (was 0)"
      )
    })
    ```

---

## 4. Developer Friction Points

### Friction Point 1: Global Config Import Order
*   **Description**: Applying global configuration changes (like `exactOptionalPropertyTypes` or `numberAllowsNaN`) late in the execution cycle fails to configure built-in keywords.
*   **Error/Symptom**: Config settings do not affect types, and built-in keywords behave with original defaults.
*   **Cause**: ArkType compiles and caches built-in keywords as soon as `"arktype"` is imported. If `configure()` is called after this import, the keywords are already frozen.
*   **Resolution & Links**: Move the configuration into a separate `config.ts` file that imports from `"arktype/config"` and import this file before any other imports in your entrypoint file.
    *   *Reference*: [ArkType Configuration Levels](https://arktype.io/docs/configuration#levels)

### Friction Point 2: Union Morphs ParseError
*   **Description**: Creating a union type where multiple branches apply different morphs to overlapping input structures is disallowed.
*   **Error/Symptom**: `ParseError: A union that could apply different morphs to the same data is a ParseError`
*   **Cause**: Set-theoretic design enforces commutativity. If an input matches multiple branches containing different morphs, the outcome is non-deterministic. For example, `type({ box: "string.numeric.parse" }).or({ box: "string" })` is invalid because `"123"` could produce either `{ box: 123 }` or `{ box: "123" }`.
*   **Resolution & Links**: Discriminate the union branches using a unique literal property, or perform a single morph that handles the conditional transformations internally.
    *   *Reference*: [ArkType Union Expressions](https://arktype.io/docs/expressions#union)

### Friction Point 3: Undeclared Object Keys Ignored by Default
*   **Description**: Developers expecting strict object validation are surprised when inputs containing extra, undeclared properties are accepted and preserved.
*   **Error/Symptom**: Objects with extra keys validate successfully, potentially leading to security or database persistence issues (e.g., mass-assignment vulnerabilities).
*   **Cause**: To align with TypeScript's structural type system and optimize performance, ArkType ignores undeclared keys by default.
*   **Resolution & Links**: Use the `+` syntax within individual object schemas to explicitly reject or delete extra keys (e.g., `type({ name: "string", "+": "reject" })`), or configure `onUndeclaredKey: "reject" | "delete"` globally.
    *   *Reference*: [ArkType Undeclared Keys](https://arktype.io/docs/objects#properties-undeclared) / [onUndeclaredKey Config](https://arktype.io/docs/configuration#onundeclaredkey)

---

## 5. Evaluation Ideas

### Simple Difficulty Tier
1.  **Form Validation**: Validate a standard user registration form with an alphanumeric username of length 3-15, an email, and an optional password of length >= 8.
2.  **Primitive Coercion**: Implement a string-to-boolean morph that coerces `"true"`, `"1"`, and `"yes"` to `true`, and `"false"`, `"0"`, and `"no"` to `false`.
3.  **Configured Password Redaction**: Create a password schema that overrides the `actual` error configuration, redacting the invalid input from being logged in error messages.

### Medium Difficulty Tier
4.  **Cyclic Schema Definition**: Define a recursive schema for a nested directory structure where each directory has a `name` (string) and an array of nested `subdirectories`.
5.  **Validated Environment Parser**: Build an environment validator using `arkenv` that parses a `PORT` (integer), a `DATABASE_URL` (URL), and a list of `ALLOWED_ORIGINS` (parsed from a comma-separated string array).
6.  **Type-Safe Function Boundary**: Declare a validated function using `type.fn` that takes a numeric array and an optional multiplier (defaulting to 1.5) and returns a validated numeric array of the same length.

### Complex Difficulty Tier
7.  **Set-Theoretic Pattern Matcher**: Implement an API response handler using `match` that discriminates between `Success` (containing a generic payload), `Error` (containing a code and reason), and `Pending` states, asserting strict runtime typing on the extracted payload.
8.  **Bidirectional JSON Schema Converter**: Build a schema migration tool that exports complex ArkType schemas (including recursive references) to standard JSON Schema draft-07 formats, with custom fallback handlers mapping custom predicates to string formats.

---

## 6. Sources

1.  [ArkType Official Documentation](https://arktype.io/docs/) - Core reference for setup, primitives, and APIs.
2.  [ArkType Primitives Reference](https://arktype.io/docs/primitives) - Comprehensive list of built-in keywords and literal definitions.
3.  [ArkType Expressions Reference](https://arktype.io/docs/expressions) - Documentation on pipes, morphs, unions, intersections, and validated functions.
4.  [ArkType Scopes Documentation](https://arktype.io/docs/scopes) - Guides on scopes, modules, cyclic types, and submodule definitions.
5.  [ArkType Configuration API](https://arktype.io/docs/configuration) - Deep dive into error customization, level overrides, JIT compilation, and `toJsonSchema` settings.
6.  [ArkType Object Properties](https://arktype.io/docs/objects) - Explains required/optional keys, default values, index signatures, and undeclared key strategies.
7.  [ArkType Release Notes (2.0, 2.1, 2.2)](https://arktype.io/llms.txt) - Detailed logs on pattern matching, type-safe regex, Standard Schema integrations, and serializable error structures.
8.  [ArkEnv Documentation](https://arkenv.js.org/) - Comprehensive guide on environment variable validation, Vite plugins, and automatic type coercions.
9.  [GitHub Repository: arktypeio/arktype](https://github.com/arktypeio/arktype) - Source of truth for tests, issues, and discussion threads regarding schema validation.
