import { Elysia } from "elysia"
import { type } from "arktype"

// Define the ArkType schema
const userSchema = type({
  username: "3 <= string.alphanumeric <= 20",
  email: "string.email",
  age: "number.integer >= 18"
})

// Create the Elysia application
const app = new Elysia()
  .post("/user", ({ body }) => {
    return {
      username: body.username,
      email: body.email,
      age: body.age
    }
  }, {
    body: userSchema
  })
  .listen(3000)

console.log(`Server is running at ${app.server?.hostname}:${app.server?.port}`)
