import { scope } from "arktype";

const types = scope({
  User: {
    id: "string.uuid",
    name: "1 <= string <= 50",
  },
  Post: {
    id: "string.uuid",
    title: "1 <= string <= 120",
    authorId: "string.uuid",
  },
  "Page<T>": {
    items: "T[]",
    total: "number.integer >= 0",
    page: "number.integer >= 1",
    perPage: "1 <= number.integer <= 100",
    hasNext: "boolean",
  },
  UserPage: "Page<User>",
  PostPage: "Page<Post>",
}).export();

export function validatePage(kind: "User" | "Post", page: unknown) {
  if (kind === "User") {
    return types.UserPage.assert(page);
  }
  if (kind === "Post") {
    return types.PostPage.assert(page);
  }
  throw new Error(`Unknown kind: ${kind}`);
}