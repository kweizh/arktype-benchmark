import { scope } from "arktype";

// Build the scope with User, Post, and a generic Page<T> wrapper.
// The scope API parses keys like "Page<T>" as generic aliases.
const $ = scope({
  // User item kind
  User: {
    id: "string.uuid",
    name: "1 <= string <= 50",
  },
  // Post item kind
  Post: {
    id: "string.uuid",
    title: "1 <= string <= 120",
    authorId: "string.uuid",
  },
  // Generic Page<T> envelope
  "Page<T>": {
    items: "T[]",
    total: "number.integer >= 0",
    page: "number.integer >= 1",
    perPage: "1 <= number.integer <= 100",
    hasNext: "boolean",
  },
}).export();

// Instantiate Page<User> and Page<Post>
export const PageOfUser = $.Page($.User);
export const PageOfPost = $.Page($.Post);

/**
 * Validates a page object against the schema for the given kind.
 * Returns the validated page on success.
 * Throws (via ArkType's assert) on validation failure.
 */
export function validatePage(
  kind: "User" | "Post",
  page: unknown
): unknown {
  if (kind === "User") {
    return PageOfUser.assert(page);
  }
  return PageOfPost.assert(page);
}
