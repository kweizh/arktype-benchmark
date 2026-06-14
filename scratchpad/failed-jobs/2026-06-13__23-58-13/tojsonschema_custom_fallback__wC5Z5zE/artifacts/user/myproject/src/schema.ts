import { scope, type } from "arktype";

export const types = scope({
    User: {
        id: "string.uuid",
        username: type("string").narrow((s) => {
            if (!/^[a-zA-Z0-9]+$/.test(s)) return false;
            if (["admin", "root", "system"].includes(s)) return false;
            return true;
        }),
        score: "string.numeric.parse",
        friends: "User[]"
    }
}).export();

export function exportSchema() {
    return types.User.toJsonSchema({
        target: "draft-07",
        fallback: {
            morph: (ctx) => ({
                type: "string",
                format: "morph-redacted",
                description: "morph dropped"
            }),
            predicate: (ctx) => ({
                ...ctx.base,
                "x-arktype-fallback": "predicate"
            })
        }
    });
}
