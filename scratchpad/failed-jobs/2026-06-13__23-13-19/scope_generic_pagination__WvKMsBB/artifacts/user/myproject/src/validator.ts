import { scope } from "arktype"

// Define the schema using the scope API with generic Page<T>
export const types = scope({
    User: {
        id: "string.uuid",
        name: "1 <= string <= 50"
    },
    Post: {
        id: "string.uuid",
        title: "1 <= string <= 120",
        authorId: "string.uuid"
    },
    "Page<T>": {
        items: "T[]",
        total: "number.integer >= 0",
        page: "number.integer >= 1",
        perPage: "1 <= number.integer <= 100",
        hasNext: "boolean"
    },
    UserPage: "Page<User>",
    PostPage: "Page<Post>"
}).export()

// Extract TypeScript types from the scope exports
export type User = typeof types.User.infer
export type Post = typeof types.Post.infer
export type UserPage = typeof types.UserPage.infer
export type PostPage = typeof types.PostPage.infer

/**
 * Validates a paginated response for the specified resource kind.
 * Returns the validated page object or throws via ArkType's assertion API.
 */
export function validatePage(kind: "User", page: unknown): UserPage
export function validatePage(kind: "Post", page: unknown): PostPage
export function validatePage(kind: "User" | "Post", page: unknown): UserPage | PostPage
export function validatePage(kind: "User" | "Post", page: unknown) {
    if (kind === "User") {
        return types.UserPage.assert(page)
    } else if (kind === "Post") {
        return types.PostPage.assert(page)
    } else {
        throw new Error(`Unknown kind: ${kind}`)
    }
}
