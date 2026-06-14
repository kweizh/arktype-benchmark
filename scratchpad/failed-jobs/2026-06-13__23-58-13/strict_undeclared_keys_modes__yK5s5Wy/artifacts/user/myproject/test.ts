import { type } from "arktype";

const ignoreSchema = type({
    id: "string.uuid",
    name: "string",
    email: "string.email",
    "+": "ignore"
});

const rejectSchema = type({
    id: "string.uuid",
    name: "string",
    email: "string.email",
    "+": "reject"
});

const deleteSchema = type({
    id: "string.uuid",
    name: "string",
    email: "string.email",
    "+": "delete"
});

const payload = {
    id: "123e4567-e89b-12d3-a456-426614174000",
    name: "Alice",
    email: "alice@example.com",
    extra: "bad"
};

console.log("IGNORE:", ignoreSchema(payload));
console.log("REJECT:", rejectSchema(payload));
console.log("DELETE:", deleteSchema(payload));
