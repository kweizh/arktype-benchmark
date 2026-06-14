import { type, scope } from "arktype";

const Username = type("string")
  .narrow((val): val is string => /^[a-zA-Z0-9]+$/.test(val) && !["admin", "root", "system"].includes(val));

export const types = scope({
  User: {
    id: "string.uuid",
    username: Username,
    score: "string.numeric.parse",
    "friends?": "User[]"
  }
}).export();

export const User = types.User;

export const userJsonSchema = User.toJsonSchema({
  target: "draft-07",
  fallback: {
    morph: (ctx) => ({
      type: "string",
      format: "morph-redacted",
      description: "morph dropped"
    }),
    predicate: (ctx) => ({
      ...ctx.base,
      "x-arktype-fallback": "predicate"
    })
  }
});
