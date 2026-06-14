import { scope, type } from "arktype";

const RESERVED_WORDS = ["admin", "root", "system"];

const UserScope = scope({
  User: {
    id: "string",
    username: type("string").narrow(
      (s): s is string => /^[a-zA-Z0-9]+$/.test(s) && !RESERVED_WORDS.includes(s)
    ),
    score: "string.numeric.parse",
    friends: "User[]",
  },
});

const { User } = UserScope.export();

const userSchema = User.toJsonSchema({
  target: "draft-07",
  useRefs: true,
  fallback: {
    morph: (ctx) => ({
      type: "string",
      format: "morph-redacted",
      description: "morph dropped",
    }),
    predicate: (ctx) => ({
      ...ctx.base,
      "x-arktype-fallback": "predicate",
    }),
  },
});

export { userSchema };