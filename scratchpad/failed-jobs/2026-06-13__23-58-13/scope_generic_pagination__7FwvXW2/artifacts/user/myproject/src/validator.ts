import { scope } from "arktype";

export const types = scope({
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

export function validatePage(kind: "User" | "Post", page: unknown) {
  if (kind === "User") {
    return types.UserPage.assert(page);
  } else if (kind === "Post") {
    return types.PostPage.assert(page);
  }
  throw new Error(`Unknown kind: ${kind}`);
}
