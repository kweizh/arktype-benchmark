import { type, scope } from "arktype";

const types = scope({
  "Page<T>": {
    items: "T[]",
    total: "number%1>=0",
    page: "number%1>=1",
    perPage: "number%1>=1<=100",
    hasNext: "boolean"
  },
  User: {
    id: "string.uuid",
    name: "string>=1<=50"
  },
  Post: {
    id: "string.uuid",
    title: "string>=1<=120",
    authorId: "string.uuid"
  },
  UserPage: "Page<User>",
  PostPage: "Page<Post>"
}).export();

console.log(types.UserPage({
  items: [{ id: "123e4567-e89b-12d3-a456-426614174000", name: "Alice" }],
  total: 10,
  page: 1,
  perPage: 10,
  hasNext: false
}));
