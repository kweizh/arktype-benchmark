import { scope, type } from "arktype";

const $ = scope({
  UUID: "string.pattern(/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i)",
  Email: "string.pattern(/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/)",
  Username: "string.alphanumeric & string.length>=3 & string.length<=20",
  Score: "string.numeric >>> number",
  Zip: "string.pattern(/^\\d{5}(-\\d{4})?$/)",
  Address: {
    street: "string",
    city: "string",
    zip: "Zip",
  },
  Post: {
    title: "string.length>=1 & string.length<=120",
    tags: "string.length>=1 & string.length<=10[]",
    comments: "Comment[]",
  },
  Comment: {
    id: "UUID",
    body: "string.length>=1",
    "replies?": "Comment[]",
  },
  User: {
    id: "UUID",
    email: "Email",
    username: "Username",
    score: "Score",
    address: "Address",
    posts: "Post[]",
  },
});

const mod = $.export();
const userSchema = mod.User;

const jsonSchema = userSchema.toJsonSchema({
  dialect: "https://json-schema.org/draft/2020-12/schema",
  fallback: {
    morph: (ctx) => ctx.base,
  },
});

console.log(JSON.stringify(jsonSchema, null, 2));