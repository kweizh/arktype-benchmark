import { type } from "arktype";
const rejectSchema = type({
    id: "string.uuid",
    name: "string",
    email: "string.email",
    "+": "reject"
});

const payload = {
    id: "123e4567-e89b-12d3-a456-426614174000",
    name: "Alice",
    email: "alice@example.com",
    extra: "bad"
};

const result = rejectSchema(payload);
if (result instanceof type.errors) {
    console.log("Error instance string:", result.toString());
    console.log("Error message:", result.message);
    console.log("Error summary:", result.summary);
} else {
    console.log("Success:", result);
}
