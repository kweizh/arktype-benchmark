import { type } from "arktype";

const usernameSchema = type("/^[a-zA-Z][a-zA-Z0-9]{2,18}$/");

const input = process.argv[2] || "";

const result = usernameSchema(input);

if (result instanceof type.errors) {
    console.log("invalid");
    process.exit(1);
} else {
    console.log("valid");
    process.exit(0);
}
