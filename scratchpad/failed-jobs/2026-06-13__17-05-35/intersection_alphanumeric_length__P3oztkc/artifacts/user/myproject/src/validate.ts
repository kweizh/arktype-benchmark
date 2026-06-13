import { type } from "arktype";

const username = type("string").narrow((s, ctx) => {
  if (s.length < 3) return ctx.reject("too short");
  if (s.length > 19) return ctx.reject("too long");
  if (!/^[a-zA-Z]/.test(s)) return ctx.reject("must start with a letter");
  if (!/^[a-zA-Z0-9]+$/.test(s)) return ctx.reject("must be alphanumeric");
  return true;
});

const input = process.argv[2] ?? "";
const result = username(input);

if (typeof result === "string") {
  console.log("valid");
  process.exit(0);
} else {
  console.log("invalid");
  process.exit(1);
}
