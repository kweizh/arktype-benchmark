import { Elysia } from "elysia";
import { type } from "arktype";

const UserSchema = type({
  username: "string.alphanumeric>=3<=20",
  email: "string.email",
  age: "number.integer>=18",
});

const app = new Elysia()
  .post("/user", ({ body }) => {
    return { username: body.username, email: body.email, age: body.age };
  }, {
    body: UserSchema,
  })
  .listen(3000);

console.log(`🦊 Elysia is running at http://localhost:${app.server!.port}`);