import { scope } from "arktype";

// Reserved words list for the username narrow/predicate
const RESERVED = new Set(["admin", "root", "system"]);

// Build a recursive User type using a named scope so self-references resolve.
const User = scope({
  User: {
    id: "string.uuid",
    username: [
      "string",
      ":",
      (s: string) => /^[A-Za-z0-9]+$/.test(s) && !RESERVED.has(s),
    ],
    score: "string.numeric.parse",
    friends: "User[]",
  },
}).export();

// The exported module has the User type as a property
const UserType = User.User;

// Convert to draft-07 JSON Schema with custom fallbacks
export const userJsonSchema = UserType.toJsonSchema({
  target: "draft-07",
  fallback: {
    // For ANY morph node, return a redacted string placeholder
    morph: () => ({
      type: "string",
      format: "morph-redacted",
      description: "morph dropped",
    }),
    // For ANY predicate/narrow node, merge an annotation into the base schema
    predicate: (ctx) => ({
      ...ctx.base,
      "x-arktype-fallback": "predicate",
    }),
  },
});
