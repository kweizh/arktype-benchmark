import { scope } from "arktype"

// Reserved words that must not be used as usernames
const RESERVED_WORDS = ["admin", "root", "system"]

// Build a recursive User scope so that `friends` can self-reference.
// The `username` field uses a thunk so we can call `.narrow()` fluently
// within the scope's own resolution context.
const userScope = scope({
  User: {
    // Unconstrained UUID string
    id: "string.uuid",

    // Alphanumeric string with a custom narrow predicate (reserved-word check)
    username: () =>
      userScope.type("string").narrow(
        (val: string) =>
          /^[a-z0-9]+$/i.test(val) && !RESERVED_WORDS.includes(val)
      ),

    // Morph: parse a numeric string → number (has no JSON Schema equivalent)
    score: "string.numeric.parse",

    // Recursive self-reference
    friends: "User[]",
  },
})

export const { User } = userScope.export()

// Convert to draft-07 JSON Schema with custom fallback handlers:
//   • morph      → redacted string placeholder
//   • predicate  → base schema + x-arktype-fallback annotation
export const userJsonSchema = User.toJsonSchema({
  target: "draft-07",
  fallback: {
    morph: (_ctx) => ({
      type: "string" as const,
      format: "morph-redacted",
      description: "morph dropped",
    }),
    predicate: (ctx) => ({
      ...ctx.base,
      "x-arktype-fallback": "predicate",
    }),
  },
})
