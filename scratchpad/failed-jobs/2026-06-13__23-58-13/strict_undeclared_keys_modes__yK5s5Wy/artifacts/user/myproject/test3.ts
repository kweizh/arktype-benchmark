import { type } from "arktype";
const schema = type("string");
const result = schema(5);
console.log(result instanceof type.errors);
console.log(result.toString());
