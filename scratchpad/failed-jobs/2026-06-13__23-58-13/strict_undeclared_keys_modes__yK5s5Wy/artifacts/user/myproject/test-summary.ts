import { type } from "arktype";
const schema = type({ id: "string.uuid", name: "string" });
const result = schema({ id: "123", name: 123 });
if (result instanceof type.errors) {
    console.log(result.summary);
}
