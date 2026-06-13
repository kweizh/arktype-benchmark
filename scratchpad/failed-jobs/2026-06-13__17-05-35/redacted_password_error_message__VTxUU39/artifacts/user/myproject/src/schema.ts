import { type } from "arktype";

export const PasswordSchema = type("string >= 8").configure({
  actual: () => "<redacted>",
});
