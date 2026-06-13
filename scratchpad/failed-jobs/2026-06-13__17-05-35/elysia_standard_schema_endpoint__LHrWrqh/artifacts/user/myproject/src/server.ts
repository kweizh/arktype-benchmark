import { Elysia } from "elysia";
import { type } from "arktype";

const userSchema = type({
  username: "string.alphanumeric >= 3 <= 20",
  email: "string.email",
  age: "number.integer >= 18",
});

const app = new Elysia()
  .post("/user", ({ body }) => {
    return { username: body.username };
  }, {
    body: userSchema,
  })
  .listen(3000);

console.log(`Server running at http://localhost:${app.server?.port}`);
