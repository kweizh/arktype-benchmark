import { type } from "arktype";

// Single ArkType expression chain:
// - Must start with a letter (a-z or A-Z)
// - Followed by 2 to 18 alphanumeric characters
// - Total length: 3–19 characters
// - No special characters allowed
const Username = type(/^[a-zA-Z][a-zA-Z0-9]{2,18}$/);

const input = process.argv[2];
const result = Username(input);

if (result instanceof type.errors) {
  console.log("invalid");
  process.exit(1);
} else {
  console.log("valid");
  process.exit(0);
}
