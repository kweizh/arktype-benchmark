import { type } from "arktype"

/**
 * Strategy 1: Loose (Ignore)
 * 
 * Allows undeclared keys on input and preserves them on output.
 * This is ArkType's default behavior, mirroring TypeScript's structural typing.
 * It can also be explicitly configured using `.onUndeclaredKey("ignore")` 
 * or inline via the `"+": "ignore"` shorthand.
 */
export const LooseUser = type({
    name: "string"
})

/**
 * Strategy 2: Reject (Strict)
 * 
 * Rejects any input that contains undeclared keys with a validation failure.
 * Configured using `.onUndeclaredKey("reject")` or inline via the `"+": "reject"` shorthand.
 */
export const RejectUser = type({
    name: "string"
}).onUndeclaredKey("reject")

/**
 * Strategy 3: Delete (Distilled/Pruned)
 * 
 * Allows undeclared keys on input, but clones the object and deletes/removes 
 * any undeclared keys from the output before returning.
 * Configured using `.onUndeclaredKey("delete")` or inline via the `"+": "delete"` shorthand.
 */
export const DeleteUser = type({
    name: "string"
}).onUndeclaredKey("delete")
