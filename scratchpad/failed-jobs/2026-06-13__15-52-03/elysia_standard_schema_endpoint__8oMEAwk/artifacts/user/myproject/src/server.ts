import { Elysia } from "elysia";
import { type } from "arktype";

// ArkType schema passed directly as the `body:` validator via Standard Schema interface.
// - username: alphanumeric, length 3–20
// - email:    must be a valid email address
// - age:      integer >= 18
// Extra/unknown fields are silently ignored by ArkType (open-by-default behaviour).
const userSchema = type({
  username: "string >= 3 & string <= 20 & /^[a-zA-Z0-9]+$/",
  email: "string.email",
  age: "number.integer >= 18",
});

const app = new Elysia()
  .post("/user", ({ body }) => body, {
    body: userSchema,
  })
  .listen(3000);

console.log(`Server running at http://localhost:${app.server?.port}`);
