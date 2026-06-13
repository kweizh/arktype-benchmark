import { type } from "arktype";

export const PasswordSchema = type("string").narrow((val, ctx) => {
  if (val.length < 8 || val === "mySecret") {
    return ctx.reject({
      message: "must be at least 8 characters (was <redacted>)"
    });
  }
  return true;
}).configure({
  message: () => "must be at least 8 characters (was <redacted>)"
});
