import { scope } from "arktype";

// ---------------------------------------------------------------------------
// Build the scope with a generic Page<T> envelope plus the two item kinds.
// The key "Page<T>" is the ArkType syntax for declaring a generic alias inside
// a scope. It will be instantiated as "Page<User>" and "Page<Post>" below.
// ---------------------------------------------------------------------------
const paginationScope = scope({
  User: {
    id: "string.uuid",
    name: "string >= 1 & string <= 50",
  },
  Post: {
    id: "string.uuid",
    title: "string >= 1 & string <= 120",
    authorId: "string.uuid",
  },
  "Page<T>": {
    items: "T[]",
    total: "number.integer >= 0",
    page: "number.integer >= 1",
    perPage: "number.integer >= 1 & number.integer <= 100",
    hasNext: "boolean",
  },
  UserPage: "Page<User>",
  PostPage: "Page<Post>",
});

const types = paginationScope.export();

export type UserPage = typeof types.UserPage.infer;
export type PostPage = typeof types.PostPage.infer;

/**
 * Validates a raw `page` payload for the given `kind`.
 * Returns the validated (and narrowed) object on success,
 * or throws an `ArkErrors` instance on failure.
 */
export function validatePage(kind: "User" | "Post", page: unknown): UserPage | PostPage {
  if (kind === "User") {
    return types.UserPage.assert(page) as UserPage;
  }
  return types.PostPage.assert(page) as PostPage;
}
