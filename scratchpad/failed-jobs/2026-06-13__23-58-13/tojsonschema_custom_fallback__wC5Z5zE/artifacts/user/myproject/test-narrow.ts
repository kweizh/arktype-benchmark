import { scope, type } from "arktype";
const types = scope({
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
console.log(types.User({
    id: "123e4567-e89b-12d3-a456-426614174000",
    username: "john",
    score: "123",
    friends: []
}));
console.log(types.User({
    id: "123e4567-e89b-12d3-a456-426614174000",
    username: "admin",
    score: "123",
    friends: []
}));
